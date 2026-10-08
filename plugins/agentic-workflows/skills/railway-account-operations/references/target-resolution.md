# Railway target resolution

Apply [service browser operations](browser-selection.md).

1. Open the dashboard account/workspace selector. Match the current project's
   repository, domain, and deployment documentation to an observed workspace.
2. Resolve the project, environment, service, and current deployment in the UI.
   Preserve visible IDs/URLs and names; similar names can exist in different scopes.
3. Use repository `.railway/` link metadata only as a non-secret hint. A local
   directory or CLI link does not prove the active browser or tool identity.
4. Determine production from domains, traffic, service role, deployment, and
   project documentation; if unclear, treat the effect as production.
5. Immediately before writing, recheck account, workspace, project, environment,
   service, deployment, and relevant configuration. Stop on stale/concurrent state.

For optional CLI logs/status, independently verify the tool's account and exact
scope, then use explicit target flags supported by installed help. Do not link or
unlink a directory, switch default context, or change a resource to resolve a read.
An unresolved/mismatched identity blocks that diagnostic; continue safe browser work.
