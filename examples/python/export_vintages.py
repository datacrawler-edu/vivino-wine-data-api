"""Export selected columns from an existing run; this script does not start a run."""

import argparse
import csv
import os
from pathlib import Path
from typing import Any, Dict, List

from client import checked_rows_for_existing_run


CSV_FIELDS = [
    "vintageId",
    "name",
    "year",
    "winery",
    "region",
    "market",
    "rating",
    "ratingsCount",
    "wineRating",
    "priceAmount",
    "priceCurrency",
]


def entity_name(value: Any) -> str:
    return value.get("name") or "" if isinstance(value, dict) else ""


def csv_row(item: Dict[str, Any]) -> Dict[str, Any]:
    price = item.get("price") or {}
    return {
        "vintageId": item.get("vintageId"),
        "name": item.get("name"),
        "year": item.get("year"),
        "winery": entity_name(item.get("winery")),
        "region": entity_name(item.get("region")),
        "market": item.get("market"),
        "rating": item.get("rating"),
        "ratingsCount": item.get("ratingsCount"),
        "wineRating": item.get("wineRating"),
        "priceAmount": price.get("amount"),
        "priceCurrency": price.get("currency"),
    }


def export_run(
    run_id: str,
    destination: Path,
    token: str,
    api_url: str = "https://api.apify.com",
    page_size: int = 100,
) -> int:
    summary, items = checked_rows_for_existing_run(
        run_id,
        token=token,
        api_url=api_url,
        page_size=page_size,
    )
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", encoding="utf-8", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(csv_row(item) for item in items)
    print("SUMMARY status: " + str(summary["status"]))
    return len(items)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_id", help="Existing Apify run ID; this command does not start a run.")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/exported-vintages.csv"),
        help="CSV destination (default: data/exported-vintages.csv).",
    )
    args = parser.parse_args()
    token = os.environ.get("APIFY_API_TOKEN")
    if not token:
        raise SystemExit("Set APIFY_API_TOKEN to read an existing run.")
    count = export_run(args.run_id, args.output, token)
    print("Exported " + str(count) + " rows to " + str(args.output))


if __name__ == "__main__":
    main()
