# Run Vivino Wine Scraper without code

Use the hosted Actor in Apify Console when you want to search wine data without installing a client library.

## Search by wine name or keyword

1. Open [Vivino Wine Scraper](https://apify.com/datascraperes/vivino-wine-scraper?fpr=edudata).
2. In the **Input** tab, enter a wine name or keyword, such as **Barolo**.
3. Select a shopping market and set **Maximum results** to a small number for a first run.
4. Leave **Vintage IDs** empty for a regular search. Enable **Include vintage details** or request a small number of **Tasting notes per wine** only when useful.
5. Click **Start** and open the **Dataset** when the run finishes.

The default output is one row per vintage. The shopping market in market identifies where an offer was checked; countryCode describes the wine's origin.

## Browse by wine type

Clear the wine name and choose **Red**, **White**, **Sparkling**, **Rosé**, **Dessert**, or **Fortified**. If the keyword is blank and **Any type** is selected, the Actor browses red wines.

## Look up known vintages

1. Clear the wine name.
2. Keep **Any type** selected.
3. Open **Lookup by vintage ID (optional)** and add each numeric vintage ID as its own entry.
4. Select **Start** and inspect the returned vintages.

A vintage ID identifies a particular vintage. A wine ID may refer to a wine that has several years.

## Read the result and summary

Open the Dataset for the saved vintage rows. The run's SUMMARY record describes whether collection finished (succeeded), returned confirmed rows but stopped early (partial), or failed. For a partial collection, check the row count, reason, and missing vintage IDs before treating the Dataset as complete.

You can export Dataset rows as JSON or CSV from Apify. See [sample-input.json](../data/sample-input.json) for a small input example.
