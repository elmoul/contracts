---
slug: progress-frozen-checks-history
title: "progress-frozen validator checks history, not the file"
type: gotcha
status: active
created: 2026-10-29
updated: 2026-10-29
provenance:
  runs: ["38d61db6-ed7b-4a34-876d-76b43358b923", "ee140ae1-68f2-4c83-9680-e3e5ec75365f"]
---
progress-frozen fails on commit history; restoring PROGRESS.md does not clear it
The conventions validator v2 check progress-frozen inspects commit history after the freeze commit (803eb1b), not the current file. If a later commit touched PROGRESS.md below its freeze header, the check keeps failing even when a commit restores the file byte-identical to the freeze commit. Do not spend time on restoring commits. The only fixes are rewriting history on main or changing the validator in the conventions repo; both need an owner or architect decision. Write a fulfillment report with status: blocked that includes the validator output, and do not push.
