"""Research Task and Execution State Schemas"""
from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone
import uuid

class TaskType(str, Enum):
    WEB_SEARCH = "web"
    DOCUMENT_RAG = "rag"
    SQL_QUERY = "sql"
    CALCULATION = "calc"
    ANALYSIS = "analysis"
    CRITIQUE = "critique"
    VERIFICATION = "verification"

class TaskStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

class ResearchTask(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    task_type: TaskType = Field(..., description="Tool or agent type executing this task")
    description: str = Field(..., description="Human-readable description of what this task aims to find")
    query_or_input: str = Field(..., description="Exact search query, SQL, or calculation expression")
    purpose: str = Field(..., description="Why this evidence is needed for the decision")
    status: TaskStatus = Field(default=TaskStatus.QUEUED)
    result_summary: Optional[str] = None
    extracted_source_ids: List[str] = Field(default_factory=list)
    duration_ms: Optional[int] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None

class ResearchPlan(BaseModel):
    decision_id: str
    tasks: List[ResearchTask] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
