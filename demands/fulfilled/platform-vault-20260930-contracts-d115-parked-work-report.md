---
demandId: platform-vault-20260930-contracts-d115-parked-work
worker: contracts
date: 2026-09-30
status: done
shipped: ["v0.39.0", "commit 226de76 on main (feat(agent-runner): parked work shapes - wait condition, run result, condition event, resume request (v0.39.0))", "schemas/agent-runner/parked.wait-condition.json", "schemas/agent-runner/parked.run-result.json", "schemas/agent-runner/parked.condition-event.json", "schemas/agent-runner/parked.resume-request.json", "tests/validate_parked.py (wired into tests/run_all.py)", "Python bindings platform_contracts.agent_runner.parked_*; TypeScript parked-*.ts + dist", "pinned worktree ../contracts-worktrees/v0.39.0", "D043 origin demand demands/2026-09-30-platform-vault-repin-d115-parked-work.md"]
---

# Fulfillment: D115 parked-work shapes

## State check

**Not previously shipped.** At v0.38.0 no `parked.*` schema, binding or test existed
(grep of the repo found only two earlier dispatcher session stubs with no changes). This
session did the work.

## What shipped

Tag **`v0.39.0`** (commit `226de76`, pushed), pinned worktree
`../contracts-worktrees/v0.39.0`. Additive. The four schemas live in
`schemas/agent-runner/` so they can `$ref` `runner.dispatch-request.json` as a sibling.

| Criterion | Where |
|---|---|
| Parked run result: wait, exact reference, resume note, deadline | `parked.run-result`: `wait{waitId, condition, deadline}` (deadline required), `reference{repo, branch, pullRequest, commit, demandIds}`, `resumeNote`, `resumeOwner`, `checkpoint` |
| Wait condition: CI run, PR merged/closed, repository created, owner decision, demand state with ALL-of/ANY-of; `after` unchanged | `parked.wait-condition`: kinds `ci-run`, `pull-request`, `repository-created`, `owner-decision`, `demands` (`mode: all | any`); `demand.json` not touched, and a test asserts `after` is still an array of demand ids |
| Condition event: observed outcome + stable key so resume happens at most once | `parked.condition-event`: `eventKey` (per observed fact), per-kind `outcome`; the resume dispatch key is derived from `waitId` + `eventKey`, so a duplicate event replays under `runner.dispatch-reservation` |
| Resume request: keyed dispatch, resume note, outcome (CI failed -> fix) | `parked.resume-request`: keyed `dispatch` (`runner.dispatch-request`), `resumeNote`, full `event`, `action` `continue | fix | reassess` |

## Decisions I made where the demand was silent

- **Composition is one level deep.** ALL-of/ANY-of apply to demands only (the demand
  asked for that); mixed-kind waits are not modelled.
- **Demand states:** `approved | satisfied | archived`. `approved` is the fact `after`
  already counts.
- **Resume key:** `"resume:" + sha256(waitId + "\n" + eventKey)`, 71 characters, inside
  the dispatch-key pattern; worked example in the schema, checked by the test.
- **`action`:** `continue | fix | reassess` (CI non-success -> `fix`; PR closed unmerged,
  owner rejection, archived demand -> `reassess`). Producers publish facts only; the
  owner maps fact to action.
- **Expiry is not an event.** It is surfaced to the owner by the owner UI, per D115.
- **`resumeOwner`** is `factory | agent-runner` only; the coordinator cannot resume.

## Verification

- `python tests/run_all.py` passes (new `validate_parked.py`: all five kinds, ALL and
  ANY, known-bad cases, key derivation); `tsc --noEmit` passes.
- D031 from the real tag: fresh venv, `pip install "platform-contracts @
  git+https://github.com/elmoul/contracts.git@v0.39.0#subdirectory=gen/python"`, the
  four `parked_*` modules import; TypeScript built clean (`npm ci`, `tsc --noEmit`) from
  a copy of the `v0.39.0` worktree.

## Caveats

- The bindings do not enforce `dispatch.dispatchKey` being required (a sibling of
  `$ref`), nor `deadline > parkedAt`; the schema and tests cover the former.
- Java is unchanged. `schemas/` is still not in the Python wheel.
- D043 origin demand raised: `demands/2026-09-30-platform-vault-repin-d115-parked-work.md`.
  Additive, so no consumer demands. The vault raises the ci-runner, demand-coordinator,
  dashboard, agent-runner and factory legs against this tag.
