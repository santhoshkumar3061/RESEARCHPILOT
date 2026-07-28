"""
Central configuration for ResearchPilot.

All secrets/keys are read from environment variables (.env in local dev,
real secret manager in production). Nothing is hard-coded.
"""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # --- LLM provider ---
    anthropic_api_key: str = ""
    llm_model: str = "claude-sonnet-4-6"
    llm_max_tokens: int = 1024

    # --- Vector store ---
    chroma_persist_dir: str = "./chroma_data"
    embedding_model_name: str = "all-MiniLM-L6-v2"  # sentence-transformers model
    collection_name: str = "research_papers"

    # --- Retrieval / chunking ---
    chunk_size_chars: int = 1200
    chunk_overlap_chars: int = 150
    top_k_chunks: int = 6

    # --- arXiv discovery ---
    arxiv_max_results: int = 20

    # --- API ---
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]


@lru_cache
def get_settings() -> Settings:
    return Settings()
