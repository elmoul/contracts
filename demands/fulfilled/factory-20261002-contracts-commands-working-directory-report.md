---
demandId: factory-20261002-contracts-commands-working-directory
worker: contracts
date: 2026-10-02
status: done
shipped: ["v0.45.0", "commit 70300a7 on main (feat(app): descriptor commands.workingDirectory (v0.45.0))", "schemas/app/descriptor.json (commands.workingDirectory, enum hexagon|app, default hexagon)", "fixtures valid-wrapped-working-directory-app, valid-in-repo-working-directory-hexagon, invalid-working-directory-value; tests/validate_app_descriptor.py", "Python and TypeScript bindings 0.45.0 (Java version bumped, output unchanged)", "pinned worktree ../contracts-worktrees/v0.45.0", "D043 origin demand demands/2026-10-02-factory-repin-commands-working-directory.md"]
---

# Fulfillment: app.descriptor commands.workingDirectory

## State check

Not previously shipped: v0.44.0's `commands` object had only `test`, `review`, `deploy`, and the description said cwd is always the hexagon root.

## What shipped

Tag `v0.45.0` (commit `70300a7`, pushed), additive. `commands.workingDirectory` is an optional enum `hexagon` | `app`, default `hexagon` when absent. The description states: `hexagon` is the hexagon repository root, `app` is `<hexagon>/<code.appRoot>`; for `in-repo` layout (`appRoot: "."`) both resolve to the same directory; the resolved directory is always inside the hexagon (`appRoot` is only `.` or `app`), which the launcher's trust rule relies on. The top-level description's "cwd is the hexagon root" line now points at the field.

Fixtures: wrapped + `app`, in-repo + `hexagon`, field absent (existing fixtures, e.g. `valid-in-repo-full`), and negative `workingDirectory: product`.

## Verification

- `python tests/run_all.py`: all validators pass.
- Bindings regenerated (datamodel-codegen, json-schema-to-typescript, tsc `dist/`).
- D031 clean install from the real tag: fresh venv `pip install git+https://github.com/elmoul/contracts.git@v0.45.0#subdirectory=gen/python` accepts `Commands(workingDirectory='app')` and defaults to `hexagon`; fresh clone of the tag plus `npm ci` with an empty cache compiles a `--strict` file using the field.

## Caveats

- Java clean install and `mvn test` not run (output unchanged; version bumped only).
- The schema cannot tie `workingDirectory: app` to `layout: wrapped`; any `appRoot` makes it valid, by design (in-repo resolves identically).
- Generated Python/TS types are unchanged in strictness; validate against the schema as before.
