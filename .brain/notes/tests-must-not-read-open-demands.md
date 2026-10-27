---
slug: tests-must-not-read-open-demands
title: "Tests reading real demand files break when they are archived"
type: gotcha
status: active
created: 2026-10-27
updated: 2026-10-27
provenance:
  runs: []
  files: ["tests/validate_demand.py", "demands/archive"]
---
Never point a test at an open demands/ file; archiving moves it to demands/archive/.
Archiving demands/2026-09-14-factory-repin-interface-extraction.md broke both validate_demand.py and DemandDispatchOrderContractsTest. validate_demand.py was repointed to demands/archive/ on 2026-09-26. If a test fails on that path, reproduce it on a clean checkout before assuming you caused it.
