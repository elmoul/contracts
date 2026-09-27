---
id: contracts-20260927-factory-repin-task-delivery
date: 2026-09-27
from: contracts
to: [factory]
capability: Close the consuming leg of factory-20260927-task-delivery-contracts — D113 task-delivery interfaces shipped in contracts v0.31.0
acceptance-criteria:
  - "factory reviews contracts v0.31.0 (schemas/delivery/, schemas/delivery-api/youtrack-delivery.openapi.yaml, docs/task-delivery.md) against D113 and either accepts it or raises the specific interface gaps back to contracts."
  - "factory re-pins to v0.31.0 at its reviewed integration step (package, image, descriptor and tests together) and confirms its stored v0.25.0 evidence receipts still load unchanged."
  - "factory raises its downstream producer demands (youtrack, agent-runner/ci-runner, plantpal/runtime/gateway) naming v0.31.0 and the gaps listed in docs/task-delivery.md §Producers, or explains why not."
needs-owner: false
status: archived
---

# D113 task delivery: close the consuming leg

## What we need

`contracts` **v0.31.0** shipped what `factory-20260927-task-delivery-contracts`
asked for:

- `schemas/delivery/`: `delivery.issue-ref`, `delivery.issue`,
  `delivery.issue-page`, `delivery.workflow`, `delivery.sync-request`,
  `delivery.sync-operation`, `delivery.error`, `delivery.evidence`,
  `delivery.decision`, `delivery.producer-result`.
- `schemas/delivery-api/youtrack-delivery.openapi.yaml`: `/delivery/v1` routes for
  the `youtrack` service.
- `docs/task-delivery.md` covers recovery semantics, resolve enforcement, the
  producer mapping and gaps, the handoff matrix and repin steps.
- Python: `platform_contracts.delivery.*`
  (`git+https://github.com/elmoul/contracts.git@v0.31.0#subdirectory=gen/python`).
  TypeScript: `delivery-*.ts` in `@platform/contracts`
  (`../contracts-worktrees/v0.31.0/gen/ts`).

The release is additive. `factory.*`, `agent_runner.*` and planner shapes are
unchanged, so moving from v0.25.0 changes nothing already in use.

Note: the generated classes do not enforce the schemas' `if/then` rules (see the
fulfillment report's binding caveat). Validate against the JSON Schema where those
rules matter.

## Why

D043 release duty: the origin closes its consuming leg. No service implements
these interfaces yet; this release does not make any endpoint or dev delivery
live.
