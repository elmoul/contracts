# contracts

The platform's shared contract kernel. Schema-first; every other hexagon pins a version of this repo.

Schemas are the source of truth. Language bindings (Java, TypeScript, Python) are generated from them — do not edit files under `gen/` by hand.

## Structure

| Path | Contents |
|---|---|
| `schemas/` | Source schemas (OpenAPI 3.1 and JSON Schema) |
| `gen/java/` | Generated Maven artifact (do not edit) |
| `gen/ts/` | Generated npm package (do not edit) |
| `gen/python/` | Generated pip package (do not edit) |
| `CHANGELOG.md` | Repo-wide, per-language-binding release history |

## Consuming this repo

Add the generated binding as a versioned Maven/npm/pip dependency. Pin the version. Never copy schemas directly.

## Generating bindings

See `DEPLOYMENT.md`.

## Testing

| Target | Command |
|---|---|
| Java | `mvn -f gen/java/pom.xml test` |
| TypeScript | `cd gen/ts && npm ci && npx tsc --noEmit` |
| Python (schema validators) | `python tests/run_all.py` — runs every `tests/validate_*.py` schema validator plus `check_state_event_sync.py` in one command, stopping at the first failure |

`tests/run_all.py` requires the `jsonschema` package (`pip install ./gen/python` or a venv with it available) — see `DEPLOYMENT.md` for the exact toolchain setup.

## Versioning

Versioned repo-wide, per language binding (semver) — see CHANGELOG.md's header
for the current reality vs. the original per-contract intent. Additive changes
(new optional field) are minor bumps; removals, renames, or new required
fields are major bumps.
