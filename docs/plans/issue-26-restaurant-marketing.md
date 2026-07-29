# Issue #26 — Restaurant Marketing Management

Status: approved for implementation
Approved by: user in the originating Codex task
Approval date: 2026-07-29
Issue: https://github.com/anhminhsoft/amsoft-agentic-workflow-codex-plugin/issues/26
Published plan:
https://github.com/anhminhsoft/amsoft-agentic-workflow-codex-plugin/issues/26#issuecomment-5111362151

## Execution identity

- Repository: `anhminhsoft/amsoft-agentic-workflow-codex-plugin`
- Base branch: `main`
- Approved base revision: `9f5331a1961bbd5a046a870f8d5f79d2e1b9825c`
- Feature branch: `feat/restaurant-marketing-skills`
- Worktree:
  `/Volumes/Dev/projects/amsoft-agentic-workflow-codex-plugin-restaurant-marketing`
- Required workflow: Standard Development Workflow
- Additional gate: AMSoft Plugin Authoring Policy

This file is the durable execution checkpoint for compaction or fresh-session resume. The GitHub
issue is the specification source of truth. The published issue comment is the exhaustive
implementation and verification plan.

## Objective

Add a standalone `restaurant-marketing` Codex plugin and a collision-safe
`amsoft-restaurant-marketing-management` capability in the central AMSoft Agentic Workflows
plugin. Help restaurant owners manage truthful, margin-aware, approval-gated, and measurable
marketing for:

1. a new permanent dish;
2. a limited-time offer or bundle;
3. a seasonal or limited-availability dish;
4. an event, catering offer, or occasion;
5. slow-day or slow-daypart demand;
6. always-on local discovery;
7. reputation and guest recovery;
8. retention, loyalty, or win-back;
9. an opening, relaunch, or major menu change.

The capability is a campaign operating system, not only a caption generator.

## Approved change envelope

### Direct work

- `plugins/restaurant-marketing/`
  - manifest, README, license;
  - `restaurant-marketing-management` skill and agent metadata;
  - onboarding, operating-system, archetype, economics, channel/creative, compliance/approval,
    measurement/learning, and research references;
  - restaurant profile, campaign plan, and campaign result templates;
  - strict v1 JSON schema;
  - dependency-free helper for validation, economics, UTM generation, and compact summaries;
  - new-dish, offer, and seasonal examples.
- `plugins/amsoft-agentic-workflows/`
  - collision-safe central skill entrypoint;
  - portable copies of the standalone references, templates, schema, examples, and helper;
  - central router, capability map, onboarding, registry, README-facing metadata, and cachebuster.
- `.agents/plugins/marketplace.json`
  - exactly one `restaurant-marketing` entry.
- root `README.md`
  - installation, update, verification, capability, and layout documentation.
- `scripts/validate_plugin_packages.py`
  - standalone/central shape, registry, router, link, schema, example, executable-helper, and
    portable-parity checks.
- `tests/test_restaurant_marketing.py`
  - positive, boundary, and failure-path coverage.

### Enabling work

- Fresh version identifiers for `restaurant-marketing` and `amsoft-agentic-workflows`.
- Exact package reinstall and authoritative installed-cache parity verification.
- A concise draft-PR evidence record linked with `Closes #26`.

### Prohibited or follow-up work

- No social scheduler, CRM, POS, loyalty, reservation, email, review, or advertising platform.
- No live customer data, restaurant records, credentials, analytics exports, or generated
  campaign state in Git.
- No autonomous publishing, customer messaging, discount activation, ad spend, influencer
  contracting, review solicitation, or public review response.
- No fake reviews, review gating, sentiment-conditioned incentives, fabricated testimonials,
  unsupported claims, or invented restaurant facts.
- No universal posting-frequency, discount-depth, budget, duration, or ROI claims.
- No production or staging deployment.

Stop and return to planning if implementation requires a new subsystem, runtime dependency,
persistence model, credential, external mutation, deployment mechanism, materially larger path
envelope, or weaker verification substitute.

## Design contract

The skill must:

1. build or refresh a restaurant source-of-truth profile;
2. classify the smallest applicable campaign archetype;
3. gate content on price, dates, terms, inventory, capacity, service, claim, consent, allergen,
   destination, and staff readiness;
