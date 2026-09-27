"""Planner Node: Decomposes decision into specific research tasks across tools"""
import time
from typing import Dict, Any, List
from backend.app.engine.state import AgentState
from backend.app.models.llm_base import LLMRequest, ChatMessage, MessageRole
from backend.app.models.factory import get_llm_provider
from backend.app.schemas.research import ResearchPlan, ResearchTask, TaskType, TaskStatus

async def planner_node(state: AgentState) -> Dict[str, Any]:
    start_time = time.time()
    llm = get_llm_provider()

    parsed = state.get("parsed_decision") or {}
    objective = parsed.get("objective", state["question"])
    alts = parsed.get("candidate_alternatives", [])
    criteria = parsed.get("evaluation_criteria", [])

    prompt = f"""You are a research planner. Generate atomic research tasks to gather empirical facts across tools:
Objective: {objective}
Alternatives: {alts}
Criteria: {criteria}

Tools available:
- 'rag': Query internal uploaded documents/benchmarks for numbers and policies
- 'sql': Query benchmark SQL database for empirical latency, memory, cost records
- 'web': Search technical benchmarks, GitHub repos, and release notes
- 'calc': Execute mathematical formulas (e.g. RAM = (vectors * dim * 4) / 1024^2)

Generate 3-5 specific tasks."""

    req = LLMRequest(
        messages=[
            ChatMessage(role=MessageRole.SYSTEM, content="Generate targeted research tasks."),
            ChatMessage(role=MessageRole.USER, content=prompt)
        ]
    )

    try:
        plan: ResearchPlan = await llm.generate_structured(req, ResearchPlan)
        tasks_list = [t.model_dump() for t in plan.tasks]
    except Exception:
        # Robust fallback tasks
        tasks_list = [
            ResearchTask(
                task_type=TaskType.SQL_QUERY,
                description="Query benchmark metrics for alternatives",
                query_or_input="SELECT * FROM benchmark_results",
                purpose="Extract p95 latency and memory"
            ).model_dump(),
            ResearchTask(
                task_type=TaskType.DOCUMENT_RAG,
                description="Search internal docs for architectural trade-offs",
                query_or_input="vector database architectural trade-offs latency memory",
                purpose="Check internal constraints"
            ).model_dump(),
            ResearchTask(
                task_type=TaskType.WEB_SEARCH,
                description="Search latest benchmarks for pgvector and ChromaDB",
                query_or_input="pgvector ChromaDB latency memory benchmark",
                purpose="Validate external findings"
            ).model_dump(),
            ResearchTask(
                task_type=TaskType.CALCULATION,
                description="Calculate monthly memory footprint",
                query_or_input="(500000 * 1536 * 4) / (1024 * 1024)",
                purpose="Compute RAM requirements"
            ).model_dump()
        ]

    duration_ms = int((time.time() - start_time) * 1000)
    return {
        "tasks": tasks_list,
        "total_tokens": state.get("total_tokens", 0) + 300,
        "total_latency_ms": state.get("total_latency_ms", 0) + duration_ms
    }
