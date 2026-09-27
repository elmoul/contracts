# D113 task delivery — contract reference (v0.35.0)

Published for demand `factory-20260927-task-delivery-contracts` (D113,
`factory/docs/YOUTRACK_DELIVERY.md` chunk 2). **This is an interface release, not a
running system.** No `/delivery/v1` route, no producer integration and no Planotell
dev deployment exists because of it; each owning service must implement and verify
its own side (see the handoff matrix).

Amended in **v0.35.0** for demand `factory-20260927-sync-recovery-retention`: a
lookup miss no longer authorises a resubmit on its own. The `youtrack` operation
store now states a coverage floor (`delivery.operation-coverage`), a by-key miss is
classified as conclusive (`operation_not_found`) or inconclusive
(`operation_lookup_out_of_coverage`), and an observed absence must be windowed
before it can justify a resend (`readBack.absentSince` / `absenceQuietUntil`,
`absenceProvenAt`, `vendorInFlightBoundSeconds`). §Retention coverage and
§Absence is not non-execution are the new rules; §Producers gained the four producer
obligations they imply. The `agent-runner` and `ci-runner` rows are unchanged from
v0.34.0, and nothing outside `schemas/delivery/` and the `youtrack` OpenAPI document
changed.

Amended in **v0.34.0** for demand `ci-runner-20260927-contracts-ci-headsha-lookup`:
the `ci-runner` side of §Producers closed its gap. `ci.run` gained an optional
`headSha`, `BuildResult` gained the same, and the `ci-runner` CI-result lookup
interface — one job by run id + job id, and every job for an exact
`(repository, revision)` — is published under `schemas/delivery-api/`, so a CI result
can finally be tied to an exact revision and re-fetched after a lost event. §CI result
routes and §Producers below state its shapes and status codes. The `agent-runner` rows
are unchanged from v0.33.0 and `delivery.*` is unchanged from v0.31.0.

Amended in **v0.33.0** for demand `agent-runner-20260927-contracts-runner-keyed-dispatch`:
the runner side of §Producers closed its gap. `schemas/agent-runner/*` gained an
optional `dispatchKey` on the request and the run record, an optional observed
`workspace` on the run record, and the new `runner.dispatch-reservation`; §Runner
routes and §Producers below now state its routes and status codes. Everything else
in this document — `delivery.*`, the `/delivery/v1` routes, the enforcement rules —
is unchanged from v0.31.0.

## Files

| Path | Kind | What it is |
|---|---|---|
| `schemas/delivery/delivery.issue-ref.json` | JSON Schema | Stable issue identity (`vendorId` binds, `idReadable` displays) |
| `schemas/delivery/delivery.issue.json` | JSON Schema | Issue snapshot: scope fingerprint, state, epic/subtasks, dependencies, delivery links |
| `schemas/delivery/delivery.issue-page.json` | JSON Schema | Paginated listing with `complete` / `unavailableProjects` |
| `schemas/delivery/delivery.workflow.json` | JSON Schema | Existing project workflow states (read-only) |
| `schemas/delivery/delivery.sync-request.json` | JSON Schema | One issue write: `link` / `comment` / `transition` / `resolve`; v0.35.0 adds optional `reservedAt` |
| `schemas/delivery/delivery.sync-operation.json` | JSON Schema | Durable operation record + read-back; v0.35.0 adds the absence window (`absentSince`/`absenceQuietUntil`), `absenceProvenAt`, `vendorInFlightBoundSeconds` |
| `schemas/delivery/delivery.operation-coverage.json` | JSON Schema | Lookup coverage floor + quiet-window bound; what a miss can and cannot prove (v0.35.0) |
| `schemas/delivery/delivery.error.json` | JSON Schema | Error payload + code/status table; v0.35.0 adds `operation_lookup_out_of_coverage` and `tracker_outcome_unknown` |
| `schemas/delivery/delivery.evidence.json` | JSON Schema | Stage-aware observation (successor to `factory.evidence-receipt` for new deliveries) |
| `schemas/delivery/delivery.decision.json` | JSON Schema | Plan approval / policy authorization / owner acceptance / request changes / abandon |
| `schemas/delivery/delivery.producer-result.json` | JSON Schema | Normalized runner / CI / app-deploy result |
| `schemas/delivery-api/youtrack-delivery.openapi.yaml` | OpenAPI 3.1 | `youtrack` service routes under `/delivery/v1` |
| `schemas/agent-runner/runner.dispatch-request.json` | JSON Schema | `POST /dispatch` body; v0.33.0 adds optional `dispatchKey` |
| `schemas/agent-runner/runner.run-record.json` | JSON Schema | Run record; v0.33.0 adds optional `dispatchKey` and observed `workspace` |
| `schemas/agent-runner/runner.dispatch-reservation.json` | JSON Schema | `GET /dispatches/{dispatchKey}` body + the `requestHash` canonicalization |
| `schemas/delivery-api/ci-runner-results.openapi.yaml` | OpenAPI 3.1 | `ci-runner` CI-result lookup routes under `/delivery/v1` (v0.34.0) |
| `schemas/ci-runner/build-result.yaml` | JSON Schema | `ci-runner` → control-plane build result; v0.34.0 adds optional `headSha` |
| `schemas/state-feed/state.event.json` | JSON Schema | `ci.run` payload; v0.34.0 adds optional `headSha` |
| `tests/validate_delivery.py` | test | 88 positive/negative fixtures + OpenAPI route checks (youtrack + ci-runner) + ci-runner component fixtures + Python binding round-trip + `check_recovery_semantics` (the two cross-field timestamp rules JSON Schema cannot express) |
| `tests/validate_runner.py` | test | Runner fixtures incl. the keyed/workspace/reservation cases + an executable `requestHash` conformance check |

