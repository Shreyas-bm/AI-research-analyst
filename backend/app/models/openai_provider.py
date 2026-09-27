"""OpenAI / NVIDIA / Ollama compatible async LLM provider"""
import json
import httpx
from typing import Type, TypeVar, Optional, Dict, Any
from pydantic import BaseModel
from backend.app.models.llm_base import LLMRequest, LLMResponse, MessageRole

T = TypeVar("T", bound=BaseModel)

class OpenAICompatibleProvider:
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = "https://api.openai.com/v1",
        default_model: str = "gpt-4o-mini"
    ):
        self.api_key = api_key or ""
        self.base_url = (base_url or "https://api.openai.com/v1").rstrip("/")
        self.default_model = default_model

    async def generate(self, request: LLMRequest) -> LLMResponse:
        model = request.model or self.default_model
        payload = {
            "model": model,
            "messages": [{"role": m.role.value, "content": m.content} for m in request.messages],
            "temperature": request.temperature
        }
        if request.max_tokens:
            payload["max_tokens"] = request.max_tokens

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(f"{self.base_url}/chat/completions", json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()

        choice = data["choices"][0]
        usage = data.get("usage", {})
        return LLMResponse(
            content=choice["message"]["content"],
            prompt_tokens=usage.get("prompt_tokens", 0),
            completion_tokens=usage.get("completion_tokens", 0),
            total_tokens=usage.get("total_tokens", 0),
            model=data.get("model", model),
            finish_reason=choice.get("finish_reason", "stop")
        )

    async def generate_structured(
        self,
        request: LLMRequest,
        schema: Type[T]
    ) -> T:
        schema_json = json.dumps(schema.model_json_schema(), indent=2)
        system_instruction = f"\nYou MUST respond with valid JSON matching this exact JSON schema:\n{schema_json}\nReturn ONLY valid JSON and nothing else."
        
        updated_messages = list(request.messages)
        if updated_messages and updated_messages[0].role == MessageRole.SYSTEM:
            updated_messages[0] = type(updated_messages[0])(
                role=MessageRole.SYSTEM,
                content=updated_messages[0].content + system_instruction
            )
        else:
            from backend.app.models.llm_base import ChatMessage
            updated_messages.insert(0, ChatMessage(role=MessageRole.SYSTEM, content=system_instruction))

        req = LLMRequest(
            messages=updated_messages,
            model=request.model or self.default_model,
            temperature=0.1
        )
        resp = await self.generate(req)
        clean_text = resp.content.strip()
        if clean_text.startswith("```json"):
            clean_text = clean_text[7:]
        if clean_text.startswith("```"):
            clean_text = clean_text[3:]
        if clean_text.endswith("```"):
            clean_text = clean_text[:-3]
        clean_text = clean_text.strip()
        return schema.model_validate_json(clean_text)
