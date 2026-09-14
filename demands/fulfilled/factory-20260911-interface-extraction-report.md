---
demandId: factory-20260911-interface-extraction
worker: contracts
date: 2026-09-14
status: done
shipped: ["v0.25.0", "commit de6cd82 on main (schema+bindings+tests+changelog)", "D031 acceptance verified in a fresh venv from the tagged GitHub URL", "v0.24.0 (already shipped, covers criterion 3)"]
summaryRef: "demands/fulfilled/factory-20260911-interface-extraction-report.md"
---

# Fulfillment — Factory delivery/runner idempotency interface extraction

## What shipped

**Criterion 3 (approval receipts) was already done before this session** —
`contracts` v0.24.0 (2026-09-13, commit `907238d`) published
`schemas/demand-coordinator/demand.approval-receipt.json` →
`DemandApprovalReceipt`, fulfilling `demand-coordinator-20260913-contracts-
approved-evidence-receipt`. That is exactly this demand's third acceptance
criterion — "coordinate archive-independent approval receipt contracts with
demand-coordinator" — so it is reported here as already satisfied, not
redone. See `demands/fulfilled/demand-coordinator-20260913-contracts-
approved-evidence-receipt-report.md` for its own full account.

**Criteria 1 and 2 are new this session**, released as `contracts` v0.25.0
(Python binding only — commit `de6cd82`, tag `v0.25.0`):

### Criterion 1 — outcome, evidence, continuation, recovery schemas

`schemas/factory/`:
- `factory.outcome.json` → `FactoryOutcome` — Factory's own new workflow
  record (requested outcome, bounded plan, acceptance criteria, lifecycle
  phase/status, approvals). Modeled directly from `factory.domain.Intake`/
  `new_mission`, not invented ahead of it.
- `factory.evidence-receipt.json` → `FactoryEvidenceReceipt` — one immutable
  evidence observation. `provenance` is a fixed `const: "owner-attestation"`
  (spec-factory.md open question 3: this slice never machine-verifies
  CI/deployment evidence).
- `factory.continuation.json` → `FactoryContinuation` — the link an
  outcome's `source` carries back to a *terminal* legacy `app-studio`
  mission. `system` is a fixed `const: "app-studio"`. `receipts` is left an
  open map deliberately — it is app-studio's own artifact-read provenance,
  not something `contracts` should re-specify.
- `factory.recovery-checkpoint.json` → `FactoryRecoveryCheckpoint` —
  branch/commits/remaining-checks preserved across a paused or interrupted
  dispatch.

`factory.outcome.json` embeds the other two via `$ref` to their on-disk
filenames (same convention `demand.approval-receipt.json`/v0.24.0
established) — reused, not duplicated. **None of `app.mission.json` or any
other existing schema was touched**: a Factory outcome is Factory's own new
record, never an edit of app-studio's mission history (spec-factory.md §3).

### Criterion 2 — runner dispatch/transcript wire contracts