Bindings: Python `platform_contracts.delivery.*` (`gen/python`), TypeScript
`delivery-*.ts` re-exported from `gen/ts/index.ts`. No Java binding for the
`delivery.*` shapes: no Java service produces or consumes them today (see §Producers
for `plantpal`). The `ci.run` / `BuildResult` shapes added in v0.34.0 **do** have
bindings in all three languages — `CiRunPayload` (Java `io.platform.contracts.events`,
`gen/ts/state-event.ts`, `gen/python`), and `BuildResult` (Java at build time,
`gen/ts/build-result.ts`, `gen/python`) — because `ci-runner` and `control-plane` are
Java services.

## Binding caveat — the v0.35.0 rules are NOT enforced by the generated bindings

Every recovery rule in this document that is written as an `if/then` conditional is
**inert in the generated Python and TypeScript bindings.** `datamodel-codegen` and
`json-schema-to-typescript` do not implement `if/then`, so they emit the fields as
plain optional properties. Verified against the v0.35.0 tag: `DeliverySyncOperation`
in a clean venv accepts an `uncertain` record with `readBack.effectPresent: false`
and *no* `absentSince`/`absenceQuietUntil`, and accepts `attempts: 2` with no
`absenceProvenAt` — both of which the JSON Schema rejects and both of which are
exactly the shapes that authorise repeating a possibly-completed write.

So, for any code that decides whether to resend:

| Rule | Enforced by the schema | Enforced by the bindings |
|---|---|---|
| `confirmed` requires `effectPresent: true` | yes | no |
| `effectPresent: false` requires `absentSince` + `absenceQuietUntil` | yes | **no** |
| `attempts >= 2` requires `absenceProvenAt` | yes | **no** |
| open records: `retainUntil` null; terminal records: present | yes | **no** |
| `rejected`/`failed`/`uncertain` carry a non-retryable `error` | yes | **no** |
| `operation_not_found` carries `reservedAt` + `coveredSince`, `retryable: true` | yes | **no** |
| `operation_lookup_out_of_coverage` carries `coveredSince` + `reason`, `retryable: false` | yes | **no** |
| `absenceProvenAt >= absenceQuietUntil` (cross-field arithmetic) | **no** — see below | no |

Two consequences a producer or consumer must act on:

1. **Validate against the JSON Schema, not the binding, wherever a resend decision
   is made.** `tests/validate_delivery.py` is the executable reference for the
   schema-level rules and `check_recovery_semantics` for the cross-field ones; port
   both rather than trusting a parsed model.
2. **The schemas are not bundled in the installed package.** `gen/python` ships
   `platform_contracts*` only, so a consumer pinned to a tag cannot read
   `schemas/delivery/*.json` from its install — it must fetch the same tag. Closing
   this (bundling the consumed schemas as package data, or generating a validator
   from them) is an open gap, recorded in the v0.35.0 fulfillment report, and is a
   packaging decision for the owner rather than something this release changed.

The `absenceProvenAt >= absenceQuietUntil` rule cannot be expressed as a JSON Schema
keyword at all (draft 2020-12 has no timestamp arithmetic), so it is enforced only
by `check_recovery_semantics` in `tests/validate_delivery.py` plus prose here. A
service can emit a document that validates and still means the wrong thing; that is
why the rule is stated as an explicit caller obligation in §Absence is not
non-execution rather than left implicit in the shapes.

## Boundary

- `youtrack` alone holds the YouTrack credential and performs every vendor call.
  Nothing in these shapes carries a vendor token; `DeliveryIssue` is a closed shape.
- The Factory→youtrack caller credential (OpenAPI `factoryCaller`) is a
  **service credential issued and verified by `youtrack`**, not a YouTrack token.
  The mechanism is the `youtrack` spec's choice. A free-text caller header is not
  authentication.
- Existing planner routes and `schemas/youtrack/planner.*` are unchanged.
  `schemas/factory/*` is unchanged. `schemas/agent-runner/*` gained only optional
  fields and one new schema in v0.33.0 — no existing required list changed, so every
  request and record that validated at v0.31.0 still validates byte-for-byte.

## Reads

- `GET /delivery/v1/issues/{vendorId}`: selected issue (Phase 1). Re-read before
  execution and before acceptance.
- `GET /delivery/v1/issues?project=PLA&openOnly=true&cursor=&limit=`: Phase 2 scan.
  **Absence proves nothing** unless the final page has `complete: true` and no page
  reported `unavailableProjects`.
- Dependencies are satisfied only when `dependenciesComplete` is `true` and every
  `depends-on` entry is `resolved`. `unknown`, a `null` linked issue, or
  `dependenciesComplete: false` means blocked/unknown, never satisfied.
- Non-empty `subtasks` = container (epic); not executable by itself.
- **Scope drift:** `scope.fingerprint` covers only owner-authored fields listed in
  `scope.fields`, and excludes state, comments, links and `updated`. Factory's own
  writes therefore never change it, and a changed fingerprint means an owner edit.
  Factory records the fingerprint in its plan decision (`scope.issueScope`).
- `GET /delivery/v1/projects/{project}/workflow`: existing states with the vendor's
  `resolved` flag. Stage→state mapping is Factory configuration reviewed by the owner.
  A stage with no state uses `comment`. Nothing creates workflow fields.

## Recovery: operation identity and lookup

Applies to every write (`PUT /delivery/v1/operations/{operationKey}`). It is also
the pattern Factory uses for its own dispatch, merge and deploy requests.

1. **Reserve first.** Factory mints `operationKey` and persists it with the full
   request before the first send. After a restart it looks the key up and does
   **not** mint a new one.
2. **Service reserves too.** `youtrack` stores the record (`reserved`, with
   `requestHash` = SHA-256 of the canonical request JSON) before calling the vendor.
