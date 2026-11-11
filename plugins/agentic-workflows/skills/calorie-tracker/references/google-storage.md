# Google Drive and Sheets storage

Google operations are host connector actions. The helper builds and journals payloads but never
authenticates to Google, uploads an image, changes sharing, or submits a Sheet batch.

## Active local contract

The protected contract is stored outside the repository:

- POSIX: `$XDG_CONFIG_HOME/agentic-workflows/calorie-tracker/storage-contract.json`, falling back to
  `~/.config/agentic-workflows/calorie-tracker/storage-contract.json`;
- Windows: `%LOCALAPPDATA%\\Agentic Workflows\\calorie-tracker\\storage-contract.json`.

Candidate fields are:

```json
{
  "google_provider": "google-drive-connector",
  "spreadsheet_id": "SYNTHETIC_SHEET_ID",
  "meals_tab": "Meals",
  "meals_sheet_id": 101,
  "items_tab": "Meal Items",
  "items_sheet_id": 102,
  "drive_folder_id": "SYNTHETIC_FOLDER_ID",
  "timezone": "Australia/Brisbane",
  "column_schema_version": 1,
  "write_mode": "append-only",
  "image_link_policy": "private-drive-url",
  "verified_at": "2026-01-01T00:00:00Z"
}
```

The stored form adds schema/revision and created/updated timestamps. It never stores OAuth tokens,
API keys, account emails, image bytes, meal history, or provider responses.

## V1 tables

`Meals` contains one row per image:

`schema_version`, `entry_id`, `observed_at`, `timezone`, `meal_label`, `image_drive_url`,
`image_drive_file_id`, `image_sha256`, `serving_g_estimate`, `calories_kcal`,
`calories_low_kcal`, `calories_high_kcal`, `protein_g`, `carbohydrate_g`, `fat_g`, `fiber_g`,
`total_sugar_g`, `sodium_mg`, `confidence`, `assumptions`, `source_summary`, `recorded_at`.

`Meal Items` contains one row per identified component:

`schema_version`, `entry_id`, `item_index`, `description`, `amount_g_estimate`, `amount_low_g`,
`amount_high_g`, `provider`, `provider_food_id`, `provider_url`, `retrieved_at`, `calories_kcal`,
`protein_g`, `carbohydrate_g`, `fat_g`, `fiber_g`, `total_sugar_g`, `sodium_mg`,
`match_confidence`, `match_reason`.

Numeric cells must use `numberValue`; untrusted text must use `stringValue`, including values that
start with `=`, `+`, `-`, or `@`. Missing values are blank CellData, not zero. Never use
`USER_ENTERED`, a formula, public sharing, or `IMAGE()`.

## Exact tracking transaction

1. Read the active contract and verify the exact spreadsheet metadata, numeric sheet IDs, headers,
   and exact Drive folder metadata/access with the current connected account.
2. Build the meal record and create its local journal in `planned` state.
3. Search bounded existing meal rows for `entry_id`; warn when the image digest already exists.
4. Upload the exact source image once with the connector's file upload action and
   `parent_folder_id=drive_folder_id`. Do not share it or alter inherited permissions.
5. Record the returned file ID/private URL as `image_uploaded`; bind it to the local record.
6. Build one payload containing two `appendCells` requests and submit it through the connector's
   spreadsheet `batchUpdate`. Google validates the requests before applying them together.
7. Mark `sheet_written_unverified`, then search/read both tabs by `entry_id` and inspect Drive file
   metadata/parent. Verify one meal row, the expected item count, typed values, totals, file ID, and
   folder.
8. Only then mark `verified` and return the entry, row references, totals, and private Drive URL.

Google batch atomicity covers the two Sheet appends, not the preceding Drive upload. Collaborators
may modify the spreadsheet around the transaction, so readback by stable ID—not an assumed row
number—is authoritative.

## Recovery

- `planned`: no confirmed remote mutation; inspect remote state before action.
- `image_uploaded`: reuse the exact file ID and proceed to the Sheet batch; do not upload again.
- `sheet_written_unverified`: search/read back; do not append again.
- `failed_recoverable`: inspect stored identities and remote state, then resume the next missing
  step. Never discard the journal merely because a tool response was lost.
- `verified`: no retry is allowed.

Multiple entry matches, changed headers/sheet IDs, inaccessible files, a different connected
account, or unknown remote outcome block automated recovery. Deleting an orphan or correcting a
row requires a separate exact-target request and before/after verification.
