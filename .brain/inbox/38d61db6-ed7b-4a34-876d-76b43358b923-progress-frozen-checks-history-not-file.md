---
slug: progress-frozen-checks-history-not-file
title: "progress-frozen validator fails on history; restoring PROGRESS.md does not clear it"
type: gotcha
created: 2026-10-28
updated: 2026-10-28
provenance:
  runs: ["38d61db6-ed7b-4a34-876d-76b43358b923"]
  files: ["PROGRESS.md"]
source: harvest
repeat_of: null
---
The conventions validator v2 check `progress-frozen` inspects commit history, not the current file. If a commit after the freeze commit (803eb1b) touched PROGRESS.md below its freeze header (here 0c6a261), the check keeps failing even after a commit restores PROGRESS.md byte-identical to the freeze commit. Do not spend time on restoring commits. The only fixes are rewriting history on main or changing the validator in the conventions repo, and both need an owner or architect decision. Write a fulfillment report with status: blocked that includes the validator output, and do not push.
