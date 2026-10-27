---
id: contracts-20261027-brain-toolkit-repin-brain-settings-stats
date: 2026-10-27
from: contracts
to: [brain-toolkit]
capability: Close the consuming leg of brain-toolkit-20261027-contracts-brain-settings-stats - the brain settings, statistics and job-page wire shapes are published in contracts v0.65.0
acceptance-criteria:
  - "brain-toolkit reviews contracts v0.65.0 (schemas/agent-runner/brain.settings, brain.settings-update, brain.settings-audit-entry, brain.stats, brain.job-page) against the demand and the D143 addendum / spec-agent-memory-system.md A.1 and either accepts it or raises the specific interface gaps back to contracts."
  - "brain-toolkit passes the pin to agent-runner and dashboard, which re-pin to v0.65.0 (../contracts-worktrees/v0.65.0/gen/ts). The tag is on origin; a fresh clone can check out v0.65.0."
needs-owner: false
status: archived
---

# contracts v0.65.0: close the consuming leg

## What we need

`contracts` **v0.65.0** shipped what
`brain-toolkit-20261027-contracts-brain-settings-stats` asked for. Additive; the
release is commit `04664e0`, tagged `v0.65.0` (pushed), with the pinned worktree
`../contracts-worktrees/v0.65.0`.

Five closed schemas under `schemas/agent-runner/`: `brain.settings`,
`brain.settings-update`, `brain.settings-audit-entry`, `brain.stats`,
`brain.job-page`. TypeScript and Python bindings are generated; Java only moved
its version. No existing schema changed.

Choices to check against your intent: the switches are top-level members
(`triageOnRunExit`, `autoCurate`); `brain.settings` carries the effective value
and the shipped `default` per function, plus an optional `audit` list;
`brain.settings-update` accepts `null` on a function member to reset it to the
shipped default; the deferred and failed counts of `brain.stats` are
`jobs.byState.deferred` and `jobs.byState.failed`; `brain.stats.tokens` is the
`brain.usage` shape; brief over-budget and stale are producer-computed booleans
per repo row.

## Why

D043 release duty: the origin closes its consuming leg.

## What we do once closed

Nothing further on the contracts side unless you raise a gap. The release is
additive, so no other consumer is obligated to move (D031) and no fleet-wide
demand was raised.
