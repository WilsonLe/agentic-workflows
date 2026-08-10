# Payload CMS testing: unit, integration, and Playwright E2E

Use a pyramid with a sharp responsibility boundary. Tests must use throwaway data and never require a
production database, a real administrator account, or credential values in artifacts.

## Unit tests

Unit-test code whose behavior is independent of Payload runtime: role predicates, ownership query
builders, option normalization, plugin transforms, hook helpers, validation, and pure component
formatters. Make inputs explicit and test both `true`/allowed and `false`/constraint/denied cases.

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

Boot the project's actual `payload.config` with a separate test database. Seed users for every
relevant role and documents in at least two tenant/ownership states. Exercise Local API and, where
the application adds route/auth wiring, HTTP APIs. Assert returned documents, validation failures,
hooks, field masking, and migration-backed schema behavior.

For plugin integration, build a config that composes the plugin with host collections/globals and
assert the transformed config preserves host entries. Seed deterministically and clean up per test;
do not make test outcome depend on previously-run migrations or parallel test order.

Migration integration coverage has its own disposable database lifecycle: baseline migration state,
apply new migration, seed/exercise new shape, down, exercise old compatible shape, then up again.

## Playwright E2E tests

Use Playwright only for a small set of browser-observable critical journeys that integration tests
cannot prove: Admin login, collection/global navigation, custom component rendering and interaction,
save feedback/readback, and a forbidden action. Start the full application against an isolated E2E
database, seed exact fixture accounts through a controlled helper, and delete/reset data after the
suite.

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
