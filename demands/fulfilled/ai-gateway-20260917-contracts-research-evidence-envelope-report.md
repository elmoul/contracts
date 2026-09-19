---
demandId: ai-gateway-20260917-contracts-research-evidence-envelope
worker: contracts
date: 2026-09-19
status: done
shipped: ["v0.27.0", "commit 06f571d on main"]
---

# Fulfillment report — contracts: research evidence job envelope

`status: done` here is a claim, not a verdict — per `DEMAND_SYSTEM.md` §4,
this report is `contracts`' only output for this demand. `contracts` does
not self-certify and has not notified `ai-gateway` directly; the coordinator
assembles and delivers the summary once the owner approves.

Checked current state first: no prior session had shipped this capability —
`schemas/ai-gateway/` held only `job.yaml`, `request.yaml`, `preflight.yaml`,
`model-manifest.json` before this session, none of which cover
evidence-gathering/URL-retrieval. This is new work, not a re-report of
something already shipped.

## What shipped

New file **`schemas/ai-gateway/research.yaml`** (OpenAPI 3.1, same idiom as
`job.yaml` — a caller-generated `jobId`, async submit-then-poll, D023-style
conditional-required on failure) defines a schema pair structurally separate
from `ai.request`/`ai.job.request`/`ai.job.status`, none of which changed:

- **`POST /ai/research-jobs`** accepts `ResearchJobRequest`:
  - `jobId` (uuid, caller-generated) — same idiom as `AiJobRequest.jobId`,
    satisfies "caller-generated durable id".
  - `appId`.
  - `sources`: array (`minItems: 1`) of `SourceRequest` — `url`,
    `maxDurationMs`, `maxBytesPerSource`, all required. This is the
    "request-side fields for bounding retrieval" criterion, expressed
    per-source rather than job-wide, since a job can request multiple URLs
    with different bounds.
  - Returns `202` with a `ResearchJobStatus`.
- **`GET /ai/research-jobs/{id}`** answers with the current
  `ResearchJobStatus` by the same `jobId` — the "GET reconciliation route"
  criterion: an interrupted caller re-polls instead of guessing whether the
  (paid) retrieval already ran.
- **`ResearchJobStatus.evidence`**: array of `EvidenceItem` — `url`,
  `status: retrieved | unavailable | rejected` (required), `fetchedAt` +
  `excerpt` (present when `retrieved`), `reason` (present when not),
  `enforcedMaxDurationMs` + `enforcedMaxBytes` (echoing the bound actually
  enforced for that source, satisfying "echoed back on the response").
  **This is the structural-separation criterion**: `EvidenceItem` has no
  field for model-generated narrative text at all, so there is no shared
  field a model-invented citation could land in alongside a
  gateway-fetched one — the separation is enforced by the schema having
  nowhere else to put it, not by a naming convention a producer has to
  honor.
- `ResearchJobStatus` carries its own `ResearchJobError` (`code`/`message`)
  rather than `$ref`-ing `job.yaml`'s `JobError` — deliberate, keeps this
  pair self-contained with zero coupling to the media-generation job schema
  it is explicitly meant to stay distinct from.

All three bindings regenerated:

- **Java:** `openapi-generator-cli` 7.23.0, `--library resttemplate`, same
  flags as `request.yaml`/`job.yaml`, into `io.platform.contracts.aigateway`
  (no class-name collisions with `AiRequest`/`AiJobRequest`/etc). `mvn -B -f
  gen/java/pom.xml test` — 34 tests, 0 failures (the run's single error is
  pre-existing and unrelated — see "Not done / caveats").
- **TypeScript:** `npx openapi-typescript` → `ai-gateway-research.ts`,
  re-exported as `AiGatewayResearchPaths`/`AiGatewayResearchComponents` from
  `index.ts`. `npm run build` + `npx tsc --noEmit --strict` clean.
