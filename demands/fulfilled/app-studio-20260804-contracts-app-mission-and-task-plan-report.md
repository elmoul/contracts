---
demandId: app-studio-20260804-contracts-app-mission-and-task-plan
worker: contracts
date: 2026-08-04
status: done
shipped: ["v0.19.0", "commit 92ca10e on main", "tag v0.19.0", "schemas/app-studio/app.mission.json", "schemas/app-studio/app.task-plan.json", "demand contracts-20260804-app-studio-repin-app-mission-and-task-plan (commit 74e29a9)"]
---

# Fulfillment — `contracts`: `app.mission` and `app.task-plan`

`status: done` here is a claim, not a verdict — per `DEMAND_SYSTEM.md` §4,
this report is `contracts`' only output for this demand. `contracts` does not
self-certify and has not notified `app-studio` directly; the coordinator
validates and delivers the summary.

## Pre-work state check

Checked first, as instructed: the capability was **not** already shipped.
`schemas/` had no `app-studio/` directory at all and no schema anywhere
describing a mission or a task plan; the newest release was `v0.18.0` (the
`guided-turn-class` `Regime` widening for design-studio). A session file for
this task existed from earlier today
(`.brain/sessions/2026-08-04_0816_fulfill-demand-app-studio-20260804-contr.md`,
`status: partial`, empty `changes`/`decisions`) but no work had been done —
the tree was clean at `cfd4d7a`. This session did the work from scratch.

## What shipped

### The two schemas

Both were read off the tutor pilot's live artifacts rather than off the demand
prose — `app-studio`'s `projection.project()`, `mission.py`, `task_plan.py`,
the ledger row for mission `d34de281-c5c5-4e44-b3c5-6085c225adea`, and that
mission's `plan.json`. That is what D066 build-then-extract asks for, and it
caught things prose would not have: `plan.json` carries `mark`, `canAuthorize`
and `problems` (all derived), and carries **no** `deferredToDispatch` at all,
because the artifact predates the field.

- **`schemas/app-studio/app.mission.json`** (`AppMission`) — the 15-stage
  gated spine as a shared `$defs/missionStage`, with `$defs/missionGateStage`
  narrowing to the five stages that move only on an owner decision. `stage`,
  `class`, `appName`, `currentWave` and the three record lists are required;
  the read-time derivations (`stageKind`, `isTerminal`, `gateContext`,
  `rewindTargets`, `pipeline`) are optional, matching app-studio's own rule
  that a derivation is never stored. `rewinds[].toStage` is typed as a *gate*
  stage, not any stage — a rewind that lands on a work stage is rejected by
  the schema, not merely by app-studio's code.
- The three append-only lists are kept structurally distinct, which is what
  the demand asked for and what the tests prove: `gateRecords[].outcome` has
  exactly two members (`approved`/`rejected`, no third `send-back`), a
  send-back record carries `recordedAt` and no `outcome` so it cannot pass as
  a decision, and `waveReviewNext` (`next-wave`/`replan`/`accept`) rides only
  on gate records.
- **`schemas/app-studio/app.task-plan.json`** (`AppTaskPlan`) — waves and work
  units. `mode` and `verify` are required on every unit, as demanded, and an
  `if`/`then` additionally requires **at least one** verify step whenever
  `mode` is `owner`/`agent`/`assisted`, exempting `advisory` — which mirrors
  `WorkUnit.validate()` exactly (advisory units dispatch nothing and close
  nothing). `openDecisions` and `deferredToDispatch` are separate array
  fields; `canAuthorize`'s description states in the schema itself that it
  does not read `deferredToDispatch`.
- `deferredToDispatch` is **optional**, deliberately. Making it required would
  have failed this demand's own second acceptance criterion, since the
  owner-approved `plan.json` that proves the shape does not have the field.
  The schema records why in its description, and the validator asserts the
  fixture still lacks it so the reason cannot quietly rot.

### Tests

`tests/validate_app_studio.py` (new, wired into `tests/run_all.py`): 26
checks. Both positive fixtures are the pilot's **own** records, copied
verbatim into `tests/fixtures/app-studio/` — the mission projection read
straight out of `app_studio.db` through app-studio's own `project()`, and its
`plan.json`. The negatives cover the distinctions the demand called
load-bearing: a send-back smuggled in as a gate outcome, a send-back record
placed in `gateRecords`, a rewind to a non-gate stage, a dispatched unit with
an empty `verify`, a unit with no `mode`, a verify step with neither `run` nor
`manual`, a verify step with an empty `expect`, and the two decision lists
collapsed into one.

