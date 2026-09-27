"""API Routers Package"""
from backend.app.api.decision import router as decision_router
from backend.app.api.documents import router as documents_router
from backend.app.api.evaluation import router as evaluation_router

__all__ = ["decision_router", "documents_router", "evaluation_router"]
