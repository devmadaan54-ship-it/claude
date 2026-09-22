"""
Tracxn API Client
Async wrapper over the Tracxn JSON-over-HTTPS API (companies, investors,
funding transactions, acquisitions) with mock mode, retry and pagination support.

Tracxn is a REST API, not a SQL database: there is no host/port to dial. You
authenticate with an access token generated from the API Token page at
https://platform.tracxn.com/a/api/apitoken and POST JSON filter bodies.
"""

import asyncio
import random
from typing import Any, AsyncGenerator, Optional
from dataclasses import dataclass, field

import httpx

from config import settings


# Datasets exposed by the Tracxn API, mapped to their endpoint path.
# Trial accounts are typically enabled for a subset of these.
DATASETS: dict[str, str] = {
    "companies": "companies",
    "investors": "investors",
    "fundings": "fundings",
    "acquisitions": "acquisitions",
}

# Tracxn caps an unfiltered call at 20 records; paginate for more.
MAX_PAGE_SIZE = 20

# Status codes worth retrying: rate limit plus transient upstream failures.
RETRYABLE_STATUS = {429, 500, 502, 503, 504}


class TracxnError(Exception):
    """Base error for Tracxn API failures."""


class TracxnAuthError(TracxnError):
    """Raised when the access token is missing, invalid or expired.

    Trial-account tokens are revoked automatically when the trial ends, so a
    token that worked yesterday can start returning 401 today.
    """


class TracxnRateLimitError(TracxnError):
    """Raised when the account's rate limit is exhausted and retries ran out."""


@dataclass
class TracxnPage:
    """One page of results from a Tracxn dataset."""
    dataset: str
    rows: list[dict] = field(default_factory=list)
    total_count: int = 0
    offset: int = 0
    size: int = 0
    raw: dict = field(default_factory=dict)

    @property
    def has_more(self) -> bool:
        """True when more records exist beyond this page."""
        return self.offset + len(self.rows) < self.total_count


# Mock rows let the UI and tests run without burning API credits.
MOCK_ROWS: dict[str, list[dict]] = {
    "companies": [
        {
            "id": "mock-co-1",
            "name": "Northwind Analytics",
            "domain": "northwind-analytics.example",
            "description": "Mock company row returned because TRACXN_MOCK_MODE is on.",
            "foundedYear": 2019,
            "location": {"country": "United States", "city": "San Francisco"},
            "totalFunding": {"amount": 42000000, "currency": "USD"},
            "latestRound": "Series B",
        },
        {
            "id": "mock-co-2",
            "name": "Lumen Robotics",
            "domain": "lumen-robotics.example",
            "description": "Mock company row returned because TRACXN_MOCK_MODE is on.",
            "foundedYear": 2021,
            "location": {"country": "India", "city": "Bengaluru"},
            "totalFunding": {"amount": 8500000, "currency": "USD"},
            "latestRound": "Seed",
        },
    ],
    "investors": [
        {
            "id": "mock-inv-1",
            "name": "Meridian Capital",
            "type": "Venture Capital",
            "location": {"country": "United States", "city": "Menlo Park"},
            "portfolioCount": 214,
        },
    ],
    "fundings": [
        {
            "id": "mock-fund-1",
            "companyName": "Northwind Analytics",
            "round": "Series B",
            "amount": {"amount": 30000000, "currency": "USD"},
            "date": "2025-11-04",
            "investors": ["Meridian Capital"],
        },
    ],
    "acquisitions": [
        {
            "id": "mock-acq-1",
            "acquirerName": "Globex Corp",
            "targetName": "Lumen Robotics",
            "amount": {"amount": 120000000, "currency": "USD"},
            "date": "2026-02-17",
        },
    ],
}


def _extract_rows(payload: dict) -> list[dict]:
    """Pull the record list out of a Tracxn response envelope.

    The envelope key differs between datasets and API versions, so check the
    known shapes rather than hard-coding one and breaking on the others.
    """
    for key in ("result", "results", "data", "rows", "records"):
        value = payload.get(key)
        if isinstance(value, list):
            return value
        # Some responses nest the list one level deeper, e.g. {"data": {"result": [...]}}
        if isinstance(value, dict):
            for inner in ("result", "results", "data", "rows", "records"):
                nested = value.get(inner)
                if isinstance(nested, list):
                    return nested
    return []


def _extract_total(payload: dict, fallback: int) -> int:
    """Pull the total match count out of a Tracxn response envelope."""
    for key in ("totalCount", "total_count", "total", "count", "matchCount"):
        value = payload.get(key)
        if isinstance(value, int):
            return value
        if isinstance(value, dict):
            inner = value.get("value")
            if isinstance(inner, int):
                return inner
    data = payload.get("data")
    if isinstance(data, dict):
        return _extract_total(data, fallback)
    return fallback