`gen/java/.../AppStudioContractsTest.java` (new): 8 tests, deserializing the
same two fixture files through the Java binding.

### Bindings — all three languages

- **Python** — `platform_contracts/app_studio/{app_mission,app_task_plan}.py`,
  generated with `datamodel-code-generator` 0.68.1,
  `--target-python-version 3.11 --use-specialized-enum`. Every generated enum
  is `StrEnum`, per this repo's convention. Wired into
  `platform_contracts/__init__.py`.
- **TypeScript** — `gen/ts/app-mission.ts`, `gen/ts/app-task-plan.ts` via
  `json-schema-to-typescript`, re-exported from `index.ts`, `dist/` rebuilt
  and committed (D031). `npx tsc --noEmit` clean.
- **Java** — a new `app-studio` jsonschema2pojo execution in
  `gen/java/pom.xml` → `io.platform.contracts.appstudio`.
  `mvn -B -f gen/java/pom.xml test`: BUILD SUCCESS, 20/20 tests (12 pre-existing
  + 8 new).
- `python tests/run_all.py`: all 12 validators + the state-event sync check
  pass.

**Versioning:** minor bump, `v0.18.0` → **`v0.19.0`** — two new files, no
existing schema touched.

### Two schema-shape decisions worth surfacing

Both were made against a generator, not in the abstract, and both are pinned
by a test so they cannot change silently:

1. **`verify`'s "run or manual" rule is written as a `not`, and the
   `mode`→`verify` rule as a bare `if`/`then`, not wrapped in `allOf`.** The
   natural `anyOf`-of-two-required-shapes made every generator emit two
   variant classes and a union (`VerifyStep1 | VerifyStep2`), and the `allOf`
   wrapper made `json-schema-to-typescript` emit an intersection with an index
   signature — which silently disables the excess-property checking that
   `additionalProperties: false` exists to give TypeScript consumers. Both
   forms were changed after seeing the generated output, not before.
2. **Nullable enums stay as `oneOf[$ref, null]`, and Java pays for it.**
   `abortedFrom` and `gateRecords[].waveReviewNext` both legitimately carry an
   explicit `null` in the real projection. jsonschema2pojo 1.2.1 does not
   follow a `oneOf`, so both surface as `java.lang.Object` in the Java
   binding. Writing the vocabulary out inline at each nullable site fixes Java
   — but then `datamodel-code-generator` emits a plain `Enum` rather than
   `StrEnum`, under which a Python consumer's
   `record.waveReviewNext == "replan"` silently evaluates **False**. Both
   forms were generated and inspected before choosing; the visible Java cast
   was preferred to the silent Python mismatch, given app-studio is the Python
   consumer and there is no Java consumer of these schemas today. The Java
   test asserts the current `Object` typing by reflection, so a future
   generator that *does* follow the `oneOf` fails loudly instead of changing
   the Java API by surprise.

## The pinnable release

**`v0.19.0`** — commit `92ca10e` on `main`, tag `v0.19.0`, both pushed to
`https://github.com/elmoul/contracts.git`.

```
platform-contracts @ git+https://github.com/elmoul/contracts.git@v0.19.0#subdirectory=gen/python
```

## D031 acceptance — post-tag, run for real, all three languages

Run against the pushed tag, not a local build (`git worktree add
../contracts-worktrees/v0.19.0 v0.19.0`, removed after verification):

- **Python:** fresh venv, `pip install
  "git+https://github.com/elmoul/contracts.git@v0.19.0#subdirectory=gen/python"`
  — installed cleanly, `pip show` confirms `0.19.0`. Against the *installed*
  package: both pilot fixtures parsed into `AppMission`/`AppTaskPlan` and
  round-tripped (`model_dump_json(by_alias=True)` → `model_validate_json`);
  `MissionStage` has 15 members, `MissionGateStage` 5, `WaveReviewNext` 3;
  the `StrEnum` convention verified by direct string comparison
  (`WaveReviewNext.replan == "replan"`, `Mode.owner == "owner"`,
  `WaveStatus.in_review == "in-review"`); the explicit `null` on `abortedFrom`
  and `waveReviewNext` accepted; an unknown `mode` and an unknown `stage` both
  raise `ValidationError`; `app_mission` reachable from the package root.
