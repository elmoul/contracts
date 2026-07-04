# Changelog

All contract versions are tracked here. Each contract is versioned independently (semver).

Format: `[contract] vX.Y.Z — YYYY-MM-DD — description`

Breaking changes (removals, renames, new required fields) bump major.
Additive changes (new optional fields) bump minor.
Fixes/clarifications bump patch.

---

## v0.4.0 — 2026-07-04

Minor release: adds an optional `media` field to `ai.request`'s `AiRequest` schema
so photo-based (and other multimodal) calls can route through `ai-gateway` on the
same envelope. Purely additive — no existing required field touched, `AiResponse`
and `BlockedResponse` are untouched (response stays text-only).

### schemas/ai-gateway/request.yaml (AiRequest — additive)
- Driven by PlantPal's chunk 1 (parallel to its own clone/scaffold chunk, no
  dependency between them): all four of PlantPal's AI-calling modules
  (identification, treatment, species enrichment, chat) need to send a photo
  alongside — or instead of — a text prompt. gateway-spec §8-3 had already leaned
  toward "same envelope, optional media field" over a second endpoint; this
  release finalizes that ruling. PlantNet (and any future vision-capable
  provider) rides the existing `AiRequest`/`ai.request` contract — there is no
  separate `ai.vision.request`.
- Added `media`: optional array of `{ data, mimeType }` objects. `data` is
  base64-encoded content (`format: byte`), `mimeType` is a free-form string
  (examples `image/jpeg`, `image/png` — not an enum, so the gateway doesn't need
  a schema bump every time a provider adds a supported format). Both fields
  required *within* a media item (`additionalProperties: false` on the item, as
  on every other object in this contract) — but the `media` array itself is not
  in `AiRequest`'s top-level `required` list, so text-only callers are unaffected.
  The gateway is expected to pass `media` through untouched to providers that
  support vision input, and to ignore it for providers that don't.
- Deliberately did not touch `AiResponse`/`BlockedResponse` — a vision call's
  result is still just text (the identification, the treatment advice, etc.), so
  the response envelope doesn't need a media-shaped counterpart.

### Codegen
- **Java:** regenerated `AiRequest.java` via openapi-generator 7.23.0
  (`JavaClientCodegen`, `resttemplate` library, `useJakartaEe=true`, scoped to
  models only via `--global-property models,supportingFiles=false,apiTests=false,
  modelTests=false,apiDocs=false,modelDocs=false`, `--model-package
  io.platform.contracts.aigateway`) directly against `request.yaml` — this is
  the same invocation shape `AiRequest.java`'s existing generator header already
  implied (JavaClientCodegen, not jsonschema2pojo like the other Java targets;
  `ai.request` is an OpenAPI document, not a plain JSON Schema, so it never went
  through the `jsonschema2pojo-maven-plugin` executions in `pom.xml`). Produced a
  new `AiRequestMediaInner.java` (the array item type) alongside the additive
  diff to `AiRequest.java` — `AiResponse.java`/`BlockedResponse.java` regenerated
  byte-identical (confirmed via diff) since their schemas didn't change.
  Verified with `mvn compile` — clean.
- **TypeScript:** regenerated `ai-gateway-request.ts` via `openapi-typescript`
  (matching the file's own header — it was never `json-schema-to-typescript`
  output like the plain-JSON-Schema control-plane files, since `request.yaml` is
  a full OpenAPI document with `paths`+`components`). Rebuilt `gen/ts/dist/`
  fresh via `npx tsc` per D031 (committed, not gitignored) — picked up the
  14-line additive diff to `dist/ai-gateway-request.d.ts` plus line-ending
  normalization on a few unrelated `dist/` files untouched in content. Verified
  with `tsc --noEmit --strict` — clean.
