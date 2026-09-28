---
id: contracts-20260927-factory-repin-sync-recovery-retention
date: 2026-09-27
from: contracts
to: [factory]
capability: Close the consuming leg of factory-20260927-sync-recovery-retention — operation retention coverage and safe missing-operation recovery shipped in contracts v0.35.0
acceptance-criteria:
  - "factory reviews contracts v0.35.0 (schemas/delivery/delivery.operation-coverage.json, delivery.error.json, delivery.sync-operation.json, delivery.sync-request.json; schemas/delivery-api/youtrack-delivery.openapi.yaml; docs/task-delivery.md §Retention coverage…, §Absence is not non-execution, §Producer obligations) and either accepts it or raises the specific interface gaps back to contracts."
  - "factory re-pins to v0.35.0 at its reviewed integration step (package, image, descriptor and tests together) and its caller-side recovery logic follows the new rules: persist reservedAt with the reserved request and send it on every lookup and write; treat operation_not_found (with details.reservedAt/details.coveredSince) as the only conclusive never-stored answer; never resubmit or re-mint a key on operation_lookup_out_of_coverage, and surface that inconclusive lookup in the waiting view instead of retrying on a timer."
  - "factory validates operation records against the JSON Schema itself where the v0.35.0 conditionals apply, not against the generated bindings alone — the pydantic/TS types do not implement if/then, so DeliverySyncOperation accepts an unwindowed absence and a resend without absenceProvenAt (see docs/task-delivery.md §Binding caveat)."
  - "factory raises its downstream producer demand to youtrack naming v0.35.0 and the four producer obligations in docs/task-delivery.md §Producer obligations added in v0.35.0 (serve the coverage route with an honest coveredSince; classify every by-key miss; gate the write path on reservedAt; window every absence observation and never mark an uncertain record retryable), or explains why not."
needs-owner: false
status: archived
---

# Operation retention coverage: close the consuming leg

## What we need

`contracts` **v0.35.0** shipped what `factory-20260927-sync-recovery-retention`
asked for. A lookup miss is no longer ambiguous:

- `delivery.operation-coverage` (new) + `GET /delivery/v1/operations/coverage`
  publish a **coverage floor** — every record the service stored whose reservation
  time is at or after `coveredSince` is still retrievable. `terminalRetentionDays`
  (floor 90) and `vendorInFlightBoundSeconds` (the reconciliation quiet window)
  come with it.
- `delivery.error` now distinguishes **`operation_not_found`** (conclusive:
  never stored — the schema requires `details.reservedAt`/`details.coveredSince`
  and pins `retryable: true`) from **`operation_lookup_out_of_coverage`**
  (inconclusive: `reason: reserved_at_before_coverage` or `no_key_provenance`,
  pinned `retryable: false`). A bare conclusive-looking 404 is no longer a
  representable document.
- `delivery.sync-request.reservedAt` (new, optional) carries the caller's key
  provenance. The **write path is gated** by it too: a re-`PUT` whose `reservedAt`
  predates `coveredSince` must be refused with nothing written.
- `delivery.sync-operation` gained `absenceProvenAt` and
  `vendorInFlightBoundSeconds`, and `readBack` gained `absentSince` /
  `absenceQuietUntil`. An `effectPresent: false` read-back without a window is
  **invalid**, and `attempts >= 2` with no `absenceProvenAt` is **invalid** — so
  no resend can look authorised by a single, unwindowed absence observation.
- `uncertain` must carry `tracker_outcome_unknown` with `retryable: false`, and an
  `uncertain` record is never purged.

The reference is **`docs/task-delivery.md`**, notably §Retention coverage and safe
missing-operation recovery, §Absence is not non-execution, §Binding caveat and
§Producer obligations added in v0.35.0.

## Why

D043 release duty: the origin closes its consuming leg. Before this release the doc
told Factory that a miss meant "the request never arrived, so Factory may submit
that key" — which, after terminal retention expiry, authorises a second write under
a key whose first write already landed. That sentence is gone.

The release is **additive**: `factory.*`, `agent_runner.*`, `ci_runner.*` and the
planner shapes are unchanged, so moving from v0.34.0 changes nothing already in use.
Per D031/D043 no other consumer is obligated to move. Nothing is live because of
this release: every `/delivery/v1` route remains unimplemented and no service emits
a `delivery.sync-operation` document yet.

## What we do once closed

The interface obligations land when `youtrack` implements the operation store —
that is the downstream producer demand in criterion 4. Factory's own follow-up is
the caller side: persist and send `reservedAt`, classify the two 404s differently,
and never let a lookup miss authorise a resend.

**Caveat, stated plainly because it changes how you implement this:** the generated
bindings do not enforce any of the v0.35.0 `if/then` rules. A caller or producer that
relies on `DeliverySyncOperation`/`DeliverySyncRequest` alone will accept exactly the
shapes these rules exist to refuse. Validate against the JSON Schema where they apply.
