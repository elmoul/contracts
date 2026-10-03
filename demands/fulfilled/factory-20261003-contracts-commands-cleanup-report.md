---
demandId: factory-20261003-contracts-commands-cleanup
worker: contracts
date: 2026-10-03
status: done
shipped: ["v0.46.0", "commit 9f8109d on main (feat(app): descriptor commands.cleanup (v0.46.0))", "schemas/app/descriptor.json (commands.cleanup argv, cleanup contract in top-level description)", "fixtures valid-in-repo-cleanup, valid-wrapped-cleanup-working-directory-app, valid-in-repo-no-cleanup, invalid-cleanup-shell-string, invalid-cleanup-empty-argv; tests/validate_app_descriptor.py", "Python and TypeScript bindings 0.46.0 (Java version bumped, output unchanged)", "CHANGELOG entry in follow-up commit on main", "pinned worktree ../contracts-worktrees/v0.46.0", "D043 origin demand demands/2026-10-03-factory-repin-commands-cleanup.md"]
---

# Fulfillment: app.descriptor commands.cleanup

## State check

Not previously shipped: v0.45.0's `commands` had `workingDirectory`, `test`, `review`, `deploy` and no `cleanup`.

## What shipped

Tag `v0.46.0`, additive. `commands.cleanup` is an optional argv array (same `argv` def as the other commands: non-empty array of non-empty strings, never a shell string), run in the directory `commands.workingDirectory` resolves to. The schema's top-level description states the contract: the launcher passes `COMMAND_PARAM_BRANCH` (integration branch) and `COMMAND_PARAM_COMMIT` (40-hex merge commit); exit 0 = checkout back on the integration branch; exit 3 = refused with nothing touched (dirty tracked tree, commit not on `origin/<branch>`, or local commits origin lacks), informational; any other exit = failure; Factory records refusals and failures with their reason and never holds an issue back from Staging because of them. The `workingDirectory` description now names cleanup too.

Fixtures: valid in-repo with cleanup, valid wrapped with cleanup + `workingDirectory: app`, valid without cleanup, invalid shell string, invalid empty argv.

## Verification

- `python tests/run_all.py`: all validators pass.
- Bindings regenerated (datamodel-codegen with `StrEnum` retained, json-schema-to-typescript, tsc `dist/`).
- D031 clean install from the real tag: fresh venv `pip install git+https://github.com/elmoul/contracts.git@v0.46.0#subdirectory=gen/python` accepts `Commands(cleanup=[...], workingDirectory='app')` and rejects a string; fresh clone of the tag plus `npm ci` with an empty cache compiles a `--strict` file using `commands.cleanup`.

## Caveats

- The v0.46.0 tag commit does not contain the CHANGELOG entry (an edit failed on an encoding error before the commit); it is on `main` in the next commit. Tag not moved, since it was already pushed.
- The contract description lives in the top-level schema description, not on the `cleanup` property, because a `$ref` with a sibling description makes json-schema-to-typescript emit a duplicate `Argv1` type.
- Java clean install and `mvn test` not run (output unchanged; version bumped only).
- Pin consumers: control-plane, launcher, portfolio and factory can pin `v0.46.0`.
