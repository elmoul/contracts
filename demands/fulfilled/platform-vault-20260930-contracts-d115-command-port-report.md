---
demandId: platform-vault-20260930-contracts-d115-command-port
worker: contracts
date: 2026-10-01
status: done
shipped: ["v0.41.0", "commit 8e166f2 on main (feat(launcher): D115 command-execution port shapes - command request, result, error (v0.41.0))", "schemas/launcher/command.request.json", "schemas/launcher/command.result.json", "schemas/launcher/command.error.json", "tests/validate_command.py (wired into tests/run_all.py)", "Java io.platform.contracts.launcher CommandRequest/CommandResult/CommandError (pom 0.41.0)", "Python platform_contracts.launcher.command_request/command_result/command_error (0.41.0)", "TypeScript command-request/result/error.ts + dist (0.41.0)", "pinned worktree ../contracts-worktrees/v0.41.0", "D043 origin demand demands/2026-10-01-platform-vault-repin-d115-command-port.md"]
---

# Fulfillment: D115 command-execution port shapes

## State check

**Not previously shipped.** At v0.40.0 no `command.*` schema, binding or test existed. An
earlier dispatch had left the three schema files uncommitted and untagged in the working
tree (no tests, no bindings, no release). This session reviewed them, kept them, added the
test, generated every binding, and released.

## What shipped

Tag **`v0.41.0`** (commit `8e166f2`, pushed), pinned worktree
`../contracts-worktrees/v0.41.0`. Additive: no existing schema changed.

| Criterion | Where |
|---|---|
| Request keyed like `runner.dispatch-reservation`, retry replays one execution | `command.request`: `commandKey` (identical pattern to `runner.dispatch-request.dispatchKey`), `command` (a name only), optional string `parameters`, optional `demandId`. Reservation (key, `requestHash`, `executionId`) is written before any process starts; same key + same hash -> `200` replay (`replayed: true`), different hash -> `409`. `requestHash` canonicalization is exact, with two worked examples verified by the test |
| Result with exit code and evidence pointer | `command.result`: `state` `running \| exited \| unknown`, `exitCode` (integer only when `exited`, else `null`, never 0 for "not reported"), `evidence {kind log\|file\|url, location, sha256?}` required when `exited`, plus `executionId`, timestamps, `replayed` |
| Errors for unknown and refused command | `command.error`: `unknown_command` (404), `command_refused` (403, requires `reason` `disabled \| parameter_not_allowed \| caller_not_enrolled`); also `command_key_conflict` (409) and `invalid_request` (422) |
| Additive release, every consumer language generated | Java, Python and TypeScript, listed below |

## Consumer languages generated

- **Java:** `io.platform.contracts.launcher.{CommandRequest, CommandResult, CommandError}`
  (plus nested `Evidence`, `Parameters`), new `launcher-command` jsonschema2pojo execution;
  `io.platform:contracts:0.41.0`.
- **Python:** `platform_contracts.launcher.command_{request,result,error}`, wired into
  `platform_contracts/__init__.py`; `platform-contracts==0.41.0`.
- **TypeScript:** `command-{request,result,error}.ts`, exported from `index.ts`, `dist/`
  rebuilt; `@platform/contracts@0.41.0`.

## Decisions I kept from the earlier draft where the demand was silent

- `command` names a command only; no program, shell text or environment is representable.
- A refusal is decided before the reservation is written and reserves nothing, so the same
  key can be reused for a corrected request. `command_key_conflict` never overwrites.
- Restart between reservation and a settled outcome yields `state: unknown` with
  `exitCode: null`; the provider never re-runs it, the caller mints a new key.
- `demandId` and `commandKey` are excluded from `requestHash`; absent `parameters` differs
  from `{}`.

## Verification

- `python tests/run_all.py` passes, including new `tests/validate_command.py` (valid and
  invalid cases per schema; exit-code/evidence conditionals; both documented `requestHash`
  examples recomputed).
- `mvn -f gen/java/pom.xml test` and `tsc --noEmit` pass.
- D031 from the real tag: fresh venv `pip install "platform-contracts @
  git+https://github.com/elmoul/contracts.git@v0.41.0#subdirectory=gen/python"` imports all
  three launcher modules; TypeScript `npm ci` + `tsc --noEmit` clean from a copy of the
  `v0.41.0` worktree; Java `mvn test` with an empty `.m2` (`-Dmaven.repo.local`) from the
  worktree generated all five launcher classes.

## Caveats

- The `exited` => exit code/evidence/finishedAt rule is an `if/then` conditional; the
  generated bindings type those fields as nullable and do not enforce it. The schema and
  `validate_command.py` do.
- `schemas/` is still not in the Python wheel.
- D043 origin demand raised: `demands/2026-10-01-platform-vault-repin-d115-command-port.md`.
  Additive, so no consumer demands.
