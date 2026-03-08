"""
Premier League data ingestion jobs.
"""

import logging
from datetime import datetime, timezone
from sqlalchemy.dialects.postgresql import insert
from shared.db.session import AsyncSessionLocal
from shared.db.models.pl import PLTeam, PLMatch, PLStanding
from shared.redis import get_redis_client
from services.ingest.app.sources.api_football import get_standings, get_fixtures

logger = logging.getLogger(__name__)

CURRENT_SEASON = 2024

def _parse_round(round_str: str | None) -> int | None:
    if not round_str:
        return None
    try:
        return int(round_str.split("-")[-1].strip())
    except (ValueError, IndexError):
        return None

async def sync_pl_standings():
    logger.info("Starting PL standings sync")
    data = await get_standings(CURRENT_SEASON)
    if not data or not data.get("response"):
        logger.warning("No PL standings data returned")
        return

    standings = data["response"][0]["league"]["standings"][0]

    async with AsyncSessionLocal() as session:
        for entry in standings:
            team = entry["team"]

            team_stmt = insert(PLTeam).values(
                team_ref=str(team["id"]),
                name=team["name"],
                short_name=team["name"][:50],
            ).on_conflict_do_update(
                constraint="pl_teams_team_ref_key",
                set_=dict(name=team["name"]),
            )
            await session.execute(team_stmt)
            await session.flush()

            from sqlalchemy import select
            from shared.db.models.pl import PLTeam as PLTeamModel
            result = await session.execute(
                select(PLTeamModel).where(PLTeamModel.team_ref == str(team["id"]))
            )
            db_team = result.scalar_one()

            standing_stmt = insert(PLStanding).values(
                season=CURRENT_SEASON,
                round=entry["all"]["played"],
                team_id=db_team.id,
                position=entry["rank"],
                played=entry["all"]["played"],
                won=entry["all"]["win"],
                drawn=entry["all"]["draw"],
                lost=entry["all"]["lose"],
                goals_for=entry["all"]["goals"]["for"],
                goals_against=entry["all"]["goals"]["against"],
                points=entry["points"],
            ).on_conflict_do_update(
                constraint="uq_pl_standing_season_round_team",
                set_=dict(
                    position=entry["rank"],
                    points=entry["points"],
                    played=entry["all"]["played"],
                    won=entry["all"]["win"],
                    drawn=entry["all"]["draw"],
                    lost=entry["all"]["lose"],
                ),
            )
            await session.execute(standing_stmt)

        await session.commit()

    redis = get_redis_client()
    await redis.hset("ingest_lag", "pl_standings", datetime.now(timezone.utc).isoformat())
    logger.info("PL standings sync complete")


async def sync_pl_fixtures():
    logger.info("Starting PL fixtures sync")
    data = await get_fixtures(CURRENT_SEASON)
    if not data or not data.get("response"):
        logger.warning("No PL fixtures data returned")
        return

    async with AsyncSessionLocal() as session:
        for fixture in data["response"]:
            f = fixture["fixture"]
            teams = fixture["teams"]
            goals = fixture["goals"]

            for team in [teams["home"], teams["away"]]:
                team_stmt = insert(PLTeam).values(
                    team_ref=str(team["id"]),
                    name=team["name"],
                    short_name=team["name"][:50],
                ).on_conflict_do_nothing()
                await session.execute(team_stmt)

            await session.flush()

            from sqlalchemy import select
            home_result = await session.execute(
                select(PLTeam).where(PLTeam.team_ref == str(teams["home"]["id"]))
            )
            away_result = await session.execute(
                select(PLTeam).where(PLTeam.team_ref == str(teams["away"]["id"]))
            )
            home_team = home_result.scalar_one_or_none()
            away_team = away_result.scalar_one_or_none()

            if not home_team or not away_team:
                continue

            match_date = datetime.fromisoformat(f["date"]) if f.get("date") else None
            finished = f["status"]["short"] in ("FT", "AET", "PEN")

            match_stmt = insert(PLMatch).values(
                api_match_id=f["id"],
                season=CURRENT_SEASON,
                round=_parse_round(fixture["league"].get("round")),
                home_team_id=home_team.id,
                away_team_id=away_team.id,
                home_goals=goals.get("home"),
                away_goals=goals.get("away"),
                match_date=match_date,
                finished=finished,
            ).on_conflict_do_update(
                constraint="pl_matches_api_match_id_key",
                set_=dict(
                    home_goals=goals.get("home"),
                    away_goals=goals.get("away"),
                    finished=finished,
                ),
            )
            await session.execute(match_stmt)

        await session.commit()

    redis = get_redis_client()
    await redis.hset("ingest_lag", "pl_fixtures", datetime.now(timezone.utc).isoformat())
    logger.info("PL fixtures sync complete")