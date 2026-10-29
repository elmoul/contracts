# Proposed spec delta: contracts

Spec `../platform-vault/spec-contracts.md`, drafted 2026-10-29 against `db95c956b273` from 1 drift item(s) in `.brain/spec/drift.json`.
Contract-zone edits only; the vault session (or the app's next Factory task) applies them, the owner approves.

## 1. front matter: replace
Drift: fact-mismatch-b4a6b6b2
- decisions: [D002, D007, D009, D010, D015, D022, D029]
+ decisions: [D002, D007, D009, D010, D014, D015, D022, D023, D029, D031, D042, D043, D054, D115, D140, D143, D144, D145, D146]
Reason: The front matter was not in the contract zone supplied, so `before` is rebuilt from the drift item's list and may not match the file's exact formatting. The edit adds the twelve decisions the spec lists and the body cites (D014, D023, D031, D042, D043, D054, D115, D140, D143, D144, D145, D146) but the front matter omits. D115, D140, D143, D144, D145 and D146 are in the spec's list but the drift item did not say they were missing from HEXAGON.md, so they are included on the spec's authority.
