---
demandId: design-studio-20260804-contracts-guided-turn-class-regime-enum
worker: contracts
date: 2026-08-04
status: done
shipped: ["v0.18.0", "commit a3644d2 on main", "tag v0.18.0"]
---

# Fulfillment — `contracts`: `Regime` enum gains `guided-turn-class`

`status: done` here is a claim, not a verdict — per `DEMAND_SYSTEM.md` §4,
this report is `contracts`' only output for this demand. `contracts` does not
self-certify and has not notified `design-studio` directly; the coordinator
validates and delivers the summary.

## Pre-work state check

Checked first, as instructed: the capability was **not** already shipped. The
enum stood at three members (`console-class`, `inhabited-class`,
`atlas-class`, shipped in `v0.17.0`) across `state.event.json`,
`state-event-java.yaml`, and all three bindings. A session file for this same
task existed from earlier today
(`.brain/sessions/2026-08-04_0757_fulfill-demand-design-studio-20260804-co.md`,
`status: partial`, empty `changes`/`decisions`) but no work had been done —
the tree was clean at `d5fe7a8`. So this session did the work from scratch.

## What shipped

- `schemas/state-feed/state.event.json`: `Regime` enum widened from
  `["console-class", "inhabited-class", "atlas-class"]` to
  `["console-class", "inhabited-class", "atlas-class", "guided-turn-class"]`
  in **both** occurrences — `DesignMissionPayload.regime` (`design.mission`)
  and `DesignSystemPayload.regime` (`design.designSystem`). The member is
  spelled exactly `guided-turn-class` — hyphenated, matching
  `console-class`/`inhabited-class`/`atlas-class`, so `design-studio`'s
  value-projection needs no mapping table.
- `schemas/state-feed/state-event-java.yaml`: same two occurrences updated in
  lockstep. `tests/check_state_event_sync.py`: 10 event types still
  structurally in sync — that check compares property names/required sets, not
  enum literals, so enum parity between the two files was confirmed by direct
  diff as well.
- `tests/validate_state_event.py`: two new known-good fixtures
  (`GOOD_DESIGN_MISSION_GUIDED_TURN_CLASS_REGIME`,
  `GOOD_DESIGN_SYSTEM_GUIDED_TURN_CLASS_REGIME`) proving `guided-turn-class`
  validates on both payloads. The pre-existing
  `BAD_DESIGN_MISSION_UNKNOWN_REGIME` fixture (`"hybrid-class"`) is untouched
  and still correctly rejected — the enum is extended, not opened up.
- **Python** (`gen/python/platform_contracts/state_feed/state_event.py`):
  regenerated with `datamodel-code-generator` 0.68.1,
  `--target-python-version 3.11 --use-specialized-enum` (the `StrEnum` base is
  preserved). The shared `Regime(StrEnum)` gains
  `guided_turn_class = 'guided-turn-class'`. Diff is 4 insertions / 3
  deletions total: the new member, the two `regime` field descriptions, and
  the generation-timestamp header — nothing else in the file moved.
- **TypeScript** (`gen/ts/state-event.ts`, `dist/` rebuilt via `npm run
  build`): both `regime` fields widen to `"console-class" |
  "inhabited-class" | "atlas-class" | "guided-turn-class"`. `npx tsc
  --noEmit` clean.
- **Java** (`gen/java/src/main/java/io/platform/contracts/events/`):
  regenerated with `openapi-generator-cli` 7.23.0, `--library resttemplate`
  (zero `com.google.gson` imports). `DesignMissionPayload.RegimeEnum` and
  `DesignSystemPayload.RegimeEnum` each gain `GUIDED_TURN_CLASS`. Only those
  two files were taken from the regen — every other generated class differed
  solely by a refreshed `@Generated` timestamp and was deliberately left
  untouched, keeping the commit diff to the two files that actually changed.
  `mvn -B -f gen/java/pom.xml test`: BUILD SUCCESS, 12/12 tests.
