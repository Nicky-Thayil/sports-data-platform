"""
Ingest service for the application.
"""

import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio
from shared.config import get_settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()


async def placeholder_job():
    logger.info("Ingest job running — replace with real jobs")


async def main():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(placeholder_job, "interval", minutes=30)
    scheduler.start()
    logger.info("Ingest service started")

    try:
        while True:
            await asyncio.sleep(3600)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()


if __name__ == "__main__":
    asyncio.run(main())