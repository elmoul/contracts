---
slug: verify-release-tag-on-origin
title: "Verify a release tag is pushed with git ls-remote, not just locally"
type: procedure
created: 2026-10-27
updated: 2026-10-27
provenance:
  runs: ["49f5fe28-87f1-4ac2-bdd5-d92426451a0f"]
  decisions: ["D031"]
source: harvest
repeat_of: null
---
Consumers pin contracts by GitHub tag (D031), so a release only counts as published when the tag is on origin. A local `git tag` plus a worktree such as ../contracts-worktrees/vX.Y.Z proves nothing. To verify a 'tagged release publishes the schema/type' criterion, run `git ls-remote --tags origin | grep vX.Y.Z` and `git ls-remote origin main`, and compare origin main with HEAD. If the tag is missing or origin main is behind the release commit, the criterion fails and the D031 clean install from the tagged URL cannot have been done. A prior worker reported done with v0.64.0 tagged locally only; origin had tags only up to v0.63.0.
