---
slug: check-tags-before-versioning
title: "Run git tag before choosing a release version"
type: gotcha
status: active
created: 2026-10-27
updated: 2026-10-27
provenance:
  runs: []
  files: ["gen/java/pom.xml", "gen/ts/package.json", "gen/python/pyproject.toml"]
---
Run git tag before stamping a version; a demand's 'vX or later' never allows reusing a tag.
A partial tree once stamped 0.33.0, which was already tagged. Pick the next free version and set it in all three version files (see one-repo-wide-version).
