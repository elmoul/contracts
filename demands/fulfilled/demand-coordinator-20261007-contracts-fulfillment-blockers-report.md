---
demandId: demand-coordinator-20261007-contracts-fulfillment-blockers
worker: contracts
date: 2026-10-07
status: done
shipped: ["tag v0.51.0 (local, not pushed)", "commit fd01f1d on main (schema, bindings, tests, version bumps)", "commit 37c52d2 on main (CHANGELOG)", "schemas/demand-coordinator/demand.fulfillment.json optional blockers", "Java, TypeScript and Python versions at 0.51.0; Python and TypeScript demand.fulfillment bindings regenerated", "tests/validate_demand.py extended", "worktree ../contracts-worktrees/v0.51.0"]
---

# Fulfillment report: contracts, optional `blockers` on `demand.fulfillment`

`done` is a claim, not a verdict; the owner approves in the coordinator.

State check first: `blockers` was not in the schema before this session, so the work was done, not no-opped.

## Acceptance criteria

- `blockers` is an optional array on `demand.fulfillment.json`; items are `{kind, text, demandId}` with `additionalProperties: false`. Met.
- `kind` is the closed enum `demand`, `runtime-step`, `owner-decision`, `other`; `text` has `minLength: 1`; `demandId` uses the schema's own demandId pattern and is required when `kind` is `demand`. Met. I also made `demandId` rejected on any other kind, following the demand body ("required for, and only allowed on, demand"); the criteria list only says optional. Say if you want it merely optional on other kinds.
- `blockers` is valid only when `status` is `blocked`. Met via a top-level `if/else` (a `done` report with `blockers` is rejected).
- Fixtures: a blocked report with blockers (all four kinds) validates, the existing blocked report without blockers still validates, plus seven known-bad cases (done with blockers, demand blocker with no id, id on non-demand, unknown kind, empty text, malformed id, extra property). The `status` description no longer says the reason belongs only in the body. Met.
- Released as a new version: v0.51.0, additive, tag is local only (no push, per the run rules). Met. demand-coordinator re-pins on its own demand.

## Verification

- `python tests/run_all.py`: all validators passed. `mvn -f gen/java/pom.xml test`: exit 0. `npm run build` and `tsc --noEmit` in `gen/ts`: clean.
- Local D031-style check: a fresh venv installed `git+file:///...contracts@v0.51.0#subdirectory=gen/python`, parsed a blocked report with `blockers` and rejected an unknown kind. The GitHub-URL, npm and Maven clean installs are not done; they need the tag pushed by the owner.

## Caveats for consumers

- No generator here emits `if/then/else`, so the Java, Python and TypeScript bindings accept a `done` report with `blockers` and a `demand` blocker without `demandId`. Only the JSON Schema validation (and the fixtures in `tests/validate_demand.py`) enforces those rules.
- The TypeScript `DemandFulfillment` changed from `interface` to `type` alias (same shape).
