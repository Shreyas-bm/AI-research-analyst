"""FastAPI Decision Analysis Endpoints & Real-time SSE Execution Stream"""
import json
import uuid
import asyncio
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database.session import get_db
from backend.app.database import crud
from backend.app.schemas.decision import DecisionIntakeRequest
from backend.app.schemas.report import DecisionReport
from backend.app.engine.workflow import run_decision_workflow

router = APIRouter(prefix="/api/decision", tags=["Decision Intelligence"])

@router.post("/analyze", response_model=DecisionReport)
async def analyze_decision(
    request: DecisionIntakeRequest,
    db: AsyncSession = Depends(get_db)
):
    """Run full agentic decision analysis workflow and return structured 14-part report."""
    run_id = f"run-{uuid.uuid4().hex[:10]}"

    # 1. Log run initiation in database
    await crud.create_research_run(
        session=db,
        run_id=run_id,
        question=request.question,
        context_data=request.context.model_dump() if request.context else {},
        constraints_data=request.constraints,
        preferred_alternatives=request.preferred_alternatives
    )

    try:
        # 2. Execute workflow
        report: DecisionReport = await run_decision_workflow(
            question=request.question,
            context=request.context.model_dump() if request.context else {},
            constraints=request.constraints,
            preferred_alternatives=request.preferred_alternatives,
            document_ids=request.document_ids,
            run_id=run_id
        )

        # 3. Persist results in DB
        for idx, s in enumerate(report.trace.sources):
            unique_source_id = f"{run_id}-src-{idx+1}"
            await crud.create_source_record(
                session=db,
                source_id=unique_source_id,
                run_id=run_id,
                source_type=s.source_type.value,
                title=s.title,
                excerpt=s.excerpt,
                url=s.url,
                metadata_json=s.metadata.model_dump(mode="json") if s.metadata else {},
                credibility_score=s.credibility_score
            )

        for idx, c in enumerate(report.evidence.claims):
            unique_claim_id = f"{run_id}-claim-{idx+1}"
            await crud.create_claim_record(
                session=db,
                claim_id=unique_claim_id,
                run_id=run_id,
                claim_text=c.claim_text,
                verification_status=c.verification_status.value,
                supporting_source_ids=c.supporting_source_ids,
                contradicting_source_ids=c.contradicting_source_ids,
                verifier_notes=c.verifier_notes,
                confidence=c.confidence
            )

        await crud.update_research_run(
            session=db,
            run_id=run_id,
            status="completed",
            recommendation_headline=report.verdict.recommendation_headline,
            confidence_score=report.verdict.confidence.score,
            confidence_reasoning=report.verdict.confidence.reasoning,
            report_data=report.model_dump(mode="json"),
            total_tokens=report.trace.total_tokens,
            estimated_cost_usd=report.trace.estimated_cost_usd,
            total_latency_ms=report.trace.total_latency_ms
        )

        return report

    except Exception as e:
        await crud.update_research_run(
            session=db,
            run_id=run_id,
            status="failed",
            error_message=str(e)
        )
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.get("/history")
async def list_decision_history(
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """Retrieve history of decision analysis runs."""
    runs = await crud.list_research_runs(db, limit=limit)
    return [
        {
            "id": r.id,
            "question": r.question,
            "status": r.status,
            "recommendation_headline": r.recommendation_headline,
            "confidence_score": r.confidence_score,
            "created_at": r.created_at.isoformat() if r.created_at else None,
            "total_tokens": r.total_tokens,
            "total_latency_ms": r.total_latency_ms
        }
        for r in runs
    ]

@router.get("/{run_id}")
async def get_decision_run(
    run_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get single decision analysis run by ID."""
    run = await crud.get_research_run(db, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Decision run not found")

    return {
        "id": run.id,
        "question": run.question,
        "status": run.status,
        "report": run.report_data,
        "recommendation_headline": run.recommendation_headline,
        "confidence_score": run.confidence_score,
        "tasks": [{"id": t.id, "type": t.task_type, "status": t.status, "summary": t.result_summary} for t in run.tasks],
        "sources": [{"id": s.id, "title": s.title, "type": s.source_type, "url": s.url, "excerpt": s.excerpt} for s in run.sources],
        "claims": [{"id": c.id, "claim": c.claim_text, "status": c.verification_status, "sources": c.supporting_source_ids} for c in run.claims],
        "total_tokens": run.total_tokens,
        "total_latency_ms": run.total_latency_ms,
        "created_at": run.created_at.isoformat() if run.created_at else None
    }

@router.get("/{run_id}/stream")
async def stream_decision_execution(
    run_id: str,
    question: Optional[str] = None
):
    """Server-Sent Events (SSE) stream simulating real-time agent thought process and lifecycle stages."""
    async def event_generator():
        stages = [
            ("intake", "Parsing decision question, constraints, and candidate alternatives..."),
            ("planner", "Generating research tasks across SQL benchmarks, Web, and Calculation tools..."),
            ("research", "Executing empirical benchmark queries and retrieving document chunks..."),
            ("synthesis", "Drafting quantitative comparison matrix and headline recommendation..."),
            ("critic", "Adversarial stress-testing of assumptions and boundary conditions..."),
            ("verifier", "Verifying claim grounding and binding sentence-level citations..."),
            ("complete", "Decision analysis complete. Final report ready.")
        ]

        for stage, message in stages:
            payload = json.dumps({"stage": stage, "message": message, "run_id": run_id})
            yield f"event: {stage}\ndata: {payload}\n\n"
            await asyncio.sleep(0.3)

    return StreamingResponse(event_generator(), media_type="text/event-stream")
