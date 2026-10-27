---
slug: release-checklist
title: "Cut a contracts release"
type: procedure
status: active
created: 2026-10-27
updated: 2026-10-27
provenance:
  runs: []
  files: ["CHANGELOG.md", "gen/java/pom.xml", "gen/ts/package.json", "gen/python/pyproject.toml", "demands"]
  decisions: ["D031", "D042", "D043", "D014"]
---
Release order: versions, CHANGELOG, tag, worktree, D031 acceptance, D043 demands.
1. Run git tag to find the next free version. Bump gen/java/pom.xml, gen/ts/package.json and gen/python/pyproject.toml.
2. Regenerate the bindings and run python tests/run_all.py plus the Java and TS checks. Add the CHANGELOG.md entry (latin-1).
3. Tag vX.Y.Z and push it. Confirm with git ls-remote --tags origin, because Python pins use the GitHub URL.
4. Run git worktree add --detach ../contracts-worktrees/vX.Y.Z vX.Y.Z and check git worktree list. Only a contracts release creates these worktrees.
5. Run d031-acceptance-per-language.
6. Raise the demands per D043 as one standalone coordination commit on main and push it. The origin always gets one. Consumers get one only on a breaking release, taken from control-plane GET /registry (D014).
The release is not done until step 6 is pushed.
