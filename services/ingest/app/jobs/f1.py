"""
F1 data ingestion jobs.
"""

import logging
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from shared.db.session import AsyncSessionLocal
from shared.db.models.f1 import F1Race, F1Driver, F1LapTime, F1DriverStanding
from shared.redis import get_redis_client
from services.ingest.app.sources.fastf1 import get_race_schedule, get_session_results, get_lap_times

logger = logging.getLogger(__name__)

CURRENT_SEASON = 2026


async def sync_f1_races():
    logger.info("Starting F1 race sync")
    schedule = get_race_schedule(CURRENT_SEASON)
    if schedule is None or schedule.empty:
        logger.warning("No F1 schedule data returned")
        return

    async with AsyncSessionLocal() as session:
        for _, event in schedule.iterrows():
            stmt = insert(F1Race).values(
                season=CURRENT_SEASON,
                round=int(event["RoundNumber"]),
                circuit_name=str(event["Location"]),
                race_name=str(event["EventName"]),
                race_date=event["EventDate"].to_pydatetime() if event["EventDate"] else None,
            ).on_conflict_do_update(
                constraint="uq_f1_race_season_round",
                set_=dict(
                    circuit_name=str(event["Location"]),
                    race_name=str(event["EventName"]),
                ),
            )
            await session.execute(stmt)
        await session.commit()

    redis = get_redis_client()
    await redis.hset("ingest_lag", "f1_races", datetime.now(timezone.utc).isoformat())
    logger.info("F1 race sync complete")


async def sync_f1_lap_times():
    logger.info("Starting F1 lap times sync")
    schedule = get_race_schedule(CURRENT_SEASON)
    if schedule is None or schedule.empty:
        return

    async with AsyncSessionLocal() as session:
        for _, event in schedule.iterrows():
            round_number = int(event["RoundNumber"])
            race_date = event["EventDate"].to_pydatetime()

            if race_date.replace(tzinfo=timezone.utc) > datetime.now(timezone.utc):
                continue

            result = await session.execute(
                select(F1Race).where(
                    F1Race.season == CURRENT_SEASON,
                    F1Race.round == round_number,
                )
            )
            race = result.scalar_one_or_none()
            if not race:
                continue

            laps = get_lap_times(CURRENT_SEASON, round_number)
            if laps is None or laps.empty:
                continue

            for _, lap in laps.iterrows():
                driver_result = await session.execute(
                    select(F1Driver).where(F1Driver.driver_ref == str(lap["Driver"]))
                )
                driver = driver_result.scalar_one_or_none()
                if not driver:
                    continue

                lap_seconds = lap["LapTime"].total_seconds() if lap["LapTime"] is not None else None

                stmt = insert(F1LapTime).values(
                    season=CURRENT_SEASON,
                    race_id=race.id,
                    driver_id=driver.id,
                    lap_number=int(lap["LapNumber"]),
                    lap_time_seconds=lap_seconds,
                    position=int(lap["Position"]) if lap["Position"] else None,
                ).on_conflict_do_nothing()
                await session.execute(stmt)

        await session.commit()

    redis = get_redis_client()
    await redis.hset("ingest_lag", "f1_lap_times", datetime.now(timezone.utc).isoformat())
    logger.info("F1 lap times sync complete")