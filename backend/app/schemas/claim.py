"""Claim Verification and Grounding Schemas"""
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field
import uuid

class VerificationStatus(str, Enum):
    SUPPORTED = "SUPPORTED"
    PARTIALLY_SUPPORTED = "PARTIALLY_SUPPORTED"
    UNSUPPORTED = "UNSUPPORTED"
    CONTRADICTED = "CONTRADICTED"

class ClaimItem(BaseModel):
    id: str = Field(default_factory=lambda: f"claim-{uuid.uuid4().hex[:8]}")
    claim_text: str = Field(..., description="The exact sentence or assertion making a factual or comparative claim")
    verification_status: VerificationStatus = Field(default=VerificationStatus.UNSUPPORTED)
    supporting_source_ids: List[str] = Field(default_factory=list, description="IDs of matching EvidenceItem sources")
    contradicting_source_ids: List[str] = Field(default_factory=list, description="IDs of contradicting EvidenceItem sources")
    verifier_notes: Optional[str] = Field(None, description="Explanation of why this claim is supported, weak, or contradicted")
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