- **Python:** `datamodel-codegen --input-file-type openapi
  --output-model-type pydantic_v2.BaseModel --target-python-version 3.11
  --use-specialized-enum` → `platform_contracts/ai_gateway/research.py`
  (both enums came out `StrEnum` as expected); wired into
  `platform_contracts/__init__.py`. Manually round-tripped
  `ResearchJobRequest`/`ResearchJobStatus` construction and
  `model_dump_json()`.

New `tests/validate_research.py` (wired into `tests/run_all.py`), following
`validate_ai_job.py`'s pattern exactly: known-good/known-bad coverage for
both `ResearchJobRequest` (two-source submission; missing/empty `sources`;
source missing `maxBytesPerSource`) and `ResearchJobStatus` (queued/
succeeded-with-mixed-evidence/failed known-good; missing `submittedAt`;
unknown `status` enum at both job and evidence-item level; failed-with-no-
error proving the conditional-required clause). All pass.

`CHANGELOG.md` v0.27.0 entry has the full per-language detail.

## D031 acceptance — post-tag, run for real, all three languages

`v0.27.0` tagged and pushed. Full clean-install test against the actual
pushed tag, from scratch locations outside this working tree, every
language:

- **Java:** fresh `git clone --branch v0.27.0`, `mvn -B clean install
  -DskipTests` into a scratch `.m2` — `BUILD SUCCESS`. A second, independent
  scratch Maven project depending on `io.platform:contracts:0.27.0`
  constructed a `ResearchJobRequest` (two-field `SourceRequest`), a
  `ResearchJobStatus` with an `EvidenceItem`, via the no-arg-constructor +
  setter shape (`generateBuilders: false`, consistent with the rest of this
  package) — `BUILD SUCCESS`, objects printed and inspected.
- **Python:** fresh venv, `pip install
  "git+https://github.com/elmoul/contracts.git@v0.27.0#subdirectory=gen/python"`
  — installed cleanly. Constructed `ResearchJobRequest`, round-tripped
  (`model_dump_json()` → `model_validate_json()`).
- **TypeScript:** `file:`-dependency scratch project pointed at the tagged
  checkout's committed `dist/`, importing `AiGatewayResearchComponents` and
  constructing both `ResearchJobRequest` and `ResearchJobStatus` shapes —
  `npx tsc --noEmit --strict` exit 0.

All scratch clones/venvs/projects deleted after verification.

## D043 release-notification duty

Additive release, so per D043 only the origin demand is required (no
fleet-wide "adopt or explain" — that is breaking-release-only). A demand
`to: [ai-gateway]` ("re-pin and adopt v0.27.0") is raised as part of this
same session, standalone coordination commit, per `DEMAND_SYSTEM.md` §3 —
`demands/2026-09-19-ai-gateway-repin-research-evidence-envelope.md`.

## Not done / caveats

- **Pre-existing, unrelated test failure, not introduced by this session:**
  `tests/validate_demand.py` and Java's
  `DemandDispatchOrderContractsTest.demandWrittenBeforeAfterExistedStillDeserializes`
  both read a fixture at `demands/2026-09-14-factory-repin-interface-
  extraction.md`, which is no longer at that path — it was moved to
  `demands/archive/2026-09-14-factory-repin-interface-extraction.md` by a
  prior session's loop-close, and neither test was updated to look there.
  Reproduced identically against a clean `git stash` of this session's
  changes (confirmed before touching anything), so it predates this work.
  `tests/run_all.py` stops at `validate_demand.py`'s failure — every
  validator that runs before it (including the new
  `validate_research.py`) passes; every validator after it
  (`check_state_event_sync.py`) was run standalone and also passes. Left
  as-is rather than fixed: out of scope for this demand, and per this
  repo's own standing orders a `contracts` session fixes `contracts` bugs
  on request/scope, not opportunistically inside an unrelated demand.
- No Python binding gap this time (unlike v0.26.0's `after`/
  `DemandQueueEntry`) — Python was regenerated cleanly alongside Java/TS,
  since `research.yaml` has no cross-file `$ref`s or dictionary-typed
  `additionalProperties` to trip the generator.
