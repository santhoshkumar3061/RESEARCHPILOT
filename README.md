[README.md](https://github.com/user-attachments/files/30445049/README.md)
# ResearchPilot AI Agent — Autonomous Research Intelligence Hub

A working full-stack scaffold for an AI research assistant: discover papers
on arXiv, organize them into a library, get AI summaries in different
styles, ask grounded (RAG) questions of a single paper or your whole
library, and hand off free-form instructions to a small tool-using agent.

## Architecture

```
ResearchPilot/
├── backend/                 FastAPI service
│   └── app/
│       ├── main.py          App entrypoint, CORS, router wiring
│       ├── config.py        Env-driven settings (pydantic-settings)
│       ├── models/          Pydantic schemas shared across routers
│       ├── services/
│       │   ├── arxiv_client.py    Paper discovery (arXiv API)
│       │   ├── vector_store.py    Chunking + embeddings (ChromaDB, local)
│       │   ├── llm_client.py      Anthropic API: summarize / RAG / agent planning
│       │   ├── library_store.py   Saved-paper persistence (JSON; swap for Postgres)
│       │   └── agent.py           Plan → execute tools → synthesize answer
│       └── routers/
│           ├── papers.py    Search, fetch, index, summarize
│           ├── library.py   Save / tag / organize / status
│           └── chat.py      RAG chat + agent task endpoint
└── frontend/                 React (Vite) SPA
    └── src/
        ├── api/client.js     fetch wrapper for the backend
        ├── components/       PaperCard, Sidebar
        └── pages/
            ├── Discover.jsx      Paper discovery
            ├── Library.jsx       Smart organization (collections/tags/status)
            ├── PaperDetail.jsx   Summarization + per-paper Q&A
            ├── LibraryChat.jsx   Cross-library contextual Q&A
            └── AgentTasks.jsx    Free-form agent instructions
```

## How each requested capability maps to code

| Requirement            | Where it lives |
|-------------------------|----------------|
| Paper discovery         | `arxiv_client.py` + `POST /api/papers/search` + Discover page |
| Smart organization      | `library_store.py` + `library.py` router + Library page (collections, tags, read status) |
| AI summarization        | `llm_client.summarize_paper` + `POST /api/papers/summarize` (4 styles: concise/detailed/eli5/critical) |
| Contextual Q&A          | `vector_store.py` (ChromaDB retrieval) + `llm_client.answer_with_context` + `POST /api/chat` |
| Research assistance     | `agent.py` — LLM plans a short tool-call sequence (search → add → summarize → search-library), executes it, and synthesizes a final answer |

## Running it locally

### 1. Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then paste your ANTHROPIC_API_KEY into .env
uvicorn app.main:app --reload --port 8000
```

The first run downloads the `all-MiniLM-L6-v2` sentence-transformers model
(~80MB) for local embeddings — no external embedding API needed. ChromaDB
persists to `backend/chroma_data/`.

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Visit `http://localhost:5173`. Vite proxies `/api/*` to `localhost:8000`
(see `vite.config.js`), so no CORS setup is needed in dev beyond what's
already in `main.py`.

## Design notes / what's real vs. simplified

- **Real**: arXiv search, ChromaDB vector indexing + retrieval, Anthropic
  Messages API calls for summarization/RAG/agent planning, a genuine
  plan-execute-synthesize agent loop with 4 callable tools.
- **Simplified for a scaffold**: library storage is a JSON file, not
  Postgres (swap `library_store.py`'s internals — the function signatures
  are already DB-shaped); paper "full text" indexing uses the abstract
  plus any notes rather than parsing the PDF (add a PDF-to-text step in
  `papers.py::index_paper` if you want full-text RAG); there's no auth —
  every request acts on a single shared library.
- **Extending it**: to add PDF full-text ingestion, pull `paper.pdf_url`,
  extract text (e.g. `pypdf`), and pass it into
  `vector_store.index_paper_text` instead of just the abstract.

## Environment variables (`backend/.env`)

| Var | Purpose | Default |
|---|---|---|
| `ANTHROPIC_API_KEY` | Required for summarization/chat/agent | — |
| `LLM_MODEL` | Anthropic model id | `claude-sonnet-4-6` |
| `CHROMA_PERSIST_DIR` | Local vector store path | `./chroma_data` |
| `EMBEDDING_MODEL_NAME` | sentence-transformers model | `all-MiniLM-L6-v2` |
