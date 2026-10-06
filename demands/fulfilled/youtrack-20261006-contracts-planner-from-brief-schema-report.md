---
demandId: youtrack-20261006-contracts-planner-from-brief-schema
worker: contracts
date: 2026-10-06
status: done
shipped: ["tag v0.49.0 (local, not pushed)", "commit 7aa6f71 on main", "schemas/youtrack/planner.brief-project-request.json", "schemas/youtrack/planner.brief-project-response.json", "schemas/youtrack/planner.brief-project-error.json", "TypeScript and Python bindings regenerated", "tests/validate_planner_brief.py with captured fixtures", "worktree ../contracts-worktrees/v0.49.0"]
---

# Fulfilment - schemas for the planner's POST /plans/from-brief

Checked first: nothing for `from-brief` existed in this repo (`schemas/youtrack/` held only the eight v0.28.0 planner schemas), so the work was done, not no-opped.

## What shipped

Tag `v0.49.0` on commit `7aa6f71` (additive minor). Local only: nothing was pushed, neither the commit nor the tag.

Three JSON Schema 2020-12 files next to the existing planner schemas, written from `brief_project.py`, its route in `api.py` and `errors.py` (read-only, youtrack working tree):

- `planner.brief-project-request.json`: projectKey, projectName, optional appName, required model, optional briefId, the approved revision record whole (`sections` exactly the ten keys, each 5 to 12000 characters; number, author, at, inputHash, metadata, inputs, questionsChanged, changed, blockers, sourceIds, hash) and the approval `{revision, hash, inputHash, at, actor}`. `additionalProperties: false` at every level.
- `planner.brief-project-response.json`: idempotencyKey, status, briefId, briefHash, project (`isNew` = created or reused), appName, stage, stateFields `{fields, readField, note, hint}`, epics `{created, alreadyPresent, failed}` with a closed `failed.code`, ownerSteps with closed `code` (add_project_key, set_state_field, add_stage_field, plus complete_stage_values which the planner also emits) and command text, plannerEditsEnv (const false), note, replayed.
- `planner.brief-project-error.json`: `{code, message, details?}` with a closed enum of the 19 codes the planner can answer this route with (422, 402, 409, 404, 502, 503; the status per code is in the description). The existing `planner.error` keeps its open `code`, unchanged.

The brief hash rule (sha256 of the record minus `hash`, sorted-key compact JSON, as Factory's digest; the planner rehashes and answers `brief_hash_mismatch`) is stated in the descriptions and not re-implemented.

Bindings: TypeScript (`gen/ts/planner-brief-project-*.ts`, index exports, `dist/` rebuilt) and Python (`gen/python/platform_contracts/youtrack/planner_brief_project_*.py`, wired in `__init__.py`, enums converted to `StrEnum` per repo convention). Versions bumped to 0.49.0 in `gen/ts/package.json` and `gen/python/pyproject.toml`. Java output is unchanged, so `gen/java/pom.xml` stays at 0.48.0 as in earlier Java-unchanged releases. CHANGELOG has a v0.49.0 entry.

## Conformance with the real payloads

I ran the planner's own suite (`planner/tests/test_brief_project.py`, 48 tests passed, whose helper `request_body`/`revision_record` builds the requests) with a throwaway plugin outside the youtrack tree that recorded every request and answer of `POST /plans/from-brief` (57 exchanges; youtrack working tree stayed clean). One exchange per distinct outcome (17) is committed in `tests/fixtures/youtrack-brief/captured-exchanges.json`. `tests/validate_planner_brief.py`, now in `tests/run_all.py`, checks:

- all 8 captured accepted requests validate against the request schema; all 8 captured 200 answers (created, replayed, reused project, partial, owner steps) validate against the response schema; all 9 captured errors validate against the error schema;
- refused: an extra property (top level, brief, approval), a section outside the ten, a missing section, a section under 5 or over 12000 characters (12000 accepted), nested metadata, a missing or malformed approval, an unknown failed code, owner step or error code, plannerEditsEnv true, and the captured brief_invalid request.

Fixture note: the stored answers omit `idempotencyKey` because the repo's gitleaks hook flags the sha256 as a key (the commit was blocked once; I did not bypass the hook). The validator rebuilds it from the documented rule `sha256(briefHash:projectKey)`, and I asserted that rule held for every captured answer before stripping it.

## Verification

- `python tests/run_all.py`: All validators passed (includes the state-event sync check).
- `mvn -B -f gen/java/pom.xml test`: exit 0.
- `cd gen/ts && npx tsc --noEmit`: clean.
- D031 clean install from the tag: fresh venv `pip install "git+file:///.../contracts@v0.49.0#subdirectory=gen/python"` imported the three models and validated all captured requests, answers and errors; fresh npm cache `npm install file:` of the pinned worktree's `gen/ts`, and a strict `tsc` check resolved the three types. The tag is not pushed, so the install used a local file URL of the tag rather than the GitHub URL; the GitHub-URL check remains for after the owner pushes.

## Caveats and next steps

- `brief.metadata` is Factory-supplied provenance of open shape; it is bounded (at most 20 scalar values, identifier-style keys, strings up to 500 characters) rather than free-form. If Factory ever puts nested data there, the schema must widen in a later release.
- The request requires every key of the revision record, whereas the planner itself only checks number and inputHash if present. This follows the demand ("record whole"); a caller sending a partial record is refused by the schema but not by today's planner.
- The planner (youtrack) and Factory adopt the pin only through their own later demands; this release obliges no consumer to move (D031).
- D043 release-notification demand to the origin (youtrack, "close your consuming leg: re-pin and adopt") is not raised: raising it means a pushed commit, which this run forbids. The owner pushes the tag and commit `7aa6f71`, then that demand is raised.
