---
slug: closed-schema-new-field-needs-repin
title: "New optional field on a closed schema needs consumer re-pin before use"
type: gotcha
created: 2026-10-27
updated: 2026-10-27
provenance:
  runs: ["c7fa4172-5bdd-464f-a98e-8ad27fe505bc"]
  files: ["schemas/agent-runner/brain.repo-summary.json", "CHANGELOG.md"]
source: harvest
repeat_of: closed-payloads-break-additive
---
Schemas under schemas/ are closed (additionalProperties false). Adding an optional field is additive for producers that omit it, but a consumer that starts sending the new field must first re-pin the new release tag. Older strict validators reject the unknown field. State this in the fulfillment report and CHANGELOG entry, and say what absent vs [] means for list fields.
