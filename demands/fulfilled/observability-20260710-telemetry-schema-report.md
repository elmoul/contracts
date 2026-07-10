---
demandId: observability-20260710-telemetry-schema
worker: contracts
status: done
summaryRef: demands/fulfilled/observability-20260710-telemetry-schema-report.md
---

# Fulfillment report — contracts: finalize `schemas/app/telemetry.json`

`status: done` here is a claim, not a verdict — per DEMAND_SYSTEM.md §4, this
report is `contracts`' only output for this demand. `contracts` does not
self-certify and has not notified `observability` directly; the coordinator
assembles and delivers the summary once the owner approves.

## What shipped

Branch `demand/observability-telemetry-schema`, pushed to `origin`, not
merged to `main`, no tag cut (recorded in `CHANGELOG.md` as the upcoming
`v0.10.0` — the architect tags after review/merge, per the v0.9.0/v0.9.1
precedent this repo has followed for every schema-adding session since
2026-07-10 session 17).

### Final schema shape

`schemas/app/telemetry.json` — STUB → full schema, same precedent as
v0.3.0's control-plane pair. Two parts, matching
`observability/docs/telemetry-conventions.md` exactly:

```
TelemetryLogRecord (root — the structured JSON log line every hexagon emits to stdout)
  timestamp: string, date-time, UTC          // required
  level: DEBUG | INFO | WARN | ERROR         // required
  message: string                            // required
  component_id: string                       // required — join key, see below
  appId?: string                             // optional (D009)
  traceId?: string                           // optional, reserved for future OTel correlation
  additionalProperties: false

$defs.PrometheusMetricLabels (documentation/validation only — not root-reachable)
  component_id: string                       // required
  env: local | staging | prod                // required, Prometheus-injected, hexagons never emit it
  app_id?: string                            // optional (D009)
  additionalProperties: true                 // reserved minimum, not exhaustive

$defs.MetricName (documentation/validation only — not root-reachable)
  string matching ^platform_[a-z0-9]+(_[a-z0-9]+)*_(total|seconds|bytes|info)$
```

**Design decisions** (full rationale in `CHANGELOG.md`'s `v0.10.0` entry):

- **Root is the log record, not a combined envelope.** A structured log line
  is a real JSON document every hexagon emits; a Prometheus label set is not
  — it's attached via the metrics client API (Micrometer,
  `prometheus_client`), never built as JSON. Making the root a `oneOf` or a
  nested-envelope of both would misrepresent the wire format and would have
  dragged in the `state.event.json`-style openapi-generator workaround for
  root-level unions, for no real benefit. `PrometheusMetricLabels`/
  `MetricName` are declared as `$defs`, deliberately unreferenced from root,
  documented as such in the schema's own top-level description.
- **`component_id` is the deliberate exception to this repo's camelCase
  convention** — snake_case on both the log record and the Prometheus label,
  matching Prometheus/Loki field-naming convention exactly as the origin's
  doc specifies (`appId`/`traceId` stay camelCase, also exactly as specified,
  including the origin doc's own note that this is an intentional
  inconsistency). This is the join key across Prometheus, Loki, and
  `state.event.componentId` (`schemas/state-feed/state.event.json`) that
  observability's Phase C headline bridge depends on.
- **`additionalProperties: true` on `PrometheusMetricLabels`, `false` on the
  root log record.** The label set is a reserved minimum (a metric may carry
  further labels); the log record is a closed shape, consistent with every
  other event schema in this repo (`usage.event`, `dimension.event`).

## What observability (the origin) needs to know

1. **Consume via:** pin `v0.10.0` per D031 once this branch is reviewed,
   merged, and tagged — the architect cuts the tag, not this session.
2. **Schema matches `docs/telemetry-conventions.md` with no deltas** —
   checked field-by-field against the doc during authoring (types, required/
   optional split, enum values, the naming-pattern examples, the
   `component_id` snake_case/`appId` camelCase asymmetry). Nothing in the doc
   needs to change as a result of this schema.
