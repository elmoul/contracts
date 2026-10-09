---
demandId: factory-20261009-contracts-from-brief-setup
worker: contracts
date: 2026-10-09
status: blocked
shipped: ["tag v0.54.0 (local, not pushed) on commit 6b18c02", "commit 93fcd90 on main", "schemas/youtrack/planner.brief-project-request.json (localOnly)", "schemas/youtrack/planner.brief-project-response.json (setup)", "schemas/factory/factory.handover-setup.json", "TypeScript and Python bindings regenerated, versions 0.54.0", "tests/validate_planner_brief.py extended", "CHANGELOG v0.54.0", "worktree ../contracts-worktrees/v0.54.0"]
---

# Fulfilment - localOnly and the setup step (task 0) in the hand-over shapes

Checked first: nothing for `localOnly` or `setup` existed, so the work was done, not no-opped.

## What shipped

Additive minor `v0.54.0`, local only (nothing pushed; the owner pushes the tag). Consumers must wait for tag **v0.54.0**. The tag points at `6b18c02` (the CHANGELOG commit on top of `93fcd90`); it was moved once locally because the first commit was tagged before the CHANGELOG edit landed.

- `planner.brief-project-request`: optional `localOnly` boolean, default false, meaning stated in the description.
- `setup` object: fixed `name` const `Set up repositories`, `state` (pending, running, done, failed), echoed `localOnly`, ordered `steps` (max 5) with closed ids (app-repo, hexagon-repo, onboard, register-project, verify-discovery), step `state` (pending, running, done, failed, skipped), closed failure `reason` plus free-text `detail`, `at` timestamp. `reason` is required when a step failed; `skipped` is the repo steps' state when localOnly is true. Embedded as optional `setup` in `planner.brief-project-response`, and as the new standalone `factory.handover-setup.json` for Factory's hand-over status (a test keeps both definitions identical).
- Bindings: Python and TypeScript regenerated (enums restored to StrEnum by hand per DEPLOYMENT.md), TS `dist/` rebuilt, versions at 0.54.0 in pom.xml, package.json, pyproject.toml. Java regenerates from the schemas at build.
- Tests: fixtures for localOnly true/false/absent/invalid, every step and setup state, refusal of unknown step id/state and other negatives. `python tests/run_all.py` passes, `mvn -f gen/java/pom.xml test` passes, `npx tsc --noEmit` passes.

## What did not ship / why blocked

- The D031 clean-install acceptance from the real tagged URL cannot be run: the tag is not pushed (owner's rule), so there is no URL to install from. Only local builds and tests were verified.
- The demand names `docs/HARVEST_ZERO_TOUCH_DESIGN.md` and `HARVEST_CLOSING_CHAIN_DESIGN.md`; neither exists in the factory working tree, so the shapes follow the demand text alone. Factory has no existing hand-over status schema in this repo, so `factory.handover-setup.json` is a new file. The failure `reason` codes are my reading (the demand left the list open); Factory/planner should confirm them.
- `if/then` (reason required on failure) is not generated into the TS/Python bindings; schema-level tests cover it.
