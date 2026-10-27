---
slug: retag-only-before-origin-demand
title: "A tag may be re-pointed only until its origin demand is pushed"
type: gotcha
status: active
created: 2026-10-27
updated: 2026-10-27
provenance:
  runs: []
  files: ["CHANGELOG.md"]
  decisions: ["D043"]
---
Re-point a flawed tag only while no consumer can have seen it; say so in the report.
That window closes when the origin demand is pushed. v0.35.0 was removed and re-tagged this way. After the push, fix forward with a new tag. Shipping a tag whose own docs contradict it is worse than re-pointing a tag no one has consumed.
