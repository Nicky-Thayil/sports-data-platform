"""
Premier League routes for the API service.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from shared.db.session import get_db
from shared.db.models.pl import PLStanding, PLTeam, PLMatch
from shared.redis import get_redis_client
from services.api.app.dependencies import get_db
import json
import time
from sqlalchemy.orm import aliased

router = APIRouter(prefix="/api/v1/pl", tags=["Premier League"])


@router.get("/standings")
async def get_pl_standings(season: int = 2024, db: AsyncSession = Depends(get_db)):
    redis = get_redis_client()
    cache_key = f"pl:standings:{season}"
    cached = await redis.get(cache_key)

    if cached:
        return json.loads(cached)

    result = await db.execute(
        select(PLStanding, PLTeam)
        .join(PLTeam, PLStanding.team_id == PLTeam.id)
        .where(PLStanding.season == season)
        .order_by(PLStanding.position)
    )
    rows = result.all()

    if not rows:
        raise HTTPException(status_code=404, detail="No standings found for this season")

    data = [
        {
            "position": s.position,
            "team": t.name,
            "played": s.played,
            "won": s.won,
            "drawn": s.drawn,
            "lost": s.lost,
            "goals_for": s.goals_for,
            "goals_against": s.goals_against,
            "points": s.points,
        }
        for s, t in rows
    ]

    response = {"data": data, "meta": {"count": len(data), "cache_age_seconds": 0}}
    await redis.set(cache_key, json.dumps(response), ex=3600)
    return response


@router.get("/fixtures")
async def get_pl_fixtures(season: int = 2024, finished: bool | None = None, db: AsyncSession = Depends(get_db)):
    redis = get_redis_client()
    cache_key = f"pl:fixtures:{season}:{finished}"
    cached = await redis.get(cache_key)

    if cached:
        return json.loads(cached)

    AwayTeam = aliased(PLTeam)
    query = (
        select(PLMatch, PLTeam.name.label("home_name"), AwayTeam.name.label("away_name"))
        .join(PLTeam, PLMatch.home_team_id == PLTeam.id)
        .join(AwayTeam, PLMatch.away_team_id == AwayTeam.id)
        .where(PLMatch.season == season)
    )
    if finished is not None:
        query = query.where(PLMatch.finished == finished)

    result = await db.execute(query.order_by(PLMatch.match_date))
    rows = result.all()

    data = [
        {
            "match_id": m.api_match_id,
            "round": m.round,
            "home_team": home,
            "away_team": away,
            "home_goals": m.home_goals,
            "away_goals": m.away_goals,
            "match_date": m.match_date.isoformat() if m.match_date else None,
            "finished": m.finished,
        }
        for m, home, away in rows
    ]

    response = {"data": data, "meta": {"count": len(data), "cache_age_seconds": 0}}
    await redis.set(cache_key, json.dumps(response), ex=1800)
    return response