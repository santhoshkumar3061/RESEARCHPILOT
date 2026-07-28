from fastapi import APIRouter

from app.models.schemas import (
    AgentTaskRequest,
    AgentTaskResponse,
    ChatRequest,
    ChatResponse,
    Citation,
)
from app.services import agent, llm_client, vector_store

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    """Contextual Q&A: retrieves relevant chunks (scoped to one paper or the
    whole library) and asks the LLM to answer grounded in them."""
    chunks = vector_store.query_similar_chunks(req.message, paper_id=req.paper_id)
    history = [m.model_dump() for m in req.history]
    answer = llm_client.answer_with_context(req.message, chunks, history)

    citations = [
        Citation(
            paper_id=c["metadata"].get("paper_id", ""),
            paper_title=c["metadata"].get("paper_title", "Unknown"),
            chunk_preview=c["text"][:220],
        )
        for c in chunks
    ]
    return ChatResponse(answer=answer, citations=citations)


@router.post("/agent/task", response_model=AgentTaskResponse)
def agent_task(req: AgentTaskRequest):
    """Free-form 'research assistance' entry point: e.g. 'find 3 recent papers
    on X, add the best one to my library, and summarize it.' The agent plans
    and executes tool calls, then returns a final synthesized answer."""
    steps, final_answer = agent.run_agent_task(req.instruction)
    return AgentTaskResponse(instruction=req.instruction, steps=steps, final_answer=final_answer)
