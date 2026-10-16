---
demandId: factory-20261016-contracts-ci-outcome-checks
worker: contracts
date: 2026-10-16
status: done
shipped: ["tag v0.57.0 (local only, not pushed)", "schemas/agent-runner/parked.condition-event.json: ci-run outcome optional check (string 1-200) and pendingChecks (integer >= 0)", "Python and TypeScript bindings (incl. dist .d.ts, and the copy in parked-resume-request), versions 0.57.0", "CHANGELOG v0.57.0 with rollout note", "eleven new cases in tests/validate_parked.py", "worktree ../contracts-worktrees/v0.57.0"]
---

# Fulfilment - `check` and `pendingChecks` on the ci-run outcome

Checked first: not shipped (latest tag v0.56.0; the ci-run outcome carried only kind, repo, commit, pullRequest, runId, result, url, failedChecks). Read the schema, its tests and the CHANGELOG pattern for earlier additive fields, then added an additive minor.

## Which tag consumers must wait for

**v0.57.0.** It is created locally; the owner pushes it. Because the outcome is closed (`additionalProperties: false`), consumers must pin v0.57.0 BEFORE any producer (ci-runner) sends either field; an older pin rejects such an event. Nobody is re-pinned by this release (D031).

## Acceptance criteria

1. **`check`** - met: optional string, 1 to 200 characters, description gives the `sonar-gate` example; absent means the producer does not say.
2. **`pendingChecks`** - met: optional integer, minimum 0, counts other checks or workflow runs of the same commit known to be queued or running. The description states `0` means none outstanding and that absence means unknown: a consumer must treat absence as unknown, never as zero.
3. **Additive** - met: neither field is required; every existing payload and fixture still validates.
4. **Fixtures** - met: valid for check + pendingChecks 3, pendingChecks 0, check at 200 characters with pendingChecks absent, pendingChecks without check, and a resume request carrying both; invalid for negative, 1.5 and string pendingChecks, and empty, 201-character and non-string check.
5. **Bindings, CHANGELOG, documentation** - met: Python and TypeScript bindings (including dist `.d.ts` and the embedded copy in `parked-resume-request`) updated by hand in the form the generator produces; Java regenerates from schemas at build; versions 0.57.0 in pom, package.json, pyproject; CHANGELOG v0.57.0. The schema descriptions are the schema documentation.

## Verification

`python tests/run_all.py` passed; `npx tsc --noEmit` clean. Not run: Java `mvn test` (only the pom version changed), the generator itself (bindings edited to match the previous pattern), and the D031 clean install from the real GitHub tag URL, because the tag is local until the owner pushes it. Repeat after the push.

Nothing pushed. Release-checklist demand to the origin (factory: "re-pin and adopt") is not raised here: the report is the fulfilment, and pushing the tag and the demand commit is the owner's step.
