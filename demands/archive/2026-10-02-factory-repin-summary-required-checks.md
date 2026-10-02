---
id: contracts-20261002-factory-repin-summary-required-checks
date: 2026-10-02
from: contracts
to: [factory]
capability: Close the consuming leg of factory-20261002-contracts-summary-required-checks - requiredChecks, appRoot and releaseBranch on the registry app summary shipped in contracts v0.44.0
acceptance-criteria:
  - "factory reviews contracts v0.44.0 (optional requiredChecks, appRoot and releaseBranch on the app object of schemas/control-plane/registry.entry.json; the Python and TypeScript bindings) and either accepts it or raises the specific gaps back to contracts."
  - "Factory re-pins to v0.44.0 and reads required checks, app root and release branch from the registry app record instead of hard-coded check names and a fixed branch."
needs-owner: false
status: archived
---

# Summary required checks: close the consuming leg

`contracts` **v0.44.0** mirrors `delivery.requiredChecks`, `code.appRoot` and `code.releaseBranch` into the
optional `app` summary on `registry.entry`. Additive; nothing existing changed. Details in
`demands/fulfilled/factory-20261002-contracts-summary-required-checks-report.md`.

## Why
D043 release duty: the origin closes its consuming leg. Additive, so no other consumer is obligated to move (D031).
