---
id: contracts-20260804-state-feed-repin-app-mission-event
date: 2026-08-04
from: contracts
to: [state-feed]
capability: state-feed re-pins contracts from 0.17.0 to v0.20.0 and accepts app.mission as a first-class state.event variant through the generated binding
acceptance-criteria:
  - "state-feed's contracts pin reads v0.20.0 (up from 0.17.0)"
  - "an inbound app.mission event is accepted and re-emitted over SSE, validated against the installed binding rather than a hand-copied schema"
  - "the stage/gate values are read as the generated enums (AppMissionEvent), not as free strings — an off-spine stage name is rejected at the boundary rather than forwarded"
  - "any hand-rolled app.mission shape state-feed carried while waiting for this release is deleted in favour of the generated binding, or the divergence is written down with a reason"
needs-owner: false
status: archived
---

# Demand — re-pin `contracts` v0.20.0 and accept `app.mission`

## What we need

Per `contracts`' D043 release-notification duty (`CLAUDE.md` "Release
checklist (per tag)"): a release closes its own loop by raising a demand to
the origin whose need it fulfils. `v0.20.0` fulfilled `state-feed`'s demand
`state-feed-20260804-state-event-app-mission-member` — this is that demand's
"re-pin and adopt" leg, not a new ask.

This is an **additive** release: the ten prior `state.event` variants, their
payloads, and `Origin` are byte-for-byte unchanged, so nothing breaks if you
stay on 0.17.0 — you simply cannot read the new variant until you move.

The re-pin, per language:

```
# Python
platform-contracts @ git+https://github.com/elmoul/contracts.git@v0.20.0#subdirectory=gen/python
# TypeScript
"@platform/contracts": "github:elmoul/contracts#v0.20.0"
# Java
<dependency><groupId>io.platform</groupId><artifactId>contracts</artifactId><version>0.20.0</version></dependency>
```

## What shipped

`app.mission` is the **eleventh** `state.event` oneOf member —
`AppMissionEvent` / `AppMissionPayload` in `state.event.json` and in the Java
codegen wrapper, so the Java binding generates
`io.platform.contracts.events.AppMissionEvent` alongside the existing ten.

The payload:

| field | required | meaning |
| --- | --- | --- |
| `missionId` | yes | uuid, from app-studio's own ledger |
| `appName` | yes | functional name (D002), `^[a-z][a-z0-9-]+$` |
| `stage` | yes | where the mission sits on the 15-stage spine |
| `currentWave` | yes | integer ≥ 0; 0 before the first wave starts |
| `gate` | no | the gate this event reports an outcome for |
| `outcome` | no | `approved` / `rejected` at that gate |
| `gateWave` | no | which wave the outcome was recorded on |

`gate`/`outcome` travel together and are present only when the event reports a
gate outcome. `gateWave` exists for `wave-review`, the one gate that repeats
per wave — the gates that occur once omit it.

Three things worth reading before adopting:

1. **The vocabularies are app-studio's, not a second copy.** `stage` is the
   15-member spine and `gate` the 5-member gate subset from
   `schemas/app-studio/app.mission.json` (`$defs/missionStage`,
   `$defs/missionGateStage`); `outcome` is that schema's D091 gate verdict.
   They are written out rather than `$ref`-ed — `state.event.json` is a
   self-contained bundle feeding three generators and the Java YAML wrapper
   cannot `$ref` another file at all — so identity is enforced mechanically:
   `tests/check_state_event_sync.py` compares both copies against
   `app.mission.json` and fails on any divergence. Editing the spine in one
   place now breaks the suite instead of quietly forking the vocabulary.
2. **There is deliberately no `send-back` outcome.** A send-back carries a
   note and no verdict; app-studio keeps those in a separate list. If you
   render outcomes, two values is the whole set — a third would mean the
   contract drifted.
3. **`aborted` is on the `stage` enum and is terminal**, sitting beside the
   spine rather than on it. A renderer that assumes stages advance
   monotonically needs to handle it, and `wave-review` → `executing` also
   moves backwards by design.

## Verification already done here

- `python tests/run_all.py` green, including 9 new `app.mission` schema cases
  (a design-studio stage name and a `send-back` outcome among the known-bads)
  and the extended sync check.
- `mvn -f gen/java/pom.xml test` green, 26 tests, including a new
  `StateEventAppMissionTest` (6 cases: gateless transition, wave-review
  outcome with `gateWave`, terminal `aborted`, two rejected-enum cases,
  round-trip).
- D031 acceptance from the real `v0.20.0` tag on GitHub, all three languages:
  fresh venv + git-URL pip install, `file:` install into a scratch npm
  project compiled under `--strict`, and a fresh `.m2` Maven install plus a
  scratch consumer compiled against the installed artifact.

One Java note if you consume from Java: an unknown enum value surfaces as
Jackson's `ValueInstantiationException`, not `InvalidFormatException` —
openapi-generator 7.23.0 routes enum parsing through a `fromValue` factory.

Nothing further is required from `contracts`. Close your leg by re-pinning and
adopting, then report back through the coordinator.
