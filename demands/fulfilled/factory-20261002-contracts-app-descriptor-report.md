---
demandId: factory-20261002-contracts-app-descriptor
worker: contracts
date: 2026-10-02
status: done
shipped: ["v0.42.0", "commit 0dc096c on main (feat(app): app.descriptor schema and registry app summary (v0.42.0))", "schemas/app/descriptor.json", "schemas/control-plane/registry.entry.json (optional app object)", "tests/validate_app_descriptor.py (wired into tests/run_all.py)", "tests/fixtures/app-descriptor/ (3 valid, 8 invalid)", "Java io.platform.contracts.app.AppDescriptor (pom 0.42.0)", "Python platform_contracts.app.descriptor (0.42.0)", "TypeScript app-descriptor.ts + dist (0.42.0)", "pinned worktree ../contracts-worktrees/v0.42.0", "D043 origin demand demands/2026-10-02-factory-repin-app-descriptor.md"]
---

# Fulfillment: app.descriptor schema

## State check

**Not previously shipped.** At v0.41.0 there was no `schemas/app/descriptor.json`, binding or
test; the only trace was the supervisor-opened session file with no changes.

## What shipped

Tag **`v0.42.0`** (commit `0dc096c`, pushed), pinned worktree `../contracts-worktrees/v0.42.0`.
Additive: `registry.entry` gains one optional property; nothing else existing changed.

| Criterion | Where |
|---|---|
| `schemas/app/descriptor.json` validates the section 6 shape | all listed fields; `additionalProperties: false` throughout; `commands` and `urls` optional so an ungated app can omit them |
| Enforced rules | `third-party` => `fork` required and non-empty, `delivery.mode: pr-only`; empty `requiredChecks` => `pr-only`; `in-repo` => `appRoot "."`, `wrapped` => `appRoot "app"` (`appRoot` enum is `"."`/`"app"`, so the iff holds); commands are `$defs/argv` (array, minItems 1, non-empty strings), so a shell string is a type error; no env map and no free-form object anywhere |
| Distinct from `app.manifest` | the schema description says so in bold and records the launcher env contract |
| Fixtures in the repo's test suite | `tests/fixtures/app-descriptor/`: valid in-repo full (Portfolio-shaped), in-repo ungated pr-only, wrapped third-party pr-only with fork; invalid: third-party no fork, empty fork, third-party full, empty checks full, in-repo with appRoot `app`, wrapped with appRoot `.`, shell-string command, env map. `tests/validate_app_descriptor.py` is in `tests/run_all.py` |
| Registry `app` summary | `registry.entry.app {name, trackerKey, layout, ownership, deliveryMode, devUrl?}`, optional; entries without it still validate (tested) |
| Additive, tagged, reported | `v0.42.0` |

## Verification

- `python tests/run_all.py`: all validators pass.
- `npx tsc --noEmit` in `gen/ts`: clean; `dist/` rebuilt.
- D031 clean install from the real tag: fresh venv `pip install git+https://github.com/elmoul/contracts.git@v0.42.0#subdirectory=gen/python` imports `AppDescriptor` and `RegistryEntry`; fresh clone of the tag plus `npm install` with an empty npm cache resolves `AppDescriptor`/`RegistryEntry` types under `tsc`.
- Java: the generated `AppDescriptor` (+ `Code`, `Delivery`, `Commands`, `Review`, `Deploy`, `Tracker`, `Urls`) compiled in `mvn -f gen/java/pom.xml test`. That run reported one failure, `BoardControllerTest.getBoardShowsTheFleetsOpenDemandsAndACleanDispatchOrderJoin` in the demand-coordinator tests; it asserts against the live demand board, which gained a new dashboard demand today, and is unrelated to this change. A fresh-`.m2` install from the tag was not run for Java.

## Caveats for consumers

- The rules are `if/then`, which `datamodel-codegen` and `json-schema-to-typescript` do not generate (known, see DEPLOYMENT.md). Generated Python/TS types accept shapes the schema refuses; validate `app.yaml` against the JSON Schema.
- The Python `schema` field is `schema_` (alias `schema`); round-trip with `model_dump(by_alias=True)`.
- Decisions where the spec was silent: `releaseBranch`, `fork` (for owned), `urls` and `commands` are optional; `tracker.youtrack` is `^[A-Z][A-Z0-9]*$`; `repo` and URLs must be `http(s)://`.
