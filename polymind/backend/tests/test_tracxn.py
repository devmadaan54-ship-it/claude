"""
Tests for the Tracxn API client and routes.

Uses httpx.MockTransport so nothing is sent to Tracxn and no credits are spent.
"""

import json

import httpx
import pytest

from config import settings
from utils.tracxn_client import (
    MAX_PAGE_SIZE,
    TracxnAuthError,
    TracxnClient,
    TracxnError,
    TracxnRateLimitError,
    _extract_rows,
    _extract_total,
)


def make_client(handler, **kwargs) -> TracxnClient:
    """Build a client whose HTTP layer is backed by a mock transport."""
    client = TracxnClient(access_token="test-token", mock_mode=False, **kwargs)
    client._client = httpx.AsyncClient(
        base_url=client.base_url,
        transport=httpx.MockTransport(handler),
        headers=client._headers(),
    )
    return client


# ============== Envelope parsing ==============

@pytest.mark.parametrize("payload, expected", [
    ({"result": [{"a": 1}]}, [{"a": 1}]),
    ({"results": [{"a": 1}]}, [{"a": 1}]),
    ({"data": [{"a": 1}]}, [{"a": 1}]),
    ({"data": {"result": [{"a": 1}]}}, [{"a": 1}]),
    ({"rows": [{"a": 1}]}, [{"a": 1}]),
    ({"unexpected": 5}, []),
])
def test_extract_rows_handles_envelope_shapes(payload, expected):
    assert _extract_rows(payload) == expected


@pytest.mark.parametrize("payload, expected", [
    ({"totalCount": 12}, 12),
    ({"total": 7}, 7),
    ({"count": {"value": 3}}, 3),
    ({"data": {"totalCount": 9}}, 9),
])
def test_extract_total_handles_envelope_shapes(payload, expected):
    assert _extract_total(payload, fallback=0) == expected


def test_extract_total_falls_back_when_absent():
    assert _extract_total({"result": []}, fallback=42) == 42


# ============== Auth and configuration ==============

def test_auth_header_carries_the_token():
    client = TracxnClient(access_token="abc123", auth_header="accessToken")
    assert client._headers()["accessToken"] == "abc123"


def test_headers_omit_auth_when_token_missing():
    client = TracxnClient(access_token=None)
    assert settings.TRACXN_AUTH_HEADER not in client._headers()


@pytest.mark.asyncio
async def test_search_without_token_raises_auth_error():
    client = TracxnClient(access_token=None, mock_mode=False)
    with pytest.raises(TracxnAuthError, match="TRACXN_ACCESS_TOKEN"):
        await client.search("companies")


@pytest.mark.asyncio
async def test_401_raises_auth_error_with_guidance():
    def handler(request):
        return httpx.Response(
            401, json={"errorCode": 401670000, "message": "Token was not recognised"}
        )

    async with make_client(handler) as client:
        with pytest.raises(TracxnAuthError, match="apitoken"):
            await client.search("companies")


# ============== Request shape ==============

@pytest.mark.asyncio
async def test_search_posts_filter_from_and_size():
    seen = {}

    def handler(request):
        seen["url"] = str(request.url)
        seen["body"] = json.loads(request.content)
        seen["token"] = request.headers.get("accessToken")
        return httpx.Response(200, json={"result": [{"id": "1"}], "totalCount": 1})

    async with make_client(handler) as client:
        await client.search("companies", {"companyName": ["Stripe"]}, offset=20, size=10)

    assert seen["url"].endswith("/companies")
    assert seen["body"] == {"filter": {"companyName": ["Stripe"]}, "from": 20, "size": 10}
    assert seen["token"] == "test-token"


@pytest.mark.asyncio
async def test_size_is_clamped_to_api_maximum():
    seen = {}

    def handler(request):
        seen["body"] = json.loads(request.content)
        return httpx.Response(200, json={"result": [], "totalCount": 0})

    async with make_client(handler) as client:
        await client.search("companies", size=500)

    assert seen["body"]["size"] == MAX_PAGE_SIZE


@pytest.mark.asyncio
async def test_unknown_dataset_is_rejected_before_any_request():
    called = False

    def handler(request):
        nonlocal called
        called = True
        return httpx.Response(200, json={})

    async with make_client(handler) as client:
        with pytest.raises(TracxnError, match="Unknown dataset"):
            await client.search("not_a_dataset")

    assert called is False


# ============== Pagination ==============

@pytest.mark.asyncio
async def test_iterate_pages_until_result_set_is_exhausted():
    total = 45
    rows = [{"id": str(i)} for i in range(total)]

    def handler(request):
        body = json.loads(request.content)
        start, size = body["from"], body["size"]
        return httpx.Response(
            200, json={"result": rows[start:start + size], "totalCount": total}
        )

    async with make_client(handler) as client:
        collected = await client.collect("companies", limit=total)

    assert [row["id"] for row in collected] == [str(i) for i in range(total)]


@pytest.mark.asyncio
async def test_collect_stops_at_limit_without_extra_calls():
    calls = 0
    rows = [{"id": str(i)} for i in range(100)]

    def handler(request):
        nonlocal calls
        calls += 1
        body = json.loads(request.content)
        start, size = body["from"], body["size"]
        return httpx.Response(
            200, json={"result": rows[start:start + size], "totalCount": 100}
        )

    async with make_client(handler) as client:
        collected = await client.collect("companies", limit=5)

    # A 5-record limit must cost exactly one page, not a full sweep.
    assert len(collected) == 5
    assert calls == 1


