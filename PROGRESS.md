# Progress

## 2026-07-02 — Session 1

**State:** v0.1.0 tagged and pushed. Repo bootstrapped; all phase A–D schemas authored and committed; three codegen targets (Java/openapi-generator+jsonschema2pojo, TS/openapi-typescript+json-schema-to-typescript, Python/datamodel-code-generator) generated and committed into gen/.

**Decisions taken this session:**
- schemas/ organised by catalog section (app/, ai-gateway/, state-feed/, control-plane/) — owner to record in vault if promoted to decision.
- app.health uses Spring Actuator shape (status: UP/DOWN/OUT_OF_SERVICE/UNKNOWN) — confirmed by architect.
- AppManifest.class corrected to D010 risk tiers [low-stakes, health-class, kids-class].
- BlockedResponse added to 402 on /ai/request per D023.

**Next step:** First consuming hexagon can now pin `io.platform:contracts:0.1.0` / `@platform/contracts@0.1.0` / `platform-contracts==0.1.0`. When control-plane or ai-gateway starts schema work, reference the stubs in schemas/control-plane/ and schemas/ai-gateway/ respectively. Codegen CI automation tracked in ci-runner spec §8.

## 2026-07-02 — Session 2

**State:** v0.2.0 tagged and pushed. Reviewed and released two changes that had landed on `main` from other repos' sessions reaching across the boundary mid-debug (process gap now closed in root `CLAUDE.md`).

**Decisions taken this session:**
- Kept `jakarta.annotation-api` in `gen/java/pom.xml` (was correct) but folded it into a real tagged release — it had landed after `v0.1.1` with no version bump, so the old tag no longer reflected a compilable state.
- Kept `schemas/ci-runner/build-command.yaml` / `build-result.yaml` as-is — reviewed, sound.
- Deleted `schemas/ci-runner/ci-run.payload.json` (an orphaned second definition of the `ci.run` payload) and revised `CiRunPayload` inside `schemas/state-feed/state.event.json` in place to the richer, ci-runner-shaped fields (GitHub `workflow_job` granularity). `state.event.json`'s `oneOf` remains the single source of truth for state-feed payloads — no per-hexagon payload files. Discriminator stays `ci.run` (dot); ci-runner's local `ci-run` (dash) TS types are the side that needs to conform.
- Regenerated all three language bindings for `state.event` and verified each compiles/validates (`mvn compile`, `tsc --noEmit --strict`, Python round-trip).
- Versioned as a minor bump (0.1.1 → 0.2.0), not major — reasoning in `CHANGELOG.md`: standard pre-1.0 semver, and no hexagon has actually pinned/built against `contracts` yet.

**Next step:** When ci-runner starts its own build (per its spec), update its local TS types to use `ci.run` (dot) instead of `ci-run`, and consume `CiRunPayload` from the generated binding rather than hand-rolling it.

## 2026-07-02 — Session 3

**State:** v0.2.1 tagged and pushed (patch, no schema changes). Closed two gaps from the v0.2.0 review.

**Decisions taken this session:**
- Codegen'd `BuildCommand`/`BuildResult` across all three targets (shipped as schemas in v0.2.0 but never actually generated). Java uses a second `jsonschema2pojo` execution (`sourceType=yamlschema`, package `io.platform.contracts.cirunner`) since these are plain object schemas, unlike `state.event.json`'s `oneOf` which needs the openapi-generator workaround.
- Per new D031 (git-tag pinning, no registry), added `gen/ts/tsconfig.json` (was missing) and `"prepare": "tsc"` to `gen/ts/package.json` so `npm install github:elmoul/contracts#v0.2.1` builds `dist/` on install. Verified with a real scratch-project install against the pushed tag. `gen/ts/dist/` is now gitignored, not committed.

**Next step:** None pending from this session. Java/Python consumers still install via version-pinned Maven/pip coordinates per D031 — only TS needed the `prepare` fix.

## 2026-07-02 — Session 4

**State:** v0.2.2 tagged and pushed (patch, no schema changes). Fixed the TS consumption mechanism per amended D031.

