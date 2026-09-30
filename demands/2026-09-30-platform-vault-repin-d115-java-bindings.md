---
id: contracts-20260930-platform-vault-repin-d115-java-bindings
date: 2026-09-30
from: contracts
to: [platform-vault]
capability: Close the consuming leg of platform-vault-20260930-contracts-d115-java-bindings - the D115 parked.* Java bindings shipped in contracts v0.40.0
acceptance-criteria:
  - "platform-vault reviews contracts v0.40.0 (gen/java io.platform.contracts.agentrunner parked classes) and either accepts it or raises the specific gaps back to contracts, including the Object-typed wait.condition limitation."
  - "Follow-up demands for Java consumers name v0.40.0 (io.platform:contracts:0.40.0, built from the tag) as the pin."
needs-owner: false
status: open
---

# D115 Java bindings: close the consuming leg

`contracts` **v0.40.0** generates the four D115 `parked.*` shapes into the Java bindings
(package `io.platform.contracts.agentrunner`) and bumps the Java package to 0.40.0.
Additive; no schema changed. Install and the `wait.condition` limitation are in
`demands/fulfilled/platform-vault-20260930-contracts-d115-java-bindings-report.md`.

## Why
D043 release duty: the origin closes its consuming leg. Additive, so no other consumer is obligated to move (D031).
