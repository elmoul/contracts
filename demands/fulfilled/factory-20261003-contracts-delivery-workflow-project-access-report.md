---
demandId: factory-20261003-contracts-delivery-workflow-project-access
worker: contracts
date: 2026-10-03
status: done
shipped: ["v0.47.0", "commit 2ba81f2 on main (feat(delivery): optional access on delivery.workflow (v0.47.0))", "schemas/delivery/delivery.workflow.json (optional access, enum delivery | read-only)", "schemas/delivery-api/youtrack-delivery.openapi.yaml (access described, worked examples delivery / read-only / absent)", "tests/validate_delivery.py cases: access delivery, access read-only, no access, unknown value rejected", "Python and TypeScript bindings 0.47.0 (Java version bumped, output unchanged)", "CHANGELOG v0.47.0 entry", "pinned worktree ../contracts-worktrees/v0.47.0", "D043 origin demand demands/2026-10-03-factory-repin-delivery-workflow-project-access.md"]
---

# Fulfillment: delivery.workflow access

## State check

Not shipped before this session: no `access` property in `delivery.workflow.json` or the OpenAPI document at v0.46.0.

## What shipped

Tag `v0.47.0` (commit `2ba81f2`, pushed to `origin/main`):

- `delivery.workflow` gains optional `access`, `type: string`, `enum: [delivery, read-only]`, not in `required`. The
  description states what each value means (`read-only`: reads work, comments/transitions/operations refused with
  `project_not_enabled`), that absent means the producer does not say, and the rollout order: consumers pin the tag
  before any producer starts sending `access` (the shape is closed, so an older pin rejects a document that carries it).
- `youtrack-delivery.openapi.yaml`: the workflow route describes `access`; the 200 response has examples `deliveryOpen`,
  `readOnly` and `accessNotStated`.
- Cases in `tests/validate_delivery.py` (the delivery validators keep fixtures inline): valid with `access: delivery`,
  valid with `access: read-only`, valid without `access` (the existing case), invalid with `access: write`. Positive
  cases also round-trip through the Python binding.
- Bindings regenerated: `gen/python/.../delivery_workflow.py` (`access: Access | None`, `StrEnum`) and
  `gen/ts/delivery-workflow.ts` (`access?: "delivery" | "read-only"`, `dist/` rebuilt). Versions 0.47.0 in all three
  manifests.

## Evidence

- `python tests/run_all.py`: all validators passed.
- D031 from the real tag, fresh venv: `pip install "git+https://github.com/elmoul/contracts.git@v0.47.0#subdirectory=gen/python"`
  gives `platform-contracts 0.47.0`; `DeliveryWorkflow` accepts no access (`None`) and `read-only`, rejects `write`.
- D031 TypeScript: clone at tag v0.47.0, fresh npm cache, `file:` dependency on `gen/ts`; `tsc --strict` accepts
  `"read-only"` and `undefined` for `DeliveryWorkflow["access"]` and rejects `"write"`.
- Worktree `../contracts-worktrees/v0.47.0` created.

## Consuming leg

Per D043 an origin demand `contracts-20261003-factory-repin-delivery-workflow-project-access` is raised to `factory`.
Additive release: no fleet-wide consumer demand. `youtrack` (the producer) should pin `v0.47.0` before it starts sending `access`.
