---
demandId: plantpal-20260927-contracts-app-deploy-receipt-and-identity
worker: contracts
date: 2026-09-28
status: done
shipped: ["v0.36.0", "commit 7bb2fcd on main (feat(delivery): app-deploy receipt + running-app identity (v0.36.0))", "schemas/delivery/delivery.deployment-receipt.json (new)", "schemas/app/deployment-identity.json (new)", "schemas/delivery/delivery.producer-result.json (correlation/check moved into $defs; no validation change; nativeRef doc names the receipt)", "docs/task-delivery.md (§App-deploy: receipt, running-app identity, CLI lookup transport, receipt -> producer-result mapping; §Producers, handoff matrix, §Binding caveat, §Upgrade / repin v0.36.0)", "tests/validate_delivery.py (114 schema cases, check_deployment_semantics, receipt_to_producer_result)", "Python binding platform_contracts.delivery.delivery_deployment_receipt + platform_contracts.app.deployment_identity", "TypeScript delivery-deployment-receipt.ts + deployment-identity.ts + rebuilt dist/", "pinned worktree ../contracts-worktrees/v0.36.0", "D043 origin demand demands/2026-09-28-plantpal-repin-app-deploy-receipt-and-identity.md"]
summaryRef: "commit 7bb2fcd on main (tag v0.36.0)"
---

# Fulfillment: app-deploy receipt, running-app identity and lookup

## State check

