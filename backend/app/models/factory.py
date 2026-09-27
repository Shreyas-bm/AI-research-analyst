"""LLM Provider Factory driven by settings"""
from backend.app.config import settings
from backend.app.models.llm_base import LLMProvider
from backend.app.models.mock_provider import MockLLMProvider
from backend.app.models.openai_provider import OpenAICompatibleProvider
from backend.app.models.gemini_provider import GeminiProvider

def get_llm_provider(provider_name: str = None) -> LLMProvider:
    name = (provider_name or settings.LLM_PROVIDER).lower()

    if name == "mock":
        return MockLLMProvider()
    elif name == "gemini":
        if not settings.GEMINI_API_KEY:
            # Safe graceful fallback to mock if no key is configured
            return MockLLMProvider()
        return GeminiProvider(api_key=settings.GEMINI_API_KEY)
    elif name == "nvidia":
        return OpenAICompatibleProvider(
            api_key=settings.NVIDIA_API_KEY or "",
            base_url=settings.OPENAI_BASE_URL or "https://integrate.api.nvidia.com/v1",
            default_model=settings.DEFAULT_MODEL or "meta/llama-3.1-70b-instruct"
        )
    elif name == "openai":
        return OpenAICompatibleProvider(
            api_key=settings.OPENAI_API_KEY or "",
            base_url=settings.OPENAI_BASE_URL or "https://api.openai.com/v1",
            default_model=settings.DEFAULT_MODEL or "gpt-4o-mini"
        )
    else:
        return MockLLMProvider()
