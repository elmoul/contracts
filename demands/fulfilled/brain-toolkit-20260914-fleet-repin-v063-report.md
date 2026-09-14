---
demandId: brain-toolkit-20260914-fleet-repin-v063
worker: contracts
date: 2026-09-14
status: done
shipped:
  - .brain/toolkit-pin updated to v0.6.3
  - CLAUDE.md documentation updated with --model flag requirement
  - Changes committed and pushed to main (commit a3bcdb7)
---

## Fulfillment Summary

Successfully re-pinned the brain-toolkit from v0.6.2 to v0.6.3, fixing the session-model-field bug where sessions incorrectly recorded `model: claude-code` regardless of the actual model.

### Changes Made

1. **Updated `.brain/toolkit-pin`**: Changed from `v0.6.2` to `v0.6.3`
2. **Updated `CLAUDE.md`**: 
   - Documented passing `--model <your-actual-model-id>` on every `session open` call
   - Updated version reference in the Pin mechanism section from v0.6.2 to v0.6.3
   - Updated adoption notice header from v0.6.2 to v0.6.3

### Verification Completed

✅ **With --model flag:** Ran `python .brain\bin\brain session open "test-pin-v0.6.3" --priority 3 --model claude-haiku-4-5-20251001`
   - Session file `.brain/sessions/2026-09-14_1559_test-pin-v0-6-3.md` correctly recorded `model: claude-haiku-4-5-20251001` (not `claude-code`)

✅ **Without --model flag:** Ran `python .brain\bin\brain session open "test-pin-no-model" --priority 2`
   - Session file `.brain/sessions/2026-09-14_1559_test-pin-no-model.md` correctly recorded `model: unknown` (not `claude-code`)
   - Tool output confirmed the fix: "recording 'unknown' rather than guessing"

### Prior State

Starting pin version: **v0.6.2** (as expected from fleet-wide 2026-07-31 sweep)

### Commit Details

- Commit hash: `a3bcdb7`
- Branch: `main`
- Message includes test verification details and co-author attribution
- Pushed to origin successfully

### Acceptance Criteria Met

- ✅ `.brain/toolkit-pin` reads v0.6.3, committed and pushed
- ✅ Pin verified by USE (not by reading): session open with --model records the actual model, not `claude-code`
- ✅ Omitted-flag path verified: without --model, session records `unknown`, not `claude-code`
- ✅ CLAUDE.md documents passing --model with actual model id on every `session open` call
- ✅ Fulfillment report documents the prior state (v0.6.2)
