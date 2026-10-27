---
slug: pyyaml-parses-frontmatter-dates
title: "PyYAML turns frontmatter dates into datetime.date"
type: gotcha
status: active
created: 2026-10-27
updated: 2026-10-27
provenance:
  runs: []
  files: ["tests/validate_demand.py", "demands"]
---
Coerce date values to strings before jsonschema-validating demand or report frontmatter.
yaml.safe_load parses an unquoted 'date: 2026-09-27' into a datetime.date. A naive check then reports 'not of type string' for every demand and fulfillment file.
