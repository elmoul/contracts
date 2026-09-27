---
id: contracts-20260927-plantpal-repin-ci-run-steps
date: 2026-09-27
from: contracts
to: [plantpal]
capability: Close the consuming leg of plantpal-20260927-contracts-ci-run-steps — optional jobId + steps[] on ci.run shipped in contracts v0.30.0
acceptance-criteria:
  - "plantpal confirms its own consuming leg: per its demand it neither produces nor consumes ci.run, so no re-pin in plantpal itself (or plantpal re-pins to v0.30.0 if that has changed)."
  - "The follow-on demands plantpal-20260927-ci-runner-ci-run-steps and plantpal-20260927-dashboard-ci-stage-view name contracts v0.30.0 as the tag to pin."
  - "The rollout order is carried into that chain: every strict consumer on the ci.run path (state-feed, dashboard) re-pins to v0.30.0 before ci-runner starts emitting jobId/steps — or plantpal explains why not."
needs-owner: false
status: open
---

# `steps[]` on `ci.run` — close the consuming leg

## What we need

`contracts` v0.30.0 shipped what `plantpal-20260927-contracts-ci-run-steps`
asked for. In `schemas/state-feed/state.event.json`, `CiRunPayload` has two new
optional fields. `jobId` is an int64. `steps` is an array of `CiRunStep`, which
has `number`, `name` and `status` (`queued|in_progress|completed`), plus optional
`conclusion` (`success|failure|cancelled|skipped`), `startedAt` and `completedAt`.
`CiRunStep` is a closed object. The Java wrapper and the Java, TS and Python
bindings carry the same fields. The step enums are also exported as named types:
`CiRunStepStatus` and `CiRunStepConclusion`.

## Why

D043: a release is not complete until the origin closes its consuming leg.
plantpal has no `ci.run` code, so its leg is the demand chain it owns
(ci-runner → dashboard).

**Rollout hazard.** Every payload is closed (`additionalProperties: false` /
pydantic `extra='forbid'`). A consumer still pinned to v0.29.0 or earlier that
validates strictly will therefore *reject* a `ci.run` that carries
`jobId`/`steps`. Old events do validate under the new schema. The reverse is not
true: new events can fail under old pins. So the order matters:
1. state-feed and dashboard re-pin.
2. Then ci-runner emits.

This is an additive release, so contracts raises no fleet-wide demands (D031/D043).
Sequencing the rollout is up to plantpal's chain.