**Decisions taken this session:**
- Session 3's git-URL fix (`prepare: tsc` on `npm install github:...`) doesn't work in practice — stock npm requires `package.json` at the repo root to resolve a git dependency at all; there's no subdirectory syntax to point it at `gen/ts/`. D031 amended in the vault to switch consumption to `"@platform/contracts": "file:<path-to-checkout>/gen/ts"`.
- Committed `gen/ts/dist/` (removed from `.gitignore`), regenerated fresh via `npx tsc`. Removed the `prepare` script — reproduced that npm still runs `prepare` on a `file:` install too, and it fails there (no `devDependencies` in a linked install), so relying on it was actively harmful, not just ineffective. `build: tsc` stays as a manual pre-release step. `types` now points at `dist/index.d.ts` instead of source `index.ts`.
- Verified end-to-end in a scratch project outside this repo: `file:` install resolves, `require('@platform/contracts')` works, and a `.ts` file importing `BuildCommand`/`BuildResult`/`UsageEvent` passes `tsc --noEmit --strict`.

**Next step:** None pending from this session. If control-plane or ai-gateway starts consuming `@platform/contracts` from TS, they should pin via `file:` path to a checked-out tag, not a git URL.

## 2026-07-03 — Session 5

**State:** v0.3.0 tagged and pushed (minor, additive). Fleshed out both control-plane STUB schemas per owner-approved design.

