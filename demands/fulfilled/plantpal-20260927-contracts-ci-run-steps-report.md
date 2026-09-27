---
demandId: plantpal-20260927-contracts-ci-run-steps
worker: contracts
date: 2026-09-27
status: done
shipped: ["v0.30.0", "commit faada39 on main", "optional jobId (int64) + steps[] (CiRunStep) on CiRunPayload in schemas/state-feed/state.event.json and state-event-java.yaml", "Java + TypeScript + Python bindings regenerated"]
summaryRef: "commit faada39 on main (feat(state-feed): optional jobId + steps[] on ci.run CiRunPayload (v0.30.0))"
---

# Fulfillment — `jobId` + `steps[]` on `ci.run`

**Release tag: `v0.30.0`**. That is commit `faada39`, pushed to `origin/main`.
The pinned worktree is at `../contracts-worktrees/v0.30.0`.

Before starting I checked the current state. The capability was not already
shipped: v0.29.0's `CiRunPayload` had no `jobId` or `steps`. An earlier
supervised session (`2026-09-27_0531`) had opened but made no changes.

## What shipped (per acceptance criterion)

1. **`state.event.json` CiRunPayload** gains two optional fields:
   - `jobId`: integer, int64.
   - `steps`: an array of `$ref CiRunStep`.

   `CiRunStep` has `additionalProperties: false`. It requires `number`
   (integer), `name` (string) and `status` (`CiRunStepStatus`:
   `queued|in_progress|completed`). It also allows `conclusion?`
   (`CiRunStepConclusion`: `success|failure|cancelled|skipped`), `startedAt?`
   and `completedAt?` (date-time).

   The two enums are named definitions, not inline. Inline enums made
   datamodel-codegen renumber the existing auto-named Python enums
   (`Status1..3` → `Status2..4`), which would have been a silent rename for
   anyone importing them. With named definitions the existing names are
   unchanged, and this was verified in the D031 venv.
2. **`state-event-java.yaml`** mirrors the change. The generated bindings carry
   the same fields:
   - Java: `CiRunPayload.getJobId(): Long`, `getSteps(): List<CiRunStep>`, and
     the `CiRunStepStatus` / `CiRunStepConclusion` enums.
   - TS: `jobId?: number` and `steps?: CiRunStep[]`, with the step types
     exported from `index.ts`.
   - Python: `jobId: int | None` and `steps: list[CiRunStep] | None`.

   `tests/check_state_event_sync.py` now also checks the nested definitions
   (properties, `required`, enums and `$ref` targets) across the JSON and YAML
   files.
3. **Additive:** a `ci.run` without `jobId`/`steps` still validates. This is
   proved in three places:
   - the schema case in `tests/validate_state_event.py`;
   - the Java test `eventWithoutJobIdOrStepsStillDeserializes`;
   - the Python D031 check.

   This is a minor release, 0.29.0 → 0.30.0. The Java `pom.xml` goes from
   0.27.0 to 0.30.0 to realign with the repo-wide version.
4. **The tag is named above** and in CHANGELOG `## v0.30.0`.

## Evidence

- `python tests/run_all.py` passes. It includes 7 new `ci.run` schema cases: 2
  valid, and 5 invalid ones (bad step status, step `timed_out`, missing step
  name, extra step property, string `jobId`).
- `mvn -f gen/java/pom.xml test` runs 39 tests, all green, including the new
  `StateEventCiRunStepsTest` (5).
- `DemandDispatchOrderContractsTest` had been failing on `main` because its
  fixture had moved to `demands/archive/`. It now points there, the Java twin of
  fix `ca2025f`.
- D031 acceptance, run against the pushed tag:
  - **Python:** `pip install "git+https://github.com/elmoul/contracts.git@v0.30.0#subdirectory=gen/python"`
    into a fresh venv installs version 0.30.0. Round-trips with and without
    steps pass, and `Status1..3` are unchanged.
  - **npm:** a `file:` install of the tagged worktree's `gen/ts` passes
    `tsc --strict`. A `@ts-expect-error` proves that `timed_out` is rejected as a
    step conclusion.
  - **Java:** `mvn install` from the tagged worktree into a fresh
    `-Dmaven.repo.local` succeeds, and the jar contains
    `CiRunStep`/`CiRunStepStatus`/`CiRunStepConclusion`.

## Rollout hazard (for the ci-runner / dashboard follow-ons)

The schema change is additive, but the payload objects are closed. A consumer
still pinned to v0.29.0 or earlier that validates strictly (JSON Schema,
pydantic `extra='forbid'`) will **reject** a `ci.run` that carries
`jobId`/`steps`. So state-feed and dashboard should re-pin to v0.30.0 **before**
ci-runner starts emitting these fields.

Java consumers are also affected: when a producer builds a `CiRunPayload` and
never sets `steps`, it serializes as `"steps": []`. That is the openapi-generator
default, and it is valid under v0.30.0.

## Consuming leg

Per D043, contracts raises the origin demand
`contracts-20260927-plantpal-repin-ci-run-steps` to `plantpal`. It asks plantpal
to:
- confirm it has no `ci.run` code of its own;
- make sure the ci-runner and dashboard follow-ons pin `v0.30.0`;
- carry the rollout order above into that chain.

This is an additive release, so no fleet-wide consumer demands are raised.
