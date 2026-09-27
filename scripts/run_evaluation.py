"""CLI Runner for DecisionLens Evaluation and Benchmark Suite"""
import argparse
import asyncio
import sys
import os

# Add workspace to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.config import settings
from backend.app.database.session import async_session_factory, init_db
from backend.app.evaluation.dataset import BENCHMARK_CASES
from backend.app.evaluation.runner import EvaluationRunner

async def main():
    parser = argparse.ArgumentParser(description="DecisionLens Automated Benchmark Suite CLI")
    parser.add_argument(
        "--config",
        type=str,
        default="Full Agentic (DecisionLens)",
        choices=[
            "Baseline (Direct LLM)",
            "Basic RAG (Vector Only)",
            "Full Agentic (DecisionLens)"
        ],
        help="Pipeline configuration to evaluate"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit number of benchmark cases to run"
    )
    parser.add_argument(
        "--provider",
        type=str,
        default="mock",
        help="LLM Provider override (mock, gemini, openai, nvidia)"
    )

    args = parser.parse_args()

    # Override provider if specified
    if args.provider:
        settings.LLM_PROVIDER = args.provider

    await init_db()

    cases = BENCHMARK_CASES[:args.limit] if args.limit else BENCHMARK_CASES

    print("\n" + "=" * 65)
    print("🚀  DECISIONLENS EVALUATION BENCHMARK RUNNER")
    print("=" * 65)
    print(f"• Configuration : {args.config}")
    print(f"• LLM Provider  : {settings.LLM_PROVIDER}")
    print(f"• Cases Count   : {len(cases)}")
    print("=" * 65 + "\n")

    async with async_session_factory() as session:
        summary = await EvaluationRunner.run_benchmark(
            config_name=args.config,
            cases=cases,
            db_session=session
        )

    print("\n" + "📊  EVALUATION RESULTS SUMMARY")
    print("-" * 65)
    print(f"• Citation Coverage (%)   : {summary.citation_coverage * 100:.1f}%")
    print(f"• Faithfulness Score     : {summary.faithfulness_score:.4f}")
    print(f"• Answer Relevance       : {summary.answer_relevance:.4f}")
    print(f"• Recall@5               : {summary.recall_at_5:.4f}")
    print(f"• Recommendation Match   : {summary.precision_at_5 * 100:.1f}%")
    print(f"• Average Latency        : {summary.avg_latency_ms:.1f} ms")
    print(f"• Avg Token Cost         : ${summary.avg_token_cost_usd:.6f}")
    print("-" * 65)

    print("\nCase Breakdown:")
    for c in summary.case_results:
        print(f" [{c['case_id']}] {c['question'][:50]}... -> Latency: {c['latency_ms']}ms | Cov: {c['citation_coverage']*100:.0f}%")

    print("\n✅ Benchmark execution persisted to database successfully.\n")

if __name__ == "__main__":
    asyncio.run(main())