**Decisions taken this session:**
- Verified nothing consumes `hexagon.descriptor`/`registry.entry` yet — control-plane chunk 1 deliberately uses its own `RegistryEntry` record and has zero `contracts` dependency (`pom.xml` comment confirms this is intentional pending this design pass) — so this is a purely additive minor release, no rebuild set to compute.
- `hexagon.descriptor.json`: full schema for the HEXAGON.md frontmatter block (`functionalName`, `kind`, `side`, `status`, optional `class`/`spec`/`decisions`/`infra`, required `deps`, optional nested `contracts.{pin,binding,used}`). Fixed the stub's `side` enum bug — added `ui` (dashboard's side, skipped by the theme-check). Deliberately no `version`, `consumedBy`, or `ports` fields — documented why in the schema description so they don't get re-added later.
- `registry.entry.json`: full schema for control-plane's served record — descriptor summary + changing state (`repoUrl`, `version`, `contractsPin`, `updatedAt`, app-only `appId`/`class`/`plan`). `status` adds `suspended` (registry-only, not a repo property).
- Regenerated all three bindings (Java: new `jsonschema2pojo` execution, package `io.platform.contracts.controlplane`; TS: `hexagon-descriptor.ts`/`registry-entry.ts`, `dist/` rebuilt fresh per D031; Python: `platform_contracts/control_plane/`). Verified `mvn compile`, `tsc --noEmit --strict`, and a Python round-trip + rejected-bad-doc all pass.
- Added `tests/validate_control_plane.py` — first structured test file in this repo (prior releases verified only by compiling generated bindings). Validates the JSON Schemas directly against example documents: known-good (treasury's real values) and known-bad (bad `side`, missing `functionalName`) for both schemas.

**Next step:** Nine repos adopt the `hexagon.descriptor` frontmatter in HEXAGON.md in parallel; control-plane's inventory reader builds against the generated Java `HexagonDescriptor`/`RegistryEntry` types (`io.platform.contracts.controlplane`). Both gated on this release — v0.3.0 is now pinnable.

## 2026-07-04 — Session 7 (build-stabilization attempt, INCOMPLETE — no release cut)

**State:** v0.6.0 remains the latest tag. Attempted the requested `gen/java` flakiness fix; the assigned hypothesis (incremental-compilation staleness) did not hold up under verification, so per the task's own stop condition I did **not** bump the version, touch `CHANGELOG.md`, or commit/tag anything. `gen/java/pom.xml` has one uncommitted, unverified change sitting in the working tree (see below) — next session should pick this up rather than assume it's safe to build on.

**What I tried:** Added an explicit `maven-compiler-plugin` block to `gen/java/pom.xml` with `<useIncrementalCompilation>false</useIncrementalCompilation>` (the plugin previously had no explicit config block, so this also surfaced a latent "plugin version not pinned" Maven warning — did not fix that, out of scope for this task).

**Verification: ran `mvn clean test` 8x in a row.** Result: 5/8 BUILD SUCCESS (9/9 tests passing each time), 3/8 BUILD FAILURE (runs 1, 2, 3, 7) — i.e. still roughly the same ~50% failure rate as before the change on this run. The incremental-compilation fix did not move the needle.

**What the failures actually look like (this rules out the incremental-compilation hypothesis):**
- Run 1: `default-compile` succeeded (30 source files), but `default-testCompile` failed with `cannot access io.platform.contracts.connector.ConnectorVocabulary … bad class file … class file truncated at offset 0`. The `.class` file physically exists on disk (built moments earlier in the same reactor run) but reads back as zero-length.
- Run 2: `default-compile` (32 files) and `default-testCompile` (3 files) both reported success, but `surefire` then failed to fork with `Unable to create test class 'ConnectorContractsRoundTripTest'` — a class that had just "successfully" compiled one phase earlier.
- Runs 3 & 7: `default-compile` reported **33** source files (vs. 30 in run 1, 32 in run 2 — the compiled file count is not even consistent between clean runs of an unmodified tree) and `default-testCompile` failed with `package io.platform.contracts.connector does not exist` / `package Verb does not exist` — i.e. entire generated packages were invisible to javac's directory scan, not just individual stale class files.
- All four failures point at `io.platform.contracts.connector` (jsonschema2pojo's `connector` execution, last of four in the same `generate-sources` phase) and, in run 7, also `io.platform.contracts.cirunner`/state-feed-derived symbols — i.e. it isn't confined to one execution or one static/generated distinction.

**Root cause is very likely something else entirely, and it's structural, not a javac setting:** `gen/java/pom.xml`'s jsonschema2pojo executions write generated sources straight into `${project.basedir}/src/main/java` — a source directory that's also scanned by `maven-compiler-plugin` in the very same reactor build, not into `target/generated-sources` (the conventional location, which is excluded from `mvn clean`'s scope but isolated from hand-maintained/checked-in sources and generated fresh under `target/` on every build). Four separate jsonschema2pojo executions run back-to-back in `generate-sources`, each writing files into that shared tree, immediately followed by `default-compile`'s source-root scan. The varying compiled-file counts (30/32/33) across otherwise-identical clean runs, plus the zero-length class file and the "package does not exist" errors, are consistent with a write/flush-then-scan race on NTFS (very plausibly amplified by Windows Defender real-time scanning newly-created files) rather than with javac's incremental-compilation cache, which `useIncrementalCompilation=false` disables but which was never in play here since every run starts from `mvn clean`.

**What I did NOT do, per the task's explicit stop condition:** guess at a second fix (e.g. moving `outputDirectory` to `target/generated-sources/jsonschema2pojo` and adding `build-helper-maven-plugin:add-source`, which would be the conventional fix for this class of race, but is a bigger structural change than "flip one flag" and deserves its own review/verification pass). No version bump, no `CHANGELOG.md` entry, no commit, no tag. `gen/java/pom.xml`'s `useIncrementalCompilation=false` change is left uncommitted in the working tree — it's harmless but unproven; discard or keep at the owner's discretion.

**Next step:** Owner decision needed on whether to move jsonschema2pojo's four `outputDirectory` settings to a `target/generated-sources/...` path (with `build-helper-maven-plugin` wiring the generated root back in as a compile source root) instead of writing into checked-in `src/main/java` — that's the structural fix that would actually separate "generate" and "compile" by directory instead of by timing, and it should be verified with the same 8x-clean-build loop before any patch release ships. Until then, Wave 4 (F1 connector-gmail, state-feed pin bump) should treat a `contracts` clean build as roughly coin-flip and may want to retry CI on failure rather than assume a genuine break.

## 2026-07-04 — Session 10 (build-stabilization, RESOLVED — v0.6.1 released)

**State:** v0.6.1 tagged and pushed (patch, Java binding only, no schema change). The structural fix Session 7 flagged as the likely real fix is confirmed: 10/10 clean `mvn clean test` runs passed, versus the ~50% failure rate observed in Sessions 7's 8x loop.

**What I did:**
- First reverted Session 7's dead-end `useIncrementalCompilation=false` block on `maven-compiler-plugin` (proven ineffective: 5/8 clean builds still failed with it in place) — `gen/java/pom.xml` diff against HEAD is now empty for that piece.
- Applied the structural fix: moved all four `jsonschema2pojo` executions' (`events`, `ci-runner`, `control-plane`, `connector`) `outputDirectory` from `${project.basedir}/src/main/java` to `${project.basedir}/target/generated-sources/jsonschema2pojo`. Verified `jsonschema2pojo-maven-plugin` 1.2.1 registers this directory as a compile source root automatically (disassembled the plugin jar, confirmed `addCompileSourceRoot` is called unconditionally) — no `build-helper-maven-plugin` needed.
- Removed the now-stale generated files from `src/main/java`: `events/UsageEvent.java`, `events/DimensionEvent.java` (jsonschema2pojo-owned only — `Origin.java`, `ComponentHealthEvent.java`, and the rest of `events/` are openapi-generator-derived static files, left untouched), all of `cirunner/` (`BuildCommand.java`, `BuildResult.java`), all of `controlplane/` (`Contracts.java`, `HexagonDescriptor.java`, `RegistryEntry.java`), all of `connector/` (`ConnectorInvokeRequest.java`, `ConnectorInvokeResponse.java`, `ConnectorVocabulary.java`, `Verb.java`) — 11 files total, confirmed via `git status` that nothing else was touched.
- Verified no consumer depends on these files being physically present in git: read `control-plane/PROGRESS.md`, which confirms it runs `mvn install -DskipTests` from a full `../contracts` checkout at the pinned tag itself (D031, no registry) — it never reads `contracts`' `src/main/java` directly, only the resulting installed jar. `ci-runner` has no Java build at all (Node/TS only), so it's unaffected regardless.
- `mvn clean install` once: BUILD SUCCESS, jar produced, 9/9 tests green.

**Verification — `mvn clean test` x10:** 10/10 BUILD SUCCESS, 9/9 tests passing every run. Zero failures, versus Session 7's 3/8 failure rate on the same loop before this fix. `gen/ts` (`npx tsc --noEmit --strict`) and `gen/python` (`python -c "import platform_contracts"`) both confirmed unaffected — exit 0, no content changes, versions left at 0.6.0 (only `gen/java/pom.xml` bumped to 0.6.1, matching the v0.2.2 precedent of bumping only the affected binding's version file).

