"""Decision Intake and Parsing Schemas"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class DecisionContext(BaseModel):
    monthly_documents: Optional[int] = Field(None, description="Volume of documents or queries processed monthly")
    team_size: Optional[int] = Field(None, description="Size of engineering or decision team")
    cloud: Optional[str] = Field(None, description="Target deployment cloud (AWS, GCP, Azure, Self-hosted)")
    budget: Optional[float] = Field(None, description="Budget constraint in USD/INR")
    timeframe: Optional[str] = Field(None, description="Delivery or migration timeframe")
    custom_context: Dict[str, Any] = Field(default_factory=dict, description="Additional arbitrary key-value context")

class DecisionIntakeRequest(BaseModel):
    question: str = Field(..., min_length=5, description="Primary decision question")
    context: Optional[DecisionContext] = Field(default_factory=DecisionContext, description="Structured constraints and context")
    constraints: List[str] = Field(default_factory=list, description="Explicit user constraints (e.g. low latency, zero API cost)")
    preferred_alternatives: List[str] = Field(default_factory=list, description="User-suggested candidate alternatives")
    document_ids: List[str] = Field(default_factory=list, description="Referenced uploaded document IDs")

class ParsedDecision(BaseModel):
    objective: str = Field(..., description="Extracted core decision objective")
    candidate_alternatives: List[str] = Field(default_factory=list, description="List of alternatives to compare")
    identified_constraints: List[str] = Field(default_factory=list, description="Normalized constraints")
    evaluation_criteria: List[str] = Field(default_factory=list, description="Key criteria to evaluate alternatives against")
    decision_domain: str = Field("technology", description="Detected domain (technology, architecture, vendor, etc.)")
