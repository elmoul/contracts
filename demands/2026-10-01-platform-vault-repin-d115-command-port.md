---
id: contracts-20261001-platform-vault-repin-d115-command-port
date: 2026-10-01
from: contracts
to: [platform-vault]
capability: Close the consuming leg of platform-vault-20260930-contracts-d115-command-port - the D115 command-execution port shapes shipped in contracts v0.41.0
acceptance-criteria:
  - "platform-vault reviews contracts v0.41.0 (schemas/launcher/command.request, command.result, command.error and the Java/Python/TypeScript bindings) and either accepts it or raises the specific gaps back to contracts."
  - "Follow-up demands for launcher and factory name v0.41.0 as the pin."
needs-owner: false
status: open
---

# D115 command port: close the consuming leg

`contracts` **v0.41.0** adds the three `launcher` command-port shapes and generates Java,
Python and TypeScript bindings. Additive; no existing schema changed. Details in
`demands/fulfilled/platform-vault-20260930-contracts-d115-command-port-report.md`.

## Why
D043 release duty: the origin closes its consuming leg. Additive, so no other consumer is obligated to move (D031).
