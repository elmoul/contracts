---
slug: verify-release-tag-on-origin
title: "A tag is released only once it is on origin"
type: gotcha
status: active
created: 2026-10-27
updated: 2026-10-29
provenance:
  runs: ["49f5fe28-87f1-4ac2-bdd5-d92426451a0f", "c7fa4172-5bdd-464f-a98e-8ad27fe505bc", "f961eb35-4c57-45a4-a640-363062ebf55d"]
---
A tag is released only once it is on origin
Consumers pin the GitHub tag (D031). Push it yourself with git push origin main vX.Y.Z, then confirm git ls-remote --tags origin | grep vX.Y.Z and that git ls-remote origin main matches HEAD. If you cannot push, report blocked, not done. On 2026-10-27 a report claimed v0.64.0 done while origin stopped at v0.63.0, so its D031 install could not have run.
Before tagging, compare git tag with git ls-remote --tags origin: a prior release (e.g. v0.66.0) may exist only locally. Push it in the same git push as the new tag; do not re-point it.
