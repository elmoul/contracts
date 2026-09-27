---
demandId: factory-20260927-sync-recovery-retention
worker: contracts
date: 2026-09-27
status: done
shipped: ["v0.35.0", "commit e678d39 on main (feat(delivery): the release)", "commit d4b3ce3 on main (docs: binding caveat; this is also the commit v0.35.0 points at)", "schemas/delivery/delivery.operation-coverage.json (new)", "schemas/delivery/delivery.error.json (operation_not_found vs operation_lookup_out_of_coverage; tracker_outcome_unknown)", "schemas/delivery/delivery.sync-operation.json (absenceProvenAt, vendorInFlightBoundSeconds, readBack.absentSince + absenceQuietUntil)", "schemas/delivery/delivery.sync-request.json (optional reservedAt, part of the hashed body)", "schemas/delivery-api/youtrack-delivery.openapi.yaml (GET /delivery/v1/operations/coverage; reservedAt on lookup and write)", "docs/task-delivery.md (retention coverage, absence is not non-execution, binding caveat, producer obligations)", "tests/validate_delivery.py (88 schema cases, incl. check_recovery_semantics covering both demand scenarios)", "Python binding platform_contracts.delivery.delivery_operation_coverage + regenerated delivery_error/sync_operation/sync_request", "TypeScript delivery-operation-coverage.ts + regenerated delivery-error/sync-operation/sync-request + rebuilt dist/"]
summaryRef: "commit d4b3ce3 on main (the v0.35.0 tree: feat e678d39 + the binding-caveat docs)"
---

# Fulfillment: operation retention coverage and safe missing-operation recovery

## State check

**Not previously shipped.** The two supervisor-opened sessions for this demand
(`2026-09-27_1108`, `2026-09-27_1207`) left no commits, no tag, and no report, and
the gap was still live in the tree before this session: `docs/task-delivery.md` said
a lookup miss meant "the request never arrived, so Factory may submit that key", and
nothing in `schemas/delivery/` distinguished a never-stored key from a purged
terminal record. This session did the work.

## What shipped

Tag **`v0.35.0`** (commit `d4b3ce3`, pushed to `origin/main`), pinned worktree
`../contracts-worktrees/v0.35.0`. The release is additive: no existing shape changed
meaning, and `git diff` against v0.34.0 touches nothing under `schemas/factory`,
`schemas/agent-runner`, `schemas/ci-runner` or the planner shapes.

The full reference is **`docs/task-delivery.md`**. Per criterion:

### 1. Never-seen is now distinguishable from expired/purged

- **`delivery.operation-coverage`** (new) + `GET /delivery/v1/operations/coverage`
  publish the **coverage floor**: `coveredSince`, at or after which every record the
  service ever stored is still retrievable; `terminalRetentionDays` (schema floor
  `90`); and `vendorInFlightBoundSeconds`. The floor may only move forward.
- **`delivery.error`** carries the classification. `operation_not_found` is
  conclusive *never stored*, and the schema now **requires** `details.reservedAt` and
  `details.coveredSince` on it and pins `retryable: true`. `operation_lookup_out_of_coverage`
  is the inconclusive answer — `reason: reserved_at_before_coverage` (the key predates
  the floor, so a terminal record for it may have been purged) or `no_key_provenance`
  (no `reservedAt` supplied) — and is pinned `retryable: false` with the floor echoed.
- **A bare conclusive-looking 404 is no longer a representable document.** The service
  has to have had, and to show, the provenance it judged. A miss alone therefore
  cannot authorise replay of a possibly completed write — the caller cannot construct
  the "safe" reading out of an unclassified 404, because the schema refuses to emit one.
- **The write path is gated too**, which the demand did not ask for but the same bug
  requires: a re-`PUT` of the same key is another way to repeat a write. If the body's
  `reservedAt` predates `coveredSince` the service must refuse with
  `operation_lookup_out_of_coverage` and write nothing.
- `delivery.sync-request.reservedAt` (new, optional) is the caller's key provenance. It
  is part of the hashed canonical body, so a replay must repeat it verbatim or it is
  `operation_key_conflict` — which is what makes the write-path gate enforceable.

### 2. Absence in one read-back is not proof of non-execution