3. **Same key + same body** returns the stored record (HTTP 200) with no second
   vendor write, whatever its status.
4. **Same key + different body** returns `409 operation_key_conflict`. The stored
   record is never overwritten.
5. **Preconditions** (`expectedScope`, `expectedState`, state mapping, resolvedness
   of the target, acceptance reference, vendor permission) are checked by re-reading
   the issue before any write. A failure is stored as `rejected` with the error, and
   nothing is written. `scope_changed` / `state_changed` / `state_unmapped` /
   `tracker_permission_denied` carry `ownerAction` for Factory's waiting view.
6. **Read-back.** After the vendor call the service re-reads the issue. The write is
   `confirmed` only when the read-back shows the effect: the comment or link carrying
   the key's marker, or the state equal to the target.
7. **Uncertain.** If the vendor call timed out, the connection dropped, or the vendor
   returned 5xx after the request was sent, and read-back cannot settle it, the status
   is `uncertain`. **The service never resends automatically from `uncertain`.** The
   error code is `tracker_outcome_unknown` (`retryable: false`) — not
   `tracker_unavailable`, which means the opposite fact (nothing was sent, retry is
   safe). `POST .../reconcile` re-reads the issue. If the effect is present the record
   becomes `confirmed`. Absence does **not** by itself authorise anything — see
   §Absence is not non-execution below. If the read-back fails, the record stays
   `uncertain`.
8. **Restart.** On start the service moves every `submitted` record to `uncertain`
   and reconciles it. Factory lists
   `GET /delivery/v1/operations?status=reserved&status=submitted&status=uncertain`
   and looks up its own reserved keys. A lookup **miss does not mean the request
   never arrived** — after terminal retention expires a completed write misses too.
   See §Retention coverage and safe missing-operation recovery.
9. **Retention.** Terminal records are kept at least 90 days (`retainUntil`).
   Open records (`reserved`/`submitted`/`uncertain`) are never purged at any age, so
   a lookup always answers while an outcome is still open. The schema enforces both
   halves: `retainUntil` must be `null` for an open record and present for a terminal
   one.
10. **No stronger claim.** This gives at most one *confirmed* effect per key, as far
    as read-back can observe. It is **not** a transaction with YouTrack and **not**
    exactly-once delivery. A vendor-side duplicate that read-back cannot distinguish
    is possible in principle. Comment/link markers make it detectable, and it is
    reported rather than hidden.
11. A sync failure blocks only that sync. It never re-runs implementation or
    deployment.

## Retention coverage and safe missing-operation recovery

**A lookup miss is not proof that a key was never used.** Terminal records are
purgeable after 90 days, so a miss can mean either *never stored* or *stored,
completed, and since purged*. Before v0.35.0 the second case was indistinguishable
from the first, and the doc told Factory a miss meant "the request never arrived, so
Factory may submit that key" — which, after a retention expiry, authorises a second
write under a key whose first write already landed.

The service now states what its store can answer, and classifies every miss.

### The coverage floor

`GET /delivery/v1/operations/coverage` returns `delivery.operation-coverage`:

- `coveredSince` — the coverage floor. Every record the service ever stored whose
  reservation time is at or after this instant is still retrievable; nothing at or
  after it has been purged. In the normal case this is `now - terminalRetentionDays`.
  The service must move it forward if it purges on any other schedule, and it never
  moves backward.
- `terminalRetentionDays` — the retention window (floor 90).
- `vendorInFlightBoundSeconds` — the quiet window for reconciliation (below).

### Classifying the miss

Factory supplies its key provenance — the time it minted the key — as `reservedAt`,
on the lookup (`GET /delivery/v1/operations/{operationKey}?reservedAt=...`) and in
the write body (`delivery.sync-request.reservedAt`). Factory persists it with the
reserved request, so it always has it. `reservedAt` is part of the hashed canonical
body: a replay must repeat it byte-for-byte or it is `operation_key_conflict`.

| Lookup result | Meaning | May Factory submit the key? |
|---|---|---|
| `200` + `delivery.sync-operation` | Found, any status | No — replaying the same body returns the record; never mint or resend around it |
| `404 operation_not_found` | Conclusive: never stored. Only returned when `reservedAt >= coveredSince`, and it always echoes `details.reservedAt`/`details.coveredSince` | **Yes** — `retryable: true`. No vendor write was ever made under this key |
| `404 operation_lookup_out_of_coverage` | **Inconclusive.** `reason: reserved_at_before_coverage` (key older than the floor: a terminal record for it may have been purged) or `reason: no_key_provenance` (no `reservedAt` supplied) | **No** — `retryable: false`. Resubmitting can duplicate a completed write |

Two rules make this hold rather than depend on good behaviour:

- The schema requires `details.reservedAt` and `details.coveredSince` on every
  `operation_not_found`, and pins `retryable: true`. A bare 404 can no longer be
  dressed up as conclusive — the service has to have had, and to show, the
  provenance it judged.
- Every `operation_lookup_out_of_coverage` must carry the floor and a `reason`, and
  is pinned `retryable: false`.

### Factory's behaviour on an inconclusive miss

Do **not** resubmit, and do not mint a replacement key as a reflex: a replacement
key is a new identity, and the old write may be on the issue under the old marker.
Instead:

1. Read the issue (`delivery.issue`) and look for this operation's marker — comment
   or link carrying the key, or the state the transition targeted. A present effect
   settles it: record it and stop.
2. If the write is genuinely absent, mint a **new** key, note the superseded key in
   the delivery record, and proceed. Do not reuse the old key: its provenance is
   what the service could not resolve.
