---
session_id: 2026-09-27_1039_fulfill-demand-agent-runner-20260927-con
agent: contracts
model: claude-code
started: 2026-09-27T10:39:13+00:00
ended: 2026-09-27T10:44:46+00:00
task: "Fulfill demand agent-runner-20260927-contracts-runner-keyed-dispatch (keyed dispatch, dispatch-key lookup, observed workspace identity, producer-result routes)"
priority: 2
status: done
launch: interactive
decisions: []
changes:
  - "Published contracts v0.33.0 (commit 3d72989, tagged + pushed, pinned worktree ../contracts-worktrees/v0.33.0): optional dispatchKey on runner.dispatch-request, optional dispatchKey + nullable observed workspace on runner.run-record, new runner.dispatch-reservation with the requestHash canonicalization, docs/task-delivery.md Runner routes section, and the runner schemas' first-ever TS bindings."
  - "tests/validate_runner.py grew to 37 cases, including an executable conformance check that recomputes the documented requestHash worked example against the schema's own prose."
  - "D031 acceptance run for real: fresh venv + tagged git-URL pip install (0.33.0) and fresh-cache npm file: install of the pinned worktree, plus an INDEPENDENT TypeScript canonicalization implementation that reproduced the documented canonical bytes and digest, proving cross-language agreement."
  - "D043: raised contracts-20260927-agent-runner-repin-keyed-dispatch to agent-runner as its own coordination commit (additive release -> origin demand only, no fleet-wide)."
  - "Fulfillment report committed to demands/fulfilled/; the coordinator board shows 0 errors and the report registered under fulfillments with status done."
lessons:
  - "The runner schemas had NO TypeScript binding at all before this release -- the demand's criterion 5 ('agent-runner can repin its file: dependency to gen/ts') was unimplementable until gen/ts gained runner-*.ts. Naming gen/ts as the repin target is a hint to check the binding actually exists there before treating a release as Python-only."
  - "json-schema-to-typescript resolves a sibling $ref by INLINING a duplicate interface (delivery-producer-result.ts/DeliveryEnvironment was the precedent; runner-dispatch-reservation.ts/RunnerRunRecord repeats it). datamodel-codegen imports the real class instead. Re-export only the canonical module's copy from index.ts or the package root collides."
  - "PyYAML parses an unquoted ISO 'date: 2026-09-27' frontmatter into a datetime.date, so a naive yaml.safe_load + jsonschema check reports 'not of type string' for every demand and fulfillment file in this repo. Coerce before validating or you will chase a phantom failure."
  - "A 'modified' file in git status with an empty git diff is line-ending churn, not content -- rebuilding gen/ts/dist/ touched 20 delivery-*.js/.d.ts files that way. git checkout -- them rather than committing no-op churn."
context_missing:
  - "The 3 demands now sitting in contracts' inbox (ci-runner ci-headsha-lookup, plantpal app-deploy-receipt-and-identity, factory sync-recovery-retention) are separate work orders, deliberately not started in this session."
notes_used: []
vault_sync: none
close: confirmed
---


## Log

**10:39 Session opened** via `brain session open`.

**10:44 Session closed via `brain session close` (status: done).**
