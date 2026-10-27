---
slug: ts-codegen-ref-description-dup
title: "A description beside a $ref makes json2ts emit a *1 type"
type: gotcha
status: active
created: 2026-10-27
updated: 2026-10-27
provenance:
  runs: []
  files: ["schemas", "gen/ts"]
---
A description next to a $ref makes json-schema-to-typescript emit a duplicate *1 type.
Put the description on the referenced $def instead. Before committing, check the generated .ts for type names ending in 1.
