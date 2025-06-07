import aiohttp
import asyncio
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from gdelt_v2 import RateLimiter, TooManyRequests

BASE_URL_V3 = "https://api.gdeltproject.org/api/v3"

rate_limiter = RateLimiter()


@dataclass
class EntityResponse:
    entities: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class EventResponse:
    events: List[Dict[str, Any]] = field(default_factory=list)


async def _request_json(endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
    @retry(
        retry=retry_if_exception_type(TooManyRequests),
        wait=wait_exponential(multiplier=1, min=1, max=60),
        stop=stop_after_attempt(3),
        reraise=True,
    )
    async def _inner() -> Dict[str, Any]:
        async with aiohttp.ClientSession() as session:
            async with rate_limiter:
                async with session.get(endpoint, params=params) as resp:
                    if resp.status == 429:
                        retry_after = int(resp.headers.get("Retry-After", "300"))
                        await asyncio.sleep(retry_after)
                        raise TooManyRequests()
                    resp.raise_for_status()
                    return await resp.json()

    return await _inner()


async def get_entities(start: str, end: str, query: str) -> EntityResponse:
    params = {
        "query": query,
        "format": "json",
        "startdatetime": start,
        "enddatetime": end,
    }
    data = await _request_json(f"{BASE_URL_V3}/entities", params)
    return EntityResponse(entities=data.get("entities", []))


async def get_events(start: str, end: str, query: str) -> EventResponse:
    params = {
        "query": query,
        "format": "json",
        "startdatetime": start,
        "enddatetime": end,
    }
    data = await _request_json(f"{BASE_URL_V3}/events", params)
    return EventResponse(events=data.get("events", []))

