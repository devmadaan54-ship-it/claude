"""
Tracxn Data API Routes
Search company, investor, funding and acquisition data from Tracxn.
"""

from fastapi import APIRouter, HTTPException

from config import settings, update_tracxn_config
from models.schemas import (
    TracxnSearchRequest,
    TracxnSearchResponse,
    TracxnCollectRequest,
    TracxnStatusResponse,
    TracxnConfigUpdate,
)
from utils.tracxn_client import (
    TracxnAuthError,
    TracxnError,
    TracxnRateLimitError,
    get_tracxn_client,
    reset_tracxn_client,
)

router = APIRouter(prefix="/tracxn", tags=["Tracxn"])


def _to_http_error(exc: TracxnError) -> HTTPException:
    """Map a Tracxn client error onto the closest HTTP status."""
    if isinstance(exc, TracxnAuthError):
        return HTTPException(status_code=401, detail=str(exc))
    if isinstance(exc, TracxnRateLimitError):
        return HTTPException(status_code=429, detail=str(exc))
    return HTTPException(status_code=502, detail=str(exc))


@router.get("/status", response_model=TracxnStatusResponse)
async def tracxn_status():
    """Verify the Tracxn connection and report what is configured.

    Hit this first after setting a token: it makes a one-record call and tells
    you whether the token and header name are accepted.
    """
    client = get_tracxn_client()
    result = await client.ping()
    return TracxnStatusResponse(
        connected=result.get("connected", False),
        mock_mode=result.get("mock_mode", settings.TRACXN_MOCK_MODE),
        base_url=result.get("base_url", settings.TRACXN_BASE_URL),
        configured=client.is_configured,
        auth_header=result.get("auth_header"),
        rows_returned=result.get("rows_returned"),
        total_count=result.get("total_count"),
        error=result.get("error"),
    )


@router.post("/search", response_model=TracxnSearchResponse)
async def tracxn_search(request: TracxnSearchRequest):
    """Search a single page of a Tracxn dataset (max 20 records per call)."""
    client = get_tracxn_client()

    filters = dict(request.filters)
    if request.name:
        # Shorthand: map `name` onto the dataset's own name filter.
        name_field = {
            "companies": "companyName",
            "investors": "investorName",
            "fundings": "companyName",
            "acquisitions": "targetName",
        }[request.dataset.value]
        filters.setdefault(name_field, [request.name])

    try:
        page = await client.search(
            dataset=request.dataset.value,
            filters=filters,
            offset=request.offset,
            size=request.size,
            sort=request.sort,
        )
    except TracxnError as exc:
        raise _to_http_error(exc) from exc

    return TracxnSearchResponse(
        dataset=request.dataset,
        rows=page.rows,
        total_count=page.total_count,
        offset=page.offset,
        size=page.size,
        has_more=page.has_more,
        mock_mode=client.mock_mode,
    )


@router.post("/collect", response_model=TracxnSearchResponse)
async def tracxn_collect(request: TracxnCollectRequest):
    """Page through a dataset and collect up to `limit` records in one response.

    Every page costs API credits, so `limit` is enforced as a hard stop.
    """
    client = get_tracxn_client()

    try:
        rows = await client.collect(
            dataset=request.dataset.value,
            filters=request.filters,
            limit=request.limit,
            sort=request.sort,
        )
    except TracxnError as exc:
        raise _to_http_error(exc) from exc

    return TracxnSearchResponse(
        dataset=request.dataset,
        rows=rows,
        total_count=len(rows),
        offset=0,
        size=len(rows),
        has_more=False,
        mock_mode=client.mock_mode,
    )


@router.post("/config")
async def tracxn_update_config(update: TracxnConfigUpdate):
    """Update the Tracxn token and settings at runtime, then reconnect."""
    update_tracxn_config(
        access_token=update.access_token,
        base_url=update.base_url,
        auth_header=update.auth_header,
        mock_mode=update.mock_mode,
    )
    # Drop the pooled client so the next call uses the new credentials.
    await reset_tracxn_client()

    client = get_tracxn_client()
    return {
        "status": "updated",
        "mock_mode": client.mock_mode,
        "base_url": client.base_url,
        "auth_header": client.auth_header,
        "has_access_token": bool(client.access_token),
    }
