---
id: contracts-20260804-app-studio-repin-binding-direction-array
date: 2026-08-04
from: contracts
to: [app-studio]
capability: app-studio re-pins contracts to v0.21.0 and reads gateContext.bindingDirection as a list of directions rather than a single string
acceptance-criteria:
  - "app-studio's contracts pin reads v0.21.0"
  - "every read and write of gateContext.bindingDirection handles a list — a gate that has rejected twice renders both directions, not just the latest"
  - "the projection that computes gateContext emits a list (oldest first) whose length tracks priorRounds, and null when the gate has never rejected"
  - "any local type, DTO or hand-rolled shape that still declares bindingDirection as a string is removed in favour of the generated binding, or the divergence is written down with a reason"
needs-owner: false
status: archived
---

# Demand — re-pin `contracts` v0.21.0 and read `bindingDirection` as a list

## What we need

Per `contracts`' D043 release-notification duty (`CLAUDE.md` "Release
checklist (per tag)"): a release closes its own loop by raising a demand to
the origin whose need it fulfils. `v0.21.0` fulfilled `app-studio`'s demand
`app-studio-20260804-contracts-binding-direction-array` — this is that
demand's "re-pin and adopt" leg, not a new ask.

## This one is breaking — a string-typed consumer will break

`app.mission`'s `gateContext.bindingDirection` changed from a nullable
**string** to a nullable **array of strings**:

| binding | v0.20.0 | v0.21.0 |
|---|---|---|
| TypeScript | `bindingDirection?: string \| null` | `bindingDirection?: string[] \| null` |
| Python | `bindingDirection: str \| None` | `bindingDirection: list[str] \| None` |
| Java | `private String bindingDirection` | `private List<String> bindingDirection` |

TS and Java call sites fail to compile; Python fails at parse time with a
pydantic `ValidationError`; anything hand-parsing the JSON silently receives a
list where it expected a string. Mechanical migration is `bindingDirection` →
`bindingDirection?.[0]`, but the point of the change is that reading only the
first (or only the last) direction is the defect — a gate that has rejected
twice binds the owner to *both* directions, and the earlier one does not stop
being binding because a later one arrived. Render them all.

`null` is unchanged and still means "this gate has never rejected".

## The re-pin, per language

```
# Python
platform-contracts @ git+https://github.com/elmoul/contracts.git@v0.21.0#subdirectory=gen/python
# TypeScript — file: against a v0.21.0 checkout (npm's github: form does not
# work for this repo; package.json is at gen/ts, not the repo root — DEPLOYMENT.md)
"@platform/contracts": "file:../contracts/gen/ts"
# Java
<dependency><groupId>io.platform</groupId><artifactId>contracts</artifactId><version>0.21.0</version></dependency>
```

All three were installed from the `v0.21.0` tag in a fresh venv / npm cache /
`.m2` before this demand was raised (D031 acceptance), and the list type was
confirmed in each installed artifact.

## Scope note — no fleet-wide demand

The breaking-release leg of D043 (demand every consumer of the changed schema)
resolves to `app-studio` alone here. The only other reader of `app.mission` is
state-feed's `AppMissionEvent` payload, which carries `missionId` / `appName` /
`stage` / `currentWave` / `gate` / `outcome` / `gateWave` and no `gateContext`
at all — unaffected. This was established from the schemas in this repo;
control-plane's `GET /registry` consumer graph was not reachable from the
release session to cross-check.
