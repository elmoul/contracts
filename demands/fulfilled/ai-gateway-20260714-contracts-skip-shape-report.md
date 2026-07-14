---
demandId: ai-gateway-20260714-contracts-skip-shape
worker: contracts
status: done
shipped: ["v0.13.0"]
date: 2026-07-14
---

# Fulfillment report — contracts: `ai.response` shape for a skipped call

`status: done` here is a claim, not a verdict — per `DEMAND_SYSTEM.md` §4,
this report is `contracts`' only output for this demand. `contracts` does not
self-certify and has not notified `ai-gateway` directly; the coordinator
assembles and delivers the summary once the owner approves.

## What shipped

`schemas/ai-gateway/request.yaml`'s `AiResponse` gained exactly the shape the
demand recommended (its own owner-delegated ruling, 2026-07-14) — applied
verbatim, no changes needed:

- New optional field `skipped: boolean` (default `false`). `true` means the
  gateway intentionally omitted the call (Treasury pre-flight returned
  `DOWNSHIFT` for a capability whose `ai.model-manifest`
  `CapabilityDeclaration.downshiftPolicy` is `skip`); absent/`false` is a
  normal completed call.
- `result`, `model`, `provider` moved from required to optional — absent on a
  skipped call (documented per-field, not schema-enforced; see "Not done"
  below).
- `tokensIn`, `tokensOut`, `computedCost` stayed required, valued `0` on a
  skipped call. No `usage.event` is expected on the Kafka side for a skipped
  call.
- Still HTTP 200 — no new status code, no fourth `ai.preflight.response`
  decision, exactly as the demand asked.

**Not done, and deliberate:** JSON Schema conditional-required (`if`/`then`
enforcing "skipped implies result/model/provider absent") was not added.
"Moved to optional" already satisfies the demand's acceptance criterion (both
shapes validate); the "absent when skipped" rule is documented as a
producer-side convention (`ai-gateway` is the only producer) rather than
mechanically enforced. If a future consumer needs it schema-enforced, that's
a follow-up, not part of this demand.

**Versioning:** minor bump, `v0.12.0` → `v0.13.0`, not major — same precedent
as `v0.11.0`'s `summaryRef` required→optional: loosening a `required` array
widens the accepted set (everything valid before stays valid), which is not
one of this repo's own major-bump triggers (removal/rename/new-required-field).

All three bindings regenerated and verified (full detail in `CHANGELOG.md`'s
`v0.13.0` entry — summarizing here):

- **Java:** regenerated `AiResponse.java` (+ `AiRequest.java`,
  `AiRequestMediaInner.java`, `BlockedResponse.java`, all in the same OpenAPI
  document — content-unchanged except `AiResponse`) via the documented direct
  `openapi-generator-cli` invocation. `result`/`model`/`provider` are now
  `@Nullable`/`required = false`/`Include.USE_DEFAULTS` (was `@Nonnull`
  /`required = true`/`Include.ALWAYS`); `skipped` defaults to
  `Boolean.FALSE`. `mvn -B -f gen/java/pom.xml clean test` — `BUILD SUCCESS`,
  `Tests run: 12, Failures: 0, Errors: 0`.
- **TypeScript:** regenerated `ai-gateway-request.ts` via `openapi-typescript`,
  rebuilt `dist/`. `result?`/`model?`/`provider?` now optional; `skipped`
  came out non-optional `boolean` (openapi-typescript's convention for a
  field with a JSON Schema `default` — the default is treated as
  always-filled). `npx tsc --noEmit --strict` clean. Also trued up
  `gen/ts/package-lock.json`'s version fields to `0.13.0` as part of this
  release.
- **Python:** regenerated `platform_contracts/ai_gateway/request.py` via
  `datamodel-codegen --input-file-type openapi`. `result`/`model`/`provider`
  now `str | None = None`; `skipped: bool | None = False`. `tokensIn`/
  `tokensOut`/`computedCost` unchanged (still `Field(...)`, required).

`tests/validate_ai_request.py` (scope widened from `AiRequest`-only to also
cover `AiResponse`): added `GOOD_COMPLETED_RESPONSE` (proves the pre-existing
shape still validates unchanged), `GOOD_SKIPPED_RESPONSE` (result/model/
provider absent, tokens/cost zeroed, `skipped: true`), and
`BAD_RESPONSE_MISSING_TOKENS_IN` (proves `tokensIn` is still genuinely
required — only `result`/`model`/`provider` were loosened). Full
`python tests/run_all.py` — all validators pass, no regression.

## D031 acceptance — post-tag, run for real, all three languages, no unverified leg

`v0.13.0` tagged and pushed. Full clean-install test against the actual
pushed tag, from a fresh scratch location outside this working tree, for
every language:

- **Java:** fresh `git clone --branch v0.13.0`, `mvn -B clean install
  -DskipTests` into a scratch `.m2` — `BUILD SUCCESS`. A second, fully
  independent scratch Maven project depending on `io.platform:contracts:0.13.0`
  compiled and ran code constructing an `AiResponse` two ways — a completed
  call (all six original fields set, `skipped` left at its default `false`)
  and a skipped call (`result`/`model`/`provider` left `null`,
  `tokensIn`/`tokensOut` `0`, `computedCost` `BigDecimal.ZERO`, `skipped`
  `true`) — `BUILD SUCCESS`, both objects printed and inspected; `null`
  fields confirmed absent as expected.
- **Python:** fresh venv, `pip install
  "git+https://github.com/elmoul/contracts.git@v0.13.0#subdirectory=gen/python"`
  — installed cleanly (`pip show` confirms `0.13.0`). Constructed `AiResponse`
  both ways, round-tripped each (`model_dump_json()` → `model_validate_json()`),
  and confirmed a document missing `tokensIn` raises `ValidationError` (1
  error) against the installed package.
- **TypeScript:** `file:`-dependency scratch project pointed at the tagged
  checkout's committed `dist/`, importing `AiGatewayRequestComponents` and
  constructing both response shapes (the skipped one omitting
  `result`/`model`/`provider` entirely) — `npx tsc --noEmit --strict` exit 0.

All scratch clones/venvs/projects deleted after verification.

## What ai-gateway does once its next session picks this up

Per the demand's own "What we do once closed": re-pin to `v0.13.0`, swap
`BrokerService.skippedResponse()` to set `skipped: true` (with
`result`/`model`/`provider` omitted, `tokensIn`/`tokensOut`/`computedCost`
zeroed) instead of the sentinel `model:"skipped"`/`provider:"none"` strings,
update/replace the tests currently asserting on those sentinel values, and
remove the stopgap documentation from `BrokerService`'s javadoc. Not this
repo's session to do — `contracts` doesn't reach into consumer repos.

## D043 release-notification duty

This is the first `contracts` tag cut since the D043 duty went live
(2026-07-13, `platform-vault-20260713-contracts-release-notification-duty`).
Additive release, so per D043 only the origin demand is required (no
fleet-wide "adopt or explain" — that's breaking-release-only): a demand
`to: [ai-gateway]` ("re-pin and adopt v0.13.0") is raised as part of this same
session, standalone coordination commit, per `DEMAND_SYSTEM.md` §3.
