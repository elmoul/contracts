---
id: contracts-20260926-youtrack-repin-planner-plan-run-note
date: 2026-09-26
from: contracts
to: [youtrack]
capability: Re-pin and adopt the optional `note` on planner.plan-run published in contracts v0.29.0 for youtrack-20260926-contracts-planner-plan-run-note
acceptance-criteria:
  - "youtrack re-pins its contracts dependency (TypeScript and/or Python binding) to v0.29.0 or later."
  - "backlog-planner emits `note` on plan-run detail when a preview is empty or trimmed because existing issues already cover the request, and omits it or sends null otherwise."
  - "youtrack's conformance suite covers an empty and a trimmed preview validated against the v0.29.0 schema, or youtrack explains by when/why not."
needs-owner: false
status: archived
---

# `note` on `planner.plan-run` — close the consuming leg

## What we need

`contracts` v0.29.0 shipped what `youtrack-20260926-contracts-planner-plan-run-note`
asked for: `schemas/youtrack/planner.plan-run.json` has an optional
`note` (`string | null`, not required), and `issues`' description states an
empty array is a valid preview. TS (`note?: string | null`) and Python
(`note: str | None = None`) bindings are regenerated in the tag.

## Why

D043: a release is not complete until the origin closes its consuming leg.
Additive release — no other consumer is obliged to move (D031).
