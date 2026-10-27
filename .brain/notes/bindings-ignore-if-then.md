---
slug: bindings-ignore-if-then
title: "Generated bindings do not enforce if/then or exactly-one-of"
type: gotcha
status: active
created: 2026-10-27
updated: 2026-10-27
provenance:
  runs: []
  files: ["gen/ts", "gen/python", "CHANGELOG.md", "DEPLOYMENT.md"]
---
TS and Python bindings accept shapes the schema refuses via if/then or exactly-one-of rules.
The generators emit those fields as optional, so only validation against the JSON Schema enforces the rule. When a release adds such a rule, say so in CHANGELOG.md and make the acceptance assert that the schema REJECTS the bad shape. Checking only that the good shape passes hides the gap: v0.35.0 nearly shipped on the belief that its rules were enforced.
