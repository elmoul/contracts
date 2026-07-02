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
