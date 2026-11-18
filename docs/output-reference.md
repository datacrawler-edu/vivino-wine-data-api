# Output reference

Each Dataset item describes one wine vintage. The top-level fields below are present in each row; values that Vivino does not supply can be null.

| Field | Type | Description |
| --- | --- | --- |
| vintageId | integer | Vivino identifier for this vintage. |
| wineId | integer | Wine-level identifier, which can group multiple vintage IDs. |
| name | string | Display name for the vintage. |
| year, wineName, wineTypeId | string/integer or null | Vintage year, wine name, and wine type when available. |
| winery, region | object or null | Each object has id and name, either of which may be null. |
| countryCode | string or null | Wine's country of origin. This is different from the selected shopping market. |
| market | string | Shopping market: US, ES, DE, IT, FR, or GB. |
| rating, ratingsCount | number/integer or null | Vintage rating and count when available. |
| ratingSource | string | search, vintage, or wine; indicates where the displayed rating came from. |
| wineRating, wineRatingsCount | number/integer or null | Wine-level aggregate rating and count when supplied. |
| imageUrl | string or null | Image URL when available. |
| price | object or null | amount, currency, merchantId, and url for an offer in the selected market. |
| details | object or null | Optional description, alcohol, grape and food entities, and rating distribution. |
| reviews | array or null | Requested public tasting notes. A note may identify a different vintage through its vintageId. |

See [sample-output.json](../data/sample-output.json) for a full fictional row that matches the current output schema.

## Run summary

The default key-value store has a SUMMARY record with status, reason, rows, sourceMatches, and missingVintageIds. Status is succeeded, partial, or failed. A partial run can retain confirmed Dataset rows; check the summary before treating those rows as a complete search.
