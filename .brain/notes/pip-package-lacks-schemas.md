---
slug: pip-package-lacks-schemas
title: "The pip-installed Python package does not bundle schemas/"
type: fact
status: active
created: 2026-10-27
updated: 2026-10-27
provenance:
  runs: []
  files: ["gen/python/pyproject.toml"]
---
pip install of gen/python ships no schemas/, so consumers cannot validate from the install.
This was reported as an owner decision on 2026-09-27 and deliberately left unfixed, because bundling wheel data is a packaging change. Check CHANGELOG.md for a later decision before relying on either state.
