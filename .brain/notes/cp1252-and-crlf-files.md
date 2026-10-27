---
slug: cp1252-and-crlf-files
title: "CHANGELOG.md and gen/ts/index.ts are cp1252, index.ts is CRLF"
type: gotcha
status: active
created: 2026-10-27
updated: 2026-10-27
provenance:
  runs: []
  files: ["CHANGELOG.md", "gen/ts/index.ts"]
---
Edit CHANGELOG.md and gen/ts/index.ts as bytes (latin-1 round trip), not as UTF-8 text.
Both files contain cp1252 bytes, so read and write them with encoding='latin-1'. gen/ts/index.ts also uses CRLF line endings: keep them. Its line 1 says v0.1.0, but that comment is stale and is not the version.
