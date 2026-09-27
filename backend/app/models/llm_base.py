"""Base LLM Provider Protocol and Message Schemas"""
from typing import List, Dict, Any, Optional, Type, TypeVar, Protocol, runtime_checkable
from pydantic import BaseModel, Field
from enum import Enum

T = TypeVar("T", bound=BaseModel)

class MessageRole(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"

class ChatMessage(BaseModel):
    role: MessageRole
    content: str

class LLMRequest(BaseModel):
    messages: List[ChatMessage]
    model: Optional[str] = None
    temperature: float = 0.2
    max_tokens: Optional[int] = None
    response_format: Optional[Dict[str, Any]] = None

class LLMResponse(BaseModel):
    content: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    model: str
    finish_reason: Optional[str] = "stop"

@runtime_checkable
class LLMProvider(Protocol):
    async def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate a standard text response."""
        ...

    async def generate_structured(
        self,
        request: LLMRequest,
        schema: Type[T]
    ) -> T:
        """Generate a response constrained and parsed to a Pydantic schema."""
        ...
