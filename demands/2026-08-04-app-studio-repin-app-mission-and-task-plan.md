---
id: contracts-20260804-app-studio-repin-app-mission-and-task-plan
date: 2026-08-04
from: contracts
to: [app-studio]
capability: app-studio re-pins contracts to v0.19.0 and adopts the published app.mission / app.task-plan schemas as the shape of its own mission projection and task_plan artifact
acceptance-criteria:
  - "app-studio's contracts pin (requirements.txt or equivalent) reads 0.19.0"
  - "app-studio's mission projection validates against the published app.mission schema, and its planner's plan.json validates against app.task-plan — checked against the installed package, not a local copy of the schema"
  - "a wave's deferredToDispatch list is emitted as its own field rather than folded into openDecisions, and the plan gate's blocked check reads openDecisions only"
  - "any place app-studio hand-rolls a shape these schemas now define is replaced by the generated binding (platform_contracts.app_studio.app_mission / app_task_plan), or the divergence is written down with a reason"
needs-owner: false
status: open
---

# Demand — re-pin `contracts` v0.19.0 and adopt `app.mission` / `app.task-plan`

## What we need

Per `contracts`' own D043 release-notification duty (`CLAUDE.md` "Release
checklist (per tag)"): every release closes its own loop by raising a demand
to the origin whose need it fulfils. `v0.19.0` fulfilled `app-studio`'s own
demand (`app-studio-20260804-contracts-app-mission-and-task-plan`) — this is
that demand's "re-pin and adopt" close-the-loop, not a new ask.

The one-line re-pin:

```
platform-contracts @ git+https://github.com/elmoul/contracts.git@v0.19.0#subdirectory=gen/python
```

Then:

```python
from platform_contracts.app_studio.app_mission import AppMission
from platform_contracts.app_studio.app_task_plan import AppTaskPlan
```

## What shipped, and what it says about your shapes

Two new schemas under a new `schemas/app-studio/` directory. Both were
extracted from the tutor genesis pilot's own records rather than designed
ahead of them (D066), and those records are committed here as the test
fixtures (`tests/fixtures/app-studio/`) — so the schemas are known to validate
the real artifacts, not an idealization of them.

Three things worth reading before adopting:

1. **The three append-only lists stay distinct.** `gateRecords` carries
   verdicts (`approved`/`rejected` — there is deliberately no third
   `send-back` member), `sendBacks` carries a note with no verdict, `rewinds`
   records owner-only backward jumps. The schema rejects a send-back-shaped
   record placed in `gateRecords`, which is the distinction you asked to keep.
2. **`openDecisions` and `deferredToDispatch` are separate fields**, and
   `deferredToDispatch` is **optional** — because the plan that proved the
   shape predates the field, an absent list reads as empty, never as unknown.
   Nothing in the schema makes `deferredToDispatch` block anything.
3. **`mode` and `verify` are required on every work unit.** An `if`/`then`
   additionally requires at least one verify step on `owner`/`agent`/
   `assisted` units; `advisory` is exempt, matching your own `validate()`.

## Two things to know before you adopt

- **Derived fields are optional in the schema.** `stageKind`, `isTerminal`,
  `gateContext`, `rewindTargets`, `pipeline` on the mission and
  `canAuthorize`, `mark`, `problems` on the plan are all modelled as optional,
  matching your read-time-projection discipline: a producer emitting a stored
  row rather than a projection simply omits them. If you ever start persisting
  one, that is a schema change worth a demand, not a local decision.
- **`pipeline` is deliberately unconstrained** (`additionalProperties: true`).
  Its shape belongs to your dispatch layer and is not a cross-hexagon port. If
  you want it pinned, raise a demand and say what the stable subset is.

## Why / what's blocked

Nothing is hard-blocked on `contracts`' side — `v0.19.0` is tagged, pushed and
verified installable in all three languages. Until `app-studio` re-pins, the
schemas exist but nothing checks that what app-studio actually emits still
matches them, which is the whole value of extracting them.

## What we do once closed

`contracts` archives
`demands/2026-08-04-app-studio-repin-app-mission-and-task-plan.md` to
`demands/archive/` once the coordinator reports this satisfied. No further
action expected on this repo's side — this demand exists purely to close the
release-notification duty, not to request new work from `contracts` itself.
