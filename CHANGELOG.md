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

## v0.14.0 — 2026-07-16

Additive release, all three bindings: Wave 6 "Media & Agents" dependency-root
release (`docs/MEDIA_AGENTS_WAVE_PACK.md` §5.1, decisions D047/D048/D051/D053)
— per the wave's own build plan, nothing else in the pack builds until this
tag lands (§6, gate W1: "tag + one consumer pin proven"). New async job
envelope for `ai-gateway` → `media-generation` generation calls, plus three
new `state.event` payload types for the wave's three new hexagons
(`media-generation`, `agent-runner`, `design-studio`), none of which exist as
repos yet.

### schemas/ai-gateway/job.yaml — `ai.job.request` / `ai.job.status` (new group)

New OpenAPI 3.1 document, `POST /ai/jobs` (submit, 202) / `GET /ai/jobs/{id}`
(poll), mirroring `request.yaml`'s existing shape:

- **`AiJobRequest`** — `jobId` (caller-generated UUID, for polling/correlating
  before the 202 returns), `appId` (D002 functional-name pattern; hub-side
  callers like `design-studio`/`agent-runner` identify the same way as apps —
  no separate class taxonomy), `capability` (`text-to-image` | `image-to-3d`;
  `video` deliberately excluded, no model/spec commitment yet per
  `spec-media-generation.md` §8), `input` (`prompt`/`imageRef`, both optional
  at the schema level — which one is meaningful depends on `capability`;
  `media-generation` cross-checks the combination, this schema does not),
  `params` (permissive object, same idiom as `connector.invoke.request`'s
  `params` — the capability adapter validates its own shape), `jobClass`
  (`interactive` | `batch`, the night-window policy named in the wave pack's
  §5.7 `conventions` brief). All six required.
