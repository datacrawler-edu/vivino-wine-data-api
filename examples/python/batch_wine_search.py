"""Run a small, sequential search for each distinct wine term."""

import argparse
import json
from typing import Dict, List, Optional

from client import collect


MAX_TERMS_PER_EXAMPLE = 5
MAX_RESULTS_PER_TERM = 3
EVENT_BUDGET_PER_RUN_USD = "0.003"


def batch_search(
    terms: List[str],
    token: Optional[str] = None,
    api_url: str = "https://api.apify.com",
    page_size: int = 100,
) -> List[Dict[str, object]]:
    unique_terms = []
    seen_terms = set()
    for raw_term in terms:
        if not isinstance(raw_term, str) or not raw_term.strip():
            continue
        term = raw_term.strip()
        key = term.casefold()
        if key not in seen_terms:
            seen_terms.add(key)
            unique_terms.append(term)

    if not unique_terms:
        raise ValueError("Supply at least one non-empty wine search term.")
    if len(unique_terms) > MAX_TERMS_PER_EXAMPLE:
        raise ValueError(
            "This example accepts at most "
            + str(MAX_TERMS_PER_EXAMPLE)
            + " distinct terms per invocation."
        )

    combined_rows: List[Dict[str, object]] = []
    seen_vintages = set()
    for term in unique_terms:
        run_input = {
            "searchTerm": term,
            "wineType": "any",
            "market": "US",
            "maxResults": MAX_RESULTS_PER_TERM,
            "includeDetails": False,
            "reviewsPerWine": 0,
            "vintageIds": [],
        }
        _, run, summary, rows = collect(
            run_input,
            token=token,
            api_url=api_url,
            max_total_charge_usd=EVENT_BUDGET_PER_RUN_USD,
            page_size=page_size,
        )
        print(
            "Search "
            + repr(term)
            + " used run "
            + run.id
            + " with summary "
            + str(summary["status"])
        )
        for row in rows:
            vintage_id = row["vintageId"]
            if vintage_id not in seen_vintages:
                seen_vintages.add(vintage_id)
                combined_rows.append(row)

    return combined_rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("terms", nargs="+", help="One wine name or keyword per run.")
    args = parser.parse_args()
    print(json.dumps(batch_search(args.terms), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
