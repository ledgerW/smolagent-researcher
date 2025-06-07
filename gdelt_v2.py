import aiohttp
import asyncio
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

BASE_URL_V2 = "https://api.gdeltproject.org/api/v2"


class TooManyRequests(Exception):
    """Raised when the API rate limit is hit."""


class RateLimiter:
    def __init__(self, rate: float = 1.0) -> None:
        self.rate = rate
        self._lock = asyncio.Lock()
        self._last_call = 0.0

    async def __aenter__(self) -> None:
        await self._lock.acquire()
        wait_time = self._last_call + 1 / self.rate - asyncio.get_event_loop().time()
        if wait_time > 0:
            await asyncio.sleep(wait_time)

    async def __aexit__(self, exc_type, exc, tb) -> None:
        self._last_call = asyncio.get_event_loop().time()
        self._lock.release()


rate_limiter = RateLimiter()


@dataclass
class DocResponse:
    articles: List[Dict[str, Any]] = field(default_factory=list)
    total: Optional[int] = None


@dataclass
class GKGResponse:
    gkg: List[Dict[str, Any]] = field(default_factory=list)
    total: Optional[int] = None


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


async def query_doc(
    query: str,
    mode: str = "TimelineTone",
    start: Optional[str] = None,
    end: Optional[str] = None,
) -> DocResponse:
    params = {"query": query, "mode": mode, "format": "json"}
    if start:
        params["startdatetime"] = start
    if end:
        params["enddatetime"] = end
    data = await _request_json(f"{BASE_URL_V2}/doc/doc", params)
    return DocResponse(articles=data.get("articles", []), total=data.get("total"))


async def query_gkg(query: str, themes: Optional[List[str]] = None) -> GKGResponse:
    params = {"query": query, "format": "json"}
    if themes:
        params["query"] = query + " " + " ".join(themes)
    data = await _request_json(f"{BASE_URL_V2}/gkg/gkg", params)
    return GKGResponse(gkg=data.get("gkg", []), total=data.get("total"))

