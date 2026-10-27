---
slug: schema-for-takes-file-name
title: "schema_for() takes the schema file name, not the bare name"
type: gotcha
status: active
created: 2026-10-27
updated: 2026-10-27
provenance:
  runs: []
  files: ["tests/validate_delivery.py"]
---
Call schema_for('delivery.producer-result.json') in tests/validate_delivery.py.
It takes the schema file name, including .json. Any other form raises FileNotFoundError.
