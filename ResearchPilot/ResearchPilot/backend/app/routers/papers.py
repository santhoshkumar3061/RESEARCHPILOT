from fastapi import APIRouter, HTTPException

from app.models.schemas import Paper, SearchRequest, SearchResponse, SummarizeRequest, SummarizeResponse
from app.services import arxiv_client, library_store, llm_client, vector_store

router = APIRouter(prefix="/api/papers", tags=["papers"])


@router.post("/search", response_model=SearchResponse)
def search_papers(req: SearchRequest):
    """Discover papers on arXiv matching a natural-language query."""
    results = arxiv_client.search_papers(req.query, max_results=req.max_results, category=req.category)
    return SearchResponse(query=req.query, results=results)


@router.get("/{paper_id}", response_model=Paper)
def get_paper(paper_id: str):
    paper = arxiv_client.get_paper_by_id(paper_id)
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found on arXiv")
    return paper


@router.post("/{paper_id}/index")
def index_paper(paper_id: str):
    """Embed the paper's abstract (and any stored notes) into the vector
    store so it becomes queryable in per-paper and global chat."""
    item = library_store.get_item(paper_id)
    paper = item.paper if item else arxiv_client.get_paper_by_id(paper_id)
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")

    text = paper.abstract
    if item and item.notes:
        text += f"\n\nResearcher notes: {item.notes}"

    n_chunks = vector_store.index_paper_text(paper.id, paper.title, text)

    if item:
        item.indexed = True
        library_store.upsert_item(item)

    return {"paper_id": paper.id, "chunks_indexed": n_chunks}


@router.post("/summarize", response_model=SummarizeResponse)
def summarize_paper(req: SummarizeRequest):
    item = library_store.get_item(req.paper_id)
    paper = item.paper if item else arxiv_client.get_paper_by_id(req.paper_id)
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")

    extra_text = item.notes if item else ""
    result = llm_client.summarize_paper(paper.title, paper.abstract, extra_text, req.style)
    return SummarizeResponse(
        paper_id=paper.id,
        style=req.style,
        summary=result.get("summary", ""),
        key_findings=result.get("key_findings", []),
        limitations=result.get("limitations", []),
    )
