# cURL request

This small request uses the synchronous API endpoint and returns the Actor's default Dataset items as JSON. It uses the sample input and caps the run at $0.003 in Actor event charges.

Set APIFY_API_TOKEN in your shell, then run from the repository root:

    curl --fail --silent --show-error       --request POST       "https://api.apify.com/v2/acts/datascraperes~vivino-wine-scraper/run-sync-get-dataset-items?timeout=300&maxTotalChargeUsd=0.003"       --header "Authorization: Bearer $APIFY_API_TOKEN"       --header "Content-Type: application/json"       --data-binary @data/sample-input.json

The endpoint waits up to 300 seconds and returns Dataset items when the run finishes. If the connection times out, inspect the run in Apify Console before starting another one. For a run ID, an explicit SUMMARY check, and page-by-page reading, use the Python or JavaScript examples.
