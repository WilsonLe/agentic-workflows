# Payload CMS testing: unit, integration, and Playwright E2E

Use a pyramid with a sharp responsibility boundary. Tests must use throwaway data and never require a
production database, a real administrator account, or credential values in artifacts.

## Compose worktree contract

All test layers run through Docker Compose with a production-built application image. A local host
command, a development server, or a test that skips the production build is diagnostic-only and
cannot satisfy this workflow.

Give each worktree a deterministic Compose project name and isolated app, Postgres, network, named
volumes, and fixture data. Reuse the repository's standard application port and, when published,
standard Postgres port mapping for every worktree; the isolation boundary is the Compose project and
its resources, not a different port or a shared database. The fixed port contract requires host-wide
serialization: exactly one Payload Compose test stack may be running at a time.

Before any Compose command that can start the stack, acquire an atomic host-wide lock. A portable
directory lock uses `mkdir "${TMPDIR:-/tmp}/amsoft-payloadcms-compose-test.lock"` (which succeeds
for exactly one contender), with an `owner` file that contains the PID, worktree path, Compose
project name, and start time. Keep that lock until cleanup has completed, including `docker compose
down --volumes --remove-orphans`, and release it through a shell `trap` for `EXIT`, `INT`, and
`TERM`. A stale lock needs explicit recovery only after reading the owner record and verifying its
PID is not live; do not automatically remove a lock based on age. On lock contention, wait or return
a clear busy result without starting another stack.

Build first, before Postgres starts: `docker compose --project-name "$project" build app` must
succeed when the database is unreachable and no database credentials are supplied to the build
stage. The Dockerfile build stage must not run migrations, seeds, or health checks, use a database
URL, or depend on the database service. Start the isolated database only after that proof, then run
migrations, fixtures, and the selected tests against the compiled production application.

## Unit tests

Unit-test code whose behavior is independent of Payload runtime: role predicates, ownership query
builders, option normalization, plugin transforms, hook helpers, validation, and pure component
formatters. Execute the unit runner through the locked Compose test command after the production
image build. Make inputs explicit and test both `true`/allowed and `false`/constraint/denied cases.

```ts
it('limits non-admin readers to published posts', () => {
  expect(publishedOrEditor({ req: { user: undefined } } as never)).toEqual({
    status: { equals: 'published' },
  })
})
```

Do not call the access function once and call authorization tested: it cannot prove that an actual
Payload operation applies the result correctly.

## Integration tests

Boot the project's actual `payload.config` with a separate, worktree-owned Compose Postgres database.
Seed users for every relevant role and documents in at least two tenant/ownership states. Exercise
Local API and, where the application adds route/auth wiring, HTTP APIs. Assert returned documents,
validation failures, hooks, field masking, and migration-backed schema behavior.

For plugin integration, build a config that composes the plugin with host collections/globals and
assert the transformed config preserves host entries. Seed deterministically and clean up per test;
do not make test outcome depend on previously-run migrations or parallel test order.

Migration integration coverage has its own disposable database lifecycle: baseline migration state,
apply new migration, seed/exercise new shape, down, exercise old compatible shape, then up again.

## Playwright E2E tests

Use Playwright only for a small set of browser-observable critical journeys that integration tests
cannot prove: Admin login, collection/global navigation, custom component rendering and interaction,
save feedback/readback, and a forbidden action. Start the compiled production application against an
isolated, worktree-owned Compose E2E database, seed exact fixture accounts through a controlled
helper, and delete/reset data after the suite.

```ts
import { test, expect } from '@playwright/test'

test('an editor can save a post but cannot open user administration', async ({ page }) => {
  await page.goto('/admin')
  await page.getByLabel('Email').fill('editor@example.test')
  await page.getByLabel('Password').fill('test-only-password')
  await page.getByRole('button', { name: /login/i }).click()
  await expect(page.getByRole('link', { name: /posts/i })).toBeVisible()
  await page.goto('/admin/collections/users')
  await expect(page.getByText(/not authorized|forbidden/i)).toBeVisible()
})
```

Prefer role, label, text, then stable `data-testid` locators; do not bind critical tests to CSS class
names or XPath. Use Playwright fixtures for isolated setup/teardown and web-first assertions instead
of sleeps. Record traces on first retry in CI and retain failure artifacts according to a policy that
excludes credentials and personal data.

## Required coverage matrix

| Change | Unit | Integration | Playwright E2E |
| --- | --- | --- | --- |
| Access predicate/query | rule outcomes | real operation and filtered docs | direct-route denial for critical UI |
| Collection/global field | validation/helper | Local/API create-read-update and hooks | one critical editor journey |
| Custom component | pure props/formatting | registration and server/client boundary | visible interaction and save/readback |
| Payload plugin | option and merge behavior | composition with host config | only if it changes a user journey |
| Postgres migration | transform helpers | required up/down/up database round trip | post-migration critical workflow |

## Official sources

- [Payload plugin testing guidance](https://payloadcms.com/docs/plugins/build-your-own)
- [Playwright best practices](https://playwright.dev/docs/best-practices)
- [Playwright fixtures](https://playwright.dev/docs/test-fixtures)
