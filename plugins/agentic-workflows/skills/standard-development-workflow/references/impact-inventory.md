# Pattern-wide impact inventory

When the user says *all*, *every*, *across*, or names one example of a repeated
pattern, inspect the actual consumers before choosing a patch. An example is
evidence of the problem, not proof of the requested boundary.

1. Extract the requested behavior and quantifier. Search routes, components,
   collections, roles, states, viewports, data paths, and generated consumers as
   applicable. Record the search or repository evidence that produced the list.
2. Give every discovered surface a stable ID, kind, inclusion decision, reason,
   and shared implementation point. An excluded surface needs a concrete reason;
   a similar name alone does not make it in scope. Ask one grouped question only
   when the boundary would materially change behavior, cost, or authorization.
3. Prefer a shared implementation where semantics are genuinely common. Keep
   necessary per-instance differences explicit. Re-run discovery after a scope
   correction or when a new consumer appears in the diff.
4. Map every included surface to a passed structural check or satisfied runtime
   claim. A broad static inventory plus representative interactions is often
   better than repeating one slow browser test per instance. Visual claims still
   need inspectable rendered evidence for relevant viewports and states.
5. At handoff, compare discovered IDs with the inventory and the final diff.
   List exclusions and their reasons. A single fixed screenshot or component
   cannot close an *all forms* request without evidence for the other forms.

Use optional `impact_inventory` in a `task_run` when a durable handoff helps.
`discovered_surface_ids` comes from repository discovery; `surfaces` must cover
that set exactly. `verification_refs` name validation steps or satisfied claims.
The record validator requires final proof for each included surface. It cannot
discover missing consumers by itself, so retain the search evidence and review
the inventory against the actual repository.

## Synthetic examples

- **Tenant forms:** discover `create-notification`, `edit-notification`, and
  `create-submission`. A fix to one form leaves two IDs unverified and cannot
  satisfy the final inventory. An unrelated public contact form may be excluded
  with a reason tied to its different tenant semantics.
- **Responsive images:** discover hero, card, and menu-image consumers. Check
  generated `srcset`/`sizes` structurally, then inspect representative narrow
  and wide rendered states. One desktop screenshot cannot prove all viewports.
- **Cross-role control:** inventory both tenant and platform administrator
  paths. Verify the shared rule plus role-specific behavior; do not assume a
  tenant-only fixture covers the platform case.
