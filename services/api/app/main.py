"""
API service for the application.
"""

from fastapi import FastAPI
from contextlib import asynccontextmanager
from shared.config import get_settings
from shared.db.session import engine
from services.api.app.middleware.tracing import TracingMiddleware
from services.api.app.routes.f1 import router as f1_router
from services.api.app.routes.pl import router as pl_router
from services.api.app.routes.metrics import router as metrics_router
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

settings = get_settings()

limiter = Limiter(key_func=get_remote_address, default_limits=[f"{settings.RATE_LIMIT_PER_MINUTE}/minute"])
@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await engine.dispose()


app = FastAPI(title="Apex", version="1.0.0", lifespan=lifespan)

app.add_middleware(TracingMiddleware)

app.include_router(f1_router)
app.include_router(pl_router)
app.include_router(metrics_router)


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "environment": settings.ENVIRONMENT,
    }