**Next step:** None pending. `contracts` clean builds should now be reliable — Wave 4 consumers (F1 connector-gmail, state-feed) no longer need to treat a `contracts` build as a coin-flip or retry-on-failure. If flakiness resurfaces despite this fix, that would point at something outside this hypothesis entirely (e.g. AV/filesystem-locking on `target/` itself) and deserves fresh investigation rather than a third guess at `src/main/java` timing.

## 2026-07-04 — Session 6

**State:** v0.4.0 tagged and pushed (minor, additive). PlantPal integration chunk 1 — extended `ai.request` for photo-based/multimodal calls, run in parallel with PlantPal's own chunk 0 clone (no dependency between them).

**Decisions taken this session:**
- Added optional `media` field to `AiRequest` (array of `{data, mimeType}`) per gateway-spec §8-3's existing lean toward "same envelope, optional field" over a separate vision endpoint — PlantNet (and any future vision provider) rides `ai.request`, full stop. `AiResponse`/`BlockedResponse` untouched — responses stay text-only.
- Confirmed `AiRequest.java`'s generator header (`JavaClientCodegen`) meant it was never on the `jsonschema2pojo` path the rest of `gen/java/pom.xml` uses — it's generated straight from `request.yaml` (an OpenAPI doc, not a plain JSON Schema) via `openapi-generator-cli generate -g java --library resttemplate --additional-properties=useJakartaEe=true --model-package io.platform.contracts.aigateway --global-property models,supportingFiles=false,apiTests=false,modelTests=false,apiDocs=false,modelDocs=false`. Reconstructed and reused this exact invocation (verified byte-for-byte match on the unchanged `AiResponse`/`BlockedResponse` output before trusting it).
- Same story for TS (`openapi-typescript`, not `json-schema-to-typescript` — that tool is only for the plain-JSON-Schema targets like control-plane) and Python (`datamodel-code-generator` **without** `--field-constraints`, since that flag inverts to `Field(ge=...)` inline style — the existing file uses `conint`/`confloat`/`constr`, which is the *default*, unflagged behavior).
- Regenerated all three bindings; verified `mvn compile`, `tsc --noEmit --strict` (after `npm install` in `gen/ts` — no `node_modules` existed locally), and a Python round-trip with media, without media (proves optionality), and a rejected missing-`mimeType` case.
- Added `tests/validate_ai_request.py` — first structured test for `ai-gateway` (same gap `validate_control_plane.py` closed for control-plane in v0.3.0). Pulls `AiRequest` out of `request.yaml`'s `components.schemas` via PyYAML since the source is an OpenAPI document, not a standalone schema file.

