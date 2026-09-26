---
demandId: youtrack-20260926-contracts-planner-plan-run-note
worker: contracts
date: 2026-09-26
status: done
shipped: ["v0.29.0", "commit 46f5fba on main", "optional note (string|null) on schemas/youtrack/planner.plan-run.json", "TypeScript + Python bindings regenerated"]
summaryRef: "commit 46f5fba on main (feat(youtrack): optional note on planner.plan-run (v0.29.0))"
---

# Fulfillment — `note` on `planner.plan-run`

## What shipped

Tag `v0.29.0` (commit `46f5fba`, pushed to `origin/main`):

- `planner.plan-run.json` gains `note`: `type: ["string", "null"]`, not in
  `required` — additive; v0.28.0-pinned consumers keep validating. Its
  description gives the "already covered by PLA-…" use and states it is
  absent or `null` when there is nothing to say (demand's example text kept as
  a schema `examples` entry).
- `issues` still has no `minItems`; its description now says an empty array
  is a valid preview (nothing to confirm, `note` explains why).
- Bindings regenerated in the same release: `gen/ts/planner-plan-run.ts`
  (`note?: string | null`, `dist/` rebuilt) and
  `gen/python/platform_contracts/youtrack/planner_plan_run.py`
  (`note: str | None = None`). Versions bumped to 0.29.0 (TS, Python; no Java
  binding for youtrack). CHANGELOG `## v0.29.0` names the tag.

## Evidence

- Schema (jsonschema 2020-12, with the youtrack `$ref` registry): empty
  `issues` valid; `note` absent / `null` / string valid; `note: 3` rejected.
- D031: `pip install "git+<origin>@v0.29.0#subdirectory=gen/python"` in a
  fresh venv imports `PlannerPlanRun` with a `note` field; model round-trip
  with and without `note`. npm `file:` install of `gen/ts` + `tsc --strict`
  against `PlannerPlanRun["note"]` accepting `null` and `undefined`.
- Other `tests/` validators pass. `tests/validate_demand.py` fails on main
  before and after this change (it reads a demand file since moved to
  `demands/archive/`) — pre-existing, unrelated, noted in PROGRESS.

## Consuming leg

Per D043 an origin demand `contracts-20260926-youtrack-repin-planner-plan-run-note`
is raised to `youtrack` (re-pin v0.29.0, emit `note`). Additive release — no
fleet-wide consumer demands.
