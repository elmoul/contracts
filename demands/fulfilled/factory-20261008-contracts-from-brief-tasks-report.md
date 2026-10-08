---
demandId: factory-20261008-contracts-from-brief-tasks
worker: contracts
date: 2026-10-08
status: done
shipped: ["tag v0.53.0 (local, not pushed)", "commit c5df79f on main", "schemas/youtrack/planner.brief-project-request.json (optional scope)", "schemas/youtrack/planner.brief-project-response.json (optional scope and tasks)", "TypeScript and Python bindings regenerated, Java regenerates at build", "two synthetic exchanges in tests/fixtures/youtrack-brief/captured-exchanges.json", "tests/validate_planner_brief.py extended", "worktree ../contracts-worktrees/v0.53.0"]
---

# Fulfilment - scope and tasks in the planner's from-brief shape

Checked first: neither `scope` nor `tasks` existed in the request or response schemas (v0.52.0), so the work was done, not no-opped.

## What shipped

Tag `v0.53.0` on commit `c5df79f` (additive minor). Local only: nothing was pushed, neither commit nor tag. The pinned worktree `../contracts-worktrees/v0.53.0` exists.

- **Request `scope`**: optional enum `epics`, `tasks`, `all`; not in `required`, so omitted validates and means `epics`. The description gives the three meanings and the idempotency-key derivation from brief hash, project key and scope.
- **Response `scope` and `tasks`**: both optional, so old answers validate. `scope` is the scope the planner ran (absent reads as `epics`). `tasks` has `created`, `alreadyPresent`, `failed`. Items carry `key` (the task's own outcome key), `epicKey` (parent), `title`; created and alreadyPresent items also `id` and `url`; failed items `code` and `reason`. All required, `additionalProperties: false`. The closed `failed.code` enum is the existing six (including `not_attempted`, e.g. a task whose epic failed); no code was added. `status` `partial` now also covers failed tasks.
- **Scope `epics` and `tasks`**: stated in the description: the planner omits `tasks`; an empty object with three empty lists is also valid.
- Unchanged: the ten section keys, every limit, `additionalProperties: false` elsewhere. No secret-capable property was added.
- Bindings: TypeScript (`dist/` rebuilt) and Python regenerated; datamodel-codegen emitted bare `Enum` again, restored to `StrEnum` by hand per DEPLOYMENT.md. Versions 0.53.0 in pom.xml, package.json, pyproject.toml. CHANGELOG has a v0.53.0 entry.
- Fixtures: two **synthetic** exchanges (stated in each `synthetic` field) built from captured exchange #0: scope `all` with four created tasks under two of the three epics; scope `tasks` replayed (`replayed` true, project not new, epics and tasks all `alreadyPresent`).
- Tests (`tests/validate_planner_brief.py`): old request and old answer (no scope, no tasks) validate; scope `all` and `tasks` exchanges validate; scope `epics` with an empty tasks object validates; unknown scope values (`everything`, empty, `EPICS`, null, number, array) are refused on request and an unknown response scope is refused; a task item without `epicKey` (created, alreadyPresent, failed), without `key`, without `id`, with an extra property, a failed task with an unknown code, and an extra property on `tasks` are refused; the idempotency-key rule per scope is checked.

## Verification

- `python tests/run_all.py`: All validators passed (includes the state-event sync check).
- `mvn -B -f gen/java/pom.xml test`: exit 0. `cd gen/ts && npx tsc --noEmit`: clean.
- Python round-trip of the old, scope `all` and scope `tasks` payloads through the generated models.
- Fresh venv install from the local tag (`git+file://...@v0.53.0#subdirectory=gen/python`) exposes `scope` and `tasks` on the response and the `Scope` enum.

## Decisions the planner and Factory should confirm

- **Idempotency key**: the demand says it derives from brief hash, project key and scope but not how. I kept `sha256(<hash>:<key>)` unchanged for `epics` (so existing stored results still match) and used `<hash>:<key>:<scope>` for `tasks` and `all`. This is stated in the schema descriptions; if the planner wants another form, it needs a contracts patch.
- `tasks` absent (not empty) when the scope is `epics`; the schema accepts both.
- Task items do not carry a position or description; none was asked for.

## Not done / caveats

- Nothing pushed, so the D031 acceptance install from the real remote tag URL was not run; the local-tag install is the closest check. Repeat it after the owner pushes.
- The D043 release-notification demand to Factory ("close your consuming leg") and the planner adoption are not raised: raising is a push, which this run forbids.
- Java: no test asserts the new fields in the generated classes; they come from jsonschema2pojo at build (build and tests passed).