**Next step:** PlantPal chunk 0 (clone/scaffold) proceeds independently. Once PlantPal starts consuming `contracts`, it pins `v0.4.0` and builds its four AI-calling modules (identification, treatment, species enrichment, chat) against the generated `AiRequest` with `media` populated for photo calls, omitted for text-only ones. `ai-gateway`'s own build still needs to actually read/forward `media` to a vision-capable provider (PlantNet) — that's gateway-side work, not a contracts change.

## 2026-07-04 — Session 7

**State:** v0.5.0 committed locally, not yet tagged/pushed (holding for explicit go-ahead). Adds the new standalone `dimension.event` schema — fills the exact gap Treasury's `DimensionUpdatePort` javadoc calls out (D024/D027 business-dimension metering, e.g. PlantPal's plant count).

**Decisions taken this session:**
- `dimension.event.json` mirrors Treasury's `DimensionDelta` record (`appId`, `userId`, `dimensionKey`, `delta`) plus `eventId`/`timestamp` — added ahead of any real adapter so the wire event carries the same idempotent-consumption shape `usage.event` already has (Treasury's `DimensionService` javadoc explicitly flags this as future work: "when a real adapter and event schema land, apply the same ledger-based dedup"). `delta` is a plain `integer` with **no** `minimum` — confirmed `KeyedLongCounter`/`DimensionCounter` both accept negative deltas by design (soft-delete decrements), unlike every other numeric field in the contract set.
- Regenerated all three bindings following the plain-JSON-Schema path (same as `usage.event`, not the OpenAPI path used for `ai.request`): Java via the existing `jsonschema2pojo` `events` execution (added the new source path alongside `usage.event.json`), TS via `json-schema-to-typescript` + `tsc` rebuild of `dist/`, Python via `datamodel-code-generator` (pydantic v2). Verified `mvn compile`, `tsc --noEmit --strict`, and a Python round-trip with a negative `delta` (no validation error, confirming the deliberate lack of constraint).
- Added `tests/validate_dimension_event.py` mirroring `validate_ai_request.py`'s pattern: known-good event, known-good event with negative `delta`, known-bad event missing `dimensionKey`. Full suite (3 files, 10 assertions total, up from 7) passes.
- Explicitly did **not** touch `treasury`, `ai-gateway`, or `plantpal` — building the Treasury Kafka consumer adapter or a PlantPal producer is out of scope for this session per the prompt; noted here for whoever picks up next.

**Next step:** Treasury can now build its inbound adapter (Kafka consumer, per `DimensionUpdatePort`'s javadoc) against the generated `DimensionEvent`/`DimensionEvent` Java binding, with real ledger-based dedup keyed on `eventId` (mirroring `UsageEventLedger`). PlantPal's producer side is a separate future chunk once it needs to emit plant-count changes. Tag and push `v0.5.0` once reviewed.

## 2026-07-04 — Session 8

**State:** v0.5.1 tagged and pushed (patch). Fixed int32 overflow on `runId` in `BuildResult` and `CiRunPayload`, found via a live end-to-end test rejecting a real 11-digit GitHub Actions run ID.

**Decisions taken this session:**
- Added `format: int64` to both `runId` properties (`schemas/ci-runner/build-result.yaml`, `schemas/state-feed/state.event.json`, `schemas/state-feed/state-event-java.yaml`). `jsonschema2pojo` (used for `BuildResult`) ignores OpenAPI's `format: int64`, so also added `existingJavaType: java.lang.Long` to force `Long` there. `openapi-generator` (used for `CiRunPayload`) respects `format: int64` natively — regenerated with `--library resttemplate` to keep Jackson serialization (the default `java` library emits Gson, which would have silently swapped the whole `events` package's serialization framework).
- Added first JUnit 5 test infra to `gen/java` (`junit-jupiter` + `maven-surefire-plugin` in `pom.xml`, `jackson-datatype-jsr310` for `OffsetDateTime` test fixtures) — no Java tests existed in this repo before now. `RunIdOverflowRegressionTest` deserializes an 11-digit `runId` into both `BuildResult` and `CiRunPayload`, catching future narrowing back to `int`.
- Regenerated all three bindings; TS/Python diffs are timestamp-only (neither language overflows at this size), Java diffs are the intended `Integer`→`Long` change plus the same regen-timestamp noise on unrelated `events` classes.

