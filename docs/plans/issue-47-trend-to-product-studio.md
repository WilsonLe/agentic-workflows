# Issue #47 implementation plan

Issue: <https://github.com/anhminhsoft/amsoft-agentic-workflow-codex-plugin/issues/47>

Base revision: `6a209f2232cfe961232c66a73b0d649ef04bfd93`

Branch: `feat/trend-to-product`

## Objective

Create an independently installable `trend-to-product` Codex plugin and a
collision-safe AMSoft suite integration. The feature must persist demographic
tracking profiles and immutable trend-to-product artifacts inside an explicitly
selected user project; normalize provenance-backed trend evidence; explain
trend and product-fit decisions separately; create production-aware design and
launch packets; and route approved image work through the host image capability
without bundling an image client.

## Scope

- Standalone plugin manifest, marketplace entry, skills, references, schemas,
  fixtures, deterministic Python CLI, tests, README, and license.
- Project, audience revision, source registry, tracking, evidence, trend,
  opportunity, concept/design, content, drop, index, and manifest contracts.
- Read-only source setup and offline CSV/JSON/NDJSON/RSS import/normalization.
- Path containment, atomic immutable runs, digest verification, index rebuild,
  configured-versus-active tracking, sanitized failure records, and prohibited
  data checks.
- Versioned trend scoring, separate product-fit scoring, hard gates, product
  hypothesis reasoning, design approval, image-tool request lineage, visual
  review, and production-readiness states.
- Central AMSoft registry, router, capability map, collision-safe bundled skills,
  cachebuster, reinstall, and installed-state byte-parity verification.

## Non-goals

- Reproducing a person's FYP or profiling an individual.
- Credential/browser harvesting, bypasses, unbounded scraping, or comment
  harvesting.
- Bundled credentialed/licensed source clients.
- Custom image model/client, vectorizer, prepress engine, store client,
  scheduler, autonomous publication, inventory purchase, or ad spend.
- Live source collection, image generation, automation creation, or store
  mutation during fixture verification.

## Architecture and data flow

```text
project contract + audience revision + source registry + tracking profile
  -> bounded adapter/import
  -> normalized evidence with provenance and limitations
  -> deduplicated/corroborated trend candidates
  -> versioned trend score + hard gates
  -> product hypotheses + separate product-fit score
  -> approved design brief and content/drop packets
  -> optional host image-capability request
  -> visual review and production-readiness record
  -> immutable run/derived manifests and rebuildable index
```

The dependency-free CLI owns deterministic records and validation. Network,
credentialed, licensed, scheduler, image, and store capabilities remain host or
cataloged integrations with explicit availability and approval boundaries.

## Implementation sequence

1. Inspect nearby plugin manifests, skills, schemas, CLIs, tests, marketplace
   format, validators, central registry/router/capability map, and install
   helpers.
2. Scaffold `plugins/trend-to-product` and add normalized manifest and
   marketplace metadata.
3. Define versioned JSON Schemas, templates, valid/invalid fixtures, stable IDs,
   enums, timestamps, limitations, and prohibited fields.
4. Implement `scripts/trend_to_product.py`:
   - project initialization and contract validation;
   - audience creation/revision/listing;
   - source add/test/sample/enable/disable/list/status/import;
   - tracking create/bind/list;
   - normalized evidence ingest and scoring;
   - immutable atomic run promotion;
   - list/read/latest/validate/verify/reindex;
   - opportunity/design/content/launch/result commands.
5. Add deterministic tests for paths, symlinks, collisions, interruption
   recovery, revisions, schema failures, source states, normalization,
   deduplication, scoring/hard gates, prohibited data, manifests, index rebuild,
   lineage, design approval, unavailable image capability, production blockers,
   and configured/active tracking.
6. Add concise skills with direct references for onboarding/discovery,
   opportunity reasoning, design generation, content, and drop operations.
7. Add a complete `vn-hcm-18-28` fixture run using offline evidence. Preserve
   requested demographic versus observed coverage and stop at concept/design
   readiness.
8. Register and bundle portable capabilities into the central AMSoft suite with
   collision-safe names; update router, capability map, versions/cachebusters,
   and marketplace state.
9. Run focused tests, complete repository validation, fixture E2E, fresh-context
   forward test where supported, source/central installation, installed-state
   checks, and byte-parity checks.
10. Review the final diff against issue #47, commit, push, and open a draft PR
    with evidence. Stop for review; do not merge or deploy.

## Requirements-to-verification matrix

| Requirement | Evidence |
| --- | --- |
| Independently installable plugin | plugin validator, marketplace validation, installed-state readback |
| Exact project/artifact root and Git policy | CLI integration tests and persisted contract |
| Audience revisions and historic readability | revision/list/read tests |
| Source onboarding without secret leakage | manifest/schema tests, sanitized CLI tests |
| Common evidence schema and source limitations | CSV/RSS fixture normalization tests |
| Duplicate/syndicated signal handling | deterministic clustering/dedup fixtures |
| Region/demographic claim separation | fixture assertions across evidence, trend, and opportunity |
| Immutable atomic runs | collision, failed-write, and overwrite tests |
| Offline list/read/latest/verify/reindex | subprocess integration tests with network disabled by design |
| Manifest tamper detection | digest mutation negative test |
| Separate trend/product-fit reasoning | score fixtures and rationale assertions |
| Unsafe concepts rejected before design | hard-gate fixtures |
| Design tied to exact upstream IDs and approval | lineage and approval-state tests |
| Host image capability only | skill/reference inspection and unavailable-capability result |
| Concept not falsely print-ready | production-readiness tests |
| Configured versus active automation | tracking state-machine tests |
| No external mutation in E2E | offline fixture command trace |
| Central integration and parity | central validators, reinstall readback, file digest comparison |

## Risks and mitigations

- **Overstating audience prevalence:** retain observed coverage separately from
  requested demographics and require limitations downstream.
- **Upstream drift:** version adapter mappings and use stable health/error states.
- **Secrets/personal data:** store references only, reject prohibited keys, and
  sanitize diagnostics.
- **Path/data corruption:** resolve exact roots, reject traversal/symlink escape,
  write project-local temporary runs, validate, then atomically promote.
- **False commercial certainty:** distinguish observations, calculations,
  inferences, unknowns, and hard blockers.
- **IP/likeness/sensitive content:** hard gates occur before design generation.
- **Image drift/production claims:** preservation-first prompts, whole-output
  review, immutable sources, and `concept_only` until deterministic prepress and
  human approval.
- **Package divergence:** generated/collision-safe central mirrors plus installed
  cache byte-parity verification.

## Completion boundary

Implementation is complete for review only when source and central plugins,
skills, schemas, tests, deterministic fixture E2E, installation state, and
parity checks pass. The delivery artifact is a draft PR. Merge, staging,
production deployment, live collection, scheduling, image generation, and store
actions remain separately authorized.
