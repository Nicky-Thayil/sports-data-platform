"""
Ingest service for the application.
"""

import logging
import asyncio
import os
import sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    job_name = os.environ.get("JOB_NAME")

    if not job_name:
        logger.error("JOB_NAME environment variable not set")
        sys.exit(1)

    logger.info(f"Starting job: {job_name}")

    try:
        if job_name == "sync_f1_races":
            from services.ingest.app.jobs.f1 import sync_f1_races
            await sync_f1_races()

        elif job_name == "sync_f1_drivers":
            from services.ingest.app.jobs.f1 import sync_f1_drivers
            await sync_f1_drivers()

        elif job_name == "sync_f1_lap_times":
            from services.ingest.app.jobs.f1 import sync_f1_lap_times
            await sync_f1_lap_times()

        elif job_name == "sync_pl_standings":
            from services.ingest.app.jobs.pl import sync_pl_standings
            await sync_pl_standings()

        elif job_name == "sync_pl_fixtures":
            from services.ingest.app.jobs.pl import sync_pl_fixtures
            await sync_pl_fixtures()

        else:
            logger.error(f"Unknown job: {job_name}")
            sys.exit(1)

    except Exception:
        logger.exception(f"Job failed: {job_name}")
        sys.exit(1)

    logger.info(f"Job complete: {job_name}")


if __name__ == "__main__":
    asyncio.run(main())