3. Surface the inconclusive lookup in the waiting view (`ownerAction` is already on
   the error) rather than retrying on a timer. A retry loop against an inconclusive
   key is how a duplicate gets made.

### The write path is gated too

A lookup is not the only way to repeat a write — a re-`PUT` of the same key is
another. If the body's `reservedAt` is earlier than `coveredSince`, the service must
refuse with `operation_lookup_out_of_coverage` and write nothing, because it cannot
prove that key is fresh. When `reservedAt` is absent the service accepts the key as
a new reservation (the caller is asserting freshness) — which is exactly why Factory
should always send it.

## Absence is not non-execution

A vendor request that was already sent may still take effect *after* a read-back
shows it absent. One read-back observing no effect proves only that the effect was
absent at that instant — so it cannot authorise a resend, and v0.35.0 no longer lets
it look like it does:

- An `effectPresent: false` read-back now **must** carry `absentSince` (the earliest
  observation from which absence has been seen continuously) and
  `absenceQuietUntil` (= `absentSince` + `vendorInFlightBoundSeconds`). An unwindowed
  absence observation is not a valid record.
- Non-execution is established only when absence has held **from `absentSince`
  through `absenceQuietUntil`** (so a delayed original request can no longer land)
  **and** the vendor exposes no record of the request where it has such a lookup.
  When both hold the service sets `absenceProvenAt`.
- Only `absenceProvenAt` authorises a resend. `attempts >= 2` with a null or missing
  `absenceProvenAt` is invalid by schema, so every resend is auditable back to the
  absence that justified it.
- If presence is observed at any point in the window, or a read-back fails, the
  window resets and the record stays `uncertain`. **Uncertainty is preserved rather
  than resolved by assumption** — an `uncertain` record is never purged, so it stays
  visible and reconciled indefinitely.

The timestamps are the contract; the ordering between them (`absenceProvenAt >=
absenceQuietUntil`, and the window running forward from `absentSince`) is arithmetic
that JSON Schema cannot express, so it is enforced by `tests/validate_delivery.py`
§`check_recovery_semantics` instead of by a keyword. A service implementing this
without those checks can still emit a doc that validates and means the wrong thing.

### `uncertain` is not retryable

The error on an `uncertain` record must be `tracker_outcome_unknown` with
`retryable: false`, and the schema enforces it. `tracker_unavailable` — pinned
`retryable: true` — describes the opposite situation (the vendor was unreachable
*before* any write was sent) and must not be used to report a post-send timeout.

## Resolve enforcement (the schema is necessary, not sufficient)

`DeliverySyncRequest` with `payload.kind: resolve` structurally requires an
`acceptance` reference whose `kind` is `owner-acceptance` and whose `basis` is
`owner`. Policy authorization, ready-for-test, worker exit and coordinator approval
cannot be encoded in it (see negative fixtures). A schema cannot authenticate an
owner, so:

- **Factory** must create `delivery.decision` records with `basis: owner` only from
  an authenticated owner action in its own UI, never from a policy, an agent, a
  coordinator verdict or an import. Policy decisions are `policy-authorization` /
  `basis: policy` with a `policy` reference.
- **youtrack** must: authenticate the Factory boundary (`caller_not_authorized`);
  require a non-null `expectedScope` equal to the live fingerprint; require the target
  state to be `resolved: true` and every `transition` target to be `resolved: false`;
  require `acceptance.candidateRevision == correlation.candidateRevision`.
- **Required negative integration tests** (in `youtrack`): a resolve with no
  acceptance, with a policy/ready-for-test/coordinator reference, with a stale scope,
  from an unauthenticated caller, and a `transition` to a resolved state are all
  rejected with nothing written. A replayed resolve key writes once. A timeout
  followed by reconcile never produces two transitions.
- `youtrack` cannot verify Factory's decision store. The acceptance reference is
  Factory's signed-by-hash claim (`decisionHash`), and trust rests on the
  authenticated Factory boundary. A stronger cross-check, such as `youtrack` fetching
  the decision from Factory, is a possible later addition and is not required here.

## Evidence and decisions

- **Observations** (`delivery.evidence`) and **authorizations/acceptance**
  (`delivery.decision`) are different record types. `basis` on evidence is
  `machine-observation` (requires `source.recordRef`), `worker-claim` (a report or
  transcript statement; a source claim only, and it can never pass a gate) or
  `owner-attestation`.
- `result` is `passed | failed | unknown | unavailable`, and only `passed` passes.
  `exitCode: null` means not reported, never 0.
- **Stage order:** `implementation`, `tests`, `ci`, `security`, `quality`, `merge`
  come before deployment; `deployment` and `live` come after. Each criterion carries
  `evaluableAt`, so deployment-only criteria do not block pre-deploy checks and cannot
  be satisfied by them.
- **Revisions** are full 40-hex SHAs. `revisionRole: task` evidence can never prove a
  `merged` SHA. `merge`/`deployment`/`live` must be `merged`. `deployment`/`live`
  require `environment` with `name: dev`, the running app's reported `appIdentity`,
  `deploymentId` and `deployedRevision`. Factory must record `failed` when
  `deployedRevision != revision`; that cross-field equality is enforced by Factory,
  not by the schema.
- Scope binding: every record carries `planHash` + `issueScope`. A changed issue scope
  or plan invalidates the evidence and decisions bound to the old values (Factory rule).
- **Separate facts, never acceptance:** agent exit, report approval, coordinator
  approval and issue sync. Only a `delivery.decision` of kind `owner-acceptance`
  (candidate + deployment + at least one evidence hash) can back a `resolve`.

### Historical receipts and compatibility

- `factory.evidence-receipt` (v0.25.0) is **unchanged**. Its
  `provenance: owner-attestation` const and `passed|failed` result stay exactly as
  they were, so every stored receipt still validates and keeps its bytes and `hash`.
