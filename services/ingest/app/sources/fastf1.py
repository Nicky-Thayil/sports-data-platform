"""
FastF1 data source for ingesting F1 data.
"""

import fastf1
import pandas as pd
from pathlib import Path
import tempfile

CACHE_DIR = Path(tempfile.gettempdir()) / "fastf1_cache"
CACHE_DIR.mkdir(exist_ok=True)
fastf1.Cache.enable_cache(str(CACHE_DIR))


def get_race_schedule(season: int) -> pd.DataFrame:
    schedule = fastf1.get_event_schedule(season, include_testing=False)
    return schedule


def get_session_results(season: int, round_number: int) -> pd.DataFrame | None:
    try:
        session = fastf1.get_session(season, round_number, "R")
        session.load(laps=False, telemetry=False, weather=False, messages=False)
        return session.results
    except Exception:
        return None


def get_lap_times(season: int, round_number: int) -> pd.DataFrame | None:
    try:
        session = fastf1.get_session(season, round_number, "R")
        session.load(laps=True, telemetry=False, weather=False, messages=False)
        return session.laps
    except Exception:
        return None