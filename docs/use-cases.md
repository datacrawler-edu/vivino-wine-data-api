# Use cases

These examples use the current Actor input contract. Each search is one Actor run; the Actor does not take a list of search terms in a single input.

## Compare offers across shopping markets

Run the same wine search separately for each market, then compare market, price amount, and price currency. An offer is a snapshot for that selected market and can change.

    {"searchTerm":"Barolo","wineType":"any","market":"US","maxResults":3}

Repeat with market ES or another supported market. A row without an available offer has price: null.

## Build a wine vintage catalogue

Search by a name or browse by type and save the returned rows in your own Dataset or database. Use vintageId as the identity for a vintage, and retain wineId when grouping vintages from the same wine.

    {"searchTerm":"Barolo","market":"US","maxResults":20}

For broad searches, use a modest maxResults first and check the run SUMMARY before using the Dataset as complete.

## Enrich known vintage IDs

Send known numeric vintage IDs with no keyword and wineType set to any. Enable details or request public tasting notes when those fields are useful.

    {"searchTerm":"","wineType":"any","market":"US","includeDetails":true,"reviewsPerWine":2,"vintageIds":[1234567,2345678]}

The lookup list accepts up to 50 IDs. The Actor deduplicates repeated IDs; missingVintageIds in SUMMARY identifies IDs it could not confirm.
