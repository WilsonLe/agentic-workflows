# Calorie Tracker onboarding

Onboard only the part needed by the user's request. Analysis can work without Google storage or a
USDA key when visible/user label facts, exact Open Food Facts data, or an explicit manual estimate
are sufficient.

## Nutrition prerequisite

For USDA lookup, ask the user to obtain a free data.gov API key from the official FoodData Central
API guide and save it in a local owner-readable file. Ask for the absolute path, never the key.
Install it with `credential-install`, then use `credential-status`, which never returns the secret.
Rotation validates a complete candidate before atomic replacement; revocation requires
`credential-revoke --confirm`.

## Google storage prerequisite

For tracking, confirm the Google Drive connector is installed and connected. The plugin stores no
OAuth material or account email. Let the user select an existing Sheet and Drive folder by exact
URL/ID, or create them only after an explicit creation request. Never guess between same-named
files.

Use connector metadata reads to resolve:

- exact spreadsheet ID;
- exact meal and item tab names plus numeric sheet IDs;
- exact Drive folder ID;
- current access and expected MIME/type; and
- exact v1 headers.

If an empty target is selected, initialize the `Meals` and `Meal Items` tabs/headers only after the
user authorizes it. Do not remap an incompatible existing table.

Create a candidate JSON with the fields defined in [Google storage](google-storage.md). Show the
destination and schema change. Only after remote verification and an explicit “use this from now
on” request run:

```bash
python scripts/calorie_tracker.py contract-set --input /absolute/candidate.json --confirm
```

The helper writes one active owner-protected contract. Failed validation leaves the old contract
unchanged. `contract-show` is local/read-only. `contract-clear --confirm` removes only the local
pointer and never changes Google data.

## Readiness readback

Return one of:

- `Ready for analysis`;
- `Ready for tracking` with exact Sheet tabs and Drive folder;
- `Needs USDA key`;
- `Needs Google connection or target selection`; or
- `Blocked` with the exact inaccessible ID/schema mismatch.

Give one copy-ready prompt such as: “Track this authorized meal photo in my configured calorie log;
show me the food and portion assumptions before writing.”
