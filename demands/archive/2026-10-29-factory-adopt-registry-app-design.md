---
id: contracts-20261029-factory-adopt-registry-app-design
date: 2026-10-29
from: contracts
to: [factory]
capability: "factory re-pins to contracts v0.71.0 and adopts the optional design block on the registry app summary"
acceptance-criteria:
  - "Closes your consuming leg of factory-20261029-contracts-registry-app-design: contracts v0.71.0 adds an optional design object to the app summary in schemas/control-plane/registry.entry.json (system, version required; pack, surfaces, check optional; same closed shape as design in schemas/app/descriptor.json). Additive: no consumer is obliged to move"
  - "Do: re-pin to v0.71.0 (D031) in the three places so the pinned RegistryEntry binding accepts a row whose app carries design. Control-plane needs its own follow-up demand to serve design in the summary; that one is yours to raise, now that the shape exists"
needs-owner: false
status: archived
---

# Demand - factory: adopt design on the registry app summary

## What we need
Re-pin to contracts v0.71.0 and raise the control-plane follow-up that copies the descriptor's design block into the served summary.

## Why / what is blocked
Until Factory re-pins, a registry row with an unknown design key is refused whole by the pinned RegistryEntry binding.

## What we do once closed
Nothing further.

## Not in scope
Any consumer code or the control-plane change itself.