- New deliveries write `delivery.evidence`. To show a legacy receipt in the new view,
  Factory may derive a new record with `basis: owner-attestation` and
  `legacyReceipt: {id, hash}` copied verbatim. The legacy record is never rewritten
  or rehashed, and no default is back-filled into it.
- `factory.outcome`, `factory.continuation` and `factory.recovery-checkpoint` are
  unchanged. A D113 delivery can reuse `factory.outcome.id` as `deliveryId`.
  `approvals[]` stays the legacy record, and new decisions go to `delivery.decision`.
- The cancelled PlantPal pilot and its legacy records are not migrated.

## Runner routes: keyed dispatch, dispatch lookup, producer result

Added in v0.33.0 (demand `agent-runner-20260927-contracts-runner-keyed-dispatch`).
`agent-runner` implements these; the schemas fix the shapes and the status codes.
Language is `agent-runner`'s choice — these are HTTP routes, not an OpenAPI document.

| Route | Request / response body | Codes |
|---|---|---|
| `POST /dispatch` | `runner.dispatch-request` → `runner.run-record` | `202` new run started · `200` **replay** (key already reserved, identical `requestHash`; the existing run record, no second process) · `409` **conflicting reuse** (key reserved, different `requestHash`; nothing started, stored reservation never overwritten) · `409` repo locked · `429` concurrency cap |
| `GET /dispatches/{dispatchKey}` | → `runner.dispatch-reservation` | `200` reservation + the run it is bound to · `404` this runner never committed a reservation for the key |
| `GET /runs/{id}/producer-result` | → `delivery.producer-result` | `200` · `404` no such run |
| `GET /dispatches/{dispatchKey}/producer-result` | → `delivery.producer-result` | `200` · `404` no reservation for the key |

**Reserve before spawn.** The runner writes the reservation — key, `requestHash`, minted
`runId` — durably **before** any process starts. That ordering is the whole mechanism:
it is what makes `GET /dispatches/{key}` meaningful, and it is why an identical retry
can be answered from the ledger instead of guessed at.

**`requestHash`.** SHA-256 over a canonical JSON of the execution-defining request
fields `repo`, `prompt`, `demandId`, `model`, `effort`, `runtime` — absent fields
omitted, never nulled; `dispatchKey` itself excluded. `runner.dispatch-reservation.json`
fixes the exact canonicalization and carries a worked example;
`tests/validate_runner.py` recomputes that example, so the prose cannot drift from a
form a caller can actually reproduce. A caller and the runner that disagree on this
hash will see every replay as a conflict.

**Conflict is not a retry.** `409` on a keyed dispatch means *this key is already
bound to a different execution*. Mint a new key for a new execution; do not "fix" the
body and resend under the same key.

**`404` on the lookup is safe to resend against.** It means no reservation was ever
committed for that key, so the request never arrived or was rejected before reserving.
It is **not** proof that no run happened under some other key, and never proof that
nothing was written to the repo.

**Lock and cap come first.** The repo lock and the concurrency cap are applied as
today, *before* the reservation is written. A `409 repo locked` or a `429` cap
rejection therefore reserves nothing, so the same key remains usable for the same
intended execution later. Neither is a conflicting reuse.

**Uncertain dispatch — the no-relaunch rule.** The runner may restart after committing
a reservation but before a settled outcome. The key then stays bound to that run: the
orphan reconciler settles it `failed` with `exitCode: null`, which maps to a producer
`outcome: unknown` — not `failed`, because `exitCode: null` means *not reported*, never
0 (D113 §Evidence and decisions). **The runner never relaunches it automatically**,
because it cannot prove the first process did not already do the work. A caller that
decides a retry is warranted mints a **new** key; reusing the old one replays or
conflicts, it never re-runs.

**Producer-result lookups.** `GET /runs/{id}/producer-result` and
`GET /dispatches/{dispatchKey}/producer-result` are `agent-runner`'s delivery.producer-result
lookups. Both return the same shape; `correlation.operationKey` is the run's
`dispatchKey` when it has one and `null` otherwise. `repository`, `branch` and
`revision` come from the run record's observed `workspace`, never from the agent's
report — and `revision` is the post-exit `HEAD` **only when `dirty` is `false`**, so a
dirty (or unobservable) tree yields a `null` revision, which can never pass a revision
gate. `outcome` is `pending` while `state` is `launched`, `passed` for `finished`+exit
0, `failed` for `failed`, and `unknown` for `stopped` or a null exit code.

**Unkeyed dispatch is unchanged.** Omitting `dispatchKey` keeps today's behaviour
exactly, including the prompt-first-line token scan for correlation. That scan is
strictly weaker than a keyed lookup; it is the fallback for callers that cannot mint a
key, not a substitute for one.

## CI result routes: revision-tied lookup

Added in v0.34.0 (demand `ci-runner-20260927-contracts-ci-headsha-lookup`).
Published as OpenAPI 3.1 in `schemas/delivery-api/ci-runner-results.openapi.yaml`,
because unlike the runner routes these return `delivery.*` JSON Schema shapes that
`factory` (Python) and `control-plane` (Java) both read; the document fixes the
shapes, the codes and the not-found body. `ci-runner` implements them.

| Route | Request / response body | Codes |
|---|---|---|
| `GET /delivery/v1/ci-results/{runId}/{jobId}` | → `delivery.producer-result` | `200` · `404` `ci_result_not_found` (no record of that job) · `422` bad id · `503` `producer_unavailable` (store unreachable, retryable) |
| `GET /delivery/v1/ci-results?repository={p}&revision={sha40}` | → `{repository, revision, items[]}` of `delivery.producer-result` | `200` (possibly empty `items`) · `422` bad pattern · `503` `producer_unavailable` |

