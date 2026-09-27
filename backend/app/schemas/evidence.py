"""Evidence and Source Schemas"""
from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone
import uuid

class SourceType(str, Enum):
    WEB = "web"
    DOCUMENT = "document"
    VECTOR_DB = "vector_db"
    SQL_RESULT = "sql_result"
    CALCULATION = "calculation"
    SYNTHESIS = "synthesis"

class SourceMetadata(BaseModel):
    author: Optional[str] = None
    publish_date: Optional[str] = None
    page_number: Optional[int] = None
    section: Optional[str] = None
    query_used: Optional[str] = None
    document_id: Optional[str] = None
    table_name: Optional[str] = None
    custom: Dict[str, Any] = Field(default_factory=dict)

class EvidenceItem(BaseModel):
    id: str = Field(default_factory=lambda: f"src-{uuid.uuid4().hex[:8]}")
    source_type: SourceType = Field(..., description="Origin of this evidence")
    title: str = Field(..., description="Title of document, web page, or data query")
    url: Optional[str] = Field(None, description="External URL or internal file path")
    excerpt: str = Field(..., description="Exact relevant passage or table row values")
    metadata: SourceMetadata = Field(default_factory=SourceMetadata)
    retrieved_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    credibility_score: float = Field(default=1.0, ge=0.0, le=1.0, description="Reliability score between 0 and 1")
