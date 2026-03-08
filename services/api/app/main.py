"""
API service for the application.
"""

from fastapi import FastAPI
from contextlib import asynccontextmanager
from shared.config import get_settings
from shared.db.session import engine
from shared.redis import get_redis_client

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await engine.dispose()


app = FastAPI(
    title="Apex",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "environment": settings.ENVIRONMENT,
    }