4. calculate contribution, discount impact, break-even demand, scenarios, downside cap, and
   guardrails from explicit inputs;
5. create audience, message, proof, CTA, phased calendar, channel roles, owners, approvals, and
   expiry actions;
6. route food-photo work to Food Image Editing and owned WordPress work to the existing WordPress
   skills;
7. distinguish drafting from separately approved publishing, sending, activation, spend,
   influencer, and sensitive-review actions;
8. define a stable campaign ID, consistent UTM names, POS/booking/manual attribution, baseline,
   primary outcome, diagnostics, guardrails, and review cadence;
9. verify every later authorized external change through real-surface readback;
10. close with expiry verification and a postmortem separating observation, calculation,
    inference, attribution uncertainty, and unknowns.

Platform and compliance guidance is drift-sensitive. Australia is the worked example, but live use
must resolve the actual jurisdiction and refresh current primary guidance.

## Implementation sequence

- [x] Research complete; four full PDFs downloaded, hashed, read, noted, and bundle-validated.
- [x] Isolated worktree created from the approved base.
- [x] Spec-ready Issue #26 published.
- [x] Exhaustive implementation and verification plan published.
- [x] User approval received.
- [x] Approved plan persisted in this file.
- [x] Create standalone and central package skeletons.
- [x] Define strict v1 schema and three valid campaign examples.
- [x] Implement the dependency-free helper.
- [x] Add focused helper and contract tests.
- [x] Write the owner-facing skill and progressive references.
- [x] Add templates, README, manifest, agent metadata, and license.
- [x] Wire central routing, registry, marketplace, versions, and root documentation.
- [x] Extend package validation and portable-file parity checks.
- [x] Run the complete validation ladder: 13 focused tests, 113 full-suite tests, package validation,
  Ruff, JSON Schema positive and strict-negative checks, portable parity, and diff hygiene pass.
- [x] Freeze and commit the clean candidate.
- [x] Reinstall and verify both plugin packages at `0.1.0+codex.20260729161000`; standalone uses
  the durable personal source and central verification uses the isolated Issue #26 local
  marketplace so concurrent shared-source work is preserved.
- [x] Push and open draft PR #29 linked with `Closes #26`.
- [x] Stop for user review; do not merge without separate approval.

## Validation ladder

Run cheap checks before expensive checks and preserve the first failure before changing code.

1. Parse changed JSON and YAML; compile changed Python.
2. Run `python3 -m unittest tests.test_restaurant_marketing -v`.
3. Run `python3 scripts/validate_plugin_packages.py`.
4. Run:

   ```text
   uv run --no-project \
     --with cryptography==49.0.0 \
     --with PyYAML==6.0.3 \
     python -m unittest discover -s tests -v
   ```

5. Run Ruff `0.1.1` over every repository Python surface, including both new helper copies and the
   new tests.
6. Verify relative links, portable-file hashes, fixture safety, placeholders, and credential/PII
   absence.
7. Independently recalculate one offer fixture.
8. Apply fresh cachebuster versions, reinstall both plugins, and verify:
   - normalized name;
   - declared and installed version;
   - enabled status;
   - resolved source path;
   - cache existence;
   - required file presence;
   - changed-file source/cache byte parity.
9. Exercise fresh-session routing for:
   - “Help me market a new dish.”
   - “Plan an offer without destroying margin.”
   - “Create a seasonal dish campaign.”

Browser, visual, device, migration, load, staging, and production checks are not applicable because
this repository change has no rendered application, database, service, or deployed environment.
Fresh-session skill discovery is the user-surface check.

## Handoff and completion gates

The draft PR may be opened only after all required local checks pass and the committed candidate is
clean. Its description must state scope, non-goals, research boundaries, design decisions, exact
test results, reinstall/parity evidence, rollback, limitations, and confirmation that no live
restaurant or customer mutation occurred.

After opening the tested draft PR, stop for user review. A later explicit approval authorizes the
default squash merge, canonical fast-forward synchronization, and exact feature worktree/branch
cleanup. It does not authorize a live restaurant campaign or production deployment.
