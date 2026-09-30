---
demandId: platform-vault-20260930-contracts-d115-java-bindings
worker: contracts
date: 2026-09-30
status: done
shipped: ["v0.40.0", "commit 0f347aa on main (feat(java): generate D115 parked.* bindings, pom 0.40.0 (v0.40.0))", "gen/java/pom.xml: agent-runner-parked jsonschema2pojo execution, version 0.34.0 -> 0.40.0", "Java package io.platform.contracts.agentrunner: ParkedRunResult, ParkedConditionEvent, ParkedResumeRequest, RunnerDispatchRequest, Wait, Reference", "pinned worktree ../contracts-worktrees/v0.40.0", "D043 origin demand demands/2026-09-30-platform-vault-repin-d115-java-bindings.md"]
---

# Fulfillment: D115 parked.* Java bindings

## State check
**Not previously shipped.** At v0.39.0 `gen/java/pom.xml` had no agent-runner execution and
was still `0.34.0`; no `io.platform.contracts.agentrunner` classes existed.

## What shipped
Tag **`v0.40.0`** (commit `0f347aa`, pushed), additive, no existing schema changed.

- New `agent-runner-parked` execution in `gen/java/pom.xml` over the four
  `schemas/agent-runner/parked.*.json` files; `mvn -f gen/java/pom.xml test` is green.
- `pom.xml` version is now `0.40.0` (matches the tag).
- Classes (package `io.platform.contracts.agentrunner`): `ParkedRunResult`,
  `ParkedConditionEvent`, `ParkedResumeRequest`, `Wait`, `Reference`, and
  `RunnerDispatchRequest` (pulled in by `parked.resume-request`'s `$ref`).

## Known limitation
`parked.wait-condition.json` has a root `oneOf`; jsonschema2pojo cannot generate per-variant
classes from that (same limitation as `state.event`). There is therefore no
`ParkedWaitCondition` class, and `ParkedRunResult.wait.condition` is typed `Object`
(a Jackson map on the wire). The JSON shape is unaffected; consumers needing typed variants
would need a separate demand (an openapi-generator path like state-event-java.yaml).

## Install coordinates (D031-verified from the tag)
Maven coordinates `io.platform:contracts:0.40.0`. There is no registry; build from the tag:

```
git clone --branch v0.40.0 https://github.com/elmoul/contracts.git
mvn -f contracts/gen/java/pom.xml install
```

Verification: fresh clone of tag `v0.40.0` from GitHub, `mvn install` with an empty
`-Dmaven.repo.local`, exit 0; `contracts-0.40.0.jar` contains all the `agentrunner/*` classes.
Consumers then depend on `io.platform:contracts:0.40.0`.
