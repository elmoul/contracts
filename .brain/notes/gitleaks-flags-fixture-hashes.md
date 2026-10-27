---
slug: gitleaks-flags-fixture-hashes
title: "gitleaks pre-commit hook flags sha256 idempotencyKey fixtures"
type: gotcha
status: active
created: 2026-10-27
updated: 2026-10-27
provenance:
  runs: []
  files: [".githooks/pre-commit"]
---
The gitleaks hook in .githooks/pre-commit rejects sha256 idempotencyKey values in fixtures.
Strip the flagged values and recompute them. Never bypass the hook.
