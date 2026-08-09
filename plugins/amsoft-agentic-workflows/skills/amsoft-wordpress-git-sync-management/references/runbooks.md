# Operator runbooks

Select the runbook from the current lifecycle state and topology:

- [Preflight, restore rehearsal, and baseline](runbooks/preflight-and-baseline.md)
- [One-object canary](runbooks/one-object-canary.md)
- [Waves, coexistence, and automation cutover](runbooks/waves-coexistence-and-cutover.md)
- [Rollback, recovery, and de-enrolment](runbooks/rollback-recovery-and-deenrollment.md)
- [Provider and runtime variants](runbooks/provider-runtime-variants.md)

Every mutating step must name prerequisites, exact target, pre-state/dry-run,
approval, expected evidence, canonical readback, failure stop, recovery, and
resume checkpoint. Placeholders are instructions to discover current values;
never copy an example target or command blindly.
