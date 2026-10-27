---
id: contracts-20261027-brain-toolkit-repin-brain-v1-schemas
date: 2026-10-27
from: contracts
to: [brain-toolkit]
capability: Close the consuming leg of brain-toolkit-20261027-contracts-brain-v1-schemas - the brain v1 wire shapes (brain.* under schemas/agent-runner/) are published in contracts v0.63.0
acceptance-criteria:
  - "brain-toolkit reviews contracts v0.63.0 (schemas/agent-runner/brain.*.json, eleven schemas) against the demand and spec-agent-memory-system.md v1.0 and either accepts it or raises the specific interface gaps back to contracts."
  - "brain-toolkit's commands emit exactly the published shapes: every --json result validates against brain.cli-result, every runs.jsonl line against brain.run-record, changes.jsonl against brain.change, notes against brain.note, inbox candidates against brain.candidate, and config/ai-functions.json against brain.functions; the bundle it reads validates against brain.run-bundle. Any mismatch is reported to contracts rather than loosened locally."
  - "brain-toolkit passes the pin to the two consumers it has demands open with: agent-runner (brain-toolkit-20261027-agent-runner-brain-v1-jobs) and dashboard (brain-toolkit-20261027-dashboard-brain-v1-page) re-pin to v0.63.0 (../contracts-worktrees/v0.63.0/gen/ts). The tag is on origin; a fresh clone can check out v0.63.0."
needs-owner: false
status: archived
---

# contracts v0.63.0: close the consuming leg

## What we need

`contracts` **v0.63.0** shipped what
`brain-toolkit-20261027-contracts-brain-v1-schemas` asked for. Additive; the
release is commit `132e71b`, tagged `v0.63.0` (pushed), with the pinned worktree
`../contracts-worktrees/v0.63.0`.

Eleven closed schemas under `schemas/agent-runner/`: `brain.run-record` (the
`runs.jsonl` line, including the `brain-job` follow-up line), `brain.run-bundle`,
`brain.change`, `brain.note`, `brain.candidate`, `brain.functions`,
`brain.cli-result`, `brain.repo-summary`, `brain.usage`, `brain.job`,
`brain.job-request`. TypeScript and Python bindings are generated; Java only
moved its version.

Where the spec won over the demand text (so read the schemas, not the demand
list): `reason` not `why` in the function table; `brain.cli-result` is
`ok/deferred/uncertain/error/model/effort/tokens/writes/details` (no `command`,
`deferredReason`, `tokensIn`, `tokensOut`); `brain.repo-summary.migrated` is a
boolean; `brain.run-record` is the spec's `runs.jsonl` line, not a `run-entry`;
`brain.job-request` has no `command` (the route names it); `brain.note-action`
is not published (pin/unpin/retire are URLs with no body).

## Why

D043 release duty: the origin closes its consuming leg. The toolkit is the
producer of every file shape here, so it is the first to confirm they match.

## What we do once closed

Nothing further on the contracts side unless you raise a gap. The release is
additive, so no other consumer is obligated to move (D031) and no fleet-wide
demand was raised.
