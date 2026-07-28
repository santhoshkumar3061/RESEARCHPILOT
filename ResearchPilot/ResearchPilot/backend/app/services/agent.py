"""
ResearchPilot agent orchestrator.

A minimal but real "AI agent" loop: the LLM proposes a short plan of tool
calls from a fixed toolset, we execute each tool locally, then the LLM
synthesizes a final answer from the tool outputs. This keeps agent behavior
inspectable and debuggable (each step is logged) rather than opaque.
"""
from app.models.schemas import AgentStep, Paper, PaperSource
from app.services import arxiv_client, library_store, llm_client, vector_store

TOOLS = ["search_papers", "add_to_library", "summarize_paper", "search_library"]


def _tool_search_papers(input_: dict) -> tuple[list[Paper], str]:
    query = input_.get("query", "")
    max_results = int(input_.get("max_results", 5))
    papers = arxiv_client.search_papers(query, max_results=max_results)
    summary = f"Found {len(papers)} papers for query '{query}'."
    return papers, summary


def _tool_add_to_library(input_: dict) -> tuple[dict, str]:
    paper_id = input_.get("paper_id")
    paper = arxiv_client.get_paper_by_id(paper_id) if paper_id else None
    if not paper:
        return {}, f"Could not find paper {paper_id} to add."
    from app.models.schemas import LibraryItem
    item = library_store.upsert_item(LibraryItem(paper=paper))
    return item.model_dump(), f"Added '{paper.title}' to library."


def _tool_summarize_paper(input_: dict) -> tuple[dict, str]:
    paper_id = input_.get("paper_id")
    item = library_store.get_item(paper_id) if paper_id else None
    paper = item.paper if item else arxiv_client.get_paper_by_id(paper_id)
    if not paper:
        return {}, f"Could not find paper {paper_id} to summarize."
    result = llm_client.summarize_paper(paper.title, paper.abstract, "", "concise")
    return result, f"Summarized '{paper.title}'."


def _tool_search_library(input_: dict) -> tuple[list[dict], str]:
    query = input_.get("query", "").lower()
    items = library_store.list_items()
    matched = [i for i in items if query in i.paper.title.lower() or query in i.paper.abstract.lower()]
    return [i.model_dump() for i in matched], f"Matched {len(matched)} library items for '{query}'."


_TOOL_FUNCS = {
    "search_papers": _tool_search_papers,
    "add_to_library": _tool_add_to_library,
    "summarize_paper": _tool_summarize_paper,
    "search_library": _tool_search_library,
}


def run_agent_task(instruction: str) -> tuple[list[AgentStep], str]:
    plan = llm_client.plan_agent_steps(instruction, TOOLS)
    if not plan:
        # Fallback: treat the instruction as a direct library/global question
        chunks = vector_store.query_similar_chunks(instruction)
        answer = llm_client.answer_with_context(instruction, chunks, [])
        return [], answer

    steps: list[AgentStep] = []
    step_outputs = []
    for raw_step in plan[:4]:  # hard cap to keep runaway plans bounded
        tool_name = raw_step.get("tool")
        tool_input = raw_step.get("input", {})
        func = _TOOL_FUNCS.get(tool_name)
        if not func:
            steps.append(AgentStep(tool=tool_name or "unknown", input=tool_input,
                                    output_summary="Skipped: unknown tool."))
            continue
        output, summary = func(tool_input)
        steps.append(AgentStep(tool=tool_name, input=tool_input, output_summary=summary))
        step_outputs.append({"tool": tool_name, "output": output})

    final_answer = llm_client.synthesize_agent_answer(instruction, step_outputs)
    return steps, final_answer
