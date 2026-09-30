"""Context-Aware Mock LLM Provider for offline development, CI, and zero-cost testing"""
import re
from typing import Type, TypeVar, Any, List, Dict
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

def _extract_decision_context(prompt: str) -> Dict[str, Any]:
    """Dynamically derive objective, alternatives, and domain from user prompt."""
    clean = prompt.strip()
    
    # Try to find 'Decision Question:' or prompt text
    q_match = re.search(r"Decision Question:\s*([^\n]+)", prompt, re.IGNORECASE)
    question = q_match.group(1).strip() if q_match else clean
    if not question:
        question = "What architecture or technical path should we choose?"

    # Detect alternatives if explicitly specified in prompt
    alts_match = re.search(r"Preferred Alternatives:\s*\[([^\]]*)\]", prompt, re.IGNORECASE)
    explicit_alts = []
    if alts_match and alts_match.group(1).strip():
        explicit_alts = [a.strip().strip("'\"") for a in alts_match.group(1).split(",") if a.strip()]

    # If no explicit alternatives, heuristically extract or generate based on question keywords
    lower_q = question.lower()
    
    if explicit_alts:
        candidates = explicit_alts
    elif " or " in lower_q or " vs " in lower_q:
        # e.g. "Should we choose X or Y?" or "X vs Y"
        parts = re.split(r"\b(?:or|vs|\/)\b", question, flags=re.IGNORECASE)
        candidates = [re.sub(r"^(?:should we choose|should we use|should i choose|should we adopt|compare)\s*", "", p, flags=re.IGNORECASE).strip(" ?.,") for p in parts if len(p.strip()) > 1][:3]
    elif "career" in lower_q or "engineering student" in lower_q or "job" in lower_q or "domain" in lower_q:
        candidates = [
            "AI / Machine Learning Engineering",
            "Backend & Distributed Systems Engineering",
            "Full-Stack Web Development & Cloud"
        ]
    elif "database" in lower_q or "vector" in lower_q:
        candidates = ["PostgreSQL + pgvector", "Dedicated Vector Store (ChromaDB / Qdrant)"]
    elif "frontend" in lower_q or "react" in lower_q:
        candidates = ["Vite React SPA", "Next.js App Router"]
    elif "orchestrat" in lower_q or "workflow" in lower_q:
        candidates = ["Temporal.io Durable Workflows", "Celery + Redis Task Queue"]
    else:
        candidates = ["Specialized Option A", "Established Option B"]

    if len(candidates) < 2:
        candidates.append("Alternative Path B")

    return {
        "question": question,
        "candidates": candidates[:3]
    }

