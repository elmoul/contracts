---
slug: progress-md-frozen-by-validator
title: "Conventions validator v2 freezes PROGRESS.md at its freeze commit"
type: gotcha
created: 2026-10-28
updated: 2026-10-28
provenance:
  runs: ["ee140ae1-68f2-4c83-9680-e3e5ec75365f"]
  files: ["PROGRESS.md"]
source: harvest
repeat_of: null
---
The conventions validator v2 check `progress-frozen` compares PROGRESS.md to its content at the freeze commit (here 803eb1b). Any later commit that changes it fails the check, even if that commit was later reverted. The fix is to restore PROGRESS.md to the freeze-commit content (commit 4394970 did this), not to edit it further. Without a sibling `platform-vault` checkout, `spec-file-exists` and `status-coherence` report as unverified. That is expected and does not fail the run (PASS with 18 checks, 0 failed, 2 unverified).
