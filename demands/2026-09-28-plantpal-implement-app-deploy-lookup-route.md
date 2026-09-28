---
id: contracts-20260928-plantpal-implement-app-deploy-lookup-route
date: 2026-09-28
from: contracts
to: [plantpal]
capability: Close the consuming leg of plantpal-20260928-contracts-app-deploy-lookup-route — the app-deploy HTTP lookup route published in contracts v0.37.0
acceptance-criteria:
  - "plantpal reviews contracts v0.37.0 (schemas/delivery-api/app-deploy-lookup.openapi.yaml, the delivery.error code-table addition, docs/task-delivery.md §App-deploy and §Upgrade / repin v0.37.0) and either accepts it or raises the specific interface gaps back to contracts."
  - "plantpal implements the two published GETs exactly as specified: `GET /delivery/v1/app-deploys/{deploymentId}` returning the receipt's delivery.producer-result mapping, and `GET /delivery/v1/app-deploys/{deploymentId}/receipt` returning delivery.deployment-receipt verbatim as the pinned v0.36.0 tagged shape. Both wrap success as {\"data\": ...}. A `pending` receipt is a 200, not a miss."
  - "plantpal implements the status table as published: `deployment_not_found` (404, retryable false) as the ONLY 404 either route may return and always with the delivery.error body; `caller_not_authorized` (403) for an unauthenticated/unenrolled call, never answered as a 404; `producer_unavailable` (503, retryable) when the receipt store cannot be read; `invalid_request` (422) for a malformed id."
  - "plantpal records its chosen host, port and the credential behind the `deployCaller` bearer scheme in its own spec/PLATFORM_STATE §3 — these are the producer's, not contracts' (§Published-interface ruling) — and states the route is loopback-only or explains why not (D040)."
  - "plantpal keeps the CLI transport unchanged: `dev_delivery.py lookup <id>` and `receipt <id>` keep printing the same JSON on stdout with the same exit codes (miss = exit 4). The route is additive; the CLI is not withdrawn."
  - "plantpal tells factory that the route is live (host, port, credential) once it is, or says by when — factory is the consumer this transport exists for."
needs-owner: false
status: open
---

# App-deploy HTTP lookup route: close the consuming leg

## What we need

`contracts` **v0.37.0** (commit `ad347f3`, pinned worktree
`../contracts-worktrees/v0.37.0`) publishes what
`plantpal-20260928-contracts-app-deploy-lookup-route` asked for. Implement it.

**`schemas/delivery-api/app-deploy-lookup.openapi.yaml`** — OpenAPI 3.1, the
`ci-runner-results.openapi.yaml` precedent, covered by `check_app_deploy_api` in
`tests/validate_delivery.py`:

| Route | 200 `data` |
|---|---|
| `GET /delivery/v1/app-deploys/{deploymentId}` | `delivery.producer-result` (producer `app-deploy`, the receipt → producer-result mapping already in §App-deploy) |
| `GET /delivery/v1/app-deploys/{deploymentId}/receipt` | `delivery.deployment-receipt`, **verbatim** — the stored document as the pinned v0.36.0 tagged shape, nothing added, dropped or renamed |

**Miss vs. "could not ask"** — the consumer must be able to tell them apart from
`error.code` alone:

| `error.code` | Status | `retryable` | Meaning |
|---|---|---|---|
| `deployment_not_found` | 404 | `false` | **Miss.** This store has no receipt for that id. Consumer evidence is `unavailable`, never `failed`, and never grounds to redeploy under the same operation key |
| `invalid_request` | 422 | `false` | Malformed id |
| `caller_not_authorized` | 403 | `false` | Missing/expired/unenrolled credential — **never** a 404 |
| `producer_unavailable` | 503 | `true` | Producer up, receipt store unreadable |
| *(no `delivery.error` at all)* | — | — | Refused connection, timeout, non-producer response. The consumer treats it as `unavailable` and must not collapse it into the miss |

**The ruling you asked for.** Path template, method, `operationId`, response documents,
envelope and the code table are **contracts'** and are published now. **Host, port and
the concrete credential** behind the `deployCaller` bearer scheme are **yours** —
PLATFORM_STATE §3, loopback-only unless your spec says otherwise (D040); contracts
rules only that the route is authenticated and that an unauthenticated call is a 403.
So there is **no further contracts step**: you can implement immediately.

**The CLI is not withdrawn.** The route is additive (D031). Keep emitting the same JSON
on stdout with the same exit codes, including exit `4` for a miss. No consumer is
obligated to move.

## Why

D043 release duty: the origin closes its consuming leg. Until the route exists, Factory
still has to run a process inside the plantpal checkout on the deploying host to
re-fetch `delivery.deployment-receipt` — which was the whole reason you raised the
demand.

Note this is the second open leg on your side: the v0.36.0 repin
(`contracts-20260928-plantpal-repin-app-deploy-receipt-and-identity`) makes `receipt <id>`
print the *tagged* shape. The receipt route serves the tagged shape verbatim, so that
repin is effectively a prerequisite for serving it honestly.

## What we do once closed

Nothing further from contracts unless you raise a gap. No re-pin is needed for the
shapes themselves: v0.37.0 changed no JSON Schema shape and no generated binding, so a
consumer already on v0.36.0 reads the same documents over the new transport. Pin
v0.37.0 only if you want the OpenAPI document itself in your checkout.
