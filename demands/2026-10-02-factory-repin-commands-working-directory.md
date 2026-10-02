---
id: contracts-20261002-factory-repin-commands-working-directory
date: 2026-10-02
from: contracts
to: [factory]
capability: Close the consuming leg of factory-20261002-contracts-commands-working-directory - optional commands.workingDirectory on app.descriptor shipped in contracts v0.45.0
acceptance-criteria:
  - "factory reviews contracts v0.45.0 (optional commands.workingDirectory, enum hexagon or app, default hexagon, in schemas/app/descriptor.json; the Python and TypeScript bindings) and either accepts it or raises the specific gaps back to contracts."
  - "Factory re-pins to v0.45.0 so the wrap migration script can write and validate the field."
needs-owner: false
status: open
---

# Commands working directory: close the consuming leg

`contracts` **v0.45.0** adds optional `commands.workingDirectory` (`hexagon` | `app`, default `hexagon`) to
`app.descriptor`. Additive; nothing existing changed. Details in
`demands/fulfilled/factory-20261002-contracts-commands-working-directory-report.md`.

## Why
D043 release duty: the origin closes its consuming leg. Additive, so no other consumer is obligated to move (D031).
