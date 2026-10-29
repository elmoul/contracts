---
demandId: factory-20261029-contracts-registry-app-design
worker: contracts
date: 2026-10-29
status: done
shipped: ["tag v0.71.0 (commit ab77c48, pushed to origin)", "schemas/control-plane/registry.entry.json: optional app.design, closed, same shape as the descriptor design block", "tests/validate_control_plane.py: app summary without design, 2 valid and 8 invalid design cases", "TypeScript binding (registry-entry.ts + dist .d.ts) and Python binding (Design in control_plane/registry_entry.py) updated; Java POJO generated at build", "versions 0.71.0 in pom.xml, package.json, pyproject.toml; CHANGELOG v0.71.0", "worktree ../contracts-worktrees/v0.71.0", "origin demand contracts-20261029-factory-adopt-registry-app-design"]
---

# Fulfilment - optional `design` on the registry app summary

Checked first: not shipped (no `design` in registry.entry.json; latest pushed tag v0.69.0, local v0.70.0).

## Acceptance criteria

1. **Schema** - met. `app.design` added to `schemas/control-plane/registry.entry.json`: `additionalProperties: false`; `system` (`^[a-z][a-z0-9-]+$`) and `version` (semver, no `v`) required; `pack` (default `design`), `surfaces` (unique), `check` (argv, min 1) optional; same path pattern and maxLength 200 as the descriptor's `relativePath`. Described as the descriptor's design block mirrored. Entries without it stay valid.
2. **Release** - met. Additive minor v0.71.0 with Java, TypeScript and Python versions bumped together. Tests: `python tests/run_all.py` passes; `mvn` 47 tests, 0 failures; `npx tsc --noEmit` clean. TS and Python bindings were hand-edited (small additive field).
3. **D031 from the pushed tag** - met. Python: fresh venv, `pip install` from the git tag URL, `App(..., design=...)` works and `pack` defaults to `design`. TypeScript: scratch project with the tag worktree as a file dependency, strict `tsc` (bundler resolution) accepts `RegistryEntry['app'].design`. Java: `mvn install` from the tag worktree into a fresh `-Dmaven.repo.local`, `io.platform:contracts:0.71.0` installed.
4. **Follow-up** - the control-plane demand is now writable; it is Factory's to raise.

## Other things pushed

The push of `main` also published the previously local-only v0.70.0 commits (descriptor `design`, its origin demand and report); the `v0.70.0` tag was pushed too, unchanged.

## D043

Additive release, so only the origin gets a demand: `demands/2026-10-29-factory-adopt-registry-app-design.md`.
