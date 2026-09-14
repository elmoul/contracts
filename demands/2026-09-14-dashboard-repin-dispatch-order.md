---
id: contracts-20260914-dashboard-repin-dispatch-order
date: 2026-09-14
from: contracts
to: [dashboard]
capability: Re-pin and adopt the demand `after` field and the DemandQueueEntry dispatch-order contracts published in contracts v0.26.0 for dashboard-20260914-demand-dispatch-order
acceptance-criteria:
  - "dashboard re-pins its contracts dependency to contracts v0.26.0 or later (TypeScript binding)."
  - "dashboard confirms it consumes the generated DemandQueueEntry type for its /agents Dispatch queue Order column instead of hand-rolling wave/waitingOn, or explains by when/why not."
  - "dashboard acknowledges that wave/waitingOn will read as absent until demand-coordinator and agent-runner land their own legs of dashboard-20260914-demand-dispatch-order — the Order column renders correctly against an entry whose waitingOn is empty and whose wave is 1, which is the state every demand is in before those legs ship."
needs-owner: false
status: open
---

# Dispatch order — close the consuming leg

## What we need

`contracts` v0.26.0 published the two contracts demanded in
`dashboard-20260914-demand-dispatch-order` criteria 1–2:

- `schemas/demand-coordinator/demand.json` — optional **`after`** (array of
  demand ids, same shape as `id`, `uniqueItems`, `minItems: 1`): the demands
  that must each be owner-approved before this one may be dispatched.
- `schemas/demand-coordinator/demand.queue-entry.json` — new
  **`DemandQueueEntry`**: one dispatch-queue row carrying **`wave`**
  (`integer`, `minimum: 1`) and **`waitingOn`** (the `after` ids not yet
  owner-approved), alongside `demandId`/`date`/`from`/`to`.

Java and TypeScript bindings only (dashboard consumes the TypeScript one, so
you are covered). Per D043, `dashboard` — the origin — needs to close its
consuming leg: re-pin to the new tag and adopt (or explain why not yet).

## Why / what's blocked

Your `/agents` Dispatch queue's Order column has nothing to read until this
lands, and hand-rolling `wave`/`waitingOn` on the dashboard side is exactly
what the demand was raised to stop.

One thing worth knowing before you build against it: **`wave` and `waitingOn`
are not each other's inverse**, and an empty `waitingOn` does not imply
`wave` 1. `wave` is raised by two independent causes — this demand's own
unresolved `after` edges (which is what `waitingOn` reports), and sequence
position within a multi-hexagon demand (a sub-demand never shows a lower wave
than the target before it). A multi-hexagon sub-demand can therefore sit at
wave 3 with an empty `waitingOn`. Do not render the Order column as
`waitingOn.length + 1`; read `wave`. This case is pinned by a known-good
document in `tests/validate_demand.py` and by a round-trip assertion in
`DemandDispatchOrderContractsTest`.

`wave` has `minimum: 1` deliberately — `0` is a bug, not a "not yet scheduled"
sentinel. An unset `wave` is omitted from the wire rather than serialized as
`0` (the Java POJO is `@JsonInclude(NON_NULL)`); a consumer that treats a
missing `wave` as `0` will sort it ahead of everything.

## What we do once closed

Split across two moments, because the types ship now but the data does not:

1. **Now** — re-pin to v0.26.0 and adopt the `DemandQueueEntry` type. The
   Order column can be built and shipped against it immediately; it will
   correctly render `wave: 1` / `waitingOn: []` for every entry until the
   next two legs land.
2. **After the remaining legs** — `demand-coordinator` (compute and serve
   wave/waitingOn, surface dangling/self/cyclic `after` ids on `GET /board`
   per D023, plus the read-only waiting-demands surface) and `agent-runner`
   (`GET /dispatchable` ordered by wave, then date, then demandId, with the
   waiting demands in a separate list), then `runtime` (rebuild and verify
   the served image). These are the other targets of the same demand and the
   coordinator sequences them; they are not additional demands raised by this
   release.

The `after` field is optional and additive, so **nothing else in the fleet is
obligated to move** — no fleet-wide bump demand was raised (D031 pins are
deliberate, D043 additive scope).

## Note on the Python binding

`after` and `DemandQueueEntry` have **no Python binding in v0.26.0**, on
purpose. Regenerating `gen/python` with the installed `datamodel-codegen`
0.68.1 also rewrites the pre-existing `to` field to a `RootModel` wrapper
(`demand.to[0] == "factory"` would become `False`) — unrelated generator
drift, verified against the unmodified v0.25.0 schema. That is a breaking
change no part of this demand asks for, so `pyproject.toml` stays at `0.25.0`.
This does not affect dashboard (TypeScript). If any of the remaining targets
is Python and needs these shapes, raise a demand rather than regenerating
blindly — the full write-up is in `CHANGELOG.md` v0.26.0.
