from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routers import chat, library, papers

settings = get_settings()

app = FastAPI(
    title="ResearchPilot AI Agent",
    description="Autonomous research intelligence hub: discover, organize, "
                 "summarize, and chat with academic papers.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(papers.router)
app.include_router(library.router)
app.include_router(chat.router)


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "ResearchPilot API"}
