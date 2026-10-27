---
slug: release-checklist
title: "Cut a contracts release"
type: procedure
status: active
created: 2026-10-27
updated: 2026-10-27
provenance:
  runs: ["c7fa4172-5bdd-464f-a98e-8ad27fe505bc", "49f5fe28-87f1-4ac2-bdd5-d92426451a0f"]
  files: ["CHANGELOG.md", "gen/java/pom.xml", "gen/ts/package.json", "gen/python/pyproject.toml", "demands"]
  decisions: ["D031", "D042", "D043", "D014"]
---
Release order: versions, CHANGELOG, tag, push, worktree, D031, D043 demands.
1. Run git tag for the next free version. Bump gen/java/pom.xml, gen/ts/package.json and gen/python/pyproject.toml together.
2. Regenerate the bindings (a small additive field may be hand-edited in gen/ts/<name>.ts, gen/ts/dist/<name>.d.ts and the Python module). Run python tests/run_all.py plus the Java and TS checks. Add the CHANGELOG.md entry (latin-1).
3. Commit, tag vX.Y.Z and run git push origin main vX.Y.Z. Check it per verify-release-tag-on-origin.
4. Run git worktree add --detach ../contracts-worktrees/vX.Y.Z vX.Y.Z and check git worktree list.
5. Run d031-acceptance-per-language against the pushed tag.
6. Raise the demands per D043 as one standalone coordination commit on main and push it. The origin always gets one. Consumers get one only on a breaking release, taken from control-plane GET /registry (D014).
The release is not done until step 6 is pushed. If you cannot push, report blocked.
