"""Evaluation Metrics Calculator for Automated Benchmarks"""
from typing import List, Dict, Any
from backend.app.schemas.report import DecisionReport
from backend.app.evaluation.dataset import BenchmarkCase

class BenchmarkMetrics:
    @staticmethod
    def calculate_citation_coverage(report: DecisionReport) -> float:
        """Percentage of claims marked as SUPPORTED or PARTIALLY_SUPPORTED with valid citations."""
        claims = report.evidence.claims
        if not claims:
            return 0.0
        supported = sum(1 for c in claims if c.verification_status.value in ["SUPPORTED", "PARTIALLY_SUPPORTED"] and len(c.supporting_source_ids) > 0)
        return round(supported / len(claims), 4)

    @staticmethod
    def calculate_faithfulness(report: DecisionReport) -> float:
        """Grounding score: ratio of claims that have empirical citation backing."""
        claims = report.evidence.claims
        if not claims:
            return 0.0
        backed = sum(1 for c in claims if len(c.supporting_source_ids) > 0)
        return round(backed / len(claims), 4)

    @staticmethod
    def calculate_answer_relevance(report: DecisionReport, case: BenchmarkCase) -> float:
        """Measures alignment between report criteria/trade-offs and benchmark case expectations."""
        report_criteria = [c.lower() for c in report.evidence.decision_criteria]
        expected_criteria = [c.lower() for c in case.ground_truth_criteria]

        if not expected_criteria:
            return 1.0

        matches = 0
        for exp in expected_criteria:
            exp_tokens = set(exp.split())
            for rep in report_criteria:
                rep_tokens = set(rep.split())
                if len(exp_tokens.intersection(rep_tokens)) >= 1:
                    matches += 1
                    break

        return round(min(1.0, matches / len(expected_criteria)), 4)

    @staticmethod
    def calculate_recommendation_alignment(report: DecisionReport, case: BenchmarkCase) -> float:
        """Checks if the report recommendation headline mentions the gold recommendation."""
        headline = report.verdict.recommendation_headline.lower()
        gold = case.gold_recommendation.lower()
        if gold in headline:
            return 1.0
        # Partial token overlap
        gold_tokens = [t for t in gold.split() if len(t) > 2]
        matches = sum(1 for t in gold_tokens if t in headline)
        return round(matches / max(1, len(gold_tokens)), 4)
