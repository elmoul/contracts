---
demandId: youtrack-20261020-contracts-delivery-defect-task
worker: contracts
date: 2026-10-20
status: done
shipped: ["tag v0.59.0 on commit 24b4424 (local only, not pushed)", "schemas/delivery-api/youtrack-delivery.openapi.yaml: POST /delivery/v1/defect-tasks (createDeliveryDefectTask, 201 new / 200 replay / error envelope)", "schemas/delivery/delivery.defect-task-request.json and delivery.defect-task.json (new, additionalProperties false)", "schemas/delivery/delivery.error.json: closed invalid_request details.reason set (epic_children_unfinished with unfinished[{idReadable,state}], task_unreadable, epic_mismatch, not_an_epic)", "docs/task-delivery.md: section Epics and the defect-task operation (epic accepts comment and transition payloads; move to Done refused while a child is not in Staging or Done)", "Python and TypeScript bindings (incl. dist), versions 0.59.0 on Java, TS and Python", "CHANGELOG v0.59.0", "31 new cases plus a route check in tests/validate_delivery.py", "worktree ../contracts-worktrees/v0.59.0"]
---

# Fulfilment - defect-task operation on the delivery API

Checked first: not shipped (latest tag was v0.58.0, no `defect-tasks` route or schema anywhere). Additive minor **v0.59.0**.

## Acceptance criteria

1. **Route and schemas** - met. `POST /delivery/v1/defect-tasks` with request `delivery.defect-task-request` (`operationKey`, `epic` as issue-ref, `summary` 1-120, `outcome` 1-700, `scope` 1-10, `acceptance` 1-8, `source` const `epic-test`, `note` 1-2000) and response `{data: delivery.defect-task}` (`operationKey`, `status` confirmed|uncertain|failed, `epic`, `issue {id,key,project,url}|null`, `error|null`, `createdAt`, `updatedAt`). Both closed. `201` new key, `200` replay. Bindings and changelog are in the release.
2. **Closed reasons** - met. `delivery.error` constrains `details.reason` on `invalid_request` to the four values; `epic_children_unfinished` requires a non-empty `details.unfinished` of `{idReadable, state}`.
3. **Docs** - met. `docs/task-delivery.md` states that an epic accepts the comment and transition payloads and that a move to Done is refused while a child is not in Staging or Done.

## Choices the demand left open (please confirm in youtrack's re-pin)

- The reason is carried as `details.reason` (and the list as `details.unfinished`), matching how `delivery.error` already carries `reason` for the lookup-miss codes. The demand named the values but not the key.
- `reason` stays optional on `invalid_request`, so existing errors still validate.
- `delivery.defect-task` couples the fields: `confirmed` has `issue` and null `error`; `failed`/`uncertain` have `error` and null `issue` (schema `if/then`; generated bindings do not enforce it).
- `outcome` "at most three sentences" is a producer rule in the description; JSON Schema cannot count sentences.
- `task_unreadable` is documented as: a child could not be read, so the Done rule could not be evaluated and the move is refused. The demand listed the code without a meaning.
- Rollout: shapes are closed, so consumers pin v0.59.0 before the planner serves the route or sends a `reason`.

## Verification

`python tests/run_all.py` passed (new cases include each reason, an unknown reason, missing/empty `unfinished`, status coupling, request bounds); `npx tsc --noEmit` and `npm run build` clean; `mvn -f gen/java/pom.xml test` passed. Clean `pip install` from the local tag `v0.59.0` in a fresh venv imported the new modules. Not run: the D031 acceptance from the real GitHub tag URL (and a fresh-cache npm install), because the tag is local until the owner pushes it. Repeat after the push.

No origin or consumer demand raised from this release: additive release, and recent releases left delivery of the summary to the coordinator.
