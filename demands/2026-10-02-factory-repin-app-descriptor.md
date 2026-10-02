---
id: contracts-20261002-factory-repin-app-descriptor
date: 2026-10-02
from: contracts
to: [factory]
capability: Close the consuming leg of factory-20261002-contracts-app-descriptor - the app.descriptor schema and the registry entry app summary shipped in contracts v0.42.0
acceptance-criteria:
  - "factory reviews contracts v0.42.0 (schemas/app/descriptor.json, the optional `app` object on schemas/control-plane/registry.entry.json, and the Java/Python/TypeScript bindings) and either accepts it or raises the specific gaps back to contracts."
  - "The five dependent demands (control-plane, launcher, factory, conventions, brain-toolkit) name v0.42.0 as the pin."
needs-owner: false
status: open
---

# app.descriptor: close the consuming leg

`contracts` **v0.42.0** adds `app.descriptor` (the `app.yaml` shape) and an optional `app`
summary on `registry.entry`. Additive; no existing schema changed. Details in
`demands/fulfilled/factory-20261002-contracts-app-descriptor-report.md`.

Note for consumers: the enforced rules are `if/then`, which the Python and TypeScript
generators do not emit, so validate `app.yaml` against `schemas/app/descriptor.json` rather
than relying on the generated types.

## Why
D043 release duty: the origin closes its consuming leg. Additive, so no other consumer is obligated to move (D031).
