# Calorie Tracker

Calorie Tracker helps Codex estimate calories, protein, carbohydrate, and fat from an authorized
meal image without pretending a photograph reveals exact weight or hidden ingredients. It prefers
visible labels and user facts, then bounded read-only Open Food Facts or USDA FoodData Central
records, and labels any remaining manual estimate.

An analysis request is read-only. A direct tracking request can upload the source image once to an
exact configured private Google Drive folder and atomically append typed meal and item rows to an
exact configured Google Sheet. The destination is remembered in one owner-protected local storage
contract and is replaced only after the user explicitly selects and verifies a complete new target.

The dependency-free helper provides secret-safe USDA-key onboarding, bounded provider reads,
normalization, local record building, typed Sheets `appendCells` payloads, and a recovery journal.
It does not analyze pixels or perform Google mutations itself.

```bash
python scripts/calorie_tracker.py credential-status
python scripts/calorie_tracker.py contract-show
python scripts/calorie_tracker.py image-digest --image /absolute/path/to/meal.jpg
python scripts/calorie_tracker.py record-build --input analysis.json --output meal-record.json
```

Read [the primary skill](skills/calorie-tracker/SKILL.md) before use. Nutrition values are wellness
estimates, not medical advice; high-stakes dietary decisions require weighed ingredients, verified
labels, and an appropriate qualified professional.