**Identity.** `operationId` is `<runId>/<jobId>` and `nativeRef` is
`ci-runner:ci.run/<runId>/<jobId>`, using the GitHub numeric ids already carried on
`ci.run`. That makes the lookup a direct read of the same identity the event
announces, so a result lost to a restart is recoverable from the ids Factory already
recorded — no prompt scan, no re-run.

**`revision` is `headSha`, never `ref`.** `ref` is a moving name; only the 40-hex
`headSha` names a revision. A job whose `headSha` `ci-runner` never observed is
returned with `revision: null` — absent, never guessed from `ref`, never defaulted.
A `null` revision cannot pass a revision gate, which is the point: the lookup must not
manufacture the correlation the event failed to carry. `BuildResult` (the
`ci-runner` → `control-plane` channel) carries the same optional `headSha` for the
same reason.

**Empty is not passed.** The by-revision listing matches `repository` + the full
40-hex `revision` exactly — no prefix, no branch matching. An empty `items` array is a
normal `200` meaning *no job is known for this revision*, and Factory must record that
as missing evidence (`unknown`), never as `passed`. Likewise `404
ci_result_not_found` on the by-id lookup is a statement about `ci-runner`'s record,
not a verdict about the build: the job may have run and failed, or never have run.

**Additive.** `headSha` is optional on both `CiRunPayload` and `BuildResult`, so every
`ci.run` fixture and every `BuildResult` that validated at v0.30.0 still validates
byte-for-byte.

## Producers

| Producer | Native record today | Maps to `delivery.producer-result` | Gap (addition needed by the owner, not made here) |
|---|---|---|---|
| `agent-runner` (TS) | `runner.run-record` (`GET /runs/{id}`): `state`, nullable `exitCode`, `transcriptPath`, optional `dispatchKey`, optional observed `workspace` | `operationId`=run id, `nativeRef`=`agent-runner:runs/<id>`, `repository`=run `repo`, `branch`/`revision` from `workspace` (`revision` only when `dirty` is `false`, else `null`), `correlation.operationKey`=`dispatchKey` or `null`, `exitCode` as-is, `finished`+0 → passed, `failed` → failed, `stopped`/null exit → unknown, `launched` → pending. Served at `GET /runs/{id}/producer-result` and `GET /dispatches/{dispatchKey}/producer-result` | **Closed in v0.33.0** — the record now carries the observed revision + branch and the dispatch key, and keys are reserved with a lookup, so a lost `POST /dispatch` response resolves without a prompt scan. Still the owner's work: implementing reservation/replay/conflict and the lookups on top of the shipped observation. A transcript's claims remain `worker-claim` only. |
| `ci-runner` | `ci.run` state event (`runId`, `jobId`, `ref`, `conclusion`, `steps[]`, `headSha`), `BuildResult` | `operationId`=`<runId>/<jobId>`, `nativeRef`=`ci-runner:ci.run/<runId>/<jobId>`, `repository`=platform repo name, `revision`=`headSha` (or `null` when never observed — never guessed from `ref`), `branch`=`ref`, `conclusion` success → passed, failure/timed_out → failed, cancelled/absent → unknown; `checks[]` from `steps[]` (step exit codes are not reported, so `null`). Served at `GET /delivery/v1/ci-results/{runId}/{jobId}` and `GET /delivery/v1/ci-results?repository=&revision=`. | **Closed in v0.34.0** at the interface level — `headSha` is on `CiRunPayload` and `BuildResult` (both optional/additive) and the lookup routes are published in `schemas/delivery-api/ci-runner-results.openapi.yaml`, so a run can be tied to an exact revision and re-fetched. Still the owner's work: emitting `headSha` from the GitHub webhook *and* implementing both lookup routes. Until `ci-runner` populates `headSha`, every result maps to `revision: null` and cannot pass a revision gate. |
| `app-deploy` (`plantpal`; routing by `runtime`/`gateway`, name proxy by `launcher`) | none. `app.health` has no revision or deployment id | `producer: app-deploy`, `environment` from the running app, `checks[]` = criterion smoke checks | Needs: a dev deployment receipt (deployment id, merged revision, image digest, result) with lookup, and a running-app identity/revision endpoint so `appIdentity`/`deployedRevision` are observed, not configured. Language is the owner's choice. A Java binding will be generated on request. |

Factory correlates by (`repository`, `revision`, producer `operationId`, and
`correlation.operationKey` when echoed). A result that cannot be correlated, has a
`null` revision, or whose native record cannot be re-fetched is recorded as
`unknown`, never `passed`.

### Producer obligations added in v0.35.0 (`youtrack` service)

This release adds no new producer and no new consumer, but it adds four things the
`youtrack` service must do when it implements the operation store. All four are
interface requirements, not implementation choices:

1. **Serve `GET /delivery/v1/operations/coverage`** and keep `coveredSince` honest —
   at or after the store's start, moved forward to cover anything actually purged on
   a different schedule, never backward.
2. **Classify every by-key miss.** `operation_not_found` only with a caller-supplied
   `reservedAt` at or after `coveredSince`; otherwise
   `operation_lookup_out_of_coverage`. Never return a bare conclusive-looking 404.
3. **Gate the write path** on `delivery.sync-request.reservedAt` — refuse a PUT whose
   `reservedAt` predates `coveredSince`, writing nothing.
4. **Window every absence observation.** Populate `readBack.absentSince` and
   `readBack.absenceQuietUntil`, refuse to resend before the window closes, set
   `absenceProvenAt` only when non-execution is actually established, and never mark
   an `uncertain` record's error `retryable`.

Nothing is live because of this release: every `/delivery/v1` route remains
unimplemented, and no service emits a `delivery.sync-operation` document yet.

