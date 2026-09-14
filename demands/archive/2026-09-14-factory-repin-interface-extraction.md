---
id: contracts-20260914-factory-repin-interface-extraction
date: 2026-09-14
from: contracts
to: [factory]
capability: Re-pin and adopt the outcome/evidence/continuation/recovery and runner dispatch/transcript contracts published for factory-20260911-interface-extraction
acceptance-criteria:
  - "factory re-pins its contracts dependency (spec-factory.md §6/§7) to contracts v0.25.0 or later (python binding)."
  - "factory confirms whether it adopts platform_contracts.factory.{factory_outcome,factory_evidence_receipt,factory_continuation,factory_recovery_checkpoint} and platform_contracts.agent_runner.{runner_dispatch_request,runner_run_record,runner_transcript_snapshot} in place of its private local dicts/pydantic models, or explains by when/why not."
  - "factory reviews the fulfillment report's note that agent-runner's real run 'state' enum is only launched/finished/failed/stopped — narrower than factory.domain's own ACTIVE_RUNS/TERMINAL_RUNS constants — and confirms whether that local constant set should be tightened to match (factory's own code change, not a contracts follow-up)."
needs-owner: false
status: archived
---

# Interface extraction — close the consuming leg

## What we need

`contracts` v0.25.0 published the six schemas demanded in
`factory-20260911-interface-extraction` criteria 1–2
(`schemas/factory/factory.outcome.json`, `factory.evidence-receipt.json`,
`factory.continuation.json`, `factory.recovery-checkpoint.json`,
`schemas/agent-runner/runner.dispatch-request.json`, `runner.run-record.json`,
`runner.transcript-snapshot.json` — Python binding only). Criterion 3
(archive-independent approval receipt) was already published in v0.24.0. Per
D043, `factory` — the origin of the demand this fulfils — needs to close its
consuming leg: re-pin to the new tag and adopt (or explain why not yet).

## Why / what's blocked

Additive release, D031 pin discipline: nothing changes for `factory` until it
explicitly re-pins. `factory`'s own local Pydantic models
(`factory.domain.Intake`/`EvidenceInput`, the `source`/`checkpoint` dicts) and
its opaque runner dispatch/reconcile calls remain unversioned duplicates of
now-published contracts until this leg closes.

## What we do once closed

Nothing further from `contracts` — this is a notification-only demand per
D043's "always to the origin" duty. Full fulfillment detail is in
`demands/fulfilled/factory-20260911-interface-extraction-report.md`.
