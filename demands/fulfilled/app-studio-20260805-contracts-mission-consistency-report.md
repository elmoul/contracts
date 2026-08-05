---
demandId: app-studio-20260805-contracts-mission-consistency
worker: contracts
date: 2026-08-05
status: done
shipped: ["v0.23.0", "commit 59a525a on main", "36 app-studio schema checks (4 new)", "26 Java tests", "python tests/run_all.py green"]
summaryRef: "commit 59a525a on main, tag v0.23.0 (what it did)"
---

# Fulfillment — `app.mission` gains an optional `consistency` object

`status: done` here is a claim, not a verdict — per `DEMAND_SYSTEM.md` §4,
this report is `contracts`' only output for this demand. `contracts` does not
self-certify and has not notified `app-studio` directly; the coordinator
assembles and delivers the summary once the owner approves.

## What shipped

`schemas/app-studio/app.mission.json` gains an optional, DERIVED
`consistency` object — the ledger-vs-artifact divergence report — same
pattern as the existing `gateContext`/`pipeline` derived fields:

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

- `consistency` itself is `["object","null"]` — null when reconciliation
  hasn't run: a producer emitting a stored ledger row rather than a
  projection, or a mission with no artifact yet to diverge from (before
  `scaffold`/`planning`).
- `consistent` (bool), `checkedAt` (date-time), `divergences` (array) are all
  required inside the object once it's present — a verdict without the list
  that backs it up doesn't validate.
- Each `divergences[]` entry requires `subject`, `ledgerValue`,
  `artifactValue`, `description`. `ledgerValue`/`artifactValue` are
  deliberately unconstrained (no `type`) — the ledger's own field types vary
  by subject (`currentWave` is an int, `stage` is a string, `targetRepo
  existence` might be a bool), same precedent as `pipeline`'s
  `additionalProperties: true`. `description` exists for the same reason
  `app.task-plan`'s verify-step `channel` (v0.22.0) exists: a contradiction
  is only actionable once it says where to look, not just that something's
  wrong.
- Additive only — `consistency` is not in the top-level `required` array, so
  every existing mission record (including the tutor pilot fixture,
  `tests/fixtures/app-studio/tutor-pilot-mission.json`) validates unchanged
  with no `consistency` key at all.

Released as **v0.23.0**, tag pushed, commit `59a525a` on `main`.

### Verification run

- `mvn -B -f gen/java/pom.xml test` — 26/26 passing (jsonschema2pojo
  regenerates `Consistency`/`Divergence` as part of the build).
- `npx tsc --noEmit` clean in `gen/ts` after regenerating `app-mission.ts`
  and rebuilding `dist/`.
- Python: `datamodel-codegen` regenerated
  `platform_contracts/app_studio/app_mission.py` (`Consistency`, `Divergence`
  classes, `ledgerValue`/`artifactValue` typed `Any`); round-tripped
  (`model_dump_json()` → `model_validate_json()`).
- `python tests/run_all.py` — full suite green, including 4 new cases in
  `tests/validate_app_studio.py`: reconciled/no-divergence,
  reconciled/one-divergence, `consistency` missing `divergences` (rejected),
  a divergence entry missing `description` (rejected).
- **Real D031 acceptance test**, not just a local build: fresh venv,
  `pip install "git+https://github.com/elmoul/contracts.git@v0.23.0#subdirectory=gen/python"`
  against the actual pushed tag — succeeded, imported `AppMission`/
  `Consistency`/`Divergence`, round-tripped a populated `Consistency` object.
  Also verified the TS `file:` path end to end: a scratch project depending
  on `file:.../gen/ts`, `npm install`, then `tsc --noEmit` against a
  `.consistency` access — clean.

## What the origin must know

- The re-pin/adopt release-notification demand is filed separately per D043:
  `demands/2026-08-05-app-studio-repin-mission-consistency.md` (id
  `contracts-20260805-app-studio-repin-mission-consistency`) — that is the
  loop-close app-studio should act on, not this report.
- Additive release; no other `app.mission` consumer is obligated to move.

## Not done / caveats

- `contracts` does not compute reconciliation itself — this ships the shape
  only. Populating `consistency` (deciding what counts as a divergence,
  running the comparison against the task_plan/target-repo artifacts) is
  app-studio's own `projection.project()` logic, same division of
  responsibility as every other DERIVED field on `app.mission`.
- No fixture in `tests/fixtures/app-studio/` carries a populated
  `consistency` yet (the existing fixtures are the tutor pilot's real
  records, which predate this field) — the new schema-level test cases in
  `tests/validate_app_studio.py` are hand-written, not extracted from a real
  build. If/when app-studio's own divergence detection produces a real
  example, per D066 that would be a good candidate to add as a fixture, same
  precedent as the pilot mission/plan fixtures.
