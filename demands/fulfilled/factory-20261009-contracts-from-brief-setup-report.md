---
demandId: factory-20261009-contracts-from-brief-setup
worker: contracts
date: 2026-10-09
status: done
shipped: ["tag v0.54.0 on commit 6b18c02 (pushed by the owner; confirmed with git ls-remote)", "commit 93fcd90 on main", "schemas/youtrack/planner.brief-project-request.json (localOnly)", "schemas/youtrack/planner.brief-project-response.json (setup)", "schemas/factory/factory.handover-setup.json", "TypeScript and Python bindings regenerated, versions 0.54.0", "tests/validate_planner_brief.py extended", "CHANGELOG v0.54.0", "worktree ../contracts-worktrees/v0.54.0", "D031 clean-install acceptance passed from the real tag"]
---

# Fulfilment - localOnly and the setup step (task 0) in the hand-over shapes

Checked first: the capability was already built by the prior session (commit `93fcd90`, tag `v0.54.0` at `6b18c02`). This run only closed the one open blocker, the clean-install acceptance. No schema changed.

## What shipped

Additive minor `v0.54.0`. Consumers pin tag **v0.54.0**.

- `planner.brief-project-request`: optional `localOnly` boolean, default false.
- `setup` object: fixed `name` const `Set up repositories`, `state` (pending, running, done, failed), echoed `localOnly`, ordered `steps` (max 5) with closed ids (app-repo, hexagon-repo, onboard, register-project, verify-discovery), step `state` (pending, running, done, failed, skipped), closed failure `reason` plus free-text `detail`, `at` timestamp. `reason` is required when a step failed; the repo steps are `skipped` when localOnly is true. Embedded as optional `setup` in `planner.brief-project-response` and as the standalone `factory.handover-setup.json` (a test keeps both identical).
- Bindings: Python and TypeScript regenerated, TS `dist/` rebuilt, versions 0.54.0.
- Tests: `python tests/run_all.py`, `mvn -f gen/java/pom.xml test`, `npx tsc --noEmit` all passed in the earlier run.

## D031 clean-install acceptance (run this session, read-only against the remote, nothing pushed)

`git ls-remote --tags origin v0.54.0` returns `6b18c02901693c5064055eec04e42da52e7e1410`. In a scratch directory (since deleted):

- Python: fresh venv, `pip install "git+https://github.com/elmoul/contracts.git@v0.54.0#subdirectory=gen/python"` installed `platform-contracts 0.54.0`; `factory_handover_setup`, `planner_brief_project_request` and `planner_brief_project_response` import.
- TypeScript: fresh `git clone --branch v0.54.0`, scratch project with `"@platform/contracts": "file:../c/gen/ts"`, `npm install` succeeded; `factory-handover-setup.d.ts` is present in the installed package.
- Java: from the same fresh clone, `mvn install` into an empty `.m2` produced `io.platform:contracts:0.54.0` (jar and pom).

## Notes for Factory and the planner

- The demand names `docs/HARVEST_ZERO_TOUCH_DESIGN.md` and `HARVEST_CLOSING_CHAIN_DESIGN.md`; neither was in the factory tree, so the shapes follow the demand text. The failure `reason` codes are my reading (the demand left the list open); please confirm them.
- `if/then` (reason required on failure) is not generated into the TS/Python bindings; schema-level tests cover it.
- `gen/java/pom.xml` does not map the `youtrack` or `factory` schema directories, so the Java artifact has no classes for these shapes (same as the existing youtrack schemas). I did not confirm this against the jar contents; add a Java mapping if a Java consumer needs these types.