3. **Re-check `docker/grafana/provisioning/dashboards/json/platform-overview.json`
   and the Promtail pipeline-stage field extraction against this schema**
   (the demand's own "what we do once closed") — this report does not do
   that check; it's observability-side, against files this session never
   read.
4. **Prometheus labels are documentation/validation-only in Java/TS** — see
   the codegen note below. If observability's own tooling is Python and wants
   a typed helper for validating a label set or a metric name against the
   convention, `platform_contracts.app.telemetry.PrometheusMetricLabels` /
   `MetricName` exist as real pydantic classes (unlike Java/TS, where nothing
   is generated for them — see below, this is a genuine per-language
   difference, not a partial implementation).
5. **Phase C is now unblocked to start against a stable `component_id`
   contract** — once this release is tagged and pinned.

## Verification status

Unlike v0.8.0/v0.9.0 (no `mvn`/`java`/Python) and v0.9.1 (Java via Docker
only), this sandbox had a working Python (`py`, 3.11.9), Node/npm, **and
Docker** — no unverified leg on this release.

- **Schema itself:** verified sound with `ajv` (`ajv/dist/2020` +
  `ajv-formats`, installed to a scratch dir, matching the draft 2020-12
  declaration) against 7 fixtures (root: 1 good, 1 good-minimal, 1 bad;
  `PrometheusMetricLabels`: 2 good, 2 bad; `MetricName`: pattern check).
- **TypeScript: fully verified.** `gen/ts/telemetry.ts` generated via
  `json-schema-to-typescript@13`; only `TelemetryLogRecord` emitted (confirms
  the unreferenced-`$defs` design works as intended). `npx tsc --noEmit
  --strict` clean in `gen/ts`. `dist/` rebuilt and committed. **The actual
  D031 consumption pattern was exercised for real**: a scratch project
  outside this repo depending on `"@platform/contracts": "file:<checkout>/gen/ts"`,
  `npm install`, then a `.ts` file importing and constructing a
  `TelemetryLogRecord` passed `tsc --noEmit --strict` clean.
- **Python: fully verified.** `platform_contracts/app/telemetry.py` generated
  via `datamodel-code-generator` (pydantic v2, `--collapse-root-models`),
  wired into `__init__.py`. In a fresh scratch virtualenv (`pip install
  ./gen/python`): imported `TelemetryLogRecord`, `PrometheusMetricLabels`,
  `MetricName`, `Level`, `Env`; constructed known-good instances of each;
  confirmed a bad `level`, a bad `env`, and a malformed metric name are all
  rejected with `ValidationError`; re-ran `import platform_contracts` and the
  full `tests/run_all.py` suite (including every pre-existing validator) in
  the same venv — all pass, no regression from the `__init__.py` edit. The
  real git-URL-tag install (`pip install "git+...@v0.10.0#subdirectory=gen/python"`)
  is **not yet run** — no tag exists yet; do this once the tag is cut, per
  the standing D031 invariant.
- **Java: fully verified.** `schemas/app/telemetry.json` was added as a third
  `sourcePath` in the existing `events` `jsonschema2pojo` execution
  (`gen/java/pom.xml`), by exact analogy to the existing `usage.event.json`/
  `dimension.event.json` entries — same plugin-wide config, no per-execution
  override needed (unlike `model-manifest.json`'s `capabilities` field, this
  schema's only `additionalProperties: true` node is the unreferenced, and
  therefore ungenerated, `PrometheusMetricLabels`, so the project-wide
  `includeAdditionalProperties: false` never comes into play). Ran `docker run
  --rm -v "<repo>:/repo" -w /repo/gen/java maven:3.9-eclipse-temurin-21 mvn -B
  clean test` for real: `BUILD SUCCESS`, `Tests run: 12, Failures: 0, Errors:
  0` (unchanged — no existing test touches this schema). Inspected
  `TelemetryLogRecord.java` directly: all four required fields present
  (`timestamp: OffsetDateTime`, `level: Level` enum, `message: String`,
  `componentId: String` with `@JsonProperty("component_id")` mapping the
  snake_case wire name), optional `appId`/`traceId` present; confirmed
  `PrometheusMetricLabels`/`MetricName` generated no class (directory listing
  of `io/platform/contracts/events/` shows only `DimensionEvent.java`,
  `TelemetryLogRecord.java`, `UsageEvent.java`) — same unreferenced-`$defs`
  behavior as TypeScript. (First Docker attempt mounted only `gen/java` and
  hit a `NullPointerException` in `jsonschema2pojo`'s relative-path
  resolution — a sandbox mounting mistake, not a schema/`pom.xml` defect;
  fixed by mounting the whole repo. Noted in `CHANGELOG.md` in case a future
  session hits the same mount mistake.)
- **D031 real acceptance test (clean install from the tagged URL) not run for
  Java/Python — cannot be, until this release is tagged.** TS's
  `file:`-dependency form of the D031 pattern (the one mechanism that doesn't
  require a pushed tag) was run for real, as noted above. Java's local `mvn
  clean test` above is the pre-tag equivalent check, same as every prior
  release's practice; the real `mvn install` against a pinned tag checkout
  still needs to happen once this is tagged.

## Acceptance criteria — self-check against the demand

- [x] `contracts/schemas/app/telemetry.json` published (on this branch),
      declaring the Prometheus label set, the metric naming pattern, and the
      Loki log fields, no longer a stub.
- [x] Matches `docs/telemetry-conventions.md` with no deltas to call out.
- [x] Bindings wired for all three languages.
- [x] Tests added (`tests/validate_telemetry.py`, 14 assertions) and wired
      into `tests/run_all.py`.
- [x] CHANGELOG entry written as `v0.10.0` (tag **not** cut — architect's
      call, per instructions/precedent).
- [x] TypeScript binding compiled/tested for real, including the D031
      `file:`-dependency consumption pattern.
- [x] Python binding executed/round-tripped for real, including negative
      (rejection) cases and a full existing-suite regression check.
- [x] Java binding compiled/tested for real via Docker (`mvn clean test`,
      `BUILD SUCCESS`, generated source inspected directly).

No unverified legs on this release, unlike v0.8.0/v0.9.0/v0.9.1.

## Open questions for the architect

1. **Per-language `$defs` reachability divergence (Java/TS generate only
   `TelemetryLogRecord`; Python also generates `PrometheusMetricLabels`/
   `MetricName`)** — left as an intentional, documented difference rather
   than forced symmetry (e.g. by referencing the Prometheus `$defs` from
   root, which would misrepresent the wire format). Flagging for awareness in
   case a future consumer expects the same typed surface across all three
   languages.
2. **Docker-based Java verification (`maven:3.9-eclipse-temurin-21`, whole
   repo mounted, working dir set to `gen/java`) worked cleanly this session**
   — worth considering as the standard local verification method for future
   sessions, rather than each one re-flagging "no JDK/Maven" as a gap; the one
   thing to remember is mounting the *whole* repo, not just `gen/java`, since
   the `pom.xml` `sourcePath`s reach up to `../../schemas/`.
