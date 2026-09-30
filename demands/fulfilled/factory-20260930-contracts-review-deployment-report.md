---
demandId: factory-20260930-contracts-review-deployment
worker: contracts
date: 2026-09-30
status: done
shipped: ["v0.38.0", "commit 1445ca4 on main (feat(delivery): review environment receipt, evidence and launcher port (v0.38.0))", "schemas/delivery/delivery.deployment-receipt.json (environment.name dev|review; optional revisionRole, review, environment.apiDocsUrl; review conditionals)", "schemas/delivery/delivery.evidence.json (environment.name dev|review; review deployment/live evidence at revisionRole task)", "schemas/launcher/review-environment.openapi.yaml (new)", "docs/task-delivery.md (§Review environments, handoff row, §Upgrade / repin v0.38.0)", "tests/validate_delivery.py (139 cases, check_review_api, check_review_evidence_semantics)", "Python bindings delivery_deployment_receipt, delivery_evidence, delivery_error; TypeScript delivery-deployment-receipt/evidence/error/producer-result + dist", "pinned worktree ../contracts-worktrees/v0.38.0", "D043 origin demand demands/2026-09-30-factory-repin-review-deployment.md"]
---

# Fulfillment: review-environment receipt, evidence and launcher port

## State check

**Not previously shipped.** At v0.37.0 `delivery.deployment-receipt` and
`delivery.evidence` both pinned `environment.name` to `dev`, `delivery.evidence` forced
`revisionRole: merged` for `deployment`/`live`, and no launcher API existed under
`schemas/`. The session opened by the dispatcher held only its stub (no commits, tag or
report). This session did the work.

## What shipped

Tag **`v0.38.0`** (commit `1445ca4`, pushed), pinned worktree
`../contracts-worktrees/v0.38.0`. **Additive**; reference is `docs/task-delivery.md`
§Review environments.

| Criterion | Where |
|---|---|
| Receipt can describe a review environment: name `review` | `environment.name` is `dev \| review` |
| Served revision with role `task` (PR head, not merged) | new optional `revisionRole`; `mergedRevision` keeps its name and holds the PR head; a `review` receipt must have `revisionRole: task` |
| PR/branch reference | receipt `branch` (PR head branch) plus new `review {pullRequest, pullRequestUrl}` (nullable members) |
| Frontend URL + optional Swagger URL | `environment.url` is the frontend URL; new optional nullable `environment.apiDocsUrl` |
| Dev receipts valid unchanged | all new fields optional; every v0.36.0 fixture still validates; a dev receipt may not carry `review`, `apiDocsUrl` or a `task` role |
| Evidence accepts review observations at the task revision | `delivery.evidence.environment.name` is `dev \| review`; `deployment`/`live` require `revisionRole: task` for `review` and still `merged` for `dev` |
| Launcher review-environment OpenAPI | `schemas/launcher/review-environment.openapi.yaml`: `POST /review/v1/environments` (repository, branch, pullRequest, expectedRevision, idempotencyKey), `GET` and `DELETE /review/v1/environments/{idempotencyKey}`; status `starting \| ready \| failed \| stopped` coupled to the receipt; `review_environment_not_found` 404 as the machine-distinguishable miss |
| Python bindings + tests | bindings regenerated; `tests/validate_delivery.py` now 139 cases |

Tests cover: a review receipt; a dev receipt unchanged (plus one with explicit
`revisionRole: merged`); a revision mismatch recorded as `failed` (receipt, evidence,
producer-result mapping and a `failed` environment in the launcher API); an unreported
identity staying `null` (receipt settles `unknown`, mapping yields `environment: null`,
and a `ready` environment with such a receipt is rejected); a `passed` mismatch caught by
the semantic checks; review evidence at the task revision; and negatives for the
role/env conditionals.

## Decisions I made where the demand was silent

- **`stopped` status.** The demand listed starting/ready/failed; stop needs a terminal
  state, so the status enum also has `stopped` (the last receipt is retained).
- **`mergedRevision` not renamed.** Renaming would break every dev receipt; the field
  holds the PR head for review, with `revisionRole` disambiguating.
- **No review-specific `rollback`.** A review receipt requires `kind: deploy` and
  `rollback: null`; a review environment is stopped, not rolled back.
- **`delivery.producer-result` unchanged in meaning.** It has no role field; the role
  is read from the receipt via `nativeRef`.

## D031 acceptance (real tag)

- **Python:** fresh venv, `pip install --no-cache-dir "platform-contracts @
  git+https://github.com/elmoul/contracts.git@v0.38.0#subdirectory=gen/python"`;
  installed version `0.38.0` from site-packages; a review receipt with an unreported
  identity round-trips (`environment.name == review`, `observed.revision is None`,
  `revisionRole == task`).
- **TypeScript:** fresh project with a `file:` dependency on the `v0.38.0` worktree and
  a fresh npm cache; `tsc --strict --noEmit` accepts `environment.name = "review"` and
  `revisionRole`.
- `python tests/run_all.py` passes; `tsc --noEmit --strict` on `gen/ts` passes.

## What the origin must know

- As before, the generated bindings do not enforce the `if/then` rules (a review
  receipt without `review`, a task-role dev receipt, a `ready` environment whose receipt
  is not `passed`). The equality `deployedRevision == revision` and
  `observed.revision == expectedRevision` has no JSON Schema keyword: Factory and
  launcher enforce it (`check_review_evidence_semantics` and `check_deployment_semantics`
  are the executable references).
- `delivery_error` (Python/TS) picked up the `deployment_not_found` code that v0.37.0
  added to the schema but never regenerated. Additive, no behavior change.
- D043 origin demand raised: `demands/2026-09-30-factory-repin-review-deployment.md`.
  The release is additive, so no consumer demands were raised. `launcher` implements
  the port on its own demand from Factory.

## Not done / caveats

- No launcher implementation and no Factory evidence recording; both are consumer legs.
- `schemas/` is still not bundled in the Python wheel (open packaging gap), so
  validating against the JSON Schema needs the tag checkout.
- The vault (port registration for launcher's review-environment API, a decision entry)
  is not touched; that goes through a `platform-vault` demand if the owner wants it.
