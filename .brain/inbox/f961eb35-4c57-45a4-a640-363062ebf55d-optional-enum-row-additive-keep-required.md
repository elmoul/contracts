---
slug: optional-enum-row-additive-keep-required
title: "Add new brain.functions rows as optional, leave required unchanged"
type: procedure
created: 2026-10-28
updated: 2026-10-28
provenance:
  runs: ["f961eb35-4c57-45a4-a640-363062ebf55d"]
  files: ["schemas/agent-runner/brain.functions.json", "gen/ts/brain-functions.ts", "gen/python/agent_runner/brain_functions.py", "tests/validate_brain.py"]
  decisions: ["D144"]
source: harvest
repeat_of: null
---
When extending schemas/agent-runner/brain.functions.json with new function names (e.g. spec-sync, spec-seed), add them as optional properties reusing the existing row shape (model, effort, reason) and leave `required` as triage, harvest, curate, seed. Older four-row tables then still validate and no consumer demands are needed. Update TS source and dist (gen/ts/brain-functions.ts, gen/ts/dist/brain-functions.d.ts), Python (hyphenated aliases for snake_case members) and tests/validate_brain.py. Java has no brain.functions binding, so it only gets the version bump. brain.settings lists functions separately and is not extended by this change.
