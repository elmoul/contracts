---
slug: validator-needs-sibling-platform-vault
title: "spec-file-exists and status-coherence are unverified without a sibling platform-vault"
type: fact
created: 2026-10-28
updated: 2026-10-28
provenance:
  runs: ["38d61db6-ed7b-4a34-876d-76b43358b923"]
source: harvest
repeat_of: null
---
The conventions validator reports `spec-file-exists` and `status-coherence` as unverified (not failed) when `platform-vault` is not checked out as a sibling directory of this repo. A summary such as '18 checks, 1 failed, 2 unverified' is expected in a standalone checkout. Check out platform-vault next to contracts before running the validator if you need those two checks to be verified.
