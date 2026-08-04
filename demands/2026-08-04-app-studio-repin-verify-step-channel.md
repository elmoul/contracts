---
id: contracts-20260804-app-studio-repin-verify-step-channel
date: 2026-08-04
from: contracts
to: [app-studio]
capability: app-studio re-pins contracts to v0.22.0 and adopts the verify step's optional `channel`, dropping the recorded gap
acceptance-criteria:
  - "app-studio's contracts pin reads v0.22.0"
  - "an absence verify step produced by the planner carries `channel` — the input path the excluded thing would have travelled on — rather than leaving the claim unfalsifiable"
  - "positive verify steps are left without a channel; the field is not filled in reflexively"
  - "the recorded gap for this missing field is dropped"
  - "any local type or hand-rolled verify-step shape declaring channel itself is removed in favour of the generated binding, or the divergence is written down with a reason"
needs-owner: false
status: open
---

# Demand — re-pin `contracts` v0.22.0 and adopt `verify.channel`

## What we need

Per `contracts`' D043 release-notification duty (`CLAUDE.md` "Release
checklist (per tag)"): a release closes its own loop by raising a demand to
the origin whose need it fulfils. `v0.22.0` fulfilled `app-studio`'s demand
`app-studio-20260804-contracts-verify-step-channel` — this is that demand's
"re-pin and adopt" leg, not a new ask.

## This one is additive — nothing of yours breaks

`app.task-plan`'s verify step gains an **optional** string `channel`:

> for an absence claim only: the input path (field, map key, header, argument)
> that could carry the thing being excluded

| binding | v0.22.0 |
|---|---|
| TypeScript | `channel?: string` on `VerifyStep` |
| Python | `channel: str \| None = None` |
| Java | `private String channel` on `VerifyStep` |

Every existing plan artifact — none of which carries the field — validates
unchanged against v0.22.0. The re-pin is a version bump, not a migration.

One Java note if you construct verify steps in Java: jsonschema2pojo's
all-args `VerifyStep` constructor gains a fourth parameter, so a call site
using that constructor (rather than no-arg + setters) needs the extra
argument. Getters, setters and JSON round-tripping are unchanged.

## What adoption actually means

The pin is the easy half. The field earns its keep only when the planner fills
it on absence steps: `expect` says what must not be true, `channel` says where
to look. "The API key never reaches the provider" is unfalsifiable until the
step names where the key would have travelled if it had — the `metadata` map
on the outbound request, the `Authorization` header, the argument passed to
the tool. On a positive step the field is meaningless and should stay unset,
which is why it is optional rather than conditionally required.

## The re-pin, per language

```
# Python
platform-contracts @ git+https://github.com/elmoul/contracts.git@v0.22.0#subdirectory=gen/python
# TypeScript — file: against a v0.22.0 checkout (npm's github: form does not
# work for this repo; package.json is at gen/ts, not the repo root — DEPLOYMENT.md)
"@platform/contracts": "file:../contracts/gen/ts"
# Java
<dependency><groupId>io.platform</groupId><artifactId>contracts</artifactId><version>0.22.0</version></dependency>
```

All three were installed from the `v0.22.0` tag into a fresh venv / npm cache
/ `.m2` before this demand was raised (D031 acceptance), and the optional
string `channel` was confirmed in each installed artifact.

## Scope note — no fleet-wide demand

D043 raises consumer-wide demands on a **breaking** release only. This one is
additive: D031 pins are deliberate, and an additive release obligates no
consumer to move. So this demand goes to the origin `app-studio` and to no one
else — `state-feed`'s `AppMissionEvent` payload, the only other app-studio
schema reader in this repo, does not touch `app.task-plan` at all.
