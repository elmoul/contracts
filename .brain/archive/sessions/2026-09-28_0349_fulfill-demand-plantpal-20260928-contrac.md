---
session_id: 2026-09-28_0349_fulfill-demand-plantpal-20260928-contrac
agent: contracts
model: claude-opus-5
started: 2026-09-28T03:49:09+00:00
ended: 2026-09-28T03:56:01+00:00
task: "fulfill demand plantpal-20260928-contracts-app-deploy-lookup-route"
priority: 1
status: done
launch: interactive
decisions:
  - id: D-2026-09-28-01
    text: "Split ruling on the published interface: path/method/operationId/response documents/code table are contracts'; host, port and the concrete deployCaller credential are the producer's own design (PLATFORM_STATE §3, D040). Publishing it in this release is what unblocks plantpal, so no further contracts step."
    supersedes: null
  - id: D-2026-09-28-02
    text: "The new 404 code is const-pinned in an OpenAPI component (DeploymentNotFoundError), not via a new if/then in delivery.error.json, because that would narrow what the shared schema accepts. Follows the v0.34.0 CiResultNotFoundError precedent."
    supersedes: null
changes:
  - "new schemas/delivery-api/app-deploy-lookup.openapi.yaml: GET /delivery/v1/app-deploys/{deploymentId} (producer-result) + /receipt (receipt verbatim), miss/failure code table, DeploymentNotFoundError component"
  - "delivery.error.json: code table + examples gain deployment_not_found; producer_unavailable names app-deploy (code stays an open string, no narrowing)"
  - "docs/task-delivery.md: §App-deploy both transports, published-interface ruling, CLI-not-withdrawn; handoff matrix row; §Upgrade / repin v0.37.0"
  - "tests/validate_delivery.py: check_app_deploy_api (114 cases, 0 failures)"
  - "tag v0.37.0 (ad347f3) + pinned worktree ../contracts-worktrees/v0.37.0; pyproject/package.json 0.37.0"
  - "demands/fulfilled/plantpal-20260928-contracts-app-deploy-lookup-route-report.md + D043 origin demand demands/2026-09-28-plantpal-implement-app-deploy-lookup-route.md (12e5692)"
lessons:
  - "A miss is only machine-distinguishable from 'could not ask' if the contract also forbids the ambiguous wire cases: deployment_not_found must be the ONLY 404 and must carry the delivery.error body, and an unauthenticated call must be 403 rather than 404. Naming codes is not enough on its own."
  - "schema_for() in tests/validate_delivery.py takes the schema FILE name (delivery.producer-result.json), not the -style bare name; passing the bare name fails with FileNotFoundError."
context_missing: []
notes_used: []
vault_sync: none
close: confirmed
---


## Log

**03:49 Session opened** via `brain session open`.

**03:56 Session closed via `brain session close` (status: done).**
