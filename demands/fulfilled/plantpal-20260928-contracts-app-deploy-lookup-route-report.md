---
demandId: plantpal-20260928-contracts-app-deploy-lookup-route
worker: contracts
date: 2026-09-28
status: done
shipped: ["v0.37.0", "commit ad347f3 on main (feat(delivery): app-deploy HTTP lookup route (v0.37.0))", "schemas/delivery-api/app-deploy-lookup.openapi.yaml (new)", "schemas/delivery/delivery.error.json (code table + examples gain deployment_not_found; producer_unavailable now names app-deploy; code stays an open string, no validity change)", "docs/task-delivery.md (§App-deploy: both lookup transports, the miss/failure table, the published-interface ruling, the CLI-not-withdrawn statement; handoff matrix row; §Upgrade / repin v0.37.0)", "tests/validate_delivery.py (check_app_deploy_api; 114 schema cases, 0 failures)", "gen/python/pyproject.toml + gen/ts/package.json bumped to 0.37.0 (no generated code changed)", "pinned worktree ../contracts-worktrees/v0.37.0", "D043 origin demand demands/2026-09-28-plantpal-implement-app-deploy-lookup-route.md"]
summaryRef: "commit ad347f3 on main (tag v0.37.0)"
---

# Fulfillment: app-deploy lookup route

## State check

**Not previously shipped.** At v0.36.0 the only published transport for
`plantpal:deployments/<id>` was the CLI, and `docs/task-delivery.md` §App-deploy said so
explicitly: *"No HTTP route exists. If Factory needs to re-fetch from another host,
plantpal must offer a new transport and contracts must publish it."* `schemas/delivery-api/`
held two documents (`youtrack-delivery.openapi.yaml`, `ci-runner-results.openapi.yaml`)
and no app-deploy one, and `delivery.error` had no `deployment_not_found` code. This
session did the work.

## What shipped

Tag **`v0.37.0`** (commit `ad347f3`, pushed to `origin/main`), pinned worktree
`../contracts-worktrees/v0.37.0`. **Additive, and schemas/docs only** — no JSON Schema
changed shape and no generated binding changed. The reference is
`docs/task-delivery.md` §App-deploy.

### 1. The route interface — criterion 1

`schemas/delivery-api/app-deploy-lookup.openapi.yaml` (OpenAPI 3.1), served by the
producer, both lookups by deployment id:

| Route | `operationId` | 200 `data` |
|---|---|---|
| `GET /delivery/v1/app-deploys/{deploymentId}` | `getAppDeployResult` | `delivery.producer-result`, the receipt → producer-result mapping (producer `app-deploy`) already fixed in §App-deploy and executable as `receipt_to_producer_result` |
| `GET /delivery/v1/app-deploys/{deploymentId}/receipt` | `getAppDeployReceipt` | `delivery.deployment-receipt`, **served verbatim** as the pinned v0.36.0 tagged shape — the stored document, nothing added, dropped or renamed |

200 on a hit, and a `pending` receipt is a hit, not a miss. Same `{"data": ...}` /
`{"error": ...}` envelope as every other `/delivery/v1` route. Rollback identity stays
on the receipt route; `delivery.producer-result` still gains no rollback field.

### 2. The miss/failure status table — criterion 2

Every case is machine-distinguishable by `error.code`:

| `error.code` | Status | `retryable` | Meaning | Consumer evidence |
|---|---|---|---|---|
| `deployment_not_found` | 404 | `false` | **Miss.** This store has no receipt for that id — the same statement as CLI exit `4`, and not proof the deployment never happened | `unavailable`, **never `failed`**; never grounds to redeploy under the same operation key |
| `invalid_request` | 422 | `false` | Malformed deployment id | could not ask |
| `caller_not_authorized` | 403 | `false` | Missing, expired or unenrolled credential — **never answered as a 404** | could not ask |
| `producer_unavailable` | 503 | `true` | Producer up, receipt store unreachable/unreadable | could not ask; retry |
| *(absent — no `delivery.error`)* | — | — | Refused connection, DNS/TLS failure, timeout, unparseable body, or a 404/5xx from something that is not this producer | `unavailable`; **must not** be collapsed into `deployment_not_found` |

Two rules make the distinction hold at the wire: `deployment_not_found` is the **only**
404 either route may return, and it must carry the `delivery.error` body — so a bare or
HTML 404 is "could not ask", not a miss. The 404 body is pinned by the component schema
`DeploymentNotFoundError` (`code` const, `retryable` const `false`), the same technique
as `CiResultNotFoundError` in v0.34.0.

`schemas/delivery/delivery.error.json` gained `deployment_not_found` in its code table
and `examples`, and `producer_unavailable` now names app-deploy alongside ci-runner. I
did **not** add an `if/then` for the new code to `delivery.error` itself: that would
narrow what the shared schema accepts (a documented-but-loose `deployment_not_found`
body was legal at v0.36.0), and the ci-runner precedent already puts the const
constraints in the OpenAPI component. `code` stays an open string, so no document that
validated before validates differently now.

### 3. The ruling — criterion 3

Recorded as §Published-interface ruling in `docs/task-delivery.md` §App-deploy. It is a
**split**, and both halves are settled by this release:

