"""LangGraph Agent State Definition for Decision Analysis Workflow"""
from typing import TypedDict, List, Dict, Any, Optional
from backend.app.schemas.decision import ParsedDecision, DecisionContext
from backend.app.schemas.research import ResearchTask, TaskStatus
from backend.app.schemas.evidence import EvidenceItem
from backend.app.schemas.claim import ClaimItem
from backend.app.schemas.report import DecisionReport, CriticReview

class AgentState(TypedDict):
    run_id: str
    question: str
    context: Dict[str, Any]
    constraints: List[str]
    preferred_alternatives: List[str]
    document_ids: List[str]

    # Parsed decision objective & alternatives
    parsed_decision: Optional[Dict[str, Any]]

    # Research tasks & evidence
    tasks: List[Dict[str, Any]]
    evidence_items: List[Dict[str, Any]]
    
    # Loop and sufficiency controls
    research_iterations: int
    max_research_iterations: int
    is_evidence_sufficient: bool

    # Synthesis & Critic
    draft_report: Optional[Dict[str, Any]]
    critic_review: Optional[Dict[str, Any]]
    critique_iterations: int
    max_critique_iterations: int

    # Claim verification
    claims: List[Dict[str, Any]]

    # Final assembled report
    final_report: Optional[Dict[str, Any]]

    # Token & Latency metrics
    total_tokens: int
    estimated_cost_usd: float
    total_latency_ms: int
    errors: List[str]
