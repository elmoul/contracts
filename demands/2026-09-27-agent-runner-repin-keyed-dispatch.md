---
id: contracts-20260927-agent-runner-repin-keyed-dispatch
date: 2026-09-27
from: contracts
to: [agent-runner]
capability: Close the consuming leg of agent-runner-20260927-contracts-runner-keyed-dispatch — keyed dispatch, the dispatch-key lookup, observed workspace identity and the producer-result lookup routes shipped in contracts v0.33.0
acceptance-criteria:
  - "agent-runner reviews contracts v0.33.0 (schemas/agent-runner/runner.dispatch-request.json, runner.run-record.json, runner.dispatch-reservation.json and docs/task-delivery.md §Runner routes) against the demand and either accepts it or raises the specific interface gaps back to contracts."
  - "agent-runner re-pins its file: dependency to ../contracts-worktrees/v0.33.0/gen/ts and imports RunnerDispatchRequest, RunnerRunRecord, RunnerRunWorkspace and RunnerDispatchReservation from @platform/contracts — these three modules did not exist in gen/ts before v0.33.0, which is why a repin was impossible."
  - "agent-runner implements reserve-before-spawn, replay, conflict and the lookup with exactly the status codes docs/task-delivery.md §Runner routes fixes (202 new, 200 replay, 409 conflicting reuse, 409 repo locked, 429 cap, 404 no reservation) and the no-relaunch rule for an uncertain dispatch."
  - "agent-runner computes requestHash with the canonicalization runner.dispatch-reservation.json fixes, and reproduces that schema's documented worked example byte-for-byte on the documented input before wiring the ledger."
  - "agent-runner stops stripping workspace from the wire run record and echoes dispatchKey, so GET /runs/{id}/producer-result and GET /dispatches/{dispatchKey}/producer-result can fill repository, branch, revision and correlation.operationKey; an unkeyed dispatch stays unchanged."
  - "agent-runner reports factory-20260927-agent-runner-delivery-results (the downstream factory demand) once its leg is live, naming v0.33.0."
needs-owner: false
status: open
---

# contracts v0.33.0: close the consuming leg

## What we need

`contracts` **v0.33.0** shipped what
`agent-runner-20260927-contracts-runner-keyed-dispatch` asked for. Additive; the
release is `3d72989`, tagged, with the pinned worktree
`../contracts-worktrees/v0.33.0`.

- `schemas/agent-runner/runner.dispatch-request.json`: optional caller-minted
  `dispatchKey`, pattern `^[A-Za-z0-9][A-Za-z0-9._:-]{7,199}$`. The `required` list
  is unchanged, so an unkeyed request validates exactly as it did before.
- `schemas/agent-runner/runner.run-record.json`: optional `dispatchKey` (echoed;
  **absent**, not null, when the run was unkeyed) and an optional nullable
  `workspace` with `baseBranch`, `baseRevision`, `branch`, `revision`, `dirty`,
  `observedAt`. Revisions are full 40-hex lowercase; `null` means *not observed*,
  never a default. Your internal `RunWorkspace` nests `base`/`head`, so the wire
  shape is the flattening: `baseBranch`/`baseRevision` are the pre-launch
  observation, `branch`/`revision`/`dirty` the post-exit one, `observedAt` the
  post-exit time. `runner.run-record` stays closed, so all six are required *inside*
  `workspace` and consumers can rely on them being present.
- **New** `schemas/agent-runner/runner.dispatch-reservation.json`: the
  `GET /dispatches/{dispatchKey}` body (`dispatchKey`, `requestHash`, `runId`,
  `reservedAt`, `run`), the reservation/replay/conflict/no-relaunch semantics, the
  exact `requestHash` canonicalization, and a worked example of it.
- `docs/task-delivery.md` §Runner routes: the route table with status codes, the
  reserve-before-spawn rule, the 409 conflicting reuse, the 404-is-safe rule, the
  no-relaunch rule, and both producer-result lookups.
- Bindings: `gen/ts` gains `runner-dispatch-request.ts`, `runner-run-record.ts`
  and `runner-dispatch-reservation.ts` (exported from `index.ts`, built into
  `dist/`). Python gains
  `platform_contracts.agent_runner.runner_dispatch_reservation`.

## Why

D043 release duty: the origin closes its consuming leg. No service implements
these routes yet — this release publishes the interface, nothing more. The
factory demand this serves (`factory-20260927-agent-runner-delivery-results`)
stays blocked until your side is live.

## What we do once closed

Nothing further on the contracts side unless you raise a gap. Note the release was
**additive**, so no other consumer is obligated to move (D031) and no fleet-wide
demand was raised — `factory` keeps consuming `agent_runner.*` at whatever pin it
holds until it chooses to move.
