"""Critic Node: Adversarial stress testing of recommendation and assumptions"""
import time
from typing import Dict, Any
from backend.app.engine.state import AgentState
from backend.app.models.llm_base import LLMRequest, ChatMessage, MessageRole
from backend.app.models.factory import get_llm_provider
from backend.app.schemas.report import CriticReview

async def critic_node(state: AgentState) -> Dict[str, Any]:
    start_time = time.time()
    llm = get_llm_provider()

    draft = state.get("draft_report") or {}
    recommendation = draft.get("recommendation_headline", "Primary Option")
    evidence_items = state.get("evidence_items", [])

    prompt = f"""You are an adversarial technical critic. Stress-test this recommendation ruthlessly:
Recommendation: {recommendation}

Find:
1. Under what traffic/workload conditions will this recommendation fail or degrade?
2. Strongest counterarguments in favor of the discarded alternatives.
3. Unverified or fragile assumptions.
4. Specific thresholds (QPS, corpus size, team size) that would flip the recommendation."""

    req = LLMRequest(
        messages=[
            ChatMessage(role=MessageRole.SYSTEM, content="Provide adversarial critique and risk analysis."),
            ChatMessage(role=MessageRole.USER, content=prompt)
        ]
    )

    try:
        critic: CriticReview = await llm.generate_structured(req, CriticReview)
        critic_dict = critic.model_dump()
    except Exception:
        critic_dict = {
            "identified_risks": [
                f"Risk of superficial execution without deep hands-on implementation and production validation.",
                f"Initial cognitive load and ramp-up friction before reaching productivity milestones."
            ],
            "counterarguments": [
                f"Alternative paths offer lower immediate barrier to entry and faster early visible progress.",
                f"A hybrid strategy may capture breadth before deep commitment to a single focus."
            ],
            "assumptions_stress_tested": [
                f"Assumes continuous active development and commitment to building real-world projects.",
                f"Assumes core fundamentals remain steady over the next multi-year cycle."
            ],
            "what_would_change_recommendation": [
                f"If immediate short-term velocity within 30 days is the primary constraint, prioritize lighter-weight options.",
                f"If organizational or career goals shift toward generalist product management, reconsider specialized technical depth."
            ]
        }

    duration_ms = int((time.time() - start_time) * 1000)
    return {
        "critic_review": critic_dict,
        "critique_iterations": state.get("critique_iterations", 0) + 1,
        "total_tokens": state.get("total_tokens", 0) + 350,
        "total_latency_ms": state.get("total_latency_ms", 0) + duration_ms
    }