- An `effectPresent: false` read-back **must** now carry `absentSince` (the earliest
  observation from which absence has held continuously) and `absenceQuietUntil`
  (= `absentSince` + `vendorInFlightBoundSeconds`). **An unwindowed absence
  observation is not a valid record** — the shape that used to authorise a resend is
  unrepresentable.
- Non-execution is established only when absence held **through `absenceQuietUntil`**
  (so a delayed original request can no longer land) **and** the vendor exposes no
  record of the request where such a lookup exists. Only then does the service set
  `absenceProvenAt`, and only `absenceProvenAt` authorises a resend.
- `attempts >= 2` with a null or missing `absenceProvenAt` is **invalid by schema**, so
  every resend is auditable back to the absence that justified it.
- Uncertainty is preserved rather than resolved by assumption: an `uncertain` record
  must carry `tracker_outcome_unknown` with `retryable: false`, and is never purged.
  `tracker_unavailable` (pinned `retryable: true`) described the opposite situation —
  the vendor unreachable *before* any write was sent — and is no longer usable to
  report a post-send timeout. That was a live hole: it let a post-send timeout look
  safely retryable.
- The ordering rules (`absenceProvenAt >= absenceQuietUntil`, the window running
  forward from `absentSince`) are arithmetic JSON Schema cannot express, so they are
  enforced by `tests/validate_delivery.py` §`check_recovery_semantics` instead of a
  keyword.

### 3. Recovery fixtures and caller/producer documentation

`tests/validate_delivery.py` grew 63 → **88 cases**; every negative was checked to fail
for its intended reason. The two scenarios the demand names are exercised in
§`check_recovery_semantics`:

- **Scenario 1 — Factory restarts after terminal retention expiry.** The purged record
  is simply gone, so the classification is the only thing between the restart and a
  duplicate write under a completed key: a key inside coverage must answer
  `operation_not_found`, a key older than the floor and a miss with no `reservedAt`
  must both answer `operation_lookup_out_of_coverage`, and each fixture's own
  provenance must classify consistently with its code. Only a conclusive miss is
  retryable.
- **Scenario 2 — a delayed vendor write.** Absence seen once *inside* the quiet window
  must not authorise a resend; absence proven *at* the quiet deadline must authorise
  the one resend; a resend authorised before the window closed, a resend with no
  recorded proof, and a resend after a read-back that saw the effect must all be
  refused. `BAD_OP_RESENT_BEFORE_QUIET` is deliberately schema-valid — that is the
  case the executable check exists to catch.

Schema-level negatives also cover the shapes directly: unwindowed absent read-back,
resend without proof, `uncertain` record that is purgeable, `confirmed` with no
retention, `uncertain` marked retryable, `uncertain` carrying a `tracker_unavailable`
error, a conclusive 404 with no provenance, a conclusive 404 that is not retryable, an
out-of-coverage error that is retryable or carries no `reason`, a coverage document
under 90 days or with a zero quiet window.

**Caller behaviour and producer changes are documented**, not just implied:
`docs/task-delivery.md` gained §Retention coverage and safe missing-operation recovery
(with the classification table and Factory's three-step behaviour on an inconclusive
miss), §Absence is not non-execution, §`uncertain` is not retryable, and §Producer
obligations added in v0.35.0 — four interface requirements for the `youtrack` service.

## The tag was re-pointed — disclosed

`v0.35.0` was first tagged at `e678d39`, then the D031 acceptance pass surfaced the
binding caveat (below). Because the tag was minutes old and no D043 demand had been
raised yet, i.e. no consumer could have seen it, I removed the tag (local and remote)
and its worktree, committed the caveat documentation as `d4b3ce3`, then re-tagged and
re-pushed so the tagged artifact is self-consistent. **`v0.35.0` now points at
`d4b3ce3`.** Nothing was ever consumed under the old commit. The worktree was
recreated and re-verified after.

## D031 acceptance (real tag, both legs)

- **Python:** a fresh venv, `pip install --no-cache-dir "platform-contracts @
  git+https://github.com/elmoul/contracts.git@v0.35.0#subdirectory=gen/python"` gives
  version 0.35.0. The binding round-trips the new fields, still loads a v0.34.0-shaped
  record, and the caveat below is asserted rather than assumed.
