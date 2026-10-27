---
slug: one-repo-wide-version
title: "One repo-wide version, not one per schema"
type: fact
status: active
created: 2026-10-27
updated: 2026-10-27
provenance:
  runs: []
  files: ["gen/java/pom.xml", "gen/ts/package.json", "gen/python/pyproject.toml", "README.md"]
---
The repo has one version across all schemas, kept in three version files.
gen/java/pom.xml, gen/ts/package.json and gen/python/pyproject.toml must agree (0.62.0 on 2026-10-26). HEXAGON.md and spec-contracts.md claim per-contract versioning; the files win. An additive change is a minor bump. A removal, a rename or a new required field is a major bump (README.md).
