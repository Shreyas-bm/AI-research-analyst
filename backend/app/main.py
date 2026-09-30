"""DecisionAI (DecisionLens) FastAPI Application Entrypoint"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.config import settings
from backend.app.database.session import init_db
from backend.app.api.decision import router as decision_router
from backend.app.api.documents import router as documents_router
from backend.app.api.evaluation import router as evaluation_router
from backend.app.api.auth import router as auth_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: initialize database schemas
    await init_db()
    yield
    # Shutdown logic if any

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="Evidence-first Agentic Decision Intelligence Platform",
    lifespan=lifespan
)

# Configure CORS for local development and UI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(auth_router)
app.include_router(decision_router)
app.include_router(documents_router)
app.include_router(evaluation_router)

@app.get("/health", tags=["System"])
async def health_check():
    return {
        "status": "healthy",
        "app": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT,
        "llm_provider": settings.LLM_PROVIDER
    }
