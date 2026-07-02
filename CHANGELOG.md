# Changelog

All contract versions are tracked here. Each contract is versioned independently (semver).

Format: `[contract] vX.Y.Z — YYYY-MM-DD — description`

Breaking changes (removals, renames, new required fields) bump major.
Additive changes (new optional fields) bump minor.
Fixes/clarifications bump patch.

---

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