class TracxnClient:
    """Async client for the Tracxn API.

    Usage:
        async with TracxnClient() as client:
            page = await client.search("companies", {"companyName": ["Stripe"]})
    """

    def __init__(
        self,
        access_token: Optional[str] = None,
        base_url: Optional[str] = None,
        auth_header: Optional[str] = None,
        mock_mode: Optional[bool] = None,
    ):
        self.access_token = access_token or settings.TRACXN_ACCESS_TOKEN
        self.base_url = (base_url or settings.TRACXN_BASE_URL).rstrip("/")
        self.auth_header = auth_header or settings.TRACXN_AUTH_HEADER
        self.mock_mode = mock_mode if mock_mode is not None else settings.TRACXN_MOCK_MODE
        self._client: Optional[httpx.AsyncClient] = None

    # ============== Lifecycle ==============

    async def __aenter__(self) -> "TracxnClient":
        self._ensure_client()
        return self

    async def __aexit__(self, *exc_info) -> None:
        await self.aclose()

    def _ensure_client(self) -> httpx.AsyncClient:
        """Create the underlying HTTP client on first use and reuse it after."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=httpx.Timeout(settings.TRACXN_TIMEOUT),
                headers=self._headers(),
            )
        return self._client

    async def aclose(self) -> None:
        """Close the underlying connection pool."""
        if self._client is not None and not self._client.is_closed:
            await self._client.aclose()
        self._client = None

    def _headers(self) -> dict[str, str]:
        """Build request headers, including the configured auth header."""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if self.access_token:
            headers[self.auth_header] = self.access_token
        return headers

    @property
    def is_configured(self) -> bool:
        """True when a token is present, or when mock mode makes one unnecessary."""
        return self.mock_mode or bool(self.access_token)

    # ============== Core request ==============

    async def _post(self, path: str, body: dict) -> dict:
        """POST a JSON body with retry on rate limits and transient failures."""
        client = self._ensure_client()
        attempts = settings.TRACXN_MAX_RETRIES + 1
        last_error: Optional[Exception] = None

        for attempt in range(attempts):
            try:
                response = await client.post(f"/{path.lstrip('/')}", json=body)
            except httpx.RequestError as exc:
                # Network-level failure: worth one more try before giving up.
                last_error = TracxnError(f"Could not reach Tracxn at {self.base_url}: {exc}")
                if attempt + 1 < attempts:
                    await asyncio.sleep(self._backoff(attempt))
                    continue
                raise last_error from exc

            if response.status_code in (401, 403):
                raise TracxnAuthError(
                    f"Tracxn rejected the access token (HTTP {response.status_code}). "
                    f"Check TRACXN_ACCESS_TOKEN and that '{self.auth_header}' is the "
                    "header name your account expects. Trial tokens are revoked when "
                    "the trial ends. Token page: https://platform.tracxn.com/a/api/apitoken"
                )

            if response.status_code in RETRYABLE_STATUS:
                if attempt + 1 < attempts:
                    await asyncio.sleep(self._backoff(attempt, response))
                    continue
                if response.status_code == 429:
                    raise TracxnRateLimitError(
                        "Tracxn rate limit still exhausted after "
                        f"{settings.TRACXN_MAX_RETRIES} retries."
                    )
                raise TracxnError(
                    f"Tracxn returned HTTP {response.status_code} after "
                    f"{settings.TRACXN_MAX_RETRIES} retries: {response.text[:300]}"
                )

            if response.status_code >= 400:
                raise TracxnError(
                    f"Tracxn returned HTTP {response.status_code}: {response.text[:300]}"
                )

            try:
                return response.json()
            except ValueError as exc:
                raise TracxnError(
                    f"Tracxn returned a non-JSON body: {response.text[:300]}"
                ) from exc

        raise last_error or TracxnError("Tracxn request failed for an unknown reason")

    def _backoff(self, attempt: int, response: Optional[httpx.Response] = None) -> float:
        """Seconds to wait before the next attempt, honouring Retry-After."""
        if response is not None:
            retry_after = response.headers.get("Retry-After")
            if retry_after:
                try:
                    return min(float(retry_after), 60.0)
                except ValueError:
                    pass
        # Exponential backoff with jitter so parallel callers do not sync up.
        return min(2 ** attempt, 30) + random.uniform(0, 0.5)

    # ============== Queries ==============

    async def search(
        self,
        dataset: str = "companies",
        filters: Optional[dict[str, Any]] = None,
        offset: int = 0,
        size: int = MAX_PAGE_SIZE,
        sort: Optional[dict[str, Any]] = None,
        extra_body: Optional[dict[str, Any]] = None,
    ) -> TracxnPage:
        """Search one Tracxn dataset and return a single page of results.

        `filters` is passed through to the API untouched, so any filter your
        plan supports works without a client change.
        """
        if dataset not in DATASETS:
            raise TracxnError(
                f"Unknown dataset '{dataset}'. Available: {', '.join(sorted(DATASETS))}"
            )

        size = max(1, min(size, MAX_PAGE_SIZE))

        if self.mock_mode:
            return self._mock_page(dataset, offset, size)

        if not self.access_token:
            raise TracxnAuthError(
                "TRACXN_ACCESS_TOKEN is not set. Generate one at "
                "https://platform.tracxn.com/a/api/apitoken, or set "
                "TRACXN_MOCK_MODE=True to work against mock data."
            )

        body: dict[str, Any] = {
            "filter": filters or {},
            "from": offset,
            "size": size,
        }
        if sort:
            body["sort"] = sort
        if extra_body:
            body.update(extra_body)

        payload = await self._post(DATASETS[dataset], body)
        rows = _extract_rows(payload)
        return TracxnPage(
            dataset=dataset,
            rows=rows,
            total_count=_extract_total(payload, fallback=offset + len(rows)),
            offset=offset,
            size=size,
            raw=payload,
        )

    async def iterate(
        self,
        dataset: str = "companies",
        filters: Optional[dict[str, Any]] = None,
        limit: int = 100,
        page_size: int = MAX_PAGE_SIZE,
        sort: Optional[dict[str, Any]] = None,
    ) -> AsyncGenerator[dict, None]:
        """Yield records across pages until `limit` rows or the result set ends.

        Each page costs credits, so `limit` is a hard stop rather than a hint.
        """
        yielded = 0
        offset = 0

        while yielded < limit:
            page = await self.search(
                dataset=dataset,
                filters=filters,
                offset=offset,
                size=min(page_size, limit - yielded),
                sort=sort,
            )
            if not page.rows:
                return

            for row in page.rows:
                yield row
                yielded += 1
                if yielded >= limit:
                    return

            if not page.has_more:
                return
            offset += len(page.rows)

    async def collect(
        self,
        dataset: str = "companies",
        filters: Optional[dict[str, Any]] = None,
        limit: int = 100,
        sort: Optional[dict[str, Any]] = None,
    ) -> list[dict]:
        """Collect up to `limit` records into a list."""
        return [
            row
            async for row in self.iterate(
                dataset=dataset, filters=filters, limit=limit, sort=sort
            )
        ]

    async def search_companies(
        self,
        name: Optional[str] = None,
        filters: Optional[dict[str, Any]] = None,
        offset: int = 0,
        size: int = MAX_PAGE_SIZE,
    ) -> TracxnPage:
        """Search companies, optionally by name."""
        merged = dict(filters or {})
        if name:
            merged.setdefault("companyName", [name])
        return await self.search("companies", merged, offset=offset, size=size)

    async def search_investors(
        self,
        name: Optional[str] = None,
        filters: Optional[dict[str, Any]] = None,
        offset: int = 0,
        size: int = MAX_PAGE_SIZE,
    ) -> TracxnPage:
        """Search investors, optionally by name."""
        merged = dict(filters or {})
        if name:
            merged.setdefault("investorName", [name])
        return await self.search("investors", merged, offset=offset, size=size)

    async def search_fundings(
        self,
        filters: Optional[dict[str, Any]] = None,
        offset: int = 0,
        size: int = MAX_PAGE_SIZE,
    ) -> TracxnPage:
        """Search funding transactions."""
        return await self.search("fundings", filters, offset=offset, size=size)

    async def search_acquisitions(
        self,
        filters: Optional[dict[str, Any]] = None,
        offset: int = 0,
        size: int = MAX_PAGE_SIZE,
    ) -> TracxnPage:
        """Search acquisitions."""
        return await self.search("acquisitions", filters, offset=offset, size=size)

    # ============== Diagnostics ==============

    async def ping(self) -> dict[str, Any]:
        """Make the smallest possible real call to verify the connection.

        Returns a diagnostic dict instead of raising, so a failing token can be
        reported to the caller rather than crashing startup.
        """
        if self.mock_mode:
            return {
                "connected": True,
                "mock_mode": True,
                "base_url": self.base_url,
                "detail": "Mock mode is on; no request was made to Tracxn.",
            }

        if not self.access_token:
            return {
                "connected": False,
                "mock_mode": False,
                "base_url": self.base_url,
                "error": "TRACXN_ACCESS_TOKEN is not set.",
            }

        try:
            page = await self.search("companies", filters={}, size=1)
        except TracxnError as exc:
            return {
                "connected": False,
                "mock_mode": False,
                "base_url": self.base_url,
                "auth_header": self.auth_header,
                "error": str(exc),
            }

        return {
            "connected": True,
            "mock_mode": False,
            "base_url": self.base_url,
            "auth_header": self.auth_header,
            "rows_returned": len(page.rows),
            "total_count": page.total_count,
        }

    # ============== Mock support ==============

    def _mock_page(self, dataset: str, offset: int, size: int) -> TracxnPage:
        """Build a deterministic page of mock rows for the given dataset."""
        rows = MOCK_ROWS.get(dataset, [])
        window = rows[offset:offset + size]
        return TracxnPage(
            dataset=dataset,
            rows=window,
            total_count=len(rows),
            offset=offset,
            size=size,
            raw={"mock": True, "result": window, "totalCount": len(rows)},
        )


# Global client instance, created lazily so settings changes are picked up.
_client: Optional[TracxnClient] = None


def get_tracxn_client() -> TracxnClient:
    """Get the shared Tracxn client instance."""
    global _client
    if _client is None:
        _client = TracxnClient()
    return _client


async def reset_tracxn_client() -> None:
    """Drop the shared client so the next call picks up new settings."""
    global _client
    if _client is not None:
        await _client.aclose()
    _client = None
