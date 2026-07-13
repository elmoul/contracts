# Deployment — contracts

`contracts` is not a deployed service. It ships as three generated language
bindings, distributed per **D031**: GitHub-tag pinning, no package registry.
Each consumer clones/references this repo at a specific tag and installs the
binding locally — there is no `npm publish`/`mvn deploy`/`twine upload` step.

## Outputs

| Target | Toolchain | Artifact |
|---|---|---|
| Java | jsonschema2pojo 1.2.1 + openapi-generator-cli 7.23.0 → Maven | `io.platform:contracts:<version>` (local `.m2` install) |
| TypeScript | json-schema-to-typescript + openapi-typescript → npm | `@platform/contracts@<version>` (local `file:` dependency) |
| Python | datamodel-code-generator (pydantic v2) → pip | `platform-contracts==<version>` (git URL install) |

## Consuming a tagged release (D031)

There is no registry. Each language has its own pinning mechanism, verified
against a real clean install (see the standing invariant in `CLAUDE.md` — a
distribution path doesn't count as working until a consumer has actually
installed through it):

### Java — local `mvn install` into `.m2`

```bash
git clone https://github.com/elmoul/contracts.git
cd contracts
git checkout v0.7.0
mvn install -f gen/java/pom.xml
```

This puts `io.platform:contracts:0.7.0` in the local `.m2` cache. The consumer
repo then depends on it as an ordinary Maven dependency:

```xml
<dependency>
  <groupId>io.platform</groupId>
  <artifactId>contracts</artifactId>
  <version>0.7.0</version>
</dependency>
```

Manual step today — not yet automated in consumer builds.

### TypeScript — `file:` dependency against a pinned checkout

Stock npm's `github:owner/repo#tag` git-dependency mechanism does not work
here: it requires `package.json` at the repo root, and this repo correctly
keeps it at `gen/ts/package.json` (D031 amendment, v0.2.1 review — confirmed by
an actual `npm install` failure, not assumed). Consumers instead check out the
tag and depend on it locally:

```bash
git clone https://github.com/elmoul/contracts.git ../contracts
cd ../contracts
git checkout v0.7.0
```

```json
{
  "dependencies": {
    "@platform/contracts": "file:../contracts/gen/ts"
  }
}
```

`gen/ts/dist/` is committed at release time (not gitignored) specifically so
this works without the consumer needing to run a build step or rely on npm's
`prepare` lifecycle hook firing on a `file:` install (it doesn't reliably —
same D031 amendment).

### Python — pip git URL with `#subdirectory=`

```bash
pip install "git+https://github.com/elmoul/contracts.git@v0.7.0#subdirectory=gen/python"
```

This is the one mechanism in D031 that is a genuine remote install (no local
checkout needed) — pip's `#subdirectory=` support handles a package that
doesn't live at the repo root. Verified end-to-end in a fresh virtualenv as
part of the v0.6.2 and v0.7.0 releases (see CHANGELOG.md). If the local pip
itself is old enough to choke on the PEP 517 hook
(`ImportError: cannot import name 'cmdoptions' from 'pip._internal.cli'`, seen
on a stock Python 3.12 `ensurepip` pip in the v0.7.0 release), run
`python -m pip install --upgrade pip` in the target venv first — a local
pip-bootstrap issue, not a `contracts` packaging bug.

## Generating bindings (regenerating from schemas/)

Regeneration is manual, run from the repo root after editing files under
`schemas/`. These are the actual locked invocations used for the v0.5.1–v0.7.0
releases (see CHANGELOG.md for the full per-release rationale); toolchain
versions are pinned via `gen/java/pom.xml` (plugin versions),
`openapitools.json` (openapi-generator-cli 7.23.0), and `gen/ts/package.json`
(devDependency versions).

### Java

Two generator paths, both wired into `gen/java/pom.xml`:

- **Plain JSON Schema definitions** (`events`, `ci-runner`, `control-plane`,
  `connector` packages) — `jsonschema2pojo-maven-plugin` 1.2.1, run
  automatically as part of `mvn compile`/`mvn test` (bound to
  `generate-sources`, output under `target/generated-sources/jsonschema2pojo`,
  never `src/main/java` — see CHANGELOG.md v0.6.1 for why that separation
  matters). No separate CLI invocation needed; `mvn -f gen/java/pom.xml test`
  regenerates and compiles in one step.
