import sys, pathlib
sys.path.append(str(pathlib.Path(__file__).resolve().parents[2]))
import asyncio
from types import SimpleNamespace

import pytest

import gdelt_v2
import gdelt_v3


class DummyResponse:
    def __init__(self, status: int, json_data: dict, headers: dict | None = None):
        self.status = status
        self._json = json_data
        self.headers = headers or {}

    async def json(self):
        return self._json

    def raise_for_status(self):
        if self.status >= 400:
            raise Exception("HTTP error")


class DummyContext:
    def __init__(self, response):
        self.response = response

    async def __aenter__(self):
        return self.response

    async def __aexit__(self, exc_type, exc, tb):
        return False


@pytest.mark.asyncio
async def test_query_doc_success(mocker):
    resp = DummyResponse(200, {"articles": [{"title": "a"}], "total": 1})
    session = SimpleNamespace(get=mocker.Mock(return_value=DummyContext(resp)))
    mocker.patch("aiohttp.ClientSession", return_value=DummyContext(session))
    result = await gdelt_v2.query_doc("test")
    assert result.articles[0]["title"] == "a"


@pytest.mark.asyncio
async def test_get_entities_retry(mocker):
    resp1 = DummyResponse(429, {}, {"Retry-After": "1"})
    resp2 = DummyResponse(200, {"entities": [{"name": "x"}]})
    session = SimpleNamespace(get=mocker.Mock(side_effect=[DummyContext(resp1), DummyContext(resp2)]))
    mocker.patch("aiohttp.ClientSession", return_value=DummyContext(session))
    result = await gdelt_v3.get_entities("s", "e", "q")
    assert result.entities[0]["name"] == "x"

