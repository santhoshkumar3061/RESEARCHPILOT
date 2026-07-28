"""
Thin wrapper around the `arxiv` package for paper discovery.

Kept isolated from the rest of the app so the discovery backend could be
swapped (Semantic Scholar, PubMed, CORE, etc.) without touching routers.
"""
import arxiv

from app.config import get_settings
from app.models.schemas import Paper, PaperSource

settings = get_settings()
_client = arxiv.Client(page_size=50, delay_seconds=1.0, num_retries=3)


def _to_paper(result: arxiv.Result) -> Paper:
    return Paper(
        id=result.get_short_id(),
        title=result.title.strip().replace("\n", " "),
        authors=[a.name for a in result.authors],
        abstract=result.summary.strip().replace("\n", " "),
        published=result.published,
        updated=result.updated,
        categories=result.categories,
        pdf_url=result.pdf_url,
        entry_url=result.entry_id,
        source=PaperSource.arxiv,
    )


def search_papers(query: str, max_results: int | None = None, category: str | None = None) -> list[Paper]:
    """Search arXiv for papers matching `query`, optionally scoped to a category
    like 'cs.AI' or 'cs.CL'."""
    full_query = f"cat:{category} AND {query}" if category else query
    search = arxiv.Search(
        query=full_query,
        max_results=max_results or settings.arxiv_max_results,
        sort_by=arxiv.SortCriterion.Relevance,
    )
    return [_to_paper(r) for r in _client.results(search)]


def get_paper_by_id(arxiv_id: str) -> Paper | None:
    search = arxiv.Search(id_list=[arxiv_id])
    results = list(_client.results(search))
    return _to_paper(results[0]) if results else None
