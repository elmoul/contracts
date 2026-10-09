---
demandId: youtrack-20261009-contracts-setup-gate-schemas
worker: contracts
date: 2026-10-09
status: done
shipped: ["tag v0.55.0 on commit 0d65f11 (local only, not pushed)", "commit fabd452 on main (schemas, bindings, tests)", "commit 0d65f11 on main (CHANGELOG v0.55.0)", "schemas/youtrack/planner.setup-progress-request.json", "schemas/youtrack/planner.setup-progress-response.json", "schemas/youtrack/planner.setup-gate.json", "schemas/youtrack/planner.setup-error.json", "optional closed startable on schemas/delivery/delivery.workflow.json and delivery.issue.json", "TypeScript and Python bindings regenerated, versions 0.55.0", "tests/validate_setup_gate.py (in run_all.py) and two startable cases in validate_delivery.py", "worktree ../contracts-worktrees/v0.55.0"]
---

# Fulfilment - setup gate schemas and `startable`

Checked first: nothing of this was shipped before (no setup-route schemas, no `startable`). Additive minor **v0.55.0**; consumers pin tag `v0.55.0` once the owner pushes it. Nothing was pushed; the tag is local and the pinned worktree `../contracts-worktrees/v0.55.0` exists.

## Acceptance criteria

1. **New closed schemas** - met, written from planner `domain/setup.py` and `api.py` at 111a727, all `additionalProperties: false`:
   - `planner.setup-progress-request`: `{step, state, reason?, detail?}` (reason required when failed, refused otherwise).
   - `planner.setup-progress-response`: the `setup` object (the `data` payload), kept equal to `factory.handover-setup` by a test.
   - `planner.setup-gate`: `{projectKey, open, reason (null | setup-not-done), setupIssue, setup, startable? {value, reason (null | setup-not-done | setup-task)}}`.
   - `planner.setup-error`: closed codes `setup_project_unknown` (404), `setup_step_unknown`, `setup_progress_invalid` (422).
2. **`startable` on the delivery surface** - met: optional closed `startable {value, reason}` on `delivery.workflow` and, as the demand allowed, `delivery.issue`, reasons `setup-not-done` and `setup-task` (reason null when value is true). Minor version cut by the repo procedure (versions, CHANGELOG, local tag, worktree); nothing pushed.

## Verification

- `python tests/run_all.py` passed; `mvn -f gen/java/pom.xml test` exit 0; `npx tsc --noEmit` clean.
- Clean install from a fresh clone of the local tag `v0.55.0` (scratch dir, deleted): fresh venv `pip install` gives `platform-contracts 0.55.0` and the new modules import; npm `file:` install contains the new `dist` files; `mvn install` into an empty `.m2` produced `io.platform:contracts:0.55.0`. **Not run:** the D031 install from the real GitHub tag URL, because the tag does not exist on the remote until the owner pushes it. Repeat it after the push.

## Notes for the planner and Factory

- **Error code mismatch in the planner.** At 111a727 `backlog_planner/domain/errors.py` declares `unknown_project`, `unknown_step` and `invalid_progress`, while the planner's CHANGELOG, its DEPLOYMENT and this demand name `setup_project_unknown`, `setup_step_unknown` and `setup_progress_invalid`. The schema follows the demand; the planner must emit the `setup_*` codes (I did not touch the planner).
- Response and gate schemas describe the `data` payload, not the `{"data": ...}` wrapper; the error schema describes the `error` payload.
- `startable` rollout: the closed shapes make an older pin reject a document carrying it, so Factory and the planner pin v0.55.0 before the planner starts sending it (the planner follow-up demand).
- `if/then/else` on the request is not generated into the TS/Python bindings; the schema-level test covers it. Python enums were restored to `StrEnum` by hand. The Java pom does not map the `youtrack` directory, so there are no Java classes for the planner shapes (as for the existing planner schemas).
