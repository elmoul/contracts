---
demandId: brain-toolkit-20261027-contracts-brain-settings-stats
worker: contracts
date: 2026-10-27
status: done
shipped: ["tag v0.65.0 pushed to origin (release commit 04664e0, on main with d9ce60a and 8dd70ff)", "schemas/agent-runner: brain.settings, brain.settings-update, brain.settings-audit-entry, brain.stats, brain.job-page (all closed, additive; no existing schema changed)", "TypeScript (source, dist, index exports) and Python (modules, __init__) bindings; versions 0.65.0 on Java, TS and Python", "CHANGELOG v0.65.0", "tests/validate_brain.py extended to 16 schemas (5 new, known-good and rejection cases)", "worktree ../contracts-worktrees/v0.65.0", "origin demand contracts-20261027-brain-toolkit-repin-brain-settings-stats raised and pushed (commit 36b3eca)"]
---

# Fulfilment - brain settings, statistics and job page shapes

Checked first: not shipped (latest tag was v0.64.0; no `brain.settings`/`brain.stats`/`brain.job-page` anywhere). Additive minor **v0.65.0**.

## Acceptance criteria

1. **Precondition** - met. The vault demand `brain-toolkit-20261027-vault-brain-console-settings` is fulfilled and approved (owner session note; D143 addendum 2026-10-27 in `PLATFORM_DECISIONS.md`, spec-agent-memory-system.md sections 3, 9 and A.1 read). The existing `brain.*` schemas (v0.63.0/v0.64.0) were read first.
2. **Additive schemas** - met.
   - `brain.settings`: per function (`triage`, `harvest`, `curate`, `seed`) effective `model` and `effort` with the shipped `default` beside them; `triageOnRunExit`, `autoCurate`; `updatedAt`, `updatedBy` (null while never saved); optional `audit` (the spec's `GET /brain/settings` returns the audit trail, so it is carried as an optional list rather than a second route shape).
   - `brain.settings-update`: the editable members only, all optional, at least one present; `null` on a function member resets it to the shipped default. Actor and time are server-side.
   - `brain.settings-audit-entry`: `at`, `actor`, `field` (restricted to the editable member paths), `from`, `to`.
   - `brain.stats`: `generatedAt`, `windowDays`, `totals` (repos, migrated, notes, pinned, inbox, briefsOverBudget, briefsStale, runsTriaged, lessonsFound, repeatIncidents, curations), `jobs.byState` (queued/running/done/deferred/failed, so the deferred and failed counts are `byState.deferred` and `byState.failed`), `tokens` (the `brain.usage` shape: tokens per day against the ceiling), and a per-repo `repos` row.
   - `brain.job-page`: `items` (`brain.job`), `total`, `page`, `pageSize`, `filters` (`repo`, `command`, `state`, `from`, `to`, each null when unused).
3. **Minor release tag pushed** - met. `v0.65.0` is on origin (`git ls-remote --tags origin` shows `04664e035fa98d1a57b162b88a0b5bdaa90b9999`). The owner session note allowed pushing main and the new tag, which I did; nothing else was pushed. The older local-only tag v0.64.0 was not pushed by this run.
4. **Bindings regenerated** - met. Python via datamodel-codegen 0.68.1 (directory mode, StrEnum, named `$defs` so no class got a numbered name; existing modules untouched); TypeScript via json-schema-to-typescript, `dist` rebuilt, only canonical copies of types exported from `index.ts`. Java has no per-schema bindings; its version moved.
5. **CHANGELOG** - met (v0.65.0 entry).

## Verification

- `python tests/run_all.py`: all validators passed.
- `npx tsc --noEmit` in `gen/ts`: clean. `mvn -f <abs>/gen/java/pom.xml test`: 44 tests, 0 failures.
- D031 clean install from the real tag: Python, fresh venv from `git+https://github.com/elmoul/contracts.git@v0.65.0#subdirectory=gen/python`, imported the five new modules and validated a `BrainJobPage`; TypeScript, scratch project with a `file:` dependency on the tag worktree, strict `tsc` compiled imports of the five new types; Java, `mvn install` from the tag worktree into a fresh `-Dmaven.repo.local` produced `io.platform:contracts:0.65.0`.

## Rollout

The schemas are closed and new, so no existing consumer is affected. `agent-runner` and `dashboard` re-pin v0.65.0 deliberately (D031). Additive release: only the origin demand was raised (D043), no fleet-wide demand.
