---
id: contracts-20261029-conventions-adopt-app-descriptor-design-block
date: 2026-10-29
from: contracts
to: [conventions]
capability: "conventions re-pins to contracts v0.70.0 and adopts the optional design block on app.descriptor"
acceptance-criteria:
  - "Closes your consuming leg of conventions-20261029-contracts-app-descriptor-design-block: contracts v0.70.0 adds an optional top-level design object to schemas/app/descriptor.json (system, version required; pack default design, surfaces, check optional). Additive: no consumer is obliged to move"
  - "Do: re-pin to v0.70.0 (D031) wherever you validate app.yaml; tell the repos that hold their own copy to re-pin before any app.yaml uses the field: factory (vendored src/factory/contract_schemas/app/descriptor.json), control-plane (generated AppDescriptor binding), launcher (hand-written validator in descriptors.js), and conventions itself (validator reads ../contracts-worktrees/<contracts.pin>/schemas/app/descriptor.json, so an app pinned below v0.70.0 will refuse design)"
needs-owner: false
status: archived
---

# Demand - conventions: adopt the app descriptor design block

## What we need
Re-pin to contracts v0.70.0 and let pilot apps add the design block to app.yaml once the consumers above have re-pinned.

## Why / what is blocked
Every older copy of the schema refuses an app.yaml carrying design (additionalProperties false).

## What we do once closed
Nothing further.

## Not in scope
Any consumer code or repin; the design pack contents.
