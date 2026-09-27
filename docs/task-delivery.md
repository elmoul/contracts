# D113 task delivery — contract reference (v0.31.0)

Published for demand `factory-20260927-task-delivery-contracts` (D113,
`factory/docs/YOUTRACK_DELIVERY.md` chunk 2). **This is an interface release, not a
running system.** No `/delivery/v1` route, no producer integration and no Planotell
dev deployment exists because of it; each owning service must implement and verify
its own side (see the handoff matrix).

## Files

| Path | Kind | What it is |
|---|---|---|
| `schemas/delivery/delivery.issue-ref.json` | JSON Schema | Stable issue identity (`vendorId` binds, `idReadable` displays) |
| `schemas/delivery/delivery.issue.json` | JSON Schema | Issue snapshot: scope fingerprint, state, epic/subtasks, dependencies, delivery links |
| `schemas/delivery/delivery.issue-page.json` | JSON Schema | Paginated listing with `complete` / `unavailableProjects` |
| `schemas/delivery/delivery.workflow.json` | JSON Schema | Existing project workflow states (read-only) |
| `schemas/delivery/delivery.sync-request.json` | JSON Schema | One issue write: `link` / `comment` / `transition` / `resolve` |
| `schemas/delivery/delivery.sync-operation.json` | JSON Schema | Durable operation record + read-back |
| `schemas/delivery/delivery.error.json` | JSON Schema | Error payload + code/status table |
| `schemas/delivery/delivery.evidence.json` | JSON Schema | Stage-aware observation (successor to `factory.evidence-receipt` for new deliveries) |
| `schemas/delivery/delivery.decision.json` | JSON Schema | Plan approval / policy authorization / owner acceptance / request changes / abandon |
| `schemas/delivery/delivery.producer-result.json` | JSON Schema | Normalized runner / CI / app-deploy result |
| `schemas/delivery-api/youtrack-delivery.openapi.yaml` | OpenAPI 3.1 | `youtrack` service routes under `/delivery/v1` |
| `tests/validate_delivery.py` | test | 62 positive/negative fixtures + OpenAPI route check + Python binding round-trip |

Bindings: Python `platform_contracts.delivery.*` (`gen/python`), TypeScript
`delivery-*.ts` re-exported from `gen/ts/index.ts`. No Java binding: no Java service
produces or consumes these shapes today (see §Producers for `plantpal`).

## Boundary

- `youtrack` alone holds the YouTrack credential and performs every vendor call.
  Nothing in these shapes carries a vendor token; `DeliveryIssue` is a closed shape.
- The Factory→youtrack caller credential (OpenAPI `factoryCaller`) is a
  **service credential issued and verified by `youtrack`**, not a YouTrack token.
  The mechanism is the `youtrack` spec's choice. A free-text caller header is not
  authentication.
- Existing planner routes and `schemas/youtrack/planner.*` are unchanged.
  `schemas/factory/*` and `schemas/agent-runner/*` are unchanged.

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
   is `uncertain`. **The service never resends automatically from `uncertain`.**
   `POST .../reconcile` re-reads the issue. If the effect is present the record
   becomes `confirmed`. If it is proven absent, the service may resend the same
   stored request once (`attempts` +1) and read back again. If the read-back fails,
   the record stays `uncertain`.
8. **Restart.** On start the service moves every `submitted` record to `uncertain`
   and reconciles it. Factory lists
   `GET /delivery/v1/operations?status=reserved&status=submitted&status=uncertain`
   and looks up its own reserved keys. `operation_not_found` means the request never
   arrived, so Factory may submit that key.
9. **Retention.** Terminal records are kept at least 90 days (`retainUntil`).
   Open records (`reserved`/`submitted`/`uncertain`) are never purged.
10. **No stronger claim.** This gives at most one *confirmed* effect per key, as far
    as read-back can observe. It is **not** a transaction with YouTrack and **not**
    exactly-once delivery. A vendor-side duplicate that read-back cannot distinguish
    is possible in principle. Comment/link markers make it detectable, and it is
    reported rather than hidden.
11. A sync failure blocks only that sync. It never re-runs implementation or
    deployment.

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

## Producers

