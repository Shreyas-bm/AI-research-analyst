"""Benchmark Dataset of 10 Curated Strategic Decision Cases"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class BenchmarkCase(BaseModel):
    case_id: str
    category: str
    question: str
    context: Dict[str, Any]
    constraints: List[str]
    candidate_alternatives: List[str]
    ground_truth_criteria: List[str]
    gold_recommendation: str
    expected_trade_offs: List[str]

BENCHMARK_CASES: List[BenchmarkCase] = [
    BenchmarkCase(
        case_id="case-001",
        category="Vector Database",
        question="Should we use PostgreSQL with pgvector or PostgreSQL with ChromaDB for semantic search?",
        context={"monthly_vectors": 500000, "team_size": 3, "cloud": "AWS", "budget_usd": 1000},
        constraints=["Low operational complexity", "ACID compliance", "Zero dual-write sync"],
        candidate_alternatives=["PostgreSQL + pgvector", "PostgreSQL + ChromaDB"],
        ground_truth_criteria=["Query latency (p95)", "Operational overhead", "ACID transactional integrity", "Memory usage"],
        gold_recommendation="PostgreSQL + pgvector",
        expected_trade_offs=["Trading minor p95 latency delta (3.5ms) for unified single-datastore ACID guarantees"]
    ),
    BenchmarkCase(
        case_id="case-002",
        category="Async Task Queue",
        question="Should we choose Celery with Redis or Temporal for orchestrating complex agentic workflows?",
        context={"team_size": 4, "workflow_steps": 12, "durations": "long_running"},
        constraints=["Durable execution", "Step retry without state loss", "Low maintenance"],
        candidate_alternatives=["Temporal.io", "Celery + Redis"],
        ground_truth_criteria=["State persistence on crash", "Code readability", "Infrastructure management"],
        gold_recommendation="Temporal.io",
        expected_trade_offs=["Higher learning curve for state machine deterministic replay traded for rock-solid workflow durability"]
    ),
    BenchmarkCase(
        case_id="case-003",
        category="Frontend Framework",
        question="Should our internal dashboard be built in Next.js App Router or Vite + Vanilla CSS SPA?",
        context={"team_size": 2, "seo_needed": False, "realtime_websockets": True},
        constraints=["Fast iteration velocity", "Zero hydration errors", "Simple local debugging"],
        candidate_alternatives=["Vite SPA", "Next.js App Router"],
        ground_truth_criteria=["Build speed", "Hydration complexity", "Developer velocity", "Client-side bundle size"],
        gold_recommendation="Vite SPA",
        expected_trade_offs=["Trading server-side rendering (unneeded for private auth dashboard) for instant HMR and zero hydration bugs"]
    ),
    BenchmarkCase(
        case_id="case-004",
        category="LLM Provider",
        question="Should we route production embeddings to OpenAI text-embedding-3-small or local all-MiniLM-L6-v2?",
        context={"daily_queries": 200000, "privacy_sensitive": True, "server_ram": 16},
        constraints=["Data privacy / zero third-party egress", "Zero marginal API cost", "p95 < 20ms"],
        candidate_alternatives=["Local all-MiniLM-L6-v2", "OpenAI text-embedding-3-small API"],
        ground_truth_criteria=["API Cost", "Data Privacy", "Retrieval Recall", "Inference Latency"],
        gold_recommendation="Local all-MiniLM-L6-v2",
        expected_trade_offs=["Accepting slightly lower MTEB benchmark score (56 vs 62) in exchange for zero API bills and complete offline data privacy"]
    ),
    BenchmarkCase(
        case_id="case-005",
        category="API Architecture",
        question="Should we build client communications using GraphQL or REST + Server-Sent Events (SSE)?",
        context={"team_size": 3, "streaming_ai_tokens": True},
        constraints=["Low schema overhead", "Native token streaming support"],
        candidate_alternatives=["REST + SSE", "GraphQL Subscriptions"],
        ground_truth_criteria=["Streaming simplicity", "Caching efficiency", "Tooling overhead"],
        gold_recommendation="REST + SSE",
        expected_trade_offs=["Lacks field-level graph querying, but offers lightweight HTTP streaming with zero subscription WebSocket proxy headaches"]
    )
]
