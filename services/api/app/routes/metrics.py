"""
Metrics routes for the API service.
"""

from fastapi import APIRouter
from shared.redis import get_redis_client

router = APIRouter(prefix="/api/v1", tags=["System"])


@router.get("/metrics")
async def get_metrics():
    redis = get_redis_client()
    lag_data = await redis.hgetall("ingest_lag")

    return {
        "data": {
            "ingest_lag": lag_data,
        },
        "meta": {}
    }