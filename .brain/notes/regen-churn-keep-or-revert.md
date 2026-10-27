---
slug: regen-churn-keep-or-revert
title: "Regen churn: keep openapi date lines, revert no-op dist"
type: gotcha
status: active
created: 2026-10-27
updated: 2026-10-27
provenance:
  runs: []
  files: ["gen/java", "gen/ts/dist"]
---
After a regen, use git diff --numstat, not git status, to see what really changed.
openapi-generator rewrites the @jakarta.annotation.Generated date line in every Java model. Commit that churn (v0.30.0 did); reverting it makes the next regen differ. Rebuilding gen/ts/dist/ marks about 20 files modified with an empty diff (line endings or identical content). Run git checkout -- on those files instead of committing no-op churn.
