# Progress

## 2026-07-02 — Session 1

**State:** v0.1.0 tagged and pushed. Repo bootstrapped; all phase A–D schemas authored and committed; three codegen targets (Java/openapi-generator+jsonschema2pojo, TS/openapi-typescript+json-schema-to-typescript, Python/datamodel-code-generator) generated and committed into gen/.

**Decisions taken this session:**
- schemas/ organised by catalog section (app/, ai-gateway/, state-feed/, control-plane/) — owner to record in vault if promoted to decision.
- app.health uses Spring Actuator shape (status: UP/DOWN/OUT_OF_SERVICE/UNKNOWN) — confirmed by architect.
- AppManifest.class corrected to D010 risk tiers [low-stakes, health-class, kids-class].
- BlockedResponse added to 402 on /ai/request per D023.

**Next step:** First consuming hexagon can now pin `io.platform:contracts:0.1.0` / `@platform/contracts@0.1.0` / `platform-contracts==0.1.0`. When control-plane or ai-gateway starts schema work, reference the stubs in schemas/control-plane/ and schemas/ai-gateway/ respectively. Codegen CI automation tracked in ci-runner spec §8.