@pytest.mark.asyncio
async def test_iterate_stops_on_empty_page():
    def handler(request):
        # Claims more records exist but returns none: must not loop forever.
        return httpx.Response(200, json={"result": [], "totalCount": 999})

    async with make_client(handler) as client:
        collected = await client.collect("companies", limit=50)

    assert collected == []


@pytest.mark.asyncio
async def test_has_more_reflects_remaining_records():
    def handler(request):
        return httpx.Response(
            200, json={"result": [{"id": "1"}], "totalCount": 10}
        )

    async with make_client(handler) as client:
        page = await client.search("companies", size=1)

    assert page.has_more is True


# ============== Retries ==============

@pytest.mark.asyncio
async def test_rate_limit_is_retried_then_succeeds(monkeypatch):
    monkeypatch.setattr(settings, "TRACXN_MAX_RETRIES", 2)
    attempts = 0

    def handler(request):
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            return httpx.Response(429, headers={"Retry-After": "0"}, json={})
        return httpx.Response(200, json={"result": [{"id": "1"}], "totalCount": 1})

    async with make_client(handler) as client:
        page = await client.search("companies")

    assert attempts == 2
    assert len(page.rows) == 1


@pytest.mark.asyncio
async def test_persistent_rate_limit_raises(monkeypatch):
    monkeypatch.setattr(settings, "TRACXN_MAX_RETRIES", 1)

    def handler(request):
        return httpx.Response(429, headers={"Retry-After": "0"}, json={})

    async with make_client(handler) as client:
        with pytest.raises(TracxnRateLimitError):
            await client.search("companies")


@pytest.mark.asyncio
async def test_non_json_body_raises_tracxn_error():
    def handler(request):
        return httpx.Response(200, text="<html>maintenance</html>")

    async with make_client(handler) as client:
        with pytest.raises(TracxnError, match="non-JSON"):
            await client.search("companies")


def test_backoff_honours_retry_after_header():
    client = TracxnClient(access_token="t")
    response = httpx.Response(429, headers={"Retry-After": "7"})
    assert client._backoff(0, response) == 7.0


def test_backoff_ignores_unparseable_retry_after():
    client = TracxnClient(access_token="t")
    response = httpx.Response(429, headers={"Retry-After": "soon"})
    # Falls through to exponential backoff rather than crashing.
    assert 1.0 <= client._backoff(0, response) <= 1.5


# ============== Mock mode ==============

@pytest.mark.asyncio
async def test_mock_mode_returns_rows_without_a_token():
    client = TracxnClient(access_token=None, mock_mode=True)
    page = await client.search("companies")
    assert page.rows
    assert page.raw["mock"] is True


@pytest.mark.asyncio
async def test_mock_ping_makes_no_request():
    client = TracxnClient(access_token=None, mock_mode=True)
    result = await client.ping()
    assert result["connected"] is True
    assert result["mock_mode"] is True


@pytest.mark.asyncio
async def test_ping_reports_failure_instead_of_raising():
    def handler(request):
        return httpx.Response(401, json={"message": "Token was not recognised"})

    async with make_client(handler) as client:
        result = await client.ping()

    assert result["connected"] is False
    assert "error" in result


# ============== Routes ==============

@pytest.fixture
def api_client(monkeypatch):
    from fastapi.testclient import TestClient
    import main

    monkeypatch.setattr(settings, "TRACXN_MOCK_MODE", True)
    monkeypatch.setattr(settings, "TRACXN_ACCESS_TOKEN", None)

    import utils.tracxn_client as tc
    tc._client = None  # force a fresh client that picks up mock mode

    with TestClient(main.app) as client:
        yield client

    tc._client = None


def test_status_route_reports_mock_mode(api_client):
    response = api_client.get("/tracxn/status")
    assert response.status_code == 200
    body = response.json()
    assert body["connected"] is True
    assert body["mock_mode"] is True


def test_search_route_returns_rows(api_client):
    response = api_client.post("/tracxn/search", json={"dataset": "companies"})
    assert response.status_code == 200
    body = response.json()
    assert body["dataset"] == "companies"
    assert len(body["rows"]) > 0


def test_search_route_rejects_oversized_page(api_client):
    response = api_client.post("/tracxn/search", json={"dataset": "companies", "size": 50})
    assert response.status_code == 422


def test_search_route_rejects_unknown_dataset(api_client):
    response = api_client.post("/tracxn/search", json={"dataset": "spaceships"})
    assert response.status_code == 422


def test_collect_route_respects_limit(api_client):
    response = api_client.post(
        "/tracxn/collect", json={"dataset": "companies", "limit": 1}
    )
    assert response.status_code == 200
    assert len(response.json()["rows"]) == 1


def test_config_route_updates_token_and_reports_state(api_client):
    response = api_client.post(
        "/tracxn/config",
        json={"access_token": "new-token", "mock_mode": False, "auth_header": "accessToken"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["has_access_token"] is True
    assert body["mock_mode"] is False
    # The token itself must never be echoed back to the caller.
    assert "new-token" not in response.text