class MockLLMProvider:
    def __init__(self, model_name: str = "mock-reasoning-v1"):
        self.model_name = model_name

    async def generate(self, request: LLMRequest) -> LLMResponse:
        user_prompt = " ".join([m.content for m in request.messages if m.role.value == "user"])
        ctx = _extract_decision_context(user_prompt)
        content = f"[Analytical Synthesis for: {ctx['question'][:80]}] The evaluated data indicates that {ctx['candidates'][0]} offers the strongest alignment with core requirements and long-term leverage."
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
        ctx = _extract_decision_context(user_prompt)
        q = ctx["question"]
        cands = ctx["candidates"]
        winner = cands[0]
        runner_up = cands[1] if len(cands) > 1 else "Alternative B"

        if schema == ParsedDecision:
            return ParsedDecision(
                objective=f"Evaluate strategic options for: {q}",
                candidate_alternatives=cands,
                identified_constraints=["High long-term ROI", "Low initial friction", "Proven market demand"],
                evaluation_criteria=["Core Effectiveness", "Learning Curve & Complexity", "Market & Ecosystem Maturity", "Scalability & Resilience"],
                decision_domain="technical_strategy"
            ) # type: ignore

        if schema == ResearchPlan:
            return ResearchPlan(
                decision_id="research-plan-dynamic",
                tasks=[
                    ResearchTask(
                        task_type=TaskType.DOCUMENT_RAG,
                        description=f"Query knowledge base and documentation for empirical comparisons on {winner} vs {runner_up}",
                        query_or_input=f"{winner} vs {runner_up} empirical comparison metrics",
                        purpose="Retrieve verifiable evidence and benchmark findings"
                    ),
                    ResearchTask(
                        task_type=TaskType.SQL_QUERY,
                        description=f"Query benchmark dataset for comparative performance and adoption metrics",
                        query_or_input="SELECT technology, p95_latency_ms, memory_mb, max_qps FROM benchmark_results",
                        purpose="Extract quantitative comparative data"
                    ),
                    ResearchTask(
                        task_type=TaskType.CALCULATION,
                        description=f"Perform quantitative balance and resource allocation calculation",
                        query_or_input="round((8.8 / 10.0) * 100, 1)",
                        purpose="Derive normalized score metric"
                    )
                ]
            ) # type: ignore

        if schema == CriticReview:
            return CriticReview(
                identified_risks=[
                    f"Over-specialization in {winner} without foundational breadth may create vulnerability if ecosystem requirements shift.",
                    f"Initial ramp-up complexity for {winner} is higher compared to traditional paths."
                ],
                counterarguments=[
                    f"{runner_up} offers lower immediate cognitive barrier and more generalized baseline opportunities.",
                    f"Hybrid foundations combining {winner} with {runner_up} may yield greater cross-functional resilience."
                ],
                assumptions_stress_tested=[
                    f"Assumes continuous active development and dedication to practical portfolio projects.",
                    f"Assumes market growth in {winner} remains robust over the next 3-5 years."
                ],
                what_would_change_recommendation=[
                    f"If immediate short-term placement within 30 days is mandatory, pivot toward {runner_up}.",
                    f"If primary interest lies strictly in visual product design rather than systems/algorithmic logic, re-evaluate toward frontend architectures."
                ]
            ) # type: ignore

        if schema == DecisionReport:
            return DecisionReport(
                id="report-dynamic",
                question=q,
                verdict=VerdictBand(
                    decision_question=q,
                    recommendation_headline=f"Prioritize {winner} as the primary path to maximize growth, depth, and compounding leverage.",
                    confidence=ConfidenceIndicator(
                        score=0.89,
                        level="High",
                        reasoning=f"High empirical convergence on market demand, technical defensibility, and strong fundamentals for {winner}."
                    ),
                    alternatives=[
                        AlternativeScore(
                            name=winner,
                            score=9.1,
                            strengths=["High ceiling for technical mastery", "Strong compounding leverage in modern industry", "High demand for deep problem solvers"],
                            weaknesses=["Steeper initial learning curve", "Requires solid mathematical and systems foundations"]
                        ),
                        AlternativeScore(
                            name=runner_up,
                            score=7.8,
                            strengths=["Rapid initial productivity", "Broad entry-level market volume", "Abundant tutorials and tooling"],
                            weaknesses=["Lower long-term differentiation", "Higher competition at entry level"]
                        )
                    ]
                ),
                evidence=EvidenceBand(
                    context_summary=f"Analysis tailored to: {q}",
                    decision_criteria=["Compounding Leverage", "Market Demand", "Learning Curve", "Long-term Defensibility"],
                    quantitative_analysis=QuantitativeAnalysis(
                        summary=f"{winner} demonstrates an 89% composite fit score based on industry growth trajectories and foundational leverage.",
                        comparison_table=[
                            ComparisonRow(criterion="Compounding Technical Depth", values={winner: "Very High (9.2/10)", runner_up: "Moderate (7.0/10)"}, winner=winner),
                            ComparisonRow(criterion="Entry-Level Accessibility", values={winner: "Medium (requires grit)", runner_up: "High (fast starts)"}, winner=runner_up),
                            ComparisonRow(criterion="Market Differentiation", values={winner: "High (Specialist tier)", runner_up: "Moderate (Generalist tier)"}, winner=winner)
                        ],
                        calculations_performed=[f"Weighted decision scoring: {winner} scored 9.1/10 vs {runner_up} 7.8/10."]
                    ),
                    key_trade_offs=[
                        f"Accepting a steeper initial learning curve with {winner} in exchange for higher long-term career resilience and differentiation."
                    ],
                    claims=[
                        ClaimItem(
                            claim_text=f"{winner} delivers the highest long-term technical leverage and specialization defensibility.",
                            verification_status=VerificationStatus.SUPPORTED,
                            supporting_source_ids=["src-1"],
                            confidence=0.92
                        ),
                        ClaimItem(
                            claim_text=f"Hands-on project proof and strong fundamentals outweigh generic credentialing.",
                            verification_status=VerificationStatus.SUPPORTED,
                            supporting_source_ids=["src-1"],
                            confidence=0.95
                        )
                    ]
                ),
                challenge=ChallengeBand(
                    critic_review=CriticReview(
                        identified_risks=[f"Risk of superficial learning without building complete end-to-end applications."],
                        counterarguments=[f"{runner_up} allows faster shipping of visible projects in the first 2 months."],
                        assumptions_stress_tested=[f"Assumes willingness to write code consistently and learn core systems concepts."],
                        what_would_change_recommendation=[f"If urgent short-term employment is the sole priority, {runner_up} offers quicker initial conversion."]
                    ),
                    material_assumptions=[f"Student has access to standard computing resources and 6-12 months of preparation time."]
                ),
                trace=TraceBand(
                    run_id="report-dynamic",
                    total_tokens=1540,
                    estimated_cost_usd=0.0022,
                    total_latency_ms=1850,
                    tool_invocations_count=3,
                    sources=[
                        EvidenceItem(source_type=SourceType.DOCUMENT, title="Industry Technical Career & Systems Benchmark Report", excerpt="Specialization in distributed systems and AI systems exhibits 3.2x higher wage growth and defensibility than entry generalist scripting.")
                    ]
                )
            ) # type: ignore

        try:
            return schema.model_validate({"mock": "data"})
        except Exception:
            return schema.construct() # type: ignore
