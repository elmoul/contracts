---
slug: cp1252-and-crlf-files
title: "cp1252/CRLF files: CHANGELOG, index.ts, descriptor.json"
type: gotcha
status: active
created: 2026-10-27
updated: 2026-11-05
provenance:
  runs: ["890fb4cf-a5d5-4e7e-8835-412825494e5a"]
  files: ["CHANGELOG.md", "gen/ts/index.ts"]
---
CHANGELOG.md and gen/ts/index.ts are cp1252; index.ts and descriptor.json are CRLF
Edit CHANGELOG.md and gen/ts/index.ts as bytes (encoding='latin-1'), not UTF-8. gen/ts/index.ts uses CRLF: keep it. Its line 1 says v0.1.0, a stale comment, not the version.
schemas/app/descriptor.json is also CRLF. A Python replace inserting LF-only text, or writing without newline='', leaves mixed endings; a raw control character in a JSON string then makes json.load fail. Detect the newline style, edit LF-normalized text, write back with the original newline, then run json.load. Git's 'LF will be replaced by CRLF' warning is harmless.
