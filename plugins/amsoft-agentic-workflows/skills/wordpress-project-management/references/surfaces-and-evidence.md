# WordPress surfaces and evidence

Choose evidence by claim. Label each result `pass`, `partial`, `blocked`, `not-run`, or
`not-applicable`, and include target, environment, account/surface, timestamp, evidence reference,
cache/CDN conditions, and limitation.

| Surface | Can prove | Cannot prove by itself |
| --- | --- | --- |
| Repository/IaC/PR | source intent, diff, tests, CI | live WordPress state or rendering |
| REST | object/config readback and schema-supported fields | visual behavior, cache, provider collection |
| WP-CLI/SSH/container | runtime, versions, options, records, plugin/theme state | public rendering or external provider state |
| Authenticated admin/CDP | private/admin access and interaction | logged-out public behavior or production deployment |
| Logged-out browser | public rendering, links, metadata, responsive behavior, interaction | hidden/private admin state or provider collection |
| Provider/audit/log | that provider's own recorded/configured state | WordPress rendering or consent unless specifically evidenced |
| Deployment/health | revision, service health, release state | content/design acceptance |

## Required verification mapping

- Content: exact object readback, managed checksum/revision, and authenticated/private or logged-out
  public rendering as the object status requires.
- Menu/navigation: object readback, route/deep-link, desktop/mobile navigation, keyboard/focus,
  and access-state checks.
- Media: attachment/source metadata plus responsive crop, alt, loading, and layout checks.
- Theme/template: owning-layer diff, focused tests, rendered responsive/keyboard/DOM checks, and
  console/network evidence.
- Plugin/configuration: runtime/admin/readback plus affected rendered or provider surface.
- SEO: implemented metadata/readback, rendered/source checks, and no unsupported recrawl/ranking
  claim.
- Analytics/consent: config/tag readback, consent states, logged-in exclusion, and provider evidence
  only when authorized and available.
- Stream/audit: policy/config/readback, supported synthetic record and cleanup, and administrator
  UI/data evidence.

API success, WP-CLI exit code, HTTP 200, screenshot, CI, deployment health, or a merged PR cannot
silently satisfy a missing required surface. A blocked channel remains blocked in the handoff.
