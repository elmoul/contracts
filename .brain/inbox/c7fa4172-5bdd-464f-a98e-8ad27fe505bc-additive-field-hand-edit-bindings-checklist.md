---
slug: additive-field-hand-edit-bindings-checklist
title: "Additive schema field: hand-edit bindings and bump three version files"
type: procedure
created: 2026-10-27
updated: 2026-10-27
provenance:
  runs: ["c7fa4172-5bdd-464f-a98e-8ad27fe505bc"]
  files: ["gen/ts/package.json", "gen/python/pyproject.toml", "gen/java/pom.xml", "tests/validate_brain.py"]
  decisions: ["D031"]
source: harvest
repeat_of: release-checklist
---
For a small additive optional field, the bindings were hand-edited instead of regenerated: gen/ts/<name>.ts and gen/ts/dist/<name>.d.ts, plus the Python module under gen/python. Bump the version in gen/ts/package.json, gen/python/pyproject.toml and gen/java/pom.xml together to the new repo-wide version. Add CHANGELOG.md entry, add cases to tests/validate_brain.py, then run python tests/run_all.py, tsc --noEmit and the Java suite. Commit, tag vX.Y.Z and create the pinned worktree ../contracts-worktrees/vX.Y.Z. Pushing (git push origin main vX.Y.Z) is left to the user, and the D031 clean-install check follows after the push.
