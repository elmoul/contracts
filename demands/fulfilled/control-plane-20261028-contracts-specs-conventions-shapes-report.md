---
demandId: control-plane-20261028-contracts-specs-conventions-shapes
worker: contracts
date: 2026-10-28
status: done
shipped: ["tag v0.66.0 (annotated, local only per the demand's 'push nothing'; release commit 9e0501d on main)", "schemas/conventions: conventions.rule, conventions.finding, conventions.repo-result, conventions.run, conventions.candidate, conventions.conflict (all closed, additive)", "schemas/spec: spec.status, spec.drift-item (all closed, additive)", "brain.job and brain.job-page command enum gains spec-sync and spec-seed (no other change to either)", "TypeScript (source, dist, index exports), Python (platform_contracts.conventions, platform_contracts.spec, enums in brain_job and brain_job_page) and Java (io.platform.contracts.conventions, io.platform.contracts.spec) bindings; versions 0.66.0 on Java, TS and Python", "CHANGELOG v0.66.0", "tests/validate_conventions.py (added to run_all.py) and ConventionsContractsRoundTripTest (Java)", "worktree ../contracts-worktrees/v0.66.0"]
---

# Fulfilment - conventions compliance and living-spec shapes (D144)

Checked first: not shipped. No `schemas/conventions` or `schemas/spec` existed and the latest tag was v0.65.0 (already on origin). Additive minor **v0.66.0**.

## Acceptance criteria

1. **Read first** - met. D144 in `PLATFORM_DECISIONS.md` and `SPECS_CONVENTIONS_PROPOSAL_2026-10-27.md` sections 4.2-4.4, 5 and 6 (read-only). `SPEC_TEMPLATE.md` v2 was not opened separately; the proposal section 4.2 carries the template and the frontmatter names the demand asked for.
2. **New `schemas/conventions/`** - met. All closed (`additionalProperties: false`), every member required, nullable members are explicit `null`.
   - `conventions.rule`: `id`, `category`, `rule` (max 300), `applies_to` (any of `all`, `kind`, `side`, `lang`, `lite`, `has_file`; at least one), `source` (min 1), `amended_by`, `enforced_by` (`check:<id>` | `hook` | `external` | `none`), `severity` (fail|warn), `exceptions` (`{path, reason}`), `status`, `as_of`. `applies_to`, `amended_by` and `enforced_by` keep the catalog's snake_case.
   - `conventions.finding`: `checkId`, `ruleId` (string or null), `status` (pass|warn|fail|unverified|skipped), `message`, `file`, `line`.
   - `conventions.repo-result`: `repo`, `sha`, `result` (pass|fail|skipped), `checks` (findings).
   - `conventions.run`: `id`, `startedAt`, `finishedAt`, `validatorSource`, `catalogHash`, `trigger` (nightly|landing|manual), `repos`.
   - `conventions.candidate`: `id`, `rule`, `evidence`, `status` (proposed|accepted|rejected), `decidedAt`, `reason`.
   - `conventions.conflict`: `id`, `summary`, `status` (open|ruled), `source`.
3. **New `schemas/spec/`** - met. `spec.status`: `hexagon`, `kind` (runtime|buildtime|app|capability), `specPath`, `specVersion`, `contractAsOf`, `stateAsOf`, `verifiedAgainst`, `commitsSince`, `driftCount`, `openQuestions`, `reviewWindowDays`, `due`, `lastJob` (a `brain.job` or null), `v2`. `spec.drift-item`: `id`, `kind` (code-vs-contract|planned-now-built|fact-mismatch), `summary`, `file`, `line`, `contractSection`.
4. **Brain job command enum** - met. `spec-sync` and `spec-seed` added to `brain.job.command` and `brain.job-page.filters.command` (the only two places the schemas define it); the bindings that inline the enum (`brain-repo-summary.ts`, the Python `Command` enums) follow.
5. **Additive only** - met in shape terms: no existing member, required list or type changed. One consequence, recorded in the CHANGELOG: widening a closed enum means a consumer on an older tag that validates `brain.job` strictly rejects a `spec-sync`/`spec-seed` job, so `agent-runner` must re-pin v0.66.0 before it enqueues one.
6. **Release** - met except the push, as instructed. Annotated tag `v0.66.0` on release commit `9e0501d`, worktree `../contracts-worktrees/v0.66.0` (listed by `git worktree list`), CHANGELOG entry. **Nothing was pushed**, so `v0.66.0` is not on origin yet and the D043 origin/consumer demands were not raised (the demand says the consumer repins are separate demands). The tag and `main` still need to be pushed by whoever releases it (`git push origin main v0.66.0`), and the D031 clean install from the real tag URL is still owed after that.

## Choices the demand left open (flag if you want them otherwise)

- Rule `status` is `active|retired` (the demand lists no values).
- `specVersion` is a string (`null` for a v1 spec); v2 `spec-version: 7` is `"7"`.
- Skipped repo: `sha` is `null`. In-progress run: `finishedAt` is `null`.
- `candidate.evidence` is a non-empty list of strings.
- Java: `spec.status.lastJob` binds as `Object` (oneOf-with-null limit); `brain.job` has no Java binding. Nested rule objects carry titles (`ConventionsRuleScope`, `ConventionsRuleException`) so no generated class shadows `java.lang.Exception`.

## Verification

- `python tests/run_all.py`: all validators passed, including the new `validate_conventions.py` (positive and rejection cases for all eight schemas and the two enum values).
- `mvn -f <abs>/gen/java/pom.xml test`: 47 tests, 0 failures (3 new). `npx tsc` in `gen/ts`: clean; strict `npx tsc --noEmit` also clean in the tag worktree.
- Local stand-in for D031 only (the tag is not on origin): the Python modules import and validate from the `v0.66.0` worktree. This is **not** the real D031 acceptance.
