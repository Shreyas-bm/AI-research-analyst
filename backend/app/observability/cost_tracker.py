"""Token Tracking and Cost Calculator"""
from typing import Dict, Any

# Pricing per 1M tokens in USD ($/1M prompt, $/1M completion)
MODEL_PRICING: Dict[str, Dict[str, float]] = {
    "gpt-4o-mini": {"prompt": 0.15 / 1_000_000, "completion": 0.60 / 1_000_000},
    "gpt-4o": {"prompt": 2.50 / 1_000_000, "completion": 10.00 / 1_000_000},
    "gemini-1.5-flash": {"prompt": 0.075 / 1_000_000, "completion": 0.30 / 1_000_000},
    "gemini-1.5-pro": {"prompt": 1.25 / 1_000_000, "completion": 5.00 / 1_000_000},
    "meta/llama-3.1-70b-instruct": {"prompt": 0.70 / 1_000_000, "completion": 0.90 / 1_000_000},
    "meta/llama-3.1-8b-instruct": {"prompt": 0.18 / 1_000_000, "completion": 0.18 / 1_000_000},
    "mock-reasoning-v1": {"prompt": 0.0, "completion": 0.0},
}

class CostTracker:
    @staticmethod
    def estimate_tokens(text: str) -> int:
        """Heuristic token estimation: ~4 chars per token for English text."""
        if not text:
            return 0
        return max(1, len(text) // 4)

    @staticmethod
    def calculate_cost(
        model_name: str,
        prompt_tokens: int,
        completion_tokens: int
    ) -> float:
        """Calculate total USD cost based on token counts."""
        pricing = MODEL_PRICING.get(model_name, {"prompt": 0.15 / 1_000_000, "completion": 0.60 / 1_000_000})
        cost = (prompt_tokens * pricing["prompt"]) + (completion_tokens * pricing["completion"])
        return round(cost, 6)

    @staticmethod
    def format_cost(cost_usd: float) -> str:
        """Format cost for UI display."""
        if cost_usd == 0.0:
            return "$0.000 (Local / Mock)"
        elif cost_usd < 0.01:
            return f"${cost_usd:.5f}"
        else:
            return f"${cost_usd:.4f}"
