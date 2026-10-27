---
slug: d031-acceptance-per-language
title: "Run the D031 clean-install acceptance in all three languages"
type: procedure
status: active
created: 2026-10-27
updated: 2026-10-27
provenance:
  runs: []
  files: [".github/workflows/verify.yml", "gen/java/pom.xml", "gen/ts/package.json", "gen/python/pyproject.toml"]
  decisions: ["D031", "D042"]
---
Before calling a release done, install the tag from scratch in each language (D031).
- Python: in a fresh venv, pip install 'platform-contracts @ git+https://github.com/elmoul/contracts.git@vX.Y.Z#subdirectory=gen/python'.
- TypeScript: in a scratch project, add a file: dependency on ../contracts-worktrees/vX.Y.Z/gen/ts, install typescript locally and run tsc in strict mode.
- Java: from the tag worktree, mvn install with a fresh -Dmaven.repo.local, then build against io.platform:contracts:X.Y.Z.
Java is the easiest to skip, and it is the only proof that a pom bump installs. To validate schemas from a fresh clone, give the registry the https://platform/contracts/delivery/<file> aliases the repo's own registry() uses, or refs fail as Unresolvable. CI also runs a clean-install job when a tag is pushed.
