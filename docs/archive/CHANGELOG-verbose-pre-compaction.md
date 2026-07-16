# contracts — verbose CHANGELOG (pre-compaction snapshot, 2026-07-16)

> Verbatim copy of `CHANGELOG.md` as it stood before the 2026-07-16 docs
> compaction pass (process-narration trim). This is the full, unabridged
> version — every command transcript, verification run, and toolchain note
> that the slimmed `CHANGELOG.md` cut for brevity is preserved here. Full
> history also in git log.

# Changelog

All releases are tracked here. In practice this repo is versioned **repo-wide,
per language binding** — one version number per release, bumped together
across `gen/java/pom.xml`, `gen/ts/package.json`, and `gen/python/pyproject.toml`
for whichever of the three languages' generated output actually changed (see
e.g. v0.6.1, a Java-only patch that left the TS/Python version files
untouched). It is not independent per-contract semver as originally intended —
no tooling here computes or enforces a separate version per schema.

Format: `## vX.Y.Z — YYYY-MM-DD`, followed by which contract(s) changed and why.

Breaking changes (removals, renames, new required fields) bump major.
Additive changes (new optional fields) bump minor.
Fixes/clarifications bump patch.

---

## v0.13.0 — 2026-07-14

Additive release, all three bindings: fulfills `ai-gateway`'s demand
(`demands/fulfilled/ai-gateway-20260714-contracts-skip-shape-report.md`,
`ai-gateway-20260714-contracts-skip-shape`) — a shape for "call intentionally
omitted" on `ai.response`.

### schemas/ai-gateway/request.yaml — `AiResponse` (additive)

`ai-gateway`'s `BrokerService.skippedResponse()` was overloading the completed-
call shape with sentinel values (`model:"skipped"`, `provider:"none"`, zero
tokens/cost) whenever Treasury's pre-flight returned `DOWNSHIFT` for a
capability whose `ai.model-manifest` `CapabilityDeclaration.downshiftPolicy`
is `skip` (v0.9.0+) — a documented stopgap, not a `contracts`-sanctioned shape.
Applied the demand's own recommended shape verbatim (its owner-delegated
ruling, 2026-07-14):

- **New optional field `skipped: boolean` (default `false`).** `true` means
  the gateway intentionally omitted the call; absent/`false` is a normal
  completed call — an existing consumer that never reads this field sees no
  behavior change.
- **`result`, `model`, `provider` moved from required to optional** — absent
  when `skipped` is `true` (documented in each field's description, not
  schema-enforced — see below). `tokensIn`, `tokensOut`, `computedCost` stay
  required, valued `0` on a skipped call; no `usage.event` is expected on the
  Kafka side for a skipped call (no work was actually metered).
- Still a 200 response — no new status code, no fourth `ai.preflight.response`
  decision, per the demand's explicit rationale.

**Not done: JSON Schema conditional-required (`if: {skipped: true} then:
{not required: [result, ...]}`) to mechanically enforce "skipped implies
result/model/provider absent."** Judged not worth the added schema complexity
for what is fundamentally a producer-side convention (`ai-gateway` is the only
producer); "moved to optional" already lets both shapes validate, which is
the acceptance criterion the demand actually asked for. A future session can
add the conditional if a consumer needs it schema-enforced rather than
documented.

**Versioning:** minor bump (0.12.0 → 0.13.0), not major. Same precedent as
`v0.11.0`'s `summaryRef` required→optional: loosening a `required` array is a
backward-compatible widening of the accepted set (every document that was
valid before is still valid), unlike a removal/rename/new-required-field. The
CHANGELOG's own major-bump criteria ("new required fields") isn't triggered
here — `skipped` is optional and `result`/`model`/`provider` became *less*
constrained, not more.

### Codegen — all three regenerated from the one schema change

- **Java:** regenerated `AiResponse.java`, `AiRequest.java`,
  `AiRequestMediaInner.java`, `BlockedResponse.java` via the documented direct
  `openapi-generator-cli` invocation (`--library resttemplate`, `-i
  schemas/ai-gateway/request.yaml -g java ... -o gen/java`) — same command
  `DEPLOYMENT.md` already prescribes for this OpenAPI document.
  `result`/`model`/`provider` are now `@jakarta.annotation.Nullable` with
  `required = false` / `JsonInclude.Include.USE_DEFAULTS` (was `@Nonnull`
  /`required = true`/`Include.ALWAYS`); new `skipped` field defaults to
  `Boolean.FALSE`. `PreflightRequest`/`PreflightResponse` (a separate schema
  file) untouched. `mvn -B -f gen/java/pom.xml clean test` —
  `BUILD SUCCESS`, `Tests run: 12, Failures: 0, Errors: 0` (no existing test
  touches `AiResponse`, so this is a compile-correctness check, not a
  behavior regression check — covered instead by the new
  `tests/validate_ai_request.py` assertions, schema-level).