- All version files bumped `0.17.0` → `0.18.0` (`gen/java/pom.xml`,
  `gen/ts/package.json` + `package-lock.json`, `gen/python/pyproject.toml`).
  `CHANGELOG.md` v0.18.0 entry added.
- `python tests/run_all.py`: all 11 validators + the state-event sync check
  pass, including the two new fixtures.

**Versioning:** minor bump, `v0.16.0`→`v0.17.0`→**`v0.18.0`** — one new enum
value on an existing field; no member removed, renamed, or made
required/optional. Same additive shape as the `atlas-class` release.

## The pinnable release

**`v0.18.0`** — commit `a3644d2` on `main`, tag `v0.18.0`, both pushed to
`https://github.com/elmoul/contracts.git`.

`design-studio` re-pins `requirements.txt` in one line:

```
platform-contracts @ git+https://github.com/elmoul/contracts.git@v0.18.0#subdirectory=gen/python
```

## D031 acceptance — post-tag, run for real, all three languages

Run against the pushed tag, not a local build (`git worktree add
../contracts-worktrees/v0.18.0 v0.18.0`, removed after verification):

- **Python:** fresh venv, `pip install
  "git+https://github.com/elmoul/contracts.git@v0.18.0#subdirectory=gen/python"`
  — installed cleanly, `pip show` confirms `0.18.0`. Against the *installed*
  package: `Regime('guided-turn-class')` constructs
  (`<Regime.guided_turn_class: 'guided-turn-class'>`); enum members read
  `['console-class', 'inhabited-class', 'atlas-class', 'guided-turn-class']`;
  full `DesignMissionPayload` and `DesignSystemPayload` instances built with
  `regime="guided-turn-class"` and round-tripped (`model_dump_json()` →
  `model_validate_json()`); the top-level `StateEvent` union accepts a
  `guided-turn-class` mission event (resolves to `DesignMissionEvent`); all
  three pre-existing members still construct; `Regime('hybrid-class')` still
  raises `ValueError`.
- **Java:** `mvn -DskipTests install` from the tagged worktree into a scratch
  `.m2`. A separate scratch Maven project depending on
  `io.platform:contracts:0.18.0` compiled and ran code building a
  `DesignMissionPayload` with `RegimeEnum.GUIDED_TURN_CLASS` and a
  `DesignSystemPayload` with `DesignSystemPayload.RegimeEnum.GUIDED_TURN_CLASS`
  — `BUILD SUCCESS`, output confirms `guided-turn-class` on both plus the
  three pre-existing members.
- **TypeScript:** `file:`-scratch consumer project pointed at the tagged
  worktree's committed `gen/ts` (already-built `dist/`), importing
  `DesignMissionPayload`/`DesignSystemPayload`/`StateEvent` and assigning
  `regime: "guided-turn-class"` — `npx tsc --noEmit` exit 0. Negative check:
  assigning `"hybrid-class"` to `DesignMissionPayload["regime"]` fails with
  `TS2322` against the same tagged build, confirming the union widened rather
  than opened.

All scratch venvs/`.m2`/projects and the `v0.18.0` worktree deleted after
verification. (Older `contracts-worktrees/` entries predate this session and
were left as found.)

## What design-studio must know

Nothing about the event shape changed beyond the single new enum value —
this is an enum widening, not a shape change. Every existing three-regime
producer and consumer keeps validating unchanged, verified both by the
untouched pre-existing fixtures in `tests/validate_state_event.py` and by
constructing all three prior members against the installed `v0.18.0` package.
`regime` remains shared verbatim across `DesignMissionPayload` and
`DesignSystemPayload` in the Python binding (both resolve to the same `Regime`
class) — no new per-payload enum was introduced. On the Java side the two
payloads keep their own nested `RegimeEnum`s, as they always have.

## D043 release-notification duty

`v0.18.0` is **additive**, so per the release checklist step 2 only the origin
demand is raised — no fleet-wide "everyone bump". The origin demand to
`design-studio` ("close your consuming leg: re-pin and adopt") is raised as
its own standalone coordination commit, separate from this release commit.

## Not done / caveats

None. The demand's acceptance criteria are met as specified; no scope was
added or deferred.
