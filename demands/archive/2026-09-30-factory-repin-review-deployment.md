---
id: contracts-20260930-factory-repin-review-deployment
date: 2026-09-30
from: contracts
to: [factory]
capability: Close the consuming leg of factory-20260930-contracts-review-deployment — the review-environment receipt, evidence and launcher port shipped in contracts v0.38.0
acceptance-criteria:
  - "factory reviews contracts v0.38.0 (schemas/delivery/delivery.deployment-receipt.json, schemas/delivery/delivery.evidence.json, schemas/launcher/review-environment.openapi.yaml; docs/task-delivery.md §Review environments and §Upgrade / repin v0.38.0) and either accepts it or raises the specific interface gaps back to contracts."
  - "factory re-pins to v0.38.0 (requirements + tests together)."
  - "factory records 'the review URL serves PR head <sha>' as delivery.evidence: basis machine-observation, stage deployment (or live), environment.name review, revisionRole task, source.producer app-deploy with source.recordRef = the receipt nativeRef. A deployedRevision that differs from revision is recorded failed, and an identity the app did not report is never recorded passed. factory enforces that equality itself: the schema and the generated bindings do not (docs/task-delivery.md §Review environments, §Binding caveat)."
  - "factory treats review_environment_not_found (404) and every absent/unauthorized/unreachable launcher answer as unavailable, never failed."
  - "factory tells launcher (its own demand or note) that v0.38.0 is the tag whose review-environment port it implements, or explains why not."
needs-owner: false
status: archived
---

# Review environment: close the consuming leg

## What we need

`contracts` **v0.38.0** shipped what `factory-20260930-contracts-review-deployment`
asked for. It is additive: every dev receipt and dev evidence record validates
unchanged.

- **`delivery.deployment-receipt`:** `environment.name` is `dev | review`. New optional
  `revisionRole` (`task | merged`, absent = `merged`), `review` (`pullRequest`,
  `pullRequestUrl`, nullable) and `environment.apiDocsUrl` (nullable). A review receipt
  requires `revisionRole: task`, the `review` block, `kind: deploy` and `rollback:
  null`. `mergedRevision` keeps its name and holds the PR head for a review receipt.
  `environment.url` is the frontend URL.
- **`delivery.evidence`:** `deployment`/`live` evidence may have `environment.name:
  review`, and then must have `revisionRole: task`. Dev evidence still must be `merged`.
- **`schemas/launcher/review-environment.openapi.yaml`:** `POST
  /review/v1/environments`, `GET`/`DELETE /review/v1/environments/{idempotencyKey}`.
  Status is `starting | ready | failed | stopped`, with the environment's receipt.
  `ready` means a `passed` review receipt whose `observed.revision` equals
  `expectedRevision`; a mismatch is `failed`. One environment per repository at a time
  is the caller's concern.

Install: `platform-contracts @ git+https://github.com/elmoul/contracts.git@v0.38.0#subdirectory=gen/python`
(D031-verified from the tagged URL in a clean venv).

## Why

D043 release duty: the origin closes its consuming leg. Nothing here obligates any
other consumer to move (additive release, D031).
