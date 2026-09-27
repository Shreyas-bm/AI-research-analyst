"""SQLAlchemy Database ORM Models for DecisionLens"""
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import (
    Column, String, Text, Float, Integer, DateTime, Boolean, ForeignKey, JSON
)
from sqlalchemy.orm import relationship
from backend.app.database.session import Base

def utc_now():
    return datetime.now(timezone.utc)

class ResearchRun(Base):
    __tablename__ = "research_runs"

    id = Column(String(64), primary_key=True, index=True)
    question = Column(Text, nullable=False)
    context_data = Column(JSON, default=dict)
    constraints_data = Column(JSON, default=list)
    preferred_alternatives = Column(JSON, default=list)
    status = Column(String(32), default="queued", index=True)  # queued, running, completed, failed
    recommendation_headline = Column(Text, nullable=True)
    confidence_score = Column(Float, nullable=True)
    confidence_reasoning = Column(Text, nullable=True)
    report_data = Column(JSON, nullable=True)  # Full serialized DecisionReport
    total_tokens = Column(Integer, default=0)
    estimated_cost_usd = Column(Float, default=0.0)
    total_latency_ms = Column(Integer, default=0)
    created_at = Column(DateTime, default=utc_now, index=True)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)

    # Relationships
    tasks = relationship("ResearchTaskRecord", back_populates="run", cascade="all, delete-orphan")
    sources = relationship("SourceRecord", back_populates="run", cascade="all, delete-orphan")
    claims = relationship("ClaimRecord", back_populates="run", cascade="all, delete-orphan")
    trace_events = relationship("TraceEventRecord", back_populates="run", cascade="all, delete-orphan")

class ResearchTaskRecord(Base):
    __tablename__ = "research_tasks"

    id = Column(String(64), primary_key=True, index=True)
    research_run_id = Column(String(64), ForeignKey("research_runs.id"), nullable=False, index=True)
    task_type = Column(String(32), nullable=False)  # web, rag, sql, calc, analysis, critique, verification
    description = Column(Text, nullable=False)
    query_or_input = Column(Text, nullable=False)
    purpose = Column(Text, nullable=True)
    status = Column(String(32), default="queued")  # queued, running, completed, failed
    result_summary = Column(Text, nullable=True)
    duration_ms = Column(Integer, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)

    run = relationship("ResearchRun", back_populates="tasks")

class SourceRecord(Base):
    __tablename__ = "sources"

    id = Column(String(64), primary_key=True, index=True)
    research_run_id = Column(String(64), ForeignKey("research_runs.id"), nullable=False, index=True)
    source_type = Column(String(32), nullable=False)  # web, document, sql_result, calculation
    title = Column(String(256), nullable=False)
    url = Column(Text, nullable=True)
    excerpt = Column(Text, nullable=False)
    metadata_json = Column(JSON, default=dict)
    credibility_score = Column(Float, default=1.0)
    retrieved_at = Column(DateTime, default=utc_now)

    run = relationship("ResearchRun", back_populates="sources")

class ClaimRecord(Base):
    __tablename__ = "claims"

    id = Column(String(64), primary_key=True, index=True)
    research_run_id = Column(String(64), ForeignKey("research_runs.id"), nullable=False, index=True)
    claim_text = Column(Text, nullable=False)
    verification_status = Column(String(32), default="UNSUPPORTED")  # SUPPORTED, PARTIALLY_SUPPORTED, UNSUPPORTED, CONTRADICTED
    supporting_source_ids = Column(JSON, default=list)
    contradicting_source_ids = Column(JSON, default=list)
    verifier_notes = Column(Text, nullable=True)
    confidence = Column(Float, default=0.5)

    run = relationship("ResearchRun", back_populates="claims")

class TraceEventRecord(Base):
    __tablename__ = "trace_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    research_run_id = Column(String(64), ForeignKey("research_runs.id"), nullable=False, index=True)
    node_name = Column(String(64), nullable=False)
    event_type = Column(String(32), nullable=False)  # start, complete, tool_call, error
    details = Column(JSON, default=dict)
    duration_ms = Column(Integer, default=0)
    timestamp = Column(DateTime, default=utc_now)

    run = relationship("ResearchRun", back_populates="trace_events")

class DocumentRecord(Base):
    __tablename__ = "documents"

    id = Column(String(64), primary_key=True, index=True)
    filename = Column(String(256), nullable=False)
    file_type = Column(String(32), nullable=False)  # pdf, md, txt
    file_size_bytes = Column(Integer, default=0)
    chunk_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=utc_now)
    extracted_text_preview = Column(Text, nullable=True)

class EvaluationRunRecord(Base):
    __tablename__ = "evaluation_runs"

    id = Column(String(64), primary_key=True, index=True)
    configuration_name = Column(String(64), nullable=False)  # Baseline, Basic RAG, Hybrid RAG, Full Agentic
    dataset_name = Column(String(64), default="standard_50")
    total_cases = Column(Integer, default=0)
    citation_coverage = Column(Float, default=0.0)
    faithfulness_score = Column(Float, default=0.0)
    answer_relevance = Column(Float, default=0.0)
    recall_at_5 = Column(Float, default=0.0)
    precision_at_5 = Column(Float, default=0.0)
    avg_latency_ms = Column(Float, default=0.0)
    avg_token_cost_usd = Column(Float, default=0.0)
    results_detail = Column(JSON, default=dict)
    created_at = Column(DateTime, default=utc_now)