- **`AiJobStatus`** — `jobId`, `status` (7-value lifecycle enum:
  `queued|admitted|loading|running|succeeded|failed|cancelled`),
  `progressPct`, `resultRefs[]`, `error` (`$ref JobError`), `usage` (`$ref
  JobUsage`), `submittedAt` (required), `startedAt`, `finishedAt` — flat
  sibling timestamp fields per the existing `CiRunPayload` idiom, not a
  nested `timestamps` object. **`error` is conditionally required when
  `status: failed`** (JSON Schema `if`/`then`, added same release — mirrors
  `preflight.yaml`'s `PreflightResponse` if/then for `block`, D023's "never
  silent" pattern applied to job failures). `JobError` requires `code` +
  `message`; `JobUsage` (`durationMs`, `vramPeakMb`) is best-effort, may be
  partially populated on a job that failed mid-run.
- Routes through `ai-gateway` per D022 (unchanged — no direct
  `media-generation` calls); local GPU jobs meter at **$0** (D047).

### state.event — three new payload types (additive `oneOf` members, 6 → 9)

Same envelope idiom as the existing six (`type`/`timestamp`/`payload`
required, `origin` optional, `additionalProperties: false`); mirrored into
`state-event-java.yaml` so both files stay structurally identical
(`tests/check_state_event_sync.py`: 9 event types in sync).

- **`job.progress`** (D047, emitted by `media-generation`): `jobId`,
  `capability`, `status` (same two enums as `ai.job.*`), `queueDepth`
  (required), `progressPct?`, `vramFreeMb?` — VRAM headroom at emission time
  ("the overflow tell" per D047's rationale, citing the 2026-07-11
  texture-stage VRAM-overflow incident).
- **`agent.run`** (D048, emitted by `agent-runner`): `runId`, `repo` (D002
  functional-name pattern), `demandId?` (same pattern as `demand.id` —
  absent for owner-commissioned sessions not tied to a demand), `phase`
  (`launched|finished|failed|stopped`, required), `durationMs?`,
  `tokensUsed?` (parsed from Claude Code's JSON output).
- **`design.mission`** (D051, emitted by `design-studio`): `missionId`,
  `targetRepo` (D002 pattern), `regime` (`console-class|inhabited-class` —
  D053's two-regime custodianship, verbatim), `stage` (9-value mission
  state-machine enum, `harvest` → ... → `closed`, required), `gateOutcome?`
  (`approved|rejected`, present only when the event reports a gate).

**The documented re-pin trap applies here** (this repo's `oneOf` is a strict
union): a consumer with a strict validator pinned to a pre-v0.14.0 tag
rejects all three new `type` values as unknown. Per the wave pack §5.6,
`state-feed` re-pins **before** any producer emits them — `media-generation`,
`agent-runner`, and `design-studio` don't exist as repos yet, so nothing
emits today, but the re-pin-first ordering is load-bearing once they do.
`dashboard`'s own re-pin (to render `job.progress`/`agent.run`/
`design.mission`) is likewise its own separately-scheduled demand (wave pack
§5.6), not raised by this release — see the D043 demand note below.

### Codegen — all three regenerated

- **Java:** `openapi-generator-cli` 7.23.0, `--library resttemplate`
  (Jackson; confirmed zero `com.google.gson` imports). New
  `io.platform.contracts.aigateway`: `AiJobRequest`, `AiJobRequestInput`,
  `AiJobStatus`, `JobError`, `JobUsage`. New `io.platform.contracts.events`:
  `JobProgressEvent`/`Payload`, `AgentRunEvent`/`Payload`,
  `DesignMissionEvent`/`Payload`; the 12 pre-existing classes in that package
  pick up only a refreshed `@Generated` timestamp — no functional change.
  `AiJobStatus`'s `error`-required-when-`failed` if/then isn't surfaced as a
  Java annotation (same precedent as `PreflightResponse`'s
  `reason`/`decision:block`) — stays `@Nullable`/`required=false`;
  enforcement is JSON-Schema-level only. `mvn -f gen/java/pom.xml clean test`:
  BUILD SUCCESS, 12/12.
- **TypeScript:** `json-schema-to-typescript` for `state-event.ts` (3 new
  interfaces, existing 6 untouched); `openapi-typescript` for the new
  `ai-gateway-job.ts` (same paths/components shape as the existing
  `ai-gateway-request.ts`/`ai-gateway-preflight.ts` siblings). Re-exported
  from `index.ts`; `dist/` rebuilt (`npm run build`). `npx tsc --noEmit`
  clean (`tsconfig.json`'s `strict: true` inherited). **Flagged, not fixed
  here:** `json-schema-to-typescript`/`openapi-typescript` are still unpinned
  in `gen/ts/package.json` (only `typescript` itself is) — this run resolved
  `openapi-typescript` 7.13.0 fresh via `npx`; a pre-existing gap, not
  introduced by this release (future demand candidate per the wave pack's own
  ledger, not this wave).
- **Python:** `datamodel-codegen --target-python-version 3.11
  --use-specialized-enum` (the two load-bearing flags per `DEPLOYMENT.md` —
  installed `datamodel-code-generator` 0.68.1 emits plain `Enum` without
  them). New `platform_contracts/ai_gateway/job.py`
  (`AiJobRequest`/`AiJobRequestInput`/`AiJobStatus`/`JobError`/`JobUsage`),
  wired into `platform_contracts/__init__.py`. **Regen side-effect on
  `state_event.py`, noted rather than avoided:** regenerating with the two
  flags converted its **five pre-existing enums** (`Status`, `Phase`,
  `Conclusion`, `Status1`, `Origin`) from plain `Enum` to `StrEnum`, in
  addition to the six new ones (`Capability`, `Status2`, `Phase1`, `Regime`,
  `Stage`, `GateOutcome`) coming out correctly as `StrEnum` from the start.
  This brings the file in line with `DEPLOYMENT.md`'s stated repo-wide
  convention ("every generated `Status`/`Level`/`Env`-style enum in this repo
  is `StrEnum`") — it had silently drifted to plain `Enum` since its last
  regen. **Behaviorally additive, not a break:** a `StrEnum` member compares
  equal to its plain-string value and serializes identically, so existing
  `== "value"` comparisons and JSON round-trips are unaffected (confirmed by
  hand this session); the one consumer-visible change is that
  `isinstance(x, str)` now also returns `True` for these members, which no
  test in this repo relies on being `False`. Other pre-existing plain-`Enum`
  files with the same legacy drift (`ai_gateway/preflight.py`,
  `app/health.py`, `app/manifest.py`, `ci_runner/build_result.py`,
  `connector/connector_invoke_response.py`,
  `connector/connector_vocabulary.py`) are **left untouched** — their schemas
  didn't change this release, so regenerating them was out of scope; flagged
  here so a future session doesn't "fix" them as a surprise mid-release.

Added `tests/validate_ai_job.py` (`AiJobRequest` text-to-image + image-to-3d
known-good; missing `jobClass`, unknown `capability`, unexpected `input`
property, and `status: failed` with no `error` known-bad; `AiJobStatus`
queued-minimal/succeeded-full/failed-with-error known-good). Extended
`tests/validate_state_event.py` with valid+invalid cases for `job.progress`,
`agent.run`, and `design.mission`, matching the existing density. Both wired
into `tests/run_all.py`; full suite green (`python tests/run_all.py`).

**Versioning:** minor bump (0.13.0 → 0.14.0) — a new schema group, three new
additive `oneOf` members, and a conditionally-required field on a
same-release-new schema (no prior `AiJobStatus` consumer exists to break).

**D031 acceptance — Java only this release, per the wave's own W1 gate**
("tag + **one** consumer pin proven", `MEDIA_AGENTS_WAVE_PACK.md` §6): fresh
`.m2` install from the tagged worktree verified (below) — the binding
`ai-gateway` needs for its own W5 session. TypeScript (`file:` scratch
project) and Python (fresh venv, git-URL install) D031 acceptance were **not**
independently re-run this release — flagged so whichever session needs those
bindings next (`dashboard`, hub consumers) knows the leg is still open,
rather than assuming it was covered here.

**Found during this release, not actioned (wave pack's own deferral):**
`contracts`' CI does not regenerate-and-diff `gen/` vs `schemas/` (CON-1's
regen-drift guard remains a hand-verified invariant); `gen/ts` codegen tools
remain unpinned in `package.json`. Both pre-exist this release and are
recorded as a future demand candidate, not fixed here.

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
the acceptance criterion the demand actually asked for.

**Versioning:** minor bump (0.12.0 → 0.13.0), not major. Same precedent as
`v0.11.0`'s `summaryRef` required→optional: loosening a `required` array is a
backward-compatible widening of the accepted set, unlike a removal/rename/
new-required-field.

### Codegen — all three regenerated from the one schema change

- **Java:** `result`/`model`/`provider` are now `@jakarta.annotation.Nullable`
  with `required = false` (was `@Nonnull`/`required = true`); new `skipped`
  field defaults to `Boolean.FALSE`.
- **TypeScript:** `result`/`model`/`provider` are now optional (`?:`);
  `skipped` came out as non-optional `boolean` (not `skipped?:`) —
  `openapi-typescript` treats a field carrying a JSON Schema `default` as
  always-present in the type, matching its convention elsewhere in this repo.
  Also trued up `gen/ts/package-lock.json`'s version fields (0.12.0 →
  0.13.0).
- **Python:** `result: str | None`, `model: str | None`, `provider: str |
  None` (all default `None`); `skipped: bool | None` default `False`.
  `tokensIn`/`tokensOut`/`computedCost` unchanged (still required).

Widened `tests/validate_ai_request.py` to also cover `AiResponse`'s completed
and skipped shapes, plus a check that `tokensIn` is still genuinely required.

D031 post-tag acceptance re-run clean on all three languages, no unverified
leg (fresh clone/venv/`file:` install against the pushed tag each).

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
  free-text forms above.

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
future 1.0 conversation, but declaring platform-wide `contracts` stability is
a bigger decision than this demand asked for and is left to an explicit owner
call, not inferred here.

### Codegen — all three regenerated from the one schema change

- **Java:** `Contracts.java` regenerated via the existing `control-plane`
  jsonschema2pojo execution — no config changes needed. jsonschema2pojo 1.2.1
  does not emit a `@Pattern` annotation for this field even with
  `useJakartaValidation=true` (consistent with `functionalName`/`decisions`'s
  existing pattern fields) — no runtime enforcement change on the Java side.
- **TypeScript:** `used: string[]` is unchanged type-wise —
  `json-schema-to-typescript` doesn't encode `pattern` into the type system.
- **Python:** `Contracts.used` is now
  `list[constr(pattern=r'^[a-z][a-z0-9]*([.-][a-z0-9]+)*$')]` — Python is the
  one binding that actually enforces the constraint at parse/construction
  time, consistent with how `functionalName`/`decisions` already behave.

Added `GOOD_USED_CONTRACT_IDS` (the six real ids from the demand's acceptance
criteria) and `BAD_USED_CONTRACT_IDS` (the three audited free-text forms) to
`tests/validate_control_plane.py`.

D031 post-tag acceptance re-run clean on all three languages, no unverified
leg — Python install confirmed the new pattern actually rejects a free-text
`used` entry against the tagged package.

## v0.11.0 — 2026-07-11

Minor release, all three bindings: reconciles
`schemas/demand-coordinator/demand.fulfillment.json` with
`DEMAND_SYSTEM.md` §5 and real fleet usage, fulfilling `demand-coordinator`'s
demand
(`demands/fulfilled/demand-coordinator-20260710-contracts-fulfillment-envelope-drift-report.md`,
`demand-coordinator-20260710-contracts-fulfillment-envelope-drift`).

Owner ruling (recorded in the demand, resolve via schema, not fleet
migration): the schema was out of step with both the doc and reality, not the
other way around. Across the 12 real fulfillment reports in the fleet today,
0 set `summaryRef` (required until now), 7 set `date`, most set `shipped` —
`DEMAND_SYSTEM.md` §5 documents `shipped`/`date` as the convention and never
mentions `summaryRef` at all.

### schemas/demand-coordinator/demand.fulfillment.json (additive)

- **`summaryRef` required → optional.** A report file's own path
  conventionally already is the summary.
- **New optional `shipped`** (`array` of `string`) — tags, versions, or
  branch@commit refs, matching what the fleet already writes.
- **New optional `date`** (`string`, `format: date`) — the report's write
  date.
- `additionalProperties: false` unchanged — additive structure, not a
  loosening of the schema's shape discipline.
- `required` is now just `["demandId", "worker", "status"]`.

Added `GOOD_FULFILLMENT_SHIPPED_DATE_NO_SUMMARY_REF` to
`tests/validate_demand.py`; dropped the now-stale "missing summaryRef" half of
`BAD_FULFILLMENT`'s failure reason. Also fixed `DEPLOYMENT.md`'s Python
section, which never recorded the two load-bearing codegen flags below.

### Codegen — all three regenerated from the one schema change

- **Java:** `DemandFulfillment.java` regenerated via the existing
  `demand-coordinator` jsonschema2pojo execution — `summaryRef` no longer
  `(Required)`, `shipped` (`List<String>`) and `date` (`String`) added.
- **TypeScript:** `summaryRef?: string`, `shipped?: string[]`, `date?: string`
  added to the `DemandFulfillment` interface; `dist/` rebuilt.
- **Python:** regenerated with `datamodel-codegen ... --target-python-version
  3.11 --use-specialized-enum` — **the two flags are load-bearing**: without
  them, the installed `datamodel-code-generator` (0.68.1) emits a plain
  `Enum` for `Status` instead of the `StrEnum` every other generated module in
  this repo uses. `summaryRef: str | None`, `shipped: list[str] | None`,
  `date: date_aliased | None` (aliased to avoid shadowing the field name),
  all default `None`.

Owner authorized the push/tag this session. D031 post-tag acceptance re-run
clean on all three languages, no unverified leg.

## v0.10.0 — 2026-07-10

Minor release, new schema realized from a stub (STUB → full schema, same
precedent as v0.3.0's control-plane pair): `schemas/app/telemetry.json`,
fulfilling `observability`'s demand
(`demands/fulfilled/observability-20260710-telemetry-schema-report.md`,
`demand/observability-20260710-telemetry-schema`). All three bindings wired.
Branch `demand/observability-telemetry-schema` reviewed and merged to `main`
(`9eb777c`), tagged `v0.10.0`.

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
  one.
- **`$defs/MetricName`:** the `platform_<hexagon>_<name>_<unit>` naming
  pattern as a regex (`^platform_[a-z0-9]+(_[a-z0-9]+)*_(total|seconds|bytes|info)$`),
  covering the four standard Prometheus unit suffixes.
- **`component_id` is the deliberate exception to this repo's camelCase JSON
  convention** — snake_case on both the log record and the Prometheus labels,
  to match Prometheus/Loki field-naming convention (`appId`/`traceId` stay
  camelCase). This is the join key across Prometheus, Loki, and
  `state.event.componentId` that the observability Phase C headline bridge
  depends on — documented explicitly in both fields' descriptions so it isn't
  "corrected" to camelCase later.
- **`PrometheusMetricLabels`/`MetricName` are deliberately unreferenced from
  the root schema** — Prometheus labels are attached via the metrics client
  API (Micrometer, `prometheus_client`), never built as a JSON document the
  way a log line is. They exist in `$defs` purely for documentation and
  direct-by-pointer validation, not as a combined root envelope that would
  misrepresent the wire format.

### Codegen — a genuine, expected per-tool divergence, not a defect

- **Java:** new `sourcePath` in the existing `events` `jsonschema2pojo`
  execution, package `io.platform.contracts.events`. Generates one class,
  `TelemetryLogRecord` — jsonschema2pojo only walks schema nodes reachable
  from the file's root, so the two unreferenced `$defs` generate no class.
- **TypeScript:** `gen/ts/telemetry.ts` generated via
  `json-schema-to-typescript`, confirming the same reachability behavior as
  Java — only `TelemetryLogRecord` is emitted, no
  `PrometheusMetricLabels`/`MetricName` interface. Re-exported from
  `index.ts`; `dist/` rebuilt.
- **Python:** **genuine divergence from Java/TS, not a bug** —
  `datamodel-code-generator` processes the whole `$defs` block regardless of
  root reachability, so it *does* generate `PrometheusMetricLabels` and
  `MetricName` (as a pydantic `RootModel[str]`) as real importable classes,
  alongside `TelemetryLogRecord` and the `Level`/`Env` enums. Left as-is
  rather than forced into artificial cross-language symmetry: Python callers
  get typed helpers for the Prometheus label/metric-name conventions "for
  free"; Java/TS callers get only what they'd actually construct (a log
  record).

Added `tests/validate_telemetry.py` (14 assertions covering the root log
record, `PrometheusMetricLabels`, and `MetricName`), wired into
`tests/run_all.py`.

D031 post-tag acceptance re-run clean on all three languages (Java verified in
Docker — `maven:3.9-eclipse-temurin-21` — since no local JDK/Maven was
available this session), no unverified leg.

## v0.9.1 — 2026-07-10

Patch release, Java binding only: fixes the two v0.9.0 defects reported by
`ai-gateway` (the first real Java consumer of the `ai.model-manifest` binding,
evidence in `../ai-gateway/demands/fulfilled/plantpal-20260709-ai-gateway-full-coverage-report.md`).
**No schema file changed** — the wire format (what JSON/YAML documents
validate) is byte-for-byte identical to v0.9.0; TS and Python bindings are
untouched apart from the version strings.

### Defect 1 — `gen/java/pom.xml` non-parseable by Maven (blocked ALL Java artifacts)

- **Root cause:** the `ai-gateway-model-manifest` execution added in v0.9.0
  carried an XML comment containing a literal `--` sequence. XML forbids `--`
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
  generated `CapabilityDeclaration` at all.
- **Fix:** per-execution override
  `<includeAdditionalProperties>true</includeAdditionalProperties>` scoped to
  the `ai-gateway-model-manifest` execution only (all other executions keep
  the plugin-wide `false`). Safe because every schema in `model-manifest.json`
  with real `properties` also declares `additionalProperties: false`
  explicitly, which jsonschema2pojo honors regardless of the flag — verified
  no spurious any-getter/any-setter appears on `AiModelManifest` or
  `CapabilityDeclaration`. The map is exposed on the generated `Capabilities`
  wrapper via `@JsonAnyGetter`/`@JsonAnySetter`
  (`Map<String, CapabilityDeclaration>`), which Jackson (de)serializes
  flattened into the JSON object — the exact wire shape the schema validates.
- Rejected alternatives: restructuring the schema (risks wire-format drift for
  zero Java gain) and `existingJavaType` on the property (types the field as a
  bare `Map` but does **not** force generation of `CapabilityDeclaration` from
  `$defs`, which is only reachable via the `additionalProperties` `$ref`).

### Verification

Verified in Docker (`maven:3.9-eclipse-temurin-21`): both fixes compile clean,
`Capabilities` now exposes `Map<String, CapabilityDeclaration>` with all four
`CapabilityDeclaration` fields (`models`, `media`, `streamingDesired`,
`downshiftPolicy`) correctly typed. Confirmed no file under `schemas/`
changed (wire format byte-identical to v0.9.0); TS/Python unaffected.
**Not run:** the D031 clean-install-from-tag test — blocked on the architect
cutting the `v0.9.1` tag; run it post-tag before any consumer re-pins.

### Known leftover (pre-existing, unchanged)

- `gen/ts/package-lock.json` still says `0.7.0` — v0.8.0 and v0.9.0 both left
  it stale, so this release follows precedent rather than regenerating the
  lockfile in a patch. Worth a cleanup in the next minor.

## v0.9.0 — 2026-07-10

Minor release, new schema: `ai.model-manifest` (gap G5, closing the contracts
leg of `plantpal-20260709-ai-gateway-full-coverage`, `to: [ai-gateway,
contracts]` — this release is `contracts`' sub-demand only; `ai-gateway`'s
consuming leg is separate). Purely additive — a new
`schemas/ai-gateway/model-manifest.json`, no existing schema touched. **Not
tagged from this session** — the git tag is cut once the architect reviews and
merges branch `demand/plantpal-model-manifest`.

### ai.model-manifest (new schema)

- Validates a static, per-app AI-capability declaration (proposed to live as
  `ai-model-manifest.yaml` at each app's repo root, sibling to
  `app-manifest.yaml`) — the structural fix for the free-text `modelHint`
  improvisation PlantPal's demand calls out. Not modeled as an OpenAPI
  document like `ai.request`/`ai.preflight`: this is a repo self-description
  artifact (spec-contracts.md §4's third catalog row), the same relationship
  `hexagon.descriptor.json` has to `HEXAGON.md`'s frontmatter, not a sync HTTP
  call. Placed under `schemas/ai-gateway/` rather than a new top-level group,
  since it's an ai-gateway contract by function even though its file format
  differs from its siblings.
- **Shape:** `{ appId, class, capabilities }`. `appId`/`class` reuse the exact
  patterns/enum already established by `app.manifest`/`hexagon.descriptor`
  (`class` is D010's risk tier). `capabilities` is an **object keyed by
  capability name** (`vision-identification`, `annotation`, `reasoning-json`,
  `chat`, …), not an array — a map both lets the gateway look a capability up
  directly by name at request time and makes "no capability declared twice"
  free. Capability keys are constrained to kebab-case via `propertyNames`
  (`^[a-z][a-z0-9]*(-[a-z0-9]+)*$`).
- Each capability declaration (`$defs/CapabilityDeclaration`) carries exactly
  the three axes the demand's §4 asked for, one field each:
  - `models` (required): the preference-ordered model set for this capability
    — free-form strings (`"gpt-4o"`, `"claude-sonnet-4-6"`, `"gemma3:4b"`, or a
    specialist provider name like `"plantnet"`), deliberately not an enum, so
    a provider roster change never forces a schema bump; `minItems: 1` +
    `uniqueItems: true`.
  - `media` (required, `required | optional | none`): whether this
    capability's calls carry photos/etc. per `ai.request`'s optional `media`
    array. Made required with no default because the gateway needs an
    explicit answer, not a guess from a missing array on an incoming call.
  - `downshiftPolicy` (required, `allow | block | skip`, D023): what the
    gateway does when Treasury's preflight can't clear the top-preference
    model. `allow` = downshift silently down the list (chat, reasoning
    tolerate quality loss); `block` = never downshift, return the explicit
    D023 block response instead (identification: a wrong answer from a
    downshifted local model is worse than an explicit "try later"); `skip` =
    drop the call entirely rather than degrade *or* hard-stop (decorative
    capabilities like visual annotation).
  - `streamingDesired` (optional, boolean, default `false`): whether this
    capability wants the future session/streaming flow (demand §3,
    `POST /ai/session` + `GET /ai/session/{id}/stream`) once it ships, rather
    than today's buffered `/ai/request`. Advisory only, not enforced here.
    Modeled as a plain boolean rather than the demand draft's bare
    `streaming: desired` marker string — there are only two meaningful states
    here (wanted vs. not).
- **Casing decision (made explicit so it isn't "fixed" later without
  review):** this schema's own field names (`appId`, `downshiftPolicy`,
  `streamingDesired`) are **camelCase**, matching `ai.request`/`ai.preflight`/
  `app.manifest` — the schemas this one is a structural sibling of. This is
  the **opposite** choice from `demand`'s v0.8.0 kebab-case fields, and
  deliberately so: that decision preserved an on-disk convention already live
  in committed `demands/*.md` files before the schema existed, whereas no
  `ai-model-manifest.yaml` has been committed anywhere yet. The one
  deliberate exception: capability *names* (the map's keys) are kebab-case,
  because they're enum-shaped identifier values, not field names — consistent
  with how `class`'s own enum values (`health-class`) are kebab-case in an
  otherwise camelCase schema.

### Codegen

- **Java:** new `jsonschema2pojo` execution (`ai-gateway-model-manifest`),
  sharing `AiRequest`/`AiResponse`'s `io.platform.contracts.aigateway`
  package. `capabilities` is this repo's first field shaped as a pure
  schema-typed dictionary (an object with no declared `properties`, only
  `additionalProperties: {$ref: ...}`) — different in kind from the
  prior Map-typed-field precedent (`connector`, v0.6.0), which was a
  *permissive bag* (`additionalProperties: true`) needing an
  `existingJavaType` override. Deliberately did **not** add an
  `existingJavaType` override here, trusting jsonschema2pojo's native
  map-schema handling instead — risking the opposite failure (short-
  circuiting `CapabilityDeclaration` generation) seemed worse. (Two real
  defects in this session's Java output — the unparseable pom.xml comment,
  and `capabilities` generating as an empty stub after all — were found and
  fixed in v0.9.1, above.)
- **TypeScript:** `model-manifest.ts` generated via `json-schema-to-typescript`
  — emits `AiModelManifest` (`capabilities: { [k: string]: CapabilityDeclaration
  }`) and `CapabilityDeclaration`. Added to `index.ts`; `dist/` rebuilt.
- **Python:** `platform_contracts/ai_gateway/model_manifest.py` written by
  hand in the exact style `datamodel-code-generator` (pydantic v2) produces
  elsewhere in this package (`StrEnum`s for `Class`/`Media`/`DownshiftPolicy`,
  `class_`/`alias="class"`, `capabilities: dict[str, CapabilityDeclaration]`).
  Wired into `platform_contracts/ai_gateway/__init__.py` and the top-level
  `__init__.py`. Hand-written, not tool output — flagged as needing a
  generator-diff spot-check before any Python consumer pins this tag.

Added `tests/validate_model_manifest.py` (2 known-good, 4 known-bad
fixtures), wired into `tests/run_all.py`. Schema soundness independently
confirmed via `ajv-cli` (draft 2020-12) since neither a JDK/Maven nor a Python
interpreter was available in this sandbox this session; **D031 real
acceptance test not run — cannot be until this release is tagged**, recorded
here so it isn't skipped once tagging happens.

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
  which live in the coordinator's own ledger, not the origin's file). `id` and
  `from`/`to` entries are pattern-constrained
  (`^[a-z][a-z0-9-]+-\d{8}-[a-z0-9-]+$` for ids, `^[a-z][a-z0-9-]+$` for
  functional names) — this is the schema's whole point per the demand: catch a
  typo'd target/field name at authoring time instead of the coordinator's
  tolerant parser silently bucketing it as unstructured. `acceptance-criteria`
  is new structure, promoted to an array of strings so the coordinator can
  check completion mechanically. `demand.fulfillment` validates
  `demands/fulfilled/<demand-id>-report.md`'s frontmatter: `demandId`,
  `subDemand` (optional — present only for one target's report within a
  multi-hexagon join), `worker`, `status` (`done | blocked` — `done` is a
  claim, not a verdict, matching DEMAND_SYSTEM.md §4's "never self-certify"
  rule), `summaryRef` (path to the human-readable summary, usually the report
  file itself).
- **Deliberate casing split, called out so it isn't "fixed" later without
  review:** `demand`'s multi-word fields (`acceptance-criteria`,
  `needs-owner`) are kebab-case, matching the convention already live in
  committed demand files — this schema formalizes an existing on-disk
  convention, it doesn't invent one. `demand.fulfillment`'s
  `demandId`/`subDemand` are camelCase, matching the interim convention
  spec-demand-coordinator.md §7 already states verbatim for this specific
  envelope. The two schemas are each internally consistent with their own
  precedent but inconsistent with each other; a future session may want an
  owner ruling to reconcile them.
- Demand files written before this schema existed (e.g. PlantPal's first live
  demand, no frontmatter at all) will not validate — expected, per the
  coordinator's own tolerant-fallback ingest design.

### Codegen
- **Java:** new `jsonschema2pojo` execution (`demand-coordinator`, package
  `io.platform.contracts.demandcoordinator`) generating
  `Demand`/`DemandFulfillment`. **Not verified this session** — no JDK/Maven
  available; the execution matches the `control-plane` execution shape
  byte-for-byte apart from source paths/package, but this is a real gap
  against this repo's own D031 "verify, don't assume" lesson. Flagged as a
  required follow-up before any Java consumer pins this tag.
- **TypeScript:** `demand.ts`/`demand-fulfillment.ts` generated via
  `json-schema-to-typescript`, added to `index.ts`; `dist/` rebuilt. Verified:
  `tsc --noEmit --strict` clean.
- **Python:** `platform_contracts/demand_coordinator/{demand,
  demand_fulfillment}.py` via `datamodel-code-generator` (pydantic v2,
  `--collapse-root-models`). Wired into `platform_contracts/__init__.py`.

Added `tests/validate_demand.py` — known-good documents for both schemas
(including a `subDemand`-bearing fulfillment and a `status: blocked` case) and
known-bad documents per schema. Full suite (7 files) passes.

## v0.7.0 — 2026-07-05

Minor release, additive: new `activity.count` event on `state.event` (sixth `oneOf`
member). Gives hub activity counters a proper shape — orchestrator and sentinel-hub
had been repurposing `load` pulses clamped to 100 (`LoadPayload.value` is
percentage-typed) as a stand-in.

### state.event (additive)
- Added `ActivityCountEvent`/`ActivityCountPayload` to `schemas/state-feed/state.event.json`
  and its Java codegen wrapper `state-event-java.yaml`, envelope identical to the
  existing five (`type`/`timestamp`/`payload` required, `origin` optional). `type` is
  `const "activity.count"`. Payload requires `componentId`, `activity` (a
  machine-readable name — `tool.call`, `mail.summary`, `scan.message`,
  `scan.finding`), and `count` (`integer`, `minimum: 0`). `count` is a **delta since
  the last emission** for a given `(componentId, activity)` pair, not a cumulative
  total — consumers aggregate.
- No existing event type touched — the five prior `oneOf` members are byte-for-byte
  unchanged aside from generator regen-timestamp noise.

### Codegen
- **Java:** regenerated the `events` package via the same `openapi-generator` CLI
  invocation used since v0.1.1/v0.6.0 — produces `ActivityCountEvent`/
  `ActivityCountPayload`; the ten pre-existing classes diff only on the
  `@Generated` timestamp.
- **TypeScript:** `state-event.ts` regenerated, adding `ActivityCountEvent`/
  `ActivityCountPayload` to the `StateEvent` union; `dist/` rebuilt.
- **Python:** `state_event.py` regenerated, adding `ActivityCountPayload`/
  `ActivityCountEvent` and extending the `StateEvent` `RootModel` union.

Added `StateEventActivityCountTest` (Java) and `tests/validate_state_event.py`
(Python) covering `activity.count` with/without `origin`, negative `count`,
missing `activity`, and an unknown extra payload property. Full suites green
(Java: 12 tests, verified stable across 3 clean `mvn clean test` runs —
confirming the v0.6.1 build-layout fix holds under real load).

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
- Fixed to `setuptools.build_meta`, the standard PEP 517 entry point.
- `version` bumped from `0.6.0` to `0.6.2` — it was left at `0.6.0` through
  v0.6.1's Java-only patch; an installed package reporting the wrong version
  is a latent trap.
- Verified via a clean install in a fresh virtualenv, both `pip install
  ./gen/python` and, post-tag, the real `pip install
  git+...@v0.6.2#subdirectory=gen/python` acceptance path. `gen/java`/`gen/ts`
  confirmed unaffected.

## v0.6.1 — 2026-07-04

Patch release, Java binding only: build-layout fix, no schema change.

### gen/java build stability
- Fixed an intermittent `gen/java` clean-build failure (~50% failure rate across
  `mvn clean test` runs, confirmed over two sessions' worth of repeated
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
  this directory as a compile source root automatically — no
  `build-helper-maven-plugin` needed. Removed the now-stale generated files from
  `src/main/java` for the packages these executions own (`events` —
  `UsageEvent.java`/`DimensionEvent.java` only; `cirunner`; `controlplane`;
  `connector`); static/openapi-generator-derived files in `events` (`Origin.java`,
  `ComponentHealthEvent.java`, etc.) are untouched.
- Verified stable across 10 consecutive clean `mvn clean test` runs (0/10
  failures, 9/9 tests passing every run — versus the ~50% failure rate before
  the fix). `gen/ts`/`gen/python` confirmed unaffected; neither binding's
  version is bumped since neither's generated output changed.

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
  roots, matching the `ci-runner`/`control-plane` group convention.
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
- **Java:** new `jsonschema2pojo` execution `connector` (package
  `io.platform.contracts.connector`), producing `ConnectorVocabulary`, `Verb`,
  `ConnectorInvokeRequest`, `ConnectorInvokeResponse`. Regenerated the `events`
  package via the existing `openapi-generator` invocation, adding an `Origin`
  enum plus the `origin` field on all five event classes; confirmed zero
  `com.google.gson` imports across `gen/java/src` (a regression flagged in an
  earlier session).
- **TypeScript:** `connector-vocabulary.ts`, `connector-invoke-request.ts`,
  `connector-invoke-response.ts` via `json-schema-to-typescript`;
  `state-event.ts` regenerated, now exporting an `Origin` type and
  `origin?: Origin` on every event interface. Added to `index.ts`; `dist/`
  rebuilt.
- **Python:** `platform_contracts/connector/{connector_vocabulary,
  connector_invoke_request, connector_invoke_response}.py` via
  `datamodel-code-generator`, wired into `platform_contracts/__init__.py`.
  `state_event.py` regenerated, adding an `Origin` enum and
  `origin: Origin | None = None` on all five event models.

Added `ConnectorContractsRoundTripTest` and `StateEventOriginTest` (Java, full
suite 9 tests green); `tests/validate_connector.py` (Python, 5 files) —
known-good/known-bad documents for `connector.vocabulary` and both
`connector.invoke` envelopes.

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
  `CiRunPayload.runId` are now `Long`. TS/Python are unaffected at this size
  (`number`/`int` don't overflow) but now declare `int64` consistently
  across all three languages.
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
  Treasury-side Kafka consumer or app-side producer is part of this release.

### Codegen
- **Java:** regenerated via the existing `jsonschema2pojo-maven-plugin`
  `events` execution — added `schemas/app/dimension.event.json` alongside
  `usage.event.json` in that execution's `sourcePaths`. Produced
  `DimensionEvent.java` in `io.platform.contracts.events`.
- **TypeScript:** regenerated `dimension-event.ts` via `json-schema-to-typescript`,
  matching `usage-event.ts`'s generation. Added `DimensionEvent` to `index.ts`.
  Rebuilt `gen/ts/dist/` via `tsc` per D031 (committed, not gitignored).
- **Python:** regenerated `platform_contracts/app/dimension_event.py` via
  `datamodel-code-generator` (pydantic v2), matching `usage_event.py`'s style.
  Wired into `platform_contracts/__init__.py`. A payload with a negative
  `delta` round-trips without error, confirming the deliberate absence of a
  `minimum` constraint.

Added `tests/validate_dimension_event.py`, validating `dimension.event.json`
directly as a JSON Schema against a known-good event, a known-bad event
missing a required field, and a known-good event with a negative `delta`.

## v0.4.0 — 2026-07-04

Minor release: adds an optional `media` field to `ai.request`'s `AiRequest` schema
so photo-based (and other multimodal) calls can route through `ai-gateway` on the
same envelope. Purely additive — no existing required field touched, `AiResponse`
and `BlockedResponse` are untouched (response stays text-only).

### schemas/ai-gateway/request.yaml (AiRequest — additive)
- Driven by PlantPal's chunk 1: all four of PlantPal's AI-calling modules
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
  required *within* a media item (`additionalProperties: false` on the item) —
  but the `media` array itself is not in `AiRequest`'s top-level `required` list,
  so text-only callers are unaffected. The gateway is expected to pass `media`
  through untouched to providers that support vision input, and to ignore it for
  providers that don't.
- Deliberately did not touch `AiResponse`/`BlockedResponse` — a vision call's
  result is still just text, so the response envelope doesn't need a
  media-shaped counterpart.

### Codegen
- **Java:** regenerated `AiRequest.java` via `openapi-generator` directly
  against `request.yaml` (this schema uses `JavaClientCodegen`, not
  `jsonschema2pojo`, since it's an OpenAPI document, not a plain JSON
  Schema — `ai.request` never went through the `jsonschema2pojo-maven-plugin`
  executions in `pom.xml`). Produced a new `AiRequestMediaInner.java` (the
  array item type); `AiResponse.java`/`BlockedResponse.java` regenerated
  byte-identical since their schemas didn't change.
- **TypeScript:** regenerated `ai-gateway-request.ts` via `openapi-typescript`
  (matching the file's own header — never `json-schema-to-typescript` output
  like the plain-JSON-Schema control-plane files, since `request.yaml` is a
  full OpenAPI document). Rebuilt `gen/ts/dist/` fresh per D031.
- **Python:** regenerated `platform_contracts/ai_gateway/request.py` via
  `datamodel-code-generator` (pydantic v2, `--input-file-type openapi`).
  Produced a new `MediaItem` model (base64 content typed as pydantic's
  `Base64Str`). Confirmed `media` is truly optional (a payload without it
  still validates) and a media item missing `mimeType` raises
  `ValidationError`.

Added `tests/validate_ai_request.py` — first structured test for `ai-gateway`
(previously verified only by compiling/typechecking the generated bindings).
Validates a known-good request with `media`, a known-good request without
`media`, and a known-bad request whose media item is missing `mimeType`.

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
  not a repo property), `repoUrl`, `version` (git tag, or `version+shortsha`),
  `contractsPin`, `updatedAt`, and app-only `appId`/`class`/`plan` (populated once
  `app.manifest` registration arrives; `class`/`plan` enums aligned with
  `app.manifest`'s).

### Codegen
- **Java:** new `jsonschema2pojo` execution (`control-plane`, plain object schemas,
  package `io.platform.contracts.controlplane`) generating `HexagonDescriptor`,
  `RegistryEntry`, and the nested `Contracts` type.
- **TypeScript:** generated `hexagon-descriptor.ts` / `registry-entry.ts` via
  json-schema-to-typescript, re-exported from `index.ts`. `gen/ts/dist/` rebuilt fresh
  per D031.
- **Python:** generated `platform_contracts/control_plane/{hexagon_descriptor,
  registry_entry}.py` via datamodel-code-generator (pydantic v2), wired into the
  package `__init__.py`.

Added `tests/validate_control_plane.py` — no test framework existed in this repo
before this release. Validates the JSON Schemas themselves against example
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
  `"prepare": "tsc"` script — npm still invokes `prepare` on a `file:` install, and it
  fails there too (no `devDependencies` present in a linked/packed install), which
  would have broken every consumer. `"build": "tsc"` remains as a manual step for
  regenerating `dist/` before a release. `types` now points at `dist/index.d.ts` (was
  `index.ts`) to match the committed-output model.
- Verified end-to-end with a scratch `file:` consumer outside this repo — resolves,
  `require('@platform/contracts')` works, and a `.ts` file importing
  `BuildCommand`/`BuildResult`/`UsageEvent` type-checks clean under `tsc --noEmit
  --strict`.

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

### gen/ts (D031 follow-through — git-tag consumption)
- Per new decision **D031** (`contracts` is consumed via GitHub-tag pinning, no package
  registry), `gen/ts/package.json` had `main: dist/index.js` but no build step npm runs
  automatically on `npm install github:...` — only a manual `build` script, which a
  git-installed dependency never triggers. Consumers pinning via tag would get a 404 on
  `dist/index.js`.
- Fixed: added a `tsconfig.json` (was missing entirely) and a `"prepare": "tsc"` script
  — `prepare` is the npm lifecycle hook that runs on `npm install github:...`. `dist/`
  is generated at install time and gitignored, not committed.
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
  `state.event.json` (`ci.run`).
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
  datamodel-code-generator 0.66.3).

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
