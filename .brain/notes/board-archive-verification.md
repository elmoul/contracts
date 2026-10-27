---
slug: board-archive-verification
title: "Check an archive on /board via data.demands, not the body"
type: gotcha
status: active
created: 2026-10-27
updated: 2026-10-27
provenance:
  runs: []
  files: ["demands/archive", "demands/fulfilled"]
---
An archived demand leaves data.demands but its fulfillments[] entry stays on GET /board.
A substring search of the body still finds the demandId twice: once in fulfillments[].demandId and once in the fulfilled/<id>-report.md path. That is expected. The body's only top-level key is data, and schema errors are under data.errors. On Windows, read the /board JSON as UTF-8.