Obligation 4 is the one that does not survive the generated bindings — see
§Binding caveat before implementing it. A service that creates its operation records
through `DeliverySyncOperation` and never validates them against
`schemas/delivery/delivery.sync-operation.json` will emit the unsafe shapes happily.

## Handoff matrix

| Interface | Producer | Consumer | Reference | Operation identity / recovery | Status at v0.35.0 |
|---|---|---|---|---|---|
| Issue read / list | `youtrack` | `factory` | `delivery.issue`, `delivery.issue-page`; `GET /delivery/v1/issues[/{vendorId}]` | n/a (reads); `complete` + `unavailableProjects` | **Unimplemented** (demand to `youtrack`) |
| Workflow metadata | `youtrack` | `factory` | `delivery.workflow`; `GET /delivery/v1/projects/{p}/workflow` | n/a | **Unimplemented** |
| Link / comment / transition / resolve | `youtrack` | `factory` | `delivery.sync-request` → `delivery.sync-operation`; `PUT/GET /delivery/v1/operations/{key}`, `POST .../reconcile`, `GET /delivery/v1/operations` | `operationKey` + `requestHash`; read-back; reconcile over a quiet window | **Unimplemented** |
| Operation lookup coverage | `youtrack` | `factory` | `delivery.operation-coverage`; `GET /delivery/v1/operations/coverage` | `coveredSince` + caller `reservedAt` classify a miss | Contract published in v0.35.0; **unimplemented** |
| Operation lookup miss | `youtrack` | `factory` | `delivery.error` with `operation_not_found` (conclusive, retryable) or `operation_lookup_out_of_coverage` (inconclusive, never retryable) | `details.reservedAt`/`coveredSince`/`reason` | Contract published in v0.35.0; **unimplemented** |
| Errors | `youtrack` | `factory` | `delivery.error` | `retryable`, `ownerAction` | **Unimplemented** |
| Evidence records | `factory` | `factory` (store/UI), later `dashboard` | `delivery.evidence` | `id` + `hash`, `supersedes` | **Unimplemented** (Factory chunk 3/4) |
| Decisions | `factory` | `factory`; `youtrack` (via `acceptance` ref) | `delivery.decision` | `id` + `hash` = `decisionId`/`decisionHash` | **Unimplemented** |
| Runner result | `agent-runner` | `factory` | `delivery.producer-result` ← `runner.run-record`; `GET /runs/{id}/producer-result`, `GET /dispatches/{dispatchKey}/producer-result` | run id; `dispatchKey` + observed `workspace` now on the record (v0.33.0) | Contract published; **lookup routes and mapping unimplemented** (agent-runner) |
| Runner dispatch + keyed lookup | `agent-runner` | `factory` | `runner.dispatch-request` (optional `dispatchKey`) → `runner.run-record`; `GET /dispatches/{dispatchKey}` → `runner.dispatch-reservation` | `dispatchKey` + `requestHash`; reserve-before-spawn; replay `200` / conflict `409`; no relaunch | Contract published in v0.33.0; **unimplemented** (agent-runner) |
| CI result | `ci-runner` | `factory` | `delivery.producer-result` ← `ci.run`; `GET /delivery/v1/ci-results/{runId}/{jobId}`, `GET /delivery/v1/ci-results?repository=&revision=` | `runId/jobId`; `revision` = `headSha` (on the event and on the lookup response, v0.34.0) | Contract published in v0.34.0; **emitting `headSha` and both lookup routes unimplemented** (ci-runner) |
| Dev deploy result | `plantpal` (+ `runtime`/`gateway`/`launcher`) | `factory` | `delivery.producer-result` (`environment`) | deployment id; **gap:** no receipt exists | **Unimplemented**; Planotell dev URL not verified |
| Routing/approval | `demand-coordinator` | `factory` | existing `demand` / `demand.fulfillment` | existing | Unchanged; not in this release |

## Upgrade / repin

### v0.35.0 (operation retention coverage + safe missing-operation recovery)

Additive, with one narrow conditional tightening (below). No consumer is obligated
to move (D031); the only repo with a leg here is `youtrack`, whose routes are
unimplemented, so this release's obligations land when that work is done. Nothing
in `factory.*`, `agent_runner.*`, `ci_runner.*` or the planner shapes changed.

- **Python (`factory`, `youtrack`):**
  `platform-contracts @ git+https://github.com/elmoul/contracts.git@v0.35.0#subdirectory=gen/python`.
  `platform_contracts.delivery` gains `delivery_operation_coverage`
  (`DeliveryOperationCoverage`); `delivery_sync_operation` gains `absenceProvenAt`,
  `vendorInFlightBoundSeconds` and the two `DeliveryReadBack` fields
  (`absentSince`, `absenceQuietUntil`); `delivery_sync_request` gains `reservedAt`.
- **TypeScript:** point the `file:` dependency at
  `../contracts-worktrees/v0.35.0/gen/ts`. `index.ts` re-exports the new
  `DeliveryOperationCoverage`. `DeliveryError` changed from an `interface` to a
  `type` alias (it gained `allOf`), which is source-compatible for every use.
- **Java:** no change — there is still no Java delivery binding, because no Java
  producer or consumer exists. Request one if `plantpal`'s deploy receipt lands in
  Java.
- **Compatibility checks after repin:** run your existing contract tests, then
  round-trip `GOOD_OP_ABSENT_IN_WINDOW`, `GOOD_OP_RESENT_AFTER_QUIET`,
  `GOOD_COVERAGE`, `ERR_OPERATION_NOT_FOUND` and `ERR_LOOKUP_OUT_OF_COVERAGE` from
  `tests/validate_delivery.py` through your binding. Confirm a v0.34.0-valid
  `delivery.sync-operation` **without** the new fields still validates — that is the
  criterion the additive claim rests on.
