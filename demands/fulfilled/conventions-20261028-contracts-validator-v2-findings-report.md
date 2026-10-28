---
demandId: conventions-20261028-contracts-validator-v2-findings
worker: contracts
date: 2026-10-28
status: blocked
shipped: ["PROGRESS.md restored below the D143 freeze header to its content at freeze commit 803eb1b (local commit 4394970 on main, not pushed)"]
---

# Fulfilment - contracts passes conventions validator v2 (progress-frozen)

Checked first: the only failing check was `progress-frozen` (`PROGRESS.md changed below its freeze header in 0c6a261 (frozen at 803eb1b)`). Commit 0c6a261 added 6 lines after the freeze.

## Done

- `git checkout 803eb1b -- PROGRESS.md`, committed as 4394970. The file is now byte-identical to the freeze commit; nothing was added. Nothing else was touched; nothing pushed.

## Validator result after the restore (blocked)

`java -jar ../conventions/validator/target/conventions-validator-0.1.0.jar .`:

```
[FAIL       ] progress-frozen   PROGRESS.md changed below its freeze header in 0c6a261 (frozen at 803eb1b)
FAIL (18 checks, 1 failed, 2 unverified)
```

The check still fails. It reports the historical commit 0c6a261, so it appears to inspect history after the freeze commit rather than the current file content; a restoring commit cannot clear it. Clearing it would need either a history rewrite of main (not sanctioned, and it would break pushed history) or a validator change (conventions' repo) so that a file restored to freeze-commit content passes. Owner/architect decision needed. The two UNVERIFIED checks (spec-file-exists, status-coherence) are only because platform-vault is not a sibling checkout here.
