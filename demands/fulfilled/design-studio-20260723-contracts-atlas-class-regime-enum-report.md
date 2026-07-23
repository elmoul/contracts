---
demandId: design-studio-20260723-contracts-atlas-class-regime-enum
worker: contracts
date: 2026-07-23
status: done
shipped: ["v0.17.0", "commit f8c8e19 on main", "tag v0.17.0"]
---

# Fulfillment — `contracts`: `Regime` enum gains `atlas-class`

`status: done` here is a claim, not a verdict — per `DEMAND_SYSTEM.md` §4,
this report is `contracts`' only output for this demand. `contracts` does
not self-certify and has not notified `design-studio` directly; the
coordinator assembles and delivers the summary once the owner approves.

## What shipped

- `schemas/state-feed/state.event.json`: `Regime` enum widened from
  `["console-class", "inhabited-class"]` to `["console-class",
  "inhabited-class", "atlas-class"]` in both occurrences —
  `DesignMissionPayload.regime` and `DesignSystemPayload.regime`. No other
  property, required-ness, or shape changed.
- `schemas/state-feed/state-event-java.yaml`: same two occurrences updated
  in lockstep (`tests/check_state_event_sync.py`: 10 event types still
  structurally in sync — this check compares property names/required sets
  only, so enum-literal parity between the two files was confirmed by
  direct diff, not by the sync test).
- `tests/validate_state_event.py`: two new known-good fixtures
  (`GOOD_DESIGN_MISSION_ATLAS_CLASS_REGIME`,
  `GOOD_DESIGN_SYSTEM_ATLAS_CLASS_REGIME`) proving `atlas-class` validates
  on both payloads; the pre-existing `BAD_DESIGN_MISSION_UNKNOWN_REGIME`
  fixture (`"hybrid-class"`) is untouched and still correctly rejected.
- **Python** (`gen/python/platform_contracts/state_feed/state_event.py`):
  regenerated via `datamodel-codegen --target-python-version 3.11
  --use-specialized-enum`. The shared `Regime(StrEnum)` class now reads
  `console_class = 'console-class'`, `inhabited_class = 'inhabited-class'`,
  `atlas_class = 'atlas-class'`. `Regime('atlas-class')` constructs
  successfully — the exact call
  `design-studio/src/design_studio/adapters/event_sink_state_feed.py:188`
  and `:210` make on every mission and design-system state event.
- **TypeScript** (`gen/ts/state-event.ts`, `dist/` rebuilt):
  `DesignMissionPayload.regime`/`DesignSystemPayload.regime` widened to
  `"console-class" | "inhabited-class" | "atlas-class"`. `npx tsc --noEmit`
  clean.
- **Java** (`gen/java/src/main/java/io/platform/contracts/events/`):
  regenerated via `openapi-generator-cli` 7.23.0, `--library resttemplate`
  (zero `com.google.gson` imports). `DesignMissionPayload.RegimeEnum` and
  `DesignSystemPayload.RegimeEnum` each gain `ATLAS_CLASS`. `mvn -f
  gen/java/pom.xml test`: BUILD SUCCESS, 12/12 tests.
- All three version files bumped `0.16.0` → `0.17.0`
  (`gen/java/pom.xml`, `gen/ts/package.json` + `package-lock.json`,
  `gen/python/pyproject.toml`). `CHANGELOG.md` v0.17.0 entry added.
- `python tests/run_all.py`: all 11 validators + the state-event sync check
  pass.

**Versioning:** minor bump, `v0.16.0` → `v0.17.0` — one new enum value
added to an existing, already-optional-shape field; no existing member's
required-ness or shape touched.

## D031 acceptance — post-tag, run for real, all three languages, no unverified leg

`v0.17.0` tagged and pushed (`git worktree add
../contracts-worktrees/v0.17.0 v0.17.0`, removed after verification):

- **Python:** fresh venv, `pip install
  "git+https://github.com/elmoul/contracts.git@v0.17.0#subdirectory=gen/python"`
  — installed cleanly (`pip show` confirms `0.17.0`). Constructed
  `ContractRegime('atlas-class')` directly (the exact call the two adapter
  call sites make), built full `DesignMissionPayload`/`DesignSystemPayload`
  instances with `regime="atlas-class"`, round-tripped
  (`model_dump_json()` → `model_validate_json()`), confirmed the top-level
  `StateEvent` union accepts an `atlas-class` mission event
  (`type(se.root).__name__ == 'DesignMissionEvent'`), and confirmed
  `ContractRegime('hybrid-class')` still raises `ValueError` against the
  installed package (enum is extended, not opened up).
- **Java:** fresh `mvn -DskipTests install` from the tagged worktree into a
  scratch `.m2`. A separate scratch Maven project depending on
  `io.platform:contracts:0.17.0` compiled and ran code constructing a
  `DesignMissionPayload` with `RegimeEnum.ATLAS_CLASS` and printed it —
  `BUILD SUCCESS`, output confirms `atlas-class`.
- **TypeScript:** `file:`-scratch consumer project pointed at the tagged
  worktree's committed `gen/ts` (already-built `dist/`), importing
  `DesignMissionPayload`/`StateEvent` and assigning `regime: "atlas-class"`
  to a full `StateEvent` value — `npx tsc --noEmit` exit 0.

All scratch clones/venvs/projects/worktrees deleted after verification.

## What design-studio must know

Nothing about the shape changed beyond the single new enum value. Once
re-pinned to `v0.17.0`, `design-studio`'s
`event_sink_state_feed.py:188`/`:210` calls to `ContractRegime('atlas-class')`
will construct without a `ValueError`/schema-validation error. `regime` is
shared verbatim across `DesignMissionPayload` and `DesignSystemPayload` in
the Python binding (both resolve to the same `Regime` class) — no new
per-payload enum was introduced.

## Not done / caveats

None. The demand's acceptance criteria are met as specified; no scope was
added or deferred.
