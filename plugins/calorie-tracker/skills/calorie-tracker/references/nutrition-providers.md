# Nutrition providers

Recheck current official documentation before live use. “Free” describes the observed access tier,
not a permanent guarantee. Do not call a provider when its access, license, quota, attribution, or
terms cannot be established.

## Provider order

1. Visible nutrition label or user-supplied verified facts.
2. Exact barcode read from Open Food Facts.
3. USDA FoodData Central search and selected food details.
4. Explicit manual estimate with no invented provider ID.

## Open Food Facts

Use only an exact product read for a visible or user-supplied 8–14 digit barcode. The current v3.6
read endpoint is keyless but requires an identifying custom User-Agent. Do not use search-as-you-
type, upload the meal image, edit a product, or authenticate a write. Current documented limits are
15 product reads/minute/IP and 10 searches/minute/IP; a global overload may return 503. Product data
is community-contributed and may be incomplete, so preserve the barcode, returned fields, match
reason, retrieval time, and missing values.

The helper requests only:

`code, product_name, brands, quantity, serving_size, nutriments`.

It normalizes `*_100g` values and converts sodium grams to milligrams. An absent required macro or
non-numeric value blocks use of that record.

## USDA FoodData Central

USDA access requires a free user-obtained data.gov API key. Never use the documentation `DEMO_KEY`
for routine operation and never place a key in chat, argv, logs, screenshots, fixtures, Git, or a
displayed URL. Install or rotate it atomically from an owner-readable local file with
`credential-install`; a failed replacement must leave the old credential intact.

Use bounded `/foods/search` calls with a three-candidate page, then `/food/{fdcId}` for the exact
selected record. Prefer preparation/form and data type appropriate to the meal. Preserve FDC ID,
description, data type, units, retrieval time, and attribution. FDC nutrients are normalized from
the record's per-100-g basis; energy kJ is converted to kcal and sodium grams to milligrams where
needed.

The current documented default is 1,000 requests/hour/IP, with 429 and temporary blocking after
the limit. Read rate-limit headers when available. FDC data is public-domain/CC0, but attribute
FoodData Central as the source.

## Request and cache contract

- Maximum eight food items, three displayed candidates per unresolved item, and 20 HTTP requests
  for one meal across search, details, and a single permitted retry.
- Deduplicate equivalent requests in the run and cache provider records for 30 days with retrieval
  and expiry times. `--force-refresh` bypasses the cache but not the request budget.
- Use HTTPS and the fixed provider-host allowlist. Reject unapproved redirects, oversized or
  non-JSON responses, malformed objects, and unsupported units.
- A 429 is never immediately retried; retain `Retry-After` when supplied. One retry is allowed for
  transport or 5xx failure, and that retry consumes the request budget.
- Never crawl, background-poll, bulk download, perform provider writes, accept arbitrary URLs or
  headers, or send image bytes to a nutrition provider.

## Minimal provider-plan example

```json
{
  "schema_version": 1,
  "requests": [
    {"provider": "open_food_facts", "operation": "product", "barcode": "0000000000000"},
    {"provider": "usda", "operation": "search", "query": "cooked brown rice"}
  ]
}
```

The barcode above is reserved synthetic test data, not a real product assertion.
