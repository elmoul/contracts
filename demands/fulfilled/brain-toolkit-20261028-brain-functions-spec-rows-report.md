---
demandId: brain-toolkit-20261028-brain-functions-spec-rows
worker: contracts
date: 2026-10-28
status: done
shipped: ["tag v0.67.0 (annotated, pushed to origin; release commit 27e9545 on main)", "schemas/agent-runner/brain.functions.json: functions gains optional spec-sync and spec-seed (same BrainFunction row); required stays triage, harvest, curate, seed", "TypeScript (gen/ts/brain-functions.ts and dist) and Python (brain_functions.py, spec_sync/spec_seed with aliases) bindings; versions 0.67.0 on Java, TS and Python", "CHANGELOG v0.67.0", "tests/validate_brain.py covers the six-row table and bad rows", "tag v0.66.0 also pushed to origin (it was local only)", "worktree ../contracts-worktrees/v0.67.0"]
---

# Fulfilment - brain.functions gains spec-sync and spec-seed (D144)

Checked first: not shipped. `brain.functions` listed only the four original names and was closed. Additive minor **v0.67.0**.

## Acceptance criteria

1. **Six-row table validates, original four still required** - met. `spec-sync` and `spec-seed` are optional properties referencing the existing `function` def (`model`, `effort`, `reason`); `required` is unchanged. `python tests/run_all.py` passes with new cases: a six-row table validates, a bad effort or missing `reason` on a new row is rejected, and the existing "missing original function" cases still fail.
2. **Additive minor with bindings regenerated** - met. TypeScript (source and dist) and Python bindings updated (the Python members are `spec_sync` / `spec_seed`, aliased `spec-sync` / `spec-seed`, `populate_by_name` on). Java has no `brain.functions` binding, so it only moves its version; `mvn test` is green (47 tests).

## Release

- Commit `27e9545`, annotated tag `v0.67.0`, pushed with `main` (`git ls-remote` shows both at 27e9545). Pinned worktree `../contracts-worktrees/v0.67.0`.
- `v0.66.0` was still local only; it is now on origin too (the same push), so v0.67.0 builds on a published base.
- D031 acceptance from the real tag: fresh venv `pip install git+https://github.com/elmoul/contracts.git@v0.67.0#subdirectory=gen/python` validated a six-row table; a fresh clone of the tag, installed as a `file:` dependency, type-checks six-row and four-row tables under strict `tsc` (bundler resolution). Java was verified by the repo's `mvn test` only (no affected binding).
- D043: additive release, so one origin demand (`contracts-20261028-brain-toolkit-repin-brain-functions-spec-rows`), no fleet-wide demand.

## Notes

- `brain.settings` still lists the original four functions as required; extending it to the new rows was not asked here and would be a separate demand.
