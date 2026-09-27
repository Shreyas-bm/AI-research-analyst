"""Async CRUD operations for database layer"""
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from sqlalchemy import select, update, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from backend.app.database.models import (
    ResearchRun, ResearchTaskRecord, SourceRecord,
    ClaimRecord, TraceEventRecord, DocumentRecord, EvaluationRunRecord
)

# --- Research Run CRUD ---

async def create_research_run(
    session: AsyncSession,
    run_id: str,
    question: str,
    context_data: Dict[str, Any] = None,
    constraints_data: List[str] = None,
    preferred_alternatives: List[str] = None,
) -> ResearchRun:
    run = ResearchRun(
        id=run_id,
        question=question,
        context_data=context_data or {},
        constraints_data=constraints_data or [],
        preferred_alternatives=preferred_alternatives or [],
        status="queued",
        created_at=datetime.now(timezone.utc)
    )
    session.add(run)
    await session.commit()
    await session.refresh(run)
    return run

async def get_research_run(session: AsyncSession, run_id: str) -> Optional[ResearchRun]:
    stmt = (
        select(ResearchRun)
        .where(ResearchRun.id == run_id)
        .options(
            selectinload(ResearchRun.tasks),
            selectinload(ResearchRun.sources),
            selectinload(ResearchRun.claims),
            selectinload(ResearchRun.trace_events),
        )
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()

async def list_research_runs(session: AsyncSession, limit: int = 50) -> List[ResearchRun]:
    stmt = select(ResearchRun).order_by(desc(ResearchRun.created_at)).limit(limit)
    result = await session.execute(stmt)
    return list(result.scalars().all())

async def update_research_run(
    session: AsyncSession,
    run_id: str,
    **kwargs
) -> Optional[ResearchRun]:
    stmt = (
        update(ResearchRun)
        .where(ResearchRun.id == run_id)
        .values(**kwargs)
        .execution_options(synchronize_session="fetch")
    )
    await session.execute(stmt)
    await session.commit()
    return await get_research_run(session, run_id)

# --- Task CRUD ---

async def create_task_record(
    session: AsyncSession,
    task_id: str,
    run_id: str,
    task_type: str,
    description: str,
    query_or_input: str,
    purpose: Optional[str] = None
) -> ResearchTaskRecord:
    task = ResearchTaskRecord(
        id=task_id,
        research_run_id=run_id,
        task_type=task_type,
        description=description,
        query_or_input=query_or_input,
        purpose=purpose,
        status="queued"
    )
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task

async def update_task_record(
    session: AsyncSession,
    task_id: str,
    **kwargs
) -> Optional[ResearchTaskRecord]:
    stmt = (
        update(ResearchTaskRecord)
        .where(ResearchTaskRecord.id == task_id)
        .values(**kwargs)
        .execution_options(synchronize_session="fetch")
    )
    await session.execute(stmt)
    await session.commit()
    result = await session.execute(select(ResearchTaskRecord).where(ResearchTaskRecord.id == task_id))
    return result.scalar_one_or_none()

# --- Sources CRUD ---

async def create_source_record(
    session: AsyncSession,
    source_id: str,
    run_id: str,
    source_type: str,
    title: str,
    excerpt: str,
    url: Optional[str] = None,
    metadata_json: Dict[str, Any] = None,
    credibility_score: float = 1.0
) -> SourceRecord:
    source = SourceRecord(
        id=source_id,
        research_run_id=run_id,
        source_type=source_type,
        title=title,
        excerpt=excerpt,
        url=url,
        metadata_json=metadata_json or {},
        credibility_score=credibility_score,
        retrieved_at=datetime.now(timezone.utc)
    )
    session.add(source)
    await session.commit()
    await session.refresh(source)
    return source

async def get_sources_for_run(session: AsyncSession, run_id: str) -> List[SourceRecord]:
    stmt = select(SourceRecord).where(SourceRecord.research_run_id == run_id).order_by(SourceRecord.retrieved_at)
    result = await session.execute(stmt)
    return list(result.scalars().all())

# --- Claims CRUD ---

async def create_claim_record(
    session: AsyncSession,
    claim_id: str,
    run_id: str,
    claim_text: str,
    verification_status: str = "UNSUPPORTED",
    supporting_source_ids: List[str] = None,
    contradicting_source_ids: List[str] = None,
    verifier_notes: Optional[str] = None,
    confidence: float = 0.5
) -> ClaimRecord:
    claim = ClaimRecord(
        id=claim_id,
        research_run_id=run_id,
        claim_text=claim_text,
        verification_status=verification_status,
        supporting_source_ids=supporting_source_ids or [],
        contradicting_source_ids=contradicting_source_ids or [],
        verifier_notes=verifier_notes,
        confidence=confidence
    )
    session.add(claim)
    await session.commit()
    await session.refresh(claim)
    return claim

async def get_claims_for_run(session: AsyncSession, run_id: str) -> List[ClaimRecord]:
    stmt = select(ClaimRecord).where(ClaimRecord.research_run_id == run_id)
    result = await session.execute(stmt)
    return list(result.scalars().all())

# --- Trace CRUD ---

async def log_trace_event(
    session: AsyncSession,
    run_id: str,
    node_name: str,
    event_type: str,
    details: Dict[str, Any] = None,
    duration_ms: int = 0
) -> TraceEventRecord:
    event = TraceEventRecord(
        research_run_id=run_id,
        node_name=node_name,
        event_type=event_type,
        details=details or {},
        duration_ms=duration_ms,
        timestamp=datetime.now(timezone.utc)
    )
    session.add(event)
    await session.commit()
    await session.refresh(event)
    return event

async def get_trace_events_for_run(session: AsyncSession, run_id: str) -> List[TraceEventRecord]:
    stmt = select(TraceEventRecord).where(TraceEventRecord.research_run_id == run_id).order_by(TraceEventRecord.timestamp)
    result = await session.execute(stmt)
    return list(result.scalars().all())

# --- Documents CRUD ---

async def create_document_record(
    session: AsyncSession,
    doc_id: str,
    filename: str,
    file_type: str,
    file_size_bytes: int,
    chunk_count: int = 0,
    extracted_text_preview: Optional[str] = None
) -> DocumentRecord:
    doc = DocumentRecord(
        id=doc_id,
        filename=filename,
        file_type=file_type,
        file_size_bytes=file_size_bytes,
        chunk_count=chunk_count,
        extracted_text_preview=extracted_text_preview,
        created_at=datetime.now(timezone.utc)
    )
    session.add(doc)
    await session.commit()
    await session.refresh(doc)
    return doc

async def list_documents(session: AsyncSession) -> List[DocumentRecord]:
    stmt = select(DocumentRecord).order_by(desc(DocumentRecord.created_at))
    result = await session.execute(stmt)
    return list(result.scalars().all())

# --- Evaluation CRUD ---

async def create_evaluation_run(
    session: AsyncSession,
    eval_id: str,
    config_name: str,
    total_cases: int,
    citation_coverage: float,
    faithfulness_score: float,
    answer_relevance: float,
    recall_at_5: float,
    precision_at_5: float,
    avg_latency_ms: float,
    avg_token_cost_usd: float,
    results_detail: Dict[str, Any] = None
) -> EvaluationRunRecord:
    eval_record = EvaluationRunRecord(
        id=eval_id,
        configuration_name=config_name,
        total_cases=total_cases,
        citation_coverage=citation_coverage,
        faithfulness_score=faithfulness_score,
        answer_relevance=answer_relevance,
        recall_at_5=recall_at_5,
        precision_at_5=precision_at_5,
        avg_latency_ms=avg_latency_ms,
        avg_token_cost_usd=avg_token_cost_usd,
        results_detail=results_detail or {},
        created_at=datetime.now(timezone.utc)
    )
    session.add(eval_record)
    await session.commit()
    await session.refresh(eval_record)
    return eval_record

async def list_evaluation_runs(session: AsyncSession) -> List[EvaluationRunRecord]:
    stmt = select(EvaluationRunRecord).order_by(desc(EvaluationRunRecord.created_at))
    result = await session.execute(stmt)
    return list(result.scalars().all())
