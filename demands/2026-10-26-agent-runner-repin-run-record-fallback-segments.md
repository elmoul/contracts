---
id: contracts-20261026-agent-runner-repin-run-record-fallback-segments
date: 2026-10-26
from: contracts
to: [agent-runner]
capability: Close the consuming leg of agent-runner-20261026-contracts-runner-run-record-fallback-segments - D142's automatic subscription-to-API fallback and per-provider usage segments are published on runner.run-record in contracts v0.62.0
acceptance-criteria:
  - "agent-runner reviews contracts v0.62.0 (schemas/agent-runner/runner.run-record.json, the fallback and usageSegments members) against the demand and either accepts it or raises the specific interface gaps back to contracts."
  - "agent-runner re-pins its file: dependency to ../contracts-worktrees/v0.62.0/gen/ts and imports RunnerRunFallback and RunnerUsageSegment from @platform/contracts. The tag is local until the owner pushes it; a fresh clone must wait for the push before checking out v0.62.0."
  - "agent-runner's wire run record serves fallback {from,to,reason,sessionId,continued} only on a run that fell back and usageSegments only on a fallback run, with the record-level usageProvider left as the starting dimension and never billed for the whole run."
  - "agent-runner validates both ends against the published schema - a pre-D142 run record still validates unchanged, and a fallback run with two usage segments validates - and reports any mismatch rather than loosening the schema locally."
needs-owner: false
status: open
---

# contracts v0.62.0: close the consuming leg

## What we need

`contracts` **v0.62.0** shipped what
`agent-runner-20261026-contracts-runner-run-record-fallback-segments` asked for.
Additive; the release is commit `3009936`, tagged `v0.62.0`, with the pinned
worktree `../contracts-worktrees/v0.62.0`.

- `runner.run-record` gains optional **`fallback`**: closed, required `from`,
  `to`, `reason` (`session-limit | weekly-limit`), `sessionId`, `continued`.
  Absent - never `null` - on every ordinary run. `continued: false` is a failed
  run, not a silent restart.
- `runner.run-record` gains optional **`usageSegments`**: closed
  `{ provider, model?, tokensIn, tokensOut }`, min one entry, present only on a
  fallback run. On a fallback run it replaces the single `usageProvider`
  dimension - meter one usage fact per segment and none for the combined total.
  Record-level `tokensIn`/`tokensOut` stay the run's totals.
- The `required` list and `additionalProperties: false` are unchanged, so a
  pre-D142 record stays valid byte-for-byte.
- Bindings: `gen/ts` exports `RunnerRunFallback` and `RunnerUsageSegment` (source
  and `dist/`, also present in `runner-dispatch-reservation.ts`); Python gains
  the same models.

## Why

D043 release duty: the origin closes its consuming leg. The shape was copied
from agent-runner's already shipped `RunFallback`/`UsageSegment`, so this is a
pin-and-adopt, not a redesign.

## What we do once closed

Nothing further on the contracts side unless you raise a gap. The release is
additive, so no other consumer is obligated to move (D031) and no fleet-wide
demand was raised.
