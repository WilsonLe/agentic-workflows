# Verification channels, frozen evidence, and release

## Verification-channel contract

For every explicitly requested or risk-critical claim, record:

- the observable claim;
- primary tool, environment, account, device, or control channel;
- early availability preflight;
- pre-approved equivalent fallbacks;
- weaker partial or diagnostic substitutes;
- approval owner and blocking behavior;
- the exact channel that produced each artifact.

An **equivalent fallback** proves the same claim through an independently justified boundary. A
**partial substitute** proves only a subset. **Diagnostic evidence** helps investigation but cannot
satisfy acceptance. If a required channel becomes unavailable and no equivalent was approved,
stop the completion claim and request direction.

Never relabel Playwright as Chrome CDP, API output as browser proof, a screenshot as interaction
proof, local evidence as deployed-environment proof, or one account/provider/device as another.
Fallback availability never broadens credential, authorization, privacy, security, or
data-integrity boundaries.

Examples:

- Browser automation through another engine is equivalent only for claims independent of the
  requested engine or control channel; otherwise it is partial.
- A simulator cannot silently replace a required real-device hardware or operating-system claim.
- An unauthenticated mock cannot satisfy an authenticated provider/account flow.
- Local health, API, or browser output cannot satisfy a staging identity or deployed-integration
  claim.

## Rehearsal and final evidence

Capture rehearsal evidence during iteration when helpful, but label it clearly and never use it to
satisfy review or deployment. Finalize evidence only after:

- the candidate is committed and tracked source is clean;
- implementation and complete planned local checks are stable;
- applicable immutable artifact identities are known;
- required channel claims are satisfied;
- retained artifacts are complete, visually inspectable when required, and secret-safe.

The final manifest binds repository and commit identity, build/package/container/deployment
artifact identities, validation results, evidence file digests, capture context, exact channels,
timestamps, skipped or inapplicable checks, limitations, and environment classification without
credentials.

Relevant source, test, workflow, generated-file, artifact, deployment, or evidence drift removes
final status and requires revalidation or recapture. Recheck the manifest at draft-PR handoff,
merge readiness, and staging. Identity and hashes do not replace visual inspection of requested
visual evidence. Cleanup cannot remove required evidence before durable handoff.

For “available now?” questions, follow [release-readback.md](release-readback.md). Read the
requested target's active revision, start mode, URL, health, and relevant user flow. Do not infer
availability from a PR, merge, completed deployment job, saved tab, or earlier readback.

## Plugin release over a private Git marketplace

When this workflow changes an authored plugin, follow its authoring policy and repository release
rules. For the Agentic Workflows marketplace, first installation from the private GitHub repository is:

```bash
codex plugin marketplace add anhminhsoft/agentic-workflows \
  --ref main --json
codex plugin add agentic-workflows@agentic-workflows --json
```

SSH is an equivalent Git transport when preconfigured:

```bash
codex plugin marketplace add \
  git@github.com:anhminhsoft/agentic-workflows.git \
  --ref main --json
```

Never embed credentials in a URL. Verify the chosen Git transport can read the exact private
repository without exposing credentials.

Refresh and reinstall later releases with:

```bash
codex plugin marketplace upgrade agentic-workflows --json
codex plugin add agentic-workflows@agentic-workflows --json
codex plugin list --json
```

Before completion, verify marketplace identity, declared version and cachebuster, normalized plugin
name, installed/enabled state, resolved source, cached-package existence, changed-file parity, and
a fresh-session route. When explicitly required and accessible, visibly verify the rendered
Plugins UI entry. A new session is required to load newly installed skills and tools.

Rollback selects a known prior Git ref or revision, refreshes that marketplace snapshot, and
reinstalls its declared plugin version. Rollback never edits project repositories or deletes
retained workflow evidence.
