---
demandId: agent-runner-20261026-contracts-runner-run-record-fallback-segments
worker: contracts
date: 2026-10-26
status: done
shipped: ["tag v0.62.0 on commit 3009936 (local; the owner pushes tags)", "pinned worktree ../contracts-worktrees/v0.62.0", "schemas/agent-runner/runner.run-record.json: optional fallback and optional usageSegments (required list and closed shape unchanged)", "TypeScript bindings runner-run-record.ts / runner-dispatch-reservation.ts and dist/, exporting RunnerRunFallback and RunnerUsageSegment", "Python binding runner_run_record.py (additive; generator enum rename restored by hand)", "versions 0.62.0 on Java, TypeScript and Python", "CHANGELOG v0.62.0", "21 new cases in tests/validate_runner.py plus structural assertions", "D031 acceptance: clean consumer install from the pinned worktree compiled against the new types"]
summaryRef: "commit 3009936 on main (v0.62.0)"
---

# Fulfilment - D142 fallback and per-provider usage segments on runner.run-record

Checked first: **not shipped**. The latest tag was v0.61.0 and
`runner.run-record.json` had neither `fallback` nor `usageSegments`. A prior
dispatch session for this same demand had failed two seconds after opening
without touching the tree, so this session did the work rather than re-reporting
it. Additive minor **v0.62.0**.

## Acceptance criteria

1. **Optional `fallback`** - met. Closed object, required `from`, `to`, `reason`,
   `sessionId`, `continued`; `reason` is the closed enum `session-limit |
   weekly-limit`; `from`/`to` are the runtime profile names (`claude` ->
   `claude-api`). Absent (not `null`) on every ordinary run.
2. **Optional `usageSegments`** - met. Array (min 1) of closed
   `{ provider, model?, tokensIn, tokensOut }`; present only on a fallback run,
   one entry per provider segment. `dependentRequired` makes `usageSegments`
   without `fallback` invalid. A failed fallback (`continued: false`) carries the
   subscription segment only.
3. **Additive only** - met. The `required` list is byte-for-byte unchanged,
   `additionalProperties` stays `false`, and the pre-D142 fixture still
   validates. `tests/validate_runner.py` asserts the required list and the closed
   shape directly, so a future edit cannot relax them silently.
4. **Docs semantics** - met, on the schema itself (the field descriptions are the
   contract's docs) and in `CHANGELOG.md`: `usageSegments` REPLACES the single
   `usageProvider` dimension on a fallback run (one usage fact per entry, none
   for the combined total; `usageProvider` is only the starting dimension), and
   `fallback.continued: false` means the API segment could not take over and the
   run is `state: "failed"` - never a silent restart.
5. **Tag and TS bindings** - met. v0.62.0 generated TS source and `dist/`,
   exported `RunnerRunFallback`/`RunnerUsageSegment` from `index.ts`, and created
   `../contracts-worktrees/v0.62.0`.

## What the origin must know

The published shape was taken from agent-runner's **already shipped** types
(`RunFallback`, `UsageSegment` in `src/domain/run.ts`), not invented: the field
names, the reason enum, the optional segment `model`, and the absent-not-null
rule all match what the runner emits today. Nothing about the producer needs to
change.

- Re-pin the file: dependency to
  `file:../contracts-worktrees/v0.62.0/gen/ts` (the tag is local until the owner
  pushes it) and import `RunnerRunFallback` and `RunnerUsageSegment`. They are
  re-exported from the package root and also present in
  `runner-dispatch-reservation.ts`, which inlines `RunnerRunRecord`.
- Because the record is closed, a consumer must pin v0.62.0 **before** the
  producer serves either member. An old pin rejects a fallback run.
- Metering remains per segment: `usageProvider` is still populated on the wire
  (the starting dimension), so a consumer that ignores `usageSegments` would
  bill the whole run to the subscription dimension. That is the documented
  reason `usageSegments` wins whenever present.

## Not done / caveats

- The tag and the pinned worktree are **local**; the owner pushes tags
  (same as v0.61.0). D031 acceptance was therefore run from the local pinned
  worktree - a clean consumer directory with
  `"@platform/contracts": "file:.../contracts-worktrees/v0.62.0/gen/ts"`,
  `npm install` and a strict `tsc` compile - not from the GitHub URL. Re-run
  from the pushed tag once it exists.
- Python was regenerated, but `datamodel-codegen` 0.68.1 renamed the unrelated
  `TaskWorkspaceState` inline enum to `State1`; the original name was restored
  by hand (same precedent as v0.26.0 / v0.59-0.60) so the Python diff is
  additive only.
- Java has no `runner.run-record` model (the Java pom only generates the parked
  agent-runner schemas); its version moved with the release but there is no Java
  codegen change.
- No consumer besides the origin is asked to move: this release is additive
  (D031); the D043 re-pin demand goes to `agent-runner` alone.
