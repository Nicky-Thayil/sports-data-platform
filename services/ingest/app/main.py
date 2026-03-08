"""
Ingest service for the application.
"""

import logging
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from shared.config import get_settings
from services.ingest.app.jobs.f1 import sync_f1_races, sync_f1_lap_times, sync_f1_drivers
from services.ingest.app.jobs.pl import sync_pl_standings, sync_pl_fixtures

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()


async def main():
    scheduler = AsyncIOScheduler()

    scheduler.add_job(sync_f1_races, "interval", hours=12, id="f1_races")
    scheduler.add_job(sync_f1_lap_times, "interval", hours=12, id="f1_lap_times")
    scheduler.add_job(sync_f1_drivers, "interval", hours=24, id="f1_drivers")
    scheduler.add_job(sync_pl_standings, "interval", hours=6, id="pl_standings")
    scheduler.add_job(sync_pl_fixtures, "interval", hours=6, id="pl_fixtures")

    scheduler.start()
    logger.info("Ingest service started")

    try:
        while True:
            await asyncio.sleep(3600)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()


if __name__ == "__main__":
    asyncio.run(main())