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
One version covers every schema; it lives in three files that must agree.
gen/java/pom.xml, gen/ts/package.json and gen/python/pyproject.toml must always agree; read them and git tag for the current value. HEXAGON.md and spec-contracts.md claim per-contract versioning; the files win. An additive change is a minor bump. A removal, a rename or a new required field is a major bump (README.md).
