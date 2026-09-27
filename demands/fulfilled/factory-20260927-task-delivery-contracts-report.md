---
demandId: factory-20260927-task-delivery-contracts
worker: contracts
date: 2026-09-27
status: done
shipped: ["v0.31.0", "commit 19a2dbc on main", "schemas/delivery/ (10 JSON Schemas: issue-ref, issue, issue-page, workflow, sync-request, sync-operation, error, evidence, decision, producer-result)", "schemas/delivery-api/youtrack-delivery.openapi.yaml (/delivery/v1 routes)", "docs/task-delivery.md (recovery semantics, resolve enforcement, producers + gaps, handoff matrix, repin)", "Python binding platform_contracts.delivery + TypeScript delivery-*.ts", "tests/validate_delivery.py (62 positive/negative fixtures)"]
summaryRef: "commit 19a2dbc on main (feat(delivery): D113 task-delivery schema set + youtrack delivery API (v0.31.0))"
---

# Fulfillment: D113 task delivery interfaces

## State check

No earlier session had shipped this. The two earlier supervisor-opened sessions
(`2026-09-27_0750`, `_0808`) left no commits, and before this work no `delivery`
schema, tag or report existed. This session did the work.

## What shipped

Tag **`v0.31.0`** (commit `19a2dbc`, pushed to `origin/main`), pinned worktree
`../contracts-worktrees/v0.31.0`. It is additive: no existing schema changed.
`git diff` against v0.30.0 touches nothing under `schemas/factory`,
`schemas/agent-runner` or `schemas/youtrack`.

The full reference is **`docs/task-delivery.md`**. Per criterion:

1. **YouTrack delivery interfaces.** `delivery.issue` gives the stable `vendorId`
   plus the readable id and project; title, description and verbatim acceptance
   material; the actual state with the vendor's `resolved` flag; type and priority;
   created/updated/resolvedAt; epic parent and subtasks; dependencies by direction
   with `resolved|unresolved|unknown`; and `dependenciesComplete`.
   `delivery.issue-page` adds cursor pagination with `complete` and
   `unavailableProjects`, so absence from a page proves nothing. `delivery.workflow`
   exposes the existing states read-only. Writes are the `link`, `comment`,
   `transition` and `resolve` kinds of `delivery.sync-request`. The routes are in
   `schemas/delivery-api/youtrack-delivery.openapi.yaml`. No shape carries a vendor
   credential; Factory authenticates to `youtrack` with a youtrack-issued service
   credential only.
2. **Durable mutation identity.** Factory reserves an `operationKey` before sending
   and the service reserves one before calling the vendor. The same key with the
   same `requestHash` replays; the same key with a different body gets
   `409 operation_key_conflict`. Preconditions produce a durable `rejected` record
   with nothing written. `confirmed` requires read-back (enforced by the schema). A
   timeout after send becomes `uncertain`, which is never resent blindly; `reconcile`
   re-reads and resends only after absence is proven. On restart `submitted` becomes
   `uncertain`, and list/lookup routes support reconciliation. Retention: open
   records are never purged and terminal records are kept at least 90 days. The
   doc states explicitly that this is **not** a transaction and **not** exactly-once.
   Scope drift: `expectedScope` is checked against a fingerprint of owner-authored
   fields only, so Factory's own writes never invalidate the plan.
3. **Stage-aware evidence.** `delivery.evidence` carries: stage (pre-deploy stages,
   then `deployment`/`live`); per-criterion `evaluableAt`; `planHash` +
   `issueScope`; repository, branch, a full 40-hex revision and a `task`/`merged`
   role (`merge`/`deployment`/`live` must be `merged`); `source` with producer and
   re-fetchable `recordRef`; observer and times; and a dev `environment` (running
   app identity, deployment id, deployed revision, URL) required after deploy.
   `basis` is machine-observation, worker-claim or owner-attestation. `result`
   adds `unknown`/`unavailable`, and `exitCode: null` means not reported, never 0.
   Authorization and acceptance live in a separate `delivery.decision`; policy is
   never an owner click. Historical `factory.evidence-receipt` is untouched and
   referenced verbatim via `legacyReceipt {id, hash}`.
4. **Producers.** `delivery.producer-result` plus `docs/task-delivery.md`
   §Producers give the mapping from `runner.run-record`, `ci.run` and a (not yet
   existing) app deploy receipt. They also set the correlation rule: an
   uncorrelatable result, a null revision or a result that cannot be re-fetched
   counts as `unknown`. Report prose, agent exit and coordinator approval never
   count as acceptance.
5. **Bindings, fixtures, tag.** Python `platform_contracts.delivery.*` for Factory
   and youtrack. TypeScript `delivery-*.ts` for the agent-runner producer. No Java
   binding, because no Java producer or consumer exists yet; one can be requested
   if plantpal's deploy receipt is Java. `tests/validate_delivery.py` has 62 cases,
   and each negative was checked to fail for its intended reason. The negatives
   cover resolve backed by policy, ready-for-test, worker exit, coordinator
   approval or missing acceptance; confirmed without read-back; `exactly-once`
   status; short SHAs; task revision as merge/live; live without environment;
   production environment; a URL in place of a deployment id; exit code `"0"`.
   `python tests/run_all.py` passes, including the unchanged factory/runner
   fixtures.
