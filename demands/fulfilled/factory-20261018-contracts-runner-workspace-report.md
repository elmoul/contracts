---
demandId: factory-20261018-contracts-runner-workspace
worker: contracts
date: 2026-10-18
status: done
shipped: ["tag v0.58.0 (local only, not pushed)", "schemas/agent-runner/runner.dispatch-request.json: optional workspace (also reaches parked.resume-request dispatch)", "schemas/agent-runner/runner.run-record.json: optional taskWorkspace", "schemas/agent-runner/runner.dispatch-reservation.json: workspace in the requestHash field list, only when present, plus a second worked example", "Python and TypeScript bindings (incl. dist .d.ts), versions 0.58.0", "CHANGELOG v0.58.0", "new cases in tests/validate_runner.py and tests/validate_parked.py", "worktree ../contracts-worktrees/v0.58.0"]
---

# Fulfilment - task workspaces in the runner shapes

Checked first: not shipped (latest tag v0.57.0; no `workspace` or `taskWorkspace` anywhere in schemas or bindings). Read the three schemas, agent-runner's `src/domain/taskWorkspace.ts`, `src/domain/dispatchKey.ts` and its CHANGELOG (read-only), and the v0.57.0 release for the additive pattern. Factory's adapters were not read: the runner source was enough to fix the shapes.

## Which tag consumers must wait for

**v0.58.0.** Created locally; the owner pushes it. The dispatch request and run record are closed, so Factory and agent-runner must pin v0.58.0 before sending or answering either member. Nothing is re-pinned by this release (D031).

## Acceptance criteria

1. **`workspace`** on the dispatch request and (via `$ref`) the parked resume dispatch - met: `kind` const `task-worktree`, `taskId` or `key` (exactly one, `oneOf`), `branch` matching `^feature/...`, `base` branch name or 40-hex, `reuse` boolean, closed. Patterns copied from the runner's own regexes.
2. **`taskWorkspace`** on the run record - met: required `id`, `kind`, `branch`, `base`; optional `path`, `state`, plus `repo`, `task`, `appPath`, `baseRevision`.
3. **`requestHash`** - met: `workspace` named as the seventh field, included only when present, canonical form `{base,branch,kind,reuse,task}` taken from the runner's `canonicalRequestJson`. The existing worked example hash is asserted unchanged; a workspace example hash (`b7ed1475...db9f`) is asserted too.
4. **Additive** - met: nothing added to `required`; all existing fixtures still pass.
5. **Fixtures, bindings, CHANGELOG, docs, suite** - met: valid (by key, by taskId with 40-hex base, absent, resume dispatch with workspace, run record full/minimal/absent); invalid (bad kind, missing kind, bad branch, branch with space, no taskId and key, both, bad key, missing/bad base, bad/missing reuse, extra member; taskWorkspace bad kind, missing id/branch, bad state, bad baseRevision, extra member). Bindings edited by hand in the generator's form; schema descriptions are the documentation.

## Two deliberate deviations to know about

- **`taskWorkspace` has more optional members than the demand lists** (`repo`, `task`, `appPath`, `baseRevision`). agent-runner's `RunWorkspaceRef` answers them today; in a closed shape omitting them would still make a real answer refuse, which is the problem this demand exists to fix.
- **`path` is documented as a label but not pattern-restricted.** agent-runner answers its absolute temp path today; forbidding absolute paths in the schema would refuse that real answer. The description tells consumers never to treat it as an address and producers to send a relative label. If the owner wants it enforced, agent-runner must first stop sending the absolute path, then a later patch can add a pattern. Also `state` is optional because the runner does not put it on run answers yet.

## Verification

`python tests/run_all.py` passed; `npx tsc --noEmit` and `npm run build` clean (dist regenerated); Python pydantic round-trips on request, run record and resume request (valid accepted, bad branch refused); `mvn -B -f gen/java/pom.xml test` passed. Not run: the generator itself (`datamodel-codegen` batch mode errors on this directory here, bindings were edited to match its form), and the D031 clean install from the real GitHub tag URL, since the tag is local until pushed. Repeat after the push. The `oneOf` exactly-one rule is not generated into TS/Python (noted in CHANGELOG).

Nothing pushed. The release-checklist demand to the origin (factory: "re-pin and adopt") is not raised here; pushing the tag and that demand commit is the owner's step.
