# Deployment — contracts

`contracts` is not a deployed service. It ships as three generated language bindings.

## Outputs

| Target | Toolchain | Artifact |
|---|---|---|
| Java | openapi-generator + jsonschema2pojo → Maven | `io.platform:contracts:<version>` |
| TypeScript | openapi-typescript + json-schema-to-typescript → npm | `@platform/contracts@<version>` |
| Python | datamodel-code-generator → pip | `platform-contracts==<version>` |

## Generating bindings

Generation is manual for now (CI automation tracked in ci-runner §8). Run from the repo root:

```bash
# Java
# openapi-generator-cli generate -i schemas/openapi/<file>.yaml -g spring -o gen/java/
# jsonschema2pojo --source schemas/json-schema/ --target gen/java/

# TypeScript
# npx openapi-typescript schemas/openapi/<file>.yaml -o gen/ts/<file>.ts
# npx json-schema-to-typescript schemas/json-schema/<file>.json -o gen/ts/<file>.ts

# Python
# datamodel-codegen --input schemas/ --output gen/python/
```

Exact commands will be documented once toolchain versions are locked.

## Publishing

Tag the repo with the contract version (e.g., `v1.2.0`) to trigger a publish. Until CI automation is in place, publish manually to the package registry.

## No runtime dependencies

There is no server to start, no container to build, no infrastructure to provision.
