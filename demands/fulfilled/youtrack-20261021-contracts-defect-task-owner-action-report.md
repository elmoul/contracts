---
demandId: youtrack-20261021-contracts-defect-task-owner-action
worker: contracts
date: 2026-10-21
status: done
shipped: ["tag v0.60.0 on commit 867734f (local only, not pushed)", "schemas/delivery/delivery.defect-task-request.json: optional boolean ownerAction (not in required; additionalProperties false)", "Python and TypeScript bindings (incl. dist), versions 0.60.0 on Java, TS and Python", "docs/task-delivery.md: ownerAction note (tag must already exist in the tracker; read-back lacking it is uncertain, never confirmed)", "CHANGELOG v0.60.0", "4 new cases in tests/validate_delivery.py", "worktree ../contracts-worktrees/v0.60.0"]
---

# Fulfilment - ownerAction on the defect-task request

Checked first: not shipped (latest tag v0.59.0, no `ownerAction` on `delivery.defect-task-request`). Additive minor **v0.60.0**.

## Acceptance criteria

1. **Property** - met. `ownerAction` is an optional boolean, not in `required`, `additionalProperties` still false. Documented: `true` asks the service to tag the created Task `owner-action`; absent and `false` are the same request. Python and TypeScript bindings and the changelog are in the release.
2. **Docs** - met. `docs/task-delivery.md` states the tag must already exist in the tracker and that a task whose read-back lacks it is reported `uncertain`, never `confirmed`. It also records that only `true` enters the request hash.

## Verification

`python tests/run_all.py` passed (true, false, string and null cases); `npx tsc --noEmit` clean; `mvn -f gen/java/pom.xml test` passed. A pip install from the local tag `v0.60.0` in a fresh venv exposes `ownerAction`. Not run: the D031 acceptance from the real GitHub tag URL, because the tag is local until the owner pushes it. Repeat after the push.

Bindings were edited by hand for this one member rather than regenerated, to keep the diff to the single field.

No origin or consumer demand raised: additive release.