| Producer | Native record today | Maps to `delivery.producer-result` | Gap (addition needed by the owner, not made here) |
|---|---|---|---|
| `agent-runner` (TS) | `runner.run-record` (`GET /runs/{id}`): `state`, nullable `exitCode`, `transcriptPath` | `operationId`=run id, `nativeRef`=`agent-runner:runs/<id>`, `exitCode` as-is, `finished`+0 → passed, `failed` → failed, `stopped`/null exit → unknown, `launched` → pending | No revision (commit SHA) the run produced, no branch, and no echo of a Factory operation key or idempotent dispatch key, so a lost `POST /dispatch` response cannot be looked up. Needs: head revision + branch on the run record, and a client-supplied dispatch key with lookup. A transcript's claims are `worker-claim` only. |
| `ci-runner` | `ci.run` state event (`runId`, `jobId`, `ref`, `conclusion`, `steps[]`), `BuildResult` | `operationId`=`<runId>/<jobId>`, `nativeRef`=`ci-runner:ci.run/<runId>/<jobId>`, `conclusion` success → passed, failure/timed_out → failed, cancelled/absent → unknown; `checks[]` from `steps[]` (step exit codes are not reported, so `null`) | No head SHA (only `ref`), so a run cannot be tied to an exact revision. Needs: `headSha` on `CiRunPayload`/`BuildResult` (additive), plus a lookup by run/job id. |
| `app-deploy` (`plantpal`; routing by `runtime`/`gateway`, name proxy by `launcher`) | none. `app.health` has no revision or deployment id | `producer: app-deploy`, `environment` from the running app, `checks[]` = criterion smoke checks | Needs: a dev deployment receipt (deployment id, merged revision, image digest, result) with lookup, and a running-app identity/revision endpoint so `appIdentity`/`deployedRevision` are observed, not configured. Language is the owner's choice. A Java binding will be generated on request. |

Factory correlates by (`repository`, `revision`, producer `operationId`, and
`correlation.operationKey` when echoed). A result that cannot be correlated, has a
`null` revision, or whose native record cannot be re-fetched is recorded as
`unknown`, never `passed`.

## Handoff matrix

| Interface | Producer | Consumer | Reference | Operation identity / recovery | Status at v0.31.0 |
|---|---|---|---|---|---|
| Issue read / list | `youtrack` | `factory` | `delivery.issue`, `delivery.issue-page`; `GET /delivery/v1/issues[/{vendorId}]` | n/a (reads); `complete` + `unavailableProjects` | **Unimplemented** (demand to `youtrack`) |
| Workflow metadata | `youtrack` | `factory` | `delivery.workflow`; `GET /delivery/v1/projects/{p}/workflow` | n/a | **Unimplemented** |
| Link / comment / transition / resolve | `youtrack` | `factory` | `delivery.sync-request` → `delivery.sync-operation`; `PUT/GET /delivery/v1/operations/{key}`, `POST .../reconcile`, `GET /delivery/v1/operations` | `operationKey` + `requestHash`; read-back; reconcile | **Unimplemented** |
| Errors | `youtrack` | `factory` | `delivery.error` | `retryable`, `ownerAction` | **Unimplemented** |
| Evidence records | `factory` | `factory` (store/UI), later `dashboard` | `delivery.evidence` | `id` + `hash`, `supersedes` | **Unimplemented** (Factory chunk 3/4) |
| Decisions | `factory` | `factory`; `youtrack` (via `acceptance` ref) | `delivery.decision` | `id` + `hash` = `decisionId`/`decisionHash` | **Unimplemented** |
| Runner result | `agent-runner` | `factory` | `delivery.producer-result` ← `runner.run-record` | run id; **gap:** dispatch key + revision | Native record live; **mapping and gap additions unimplemented** |
| CI result | `ci-runner` | `factory` | `delivery.producer-result` ← `ci.run` | `runId/jobId`; **gap:** head SHA | Native event live; **mapping and gap additions unimplemented** |
| Dev deploy result | `plantpal` (+ `runtime`/`gateway`/`launcher`) | `factory` | `delivery.producer-result` (`environment`) | deployment id; **gap:** no receipt exists | **Unimplemented**; Planotell dev URL not verified |
| Routing/approval | `demand-coordinator` | `factory` | existing `demand` / `demand.fulfillment` | existing | Unchanged; not in this release |

## Upgrade / repin

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