- **The conditional tightening, stated plainly:** two shapes that used to validate
  no longer do. (a) `attempts >= 2` now requires a non-null `absenceProvenAt`;
  (b) `readBack.effectPresent: false` now requires `absentSince` and
  `absenceQuietUntil`. Both are the shapes that let a caller repeat a
  possibly-completed write, both are written as `if/then` conditionals rather than
  as new entries in a `required` list (the same pattern `delivery.sync-request`'s
  `expectedScope` already uses), and no producer or stored document uses either —
  every `/delivery/v1` route is unimplemented and no delivery binding has ever been
  adopted by a consumer. If your own store already holds documents in those shapes,
  they need the fields added, not a migration of meaning.
- **Also tightened, same class:** an `uncertain`/`reserved`/`submitted` record may no
  longer carry a non-null `retainUntil`, a `confirmed`/`rejected`/`failed` record
  must carry one, an `uncertain` record's `error.retryable` must be `false`, and
  `tracker_unavailable` must be `retryable: true` (so a post-send timeout must be
  reported as `tracker_outcome_unknown`, a new code in this release).

### v0.34.0 (CI headSha + CI-result lookup)

Additive: no existing required list changed and no consumer is obligated to move
(D031). Only `ci-runner` needs to, and only `ci-runner`'s leg is open.

- **TypeScript (`ci-runner`, if it reads the shapes from TS):** point the `file:`
  dependency at `../contracts-worktrees/v0.34.0/gen/ts`. `BuildResult` (in
  `build-result.ts`) and `CiRunPayload` (in `state-event.ts`) each gain an optional
  `headSha?: string`. The generated `CiRunStep` / `CiRunPayload` types are otherwise
  unchanged.
- **Java (`ci-runner`, `control-plane`):** `io.platform:contracts:0.34.0` from a
  local `mvn install` at the tag. `CiRunPayload` gains a nullable `headSha` with the
  usual `JSON_PROPERTY_HEAD_SHA` constant; `BuildResult` is generated at build time
  from `schemas/ci-runner/build-result.yaml` and gains the same.
- **Python (`factory`):**
  `platform-contracts @ git+https://github.com/elmoul/contracts.git@v0.34.0#subdirectory=gen/python`.
  `state_feed.state_event` and `ci_runner.build_result` gain the optional field.
- **New file to read:** `schemas/delivery-api/ci-runner-results.openapi.yaml` — the
  two lookup routes and their not-found body. This is what `ci-runner` implements
  against; nothing in it is live until `ci-runner` ships it.
- **Compatibility checks after repin:** `tests/validate_delivery.py`'s
  `GOOD_PRODUCER_CI_PASSED` and `tests/validate_state_event.py`'s
  `GOOD_CI_RUN_WITH_HEAD_SHA` are the positive fixtures to round-trip through your
  binding. Re-check that a `ci.run` payload **without** `headSha` still validates
  unchanged — that is the criterion the additive claim rests on.

### v0.33.0 (runner keyed dispatch + observed workspace)

Additive: no existing required list changed and no consumer is obligated to move
(D031). Only `agent-runner` needs to.

- **TypeScript (agent-runner):** point the `file:` dependency at
  `../contracts-worktrees/v0.33.0/gen/ts` and import `RunnerDispatchRequest`,
  `RunnerRunRecord`, `RunnerDispatchReservation` (plus `RunnerRunWorkspace`) from
  `@platform/contracts`. **The runner schemas had no TS binding before v0.33.0** —
  they were published as JSON Schema only, so `gen/ts` gains
  `runner-dispatch-request.ts`, `runner-run-record.ts` and
  `runner-dispatch-reservation.ts` in this release. That was the blocker on repinning
  to `gen/ts` at all, and it is why this release is not Python-only.
- **Python:** `platform-contracts @ git+https://github.com/elmoul/contracts.git@v0.33.0#subdirectory=gen/python`
  if you validate runner shapes from Python (Factory does, to reconcile). The
  `agent_runner.*` models gain the new optional fields; everything else is unchanged.
- **Compatibility checks after repin:** run your existing contract tests, then
  round-trip the new fixtures (`GOOD_DISPATCH_REQUEST_KEYED`,
  `GOOD_RUN_RECORD_WITH_WORKSPACE`, `GOOD_DISPATCH_RESERVATION` in
  `tests/validate_runner.py`) through your binding. Re-check that an unkeyed
  `POST /dispatch` body still validates unchanged — that is the criterion the
  additive claim rests on.

### v0.31.0 (delivery interfaces)

Additive release: no existing schema, class or type changed, and no consumer is
obligated to move (D031).

- **Python (factory, youtrack):**
  `platform-contracts @ git+https://github.com/elmoul/contracts.git@v0.31.0#subdirectory=gen/python`,
  then `from platform_contracts.delivery.delivery_sync_request import DeliverySyncRequest`
  (etc.). Factory moves from v0.25.0. Everything it imports from `factory.*` and
  `agent_runner.*` is byte-identical in shape. Enum classes in the new modules are
  `StrEnum`, which needs Python ≥ 3.11 (already the package floor).
- **TypeScript (agent-runner):** point the `file:` dependency at
  `../contracts-worktrees/v0.31.0/gen/ts` and import `DeliveryProducerResult` etc.
  from `@platform/contracts`.
- **Compatibility checks after repin:** run your existing contract tests plus a
  round-trip of one positive fixture from `tests/validate_delivery.py` through your
  binding. Factory should additionally confirm its stored v0.25.0 receipts still load
  unchanged.
- **Rollout order:** schema shapes are closed (`additionalProperties: false`). Build
  the service side (`youtrack`) and the consumer (`factory`) against the same tag.
