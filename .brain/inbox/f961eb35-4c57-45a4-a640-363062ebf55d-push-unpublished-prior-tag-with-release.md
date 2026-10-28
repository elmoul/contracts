---
slug: push-unpublished-prior-tag-with-release
title: "Push an unpublished prior tag in the same push as the new release"
type: procedure
created: 2026-10-28
updated: 2026-10-28
provenance:
  runs: ["f961eb35-4c57-45a4-a640-363062ebf55d"]
  files: ["CHANGELOG.md"]
source: harvest
repeat_of: verify-release-tag-on-origin
---
Before tagging a release, compare local tags with origin (git tag vs git ls-remote --tags origin). A previous release (e.g. v0.66.0) may exist only as a local tag. If so, push it together with the new tag in the same git push so the new release builds on a published base. Do not re-point it; a tag may only be moved until its origin demand is pushed.
