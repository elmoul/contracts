---
id: contracts-20260805-app-studio-repin-mission-consistency
date: 2026-08-05
from: contracts
to: [app-studio]
capability: app-studio re-pins contracts to v0.23.0 and, wherever it computes a ledger-vs-artifact divergence check today (or wants to), emits it through the new app.mission `consistency` field rather than a bespoke shape
acceptance-criteria:
  - "app-studio's contracts pin (requirements.txt or equivalent) reads 0.23.0"
  - "app-studio's mission projection (projection.project()) sets `consistency` to null wherever reconciliation hasn't run, and to a populated `{consistent, checkedAt, divergences}` object wherever it has — checked against the installed package, not a local copy of the schema"
  - "any place app-studio already surfaces a ledger-vs-artifact contradiction (console note, log line, ad-hoc field) is replaced by `consistency`, or the divergence from this shape is written down with a reason"
needs-owner: false
status: archived
---

# Demand — re-pin `contracts` v0.23.0 and adopt `app.mission.consistency`

## What we need

Per `contracts`' D043 release-notification duty (`CLAUDE.md` "Release
checklist (per tag)"): every release closes its own loop by raising a demand
to the origin whose need it fulfils. `v0.23.0` fulfils `app-studio`'s own
demand `app-studio-20260805-contracts-mission-consistency` — this is that
demand's "re-pin and adopt" close-the-loop, not a new ask.

Additive release — no other consumer of `app.mission` is obligated to move
(D031 pins are deliberate); this demand goes to the origin only.

The one-line re-pin:

```
platform-contracts @ git+https://github.com/elmoul/contracts.git@v0.23.0#subdirectory=gen/python
```

```python
from platform_contracts.app_studio.app_mission import AppMission, Consistency, Divergence
```

## What shipped

`app.mission` gains an optional `consistency` object, DERIVED like
`gateContext`/`pipeline` — computed at read time by `projection.project()`,
never persisted:

```json
"consistency": {
  "consistent": false,
  "checkedAt": "2026-08-05T07:00:00+00:00",
  "divergences": [
    {
      "subject": "currentWave",
      "ledgerValue": 2,
      "artifactValue": 1,
      "description": "ledger says wave 2 but task_plan.json has no wave 2 entry"
    }
  ]
}
```

- Null when reconciliation hasn't run: a producer emitting a stored row
  rather than a projection, or a mission with no artifact yet to diverge from
  (before `scaffold`/`planning`).
- `divergences` empty exactly when `consistent` is true.
- Each divergence names the `subject` that disagrees, the ledger's and the
  artifact's own values for it (deliberately unconstrained — the field types
  vary by subject, same precedent as `pipeline`), and a `description` in the
  owner's own terms. Mirrors `app.task-plan`'s verify-step `channel`
  (v0.23.0's own predecessor, v0.22.0): a contradiction is only actionable
  once it says where to look, not just that something's wrong.

Full binding regenerated (Java/TS/Python), tests green, real D031 acceptance
run against the tagged git URL — see `CHANGELOG.md` v0.23.0 and
`demands/fulfilled/app-studio-20260805-contracts-mission-consistency-report.md`.

## What we do once closed

Nothing further from `contracts` — this is the whole loop for this demand.
When app-studio's re-pin lands, archive this file per the demand system's
loop-close step.
