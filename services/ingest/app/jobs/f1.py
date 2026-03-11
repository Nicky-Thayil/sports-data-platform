"""
F1 data ingestion jobs.
"""

import logging
import pandas as pd
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

async def sync_f1_drivers():
    logger.info("Starting F1 driver sync")
    schedule = get_race_schedule(CURRENT_SEASON)
    if schedule is None or schedule.empty:
        return

    # Get first completed race to extract driver list
    results = get_session_results(CURRENT_SEASON, 1)
    if results is None or results.empty:
        logger.warning("No session results available for driver sync")
        return

    async with AsyncSessionLocal() as session:
        for _, driver in results.iterrows():
            stmt = insert(F1Driver).values(
                driver_ref=str(driver["Abbreviation"]),
                code=str(driver["Abbreviation"]),
                first_name=str(driver["FirstName"]),
                last_name=str(driver["LastName"]),
                nationality=None,
            ).on_conflict_do_update(
                constraint="f1_drivers_driver_ref_key",
                set_=dict(
                    first_name=str(driver["FirstName"]),
                    last_name=str(driver["LastName"]),
                )
            )
            await session.execute(stmt)
        await session.commit()

    redis = get_redis_client()
    await redis.hset("ingest_lag", "f1_drivers", datetime.now(timezone.utc).isoformat())
    logger.info("F1 driver sync complete")

async def sync_f1_lap_times():
    logger.info("Starting F1 lap times sync")
    schedule = get_race_schedule(CURRENT_SEASON)
    if schedule is None or schedule.empty:
        return

    async with AsyncSessionLocal() as session:
        driver_result = await session.execute(select(F1Driver))
        driver_map: dict[str, F1Driver] = {
            d.driver_ref: d for d in driver_result.scalars().all()
        }
        
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
                driver = driver_map.get(str(lap["Driver"]))
                if not driver:
                    logger.warning(f"Driver not found in map: {lap['Driver']} — skipping lap")
                    continue

                lap_seconds = lap["LapTime"].total_seconds() if lap["LapTime"] is not None else None

                stmt = insert(F1LapTime).values(
                    season=CURRENT_SEASON,
                    race_id=race.id,
                    driver_id=driver.id,
                    lap_number=int(lap["LapNumber"]),
                    lap_time_seconds=lap_seconds,
                    position=int(lap["Position"]) if lap["Position"] and not pd.isna(lap["Position"]) else None,
                ).on_conflict_do_nothing()
                await session.execute(stmt)

        await session.commit()

    redis = get_redis_client()
    await redis.hset("ingest_lag", "f1_lap_times", datetime.now(timezone.utc).isoformat())
    logger.info("F1 lap times sync complete")