**Next step:** None pending. Consumers currently pinned to `v0.5.0` (none yet, per session 7) should pin `v0.5.1` before building against `BuildResult`/`CiRunPayload` for real workflow runs.

## 2026-07-04 — Session 9

**State:** v0.6.0 tagged and pushed (minor, additive). Wave 4 hub schema delta per owner work order — new `connector` schema group plus optional `origin` on `state.event`.

**Decisions taken this session:**
- New `schemas/connector/` group per spec-connectors.md §2/§5/§6-1: `connector.vocabulary` (a connector's machine-readable verb vocabulary, mirroring `HEXAGON.md` prose) and `connector.invoke.request`/`.response` (the sync orchestrator/sentinel-hub → connector call envelope). Split into three files, one root schema each — matches the `ci-runner`/`control-plane` group convention rather than cramming multiple roots into one file. `refused` is a first-class `status` value on the response (spec-connectors.md's threat model: refusal, not error). `reason`'s "required when status != ok" is documented in the description only, not schema-enforced via `if`/`then` — matches this repo's existing convention for conditionally-present fields (`CiRunPayload.conclusion`) and avoids inconsistent handling across three very different generators.
- Hit a new jsonschema2pojo quirk: with `includeAdditionalProperties=false` (the setting every execution in this repo already uses), a bare `"additionalProperties": true` object schema doesn't fall back to a `Map` — it silently generates an empty, useless POJO. Fixed the same way as v0.5.1's `runId` overflow: added the jsonschema2pojo-specific `existingJavaType: java.util.Map<String, Object>` extension directly to the `params`/`result` schema nodes in the JSON Schema files. TS (`json-schema-to-typescript`) and Python (`datamodel-code-generator`) both mapped the same permissive nodes to the right native type (`{[k: string]: unknown}` / `dict[str, Any]`) with no extension needed — this is a jsonschema2pojo-specific gap, not a general "permissive object" problem.
- Added optional `origin` (`host`/`hub`, D011) to all five `state.event` envelopes in both `state.event.json` and `state-event-java.yaml` — added explicitly to each envelope since `additionalProperties: false` is set per-envelope, not inherited. Regenerated the `events` Java package via the same `openapi-generator` CLI invocation used since v0.1.1/v0.5.1 (`-g java --library resttemplate --additional-properties=useJakartaEe=true --model-package io.platform.contracts.events`) — reconfirmed zero `com.google.gson` imports across `gen/java/src` after regen (the regression flagged in session 8's PROGRESS note).
- Did not touch `ai-gateway` schemas — per owner ruling 2026-07-04 (platform root `PROGRESS.md`, Wave 4 entry), hub callers identify by `appId`, no schema change needed there.
- Regenerated all three bindings; added `ConnectorContractsRoundTripTest` + `StateEventOriginTest` to `gen/java` (full suite: 9 tests green, including `RunIdOverflowRegressionTest`), `tests/validate_connector.py` in Python (full suite: 5 files green). `tsc --noEmit --strict` clean; Python package imports cleanly.

**Next step:** None pending from this session. First connector to build (per spec-connectors.md §7, `connector-gmail` read-only) should declare its vocabulary against the generated `ConnectorVocabulary`/`Verb` binding and speak `ConnectorInvokeRequest`/`ConnectorInvokeResponse` for the orchestrator call; state-feed producers may start tagging `origin: hub` on hub-side events once state-feed itself builds against `v0.6.0`.
