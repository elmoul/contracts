---
slug: closed-payloads-break-additive
title: "Additive fields break strict consumers of closed payloads"
type: gotcha
status: active
created: 2026-10-27
updated: 2026-10-27
provenance:
  runs: ["c7fa4172-5bdd-464f-a98e-8ad27fe505bc"]
  files: ["schemas", "CHANGELOG.md"]
  decisions: ["D031"]
---
A new field on a closed schema breaks old strict consumers until they re-pin.
Schemas are closed (additionalProperties false). Old bindings (extra=forbid) and strict validators reject the unknown field, so the change is additive only for producers that omit it. A consumer must re-pin the new tag before it sends the field. State that rollout order in the fulfillment report, the origin demand and CHANGELOG.md. For a list field, also say what absent means versus [].
