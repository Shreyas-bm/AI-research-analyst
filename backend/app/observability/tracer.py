"""Execution Tracing and Observability Engine for DecisionLens"""
import time
from typing import Dict, Any, Optional, AsyncGenerator
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.database import crud
from backend.app.observability.cost_tracker import CostTracker

class ExecutionTracer:
    """Records real-time lifecycle trace events for agent workflow nodes and tool calls."""

    def __init__(self, run_id: str, db_session: Optional[AsyncSession] = None):
        self.run_id = run_id
        self.db = db_session
        self.events: list[Dict[str, Any]] = []

    async def log_event(
        self,
        node_name: str,
        event_type: str,
        details: Optional[Dict[str, Any]] = None,
        duration_ms: int = 0
    ) -> Dict[str, Any]:
        """Record an atomic trace event in memory and optionally in persistent storage."""
        event_payload = {
            "run_id": self.run_id,
            "node_name": node_name,
            "event_type": event_type,
            "details": details or {},
            "duration_ms": duration_ms,
            "timestamp": time.time()
        }
        self.events.append(event_payload)

        if self.db is not None:
            try:
                await crud.log_trace_event(
                    session=self.db,
                    run_id=self.run_id,
                    node_name=node_name,
                    event_type=event_type,
                    details=details or {},
                    duration_ms=duration_ms
                )
            except Exception:
                # Tracing should never crash the primary execution path
                pass

        return event_payload

    @asynccontextmanager
    async def trace_node(
        self,
        node_name: str,
        initial_details: Optional[Dict[str, Any]] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Async context manager to trace start, duration, and completion/error of a node."""
        start_time = time.time()
        ctx_details: Dict[str, Any] = initial_details.copy() if initial_details else {}
        await self.log_event(node_name=node_name, event_type="start", details=ctx_details)
        try:
            yield ctx_details
            duration_ms = int((time.time() - start_time) * 1000)
            await self.log_event(
                node_name=node_name,
                event_type="complete",
                details=ctx_details,
                duration_ms=duration_ms
            )
        except Exception as exc:
            duration_ms = int((time.time() - start_time) * 1000)
            ctx_details["error"] = str(exc)
            await self.log_event(
                node_name=node_name,
                event_type="error",
                details=ctx_details,
                duration_ms=duration_ms
            )
            raise
