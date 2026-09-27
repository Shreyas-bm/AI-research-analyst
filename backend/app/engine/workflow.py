"""LangGraph Decision Analysis Workflow Assembler and Runner"""
import uuid
import time
from typing import Dict, Any, Optional, List
from langgraph.graph import StateGraph, END
from backend.app.engine.state import AgentState
from backend.app.engine.nodes.intake_node import intake_node
from backend.app.engine.nodes.planner_node import planner_node
from backend.app.engine.nodes.research_node import research_node
from backend.app.engine.nodes.synthesis_node import synthesis_node
from backend.app.engine.nodes.critic_node import critic_node
from backend.app.engine.nodes.verifier_node import verifier_node
from backend.app.schemas.report import DecisionReport

def check_evidence_sufficiency(state: AgentState) -> str:
    """Conditional routing edge checking if evidence suffices or re-planning is required."""
    is_sufficient = state.get("is_evidence_sufficient", False)
    iterations = state.get("research_iterations", 1)
    max_iterations = state.get("max_research_iterations", 2)

    if not is_sufficient and iterations < max_iterations:
        return "planner"
    return "synthesis"

def build_decision_graph() -> StateGraph:
    """Construct and compile the multi-agent decision intelligence graph."""
    builder = StateGraph(AgentState)

    # Add Nodes
    builder.add_node("intake", intake_node)
    builder.add_node("planner", planner_node)
    builder.add_node("research", research_node)
    builder.add_node("synthesis", synthesis_node)
    builder.add_node("critic", critic_node)
    builder.add_node("verifier", verifier_node)

    # Add Edges
    builder.set_entry_point("intake")
    builder.add_edge("intake", "planner")
    builder.add_edge("planner", "research")
    
    builder.add_conditional_edges(
        "research",
        check_evidence_sufficiency,
        {
            "planner": "planner",
            "synthesis": "synthesis"
        }
    )

    builder.add_edge("synthesis", "critic")
    builder.add_edge("critic", "verifier")
    builder.add_edge("verifier", END)

    return builder.compile()

# Singleton compiled workflow
decision_graph = build_decision_graph()

async def run_decision_workflow(
    question: str,
    context: Optional[Dict[str, Any]] = None,
    constraints: Optional[List[str]] = None,
    preferred_alternatives: Optional[List[str]] = None,
    document_ids: Optional[List[str]] = None,
    run_id: Optional[str] = None,
) -> DecisionReport:
    """Execute complete end-to-end decision workflow and return DecisionReport."""
    active_run_id = run_id or f"run-{uuid.uuid4().hex[:10]}"

    initial_state: AgentState = {
        "run_id": active_run_id,
        "question": question,
        "context": context or {},
        "constraints": constraints or [],
        "preferred_alternatives": preferred_alternatives or [],
        "document_ids": document_ids or [],
        "parsed_decision": None,
        "tasks": [],
        "evidence_items": [],
        "research_iterations": 0,
        "max_research_iterations": 2,
        "is_evidence_sufficient": False,
        "draft_report": None,
        "critic_review": None,
        "critique_iterations": 0,
        "max_critique_iterations": 1,
        "claims": [],
        "final_report": None,
        "total_tokens": 0,
        "estimated_cost_usd": 0.0,
        "total_latency_ms": 0,
        "errors": []
    }

    final_state = await decision_graph.ainvoke(initial_state)
    report_dict = final_state.get("final_report")
    if not report_dict:
        raise RuntimeError("Workflow execution completed without generating final report.")

    return DecisionReport.model_validate(report_dict)