- **TypeScript:** a scratch npm project with a fresh cache installed
  `file:../contracts-worktrees/v0.35.0/gen/ts`; `tsc --strict --noEmit` passes when
  importing `DeliveryOperationCoverage` / `DeliverySyncOperation` / `DeliverySyncRequest`,
  and `dist/` carries the new type (which is what a consumer actually resolves).
- **Schema level:** 12 checks against a fresh clone at `--branch v0.35.0`, because the
  v0.35.0 rules live in `if/then` and the bindings do not implement it (below).

## What the origin must know

1. **The bindings do not enforce any of the v0.35.0 rules.** Neither
   `datamodel-codegen` nor `json-schema-to-typescript` implements `if`/`then`, so
   `DeliverySyncOperation` and `DeliverySyncRequest` **accept** an unwindowed absence
   and a resend without `absenceProvenAt`. This is not new, but v0.35.0 moved
   load-bearing rules into `if/then`, so it now matters. **Validate against the JSON
   Schema itself where these rules apply** (or re-implement them). Table in
   `docs/task-delivery.md` §Binding caveat.
2. **Send `reservedAt`.** Factory persists it with the reserved request and must send it
   on every lookup and every write. Without it the service can only answer
   `no_key_provenance`, so an omitted `reservedAt` degrades every miss to inconclusive.
3. **The two 404s mean opposite things.** `operation_not_found` (retryable) is the only
   answer that permits submitting the key. On `operation_lookup_out_of_coverage`,
   Factory must not resubmit and must not mint a replacement key as a reflex — the old
   write may be on the issue under the old marker. Read the issue for the operation's
   marker first; only if the write is genuinely absent, mint a **new** key, note the
   superseded one, and surface the inconclusive lookup in the waiting view rather than
   retrying on a timer.
4. **The work lands in `youtrack`, not Factory.** All four producer obligations are for
   the service that owns the operation store; every `/delivery/v1` route is still
   unimplemented and no service emits a `delivery.sync-operation` document yet, so
   **nothing is live because of this release**. The origin's own follow-up is the caller
   side plus raising the downstream producer demand.
5. **Additive release.** Per D031/D043 no consumer is obligated to move; the D043 origin
   demand `contracts-20260927-factory-repin-sync-recovery-retention` is raised
   `to: [factory]` in its own coordination commit. No fleet-wide bump.

## Not done / caveats

- **The installed Python package does not bundle the schemas.** `gen/python` ships only
  generated modules, so the advice "validate against the JSON Schema" is **not
  followable from a pip install** — a consumer must read the schema from a checkout or
  the pinned worktree. I did not fix this: it changes packaging and I judged it an owner
  call rather than a silent scope expansion of this demand. Proposed fix for the owner:
  ship `schemas/` inside the wheel (or a `platform_contracts.schemas` accessor) so each
  binding version carries the schema it was generated from. Filed here, not implemented.
- **`format: date-time` is inert repo-wide.** `jsonschema`'s `FormatChecker` has no
  `date-time` checker installed in this repo's test environment, so `format` never
  rejects a bad timestamp — a pre-existing gap, not introduced here. The new timestamp
  fields therefore carry `type` constraints (enforced) but their `format` is
  documentation. The new fixture is a type violation rather than a format violation for
  that reason. Worth a repo-wide decision; not fixed here.
- **The two `if/then` tightenings are conditional, not purely additive.** A record that
  was previously valid can now be invalid if it is `uncertain` with a retryable error, or
  carries an absence observation with no window. No consumer stores such records today
  (no service emits them at all), and the tightenings are stated plainly in the
  CHANGELOG, `docs/task-delivery.md` §Upgrade/repin and the origin demand — but they are
  tightenings and are named as such rather than folded into "additive".
- **No Java binding** for the delivery set, still: no Java producer or consumer exists.
  Unchanged from v0.31.0; one can be requested if plantpal's deploy receipt turns out to
  be Java.
- **Nothing here is implemented.** Every `/delivery/v1` route — including the new
  coverage route — remains unimplemented, and no runtime endpoint or dev delivery is live
  because of this release.