- **Python:** regenerated `platform_contracts/ai_gateway/request.py` via
  `datamodel-code-generator` (pydantic v2, `--input-file-type openapi`, no
  `--field-constraints` flag — matching the existing file's `constr`/`conint`/
  `confloat`-style constraints rather than inline `Field(ge=...)`). Produced a
  new `MediaItem` model (base64 content typed as pydantic's `Base64Str`).
  Verified: a payload with `media` round-trips (`model_dump_json` →
  `model_validate_json`), a payload without `media` still validates (proves the
  field is truly optional, not accidentally required), and a media item missing
  `mimeType` raises `ValidationError` (rejected by `extra='forbid'` +
  `mimeType`'s required-ness).

### Tests
- Added `tests/validate_ai_request.py` — first structured test for `ai-gateway`
  (previously verified only by compiling/typechecking the generated bindings, same
  gap `validate_control_plane.py` closed for control-plane in v0.3.0). Pulls
  `AiRequest` out of `request.yaml`'s `components.schemas` (it's an OpenAPI
  document, not a standalone JSON Schema file) and validates it directly against:
  a known-good request with `media` (plausible base64 JPEG stub), a known-good
  request without `media` (proves optionality), and a known-bad request whose
  media item is missing `mimeType` (must be rejected).

## v0.3.0 — 2026-07-03

Minor release: fleshes out the two control-plane STUB schemas per the owner-approved
design. Purely additive — verified first that nothing consumes them yet (control-plane
chunk 1 deliberately used its own `RegistryEntry` record instead of these stubs, and
has no `contracts` dependency at all).

### schemas/control-plane/hexagon.descriptor.json (STUB → full schema)
- Validates the YAML frontmatter block every repo carries at the top of its
  `HEXAGON.md`. Fields: `functionalName`, `kind` (runtime/app/buildtime), `side`
  (host/hub/ui/shared), `status` (planned/building/active/deprecated), `class`
  (optional, D010 risk tier, meaningful only for `kind: app`), `spec`, `decisions`,
  `deps` (required, may be empty), `infra`, and an optional nested `contracts` object
  (`pin`, `binding`, `used` — per-contract, not per-repo, since the D015 rebuild set is
  computed per contract).
- **`side` enum fix:** the stub's enum (`host`/`hub`/`shared`) was wrong — added `ui`,
  which spec-conventions officially recognizes as the side whose repos the theme-check
  skips (dashboard is `side: ui`).
- Deliberately **no `version` field** — hand-edited versions in frontmatter go stale;
  changing state lives in `registry.entry`, sourced from git/CI.
- Deliberately **no `consumedBy`** (derived by control-plane by inverting `deps` across
  the fleet) and **no `ports`** (deferred — `deps` + `contracts.used` are the machine
  projection of the port tables; prose keeps the rest). Both omissions noted in the
  schema description so they aren't "helpfully" re-added later.

### schemas/control-plane/registry.entry.json (STUB → full schema)
- Control plane's served record — a descriptor summary plus changing state:
  `functionalName`, `kind`, `side`, `status` (adds `suspended`, a registry-only action,
  not a repo property), `repoUrl`, `version` (git tag, or `version+shortsha` — the
  convention control-plane's static registry file already established), `contractsPin`,
  `updatedAt`, and app-only `appId`/`class`/`plan` (populated once `app.manifest`
  registration arrives; `class`/`plan` enums aligned with `app.manifest`'s).

### Codegen
- **Java:** new `jsonschema2pojo` execution (`control-plane`, plain object schemas,
  package `io.platform.contracts.controlplane`) generating `HexagonDescriptor`,
  `RegistryEntry`, and the nested `Contracts` type. Verified with `mvn compile`.
- **TypeScript:** generated `hexagon-descriptor.ts` / `registry-entry.ts` via
  json-schema-to-typescript, re-exported from `index.ts`. `gen/ts/dist/` rebuilt fresh
  per D031. Verified with `tsc --noEmit --strict`.
- **Python:** generated `platform_contracts/control_plane/{hexagon_descriptor,
  registry_entry}.py` via datamodel-code-generator (pydantic v2), wired into the
  package `__init__.py`. Verified with a model round-trip and a rejected known-bad
  document.

### Tests
- Added `tests/validate_control_plane.py` — no test framework existed in this repo
  before this release (prior sessions verified only by compiling/typechecking the
  generated bindings). This validates the JSON Schemas themselves against example
  documents: a known-good `hexagon.descriptor` (treasury's real values — `kind:
  runtime`, `side: host`, `deps: [contracts, state-feed]`, `contracts.pin: v0.2.2`,
  `binding: java`, `used: [ai.preflight, usage.event, state.event]`) and a known-bad
  one (`side: invalid`, missing `functionalName`), plus the equivalent pair for
  `registry.entry`.

## v0.2.2 — 2026-07-02

Patch release fixing a consumption-mechanism defect found while re-verifying D031 in
practice. No schema changes.

### gen/ts (D031 amended — git-URL mechanism doesn't work, switch to `file:` + committed `dist/`)
- The v0.2.1 fix assumed a git-URL dependency (`npm install github:...`) would run the
  `prepare` lifecycle script to build `dist/` at install time. Verified against a real
  install and it does not hold up: stock npm requires `package.json` at the *repo root*
  to resolve a git dependency at all — there is no subdirectory syntax for pointing a
  git dep at `gen/ts/`. The mechanism in v0.2.1 could never have worked for a consumer.
- Fixed per amended **D031**: consumers depend on `contracts` via
  `"@platform/contracts": "file:<path-to-checkout>/gen/ts"` instead of a git URL.
  `gen/ts/dist/` is now committed (removed from `.gitignore`) and regenerated fresh as
  part of each release, so consumers never depend on a `prepare`/lifecycle script
  firing correctly at install time. Removed the now-unnecessary (and actively harmful)
  `"prepare": "tsc"` script — confirmed by reproduction that npm still invokes
  `prepare` on a `file:` install, and it fails there too (no `devDependencies` present
  in a linked/packed install), which would have broken every consumer. `"build": "tsc"`
  remains as a manual step for regenerating `dist/` before a release. `types` now
  points at `dist/index.d.ts` (was `index.ts`) to match the committed-output model.
- Verified end-to-end: built `dist/` fresh (`npx tsc`), then in a scratch directory
  outside this repo created a throwaway `package.json` with
  `"@platform/contracts": "file:C:/Users/moulo/Desktop/platform/contracts/gen/ts"`,
  ran `npm install`, confirmed `require('@platform/contracts')` resolves, and
  confirmed a `.ts` file importing `BuildCommand`/`BuildResult`/`UsageEvent` type-checks
  clean under `tsc --noEmit --strict`. First attempt (with `prepare: tsc` still present)
  reproduced the exact install-time failure this fix addresses; removing `prepare` and
  relying on the committed `dist/` resolved it.

## v0.2.1 — 2026-07-02

Patch release closing two gaps found in the v0.2.0 review. No schema changes.

### gen/java, gen/ts, gen/python (codegen gap fix)
- `build-command.yaml` (`BuildCommand`) and `build-result.yaml` (`BuildResult`) shipped
  as schemas in v0.2.0 but were never actually run through codegen — no generated type
  existed in any of the three language bindings. Fixed:
  - **Java:** added a second `jsonschema2pojo-maven-plugin` execution (`ci-runner`,
    `sourceType=yamlschema`) targeting `io.platform.contracts.cirunner` — `BuildCommand`
    and `BuildResult` are plain object schemas (no `oneOf`), so unlike `state.event.json`
    they don't need the openapi-generator union workaround.
  - **TypeScript:** generated `build-command.ts` / `build-result.ts` via
    json-schema-to-typescript, re-exported from `index.ts`.
  - **Python:** generated `platform_contracts/ci_runner/{build_command,build_result}.py`
    via datamodel-code-generator (pydantic v2), wired into the package `__init__.py`.
  - Verified: `mvn compile`, `tsc --noEmit --strict`, and a Python round-trip
    (`model_dump_json`) all pass clean on the new types.

### gen/ts (D031 follow-through — git-tag consumption)
- Per new decision **D031** (`contracts` is consumed via GitHub-tag pinning, no package
  registry), `gen/ts/package.json` had `main: dist/index.js` but no build step npm runs
  automatically on `npm install github:...` — only a manual `build` script, which a
  git-installed dependency never triggers. Consumers pinning via tag would get a 404 on
  `dist/index.js`.
- Fixed: added a `tsconfig.json` (was missing entirely — bare `tsc` with no config and
  no file args does nothing, so this was a second, compounding gap) and a `"prepare":
  "tsc"` script — `prepare` is the npm lifecycle hook that runs on `npm install
  github:...`. `dist/` is generated at install time and gitignored, not committed.
- Verified end-to-end: `npm install github:elmoul/contracts#v0.2.1` into a scratch
  project builds `dist/index.js` and the package is importable.

## v0.2.0 — 2026-07-02

Two changes landed on `main` directly from other repos' sessions reaching across the
repo boundary mid-debug (a process gap now closed — see root `CLAUDE.md`). Reviewed
here and folded into a proper tagged release rather than reverted, since the content
was mostly right.

### gen/java (tag-integrity fix)
- `jakarta.annotation-api` was added to `pom.xml` (commit `8bf51ba`) after the `v0.1.1`
  tag was already cut, with no version bump. The dependency itself is correct —
  openapi-generator's `resttemplate` library (with `useJakartaEe=true`) emits
  `@jakarta.annotation.Nonnull`/`@Nullable` on every generated field, and the artifact
  was missing from the classpath. But because it landed post-tag, `git checkout v0.1.1`
  today produces a `pom.xml` that does not compile — the tag lies about its own
  content. This alone would justify a patch release.

### ci-runner control-plane contracts (additive)
- Added `build-command.yaml` (`BuildCommand`) and `build-result.yaml` (`BuildResult`):
  the control-plane → ci-runner async build-dispatch contracts (correlationId echo
  pattern for correlating the async `BuildResult` back to its `BuildCommand`).
  Reviewed — sound, no conflicts with existing contracts.

### state.event / CiRunPayload (breaking)
- `schemas/ci-runner/ci-run.payload.json` shipped as a second, disconnected
  definition of the `ci.run` state-event payload, conflicting with the `CiRunPayload`
  already wired into `state.event.json`'s `oneOf`. It described real GitHub
  `workflow_job` lifecycle granularity (phase/conclusion/runnerLabels, per-job) —
  more accurate than the original `CiRunPayload`, which was a guess written before
  `ci-runner` existed — but as a second file it broke the "one `oneOf`, one source of
  truth" rule, and even used a different discriminator spelling (`ci-run`) than
  `state.event.json` (`ci.run`), which ci-runner's own `PROGRESS.md` flagged as an
  unresolved TODO.
- Fixed by deleting the orphaned file and revising `CiRunPayload` in
  `state.event.json` in place to the richer, ci-runner-shaped fields: `runId`
  (string → integer), `repo`, `ref`, `workflow`, `jobName`, `phase`
  (queued/in_progress/completed), `conclusion?`, `startedAt?`, `completedAt?`,
  `runnerLabels`. Removed: `repoName`, `status` (running/success/failed), `branch`,
  `durationMs`. `state.event.json`'s `oneOf` is once again the only source of truth
  for state-feed payloads.
- Discriminator: kept `ci.run` (dot) as canonical — consistent with every other event
  (`component.health`, `cost.tick`, `app.status`). ci-runner's local `ci-run` TS types
  are the side that needs to conform.
- Also updated `schemas/state-feed/state-event-java.yaml` (the openapi-generator
  wrapper used only to drive the Java binding) to match, and regenerated all three
  language bindings for `state.event` (Java via openapi-generator 7.23.0 +
  `useJakartaEe=true`, TypeScript via json-schema-to-typescript, Python via
  datamodel-code-generator 0.66.3). Verified: `mvn compile`, `tsc --noEmit --strict`,
  and a Python round-trip (`model_dump_json` → `model_validate`) all pass clean.

**Versioning:** bumped minor (0.1.1 → 0.2.0), not patch, not major. The repo's own
stated rule (breaking = major bump) is the 1.0+ rule; while a package sits at
`0.y.z`, standard semver treats that line as initial development, where breaking
changes conventionally move the minor digit and major stays `0` until a `1.0.0`
stability declaration. No hexagon has actually pinned or built against a `contracts`
version yet — `control-plane`, `ci-runner`, and `ai-gateway` are all still in
spec-only or early-build phase — so the original `CiRunPayload` guess was never
consumed in anger. Reserving a major bump for when a real breaking change would
ripple through running consumer code, not a schema nobody has built against yet.

## v0.1.1 — 2026-07-02

### state.event (patch — schema shape fix, wire format unchanged)
- Restructured oneOf from dual-declaration to self-contained branches: removed top-level
  `type`/`timestamp` properties and `required` block; each variant (ComponentHealthEvent,
  LoadEvent, CostTickEvent, CiRunEvent, AppStatusEvent) now declares all three fields
  (type, timestamp, payload) in its own required block.
- Extracted inline payload objects to named definitions (ComponentHealthPayload, LoadPayload,
  CostTickPayload, CiRunPayload, AppStatusPayload) with explicit titles.
- Switched `$defs` → `definitions` keyword so jsonschema2pojo can resolve $refs.
- Codegen fix (all three targets): Java now emits per-variant classes with typed payload
  fields and Jackson annotations (openapi-generator + resttemplate library); Python emits
  Literal-typed, non-erased RootModel union; TypeScript files re-saved as UTF-8.
- Also fixed all Java (app, ai-gateway) classes: were using Gson due to okhttp-gson default
  library; regenerated with resttemplate/Jackson for Spring compatibility.

### app.manifest (patch)
- `class` field enum corrected to D010 risk tiers [low-stakes, health-class, kids-class].
  (Was wrongly [app, connector, agent] in v0.1.0.)

### ai.request (patch)
- Added `BlockedResponse` schema with required `reason` field; wired to 402 response per D023.

## Unreleased

### usage.event
- Initial schema: appId, userId, provider, model, tokensIn, tokensOut, computedCost, timestamp.

### ai.request / ai.response
- Initial schema: unified AI call shape through ai-gateway.

### ai.preflight.request / ai.preflight.response
- Initial schema: gateway ↔ Treasury synchronous authorization (allow / downshift / block).

### app.manifest
- Initial schema: app registration payload (name, version, routes, owner, plan, class).

### app.health
- Initial schema: health response shape.

### state.event
- Initial schema: SSE event envelope for the state feed.
