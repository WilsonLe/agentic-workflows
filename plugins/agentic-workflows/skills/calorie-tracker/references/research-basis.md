# Research and provider basis

Last reviewed: 2026-08-04. Recheck these primary sources before relying on drift-prone access,
quota, version, scope, or transaction claims.

- [USDA FoodData Central API guide](https://fdc.nal.usda.gov/api-guide/) — API key responsibility,
  endpoints, default limit and 429 behavior, rate-limit headers, DEMO_KEY limitations, CC0/public-
  domain status, and requested attribution.
- [USDA FoodData Central data documentation](https://fdc.nal.usda.gov/data-documentation/) — data
  types and nutrient-record interpretation.
- [Open Food Facts API introduction](https://openfoodfacts.github.io/openfoodfacts-server/api/) —
  current v3 guidance, licenses, accuracy warning, custom User-Agent, read authentication, rate
  limits, and prohibition on abusive search/crawling.
- [Open Food Facts v3 product read](https://openfoodfacts.github.io/documentation/docs/Product-Opener/v3/products/get-api-v3-product-code/)
  — exact barcode product route and identifying header.
- [Google Sheets batchUpdate](https://developers.google.com/workspace/sheets/api/reference/rest/v4/spreadsheets/batchUpdate)
  — all requests are validated before application and valid updates apply together atomically,
  while collaborator changes can affect the resulting spreadsheet.
- [Google Sheets AppendCellsRequest](https://developers.google.com/workspace/sheets/api/reference/rest/v4/spreadsheets/request#appendcellsrequest)
  — typed rows, target numeric sheet ID, and field mask.
- [Google Drive uploads](https://developers.google.com/workspace/drive/api/guides/manage-uploads)
  — file creation/upload behavior.
- [Google Drive API scopes](https://developers.google.com/workspace/drive/api/guides/api-specific-auth)
  — use the narrowest suitable scope and prefer per-file `drive.file` access where applicable.

These sources establish data and API mechanics, not the accuracy of calories inferred from one
photo. The workflow's central accuracy safeguard is therefore evidence separation, user-provided
weight/label precedence, explicit portion ranges, provider lineage, match confidence, and refusal
of unsupported precision.
