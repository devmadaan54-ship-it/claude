#!/usr/bin/env python3
"""
Tracxn Connection Checker

Verifies that PolyMind can reach the Tracxn API with your access token, and
reports exactly what failed if it cannot.

Because the header name carrying the token is account/plan specific, this
script probes the common variants and tells you which one your account
accepts, so you can pin it via TRACXN_AUTH_HEADER.

Usage:
    cd backend
    python scripts/check_tracxn.py                 # uses TRACXN_ACCESS_TOKEN from .env
    python scripts/check_tracxn.py --token <token> # or pass one explicitly
    python scripts/check_tracxn.py --probe-headers # try every known header name
"""

import argparse
import asyncio
import json
import os
import sys

# Allow running as `python scripts/check_tracxn.py` from the backend directory.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import httpx

from config import settings
from utils.tracxn_client import DATASETS, TracxnClient, TracxnError


# Header names seen across Tracxn plans and documentation.
CANDIDATE_HEADERS = [
    "accessToken",
    "access-token",
    "X-API-Key",
    "apiKey",
    "Authorization",
]


def mask(token: str) -> str:
    """Show enough of a token to identify it without printing the secret."""
    if not token:
        return "<not set>"
    if len(token) <= 8:
        return "*" * len(token)
    return f"{token[:4]}...{token[-4:]} ({len(token)} chars)"


async def probe_header(base_url: str, token: str, header: str) -> tuple[str, str]:
    """Try a single header name and classify the outcome.

    Tracxn distinguishes the two failure modes clearly, which is what makes
    this probe useful:
      401 "Token was not recognised"  -> the header WAS read; the token is bad
      403 "Invalid web session access" -> the header was ignored entirely

    Returns one of "accepted", "token-bad", "header-ignored", "error".
    """
    value = f"Bearer {token}" if header == "Authorization" else token
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        header: value,
    }
    body = {"filter": {}, "from": 0, "size": 1}

    try:
        async with httpx.AsyncClient(timeout=settings.TRACXN_TIMEOUT) as client:
            response = await client.post(
                f"{base_url.rstrip('/')}/companies", json=body, headers=headers
            )
    except httpx.RequestError as exc:
        return "error", f"network error: {exc}"

    detail = f"HTTP {response.status_code}: {response.text[:120]}"

    if response.status_code == 401:
        return "token-bad", detail
    if response.status_code == 403:
        return "header-ignored", detail
    if response.status_code == 429:
        # The request authenticated; the account is simply out of quota.
        return "accepted", "HTTP 429 (authenticated, but rate limited)"
    if response.status_code >= 400:
        return "error", detail
    return "accepted", f"HTTP {response.status_code} (authenticated)"


async def run_probe(base_url: str, token: str) -> None:
    """Try every candidate header and report which one the API actually reads."""
    print(f"\nProbing header names against {base_url}/companies ...\n")

    labels = {
        "accepted": "PASS",
        "token-bad": "READ",
        "header-ignored": "SKIP",
        "error": "FAIL",
    }
    accepted: list[str] = []
    read_but_bad: list[str] = []

    for header in CANDIDATE_HEADERS:
        status, detail = await probe_header(base_url, token, header)
        print(f"  [{labels[status]}] {header:<16} {detail}")
        if status == "accepted":
            accepted.append(header)
        elif status == "token-bad":
            read_but_bad.append(header)

    print()
    if accepted:
        print(f"Authenticated with: {', '.join(accepted)}")
        print(f"Set in backend/.env:  TRACXN_AUTH_HEADER={accepted[0]}")
        return

    if read_but_bad:
        print(f"Header(s) the API read: {', '.join(read_but_bad)}  (marked READ above)")
        print("The header name is right, so the TOKEN is the problem: it is wrong,")
        print("expired, or issued by a trial that has since ended.")
        print("Regenerate at https://platform.tracxn.com/a/api/apitoken")
        print(f"Then set:  TRACXN_AUTH_HEADER={read_but_bad[0]}")
        return

    print("No header was read by the API (all returned 403 / errors). Likely causes:")
    print("  - Your plan does not include API access (contact support@tracxn.com).")
    print("  - Outbound HTTPS to platform.tracxn.com is blocked from this host.")
    print("  - The base URL is wrong; confirm it on your API Token page.")


async def run_check(token: str) -> int:
    """Run the standard connection check and a sample query per dataset."""
    print("=" * 62)
    print("Tracxn Connection Check")
    print("=" * 62)
    print(f"  Base URL      : {settings.TRACXN_BASE_URL}")
    print(f"  Auth header   : {settings.TRACXN_AUTH_HEADER}")
    print(f"  Access token  : {mask(token)}")
    print(f"  Mock mode     : {settings.TRACXN_MOCK_MODE}")
    print(f"  Timeout       : {settings.TRACXN_TIMEOUT}s")
    print("-" * 62)

    if settings.TRACXN_MOCK_MODE:
        print("\nMock mode is ON, so nothing is sent to Tracxn.")
        print("Set TRACXN_MOCK_MODE=False in backend/.env to test the live API.\n")

    if not token and not settings.TRACXN_MOCK_MODE:
        print("\nTRACXN_ACCESS_TOKEN is not set.")
        print("Generate one at https://platform.tracxn.com/a/api/apitoken and add it")
        print("to backend/.env as TRACXN_ACCESS_TOKEN=<token>\n")
        return 1

    async with TracxnClient(access_token=token or None) as client:
        result = await client.ping()
        print("\nPing result:")
        print(json.dumps(result, indent=2))

        if not result.get("connected"):
            print("\nConnection failed. Re-run with --probe-headers to find the")
            print("header name your account expects.\n")
            return 1

        print("\nSample query per dataset (1 record each):")
        for dataset in DATASETS:
            try:
                page = await client.search(dataset, filters={}, size=1)
                sample = page.rows[0] if page.rows else None
                keys = ", ".join(list(sample)[:6]) if sample else "no rows"
                print(f"  {dataset:<14} total={page.total_count:<8} fields: {keys}")
            except TracxnError as exc:
                # A dataset outside your plan fails on its own; keep checking the rest.
                print(f"  {dataset:<14} unavailable: {exc}")

    print("\nConnection OK.\n")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Check the Tracxn API connection")
    parser.add_argument("--token", help="Access token (defaults to TRACXN_ACCESS_TOKEN)")
    parser.add_argument(
        "--probe-headers",
        action="store_true",
        help="Try each known auth header name and report which authenticates",
    )
    args = parser.parse_args()

    token = args.token or settings.TRACXN_ACCESS_TOKEN or ""

    if args.probe_headers:
        if not token:
            print("A token is required to probe headers. Pass --token or set TRACXN_ACCESS_TOKEN.")
            return 1
        asyncio.run(run_probe(settings.TRACXN_BASE_URL, token))
        return 0

    return asyncio.run(run_check(token))


if __name__ == "__main__":
    raise SystemExit(main())
