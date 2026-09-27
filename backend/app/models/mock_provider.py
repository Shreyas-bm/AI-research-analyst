"""Deterministic Mock LLM Provider for offline development, CI, and zero-cost testing"""
import json
from typing import Type, TypeVar, Any
from pydantic import BaseModel
from backend.app.models.llm_base import LLMProvider, LLMRequest, LLMResponse
from backend.app.schemas.decision import ParsedDecision
from backend.app.schemas.research import ResearchPlan, ResearchTask, TaskType, TaskStatus
from backend.app.schemas.claim import ClaimItem, VerificationStatus
from backend.app.schemas.report import (
    DecisionReport, VerdictBand, EvidenceBand, ChallengeBand, TraceBand,
    ConfidenceIndicator, AlternativeScore, QuantitativeAnalysis, ComparisonRow,
    CriticReview
)
from backend.app.schemas.evidence import EvidenceItem, SourceType

T = TypeVar("T", bound=BaseModel)

class MockLLMProvider:
    def __init__(self, model_name: str = "mock-reasoning-v1"):
        self.model_name = model_name

    async def generate(self, request: LLMRequest) -> LLMResponse:
        user_prompt = " ".join([m.content for m in request.messages if m.role.value == "user"])
        content = f"[Mock Analysis for: {user_prompt[:80]}...] The evidence indicates Option A satisfies constraints with lower operational overhead."
        prompt_tokens = len(user_prompt.split()) * 2
        completion_tokens = len(content.split()) * 2
        return LLMResponse(
            content=content,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
            model=self.model_name
        )

    async def generate_structured(
        self,
        request: LLMRequest,
        schema: Type[T]
    ) -> T:
        user_prompt = " ".join([m.content for m in request.messages if m.role.value == "user"])

        if schema == ParsedDecision:
            # Extract alternatives or use defaults
            return ParsedDecision(
                objective="Compare PostgreSQL + pgvector vs PostgreSQL + ChromaDB for low-overhead vector search",
                candidate_alternatives=["PostgreSQL + pgvector", "PostgreSQL + ChromaDB"],
                identified_constraints=["Low operational complexity", "Budget <= $1000/mo", "ACID compliance"],
                evaluation_criteria=["Query latency (p95)", "Memory overhead", "Operational simplicity", "Dual-write sync risks"],
                decision_domain="database_architecture"
            ) # type: ignore

        if schema == ResearchPlan:
            return ResearchPlan(
                decision_id="mock-decision",
                tasks=[
                    ResearchTask(
                        task_type=TaskType.DOCUMENT_RAG,
                        description="Query internal benchmark documentation for pgvector vs ChromaDB p95 latency and memory footprint",
                        query_or_input="pgvector ChromaDB latency memory benchmark",
                        purpose="Retrieve empirical performance figures from internal tests"
                    ),
                    ResearchTask(
                        task_type=TaskType.WEB_SEARCH,
                        description="Search public benchmarks and community feedback on pgvector HNSW indexing performance",
                        query_or_input="pgvector HNSW performance benchmarks 2025 2026",
                        purpose="Validate community findings against internal benchmarks"
                    ),
                    ResearchTask(
                        task_type=TaskType.SQL_QUERY,
                        description="Query database benchmark table for exact p95 latency and memory metrics",
                        query_or_input="SELECT technology, p95_latency_ms, memory_mb, max_qps FROM benchmark_results",
                        purpose="Extract exact structured performance figures"
                    ),
                    ResearchTask(
                        task_type=TaskType.CALCULATION,
                        description="Calculate monthly vector memory footprint for 500k 1536-dim embeddings",
                        query_or_input="(500000 * 1536 * 4) / (1024 * 1024)",
                        purpose="Estimate exact raw memory footprint in megabytes"
                    )
                ]
            ) # type: ignore

        if schema == CriticReview:
            return CriticReview(
                identified_risks=[
                    "High write lock contention in PostgreSQL if intensive vector indexing runs concurrently with core transactional writes",
                    "pgvector RAM growth may require dedicated RDS instance scaling"
                ],
                counterarguments=[
                    "ChromaDB embedded mode achieves lower cold query latency (8.9ms vs 12.4ms)",
                    "ChromaDB isolates vector memory completely from the relational transactional memory pool"
                ],
                assumptions_stress_tested=[
                    "Assumes vector collection remains under 2M items",
                    "Assumes the team has existing Postgres maintenance expertise"
                ],
                what_would_change_recommendation=[
                    "If corpus exceeds 5M vectors requiring distributed sharding, migrate to ChromaDB / dedicated vector store",
                    "If QPS exceeds 2000 write operations/sec, decouple vector storage from PostgreSQL"
                ]
            ) # type: ignore

        if schema == DecisionReport:
            return DecisionReport(
                id="mock-report-1",
                question="Should we choose PostgreSQL + pgvector or PostgreSQL + ChromaDB?",
                verdict=VerdictBand(
                    decision_question="Should we use PostgreSQL + pgvector or PostgreSQL + ChromaDB?",
                    recommendation_headline="Deploy PostgreSQL + pgvector to minimize operational complexity and preserve ACID guarantees.",
                    confidence=ConfidenceIndicator(
                        score=0.88,
                        level="High",
                        reasoning="Strong empirical alignment with single-database architecture and sub-15ms p95 latency."
                    ),
                    alternatives=[
                        AlternativeScore(name="PostgreSQL + pgvector", score=8.8, strengths=["Single ACID store", "Zero dual-write sync risks", "Proven tooling"], weaknesses=["Higher RAM utilization"]),
                        AlternativeScore(name="PostgreSQL + ChromaDB", score=7.2, strengths=["Lower raw latency (8.9ms)", "Decoupled memory"], weaknesses=["Dual-write sync complexity", "Secondary failure mode"])
                    ]
                ),
                evidence=EvidenceBand(
                    context_summary="Workload with 500k monthly vector embeddings, 2-person team, strict budget constraint.",
                    decision_criteria=["Operational simplicity", "p95 Query Latency", "ACID guarantees", "Cost"],
                    quantitative_analysis=QuantitativeAnalysis(
                        summary="pgvector achieves 12.4ms p95 latency with 1.2GB RAM footprint; ChromaDB achieves 8.9ms latency with 2.1GB RAM.",
                        comparison_table=[
                            ComparisonRow(criterion="p95 Query Latency", values={"PostgreSQL + pgvector": "12.4ms", "PostgreSQL + ChromaDB": "8.9ms"}, winner="PostgreSQL + ChromaDB"),
                            ComparisonRow(criterion="Memory Overhead", values={"PostgreSQL + pgvector": "1.2 GB", "PostgreSQL + ChromaDB": "2.1 GB"}, winner="PostgreSQL + pgvector"),
                            ComparisonRow(criterion="Operational Complexity", values={"PostgreSQL + pgvector": "Low (Single DB)", "PostgreSQL + ChromaDB": "Medium (Dual Store)"}, winner="PostgreSQL + pgvector")
                        ],
                        calculations_performed=["Raw memory calculation: (500000 * 1536 * 4) / (1024 * 1024) = 2929.68 MB unindexed."]
                    ),
                    key_trade_offs=[
                        "Accepting a 3.5ms query latency delta to avoid building and monitoring a dual-write sync pipeline."
                    ],
                    claims=[
                        ClaimItem(
                            claim_text="pgvector HNSW index delivers 12.4ms p95 latency on 500k vectors.",
                            verification_status=VerificationStatus.SUPPORTED,
                            supporting_source_ids=["src-1"],
                            confidence=0.95
                        ),
                        ClaimItem(
                            claim_text="ChromaDB local embedded delivers 8.9ms p95 latency.",
                            verification_status=VerificationStatus.SUPPORTED,
                            supporting_source_ids=["src-1"],
                            confidence=0.92
                        ),
                        ClaimItem(
                            claim_text="Running dual databases introduces potential divergence if worker crashes during vector write.",
                            verification_status=VerificationStatus.SUPPORTED,
                            supporting_source_ids=["src-1"],
                            confidence=0.90
                        )
                    ]
                ),
                challenge=ChallengeBand(
                    critic_review=CriticReview(
                        identified_risks=["Potential lock contention during heavy concurrent vector builds and OLTP writes."],
                        counterarguments=["ChromaDB offers better microservices isolation."],
                        assumptions_stress_tested=["Assumes workload does not exceed 2M vector embeddings."],
                        what_would_change_recommendation=["If vector corpus exceeds 5M vectors or requires distributed sharding, decouple to a dedicated vector database."]
                    ),
                    material_assumptions=["Team already manages PostgreSQL in production."]
                ),
                trace=TraceBand(
                    run_id="mock-report-1",
                    total_tokens=1480,
                    estimated_cost_usd=0.0029,
                    total_latency_ms=2840,
                    tool_invocations_count=4,
                    sources=[
                        EvidenceItem(source_type=SourceType.DOCUMENT, title="Internal Vector DB Benchmark Report", excerpt="pgvector achieved 12.4ms p95 latency on 500k vectors with 1.2 GB RAM.")
                    ]
                )
            ) # type: ignore

        # Fallback to creating a generic dummy schema instance
        try:
            return schema.model_validate({"mock": "data"})
        except Exception:
            return schema.construct() # type: ignore
