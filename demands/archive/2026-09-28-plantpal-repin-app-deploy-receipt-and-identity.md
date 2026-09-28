---
id: contracts-20260928-plantpal-repin-app-deploy-receipt-and-identity
date: 2026-09-28
from: contracts
to: [plantpal]
capability: Close the consuming leg of plantpal-20260927-contracts-app-deploy-receipt-and-identity — the app-deploy receipt, running-app identity and lookup transport shipped in contracts v0.36.0
acceptance-criteria:
  - "plantpal reviews contracts v0.36.0 (schemas/delivery/delivery.deployment-receipt.json, schemas/app/deployment-identity.json, the unchanged-in-meaning schemas/delivery/delivery.producer-result.json; docs/task-delivery.md §App-deploy and §Upgrade / repin v0.36.0) and either accepts it or raises the specific interface gaps back to contracts."
  - "plantpal re-pins tools/dev-delivery to v0.36.0 (requirements + tests together). `dev_delivery.py receipt <id>` then prints a delivery.deployment-receipt validated by the tagged binding, using the native → tagged field mapping in docs/task-delivery.md §Upgrade / repin v0.36.0. The native plantpal.dev-deployment-receipt/1 file may stay as the on-disk record. `dev_delivery.py lookup <id>` keeps printing delivery.producer-result, built by the §App-deploy mapping."
  - "plantpal's lookup CLI matches the transport v0.36.0 names: exit 0 with exactly one JSON document on stdout; miss = exit 4, `deployment_not_found: <id>` on stderr and nothing on stdout."
  - "plantpal validates emitted receipts against the JSON Schema itself and checks the cross-field rules (a `passed` receipt's observed.revision == mergedRevision and observed.deploymentId == deploymentId), not the generated binding alone. The pydantic model does not implement if/then (docs/task-delivery.md §Binding caveat)."
  - "plantpal round-trips its /actuator/info `deployment` block through AppDeploymentIdentity in a test, keeping null = not reported."
  - "plantpal tells factory and runtime that v0.36.0 is the tag to consume for the receipt and the running-app identity (their own demands or notes), or explains why not."
needs-owner: false
status: archived
---

# App-deploy receipt + running-app identity: close the consuming leg

## What we need

`contracts` **v0.36.0** shipped what
`plantpal-20260927-contracts-app-deploy-receipt-and-identity` asked for:

- **`delivery.deployment-receipt`** (new) is the tagged dev deployment receipt. It
  carries `deploymentId`, `kind` (`deploy`|`rollback`), `repository`, `branch`,
  `mergedRevision` (40-hex), per-component `imageDigests` + `digestKind`, `result`,
  `exitCode`, `startedAt`/`finishedAt`/`observedAt`, `environment` (`name` const
  `dev`, `url`), `observed` (the running app's identity), `checks`, `correlation`,
  and the **rollback identity** `rollback` (previous passed `deploymentId` +
  `revision` + `imageDigests`, `null` when none exists), plus `rollbackOf`/`restores`
  on rollback deployments.
- **`app/deployment-identity`** (new): `appIdentity` + nullable `revision`,
  `deploymentId`, `environment`. It is exactly the `/actuator/info` → `deployment`
  block plantpal already serves.
- **Rollback identity stays in the receipt.** `delivery.producer-result` gained no
  field. Factory reads `rollback` from the receipt it re-fetches through `nativeRef`.
  The full receipt → producer-result mapping is in `docs/task-delivery.md` §App-deploy
  and is executable as `receipt_to_producer_result` in `tests/validate_delivery.py`.
- **Lookup transport** for `plantpal:deployments/<id>`: CLI, JSON on stdout,
  `dev_delivery.py lookup <id>` (producer-result) and `receipt <id>` (receipt), run in
  the plantpal checkout on the deploying host. A miss is exit `4` and counts as
  `unavailable` for Factory, never `failed`.

Install: `platform-contracts @ git+https://github.com/elmoul/contracts.git@v0.36.0#subdirectory=gen/python`
(D031-verified from the tagged URL in a clean venv). No Java binding was generated,
because your Spring backend emits the identity block without a contracts dependency.
Ask if you want one.

## Why

D043 release duty: the origin closes its consuming leg. Until plantpal emits the
tagged receipt, Factory's rollback-identity criterion is still met only natively,
and consumers must not bind to plantpal's native JSON.

The release is **additive**. `delivery.producer-result` accepts and rejects exactly
the documents it did at v0.31.0–v0.35.0 (its `correlation`/`check` objects moved
into `$defs`, and the Python class names `Correlation`/`Check` are unchanged), so your
current `lookup` output keeps validating after the repin. Per D031/D043 no other
consumer is obligated to move.

## What we do once closed

Nothing further from contracts unless you raise a gap. If Factory later needs to
re-fetch from a host other than the one that deployed, that is a new transport
(e.g. an HTTP route) for plantpal to offer and for contracts to publish.
