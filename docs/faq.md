# FAQ

## Can I search without entering a wine name?

Yes. Leave searchTerm blank and select a wine type. With no keyword and wineType: any, the Actor browses red wines.

## How do I look up a specific vintage?

Use its numeric Vivino vintageId in vintageIds. Clear searchTerm and set wineType to any. A wine ID can represent multiple vintages, so it is not interchangeable with a vintage ID.

## Can one run compare several shopping markets?

A run has one market. Start separate runs for the markets you want to compare, then compare market, price amount, and price currency fields. Offers can change over time.

## Why can a row have no price or details?

Vivino may not supply an offer or an optional detail for every vintage and market. Missing values are null; an unavailable offer is not a zero price.

## Why do tasting notes sometimes describe another year?

Notes are selected at wine level. When Vivino provides a vintageId for a note, use it to see which vintage it describes.

## What does a partial result mean?

Check the SUMMARY record. It reports status, reason, rows, and any missingVintageIds. A partial run can keep confirmed rows in the Dataset, but those rows do not represent a complete collection.

## What is billed?

The Actor uses pay-per-event pricing. One vintage-result event is billed when a confirmed vintage is saved to the Dataset. Requested details and tasting notes are part of that row's event. Check the live Pricing tab for current tier rates.

## Does the CSV export example start another run?

No. examples/python/export_vintages.py takes an existing run ID, reads its summary and Dataset, then writes a compact CSV. It does not start an Actor run.
