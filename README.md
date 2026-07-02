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
| `CHANGELOG.md` | Per-contract semver history |

## Consuming this repo

Add the generated binding as a versioned Maven/npm/pip dependency. Pin the version. Never copy schemas directly.

## Generating bindings

See `DEPLOYMENT.md`.

## Versioning

Each contract is versioned independently (semver). Additive changes (new optional field) are minor bumps; removals, renames, or new required fields are major bumps.
