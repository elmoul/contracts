---
demandId: conventions-20261029-contracts-app-descriptor-design-block
worker: contracts
date: 2026-10-29
status: done
shipped: ["tag v0.70.0 (local only, commit c0014dd; not pushed per the demand)", "schemas/app/descriptor.json: optional top-level design object + $defs/relativePath", "tests/fixtures/app-descriptor: 2 valid + 7 invalid design fixtures, registered in tests/validate_app_descriptor.py", "TypeScript binding (app-descriptor.ts + dist .d.ts) and Python binding (Design, RelativePath) updated; Java POJO generated at build", "versions 0.70.0 in pom.xml, package.json, pyproject.toml; CHANGELOG v0.70.0", "worktree ../contracts-worktrees/v0.70.0", "origin demand contracts-20261029-conventions-adopt-app-descriptor-design-block (written, committed locally, not pushed)"]
---

# Fulfilment - optional `design` block on app.descriptor

Checked first: not shipped (no `design` in the schema; latest tag v0.69.0).

## Acceptance criteria

1. **(a) Schema** - met. Optional top-level `design`, `additionalProperties: false`: `system` (`^[a-z][a-z0-9-]+$`, required), `version` (semver without `v`, required), `pack` (relative path, default `design`), `surfaces` (array of relative paths, unique), `check` (the shared argv def, run from the hexagon root). Relative paths use a new `$defs/relativePath` (no leading `/`, no drive letter, no `.`/`..` segment, no spaces, max 200). The regex avoids lookaheads so the Python (Rust regex) binding loads. One line added to the top description.
2. **(b) Examples and tests** - met. Valid: `valid-in-repo-design-minimal`, `valid-wrapped-design-full`. Invalid: `..` pack, absolute surface, `v` prefixed version, uppercase system, missing version, shell-string check, extra property. `python tests/run_all.py` passes; `mvn` 47 tests 0 failures; `npx tsc --noEmit` clean. TS and Python bindings were hand-edited (small additive field, per the release note) and the Python model round-trips the fixtures.
3. **(c) Release** - met locally. Additive minor v0.70.0, CHANGELOG entry, pinned worktree `../contracts-worktrees/v0.70.0`. D031 check run against that worktree (fresh venv, `pip install` of `gen/python`, import and validate `Design`); the real tag-URL install could not run because nothing was pushed.
4. **(d) Local only** - met. Committed and tagged locally; nothing pushed; no other repo edited.

## Repos that validate app.yaml against a pinned copy (found read-only)

- **factory**: vendored `src/factory/contract_schemas/app/descriptor.json` - must re-pin/refresh before any app.yaml uses `design`.
- **control-plane**: generated `io.platform.contracts.app.AppDescriptor` binding (`inventory/AppDescriptorParser.java`) - re-pin; check unknown-property handling.
- **launcher**: hand-written validator in `descriptors.js` mirroring the schema - needs code to accept `design`.
- **conventions**: `AppDescriptorValidCheck` loads `../contracts-worktrees/<contracts.pin>/schemas/app/descriptor.json`, so each app's own `contracts.pin` must be v0.70.0 or later.
- **brain-toolkit**: no schema copy found (only writes app.yaml in tests); no action seen.

## D043

Additive release, so only the origin gets a demand: `demands/2026-10-29-conventions-adopt-app-descriptor-design-block.md`, committed as its own commit on main but **not pushed** (the push is the raise; the demand said push nothing). Pending push: `git push origin main v0.70.0`, then the D031 install from the real tag.
