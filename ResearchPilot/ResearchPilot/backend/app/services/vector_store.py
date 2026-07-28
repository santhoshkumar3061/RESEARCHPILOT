"""
Vector store service.

Wraps ChromaDB (local, persistent, no external infra needed) with a
sentence-transformers embedding function. Swappable for Pinecone/Weaviate/
pgvector in production by changing only this file.
"""
import uuid

import chromadb
from chromadb.utils import embedding_functions

from app.config import get_settings

settings = get_settings()

_chroma_client = chromadb.PersistentClient(path=settings.chroma_persist_dir)

_embedder = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name=settings.embedding_model_name
)

_collection = _chroma_client.get_or_create_collection(
    name=settings.collection_name,
    embedding_function=_embedder,
    metadata={"hnsw:space": "cosine"},
)


def _chunk_text(text: str) -> list[str]:
    """Simple fixed-size overlapping chunker. Good enough for abstracts +
    extracted PDF text; swap for a semantic chunker if needed later."""
    size = settings.chunk_size_chars
    overlap = settings.chunk_overlap_chars
    if len(text) <= size:
        return [text]
    chunks = []
    start = 0
    while start < len(text):
        end = start + size
        chunks.append(text[start:end])
        start = end - overlap
    return chunks


def index_paper_text(paper_id: str, paper_title: str, full_text: str) -> int:
    """Chunk + embed a paper's text (abstract or full extracted PDF text) and
    upsert into the collection. Returns number of chunks indexed."""
    chunks = _chunk_text(full_text)
    ids = [f"{paper_id}::chunk::{i}::{uuid.uuid4().hex[:8]}" for i in range(len(chunks))]
    metadatas = [{"paper_id": paper_id, "paper_title": paper_title, "chunk_index": i}
                 for i in range(len(chunks))]

    # Remove any previous chunks for this paper before re-indexing
    existing = _collection.get(where={"paper_id": paper_id})
    if existing and existing.get("ids"):
        _collection.delete(ids=existing["ids"])

    _collection.add(ids=ids, documents=chunks, metadatas=metadatas)
    return len(chunks)


def query_similar_chunks(query: str, paper_id: str | None = None, top_k: int | None = None):
    """Return the most relevant chunks for `query`, optionally restricted to
    a single paper (per-paper Q&A) or across the whole library (global chat)."""
    where = {"paper_id": paper_id} if paper_id else None
    result = _collection.query(
        query_texts=[query],
        n_results=top_k or settings.top_k_chunks,
        where=where,
    )
    hits = []
    docs = result.get("documents", [[]])[0]
    metas = result.get("metadatas", [[]])[0]
    dists = result.get("distances", [[]])[0]
    for doc, meta, dist in zip(docs, metas, dists):
        hits.append({"text": doc, "metadata": meta, "distance": dist})
    return hits


def is_indexed(paper_id: str) -> bool:
    existing = _collection.get(where={"paper_id": paper_id}, limit=1)
    return bool(existing and existing.get("ids"))


def delete_paper(paper_id: str) -> None:
    existing = _collection.get(where={"paper_id": paper_id})
    if existing and existing.get("ids"):
        _collection.delete(ids=existing["ids"])