6. **Handoff.** The matrix, repin steps and unimplemented dependencies are below and
   in `docs/task-delivery.md`.

## D031 acceptance (real tag)

- Python: a fresh venv, `pip install --no-cache-dir "platform-contracts @
  git+https://github.com/elmoul/contracts.git@v0.31.0#subdirectory=gen/python"`
  gives version 0.31.0. The installed binding validates the positive fixtures,
  rejects policy/ready-for-test/worker-exit resolves, and still loads a legacy
  v0.25.0 `FactoryEvidenceReceipt`.
- TypeScript: a scratch npm project with a fresh cache installed
  `file:../contracts-worktrees/v0.31.0/gen/ts`; `tsc --strict --noEmit` passes when
  importing `DeliveryProducerResult` / `DeliverySyncOperation`.

**Binding caveat:** the pydantic/TS types do not enforce the schemas'
`if/then` conditionals. These are: `expectedScope` required for
transition/resolve; `environment` required and role `merged` after deploy;
`recordRef` required for machine observations; decision kind/basis pairing;
`confirmed` implies `effectPresent: true`. **Producers and the youtrack service
must validate request bodies against the JSON Schema itself** (or re-implement
those rules), not rely on the generated classes alone.

## Handoff matrix

| Interface | Producer → Consumer | Reference | Identity / recovery | Status |
|---|---|---|---|---|
| Issue read/list, workflow | youtrack → factory | `delivery.issue`, `.issue-page`, `.workflow`; `GET /delivery/v1/...` | cursor + `complete` | **unimplemented** |
| Link/comment/transition/resolve | youtrack → factory | `delivery.sync-request` / `.sync-operation` / `.error`; `PUT/GET /delivery/v1/operations/{key}`, `POST .../reconcile`, `GET /delivery/v1/operations` | `operationKey` + `requestHash`, read-back | **unimplemented** |
| Evidence, decisions | factory → factory (+ youtrack via acceptance ref) | `delivery.evidence`, `delivery.decision` | `id` + `hash` | **unimplemented** |
| Runner result | agent-runner → factory | `delivery.producer-result` ← `runner.run-record` | run id; **gap:** dispatch key + revision | native record live, mapping unimplemented |
| CI result | ci-runner → factory | `delivery.producer-result` ← `ci.run` | runId/jobId; **gap:** head SHA | native event live, mapping unimplemented |
| Dev deploy result | plantpal (+ runtime/gateway/launcher) → factory | `delivery.producer-result.environment` | deployment id; **gap:** no receipt exists | **unimplemented**; Planotell dev URL unverified |

## Compatibility and repin

- Factory: `platform-contracts @ git+https://github.com/elmoul/contracts.git@v0.31.0#subdirectory=gen/python`
  (from v0.25.0). The `factory.*` and `agent_runner.*` shapes are unchanged. New
  enums are `StrEnum` (Python ≥ 3.11, already the floor). After repinning, run
  existing tests plus one fixture round-trip, and confirm stored receipts load
  unchanged.
- youtrack: same pin. Implement `/delivery/v1` against the OpenAPI document plus the
  enforcement and negative integration tests listed in `docs/task-delivery.md`
  §Resolve enforcement.
- agent-runner (TS): `file:../contracts-worktrees/v0.31.0/gen/ts`.
- Additive release: per D031/D043 no other consumer is obligated to move.

## Explicit unimplemented dependencies (not live because of this release)

- **youtrack:** every `/delivery/v1` route, the operation store, reconcile, the
  Factory caller credential and its enforcement.
- **agent-runner:** head revision/branch on run records; a client-supplied dispatch
  key with lookup. Contract additions would follow in a later contracts release on
  their demand.
- **ci-runner:** `headSha` on `ci.run`/`BuildResult` (a later additive contracts
  change on demand).
- **plantpal / runtime / gateway / launcher:** a dev deployment receipt with lookup,
  a running-app identity+revision endpoint, and a verified dev route. Planotell's dev
  URL remains unverified.
- **factory:** the delivery store, evidence/decision recording, correlation and the
  waiting view.

Nothing here makes a runtime endpoint or dev delivery live.

## Open interface decisions (reported, not silently decided)

- The Factory→youtrack caller authentication mechanism is left to `spec-youtrack.md`
  (contract fixes only that it is a youtrack-issued service credential, not a vendor
  token).
- The service port in the OpenAPI `servers` entry defaults to 8095 (the planner's
  port, D111) as a placeholder, not a ruling.
- Whether `youtrack` should cross-check an acceptance reference against Factory's
  decision store (instead of trusting the authenticated boundary) is left as a
  possible later addition.

D043: an origin demand `contracts-20260927-factory-repin-task-delivery` is raised
`to: [factory]` in its own coordination commit ("close your consuming leg: re-pin
and adopt"). The release is additive, so no fleet-wide consumer demand is raised.