- **Java:** `mvn -DskipTests install` from the tagged worktree into a scratch
  `.m2`. A separate scratch Maven project depending on
  `io.platform:contracts:0.19.0` compiled and ran code that deserialized both
  fixture files, round-tripped them, checked all four enum cardinalities, and
  confirmed an unknown `mode` is rejected — output `ALL JAVA D031 CHECKS
  PASSED`.
- **TypeScript:** `file:`-scratch consumer project pointed at the tagged
  worktree's committed `gen/ts` (already-built `dist/`), building a full
  `AppMission`, `AppTaskPlan`, `WorkUnit` and `VerifyStep` with
  `deferredToDispatch` populated — `npx tsc --noEmit` exit 0 under
  `"strict": true`. Negative check against the same tagged build: `mode:
  "human"` and `stage: "implementing"` both fail with `TS2322`, confirming the
  unions are closed.

All scratch venvs / `.m2` / projects and the `v0.19.0` worktree were deleted
after verification. (Older `contracts-worktrees/` entries predate this session
and were left as found.)

## D043 release-notification duty

`v0.19.0` is **additive** — two brand-new schemas, no existing schema
touched — so per the release checklist step 2 only the origin demand is
raised, and the consumer enumeration was still run rather than assumed:

- **Origin demand raised:**
  `contracts-20260804-app-studio-repin-app-mission-and-task-plan` →
  `app-studio`, "close your consuming leg: re-pin and adopt", as its own
  standalone coordination commit `74e29a9`, pushed.
- **Other consumers: none, verified.** control-plane's `GET /registry` was not
  reachable (nothing serving it on 8080/8082/8090/9090 — the service is not
  running), so the enumeration was run against the same source that endpoint
  derives from: every repo's `HEXAGON.md` `contracts.used` block across the
  fleet. No repo outside `contracts` references `app.mission` or
  `app.task-plan` in any form — which is what one would expect of schemas that
  did not exist until this release. No fleet-wide "everyone bump" was raised;
  D031 pins are deliberate and an additive release obligates no consumer to
  move.

## The acceptance criteria, one by one

1. *`schemas/app-studio/app.mission.json` exists and validates the tutor
   pilot's own mission record* — **yes**. The pilot's actual projected mission
   record is `tests/fixtures/app-studio/tutor-pilot-mission.json`, validated by
   `tests/validate_app_studio.py` and deserialized by the Java test and by the
   post-tag Python and Java D031 probes.
2. *`schemas/app-studio/app.task-plan.json` exists and validates the tutor
   pilot's own `plan.json`* — **yes**, same three ways, from the same
   verbatim copy of the owner-approved artifact.
3. *Both land as an additive minor release; no existing schema changes shape*
   — **yes**. `git diff v0.18.0 v0.19.0 -- schemas/` adds two files and
   modifies none.
4. *A D043 release-notification demand goes to app-studio, and to any other
   consumer of the release* — **yes** to app-studio (commit `74e29a9`); other
   consumers enumerated and found to be none, method and caveat recorded
   above.
5. *The `Regime` enum in `state.event` is NOT changed by this demand* —
   **honoured**. `schemas/state-feed/` is untouched in `v0.19.0`;
   `guided-turn-class` was added separately in `v0.18.0` as design-studio's
   own demand, and nothing in this release revisits it.

## Not done / caveats

- The `java.lang.Object` typing of `abortedFrom` and
  `gateRecords[].waveReviewNext` in the **Java** binding is a real limitation,
  not an oversight — chosen deliberately over degrading the Python binding,
  documented in the schema, the CHANGELOG and the Java test. If a Java
  consumer of `app.mission` ever appears, the fix is a Java-flavoured mirror
  schema (the pattern `state-event-java.yaml` already establishes) plus a sync
  check, and it should be raised as its own demand rather than done quietly.
- `pipeline` on `app.mission` is intentionally left unconstrained
  (`additionalProperties: true`): its shape belongs to app-studio's dispatch
  layer, not to a cross-hexagon port. Called out in the demand to app-studio so
  it is a known gap rather than a silent one.
- No scope was added or deferred otherwise.
