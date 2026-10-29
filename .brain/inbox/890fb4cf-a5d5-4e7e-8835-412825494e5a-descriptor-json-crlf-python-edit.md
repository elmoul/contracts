---
slug: descriptor-json-crlf-python-edit
title: "schemas/app/descriptor.json is CRLF: normalize newlines before string-editing it"
type: gotcha
created: 2026-10-29
updated: 2026-10-29
provenance:
  runs: ["890fb4cf-a5d5-4e7e-8835-412825494e5a"]
  files: ["schemas/app/descriptor.json"]
source: harvest
repeat_of: cp1252-and-crlf-files
---
schemas/app/descriptor.json uses CRLF line endings. A Python string replace that inserts LF-only text, or that writes without newline='', leaves mixed endings that put a raw control character inside a JSON string, so json.load fails with 'Invalid control character'. Detect the newline style, edit on LF-normalized text, and write back with the original newline. Check json.load afterwards. Git also warns 'LF will be replaced by CRLF' on this file; that warning is harmless.
