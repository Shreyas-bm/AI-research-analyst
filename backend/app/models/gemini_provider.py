"""Google Gemini REST API adapter"""
import json
import httpx
from typing import Type, TypeVar, Optional, Dict, Any
from pydantic import BaseModel
from backend.app.models.llm_base import LLMRequest, LLMResponse, MessageRole

T = TypeVar("T", bound=BaseModel)

class GeminiProvider:
    def __init__(
        self,
        api_key: Optional[str] = None,
        default_model: str = "gemini-1.5-flash"
    ):
        self.api_key = api_key or ""
        self.default_model = default_model

    async def generate(self, request: LLMRequest) -> LLMResponse:
        model = request.model or self.default_model
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={self.api_key}"

        contents = []
        for msg in request.messages:
            role = "user" if msg.role in [MessageRole.USER, MessageRole.SYSTEM] else "model"
            contents.append({
                "role": role,
                "parts": [{"text": msg.content}]
            })

        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": request.temperature,
            }
        }
        if request.max_tokens:
            payload["generationConfig"]["maxOutputTokens"] = request.max_tokens

        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()

        candidates = data.get("candidates", [])
        content = ""
        if candidates and "content" in candidates[0]:
            parts = candidates[0]["content"].get("parts", [])
            content = "".join([p.get("text", "") for p in parts])

        usage = data.get("usageMetadata", {})
        prompt_tokens = usage.get("promptTokenCount", 0)
        completion_tokens = usage.get("candidatesTokenCount", 0)
        total_tokens = usage.get("totalTokenCount", 0)

        return LLMResponse(
            content=content,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            model=model,
            finish_reason=candidates[0].get("finishReason", "STOP") if candidates else "STOP"
        )

    async def generate_structured(
        self,
        request: LLMRequest,
        schema: Type[T]
    ) -> T:
        schema_json = json.dumps(schema.model_json_schema(), indent=2)
        system_instruction = f"\nYou MUST respond with valid JSON matching this exact schema:\n{schema_json}\nReturn ONLY JSON."
        
        from backend.app.models.llm_base import ChatMessage
        messages = list(request.messages)
        messages.append(ChatMessage(role=MessageRole.USER, content=system_instruction))

        req = LLMRequest(
            messages=messages,
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
