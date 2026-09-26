---
demandId: youtrack-20260926-contracts-backlog-planner-schema-set
worker: contracts
date: 2026-09-26
status: done
shipped: ["v0.28.0", "commit 585369b on main", "8 JSON Schema 2020-12 files under schemas/youtrack/", "TypeScript bindings in gen/ts", "Python bindings in gen/python/platform_contracts/youtrack/"]
summaryRef: "commit 585369b on main (feat(youtrack): publish backlog-planner schema set (v0.28.0))"
---

# Fulfillment — publish the backlog-planner schema set

## What shipped

Tag `v0.28.0` (commit `585369b`, pushed to `origin/main`) adds
`schemas/youtrack/` with all 8 requested JSON Schema 2020-12 files, built
field-for-field from `youtrack/planner/src/backlog_planner/api.py` (route
bodies) and `domain/errors.py` (error codes), per the demand's own table:

- `planner.project.json`
- `planner.model.json`
- `planner.plan-request.json` (`oneOf` enforces exactly one of
  `project`/`newProject`)
- `planner.plan-issue.json`
- `planner.plan-summary.json`
- `planner.plan-run.json` (flat object, not an `allOf`-extension of
  `plan-summary` — `additionalProperties: false` does not compose across
  `allOf` branches; `issues` is a cross-file `$ref` to `planner.plan-issue.json`)
- `planner.confirm-request.json` (whole body optional; fields/links
  deliberately not accepted, D111 clause 2)
- `planner.error.json` (`code` is an open string, not a closed enum, with the
  documented code/status table in its description)

**Envelopes**: these 8 schemas are the `data`/`error` payload shapes; the
`{"data": ...}` / `{"error": ...}` wrapping itself is documented in each
schema's description and in the CHANGELOG entry, matching how the demand's
own route table is written (no separate envelope-wrapper schema files were
requested or added).

**TypeScript**: one `.ts` file per schema (`gen/ts/planner-*.ts`) via
`json-schema-to-typescript`, re-exported from `gen/ts/index.ts`, `dist/`
rebuilt and committed. Verified with a real `file:` install into a scratch
npm project (D031 acceptance) — `PlannerPlanRun` and friends resolve and
type-check (`npx tsc --noEmit` clean).

**Python**: generated via `datamodel-codegen` in directory-batch mode into
`gen/python/platform_contracts/youtrack/`, wired into
`platform_contracts/__init__.py`. Verified with a real
`pip install ./gen/python` into a fresh venv, including a
`model_dump_json()` / `model_validate_json()` round-trip on `PlannerPlanRun`
(D031 acceptance).

Release notes: `CHANGELOG.md`'s `## v0.28.0 — 2026-09-26` entry names the tag
and lists every new file, so `youtrack` and `dashboard` can pin
`v0.28.0` directly.

## What the origin must know

- Pin `v0.28.0` — TypeScript via `file:` checkout, Python via
  `pip install "git+https://github.com/elmoul/contracts.git@v0.28.0#subdirectory=gen/python"`
  (see `contracts/DEPLOYMENT.md`).
- This is an **additive** release (new schemas only, nothing existing
  touched) — per D043/D031, no fleet-wide "everyone re-pin" demand was
  raised, only this one back to `youtrack` as the origin.
- No Java binding was generated — the demand didn't ask for one.
- `planner.error.json`'s `code` enum is deliberately open (documented via
  `examples`, not a closed JSON Schema `enum`) so a future error code the
  planner adds is additive for consumers, not breaking.

## Not done / caveats

- No conformance test was added in `contracts` validating the planner's live
  payloads against these schemas — the demand's own "What we do once closed"
  section assigns that follow-up to `youtrack` (add it in the planner repo
  once it re-pins), not to `contracts`.
- The pre-existing `python tests/run_all.py` failure in `validate_demand.py`
  (a stale hardcoded path to an already-archived demand file,
  `2026-09-14-factory-repin-interface-extraction.md`) predates this session
  and is unrelated to this change — left untouched per the "don't fix
  unrelated things from here" rule; every schema-specific validator in that
  suite passes.
