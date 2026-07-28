from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class ReadStatus(str, Enum):
    unread = "unread"
    reading = "reading"
    read = "read"


class PaperSource(str, Enum):
    arxiv = "arxiv"
    manual = "manual"


class Paper(BaseModel):
    """Canonical representation of a paper, whether discovered or saved."""
    id: str  # arXiv id or generated uuid for manual uploads
    title: str
    authors: list[str] = Field(default_factory=list)
    abstract: str = ""
    published: Optional[datetime] = None
    updated: Optional[datetime] = None
    categories: list[str] = Field(default_factory=list)
    pdf_url: Optional[str] = None
    entry_url: Optional[str] = None
    source: PaperSource = PaperSource.arxiv


class SearchRequest(BaseModel):
    query: str
    max_results: int = 10
    category: Optional[str] = None  # e.g. "cs.AI"


class SearchResponse(BaseModel):
    query: str
    results: list[Paper]


class LibraryItem(BaseModel):
    paper: Paper
    tags: list[str] = Field(default_factory=list)
    collection: str = "Uncategorized"
    status: ReadStatus = ReadStatus.unread
    notes: str = ""
    added_at: datetime = Field(default_factory=datetime.utcnow)
    indexed: bool = False  # whether full text has been embedded for Q&A


class AddToLibraryRequest(BaseModel):
    paper: Paper
    tags: list[str] = Field(default_factory=list)
    collection: str = "Uncategorized"


class UpdateLibraryItemRequest(BaseModel):
    tags: Optional[list[str]] = None
    collection: Optional[str] = None
    status: Optional[ReadStatus] = None
    notes: Optional[str] = None


class SummarizeRequest(BaseModel):
    paper_id: str
    style: str = "concise"  # "concise" | "detailed" | "eli5" | "critical"


class SummarizeResponse(BaseModel):
    paper_id: str
    style: str
    summary: str
    key_findings: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)


class ChatMessage(BaseModel):
    role: str  # "user" | "assistant"
    content: str


class ChatRequest(BaseModel):
    paper_id: Optional[str] = None  # None => chat across whole library
    message: str
    history: list[ChatMessage] = Field(default_factory=list)


class Citation(BaseModel):
    paper_id: str
    paper_title: str
    chunk_preview: str


class ChatResponse(BaseModel):
    answer: str
    citations: list[Citation] = Field(default_factory=list)


class AgentTaskRequest(BaseModel):
    """Free-form instruction routed through the research agent, e.g.
    'Find recent papers on retrieval-augmented generation and summarize the top 3.'"""
    instruction: str


class AgentStep(BaseModel):
    tool: str
    input: dict
    output_summary: str


class AgentTaskResponse(BaseModel):
    instruction: str
    steps: list[AgentStep]
    final_answer: str
