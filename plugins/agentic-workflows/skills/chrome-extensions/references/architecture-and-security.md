# Architecture and security

| Context | Responsibility | Boundary to verify |
| --- | --- | --- |
| Service worker | Event handling, privileged APIs, coordination | No DOM; suspension must not lose durable state |
| Content script | Bounded page interaction | Page content and messages are untrusted |
| Popup, side panel, options page | User interactions and configuration | Lifecycle, keyboard access, explicit loading/error states |
| Offscreen document | A documented DOM-only capability unavailable in the worker | Justify the reason and close it when finished |

Register worker event listeners at top level so they exist when Chrome dispatches events.
Persist necessary state with `chrome.storage` or appropriate durable storage. Make event
handling safe to retry; use `chrome.alarms` for scheduled work rather than relying on an
in-memory timer surviving worker termination. Verify storage after worker restart.

Prefer `activeTab` for a user-triggered action on the current page when it suffices.
Request `scripting`, `storage`, `sidePanel`, and host permissions only for an implemented
need. Optional permissions require an understandable user action, denial handling, and
revocation handling. Broad host access requires a concrete explanation in store metadata.
An API permission and host access are separate decisions.

Content scripts use an isolated JavaScript world by default, but share the page DOM.
Treat page text, DOM events, and messages as untrusted. Validate message type and payload,
sender identity, and tab/origin against the operation's allowed callers. Never turn an
arbitrary message URL into an unrestricted privileged fetch. External messaging needs a
bounded `externally_connectable` policy and separate caller checks. Avoid disclosing secrets
or granting access merely because a message originated from an extension-owned surface.

Bundle scripts locally. Respect MV3 extension-page CSP: avoid inline executable scripts,
`eval`, and remote executable code. Render untrusted content as text or sanitize it with an
appropriate reviewed method. Restrict web-accessible resources to intended assets and
origins. Inspect the production artifact for secrets and unintended files before packaging.

The offline audit checks MV3 identity/version, selected packaged assets, deprecated background
fields, permission-array shape, and a few explicit insecure CSP tokens. It does not parse
HTML/JavaScript, validate every manifest field, match pattern, CSP directive, API name, or
Web Store policy. Chrome loading, code review, and runtime tests remain required.

Official references (consult the current versions for the chosen APIs):

- [Worker lifecycle](https://developer.chrome.com/docs/extensions/develop/concepts/service-workers/lifecycle)
- [Content scripts](https://developer.chrome.com/docs/extensions/develop/concepts/content-scripts)
- [Message passing](https://developer.chrome.com/docs/extensions/develop/concepts/messaging)
- [Permission declarations](https://developer.chrome.com/docs/extensions/develop/concepts/declare-permissions)
- [Extension CSP](https://developer.chrome.com/docs/extensions/reference/manifest/content-security-policy)
