"""
LLM client wrapping the Anthropic Messages API.

All prompting logic (summarization styles, RAG answer synthesis, agent
planning) funnels through this module so model/provider can be swapped in
one place.
"""
import json

from anthropic import Anthropic
from tenacity import retry, stop_after_attempt, wait_exponential

from app.config import get_settings

settings = get_settings()
_client = Anthropic(api_key=settings.anthropic_api_key)

SUMMARY_STYLE_PROMPTS = {
    "concise": "Write a tight 3-4 sentence summary a busy researcher can skim in 10 seconds.",
    "detailed": "Write a thorough summary covering motivation, method, and results in 2-3 short paragraphs.",
    "eli5": "Explain the paper as if to a smart undergraduate with no background in the subfield.",
    "critical": "Summarize the paper AND critically assess its methodology, novelty, and weaknesses.",
}


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=8))
def _complete(system: str, user: str, max_tokens: int | None = None) -> str:
    response = _client.messages.create(
        model=settings.llm_model,
        max_tokens=max_tokens or settings.llm_max_tokens,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    return "".join(block.text for block in response.content if block.type == "text")


def summarize_paper(title: str, abstract: str, extra_text: str, style: str) -> dict:
    """Produce a structured summary: prose summary + key findings + limitations."""
    style_instruction = SUMMARY_STYLE_PROMPTS.get(style, SUMMARY_STYLE_PROMPTS["concise"])
    system = (
        "You are a research assistant that summarizes academic papers accurately. "
        "Never invent results that aren't supported by the given text. "
        "Respond ONLY with valid JSON, no markdown fences, matching this schema: "
        '{"summary": str, "key_findings": [str], "limitations": [str]}'
    )
    user = (
        f"{style_instruction}\n\n"
        f"Title: {title}\n\nAbstract: {abstract}\n\n"
        f"Additional context (may be empty): {extra_text[:6000]}"
    )
    raw = _complete(system, user)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # Fallback: model didn't return clean JSON — degrade gracefully
        return {"summary": raw.strip(), "key_findings": [], "limitations": []}


def answer_with_context(question: str, chunks: list[dict], history: list[dict]) -> str:
    """RAG-style answer synthesis grounded in retrieved chunks."""
    context_block = "\n\n".join(
        f"[Source: {c['metadata'].get('paper_title', 'unknown')}]\n{c['text']}"
        for c in chunks
    ) or "No relevant context was retrieved."

    system = (
        "You are ResearchPilot, a research assistant. Answer the user's question "
        "using ONLY the provided context chunks. If the context doesn't contain "
        "the answer, say so plainly instead of guessing. Cite paper titles inline "
        "when you use a fact from them."
    )
    history_block = "\n".join(f"{m['role']}: {m['content']}" for m in history[-6:])

    user = (
        f"Conversation so far:\n{history_block}\n\n"
        f"Retrieved context:\n{context_block}\n\n"
        f"Question: {question}"
    )
    return _complete(system, user)


def plan_agent_steps(instruction: str, available_tools: list[str]) -> list[dict]:
    """Ask the LLM to break a free-form instruction into an ordered tool-call
    plan. Returns a list of {"tool": ..., "input": {...}} dicts."""
    system = (
        "You are the planning module of a research agent. Given a user "
        "instruction and a list of available tools, output a JSON array of "
        "steps to execute in order. Each step is "
        '{"tool": "<tool_name>", "input": {...}}. '
        f"Available tools: {', '.join(available_tools)}. "
        "Keep plans short (max 4 steps). Respond ONLY with the JSON array."
    )
    raw = _complete(system, instruction, max_tokens=512)
    try:
        plan = json.loads(raw)
        return plan if isinstance(plan, list) else []
    except json.JSONDecodeError:
        return []


def synthesize_agent_answer(instruction: str, step_outputs: list[dict]) -> str:
    system = (
        "You are ResearchPilot's agent. Given the original instruction and the "
        "outputs of the tool calls that were executed, write a clear final "
        "answer for the user."
    )
    user = f"Instruction: {instruction}\n\nStep outputs:\n{json.dumps(step_outputs, default=str)}"
    return _complete(system, user)
