---
demandId: conventions-20261028-contracts-retire-dead-schemas
worker: contracts
date: 2026-10-28
status: done
shipped: ["removed schemas/state-feed/state.projection.guest.json and schemas/app/identity.json (local commit 937075a on main, not pushed)", "marked app-studio schemas app.mission.json and app.task-plan.json RETIRED in their descriptions and CHANGELOG, to be removed in the next minor", "released v0.68.0 as a local annotated tag with worktree ../contracts-worktrees/v0.68.0 (not pushed)"]
---

# Fulfilment - contracts retires the dead stub schemas

Prior state checked: neither stub had been removed and the highest tag was v0.67.0, so the work was new.

**Removed** (commit 937075a): `state.projection.guest` and `app.identity` schemas. Neither had an index or registry entry, binding or test. Doc references were updated in `HEXAGON.md`, `docs/task-delivery.md` and the `app/deployment-identity.json` description.

**Retired**: `schemas/app-studio/app.mission.json` and `app.task-plan.json` now start their descriptions with a RETIRED note, and the CHANGELOG says they go in the next minor. Shapes are unchanged. Bindings were not regenerated, so the generated TS/Python/Java descriptions do not yet carry the note. `tests/validate_app_studio.py` and `check_state_event_sync.py` still reference the family and still pass.

**Consumer grep** across the platform root (code, config and docs, excluding node_modules, build output, `.brain`, archives and contracts itself): no user of either stub or of the app-studio schema files or bindings. Hits were only dashboard component selectors that merely contain "app-mission" and archived design notes (`dashboard/design/archive/exposure-atlas-2026-07-10.md`), plus stale pinned copies of old contracts under `ci-runner/runner-work` (build workspaces, not consumers). No active user found.

**Release**: v0.68.0 (minor, as the demand specifies). Versions are 0.68.0 in `gen/java/pom.xml`, `gen/ts/package.json` and `gen/python/pyproject.toml`. The annotated tag `v0.68.0` is local, and the worktree `../contracts-worktrees/v0.68.0` exists.

**Tests** (all green): `python tests/run_all.py` (All validators passed), `mvn -f gen/java/pom.xml test` (47 run, 0 failures), `npx tsc --noEmit` in `gen/ts` (exit 0).

**Not done (run rules)**: nothing was pushed, so the D031 clean-install-from-tag acceptance could not be run (the tag is not on origin). The D043 origin notification demand was not raised: this demand is itself the origin's, and its push would be the raise. No consumer was found, so no consumer demands are owed. Push of `main` and `v0.68.0` is left for the owner.
