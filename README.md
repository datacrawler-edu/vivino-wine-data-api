# Vivino Wine Data API examples

Use the hosted Apify Actor to search Vivino wines and vintages, then work with structured Dataset rows from Python, JavaScript, or cURL. This repository is an integration guide; it does not contain the Actor runtime source or connect directly to Vivino.

[Open Vivino Wine Scraper on Apify](https://apify.com/datascraperes/vivino-wine-scraper?fpr=edudata)

## What this repository helps you do

- Search one wine name or keyword and collect its matching vintages.
- Browse by wine type and compare available offers in different shopping markets.
- Look up known Vivino vintage IDs and add optional details or public tasting notes.
- Call the hosted Actor from an application and export selected fields to CSV.

## Example result

This short record is fictional and sanitized. The complete illustrative row, which follows the Actor's output schema, is in [sample-output.json](data/sample-output.json).

    {
      "vintageId": 1200001,
      "name": "Example Estate Cabernet Sauvignon 2021",
      "year": "2021",
      "market": "US",
      "rating": 4.2,
      "ratingSource": "vintage",
      "price": {
        "amount": 32.5,
        "currency": "USD"
      }
    }

The Actor returns one Dataset item per vintage. Price, details, and tasting notes can be unavailable for an individual item.

## Run without code

You can use the hosted Actor from Apify's web interface:

1. Open [Vivino Wine Scraper](https://apify.com/datascraperes/vivino-wine-scraper?fpr=edudata).
2. In **Input**, enter a wine name such as **Barolo**, or leave it blank to browse by wine type.
3. Choose a shopping market and a maximum number of vintages.
4. Select **Start**, then inspect the **Dataset** when the run finishes.
5. Export the Dataset as JSON or CSV.

For a direct vintage lookup, clear the search term, keep **Any type**, and add numeric IDs in **Lookup by vintage ID**. See the [no-code guide](docs/no-code-guide.md) for optional settings and the run summary.

## Try it with Apify's free plan

Apify's Free plan currently includes **$5 of monthly prepaid usage** for Store Actors and platform usage, and no credit card is required to start. This can cover a small test while credit is available; it is not unlimited free usage. Unused credit expires at the end of the billing cycle.

Check the [current Apify pricing](https://apify.com/pricing?fpr=edudata) before a larger run. The amount of free credit is separate from the Actor's event price.

## Quick start for developers

### Python

Install the pinned client:

    python -m pip install -r examples/python/requirements.txt

Set an API token in your shell:

    export APIFY_API_TOKEN="your-token"

On Windows PowerShell:

    $env:APIFY_API_TOKEN = "your-token"

Run the small search example:

    python examples/python/search_wine.py

It starts one run with a $0.003 event budget for the three-row sample, waits for that run, checks the SUMMARY record against the Dataset, and prints the rows. A partial summary is reported with its reason; the example does not start a replacement run.

### Batch and CSV workflows

The [batch example](examples/python/batch_wine_search.py) makes one bounded run per distinct search term. This sample accepts up to five distinct terms and caps each run at three result events; those are example safeguards, not Actor input limits. The [CSV export example](examples/python/export_vintages.py) reads a run you already have and does not start another Actor run.

## Input example

    {
      "searchTerm": "Barolo",
      "wineType": "any",
      "market": "US",
      "maxResults": 3,
      "includeDetails": true,
      "reviewsPerWine": 2,
      "vintageIds": []
    }

All input fields are optional. See the [input reference](docs/input-reference.md) for defaults, allowed values, lookup rules, and field limits.

## Request examples

- **cURL:** [synchronous request](examples/curl-request.md). This small request returns Dataset items directly; use the Python or JavaScript example when you need the run ID and summary.
- **Python:** [one wine search](examples/python/search_wine.py), [sequential batch](examples/python/batch_wine_search.py), and [existing-run CSV export](examples/python/export_vintages.py).
- **JavaScript:** [native fetch request](examples/javascript/request.mjs).

All examples call the hosted Apify Actor. They do not expose proxy settings or require local Actor source.

## Output fields

| Field | Meaning |
| --- | --- |
| vintageId | Identifier for one specific wine vintage; use it for direct lookup. |
| wineId | Wine-level identifier that can group multiple vintages. |
| market | Shopping market selected for the run. |
| countryCode | Country of origin when supplied; it is separate from market. |
| rating, ratingsCount | Vintage rating and number of ratings when available. |
| ratingSource | Whether the displayed rating came from search, vintage details, or a wine-level value. |
| price | Market offer with amount, currency, merchant ID, and URL when available. |
| details, reviews | Optional vintage details and public tasting notes, when returned. |

See the [output reference](docs/output-reference.md) for nested fields and the run-level SUMMARY record.

## Common use cases

The [use-case guide](docs/use-cases.md) shows three supported workflows:

- Compare offers across selected shopping markets in separate runs.
- Build a vintage catalogue from a wine name or wine type.
- Enrich known vintage IDs with details and tasting notes.

## Search Vivino wines by keyword with Python

Load a short wine list into the [batch example](examples/python/batch_wine_search.py) to run one capped Actor run per distinct term. The Actor accepts one searchTerm per run, so the example sequences those calls instead of sending an unsupported batch field.

## Export Vivino vintage data to CSV

Pass an existing Apify run ID to the [export example](examples/python/export_vintages.py). It reads pages from that run's Dataset, verifies the item count against SUMMARY, and writes a compact CSV without launching a new paid run.

## FAQ

See the [FAQ](docs/faq.md) for lookup mode, market prices, tasting-note behavior, partial runs, and event billing.

## Limits and pricing

The Actor uses PAY_PER_EVENT. One vintage-result event is charged for each confirmed vintage saved to the Dataset; requested details and tasting notes are included in that row's event.

The live Actor pricing configuration verified on **2026-11-18** is tiered per result: **$0.001** at FREE, **$0.0009** at BRONZE, **$0.0008** at SILVER, and **$0.00075** at GOLD, PLATINUM, and DIAMOND. Check the Actor's [Pricing tab](https://apify.com/datascraperes/vivino-wine-scraper?fpr=edudata) for current rates.

Searches accept up to 500 unique vintages per run. Direct lookup accepts up to 50 numeric vintage IDs. If a run summary says partial, use its row count, reason, and missing vintage IDs to understand what was saved before using the Dataset as complete.

## Hosted version

Use the hosted [Vivino Wine Scraper](https://apify.com/datascraperes/vivino-wine-scraper?fpr=edudata) for web runs, API calls, and Dataset storage. Its input form and current Pricing tab are the source of truth for available settings and rates.

## Responsible use

Use returned information in accordance with applicable terms, privacy requirements, and law. Check your rights before redistributing tasting notes or images.

## Support

For a problem with these examples, [open a GitHub issue](https://github.com/datacrawler-edu/vivino-wine-data-api/issues) with the command, sanitized input, and error message. For an Actor run issue, include the run ID but never include your API token.

## License

The integration examples and documentation are released under the MIT License.
