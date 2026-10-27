---
slug: npx-tsc-is-a-squatter
title: "npx tsc resolves to a squatter package"
type: gotcha
status: active
created: 2026-10-27
updated: 2026-10-27
provenance:
  runs: []
  files: ["gen/ts/package.json"]
  decisions: ["D031"]
---
Never run npx tsc in a scratch project; install typescript there and use its tsc.
In a scratch project, npx resolves 'tsc' to an unrelated squatter package, and the acceptance fails for no real reason. Inside gen/ts, npm ci installs typescript first, so npx tsc --noEmit is safe there.
