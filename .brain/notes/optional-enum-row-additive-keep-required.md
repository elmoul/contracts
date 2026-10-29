---
slug: optional-enum-row-additive-keep-required
title: "Add brain.functions rows as optional"
type: procedure
status: active
created: 2026-10-29
updated: 2026-10-29
provenance:
  runs: ["f961eb35-4c57-45a4-a640-363062ebf55d"]
---
Add new brain.functions rows as optional, leave required unchanged
When extending schemas/agent-runner/brain.functions.json with new function names (e.g. spec-sync, spec-seed), add them as optional properties reusing the existing row shape (model, effort, reason) and leave required as triage, harvest, curate, seed. Older four-row tables still validate, so no consumer demands are needed. Update TS source and dist (gen/ts/brain-functions.ts, gen/ts/dist/brain-functions.d.ts), Python (hyphenated aliases for snake_case members) and tests/validate_brain.py. Java has no brain.functions binding, so it only gets the version bump. brain.settings lists functions separately and is not extended.
