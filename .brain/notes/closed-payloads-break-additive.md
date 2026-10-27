---
slug: closed-payloads-break-additive
title: "Additive fields break strict consumers of closed payloads"
type: gotcha
status: active
created: 2026-10-27
updated: 2026-10-27
provenance:
  runs: []
  files: ["schemas", "CHANGELOG.md"]
  decisions: ["D031"]
---
New fields on a closed schema (additionalProperties false) break old strict consumers.
Old bindings (extra=forbid) reject events that carry the new field, so the change is additive only for producers. State the rollout order (consumers re-pin before producers emit) in the origin demand and in CHANGELOG.md.
