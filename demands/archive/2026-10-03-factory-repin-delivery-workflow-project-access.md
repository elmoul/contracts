---
id: contracts-20261003-factory-repin-delivery-workflow-project-access
date: 2026-10-03
from: contracts
to: [factory]
capability: Close the consuming leg of factory-20261003-contracts-delivery-workflow-project-access - optional access on delivery.workflow shipped in contracts v0.47.0
acceptance-criteria:
  - "factory reviews contracts v0.47.0 (optional access on delivery.workflow, closed values delivery and read-only, absent means the producer does not say, in schemas/delivery/delivery.workflow.json; worked examples in schemas/delivery-api/youtrack-delivery.openapi.yaml; Python and TypeScript bindings) and either accepts it or raises the specific gaps back to contracts."
  - "Factory re-pins to v0.47.0 and reads access instead of inferring whether a project is open to delivery; it treats an absent access as not stated. Consumers pin the tag before any producer starts sending access, so factory and youtrack must both be on v0.47.0 first."
needs-owner: false
status: archived
---

# delivery.workflow access: close the consuming leg

`contracts` **v0.47.0** adds optional `access` (`delivery` | `read-only`) to `delivery.workflow`. Additive; nothing existing changed.
Details in `demands/fulfilled/factory-20261003-contracts-delivery-workflow-project-access-report.md`.

## Why
D043 release duty: the origin closes its consuming leg. Additive, so no other consumer is obligated to move (D031); the
producer (`youtrack`) is told the rollout order by the schema description and must not send `access` until factory has pinned.
