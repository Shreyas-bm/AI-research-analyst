"""Automated Evaluation and Comparative Benchmark Endpoints"""
from typing import List, Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database.session import get_db
from backend.app.database import crud
from backend.app.database.models import User
from backend.app.api.auth import get_current_user
from backend.app.evaluation.dataset import BENCHMARK_CASES
from backend.app.evaluation.runner import EvaluationRunner, BenchmarkResultSummary

router = APIRouter(prefix="/api/eval", tags=["Evaluation & Benchmarking"])

class EvalRunRequest(BaseModel):
    configuration_name: str = Field(default="Full Agentic (DecisionLens)")
    case_ids: Optional[List[str]] = Field(default=None)

@router.post("/run", response_model=BenchmarkResultSummary)
async def run_evaluation(
    request: EvalRunRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Run automated benchmarks against selected pipeline configuration."""
    selected_cases = None
    if request.case_ids:
        selected_cases = [c for c in BENCHMARK_CASES if c.case_id in request.case_ids]

    summary = await EvaluationRunner.run_benchmark(
        config_name=request.configuration_name,
        cases=selected_cases,
        db_session=db
    )
    return summary

@router.get("/runs")
async def list_evaluation_runs(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve history of all comparative evaluation benchmark runs."""
    runs = await crud.list_evaluation_runs(db)
    return [
        {
            "id": r.id,
            "configuration_name": r.configuration_name,
            "dataset_name": r.dataset_name,
            "total_cases": r.total_cases,
            "citation_coverage": r.citation_coverage,
            "faithfulness_score": r.faithfulness_score,
            "answer_relevance": r.answer_relevance,
            "recall_at_5": r.recall_at_5,
            "precision_at_5": r.precision_at_5,
            "avg_latency_ms": r.avg_latency_ms,
            "avg_token_cost_usd": r.avg_token_cost_usd,
            "created_at": r.created_at.isoformat() if r.created_at else None
        }
        for r in runs
    ]

@router.get("/dataset")
async def get_benchmark_dataset():
    """Retrieve the curated standard benchmark cases."""
    return BENCHMARK_CASES
