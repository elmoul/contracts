---
demandId: agent-runner-20261027-repo-summary-v06-leftovers
worker: contracts
date: 2026-10-27
status: done
shipped: ["tag v0.64.0 (local only, not pushed)", "schemas/agent-runner/brain.repo-summary.json: optional v06Leftovers array of non-empty strings (not in required; additionalProperties false)", "TypeScript (source and dist) and Python bindings, versions 0.64.0 on Java, TS and Python", "CHANGELOG v0.64.0", "6 new cases in tests/validate_brain.py", "worktree ../contracts-worktrees/v0.64.0"]
---

# Fulfilment - brain.repo-summary v06Leftovers

Checked first: not shipped (latest tag v0.63.0, no `v06Leftovers` anywhere). Additive minor **v0.64.0**.

## Acceptance criteria

1. **Optional field** - met. `v06Leftovers` is an optional `string[]` (items `minLength` 1), absent from `required`; `additionalProperties` still false. Summaries without it still validate (the existing known-good cases pass unchanged). Absent = producer does not report; `[]` = none.
2. **Tagged release publishes schema and TypeScript type** - met locally: tag v0.64.0 carries the schema and `v06Leftovers?: string[]` in `gen/ts/brain-repo-summary.ts` and `dist`. Python binding updated too.

## Verification

`python tests/run_all.py` passed (list, empty list, string, non-string element, empty name and null rejected); `npx tsc --noEmit` clean; `mvn -f gen/java/pom.xml test` 44 tests, 0 failures. Not run: D031 clean-install acceptance from the real GitHub tag URL, since the tag is local until pushed. Repeat after the push.

## Rollout

The schema is closed: agent-runner must re-pin v0.64.0 before sending `v06Leftovers`. No origin or consumer demand raised: additive release, the origin re-pins from this report.
