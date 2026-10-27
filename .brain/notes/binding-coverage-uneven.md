---
slug: binding-coverage-uneven
title: "Not every schema has a binding in every language"
type: fact
status: active
created: 2026-10-27
updated: 2026-10-27
provenance:
  runs: []
  files: ["gen/java", "gen/ts", "gen/python"]
---
Check each gen/ language actually has a binding for the schema before scoping a release.
The runner schemas had no TypeScript binding until a demand needed gen/ts/runner-*.ts. As of 2026-10-26, Java still has no binding for the delivery, factory or youtrack planner schemas, nor for runner dispatch, reservation and run-record. A demand that names a language's binding as its re-pin target may mean you have to add that binding.
