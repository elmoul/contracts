---
session_id: 2026-09-27_1050_fulfill-demand-ci-runner-20260927-contra
agent: contracts
model: deepseek-flash
started: 2026-09-27T10:50:55+00:00
ended: 2026-09-27T10:54:52+00:00
task: "Fulfill demand ci-runner-20260927-contracts-ci-headsha-lookup (headSha on ci.run/BuildResult + ci-runner result lookup interface, release v0.34.0)"
priority: 2
status: done
launch: interactive
decisions: []
changes:
  - "schemas/state-feed/state.event.json + state-event-java.yaml: optional headSha (^[0-9a-f]{40}$) on CiRunPayload, both files together (check_state_event_sync.py enforces sync)"
  - "schemas/ci-runner/build-result.yaml: same optional headSha on BuildResult"
  - "schemas/delivery-api/ci-runner-results.openapi.yaml: NEW -- GET /delivery/v1/ci-results/{runId}/{jobId} and GET /delivery/v1/ci-results?repository=&revision=, both -> delivery.producer-result, plus the CiResultNotFoundError shape (code const ci_result_not_found, retryable const false)"
  - "schemas/delivery/delivery.error.json: ci_result_not_found + producer_unavailable added to the code table and examples; code stays an open string"
  - "docs/task-delivery.md: NEW section CI result routes; Producers ci-runner row and handoff matrix row updated (gap closed at the interface level, implementation stays with ci-runner); v0.34.0 repin section; Bindings note corrected (these two shapes DO have Java bindings)"
  - "gen/ts build-result.ts + state-event.ts + dist/ (headSha?: string, dist rebuilt per D031)"
  - "gen/java src events/CiRunPayload.java regenerated (openapi-generator 7.23.0) + pom.xml 0.30.0 -> 0.34.0 -- this release changes Java output, unlike v0.33.0"
  - "gen/python ci_runner/build_result.py + state_feed/state_event.py regenerated with their previous flags, so the diff is only the new field + timestamp"
  - "tests/validate_state_event.py: 3 new ci.run cases (40-hex accepted, abbreviated rejected, uppercase rejected)"
  - "tests/validate_delivery.py: check_ci_api + a passed ci-runner producer-result fixture (63 cases)"
  - "gen/java/src/test/.../CiHeadShaTest.java: NEW, 5 cases (44 in the module)"
  - "CHANGELOG.md: v0.34.0 entry"
  - "demands/2026-09-27-ci-runner-repin-headsha-lookup.md + demands/fulfilled/ci-runner-20260927-contracts-ci-headsha-lookup-report.md (D043 origin demand + fulfillment report)"
lessons:
  - "This demand had TWO prior supervisor-opened sessions that left no commits: 1130 closed status: failed and 1150 was never closed (still marked open, will read as abandoned). But 1130 DID leave a real partial working tree -- schemas and tests, uncommitted. Checking git status and the session files before writing anything turned a 'redo from scratch' into 'review, finish, release'. The uncommitted tree was sound and all validators passed on it as-is."
  - "openapi-generator rewrites EVERY model in the output dir because the @jakarta.annotation.Generated date line changes in each. That is not damage -- the v0.30.0 release committed the same churn (23 files, 1/1 line each). Do not 'clean it up' by reverting; it is the honest output of the pinned generator invocation, and reverting would make the next regen differ."
  - "npx json-schema-to-typescript/vite-style build steps rewrite committed dist/ files with identical content, so git status shows ~20 modified files while git diff --numstat shows only the 2 that actually changed. Check numstat, not status, before panicking about collateral churn."
  - "The version in this demand was misjudged in the partial tree as 0.33.0, which was already tagged (agent-runner keyed dispatch). Always check `git tag` before stamping a release version -- the demand said 'v0.32.0 or later', which is permission for a later tag, not for reusing a taken one."
  - "D031 acceptance is per-language and each path fails differently: Python (fresh venv + git URL), TS (scratch project + file: dep + strict tsc), Java (fresh -Dmaven.repo.local install). The Java one is the easiest to skip and the only way to know the 0.30.0 -> 0.34.0 pom bump actually produces an installable artifact."
context_missing: []
notes_used: []
vault_sync: none
close: confirmed
---


## Log

**10:50 Session opened** via `brain session open`.

**10:52 State check first.** `demands/` had no file for this demand; the coordinator
(`GET /inbox/contracts` on 127.0.0.1:8082) returned it `open`, `readyFor: contracts`,
wave 1, with the five acceptance criteria verbatim. Two prior sessions on the same
demand (1130 `failed`, 1150 unclosed) had left an uncommitted working tree:
`schemas/ci-runner/build-result.yaml`, `schemas/state-feed/state.event.json`,
`state-event-java.yaml`, `delivery.error.json`, both `tests/validate_*.py`, and a new
`schemas/delivery-api/ci-runner-results.openapi.yaml`. `python tests/run_all.py`
passed on that tree as-is, so the prior work was sound and worth finishing rather
than redoing. Not shipped: no tag carried the capability (latest was v0.33.0,
agent-runner keyed dispatch), and nothing was committed.

**10:53 Finished and released as v0.34.0** (not v0.33.0 as the partial tree had
stamped -- v0.33.0 was taken). Retargeted every version stamp, wrote the docs
(§CI result routes, Producers row, handoff matrix, repin section, Bindings
correction), the CHANGELOG entry, and the D043 origin demand + fulfillment report.
Regenerated all three bindings; added the Java `CiHeadShaTest` (44 tests green) on
top of the prior session's Python validator cases.

**10:54 Tagged and verified.** Tag `v0.34.0` on `9f6c2ea`, pushed; pinned worktree
`../contracts-worktrees/v0.34.0`; coordination commit `840b799` raised the ci-runner
re-pin demand. D031 acceptance re-run against the pushed tag in all three languages:
Python fresh-venv git-URL install -> `platform-contracts-0.34.0`; TS scratch `file:`
install -> `@platform/contracts@0.34.0` + `tsc --strict --noEmit`; Java
`mvn install` into a fresh `-Dmaven.repo.local` -> `contracts-0.34.0.jar`.

**10:54 Session closed via `brain session close` (status: done).** Nothing left
running: the Maven/npx JVMs from this session all exited (verified by process start
times -- the surviving java.exe/node.exe predate the session or belong to other
repos).
