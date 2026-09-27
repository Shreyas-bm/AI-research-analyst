"""Intake Node: Formulates structured objective, alternatives, and constraints"""
import time
from typing import Dict, Any
from backend.app.engine.state import AgentState
from backend.app.models.llm_base import LLMRequest, ChatMessage, MessageRole
from backend.app.models.factory import get_llm_provider
from backend.app.schemas.decision import ParsedDecision

async def intake_node(state: AgentState) -> Dict[str, Any]:
    start_time = time.time()
    llm = get_llm_provider()

    question = state["question"]
    context = state.get("context", {})
    constraints = state.get("constraints", [])
    pref_alts = state.get("preferred_alternatives", [])

    prompt = f"""You are a senior decision architect. Parse this decision request into structured objectives, constraints, and comparison candidates.
Decision Question: {question}
User Context: {context}
Explicit Constraints: {constraints}
Preferred Alternatives: {pref_alts}

Identify:
1. Core objective
2. 2-4 candidate alternatives to evaluate
3. Concrete quantitative/qualitative constraints
4. Key decision criteria
5. Domain (database, cloud, architecture, tool, etc.)"""

    req = LLMRequest(
        messages=[
            ChatMessage(role=MessageRole.SYSTEM, content="Extract structured decision architecture parameters."),
            ChatMessage(role=MessageRole.USER, content=prompt)
        ]
    )

    try:
        parsed: ParsedDecision = await llm.generate_structured(req, ParsedDecision)
        parsed_dict = parsed.model_dump()
    except Exception:
        parsed_dict = {
            "objective": f"Evaluate alternatives for: {question}",
            "candidate_alternatives": pref_alts or ["Alternative A", "Alternative B"],
            "identified_constraints": constraints,
            "evaluation_criteria": ["Performance", "Cost", "Operational Complexity", "Scalability"],
            "decision_domain": "technology"
        }

    duration_ms = int((time.time() - start_time) * 1000)
    return {
        "parsed_decision": parsed_dict,
        "total_tokens": state.get("total_tokens", 0) + 250,
        "total_latency_ms": state.get("total_latency_ms", 0) + duration_ms
    }