**Not previously shipped.** The supervisor-opened session for this demand
(`2026-09-28_0000`) held only its open stub: no commits, no tag, no report. At
v0.35.0, `docs/task-delivery.md` §Producers still listed the `app-deploy` gap
("Needs: a dev deployment receipt … with lookup, and a running-app identity/revision
endpoint"). This session did the work.

## What shipped

Tag **`v0.36.0`** (commit `7bb2fcd`, pushed to `origin/main`), pinned worktree
`../contracts-worktrees/v0.36.0`. **Additive.** The bindings are Python and
TypeScript; Java is unchanged. The reference is **`docs/task-delivery.md` §App-deploy**.

### 1. Deployment receipt schema — `delivery.deployment-receipt`

`schemas/delivery/delivery.deployment-receipt.json` (`DeliveryDeploymentReceipt`), a
closed shape. It covers every field the criterion names:

| Criterion field | Receipt field |
|---|---|
| deploymentId | `deploymentId` |
| repository, branch | `repository`, `branch` |
| mergedRevision (40-hex) | `mergedRevision`, pattern `^[0-9a-f]{40}$`, never null |
| imageDigests per component | `imageDigests`: component → `sha256:<64hex>` or `null`, at least one entry, plus `digestKind` (`local-image-id` / `registry-manifest`) |
| result (passed/failed/unknown/unavailable/pending) | `result`, exactly that enum |
| observedAt | `observedAt` (`null` only while `pending`, enforced by the schema) |
| smoke checks | `checks[]`, the same item shape as `delivery.producer-result.checks` |
| environment (name const dev) | `environment: {name: const "dev", url}` |
| rollback identity (previous deploymentId + revision + digests, nullable) | `rollback: {deploymentId, revision, imageDigests}` or `null` |

It also adds what plantpal's native receipt already records and Factory needs: `kind`
(`deploy`|`rollback`) with `rollbackOf`/`restores`, `exitCode` (nullable, never
defaulted), `startedAt`/`finishedAt`, `observed` (the running app's identity as
reported), `correlation`, and `nativeRef`.

The schema enforces these conditionals: a settled receipt has `finishedAt` and
`observedAt`; `passed` requires `exitCode: 0`, a non-null `observed` and every digest
non-null; `kind: rollback` requires `rollbackOf` and `restores`, and `kind: deploy`
requires both to be `null`. The equality rules (`passed` ⇒ `observed.revision ==
mergedRevision` and `observed.deploymentId == deploymentId`) have no JSON Schema
keyword and are enforced by `check_deployment_semantics` in
`tests/validate_delivery.py`.

### 2. producer-result and the rollback mapping

I took the **docs** option. `delivery.producer-result` gained no rollback field.
`docs/task-delivery.md` §App-deploy states that rollback identity is read from the
receipt through `nativeRef`, and it writes down the full receipt →
`delivery.producer-result` mapping for producer `app-deploy`. In summary:
`operationId`=`deploymentId`, `revision`=`mergedRevision`, `outcome`=`result`,
`artifactRef`=the primary component's digest, and `environment` built **only** from
`observed` (`null` unless the app reported a revision and a deployment id). The same
mapping runs as `receipt_to_producer_result` in the tests, and every mapped fixture
validates against `delivery.producer-result`.

The schema file did change, but not in what it accepts. Its inline `correlation`
and `checks[]` item objects moved into `$defs` so the receipt can `$ref` them. All
pre-existing producer-result fixtures still validate, and the regenerated bindings
keep the names `Correlation`/`Check` (Python) and
`DeliveryProducerCorrelation`/`DeliveryProducerCheck` (TS).

### 3. Running-app identity — `app/deployment-identity`

`schemas/app/deployment-identity.json` (`AppDeploymentIdentity`) has `appIdentity`
(required, non-null) plus `revision` (40-hex or `null`), `deploymentId` and
`environment`, each nullable. The schema description states that `null` means not
reported, never a default, and that `null` never matches an expected value. It is
exactly the block plantpal serves at `GET /actuator/info` → `deployment`, and
§App-deploy names that route. It is kept separate from the `app/identity.json`
attribution stub, which is a different concept. `environment` is not restricted to
`dev` here because the shape describes any running instance; the D113 `dev` pin lives
on the receipt.

### 4. Lookup transport

This release names the transport as **CLI, JSON on stdout**, run in the plantpal
checkout on the deploying host:
`python tools/dev-delivery/dev_delivery.py lookup <id>` prints `delivery.producer-result`,
and `receipt <id>` prints `delivery.deployment-receipt`. A miss is exit `4`, with
`deployment_not_found: <id>` on stderr and nothing on stdout, which matches plantpal's
current tool. Factory must treat a miss as `unavailable`, never `failed`, and never
as grounds to redeploy. No HTTP route is published. If Factory needs to re-fetch from
another host, that transport is a later plantpal offer and a later contracts release.

### 5. Bindings

- **Python:** `platform_contracts.delivery.delivery_deployment_receipt` and
  `platform_contracts.app.deployment_identity`. They were generated in one batch run,
  so the receipt imports the identity and producer-result classes instead of
  duplicating them.
- **TypeScript:** `delivery-deployment-receipt.ts` and `deployment-identity.ts`,
  re-exported from `index.ts`. They are included because every `delivery.*` shape has
  a TS binding and `runtime`'s language is not fixed.
- **Java:** not generated. plantpal's producer is Python, its Spring backend emits
  the identity block without depending on contracts, and no Java consumer exists.

## D031 acceptance (real tag)

- **Python:** fresh venv, `pip install --no-cache-dir "platform-contracts @
  git+https://github.com/elmoul/contracts.git@v0.36.0#subdirectory=gen/python"`. The
  installed version is `0.36.0`, imported from site-packages. All 5 good receipt and
  2 good identity fixtures round-trip, and each mapped producer-result parses. The 7
  sampled negatives are rejected, and pre-existing producer-result fixtures still
  parse.
- **TypeScript:** a fresh npm project with a `file:` dependency on
  `../contracts-worktrees/v0.36.0/gen/ts` and a fresh cache. `tsc --strict --noEmit`
  passes on code that constructs `DeliveryDeploymentReceipt`,
  `DeliveryRollbackIdentity` and `AppDeploymentIdentity`.
- `python tests/run_all.py` passes. `validate_delivery.py` reports 114 cases and
  0 failures.

## What the origin must know

- As with v0.35.0, **the generated bindings do not enforce the `if/then` rules.**
  `DeliveryDeploymentReceipt` will accept a `passed` receipt with `observed: null` or
  `exitCode: null`. Validate emitted receipts against the JSON Schema and port
  `check_deployment_semantics` (see §Binding caveat).
- The native → tagged field mapping (`revision` → `mergedRevision`, `testUrl` →
  `environment.url`, `digestKind` → `local-image-id`, and dropping `schema` /
  `revisionRole` / `composeProject` / `port` / `preDeployChecks` / `log`) is in
  §Upgrade / repin v0.36.0.
- D043 origin demand raised:
  `demands/2026-09-28-plantpal-repin-app-deploy-receipt-and-identity.md`. The release
  is additive, so no fleet-wide consumer demands were raised.

## Not done / caveats

- `schemas/` is still not bundled in the Python wheel (the open packaging gap from
  the v0.35.0 report), so a consumer needs the tag checkout to validate against the
  JSON Schema.
- The Planotell route and managed hosting are unchanged here. They remain with
  `runtime` (Factory demand `factory-20260927-dev-delivery-routing`).