`schemas/agent-runner/`:
- `runner.dispatch-request.json` → `RunnerDispatchRequest` — the exact
  `POST /dispatch` request body (agent-runner's own `DispatchInput`).
- `runner.run-record.json` → `RunnerRunRecord` — the exact returned/listed
  run record (agent-runner's own `RunRecord`). `state`'s 4-value enum
  (`launched`/`finished`/`failed`/`stopped`) matches `state.event.json`'s
  `AgentRunPayload.phase` exactly — agent-runner's own `RunState` type is a
  direct alias of it, verified by reading `src/domain/run.ts`.
- `runner.transcript-snapshot.json` → `RunnerTranscriptSnapshot` — the
  normalized `transcriptTail`/`result`/`resultTruncated` view `GET
  /runs/{id}` always serves. Deliberately does NOT extract the deeper
  structured per-event timeline (`session`/`events`/`transcriptSummary`)
  agent-runner also serves — that is dashboard/design-studio's own proven
  need, not this demand's; pulling it in would be scope creep, not the
  additive/proportional publish asked for.

**Stable operation correlation and receipt semantics** (spec-factory.md open
question 2: "agent-runner has no idempotency-key contract") are documented
in both runner schemas' descriptions rather than modeled as a new field.
agent-runner's real wire has no dedicated idempotency key today, so none was
invented. The real, already-proven convention
(`factory.service.dispatch`/`reconcile`) is transcribed as-is: a caller
mints its own operation token and embeds it as literally the first line of
`prompt`; it is later re-identified by an exact `RunnerRunRecord.id` match
or by `prompt` starting with `"<token>\n"`; zero or ambiguous matches both
mean "still uncertain, do not resend" — never "assume failure" or "assume
success." `RunnerRunRecord` (plus the transcript snapshot) is documented as
the only authoritative receipt of what a dispatch actually did; an HTTP
error or an absent record is documented as never proving non-dispatch.

### Verification performed, not assumed

- `python tests/run_all.py` — green. Two new validators added
  (`tests/validate_factory.py`, `tests/validate_runner.py`), following
  `validate_demand.py`'s direct-JSON-Schema-validation pattern with
  good/bad fixtures per schema; `validate_factory.py` resolves
  `factory.outcome.json`'s cross-file `$ref`s the same way
  `validate_demand.py` resolves `demand.approval-receipt.json`'s.
- Python round-trip: `pip install -e ./gen/python`,
  `model_dump_json()`/`model_validate_json()` on a `FactoryOutcome` (with
  its embedded `checkpoint`), construction of `RunnerDispatchRequest`/
  `RunnerRunRecord`/`RunnerTranscriptSnapshot`.
- **D031 acceptance test actually run**, per the standing invariant in
  `CLAUDE.md`: fresh venv, `pip install "git+https://github.com/elmoul/
  contracts.git@v0.25.0#subdirectory=gen/python"` against the real tagged
  URL (not the local working tree), then the same import/round-trip check —
  passed.
- Discovered and documented in `DEPLOYMENT.md`: `factory.outcome.json`'s
  cross-file `$ref`s require `datamodel-codegen`'s batch mode
  (`--input schemas/factory --output <dir>`, not a single-file
  `--input`/`--output` pair) — a single-file invocation either errors
  ("Modular references require an output directory, not a file") or
  silently inlines the referenced schemas as duplicate classes instead of
  importing them. Verified both ways this session, not assumed.

Tag `v0.25.0` pushed to `main`. `CHANGELOG.md` updated.

## What the origin must know

- Re-pin `factory` to `contracts` `v0.25.0` (Python only — Java/TS
  untouched, same precedent as v0.6.1/v0.24.0).
- These are **contract shapes only** — `contracts` implements no business
  logic. Factory's own SQLite records, `factory.domain` module, and
  `factory.service` dispatch/reconcile logic are unaffected until Factory's
  own session re-pins and adopts.
- `factory.outcome.json`'s `phase` field is intentionally free text, not an
  enum — the ordered phase sequence is `kind`-specific and lives in
  Factory's own `WORKFLOWS` dict, not duplicated here.
- `runner.run-record.json`'s `state` enum is the real 4 values
  (`launched`/`finished`/`failed`/`stopped`) — note this is a *smaller* set
  than the `ACTIVE_RUNS`/`TERMINAL_RUNS` constants in Factory's own
  `factory.domain` (which include `queued`/`starting`/`running`/`stopping`/
  `timed-out`, values agent-runner's real wire never actually emits per
  `runManager.ts`'s `classifyOutcome`). If Factory's own re-pin session
  wants to tighten those constants to match reality, that's Factory's own
  code change, not a contracts follow-up.
- The operation-correlation convention (token as `prompt`'s first line) is
  documented, not schema-enforced — `RunnerDispatchRequest.prompt` stays
  opaque free text on the wire. Factory's own `factory.service.dispatch` can
  adopt the published schemas without changing this behavior at all.
- Criterion 3's `DemandApprovalReceipt` (v0.24.0) already exists — no
  further contracts work needed there; Factory's own re-pin/adoption is
  what's outstanding on that leg (see the demand-coordinator report for
  detail, and re-pin to at least `v0.25.0` to get it plus this session's
  additions in one bump).

## Not done / caveats

- TS/Java bindings were **not** generated for any of the six new schemas —
  Factory (Python) is this demand's origin and the only named consumer;
  agent-runner (TypeScript) already has its own equivalent local types and
  is not asked to adopt the generated Python bindings, only to have its
  wire shape now exist as a reviewable, versioned contract. If a
  non-Python consumer emerges, that's a follow-up release, not a gap here.
- Only the normalized `transcriptTail`/`result`/`resultTruncated` view is
  published — agent-runner's deeper structured per-event transcript
  taxonomy (background tasks, tool-call correlation, thinking events, etc.)
  used by dashboard/design-studio is out of scope for this demand and was
  not extracted.
- The idempotency-key gap spec-factory.md's open question 2 names is
  documented, not closed: agent-runner still has no dedicated correlation
  field on the wire. This release makes the existing workaround convention
  reviewable and versioned; it does not change agent-runner's own API.
- This release defines contract shape only, per `contracts`' own
  boundaries — it does not implement any of Factory's storage, dispatch, or
  reconciliation logic.