- **`oneOf`-union schemas that jsonschema2pojo can't handle**
  (`state.event` → `state-event-java.yaml`, and OpenAPI documents like
  `ai.request`) — `openapi-generator-cli` 7.23.0, invoked directly:

  ```bash
  npx @openapitools/openapi-generator-cli generate \
    -i schemas/state-feed/state-event-java.yaml \
    -g java --library resttemplate \
    --additional-properties=useJakartaEe=true \
    --model-package io.platform.contracts.events \
    --global-property models,supportingFiles=false,apiTests=false,modelTests=false,apiDocs=false,modelDocs=false \
    -o gen/java
  ```

  For `ai.request`/`ai.response` (an OpenAPI document, not a plain JSON
  Schema file):

  ```bash
  npx @openapitools/openapi-generator-cli generate \
    -i schemas/ai-gateway/request.yaml \
    -g java --library resttemplate \
    --additional-properties=useJakartaEe=true \
    --model-package io.platform.contracts.aigateway \
    --global-property models,supportingFiles=false,apiTests=false,modelTests=false,apiDocs=false,modelDocs=false \
    -o gen/java
  ```

  `--library resttemplate` is required — the default `java` library emits
  Gson, which would silently swap the serialization framework for the whole
  package away from Jackson (regression caught and fixed in earlier sessions;
  verified zero `com.google.gson` imports after every regen since).

Verify: `mvn -B -f gen/java/pom.xml test`.

### TypeScript

```bash
cd gen/ts
npx json-schema-to-typescript ../../schemas/state-feed/state.event.json -o state-event.ts
npx json-schema-to-typescript ../../schemas/app/dimension.event.json -o dimension-event.ts
npx json-schema-to-typescript ../../schemas/connector/connector.vocabulary.json -o connector-vocabulary.ts
npx json-schema-to-typescript ../../schemas/connector/connector.invoke.request.json -o connector-invoke-request.ts
npx json-schema-to-typescript ../../schemas/connector/connector.invoke.response.json -o connector-invoke-response.ts
npx openapi-typescript ../../schemas/ai-gateway/request.yaml -o ai-gateway-request.ts
```

Re-export any new generated file from `index.ts`, then rebuild `dist/` (D031 —
committed, not gitignored):

```bash
npm run build   # npx tsc
```

Verify: `npx tsc --noEmit` (or `--noEmit --strict`, matching the repo's
`tsconfig.json`, which already sets `"strict": true`).

### Python

```bash
cd gen/python
datamodel-codegen \
  --input ../../schemas/state-feed/state.event.json \
  --input-file-type jsonschema \
  --output platform_contracts/state_feed/state_event.py \
  --output-model-type pydantic_v2.BaseModel
```

Same pattern (`--input-file-type jsonschema`, `--output-model-type
pydantic_v2.BaseModel`, no `--field-constraints` flag — matches this repo's
existing `conint`/`confloat`/`constr`-style output) for the other JSON Schema
files under `schemas/`. For OpenAPI documents (`ai.request`), add
`--input-file-type openapi`. Wire any new module into
`platform_contracts/__init__.py`.

For any schema with an `enum`, add `--target-python-version 3.11
--use-specialized-enum`: every generated `Status`/`Level`/`Env`-style enum in
this repo is `StrEnum`, matching `requires-python = ">=3.11"` in
`pyproject.toml`, but a plain `datamodel-codegen` invocation on at least one
locally-installed version (0.68.1, confirmed in the `v0.11.0` session) emits
a bare `Enum` instead — a silent convention drift that no existing test
catches, since schema-level validation doesn't care about the Python enum
base class. Diff the regenerated file against the previous one before
committing if you're unsure which behavior your installed version defaults
to.

Verify: `pip install ./gen/python` in a scratch venv, then
`python -c "import platform_contracts"` plus a round-trip
(`model_dump_json()` → `model_validate_json()`) on any newly generated model.

## Releasing (tag + version bump)

1. Bump the affected package's version file(s): `gen/java/pom.xml`
   (`<version>`), `gen/ts/package.json` (`"version"`),
   `gen/python/pyproject.toml` (`[project] version`). Only bump the version
   files for languages whose generated output actually changed in this
   release (see CHANGELOG.md v0.6.1 for an example of a Java-only patch that
   left TS/Python versions untouched).
2. Regenerate + verify all three bindings per the commands above.
3. Add a CHANGELOG.md entry (see its own header for the format).
4. Run the real D031 acceptance test for every language whose packaging
   changed — a clean install from the actual tagged path (Java: fresh `.m2`
   local install; TS: `file:` install into a scratch project; Python: fresh
   venv + git-URL pip install) — not just a local build. Two past releases
   (v0.2.1 npm, v0.6.2 Python) shipped on an untested packaging assumption;
   don't repeat that.
5. `git tag vX.Y.Z && git push origin main --tags`.
6. **Raise the release-notification demands (D043 — see CLAUDE.md's Release
   checklist section for the full rule).** Always a demand `to: [<origin>]`
   ("re-pin and adopt"); on a breaking release, also a demand to every
   consumer of the changed schema(s) ("adopt or explain by when"), enumerated
   via control-plane's `GET /registry` consumer graph (D014). The tag is not
   done until these are raised and pushed as their own standalone coordination
   commit(s), per `DEMAND_SYSTEM.md` §3.

## No runtime dependencies

There is no server to start, no container to build, no infrastructure to
provision.
