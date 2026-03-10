"""
Formula 1 routes for the API service.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from shared.db.session import get_db
from shared.db.models.f1 import F1Race, F1Driver, F1LapTime, F1DriverStanding
from shared.redis import get_redis_client
import json

router = APIRouter(prefix="/api/v1/f1", tags=["Formula 1"])


@router.get("/races")
async def get_f1_races(season: int = 2026, db: AsyncSession = Depends(get_db)):
    redis = get_redis_client()
    cache_key = f"f1:races:{season}"
    cached = await redis.get(cache_key)

    if cached:
        return json.loads(cached)

    result = await db.execute(
        select(F1Race).where(F1Race.season == season).order_by(F1Race.round)
    )
    races = result.scalars().all()

    if not races:
        raise HTTPException(status_code=404, detail="No races found for this season")

    data = [
        {
            "round": r.round,
            "race_name": r.race_name,
            "circuit": r.circuit_name,
            "date": r.race_date.isoformat() if r.race_date else None,
        }
        for r in races
    ]

    response = {"data": data, "meta": {"count": len(data), "cache_age_seconds": 0}}
    await redis.set(cache_key, json.dumps(response), ex=3600)
    return response


@router.get("/drivers")
async def get_f1_drivers(db: AsyncSession = Depends(get_db)):
    redis = get_redis_client()
    cache_key = "f1:drivers"
    cached = await redis.get(cache_key)

    if cached:
        return json.loads(cached)

    result = await db.execute(select(F1Driver).order_by(F1Driver.last_name))
    drivers = result.scalars().all()

    data = [
        {
            "code": d.code,
            "first_name": d.first_name,
            "last_name": d.last_name,
        }
        for d in drivers
    ]

    response = {"data": data, "meta": {"count": len(data), "cache_age_seconds": 0}}
    await redis.set(cache_key, json.dumps(response), ex=86400)
    return response


@router.get("/lap-times/{season}/{round}")
async def get_lap_times(season: int, round: int, db: AsyncSession = Depends(get_db)):
    redis = get_redis_client()
    cache_key = f"f1:lap_times:{season}:{round}"
    cached = await redis.get(cache_key)

    if cached:
        return json.loads(cached)

    result = await db.execute(
        select(F1LapTime, F1Driver)
        .join(F1Driver, F1LapTime.driver_id == F1Driver.id)
        .join(F1Race, F1LapTime.race_id == F1Race.id)
        .where(F1Race.season == season, F1Race.round == round)
        .order_by(F1LapTime.lap_number, F1LapTime.position)
    )
    rows = result.all()

    if not rows:
        raise HTTPException(status_code=404, detail="No lap times found")

    data = [
        {
            "lap": lt.lap_number,
            "driver": d.code,
            "lap_time_seconds": lt.lap_time_seconds,
            "position": lt.position,
        }
        for lt, d in rows
    ]

    response = {"data": data, "meta": {"count": len(data), "cache_age_seconds": 0}}
    await redis.set(cache_key, json.dumps(response), ex=86400)
    return response