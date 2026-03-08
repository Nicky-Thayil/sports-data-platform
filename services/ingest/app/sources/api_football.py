"""
API Football data source for ingesting Premier League data.
"""

import httpx
from shared.config import get_settings

BASE_URL = "https://v3.football.api-sports.io"
PL_LEAGUE_ID = 39


def _headers() -> dict:
    settings = get_settings()
    return {"x-apisports-key": settings.API_FOOTBALL_KEY}


async def get_standings(season: int) -> dict | None:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/standings",
            headers=_headers(),
            params={"league": PL_LEAGUE_ID, "season": season},
        )
        if response.status_code != 200:
            return None
        return response.json()


async def get_fixtures(season: int) -> dict | None:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/fixtures",
            headers=_headers(),
            params={"league": PL_LEAGUE_ID, "season": season},
        )
        if response.status_code != 200:
            return None
        return response.json()