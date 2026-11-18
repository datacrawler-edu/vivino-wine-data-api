# Input reference

Every field is optional. The default input searches red wines in the United States and saves up to 20 vintage rows.

| Field | Type | Required | Example | Description |
| --- | --- | :---: | --- | --- |
| searchTerm | string | No | Barolo | Wine name or keyword, up to 120 characters. Leave blank to browse by type or use vintage lookup. |
| wineType | string | No | any | any, red, white, sparkling, rose, dessert, or fortified. With no keyword, any browses red wines. |
| market | string | No | US | Shopping market: US, ES, DE, IT, FR, or GB. Defaults to US. |
| maxResults | integer | No | 3 | Maximum unique vintages to save, from 1 to 500. Defaults to 20. |
| includeDetails | boolean | No | true | Request description, alcohol, grapes, food pairings, and rating distribution when available. Defaults to false. |
| reviewsPerWine | integer | No | 2 | Request 0 to 10 public tasting notes per wine. Defaults to 0. Notes can refer to another vintage of the same wine. |
| vintageIds | integer array | No | [1234567] | Look up up to 50 positive numeric vintage IDs. Clear searchTerm and choose any for direct lookup. Repeated IDs are counted once. |

## Modes and limits

- A search uses one searchTerm, or a blank term with the selected wineType.
- A lookup uses vintageIds; clear searchTerm and select wineType: any.
- A search can save up to 500 unique vintages per run.
- A lookup accepts up to 50 IDs, each a positive integer.
- searchTerm has a maximum length of 120 characters.
- reviewsPerWine must be between 0 and 10.

The Actor does not accept a list of search terms in one input. The batch example starts one run per distinct term.
