---
demandId: "brain-toolkit-20261027-contracts-brain-v1-schemas"
worker: "contracts"
date: "2026-10-27"
status: "done"
shipped: ["tag v0.63.0 on commit 132e71b, pushed to origin together with main (owner note of 2026-10-27 allowed pushing new contracts tags)", "eleven new closed schemas under schemas/agent-runner/ (commit 4822d85): brain.run-record, brain.run-bundle, brain.change, brain.note, brain.candidate, brain.functions, brain.cli-result, brain.repo-summary, brain.usage, brain.job, brain.job-request", "tests/validate_brain.py, 192 cases, added to tests/run_all.py (commit 4822d85)", "TypeScript (source and dist) and Python bindings for all eleven, exported from index.ts and platform_contracts/__init__.py (commit 2a9966a)", "versions 0.63.0 on Java, TypeScript and Python; CHANGELOG v0.63.0 (commit 132e71b)", "D031 acceptance from the pushed tag: fresh venv pip git URL, fresh clone plus file install into a scratch project plus strict tsc, fresh .m2 mvn install", "pinned worktree ../contracts-worktrees/v0.63.0", "D043 re-pin demand to brain-toolkit (commit 05a3627)"]
---

# Fulfilment - brain v1 wire shapes in contracts v0.63.0

Checked first: not already shipped (latest tag was v0.62.0, no `brain.*` schema existed). Additive minor **v0.63.0**.

## Precondition

Demand `brain-toolkit-20261027-vault-brain-v1-ruling` has a `done` fulfilment report (platform-vault, D143 and `spec-agent-memory-system.md` v1.0, both read in `../platform-vault`). At the time I wrote this the coordinator board still listed that demand as `open` (not yet shown as approved); I relied on the owner's note in my dispatch that the vault demand is approved and that spec v1.0 wins where it differs from the demand text. The owner should confirm that approval is recorded on the board.

## What shipped

All under `schemas/agent-runner/`, all closed (`additionalProperties: false`), `$id` `https://platform/contracts/agent-runner/brain.<name>`:

| Schema | What it is | Spec |
|---|---|---|
| `brain.run-record` | one `runs.jsonl` line: `oneOf` the run line (`dispatched` or `interactive`) and the `kind: brain-job` follow-up line a retried deferred job appends | 2.4 |
| `brain.run-bundle` | the triage input written at run exit | 4.1 |
| `brain.change` | one `changes.jsonl` line | 2.5 |
| `brain.note` | a parsed note (status `active`, `pinned` or `retired`; `slug`) | 2.2 |
| `brain.candidate` | an inbox candidate (`source`, `repeat_of`) | 2.3 |
| `brain.functions` | `config/ai-functions.json`: version plus triage, harvest, curate, seed | 3 |
| `brain.cli-result` | what every toolkit command prints with `--json`: ok, deferred, uncertain, error, model, effort, tokens, writes, details | owner note |
| `brain.repo-summary` | an element of `GET /brain/repos` | 9 |
| `brain.usage` | `GET /brain/usage`: ceiling and tokens per day | 9 |
| `brain.job` | a queue entry, referenced by `brain.repo-summary.lastJob` | demand and 7 |
| `brain.job-request` | optional `{model, effort}` body of curate, seed and migrate | 9 |

Commits (as `git log` prints them): `4822d85` schemas and tests, `2a9966a` bindings, `132e71b` release (versions and CHANGELOG, tagged `v0.63.0`), `05a3627` the D043 demand to brain-toolkit. Pinned worktree `../contracts-worktrees/v0.63.0` exists. `main` and the tag `v0.63.0` were pushed to origin (the owner's note for this run allowed it, which overrides the general "do not push" rule); the report and archive commits after `05a3627` are pushed with `main` as well.

Verification: `python tests/run_all.py` passes (including the new `validate_brain.py`, 192 cases); `mvn -f gen/java/pom.xml test` passes; `npx tsc --noEmit` is clean. D031 acceptance run from the pushed tag, in clean environments: `pip install "git+https://github.com/elmoul/contracts.git@v0.63.0#subdirectory=gen/python"` into a new venv (version 0.63.0, `BrainCliResult` JSON round trip equal); `git clone --branch v0.63.0` plus `npm install` of `gen/ts` into a scratch project, then a strict `tsc --noEmit` of a file importing the new types from `@platform/contracts`; `mvn install` of the clone into a new empty `.m2` (artifact `io.platform:contracts:0.63.0`).

## Where I followed spec v1.0 (or the owner's note) over the demand text

- `brain.functions` member is `reason`, not `why`.
- `brain.cli-result` has the owner-note member list (`tokens` as one integer); the demand's `command`, `deferredReason`, `tokensIn`, `tokensOut` are not in it. Deferral detail goes in `details`.
- `brain.repo-summary.migrated` is a boolean (spec: "migrated yes/no"), not `v0.6 | v1`. The spec's "last run" is `lastRun`, "deferred jobs" is `deferredJobs`; the demand's `lastJob` is kept.
- `brain.run-record` is the spec's `runs.jsonl` line (`runId`, `at`, `triage`, `brainTokens`...), replacing the demand's `brain.run-entry`.
- `brain.job-request` has no `command` (the route names it, spec section 9).
- `brain.job` and `brain.job-request` were kept although the owner note said to drop them unless agent-runner needs them: the open agent-runner demand (`brain-toolkit-20261027-agent-runner-brain-v1-jobs`) serves `GET /brain/jobs` and the curate, seed and migrate presses with them, and `lastJob` needs a job shape. `brain.note-action` is dropped, as told: pin, unpin and retire are URLs with no body.
- `brain.note`/`brain.candidate` front matter keeps the spec's spellings (`slug`, `repeat_of`).

## What the origin must know

- Shapes the spec leaves open that I had to choose (flagged so the toolkit or the owner can object): `brain.run-bundle.transcriptPath` is `string | null` (null for an interactive close); `model`/`effort`/`runtime` are optional strings on run lines and bundles (absent means not reported); `brain.change.slug` is `null` for `op: brief`; `brain.candidate.id` is the inbox file stem and `status` is optional on it; `brain.note.raw` is optional (single-note route); `brain.cli-result.effort` and `brain.functions` effort use the closed vocabulary `low|medium|high|xhigh` (run lines and bundles keep a free string, since they record what ran); note dates are `YYYY-MM-DD`; the retry line's `result` is a `brain.cli-result`; `brain.usage.ceiling` is nullable. The spec gives no shape for a re-seed confirmation, so none is published.
- The release is additive and the shapes are closed: pin v0.63.0 BEFORE producing or serving them. brain-toolkit has the re-pin demand (`contracts-20261027-brain-toolkit-repin-brain-v1-schemas`); agent-runner and dashboard re-pin through the demands brain-toolkit already holds with them.

## Not done / caveats

- The `if/then` couplings of `brain.cli-result` (ok excludes deferred, uncertain and error; a plain failure needs an error) are enforced by the schema only; the generators do not emit them (documented in the schema and CHANGELOG, with test cases).
- TypeScript: `brain-run-record.ts`, `brain-job.ts`, `brain-repo-summary.ts` inline copies of `BrainCliResult`/`BrainJob`, as `runner-dispatch-reservation.ts` does; the owning modules are the canonical exports. Python: `BrainRunRecord` is a `RootModel` over `BrainRunRecord1 | BrainRunRecord2`; the generator emitted plain `Enum`, which I rewrote to `StrEnum` by hand per the repo convention.
- No Java model for these shapes (agent-runner's run shapes have none either); only the Java version moved.
- The coordinator's approval of the vault precondition was not visible on the board (see Precondition).