| Part of the surface | Whose |
|---|---|
| Path template, method, `operationId` | **contracts'** — published here. A consumer must be able to write the request without asking the producer; this is how v0.36.0 §App-deploy reads and how `ci-runner-results.openapi.yaml` already works |
| Response documents + the `{"data"}`/`{"error"}` envelope | **contracts'** |
| The code table, each code's status and `retryable` | **contracts'** |
| Host and port | **producer's own service design** — PLATFORM_STATE §3; the OpenAPI `servers` entry is an example default, loopback-only unless plantpal's spec says otherwise (D040) |
| The concrete credential behind the `deployCaller` bearer scheme (issuance, rotation, enrolment) | **producer's own service design.** Contracts rules only that the route is authenticated and that an unauthenticated call is `caller_not_authorized` (403), never a 404 |

I did not take the "it's all producer design, no contracts change needed" reading. The
path and the code table are exactly the parts a consumer on another host cannot
discover or negotiate at runtime, and leaving them to the producer would mean Factory
binds to an undocumented surface. But the practical effect the criterion asked for is
delivered anyway: **the publication happened in this release, so plantpal is unblocked
to implement immediately — no further contracts step.**

### 4. The CLI is not withdrawn — criterion 4

Stated in the OpenAPI `info.description`, in §App-deploy (`#### The CLI is not
withdrawn`), in §Upgrade / repin v0.37.0 and in the CHANGELOG entry. The route is
additive (D031): `dev_delivery.py lookup <id>` and `receipt <id>` keep printing the same
JSON on stdout with the same exit codes, including exit `4` for a miss; plantpal keeps
emitting it unchanged; no existing consumer is obligated to move; and a consumer may use
either transport, because they serve the same documents and a miss means the same thing
on both.

### 5. Publication vehicle and test coverage — criterion 5

An OpenAPI document under `schemas/delivery-api/` (the `ci-runner-results.openapi.yaml`
precedent), covered by `check_app_deploy_api` in `tests/validate_delivery.py`, which
asserts: both routes exist with their `operationId`s; both declare a 404; the receipt
route's 200 `data` refs `delivery.deployment-receipt.json` and the result route's refs
`delivery.producer-result.json` (this is the check that the receipt is served verbatim,
not re-wrapped); all four codes appear on the published surface; the
`DeploymentNotFoundError` body accepts the real miss and rejects a wrong code or
`retryable: true`; and both 200 payloads accept the shared `GOOD_RECEIPT_PASSED` fixture
and its mapping. I verified the check bites by breaking an `operationId` and watching it
fail before restoring. 114 schema cases, 0 failures; `python tests/run_all.py` passes.

## D031 acceptance (real tag)

- **Tagged worktree:** `git worktree add --detach ../contracts-worktrees/v0.37.0 v0.37.0`,
  confirmed in `git worktree list`. In that worktree the OpenAPI document reports
  `info.version: 0.37.0`, both routes are present, all three `../delivery/*.json` `$ref`
  targets resolve, and `python tests/run_all.py` passes.
- **Python:** fresh venv, `pip install --no-cache-dir "platform-contracts @
  git+https://github.com/elmoul/contracts.git@v0.37.0#subdirectory=gen/python"` — installed
  version `0.37.0` from site-packages, `DeliveryDeploymentReceipt` and
  `DeliveryProducerResult` import.
- **TypeScript:** fresh npm project and fresh cache, `file:` dependency on
  `../contracts-worktrees/v0.37.0/gen/ts` — installed package version `0.37.0`,
  `tsc --strict --noEmit` passes on code typed against both shapes.

## What the origin must know

- **No re-pin is required for the shapes.** v0.37.0 changed no JSON Schema shape and no
  generated code; a consumer already on v0.36.0 reads the same documents over the new
  transport. Pin v0.37.0 only to have the OpenAPI document in your checkout.
- **No generated client ships for this document**, as with `ci-runner-results.openapi.yaml`.
  Consumers build the two GETs themselves and validate payloads against the pinned JSON
  Schemas — and per §Binding caveat, against the **schemas**, not the bindings, since the
  receipt's `if/then` rules are not enforced by the generated classes.
- **Serving the receipt verbatim presupposes the v0.36.0 repin.** Until
  `dev_delivery.py receipt <id>` emits the tagged shape (open demand
  `contracts-20260928-plantpal-repin-app-deploy-receipt-and-identity`), the receipt route
  would serve plantpal's native `plantpal.dev-deployment-receipt/1`. That repin is
  effectively a prerequisite.
- **D043:** origin demand raised —
  `demands/2026-09-28-plantpal-implement-app-deploy-lookup-route.md`. The release is
  additive, so **no fleet-wide consumer demands** were raised (D031/D043: an additive
  release obligates no consumer to move).

## Not done / caveats

- The route is **published, not implemented**. The handoff matrix row says so; serving
  it is plantpal's work.
- `gen/ts/package-lock.json` still carries a stale `0.21.0` version field. Pre-existing
  and untouched here; it is not what consumers pin.
- `schemas/` is still not bundled in the Python wheel (the open packaging gap carried
  from v0.35.0/v0.36.0), so a consumer needs the tag checkout to validate against the
  JSON Schema or to read this OpenAPI document.
