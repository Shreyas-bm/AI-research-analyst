"""Decision Report Schemas (14-part report across 4 UI bands)"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from backend.app.schemas.evidence import EvidenceItem
from backend.app.schemas.claim import ClaimItem

class AlternativeScore(BaseModel):
    name: str = Field(..., description="Name of the alternative (e.g. pgvector, ChromaDB)")
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    score: Optional[float] = Field(None, ge=0.0, le=10.0)

class ComparisonRow(BaseModel):
    criterion: str = Field(..., description="Evaluation dimension (e.g. Latency p95, Memory, ACID, Setup Cost)")
    values: Dict[str, str] = Field(..., description="Alternative name -> value string")
    winner: Optional[str] = None
    notes: Optional[str] = None

class QuantitativeAnalysis(BaseModel):
    summary: str = Field(..., description="Quantitative synthesis summary")
    comparison_table: List[ComparisonRow] = Field(default_factory=list)
    calculations_performed: List[str] = Field(default_factory=list)

class CriticReview(BaseModel):
    identified_risks: List[str] = Field(default_factory=list, description="Key operational, technical or financial risks")
    counterarguments: List[str] = Field(default_factory=list, description="Adversarial arguments against the primary recommendation")
    assumptions_stress_tested: List[str] = Field(default_factory=list, description="Assumptions that might fail under stress")
    what_would_change_recommendation: List[str] = Field(
        default_factory=list,
        description="Conditions under which another alternative would be superior"
    )

class ConfidenceIndicator(BaseModel):
    score: float = Field(..., ge=0.0, le=1.0, description="Overall confidence score (e.g. 0.85)")
    level: str = Field(..., description="High / Moderate / Low")
    reasoning: str = Field(..., description="Monospace-formatted reasoning string (e.g. 'Sensitive to traffic growth assumption')")

class VerdictBand(BaseModel):
    decision_question: str
    recommendation_headline: str = Field(..., description="Direct sentence recommendation")
    confidence: ConfidenceIndicator
    alternatives: List[AlternativeScore] = Field(default_factory=list)

class EvidenceBand(BaseModel):
    context_summary: str
    decision_criteria: List[str] = Field(default_factory=list)
    quantitative_analysis: QuantitativeAnalysis
    key_trade_offs: List[str] = Field(default_factory=list)
    claims: List[ClaimItem] = Field(default_factory=list)

class ChallengeBand(BaseModel):
    critic_review: CriticReview
    material_assumptions: List[str] = Field(default_factory=list)

class TraceBand(BaseModel):
    run_id: str
    total_tokens: int = 0
    estimated_cost_usd: float = 0.0
    total_latency_ms: int = 0
    tool_invocations_count: int = 0
    sources: List[EvidenceItem] = Field(default_factory=list)

class DecisionReport(BaseModel):
    id: str
    question: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    verdict: VerdictBand
    evidence: EvidenceBand
    challenge: ChallengeBand
    trace: TraceBand
    raw_markdown: Optional[str] = None
