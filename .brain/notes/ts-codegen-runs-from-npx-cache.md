---
slug: ts-codegen-runs-from-npx-cache
title: "json-schema-to-typescript runs only from the npx cache"
type: gotcha
status: active
created: 2026-10-27
updated: 2026-10-27
provenance:
  runs: []
  files: ["gen/ts", "gen/ts/index.ts"]
---
Run json-schema-to-typescript per schema file from gen/ts via npx; it is not installed.
It lives only in the npx cache, so invoke it once per file from inside gen/ts. It has no --version flag, so do not use that to check for it. Add the new exports to gen/ts/index.ts by hand afterwards (see cp1252-and-crlf-files).