- **TypeScript:** regenerated `ai-gateway-request.ts` via `openapi-typescript`,
  rebuilt `dist/` (D031 — committed, not gitignored). `result`/`model`/
  `provider` are now `?:` (optional); `skipped` came out as non-optional
  `boolean` (not `skipped?:`) — `openapi-typescript` treats a field carrying a
  JSON Schema `default` as always-present in the type (the default fills it
  in), which is its documented convention elsewhere in this repo too, not a
  regression. `npx tsc --noEmit --strict` clean. Also trued up
  `gen/ts/package-lock.json`'s version fields (0.12.0 → 0.13.0, via `npm
  install --package-lock-only`) as part of this release rather than leaving it
  for a later hygiene pass (the leftover flagged since v0.10.0 was already
  closed in the 2026-07-14 hygiene session; this keeps it current going
  forward). `npm ci` clean, 0 vulnerabilities.
- **Python:** regenerated `platform_contracts/ai_gateway/request.py` via
  `datamodel-codegen --input-file-type openapi` (no enum in this schema, so
  the `--use-specialized-enum`/`--target-python-version` flags don't apply
  here). `result: str | None`, `model: str | None`, `provider: str | None`
  (all default `None`); `skipped: bool | None` default `False`. `tokensIn`/
  `tokensOut`/`computedCost` unchanged (still required, `Field(...)`).

### tests/validate_ai_request.py

Renamed in scope (was `AiRequest`-only, now also covers `AiResponse`). Added
`GOOD_COMPLETED_RESPONSE` (result/model/provider present, `skipped` absent —
proves the pre-existing completed-call shape still validates unchanged),
`GOOD_SKIPPED_RESPONSE` (result/model/provider absent, tokens/cost zeroed,
`skipped: true`), and `BAD_RESPONSE_MISSING_TOKENS_IN` (proves `tokensIn` is
still genuinely required — the loosening only touched `result`/`model`/
`provider`). Deliberately does *not* assert `skipped: true` + `result` present
as invalid — that combination is schema-legal by design (see the "not done"
note above); asserting it invalid would test a constraint the schema doesn't
actually enforce.

### D031 acceptance — post-tag, run for real, all three languages

`v0.13.0` tagged and pushed; **post-tag D031 acceptance test run for real
against the pushed tag, all three languages, no unverified leg:**

- **Java:** fresh `git clone --branch v0.13.0` (independent of this working
  tree), `mvn -B clean install -DskipTests` into a scratch `.m2` —
  `BUILD SUCCESS`, installed `io.platform:contracts:0.13.0`. A second, fully
  independent scratch Maven project depending on that coordinate compiled and
  ran code constructing an `AiResponse` two ways — a completed call (all six
  original fields set, `skipped` left null) and a skipped call
  (`result`/`model`/`provider` left null, `tokensIn`/`tokensOut` `0`,
  `computedCost` `BigDecimal.ZERO`, `skipped` `true`) — `BUILD SUCCESS`, both
  objects printed and inspected.
- **Python:** fresh venv, `pip install
  "git+https://github.com/elmoul/contracts.git@v0.13.0#subdirectory=gen/python"`
  — installed cleanly; constructed `AiResponse` both ways (completed and
  skipped), round-tripped each (`model_dump_json()` →
  `model_validate_json()`), and confirmed a document missing `tokensIn`
  raises `ValidationError` against the installed package.
- **TypeScript:** `file:`-dependency scratch project pointed at the tagged
  checkout's committed `dist/`, importing `AiGatewayRequestComponents` and
  constructing both response shapes; `tsc --noEmit --strict` clean. All
  scratch clones/venvs/projects deleted after verification.

### Toolchain reality

Local Maven 3.9.16 + JDK 21, Node/npm, and the pre-provisioned `.venv` with
`datamodel-code-generator` 0.68.1 all available this session — no unverified
leg, same as sessions 19–22.

## v0.12.0 — 2026-07-13

Breaking release, all three bindings: fulfills `conventions`' demand
(`demands/fulfilled/conventions-20260713-descriptor-used-contracts-pattern-report.md`,
`conventions-20260713-descriptor-used-contracts-pattern`) to pattern-constrain
`hexagon.descriptor.json`'s `contracts.used` array items with a machine-readable
contract-id shape.

### schemas/control-plane/hexagon.descriptor.json (breaking)

- **`contracts.used` items: `{type: string}` → `{type: string, pattern:
  "^[a-z][a-z0-9]*([.-][a-z0-9]+)*$"}`.** A 2026-07-13 platform registry audit
  found real free-text entries in the fleet (`sentinel-hub`: `"ai.request /
  ai.response / ai.blocked"`; `publishing`: `"ai.preflight (blocked-response
  shape only, via ai-gateway's 402)"`; others shaped like `"state.event
  (activity.count)"`), which make the field's own stated purpose — the D015
  rebuild set ("who consumes contract X") — mechanically unanswerable. The
  pattern is the schema-side half of `conventions`' repo-side
  `used-contracts-format` validator rule; the two are intentionally redundant
  (the validator catches repos on an older contracts pin or repos `conventions`
  never runs against; the schema catches every consumer, in every binding,
  independent of whether the validator runs).
- Verified the pattern accepts every real contract id in fleet use today
  (`state.event`, `ai.preflight.request`, `build-command`, `registry.entry`,
  `usage.event`, `state.event.activity.count`) and rejects all three audited
  free-text forms above — see the new `GOOD_USED_CONTRACT_IDS` /
  `BAD_USED_CONTRACT_IDS` cases in `tests/validate_control_plane.py`.

**Owner ruling (recorded per the demand's acceptance criteria):** breaking, not
additive. `sentinel-hub`'s and `publishing`'s existing non-conforming
descriptors will fail validation against this schema — accepted, since the
field is meaningless as a machine-readable rebuild-set input otherwise. Those
two repos' `HEXAGON.md` frontmatter needs a follow-up fix once they re-pin;
out of scope here (`contracts` doesn't reach into consumer repos).

**Versioning:** bumped minor (0.11.0 → 0.12.0), not the major digit — this
repo's own precedent (see v0.2.0 below) reserves an actual major-version bump
for a `1.0.0` stability declaration, which is a separate decision from
classifying a given change as breaking while the package sits at `0.y.z`. This
release *is* the scenario that precedent flagged as the real trigger for that
future 1.0 conversation (unlike v0.2.0's, this one has real fleet documents —
not yet running code — that will fail validation), but declaring platform-wide
`contracts` stability is a bigger decision than this demand asked for and is
left to an explicit owner call, not inferred here.

### Codegen — all three regenerated from the one schema change

- **Java:** `mvn -B -f gen/java/pom.xml clean test` — `Contracts.java`
  regenerated via the existing `control-plane` jsonschema2pojo execution (no
  config changes needed). Confirmed (again — same as `functionalName`'s and
  `decisions`' existing `pattern` constraints) that jsonschema2pojo 1.2.1 does
  not emit a `@Pattern` annotation for this field even with
  `useJakartaValidation=true`; the updated description is the only visible
  diff in the generated class. No runtime enforcement change on the Java side.
- **TypeScript:** regenerated `hexagon-descriptor.ts` via
  `json-schema-to-typescript`, rebuilt `dist/` (D031 — committed, not
  gitignored). `used: string[]` is unchanged type-wise — the tool doesn't
  encode `pattern` into the type system, same as `functionalName`. Verified
  with `tsc --noEmit --strict`.
- **Python:** regenerated `platform_contracts/control_plane/hexagon_descriptor.py`
  via `datamodel-codegen` (`--target-python-version 3.11
  --use-specialized-enum`, matching this repo's `StrEnum` convention).
  `Contracts.used` is now `list[constr(pattern=r'^[a-z][a-z0-9]*([.-][a-z0-9]+)*$')]`
  — Python is the one binding that actually enforces the constraint at
  parse/construction time, consistent with how `functionalName`/`decisions`
  already behave. Verified with a `model_dump_json()` → `model_validate_json()`
  round-trip and a rejected known-bad `used` entry.

### tests/validate_control_plane.py

Added `GOOD_USED_CONTRACT_IDS` (the six real ids from the demand's acceptance
criteria) and `BAD_USED_CONTRACT_IDS` (the three audited free-text forms),
each exercised against `hexagon.descriptor.json` via the existing
`expect_valid`/`expect_invalid` helpers.

### D031 acceptance — post-tag, run for real, all three languages

`v0.12.0` tagged and pushed; **post-tag D031 acceptance test run for real
against the pushed tag, all three languages, no unverified leg:**

- **Java:** fresh `git clone --branch v0.12.0` (independent of this working
  tree), `mvn -B clean install -DskipTests` into a scratch `.m2` —
  `BUILD SUCCESS`, installed `io.platform:contracts:0.12.0`. A second, fully
  independent scratch Maven project depending on that coordinate compiled and
  ran code constructing a `Contracts` with `used: ["ai.preflight.request",
  "state.event"]` — `BUILD SUCCESS`, printed object confirms the value.
- **Python:** fresh venv, `pip install
  "git+https://github.com/elmoul/contracts.git@v0.12.0#subdirectory=gen/python"`
  — installed cleanly; constructed a `HexagonDescriptor`, round-tripped
  (`model_dump_json()` → `model_validate_json()`), and confirmed the new
  `contracts.used` pattern rejects a free-text entry (`ValidationError`
  raised for `"ai.request / ai.response / ai.blocked"`).
- **TypeScript:** `file:`-dependency scratch project pointed at the tagged
  checkout's `gen/ts` (its committed `dist/` per D031), `npx tsc --noEmit
  --strict` clean against a `HexagonDescriptor` literal with a real
  `contracts.used` array.

## v0.11.0 — 2026-07-11

Minor release, all three bindings: reconciles
`schemas/demand-coordinator/demand.fulfillment.json` with
`DEMAND_SYSTEM.md` §5 and real fleet usage, fulfilling `demand-coordinator`'s
demand
(`demands/fulfilled/demand-coordinator-20260710-contracts-fulfillment-envelope-drift-report.md`,
`demand-coordinator-20260710-contracts-fulfillment-envelope-drift`).

### schemas/demand-coordinator/demand.fulfillment.json (additive)

Owner ruling (recorded in the demand, resolve via schema, not fleet
migration): the schema was out of step with both the doc and reality, not the
other way around. Across the 12 real fulfillment reports in the fleet today,
0 set `summaryRef` (required until now), 7 set `date`, most set `shipped` —
`DEMAND_SYSTEM.md` §5 documents `shipped`/`date` as the convention and never
mentions `summaryRef` at all.

- **`summaryRef` required → optional.** A report file's own path
  conventionally already is the summary.
- **New optional `shipped`** (`array` of `string`) — tags, versions, or
  branch@commit refs, matching what the fleet already writes (free-text
  entries like `"v0.10.0"` or `"demand/observability-telemetry-schema@9eb777c"`).
- **New optional `date`** (`string`, `format: date`) — the report's write
  date.
- `additionalProperties: false` unchanged — additive structure, not a
  loosening of the schema's shape discipline, per the demand's acceptance
  criteria.
- `required` is now just `["demandId", "worker", "status"]`.

### tests/validate_demand.py

Added `GOOD_FULFILLMENT_SHIPPED_DATE_NO_SUMMARY_REF` (exercises `shipped`/
`date` with no `summaryRef` at all) and dropped the now-stale "missing
summaryRef" half of `BAD_FULFILLMENT`'s failure reason — that document is
invalid solely on its bad `status` value now.

### Codegen — all three regenerated from the one schema change

- **Java:** `mvn -B -f gen/java/pom.xml clean test` — `DemandFulfillment.java`
  regenerated via the existing `demand-coordinator` jsonschema2pojo execution
  (no config changes needed), `summaryRef` no longer in the `(Required)`
  javadoc, `shipped` (`List<String>`) and `date` (`String`) added.
  `BUILD SUCCESS`, `Tests run: 12, Failures: 0, Errors: 0` (unchanged — no
  existing test touches `DemandFulfillment`).
- **TypeScript:** `npx json-schema-to-typescript
  ../../schemas/demand-coordinator/demand.fulfillment.json -o
  demand-fulfillment.ts`, re-built `dist/` (`npm run build`, committed per
  D031). `summaryRef?: string`, `shipped?: string[]`, `date?: string` added
  to the `DemandFulfillment` interface. `npx tsc --noEmit --strict` clean.
- **Python:** `datamodel-codegen --input
  ../../schemas/demand-coordinator/demand.fulfillment.json --input-file-type
  jsonschema --output
  platform_contracts/demand_coordinator/demand_fulfillment.py
  --output-model-type pydantic_v2.BaseModel --target-python-version 3.11
  --use-specialized-enum`. The last two flags are load-bearing: without them
  this installed `datamodel-code-generator` (0.68.1) emits a plain `Enum` for
  `Status` instead of the `StrEnum` every other generated module in this repo
  uses (`demand.py`, `telemetry.py`, `model_manifest.py`,
  `hexagon_descriptor.py`, `registry_entry.py`) — caught by diffing against
  the prior file before committing, not by any test (no existing test
  round-trips `DemandFulfillment.status` through JSON, so a plain `Enum`
  would still validate; it would just silently diverge from convention).
  `summaryRef: str | None`, `shipped: list[str] | None`, `date: date_aliased
  | None` (datemodel-codegen aliases the field's `date` type import to avoid
  shadowing the field name `date`) all default to `None`. Full
  `python tests/run_all.py` — all validators pass, including the new
  `validate_demand.py` fixture.

### D031 acceptance — post-tag, run for real, all three languages

Owner authorized the push/tag this session. `v0.11.0` tagged and pushed;
**post-tag D031 acceptance test run for real against the pushed tag, all
three languages, no unverified leg:**

- **Java:** fresh `git clone --branch v0.11.0` (independent of this working
  tree), `mvn -B clean install -DskipTests` into a scratch `.m2` —
  `BUILD SUCCESS`, installed `io.platform:contracts:0.11.0`. A second, fully
  independent scratch Maven project depending on that coordinate compiled and
  ran code constructing a `DemandFulfillment` with `summaryRef` unset —
  `BUILD SUCCESS`, printed object confirms `summaryRef=<null>`.
- **Python:** fresh venv, `pip install
  "git+https://github.com/elmoul/contracts.git@v0.11.0#subdirectory=gen/python"`
  — installed cleanly; constructed, round-tripped
  (`model_dump_json()` → `model_validate_json()`), and confirmed the bad-status
  rejection case still raises `ValidationError`.
- **TypeScript:** `file:`-dependency scratch project, `npx tsc --noEmit
  --strict` clean against a `DemandFulfillment` literal with `summaryRef`
  omitted.

## v0.10.0 — 2026-07-10

Minor release, new schema realized from a stub (STUB → full schema, same
precedent as v0.3.0's control-plane pair): `schemas/app/telemetry.json`,
fulfilling `observability`'s demand
(`demands/fulfilled/observability-20260710-telemetry-schema-report.md`,
`demand/observability-20260710-telemetry-schema`). All three bindings wired.
Branch `demand/observability-telemetry-schema` reviewed and merged to `main`
(`9eb777c`, architect's call, at the owner's explicit request), tagged
`v0.10.0`. **Post-tag D031 acceptance test run for real against the pushed
tag, all three languages, no unverified leg:**
- **Python:** fresh venv, `pip install "git+https://github.com/elmoul/contracts.git@v0.10.0#subdirectory=gen/python"`
  — installed cleanly; imported `TelemetryLogRecord`/`PrometheusMetricLabels`/
  `MetricName`/`Level`/`Env` from the tagged install and re-ran the same
  construct/reject round-trip checks used pre-tag — all passed.
- **Java:** fresh `git clone` + `git checkout v0.10.0` (independent of this
  working tree), `mvn -B clean install -DskipTests` into a scratch `.m2`
  (`docker run maven:3.9-eclipse-temurin-21`) — `BUILD SUCCESS`, installed
  `io.platform:contracts:0.10.0`. A second, fully independent scratch Maven
  project depending on that coordinate (`<version>0.10.0</version>`, no
  path/reactor relationship to this repo) compiled and ran code constructing
  a `TelemetryLogRecord` — `BUILD SUCCESS`, printed the constructed object.
- **TypeScript:** the `file:`-dependency form of D031 (the one mechanism that
  doesn't require a pushed tag) was already verified pre-tag, on the branch —
  see below.

### schemas/app/telemetry.json (STUB → full schema)

Formalizes the conventions already documented and already followed by every
hexagon emitting metrics/logs today, per
`observability/docs/telemetry-conventions.md`:

- **Root (`TelemetryLogRecord`):** the structured JSON log line every hexagon
  emits to stdout for Promtail/Loki ingestion. Required: `timestamp`
  (date-time, UTC), `level` (`DEBUG`/`INFO`/`WARN`/`ERROR`), `message`,
  `component_id`. Optional: `appId` (D009), `traceId` (reserved for future
  OTel correlation). `additionalProperties: false`.
- **`$defs/PrometheusMetricLabels`:** the label set every Prometheus metric
  must carry — required `component_id`, `env` (`local`/`staging`/`prod`,
  Prometheus-injected via `external_labels`, hexagons never emit it
  themselves); optional `app_id` (D009). `additionalProperties: true`
  deliberately — this is the *reserved minimum* label set, not an exhaustive
  one; individual metrics may carry further labels.
- **`$defs/MetricName`:** the `platform_<hexagon>_<name>_<unit>` naming
  pattern as a regex (`^platform_[a-z0-9]+(_[a-z0-9]+)*_(total|seconds|bytes|info)$`),
  covering the four standard Prometheus unit suffixes.
- **`component_id` is the deliberate exception to this repo's camelCase JSON
  convention** — snake_case on both the log record and the Prometheus labels,
  to match Prometheus/Loki field-naming convention (`appId`/`traceId` stay
  camelCase). This is the join key across Prometheus, Loki, and
  `state.event.componentId` (schemas/state-feed/state.event.json) that the
  observability Phase C headline bridge depends on — documented explicitly in
  both fields' descriptions so it isn't "corrected" to camelCase later.
- **`PrometheusMetricLabels`/`MetricName` are deliberately unreferenced from
  the root schema** — Prometheus labels are attached via the metrics client
  API (Micrometer, `prometheus_client`), never built as a JSON document the
  way a log line is. They exist in `$defs` purely for documentation and
  direct-by-pointer validation (see `tests/validate_telemetry.py`), not as a
  combined root envelope that would misrepresent the wire format (no hexagon
  emits one JSON document containing both a log record and a label set).

### Codegen — a genuine, expected per-tool divergence, not a defect

- **Java:** new `sourcePath` in the existing `events` `jsonschema2pojo`
  execution (`gen/java/pom.xml`), package `io.platform.contracts.events`.
  Generates one class, `TelemetryLogRecord` — jsonschema2pojo only walks
  schema nodes reachable from the file's root, so the two unreferenced `$defs`
  generate no class. Hand-wired by exact analogy to the existing
  `usage.event.json`/`dimension.event.json` entries in the same execution
  (same plugin-wide config, no per-execution override needed — unlike the
  v0.9.0/v0.9.1 `model-manifest.json` case, this schema's only
  `additionalProperties: true` node is the unreferenced-and-therefore-ungenerated
  `PrometheusMetricLabels`, so the project-wide `includeAdditionalProperties:
  false` never comes into play here). **Verified for real, unlike
  v0.8.0/v0.9.0/v0.9.1** (this sandbox had Docker where those didn't):
  `docker run --rm -v "<repo>:/repo" -w /repo/gen/java maven:3.9-eclipse-temurin-21
  mvn -B clean test` — `BUILD SUCCESS`, `Tests run: 12, Failures: 0, Errors: 0`
  (unchanged from v0.9.1 — no existing test touches `TelemetryLogRecord`).
  Inspected the generated source directly: `TelemetryLogRecord.java` carries
  all four required fields (`timestamp: OffsetDateTime`, `level: Level` enum
  with the four values, `message: String`, `componentId: String` — Jackson
  `@JsonProperty("component_id")` mapping the snake_case wire name to the
  camelCase Java field), plus optional `appId`/`traceId`; confirmed
  `PrometheusMetricLabels`/`MetricName` generated **no** class in
  `io/platform/contracts/events/` (only `DimensionEvent.java`,
  `TelemetryLogRecord.java`, `UsageEvent.java` present) — the unreferenced-
  `$defs` design behaves identically in Java and TypeScript.
- **TypeScript:** `gen/ts/telemetry.ts` generated via `json-schema-to-typescript`
  (`npx json-schema-to-typescript@13`), confirming the same reachability
  behavior as Java — only `TelemetryLogRecord` is emitted, no
  `PrometheusMetricLabels`/`MetricName` interface. Re-exported from
  `index.ts`; `gen/ts/dist/` rebuilt fresh per D031. **Verified for real**:
  `npx tsc --noEmit --strict` clean in `gen/ts`, and — the actual D031
  acceptance pattern — a scratch project outside this repo depending on
  `"@platform/contracts": "file:C:/Users/pc/Desktop/platform/contracts/gen/ts"`,
  `npm install`, then a `.ts` file importing and constructing a
  `TelemetryLogRecord` passed `tsc --noEmit --strict` clean.
- **Python:** `gen/python/platform_contracts/app/telemetry.py` generated via
  `datamodel-code-generator` (pydantic v2, `--collapse-root-models`), wired
  into `platform_contracts/__init__.py` (both the `from ... import` line and
  `__all__`, plus the version-comment header). **Genuine divergence from
  Java/TS, not a bug:** `datamodel-code-generator` processes the whole
  `$defs` block regardless of root reachability, so — unlike Java/TS — it
  *does* generate `PrometheusMetricLabels` and `MetricName` (as a pydantic
  `RootModel[str]`) as real importable classes, alongside `TelemetryLogRecord`
  and the `Level`/`Env` enums. Left as-is rather than forced into artificial
  cross-language symmetry: Python callers get typed helpers for the
  Prometheus label/metric-name conventions "for free"; Java/TS callers get
  only what they'd actually construct (a log record). **Verified for real**
  in a fresh scratch virtualenv (`pip install ./gen/python`): imported
  `TelemetryLogRecord`, `PrometheusMetricLabels`, `MetricName`, `Level`, `Env`;
  constructed known-good instances of each; confirmed a bad `level`, a bad
  `env`, and a malformed metric name are all rejected with `ValidationError`;
  re-ran the *existing* `platform_contracts` import (`import
  platform_contracts`) and the full `tests/run_all.py` suite in the same venv
  — all pre-existing validators still pass, no regression from the
  `__init__.py` edit. The real git-URL-tag install (`pip install
  "git+...@v0.10.0#subdirectory=gen/python"`) is **not yet run** — no tag
  exists yet (architect's call, as above); do this once the tag is cut, per
  the standing D031 invariant.

### Tests

- Added `tests/validate_telemetry.py` (14 assertions: 3 for the root log
  record, 4 for `PrometheusMetricLabels`, 7 for `MetricName` — 4 good, 3 bad),
  wired into `tests/run_all.py` between `validate_dimension_event.py` and
  `validate_state_event.py`. Validates the two `$defs` directly via JSON
  pointer (`schema["$defs"]["PrometheusMetricLabels"]`), same technique used
  to confirm the schema is sound with `ajv` (`ajv/dist/2020` + `ajv-formats`,
  installed to a scratch dir) before any codegen was attempted.
- Full `python tests/run_all.py` re-run after the `validate_telemetry.py`
  addition: all validators (including every pre-existing one) still pass.

### Toolchain reality this session

Unlike v0.8.0/v0.9.0 (no `mvn`/`java`/Python at all) and v0.9.1 (Java only via
Docker, no local Python), **this sandbox had `py` (Python 3.11.9), Node/npm,
and Docker** — no unverified leg this release. `py` + a scratch venv installed
`datamodel-code-generator`/`pydantic`/`jsonschema` for the real Python
generation/round-trip/full-suite-regression check; Node/npm ran the real
`json-schema-to-typescript` generation, `tsc --noEmit --strict`, and a D031
`file:`-dependency consumer check; `docker run maven:3.9-eclipse-temurin-21`
ran the real `mvn clean test` and let the generated `TelemetryLogRecord.java`
be inspected directly. One correction made mid-session: the first Docker
attempt mounted only `gen/java`, which broke the `../../schemas/app/*.json`
relative `sourcePath`s in `pom.xml` (`NullPointerException` in
`jsonschema2pojo`'s `URLUtil.parseURL` — a sandbox mounting mistake, not a
schema or `pom.xml` defect); mounting the whole repo and setting the working
directory to `gen/java` inside the container fixed it, and the *existing*
`usage.event`/`dimension.event` sources would have hit the identical failure
under the same wrong mount, confirming it wasn't specific to this change.

## v0.9.1 — 2026-07-10

Patch release, Java binding only: fixes the two v0.9.0 defects reported by
`ai-gateway` (the first real Java consumer of the `ai.model-manifest` binding,
evidence in `../ai-gateway/demands/fulfilled/plantpal-20260709-ai-gateway-full-coverage-report.md`).
**No schema file changed** — the wire format (what JSON/YAML documents
validate) is byte-for-byte identical to v0.9.0; TS and Python bindings are
untouched apart from the version strings. Branch `fix/java-binding-v0.9.1`;
tag to be cut by the architect after review, per house convention.

### Defect 1 — `gen/java/pom.xml` non-parseable by Maven (blocked ALL Java artifacts)

- **Root cause:** the `ai-gateway-model-manifest` execution added in v0.9.0
  carried an XML comment containing a literal `--` sequence
  ("…request.yaml/preflight.yaml) -- model-manifest.json…"). XML forbids `--`
  inside a comment body, so Maven failed with "Non-parseable POM … in comment
  after two dashes (--)" before doing anything — no Java artifact of v0.9.0
  could be produced by any consumer.
- **Fix:** reworded the comment (`--` → `;`); no semantic change to the build.

### Defect 2 — `capabilities` generated as an empty stub, `CapabilityDeclaration` never generated

- **Root cause:** `capabilities` in `model-manifest.json` is a pure dictionary
  — an object with **no** `properties` of its own, only
  `additionalProperties: {$ref: #/$defs/CapabilityDeclaration}`. jsonschema2pojo
  (1.2.1) only emits the map-typed `additionalProperties` field — and only then
  walks the `$ref` to generate the value class — when
  `includeAdditionalProperties` is `true`. The plugin-wide
  `<includeAdditionalProperties>false</includeAdditionalProperties>` therefore
  silently produced an empty `Capabilities` class (zero fields) and never
  generated `CapabilityDeclaration` at all. Reproduced in isolation with a
  minimal schema before touching the config.
- **Fix:** per-execution override `<includeAdditionalProperties>true</includeAdditionalProperties>`
  scoped to the `ai-gateway-model-manifest` execution only (all other
  executions keep the plugin-wide `false`). Safe because every schema in
  `model-manifest.json` with real `properties` also declares
  `additionalProperties: false` explicitly, which jsonschema2pojo honors
  regardless of the flag — verified no spurious any-getter/any-setter appears
  on `AiModelManifest` or `CapabilityDeclaration`. The map is exposed on the
  generated `Capabilities` wrapper via `@JsonAnyGetter`/`@JsonAnySetter`
  (`Map<String, CapabilityDeclaration>`), which Jackson (de)serializes
  flattened into the JSON object — exactly the wire shape the schema validates,
  not nested under any extra key.
- Rejected alternatives: restructuring the schema (would risk wire-format
  drift for zero Java gain) and `existingJavaType` on the property (types the
  field as a bare `Map` but does **not** force generation of
  `CapabilityDeclaration` from `$defs`, which is only reachable via the
  `additionalProperties` `$ref`).

### Verification — real builds, not analogy

- `mvn -B clean package` in a fresh `maven:3.9-eclipse-temurin-21` Docker
  container mounting this repo (`-w /work/gen/java`): **BUILD SUCCESS** —
  POM parses, all 6 jsonschema2pojo executions + openapi-generator run,
  `Compiling 40 source files`, `Tests run: 12, Failures: 0, Errors: 0,
  Skipped: 0`, `Building jar: target/contracts-0.9.1.jar`. Run twice (once
  after each fix, once after the version bump).
- Generated sources inspected under `target/generated-sources/jsonschema2pojo/
  io/platform/contracts/aigateway/`: `Capabilities` exposes
  `Map<String, CapabilityDeclaration>`; `CapabilityDeclaration` has
  `Set<String> models` (from `uniqueItems: true`), `Media media`
  (enum REQUIRED/OPTIONAL/NONE), `Boolean streamingDesired = false`,
  `DownshiftPolicy downshiftPolicy` (enum ALLOW/BLOCK/SKIP).
- Wire format proof: `git diff` confirms no file under `schemas/` changed;
  `npx tsc --noEmit` in `gen/ts` clean (exit 0); full `python tests/run_all.py`
  (in a `python:3.12-slim` container) — all validators passed, including
  `validate_model_manifest.py`'s 8 fixtures.
- **Not run:** the D031 clean-install-from-tag acceptance test — impossible
  until the architect cuts the `v0.9.1` tag; must be run post-tag before any
  consumer re-pins.

### Known leftover (pre-existing, unchanged)

- `gen/ts/package-lock.json` still says `0.7.0` — v0.8.0 and v0.9.0 both left
  it stale, so this release follows precedent rather than regenerating the
  lockfile in a patch. Worth a cleanup in the next minor.

## v0.9.0 — 2026-07-10

Minor release, new schema: `ai.model-manifest` (gap G5, closing the contracts
leg of `plantpal-20260709-ai-gateway-full-coverage`, `to: [ai-gateway,
contracts]` — this release is `contracts`' sub-demand only; `ai-gateway`'s
consuming leg is separate and not part of this release). Purely additive — a
new `schemas/ai-gateway/model-manifest.json`, no existing schema touched. **Not
tagged from this session** — v0.9.0 is recorded here as the version this
release will carry once the architect reviews and merges the branch
(`demand/plantpal-model-manifest`); the git tag itself is cut after that, per
this demand's own instructions.

### ai.model-manifest (new schema)

- Validates a static, per-app AI-capability declaration (proposed to live as
  `ai-model-manifest.yaml` at each app's repo root, sibling to
  `app-manifest.yaml`) — the structural fix for the free-text `modelHint`
  improvisation PlantPal's demand calls out. Not modeled as an OpenAPI
  document like `ai.request`/`ai.preflight`: this is a repo self-description
  artifact (spec-contracts.md §4's third catalog row — "Repo self-description
  → JSON Schema"), the same relationship `hexagon.descriptor.json` has to
  `HEXAGON.md`'s frontmatter, not a sync HTTP call. Placed under
  `schemas/ai-gateway/` (the catalog group that already holds
  `request.yaml`/`preflight.yaml`) rather than a new top-level group, since
  it's an ai-gateway contract by function even though its file format differs
  from its siblings.
- **Shape:** `{ appId, class, capabilities }`. `appId`/`class` reuse the exact
  patterns/enum already established by `app.manifest`/`hexagon.descriptor`
  (`class` is D010's risk tier). `capabilities` is an **object keyed by
  capability name** (`vision-identification`, `annotation`, `reasoning-json`,
  `chat`, …), not an array — a map both lets the gateway look a capability up
  directly by name at request time and makes "no capability declared twice"
  free (JSON object keys are inherently unique; an array would have needed a
  uniqueness rule bolted on). Capability keys are constrained to kebab-case via
  `propertyNames` (`^[a-z][a-z0-9]*(-[a-z0-9]+)*$`), matching this repo's
  existing convention for enum-*value* strings (e.g. `class`'s
  `health-class`/`kids-class`), not this schema's own field-name casing (see
  the casing note below).
- Each capability declaration (`$defs/CapabilityDeclaration`) carries exactly
  the three axes the demand's §4 asked for, one field each:
  - `models` (required): the preference-ordered model set for this capability
    — free-form strings (`"gpt-4o"`, `"claude-sonnet-4-6"`, `"gemma3:4b"`, or a
    specialist provider name like `"plantnet"`), deliberately not an enum, so
    a provider roster change never forces a schema bump; `minItems: 1` +
    `uniqueItems: true` (an empty or self-duplicating preference list is
    meaningless).
  - `media` (required, `required | optional | none`): whether this
    capability's calls carry photos/etc. per `ai.request`'s optional `media`
    array. Made required with no default (unlike `streamingDesired`) because
    the gateway needs an explicit answer — inferring "media expected" from a
    missing array on an incoming call would be a guess, not a declaration.
  - `downshiftPolicy` (required, `allow | block | skip`, D023): what the
    gateway does when Treasury's preflight can't clear the top-preference
    model. `allow` = downshift silently down the list (chat, reasoning
    tolerate quality loss); `block` = never downshift, return the explicit
    D023 block response instead (identification: a wrong answer from a
    downshifted local model is worse than an explicit "try later"); `skip` =
    drop the call entirely rather than degrade *or* hard-stop (decorative
    capabilities like visual annotation — matches the demand's own worked
    example verbatim).
  - `streamingDesired` (optional, boolean, default `false`): whether this
    capability wants the future session/streaming flow (demand §3,
    `POST /ai/session` + `GET /ai/session/{id}/stream}`) once it ships, rather
    than today's buffered `/ai/request`. Advisory only, not enforced here — a
    capability may declare this `true` today and keep calling the buffered
    endpoint until the session flow exists, the same documented asymmetry
    PlantPal's own demand commits to for chat. Modeled as a plain boolean
    rather than the demand draft's bare `streaming: desired` marker string —
    there are only two meaningful states here (wanted vs. not), so a third
    enum value would have been dead weight.
- **Casing decision (made explicit per this session's brief, so it isn't
  "fixed" later without review):** this schema's own field names
  (`appId`, `downshiftPolicy`, `streamingDesired`) are **camelCase**, matching
  `ai.request`/`ai.preflight`/`app.manifest` — the schemas this one is a
  structural sibling of, all of which are camelCase throughout. This is the
  **opposite** choice from `demand`'s v0.8.0 kebab-case fields
  (`acceptance-criteria`, `needs-owner`), and deliberately so: that decision
  preserved an on-disk convention already live in committed `demands/*.md`
  files before the schema existed. No `ai-model-manifest.yaml` has been
  committed anywhere yet — there is no pre-existing convention to preserve —
  so this schema defaults to the repo's dominant camelCase convention instead
  of inventing a third casing style. The one deliberate exception: capability
  *names* (the map's keys, e.g. `vision-identification`) are kebab-case,
  because they're enum-shaped identifier values, not field names — consistent
  with how `class`'s own enum values (`health-class`) are kebab-case in an
  otherwise camelCase schema.

### Codegen

- **Java:** new `jsonschema2pojo` execution (`ai-gateway-model-manifest`) in
  `gen/java/pom.xml`, sharing `AiRequest`/`AiResponse`'s
  `io.platform.contracts.aigateway` package (no class-name collision:
  `AiModelManifest`/`CapabilityDeclaration` vs. `AiRequest`/`AiResponse`/
  `BlockedResponse`). `gen/java/pom.xml` bumped to `0.9.0`.
  **Not verified in this session — same absent-JDK gap as v0.8.0** (`mvn`,
  `java` confirmed absent from PATH again). Beyond the routine gap, this
  execution also carries a **first-time structural risk** for this repo's
  Java codegen: `capabilities` is the first field in any schema here shaped as
  a pure dictionary (an object with *no* declared `properties`, only
  `additionalProperties` pointing at a `$ref`). Every prior Map-typed field in
  this repo (`connector.invoke.request`'s `params`/`result`, v0.6.0) was a
  *permissive bag* (`additionalProperties: true`) that needed an explicit
  `existingJavaType: java.util.Map<String, Object>` override to stop
  `includeAdditionalProperties=false` from collapsing it to an empty POJO.
  `capabilities` is different in kind — a schema-typed dictionary, which
  jsonschema2pojo's documented behavior maps to `Map<String,
  CapabilityDeclaration>` natively, unrelated to the `includeAdditionalProperties`
  setting. Deliberately did **not** add an `existingJavaType` override here:
  doing so risks the opposite failure (short-circuiting generation of
  `CapabilityDeclaration` itself, since its only `$ref` in this schema is the
  one inside `capabilities.additionalProperties` — an override could leave
  `Map<String, CapabilityDeclaration>` pointing at a class jsonschema2pojo
  never actually generates). Trusting the tool's native map-schema handling is
  the lower-risk choice, but it is **untested** and flagged as a required
  follow-up alongside the routine `mvn clean test` gap: confirm
  `AiModelManifest.getCapabilities()` compiles as `Map<String,
  CapabilityDeclaration>` (not an empty POJO, not a compile error) before any
  Java consumer pins this tag.
- **TypeScript:** `model-manifest.ts` generated via `json-schema-to-typescript`
  (ephemeral `npx`, not added to `package.json`/lockfile, same one-shot
  precedent as v0.8.0) — emits `AiModelManifest` (with `capabilities: { [k:
  string]: CapabilityDeclaration }`) and `CapabilityDeclaration`. Added both
  to `index.ts`. `dist/` rebuilt via `tsc` per D031 (committed) — picked up
  the new `model-manifest.d.ts`/`.js` plus the additive one-line diff to
  `dist/index.d.ts`. `package.json` bumped to `0.9.0`. **Verified:** `npx tsc
  --noEmit --strict` clean; `npx tsc` (the actual `dist/` rebuild) also clean.
- **Python:** `platform_contracts/ai_gateway/model_manifest.py` written by hand
  in the exact style `datamodel-code-generator` (pydantic v2) produces
  elsewhere in this package (`StrEnum`s for `Class`/`Media`/`DownshiftPolicy`,
  `class_`/`alias="class"` matching `hexagon_descriptor.py`'s existing
  `class_` handling, `capabilities: dict[str, CapabilityDeclaration]` — a
  dictionary is pydantic v2's/`datamodel-code-generator`'s native, unambiguous
  mapping for this same JSON Schema shape, no Java-style ambiguity here).
  Wired into `platform_contracts/ai_gateway/__init__.py` and the top-level
  `platform_contracts/__init__.py` (also corrected its header comment from
  `v0.8.0`). `pyproject.toml` bumped to `0.9.0`. **Not verified — no Python
  interpreter was available in this session either** (`python`/`python3`/`py`
  all resolve only to the Windows Store install-stub, confirmed absent from
  PATH; no `C:\Python*`/`Program Files\Python*` install found). Unlike the
  Java gap, this file was never run through the actual generator — it is a
  hand-written best-effort match to the tool's style, not tool output, and
  must be spot-checked (at minimum: `datamodel-code-generator` regeneration
  from `model-manifest.json` diffed against this file, plus the usual
  round-trip/rejection checks) before any Python consumer pins this tag.

### Tests

- Added `tests/validate_model_manifest.py`, mirroring `validate_demand.py`'s
  pattern: one known-good full declaration (PlantPal's four capabilities from
  the demand's own worked example), one known-good declaration proving
  `streamingDesired`'s optionality, and four known-bad documents (a capability
  missing required `media`; a capability key that isn't kebab-case; an
  unrecognized `downshiftPolicy` value; an empty `models` list; missing
  top-level `appId`/`class`). Wired into `tests/run_all.py` between
  `validate_demand.py` and `check_state_event_sync.py`.
- **Verification substitute for the missing Python interpreter:** every
  fixture in `validate_model_manifest.py` (and the schema's own good/bad cases
  above) was independently checked against `schemas/ai-gateway/model-manifest.json`
  using `ajv-cli` (`npx ajv-cli@5 validate --spec=draft2020`, draft 2020-12 —
  the same draft this schema declares) — all six behave exactly as the Python
  test asserts (2 valid, 4 rejected with the expected error paths). This
  confirms the *schema itself* is sound; it does not confirm
  `jsonschema`+pytest actually runs clean end to end in this repo's own test
  harness, which is the real gap being flagged, not a substitute for it.
- Full Python suite (now 8 files) **not run** — no interpreter available; see
  above. `check_state_event_sync.py` is unaffected by this release (no
  `state.event` change).

### Verification

- `gen/ts`: `npx tsc --noEmit --strict` clean; `npx tsc` (dist rebuild) clean;
  `dist/` committed.
- `gen/java`: **not verified** — no JDK/Maven in this sandbox, same as v0.8.0;
  additionally carries the first-time Map-shaped-schema risk noted above.
  Flagged as a required follow-up before any Java consumer pins this tag.
- `gen/python`: **not verified** — no Python interpreter in this sandbox
  (checked harder than v0.8.0's session: `python`/`python3`/`py` all absent,
  no local install found). `model_manifest.py` is hand-written to match the
  generator's style, not generator output — flagged as a required follow-up,
  stronger than the routine "re-run against the tagged URL" gap other
  releases carry.
- Schema soundness (draft-2020-12 conformance of `model-manifest.json`
  itself, independent of any language binding) verified via `ajv-cli` against
  the six fixtures above — see Tests.
- **D031 real acceptance test (clean install from the tagged URL, all three
  languages) not run — cannot be, until this release is tagged.** Recorded
  here so it isn't skipped once tagging happens, per this repo's own standing
  lesson.

## v0.8.0 — 2026-07-09

Minor release, new schema group: `demand` + `demand.fulfillment`, fulfilling
`demand-coordinator`'s bootstrap demand
(`demand-coordinator-20260709-demand-schema`, see `demands/fulfilled/`). Purely
additive — a new `schemas/demand-coordinator/` group, no existing schema
touched.

### demand, demand.fulfillment (new schemas)
- New `schemas/demand-coordinator/` group, sibling to `control-plane`'s
  (`hexagon.descriptor.json` + `registry.entry.json` precedent). `demand`
  validates the YAML frontmatter every repo's `demands/*.md` carries
  (DEMAND_SYSTEM.md §5): `id`, `date`, `from`, `to[]`, `capability`,
  `acceptance-criteria[]`, `needs-owner`, `status` (`open | satisfied |
  archived` — deliberately excludes the coordinator-internal lifecycle states,
  which live in the coordinator's own ledger per spec-demand-coordinator.md §5,
  not the origin's file). `id` and `from`/`to` entries are pattern-constrained
  (`^[a-z][a-z0-9-]+-\d{8}-[a-z0-9-]+$` for ids, `^[a-z][a-z0-9-]+$` for
  functional names, reusing `hexagon.descriptor`'s convention) — this is the
  schema's whole point per the demand: catch a typo'd target/field name at
  authoring time instead of the coordinator's tolerant parser silently
  bucketing it as unstructured. `acceptance-criteria` is new structure, not
  present in the interim envelope (DEMAND_SYSTEM.md §5 keeps it as a markdown
  body section) — promoted to an array of strings so the coordinator can check
  completion mechanically. `demand.fulfillment` validates
  `demands/fulfilled/<demand-id>-report.md`'s frontmatter: `demandId`,
  `subDemand` (optional — present only for one target's report within a
  multi-hexagon join), `worker`, `status` (`done | blocked` — `done` is a
  claim, not a verdict, matching DEMAND_SYSTEM.md §4's "never self-certify"
  rule; `blocked` exists so a stalled worker reports explicitly per D023
  rather than going silent), `summaryRef` (path to the human-readable summary,
  usually the report file itself).
- **Deliberate casing split, called out so it isn't "fixed" later without
  review:** `demand`'s multi-word fields (`acceptance-criteria`,
  `needs-owner`) are kebab-case, matching the convention already live in
  committed demand files (e.g. `demand-coordinator`'s own bootstrap demand) —
  this schema formalizes an existing on-disk YAML convention, it doesn't
  invent one. `demand.fulfillment`'s `demandId`/`subDemand` are camelCase,
  matching the interim convention spec-demand-coordinator.md §7 already states
  verbatim for this specific envelope. The two schemas are each internally
  consistent with their own precedent but inconsistent with each other; a
  future session may want an owner ruling to reconcile them, but neither
  precedent was mine to overrule unilaterally.
- Demand files written before this schema existed (DEMAND_SYSTEM.md's own
  example of PlantPal's first live demand, written with no frontmatter at all)
  will not validate — expected, per the coordinator's own ingest design, which
  keeps a tolerant fallback for exactly this case.

### Codegen
- **Java:** new `jsonschema2pojo` execution (`demand-coordinator`, plain
  object schemas, package `io.platform.contracts.demandcoordinator`)
  generating `Demand`/`DemandFulfillment`, wired into `gen/java/pom.xml`
  alongside the `control-plane`/`connector` executions.
  `gen/java/pom.xml` bumped to `0.8.0`. **Not verified in this session** — no
  JDK/Maven is available in this sandbox (confirmed: `mvn`, `java` absent from
  PATH, no local `.m2`/JDK install found). The execution block matches the
  `control-plane` execution byte-for-byte apart from source paths and target
  package, which is a low-risk shape (plain object schemas, no `oneOf`, no
  `int64`/Map-typed fields needing jsonschema2pojo extensions), but this is a
  real gap against this repo's own "verify, don't assume" standing lesson
  (D031). **Flagged as a required follow-up**: run `mvn clean test` in
  `gen/java` from an environment with Java 21 + Maven before any Java consumer
  (e.g. `demand-coordinator` itself) pins this tag in anger.
- **TypeScript:** `demand.ts`/`demand-fulfillment.ts` generated via
  `json-schema-to-typescript` (installed ephemerally into `gen/ts/node_modules`
  for this session — not added to `package.json`/`package-lock.json`, since it's
  a one-shot generator invocation, not a runtime or build dependency of the
  published package). Added `Demand`/`DemandFulfillment` to `index.ts`.
  `dist/` rebuilt via `tsc` per D031 (committed) — picked up the two new files
  plus line-ending normalization noise on unrelated `dist/` files (no content
  diff, same as the v0.4.0 precedent). `package.json` bumped to `0.8.0`.
  Verified: `tsc --noEmit --strict` clean.
- **Python:** `platform_contracts/demand_coordinator/{demand,
  demand_fulfillment}.py` via `datamodel-code-generator` (pydantic v2,
  `--collapse-root-models` so pattern-constrained array items resolve to
  `list[constr(...)]` rather than a synthetic `RootModel` wrapper class,
  matching `hexagon_descriptor.py`'s existing style for `decisions`). Wired
  into `platform_contracts/__init__.py`. `pyproject.toml` bumped to `0.8.0`
  (also corrected the `__init__.py` header comment, which had drifted to
  `v0.6.0` since the last untouched release).

### Tests
- Added `tests/validate_demand.py`, mirroring `validate_control_plane.py`'s
  pattern: known-good documents for both schemas (including a
  `demand.fulfillment` with `subDemand` set, for the multi-hexagon-join case,
  and one with `status: blocked`), and known-bad documents per schema (missing
  required fields, a coordinator-internal `status` value rejected on
  `demand`, a malformed `id` missing its embedded `YYYYMMDD` segment, a
  worker-unreportable `status` value rejected on `demand.fulfillment`). Wired
  into `tests/run_all.py`. Full suite (7 files) passes.

### Verification
- `python tests/run_all.py`: all 7 validators pass, including the new one.
- `gen/ts`: `npx tsc --noEmit --strict` clean; `dist/` rebuilt and committed.
- `gen/python`: `pip install ./gen/python` into a fresh scratch virtualenv,
  followed by importing `platform_contracts.demand_coordinator.{demand,
  demand_fulfillment}` and round-tripping a `Demand`/`DemandFulfillment` pair
  (`model_dump_json(by_alias=True)` → `model_validate_json`), plus confirming a
  known-bad document (missing `id`, coordinator-internal `status`) is rejected.
  `pip show platform-contracts` confirms `0.8.0`. **Not yet run against the
  real tagged URL** (`pip install
  "git+https://github.com/elmoul/contracts.git@v0.8.0#subdirectory=gen/python"`)
  — that is the actual D031 acceptance test and can only run after this
  release is tagged and pushed; noted here so it isn't skipped.
- **Java: not verified** — see Codegen note above. This is a gap against this
  repo's own D031 standing invariant and is called out explicitly rather than
  silently assumed correct.

## v0.7.0 — 2026-07-05

Minor release, additive: new `activity.count` event on `state.event` (sixth `oneOf`
member). Gives hub activity counters a proper shape — orchestrator and sentinel-hub
had been repurposing `load` pulses clamped to 100 (`LoadPayload.value` is
percentage-typed) as a stand-in. Follow-up recorded in spec-orchestrator.md and
spec-sentinel-hub.md §7 build notes.

### state.event (additive)
- Added `ActivityCountEvent`/`ActivityCountPayload` to `schemas/state-feed/state.event.json`
  and its Java codegen wrapper `state-event-java.yaml`, envelope identical to the
  existing five (`type`/`timestamp`/`payload` required, `origin` optional). `type` is
  `const "activity.count"`. Payload requires `componentId`, `activity` (a
  machine-readable name — `tool.call`, `mail.summary`, `scan.message`,
  `scan.finding`), and `count` (`integer`, `minimum: 0`). `count` is a **delta since
  the last emission** for a given `(componentId, activity)` pair, not a cumulative
  total — consumers aggregate; documented directly on the field.
- No existing event type touched — the five prior `oneOf` members are byte-for-byte
  unchanged aside from generator regen-timestamp noise.

### Codegen
- **Java:** regenerated the `events` package via the same `openapi-generator` CLI
  invocation used since v0.1.1/v0.6.0 (`-g java --library resttemplate
  --additional-properties=useJakartaEe=true --model-package
  io.platform.contracts.events`) against the updated `state-event-java.yaml` —
  produces `ActivityCountEvent`/`ActivityCountPayload`; the ten pre-existing classes
  diff only on the `@Generated` timestamp. `gen/java/pom.xml` bumped to `0.7.0`.
- **TypeScript:** `state-event.ts` regenerated via `json-schema-to-typescript`,
  adding `ActivityCountEvent`/`ActivityCountPayload` to the `StateEvent` union and
  as named exports; wired into `index.ts`. `dist/` rebuilt via `tsc` per D031
  (committed). `package.json` bumped to `0.7.0`. `tsc --noEmit` clean via `npm run build`.
- **Python:** `state_event.py` regenerated via `datamodel-code-generator`
  (pydantic v2, `--output-model-type pydantic_v2.BaseModel`, no `--field-constraints`
  — matches the existing file's `conint`/`confloat`/`constr` style), adding
  `ActivityCountPayload`/`ActivityCountEvent` and extending the `StateEvent`
  `RootModel` union. `pyproject.toml` bumped to `0.7.0`.

### Tests
- **Java:** added `StateEventActivityCountTest` — deserializes an
  `activity.count` event with `origin: hub`, one without `origin`, and confirms
  Jackson rejects an unknown payload property (`extra`). Full suite: 12 tests green
  (up from 9), including `StateEventOriginTest` and `RunIdOverflowRegressionTest`.
  Verified with `mvn clean test` 3x in a row, 12/12 every run (the v0.6.1 lesson:
  generated sources must land in `target/generated-sources`, never `src/main/java`,
  or repeated clean builds race).
- **Python:** added `tests/validate_state_event.py` mirroring
  `validate_dimension_event.py`'s pattern: known-good `activity.count` event with
  and without `origin`, known-bad negative `count`, known-bad missing `activity`,
  known-bad unknown extra payload property. Full suite (5 files, 20 assertions
  total, up from 15) passes.

### Verification
- `mvn clean test` in `gen/java`: 3/3 clean runs, 12/12 tests green every time.
- `gen/ts`: `npx tsc` (via `npm run build`) clean, `dist/` committed.
- `gen/python`: after tagging, `pip install
  "git+https://github.com/elmoul/contracts.git@v0.7.0#subdirectory=gen/python"` in a
  fresh virtualenv, followed by importing `platform_contracts.state_feed.state_event`
  and constructing an `ActivityCountEvent` — the real acceptance path, not an
  editable/`.pth` install (D031 lesson from v0.6.2).

## v0.6.2 — 2026-07-05

Patch release, Python packaging fix only: no schema change.

### gen/python build-backend fix
- `gen/python/pyproject.toml` declared `build-backend =
  "setuptools.backends.legacy:build"` — that module path does not exist in
  setuptools. Any PEP 517 install (including the documented D031 consumer
  pattern, `pip install
  "git+https://github.com/elmoul/contracts.git@<tag>#subdirectory=gen/python"`)
  failed at the build-backend hook with `ModuleNotFoundError: No module named
  'setuptools.backends'`. `connector-gmail` (first Python consumer) hit this
  and worked around it locally instead of fixing it here; `orchestrator` and
  `sentinel-hub` (both Python, next in Wave 4) would have hit the same wall.
  The D031 "pip `#subdirectory=` genuinely works" note had never actually been
  run against this file.
- Fixed to `setuptools.build_meta`, the standard PEP 517 entry point.
- `version` bumped from `0.6.0` to `0.6.2` — it was left at `0.6.0` through
  v0.6.1's Java-only patch; an installed package reporting the wrong version
  is a latent trap.
- Verified with a clean install in a fresh virtualenv, build isolation on
  (`pip install ./gen/python`): resolves, builds `platform_contracts-0.6.2-py3-none-any.whl`,
  installs cleanly. Then, after tagging, verified the real acceptance path —
  `pip install "git+https://github.com/elmoul/contracts.git@v0.6.2#subdirectory=gen/python"`
  in a second fresh virtualenv — followed by importing
  `platform_contracts`, `platform_contracts.connector.connector_vocabulary`,
  and `platform_contracts.state_feed.state_event`. `gen/java`
  (`mvn clean test`, 10/10-stable per v0.6.1) and `gen/ts`
  (`tsc --noEmit --strict`) confirmed untouched and unaffected.

## v0.6.1 — 2026-07-04

Patch release, Java binding only: build-layout fix, no schema change.

### gen/java build stability
- Fixed an intermittent `gen/java` clean-build failure (~50% failure rate across
  `mvn clean test` runs, confirmed over two sessions' worth of 8x/10x repeated
  clean-build loops) that showed up as truncated/zero-length `.class` files,
  `surefire` failing to load a class that had "successfully" compiled one phase
  earlier, or entire generated packages going invisible to javac's directory scan
  (`package io.platform.contracts.connector does not exist`) — with the affected
  package and even the compiled-file count varying between otherwise-identical
  clean runs.
- Root cause: all four `jsonschema2pojo` executions (`events`, `ci-runner`,
  `control-plane`, `connector`) wrote generated sources directly into
  `${project.basedir}/src/main/java` — the checked-in source tree that
  `maven-compiler-plugin` scans in the same reactor build, immediately after the
  four executions finish writing to it in the same `generate-sources` phase. This
  is a write-then-scan race in a shared directory, not an incremental-compilation
  cache issue (failures occurred even from `mvn clean` every time, and even
  affected static, non-generated files in the same directory).
- Fix: moved all four executions' `outputDirectory` to the conventional
  `target/generated-sources/jsonschema2pojo`, isolating generated output from the
  checked-in `src/main/java` tree. `jsonschema2pojo-maven-plugin` 1.2.1 registers
  this directory as a compile source root automatically (confirmed via the
  plugin's own `addCompileSourceRoot` call) — no `build-helper-maven-plugin`
  needed. Removed the now-stale generated files from `src/main/java` for the
  packages these executions own (`events` — `UsageEvent.java`/`DimensionEvent.java`
  only; `cirunner`; `controlplane`; `connector`); static/openapi-generator-derived
  files in `events` (`Origin.java`, `ComponentHealthEvent.java`, etc.) are
  untouched.
- Verified with `mvn clean test` **10 times in a row**: 10/10 BUILD SUCCESS, 9
  tests passing each run — first clean run of this loop with a 0% failure rate
  since the flakiness was first observed. `gen/ts` (`tsc --noEmit --strict`) and
  `gen/python` (`import platform_contracts`) confirmed unaffected; neither
  binding's version is bumped since neither's generated output changed.

## v0.6.0 — 2026-07-04

Minor release: Wave 4 hub schema delta. Three additive changes — new `connector`
schema group, an optional `origin` field on every `state.event` envelope. No
existing required field touched.

### connector.vocabulary, connector.invoke.request, connector.invoke.response (new schemas)
- New `schemas/connector/` group (spec-connectors.md §2, §5, §6-1). `connector.vocabulary`
  is the machine-readable form of a connector's verb vocabulary — mirrors what each
  connector's `HEXAGON.md` declares in prose, letting the orchestrator discover
  capabilities mechanically and the conventions validator check "no undeclared verbs."
  Each `Verb` has `name`, `mode` (`read`/`write`), `description`, a deliberately
  permissive `params` field, and `returns`. `connector.invoke.request`/`.response` are
  the sync request/response envelope for one verb call (orchestrator/sentinel-hub →
  connector). `confirmationToken` is optional on the request — write verbs require one
  to succeed, but enforcement is connector-side policy, not this schema. `refused` is a
  first-class `status` value on the response, not folded into `error`; `reason` is
  optional but documented as required whenever `status` isn't `ok` (not schema-enforced,
  matching this repo's existing convention for conditionally-present fields, e.g.
  `CiRunPayload.conclusion`).
- Split into three files (one root schema each) rather than one file with multiple
  roots, matching the `ci-runner`/`control-plane` group convention (`build-command.yaml`
  + `build-result.yaml`, `hexagon.descriptor.json` + `registry.entry.json`).
- **Java quirk:** `jsonschema2pojo` with `includeAdditionalProperties=false` (the
  setting every other execution in this repo uses) silently drops a bare
  `"additionalProperties": true` object down to an empty POJO — it does not fall back
  to a `Map`. Fixed the same way `runId`'s `int64` overflow was fixed in v0.5.1: added
  the jsonschema2pojo-specific `existingJavaType: java.util.Map<String, Object>`
  extension directly to the `params`/`result` schema nodes. TS/Python generators map
  the same nodes to `{[k: string]: unknown}` / `dict[str, Any]` natively, no extension
  needed there.

### state.event (additive)
- Added optional `origin` field (`host`/`hub`, D011) to the envelope of all five event
  types (`ComponentHealthEvent`, `LoadEvent`, `CostTickEvent`, `CiRunEvent`,
  `AppStatusEvent`) in both `state.event.json` and its Java codegen wrapper
  `state-event-java.yaml`. Absent means host — existing producers are untouched and
  keep deserializing. Added to both files explicitly since every envelope declares
  `additionalProperties: false`.

### Codegen
- **Java:** new `jsonschema2pojo` execution `connector` in `gen/java/pom.xml`
  (package `io.platform.contracts.connector`), producing `ConnectorVocabulary`,
  `Verb`, `ConnectorInvokeRequest`, `ConnectorInvokeResponse`. Regenerated the
  `events` package via the same `openapi-generator` invocation used for
  `state-event-java.yaml` since v0.1.1 (`-g java --library resttemplate
  --additional-properties=useJakartaEe=true --model-package
  io.platform.contracts.events`) — produces a new `Origin` enum plus the `origin`
  field on all five event classes; verified zero `com.google.gson` imports across
  `gen/java/src` (the regression flagged in an earlier session). `mvn compile` clean.
- **TypeScript:** `connector-vocabulary.ts`, `connector-invoke-request.ts`,
  `connector-invoke-response.ts` via `json-schema-to-typescript`; `state-event.ts`
  regenerated the same way, now exporting an `Origin` type and `origin?: Origin` on
  every event interface. Added all three new types to `index.ts`. `dist/` rebuilt via
  `tsc` per D031 (committed, not gitignored). `tsc --noEmit --strict` clean.
- **Python:** `platform_contracts/connector/{connector_vocabulary,
  connector_invoke_request, connector_invoke_response}.py` via
  `datamodel-code-generator` (pydantic v2), wired into `platform_contracts/__init__.py`.
  `state_event.py` regenerated the same way, adding an `Origin` enum and
  `origin: Origin | None = None` on all five event models. Package imports cleanly.

### Tests
- **Java:** added `ConnectorContractsRoundTripTest` (serialize/deserialize
  `ConnectorVocabulary`, `ConnectorInvokeRequest` with and without
  `confirmationToken`, `ConnectorInvokeResponse` for both `ok` and `refused`
  statuses) and `StateEventOriginTest` (an origin-tagged `ComponentHealthEvent`
  deserializes with `Origin.HUB`; an origin-less event still deserializes with
  `origin` null). Full suite green, including `RunIdOverflowRegressionTest`
  (9 tests total, up from 2).
- **Python:** added `tests/validate_connector.py` mirroring
  `validate_control_plane.py`'s pattern: known-good/known-bad documents for
  `connector.vocabulary` (empty `verbs`, undeclared `mode`) and both
  `connector.invoke` envelopes (missing `verb`, missing `status`). Full suite
  (5 files) passes.

## v0.5.1 — 2026-07-04

Patch release: fixes an int32 overflow on both `runId` fields.

### ci-runner/build-result, state-feed/CiRunPayload (fix)
- `BuildResult.runId` (`schemas/ci-runner/build-result.yaml`) and
  `CiRunPayload.runId` (`schemas/state-feed/state.event.json` and its Java
  codegen wrapper `schemas/state-feed/state-event-java.yaml`) were declared as
  a plain `integer` with no width, so the Java generator emitted `Integer`.
  Real GitHub Actions run IDs are ~11 digits (e.g. `28714195292`), which
  overflows a 32-bit int. Found via a live end-to-end test: a real
  `workflow_dispatch` run's result was rejected by control-plane's
  `/ci/results` endpoint with `HttpMessageNotReadableException: JSON parse
  error: Numeric value (28714195292) out of range of int`.
- Fixed by adding `format: int64` to both `runId` properties. For
  `BuildResult`, `jsonschema2pojo` doesn't map OpenAPI's `format: int64` on
  its own, so `existingJavaType: java.lang.Long` was also added as a
  jsonschema2pojo-specific extension to force the field to `Long`.
  `CiRunPayload` is generated via `openapi-generator` (not
  `jsonschema2pojo`), which does respect `format: int64` and emits `Long`
  directly — regenerated with `--library resttemplate` (the same Jackson
  serialization as before; the default `java` library emits Gson, which
  would have silently swapped serialization frameworks for the whole
  `events` package).
- Regenerated all three bindings. Java: `BuildResult.runId` and
  `CiRunPayload.runId` are now `Long` — verified `mvn compile`. TS/Python are
  unaffected at this size (`number`/`int` don't overflow) but now declare
  `int64` consistently across all three languages.
- Added `gen/java/src/test/java/io/platform/contracts/RunIdOverflowRegressionTest.java`
  (first JUnit test in this repo — added `junit-jupiter` +
  `maven-surefire-plugin` to `gen/java/pom.xml` to support it) deserializing
  an 11-digit `runId` (`28714195292`) into both `BuildResult` and
  `CiRunPayload`, so a future accidental narrowing back to `int`/`Integer` is
  caught by `mvn test`.

## v0.5.0 — 2026-07-04

Minor release: adds a new standalone `dimension.event` schema. Purely additive —
no existing schema touched.

### dimension.event (new schema)
- Initial schema for D024 business-dimension metering (e.g. PlantPal's plant
  count). Mirrors Treasury's existing `DimensionDelta` record
  (`treasury/src/main/java/io/platform/treasury/dimension/`) — `appId`,
  `userId`, `dimensionKey`, `delta` — plus `eventId` and `timestamp`, added so
  the wire event carries the same idempotent-consumption and ordering
  guarantees `usage.event` already has, ahead of any real adapter landing.
  `delta` is a plain `integer` with no `minimum` constraint (unlike
  `usage.event`'s `tokensIn`/`tokensOut`) — Treasury's `KeyedLongCounter` and
  `DimensionCounter` both accept negative deltas by design, to support
  soft-delete decrements.
- This schema fills the exact gap `DimensionUpdatePort`'s javadoc calls out:
  "the dimension-update event schema doesn't exist in contracts yet." No
  Treasury-side Kafka consumer or app-side producer is part of this release —
  those land in future, separately reviewed changes once this schema is
  available to depend on.

### Codegen
- **Java:** regenerated via the existing `jsonschema2pojo-maven-plugin`
  `events` execution in `pom.xml` — added `schemas/app/dimension.event.json`
  alongside `usage.event.json` in that execution's `sourcePaths`. Produced
  `DimensionEvent.java` in `io.platform.contracts.events`. Verified with `mvn
  compile` — clean.
- **TypeScript:** regenerated `dimension-event.ts` via `json-schema-to-typescript`,
  matching `usage-event.ts`'s generation. Added `DimensionEvent` to `index.ts`.
  Rebuilt `gen/ts/dist/` via `tsc` per D031 (committed, not gitignored).
  Verified with `tsc --noEmit --strict` — clean.
- **Python:** regenerated `platform_contracts/app/dimension_event.py` via
  `datamodel-code-generator` (pydantic v2), matching `usage_event.py`'s style.
  Wired into `platform_contracts/__init__.py`. Verified: a payload with a
  negative `delta` round-trips (`model_dump_json` → `model_validate_json`)
  without error, confirming the deliberate absence of a `minimum` constraint.

### Tests
- Added `tests/validate_dimension_event.py`, mirroring
  `tests/validate_ai_request.py`'s pattern: validates `dimension.event.json`
  directly as a JSON Schema (not through a language binding) against a
  known-good event, a known-bad event missing a required field, and a
  known-good event with a negative `delta` — the one field in this schema that
  deviates from every other numeric field in the contract set, so it gets its
  own explicit assertion.

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
  `"@platform/contracts": "file:C:/Users/pc/Desktop/platform/contracts/gen/ts"`,
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
