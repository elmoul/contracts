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

## 2026-07-04 — Session 6

**State:** v0.4.0 tagged and pushed (minor, additive). PlantPal integration chunk 1 — extended `ai.request` for photo-based/multimodal calls, run in parallel with PlantPal's own chunk 0 clone (no dependency between them).

**Decisions taken this session:**
- Added optional `media` field to `AiRequest` (array of `{data, mimeType}`) per gateway-spec §8-3's existing lean toward "same envelope, optional field" over a separate vision endpoint — PlantNet (and any future vision provider) rides `ai.request`, full stop. `AiResponse`/`BlockedResponse` untouched — responses stay text-only.
- Confirmed `AiRequest.java`'s generator header (`JavaClientCodegen`) meant it was never on the `jsonschema2pojo` path the rest of `gen/java/pom.xml` uses — it's generated straight from `request.yaml` (an OpenAPI doc, not a plain JSON Schema) via `openapi-generator-cli generate -g java --library resttemplate --additional-properties=useJakartaEe=true --model-package io.platform.contracts.aigateway --global-property models,supportingFiles=false,apiTests=false,modelTests=false,apiDocs=false,modelDocs=false`. Reconstructed and reused this exact invocation (verified byte-for-byte match on the unchanged `AiResponse`/`BlockedResponse` output before trusting it).
- Same story for TS (`openapi-typescript`, not `json-schema-to-typescript` — that tool is only for the plain-JSON-Schema targets like control-plane) and Python (`datamodel-code-generator` **without** `--field-constraints`, since that flag inverts to `Field(ge=...)` inline style — the existing file uses `conint`/`confloat`/`constr`, which is the *default*, unflagged behavior).
- Regenerated all three bindings; verified `mvn compile`, `tsc --noEmit --strict` (after `npm install` in `gen/ts` — no `node_modules` existed locally), and a Python round-trip with media, without media (proves optionality), and a rejected missing-`mimeType` case.
- Added `tests/validate_ai_request.py` — first structured test for `ai-gateway` (same gap `validate_control_plane.py` closed for control-plane in v0.3.0). Pulls `AiRequest` out of `request.yaml`'s `components.schemas` via PyYAML since the source is an OpenAPI document, not a standalone schema file.

**Next step:** PlantPal chunk 0 (clone/scaffold) proceeds independently. Once PlantPal starts consuming `contracts`, it pins `v0.4.0` and builds its four AI-calling modules (identification, treatment, species enrichment, chat) against the generated `AiRequest` with `media` populated for photo calls, omitted for text-only ones. `ai-gateway`'s own build still needs to actually read/forward `media` to a vision-capable provider (PlantNet) — that's gateway-side work, not a contracts change.
