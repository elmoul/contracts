---
slug: validator-needs-sibling-platform-vault
title: "Validator needs sibling platform-vault for 2 checks"
type: fact
status: active
created: 2026-10-29
updated: 2026-10-29
provenance:
  runs: ["38d61db6-ed7b-4a34-876d-76b43358b923", "ee140ae1-68f2-4c83-9680-e3e5ec75365f"]
---
spec-file-exists and status-coherence are unverified without platform-vault
The conventions validator v2 reports spec-file-exists and status-coherence as unverified (not failed) when platform-vault is not checked out as a sibling directory of this repo. A summary like '18 checks, 0 failed, 2 unverified' is expected in a standalone checkout and passes. Check out platform-vault next to contracts if you need those two checks verified.
