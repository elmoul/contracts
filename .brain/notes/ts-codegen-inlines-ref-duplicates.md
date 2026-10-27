---
slug: ts-codegen-inlines-ref-duplicates
title: "json-schema-to-typescript duplicates types behind a $ref"
type: gotcha
status: active
created: 2026-10-27
updated: 2026-10-27
provenance:
  runs: []
  files: ["gen/ts/index.ts", "gen/ts/delivery-producer-result.ts", "gen/ts/runner-dispatch-reservation.ts"]
---
A sibling $ref is inlined as a duplicate interface; re-export only the canonical copy.
Precedents: delivery-producer-result.ts carries its own DeliveryEnvironment and runner-dispatch-reservation.ts its own RunnerRunRecord. If gen/ts/index.ts re-exports both copies, the package root collides. datamodel-codegen imports the real class instead, so Python is not affected.
