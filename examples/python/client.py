"""Small helpers for safe, bounded calls to the hosted Vivino Actor."""

from __future__ import annotations

import json
import os
import sys
from datetime import timedelta
from typing import Any, Dict, List, Optional, Tuple
from urllib.request import Request, urlopen

from apify_client import ApifyClient


ACTOR_ID = "datascraperes~vivino-wine-scraper"
DEFAULT_API_URL = "https://api.apify.com"
DEFAULT_EVENT_BUDGET_USD = "0.003"
DATASET_PAGE_SIZE = 100


def get_token(token: Optional[str] = None) -> str:
    value = token or os.environ.get("APIFY_API_TOKEN")
    if not value:
        raise RuntimeError("Set APIFY_API_TOKEN before calling the Actor.")
    return value


def make_client(token: Optional[str] = None, api_url: str = DEFAULT_API_URL) -> ApifyClient:
    return ApifyClient(get_token(token), api_url=api_url, max_retries=1)


def start_run_once(
    run_input: Dict[str, Any],
    token: Optional[str] = None,
    api_url: str = DEFAULT_API_URL,
    max_total_charge_usd: str = DEFAULT_EVENT_BUDGET_USD,
) -> str:
    """Send one paid start request. Never retry a start with an unknown response."""
    api_token = get_token(token)
    request = Request(
        api_url.rstrip("/")
        + "/v2/acts/"
        + ACTOR_ID
        + "/runs?timeout=180&maxTotalChargeUsd="
        + max_total_charge_usd,
        data=json.dumps(run_input).encode("utf-8"),
        headers={
            "Authorization": "Bearer " + api_token,
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urlopen(request, timeout=30) as response:
            payload = json.load(response)
        run_id = payload["data"]["id"]
    except Exception:
        raise RuntimeError(
            "The start response was unavailable. Inspect existing runs in Apify Console "
            "before trying again; this example does not send a second start."
        ) from None
    return run_id


def read_summary(client: ApifyClient, key_value_store_id: str) -> Dict[str, Any]:
    record = client.key_value_store(key_value_store_id).get_record("SUMMARY")
    summary = record.get("value") if record else None
    if not isinstance(summary, dict):
        raise RuntimeError("The run has no readable SUMMARY record; inspect the existing run.")
    if summary.get("status") not in ("succeeded", "partial", "failed"):
        raise RuntimeError("The SUMMARY record has an unknown status; inspect the existing run.")
    return summary


def read_dataset_rows(
    client: ApifyClient, dataset_id: str, page_size: int = DATASET_PAGE_SIZE
) -> List[Dict[str, Any]]:
    """Read every Dataset page, including the final empty page for exact page multiples."""
    if page_size < 1:
        raise ValueError("page_size must be positive.")
    rows: List[Dict[str, Any]] = []
    seen_vintages = set()
    offset = 0
    dataset = client.dataset(dataset_id)

    while True:
        page = dataset.list_items(
            offset=offset,
            limit=page_size,
            clean=False,
            desc=False,
        )
        items = page.items
        for row in items:
            vintage_id = row.get("vintageId")
            if not isinstance(vintage_id, int) or vintage_id in seen_vintages:
                raise RuntimeError("The Dataset contains a missing or duplicate vintageId.")
            seen_vintages.add(vintage_id)
            rows.append(row)
        offset += len(items)
        if len(items) < page_size:
            break

    return rows


def _check_summary_rows(
    client: ApifyClient, run: Any, page_size: int = DATASET_PAGE_SIZE
) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    summary = read_summary(client, run.default_key_value_store_id)
    if summary.get("status") == "failed":
        raise RuntimeError(
            "The Actor summary reports failure ("
            + str(summary.get("reason"))
            + "); inspect the existing run."
        )

    rows = read_dataset_rows(client, run.default_dataset_id, page_size=page_size)
    if summary.get("rows") != len(rows):
        raise RuntimeError(
            "Dataset row count differs from SUMMARY; inspect the existing run before exporting."
        )

    if summary.get("status") == "partial":
        print(
            "Partial collection: reason="
            + str(summary.get("reason"))
            + ", missingVintageIds="
            + json.dumps(summary.get("missingVintageIds", [])),
            file=sys.stderr,
        )
    return summary, rows


def collect(
    run_input: Dict[str, Any],
    token: Optional[str] = None,
    api_url: str = DEFAULT_API_URL,
    max_total_charge_usd: str = DEFAULT_EVENT_BUDGET_USD,
    page_size: int = DATASET_PAGE_SIZE,
) -> Tuple[ApifyClient, Any, Dict[str, Any], List[Dict[str, Any]]]:
    api_token = get_token(token)
    run_id = start_run_once(
        run_input,
        token=api_token,
        api_url=api_url,
        max_total_charge_usd=max_total_charge_usd,
    )
    print("Run ID: " + run_id, file=sys.stderr)

    client = make_client(api_token, api_url=api_url)
    run = client.run(run_id).wait_for_finish(wait_duration=timedelta(seconds=240))
    if run is None or run.status != "SUCCEEDED":
        raise RuntimeError(
            "Inspect existing run "
            + run_id
            + "; it did not finish successfully. Do not start another run automatically."
        )

    summary, rows = _check_summary_rows(client, run, page_size=page_size)
    return client, run, summary, rows


def get_completed_run(
    run_id: str,
    token: Optional[str] = None,
    api_url: str = DEFAULT_API_URL,
) -> Tuple[ApifyClient, Any]:
    client = make_client(token, api_url=api_url)
    run = client.run(run_id).get()
    if run is None:
        raise RuntimeError("Run ID was not found or is not accessible.")
    if run.status != "SUCCEEDED":
        raise RuntimeError(
            "The existing run is not SUCCEEDED; inspect it before exporting its Dataset."
        )
    return client, run


def checked_rows_for_existing_run(
    run_id: str,
    token: Optional[str] = None,
    api_url: str = DEFAULT_API_URL,
    page_size: int = DATASET_PAGE_SIZE,
) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    client, run = get_completed_run(run_id, token=token, api_url=api_url)
    return _check_summary_rows(client, run, page_size=page_size)
