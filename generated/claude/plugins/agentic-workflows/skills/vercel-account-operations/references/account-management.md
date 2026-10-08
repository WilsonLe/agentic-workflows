# Vercel browser account and team management

Apply [service browser operations](browser-selection.md).

1. Verify the signed-in browser identity and inspect the account/team selector.
2. Match the current project's repository/domain and select the exact team and
   project. Paginate or narrow visible lists; report partial inventory honestly.
3. Inspect actual access, memberships, roles, integrations, domains, spend settings,
   and account entitlements through visible dashboard settings as needed.
4. Before changing anything, capture relevant non-secret pre-state, exact target,
   permissions/cost/access effect, task authority, verification, and recovery.
5. Invite/remove members, change roles, transfer projects, manage domains/integrations,
   or adjust spend through supported dashboard controls. Preserve a usable owner
   or administrator path. Invitations/messages require explicit communication scope.
6. Reopen settings and verify saved state and effective access. State when a transfer,
   removal, or cancellation has no automatic rollback.

Optional `vercel whoami` and read-only team/project inventory can supplement reads
only after matching browser identity and scope. They must not change global context
or auto-link a directory. Do not switch to `vercel api`, REST, or MCP mutations
because they are convenient; missing UI controls require disclosure and explicit
user direction for the alternative operation.
