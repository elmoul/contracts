---
id: contracts-20261003-factory-repin-commands-cleanup
date: 2026-10-03
from: contracts
to: [factory]
capability: Close the consuming leg of factory-20261003-contracts-commands-cleanup - optional commands.cleanup on app.descriptor shipped in contracts v0.46.0
acceptance-criteria:
  - "factory reviews contracts v0.46.0 (optional commands.cleanup argv array on app.descriptor, with the COMMAND_PARAM_BRANCH / COMMAND_PARAM_COMMIT environment and exit 0 / exit 3 / other contract, in schemas/app/descriptor.json; the Python and TypeScript bindings) and either accepts it or raises the specific gaps back to contracts."
  - "Factory re-pins to v0.46.0 so the launcher can offer cleanup per app without a hand-kept allowlist entry."
needs-owner: false
status: open
---

# Commands cleanup: close the consuming leg

`contracts` **v0.46.0** adds optional `commands.cleanup` to `app.descriptor`. Additive; nothing existing changed.
Details in `demands/fulfilled/factory-20261003-contracts-commands-cleanup-report.md`.

## Why
D043 release duty: the origin closes its consuming leg. Additive, so no other consumer is obligated to move (D031).
