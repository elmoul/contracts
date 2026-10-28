---
id: contracts-20261028-brain-toolkit-repin-brain-functions-spec-rows
date: 2026-10-28
from: contracts
to: [brain-toolkit]
capability: Close the consuming leg of brain-toolkit-20261028-brain-functions-spec-rows - brain.functions admits spec-sync and spec-seed in contracts v0.67.0
acceptance-criteria:
  - "brain-toolkit re-pins contracts v0.67.0 (../contracts-worktrees/v0.67.0) in its test and validates the full six-row config/ai-functions.json against schemas/agent-runner/brain.functions, or raises the specific gap back to contracts."
status: archived
needs-owner: false
---

# contracts v0.67.0: close the consuming leg

## What we need

`contracts` **v0.67.0** shipped what `brain-toolkit-20261028-brain-functions-spec-rows` asked for. Additive; release commit `27e9545`, tag `v0.67.0` (pushed), pinned worktree `../contracts-worktrees/v0.67.0`.

`brain.functions` `functions` gains optional `spec-sync` and `spec-seed` (same row shape); the original four stay required. TypeScript and Python bindings are regenerated; Java only moved its version. Note `brain.settings` is unchanged and still lists four functions.

## Why

D043 release duty: the origin closes its consuming leg.

## What we do once closed

Nothing further unless you raise a gap. The release is additive, so no other consumer is obligated to move (D031).
