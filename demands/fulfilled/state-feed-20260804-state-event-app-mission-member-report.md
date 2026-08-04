---
demandId: state-feed-20260804-state-event-app-mission-member
worker: contracts
date: 2026-08-04
status: done
shipped: ["v0.20.0", "commit 9366915 on main", "tag v0.20.0", "schemas/state-feed/state.event.json (AppMissionEvent + AppMissionPayload)", "schemas/state-feed/state-event-java.yaml (AppMissionEvent + AppMissionPayload)", "io.platform.contracts.events.AppMissionEvent", "tests/check_state_event_sync.py (enum-identity check vs app.mission.json)", "tests/validate_state_event.py (9 cases)", "gen/java/src/test/java/io/platform/contracts/StateEventAppMissionTest.java (6 cases)", "demand contracts-20260804-state-feed-repin-app-mission-event (commit d91127a)"]
---

# Fulfillment — `contracts`: `app.mission` as a `state.event` member

`status: done` here is a claim, not a verdict — per `DEMAND_SYSTEM.md` §4,
this report is `contracts`' only output for this demand. `contracts` does not
self-certify and has not notified `state-feed` directly; the coordinator
validates and delivers the summary.

## Pre-work state check

Checked first, as instructed: the capability was **not** already shipped. At
`600010e` the `state.event` oneOf had ten members and neither
`state.event.json` nor `state-event-java.yaml` mentioned `app.mission`
anywhere; the newest release was `v0.19.0` (the `app-studio` schemas). The
work below was done from scratch in this session.

## What shipped

### The eleventh oneOf member

`AppMissionEvent` / `AppMissionPayload`, added to **both** files that define
the union — `state.event.json` (source of truth for TypeScript, Python and
the validators) and `state-event-java.yaml` (the OpenAPI wrapper that exists
only because jsonschema2pojo cannot generate per-variant classes from a
`oneOf`). The Java binding now generates
`io.platform.contracts.events.AppMissionEvent` alongside the existing ten
variants, as asked.

The payload requires `missionId` (uuid), `appName` (functional name, D002
pattern), `stage` and `currentWave` (integer ≥ 0), and carries the latest gate
outcome as the optional trio `gate` / `outcome` / `gateWave`. `gate` and
`outcome` travel together and are present only when the event reports a
verdict; `gateWave` exists for `wave-review`, the one gate that repeats per
wave, and is absent for the gates that occur once — which is the "and `wave`
where the gate repeats" clause of the acceptance criteria.

### One vocabulary, not two — and enforced, not promised

This is the criterion that shaped the implementation, so it is worth being
precise about what was done and why.

`stage` is the 15-member mission spine and `gate` the 5-member gate subset
from `schemas/app-studio/app.mission.json` (`$defs/missionStage`,
`$defs/missionGateStage`); `outcome` is that same schema's D091 gate verdict,
`approved`/`rejected`, with no third `send-back` member.

They are **written out** in the two state-feed files rather than `$ref`-ed
across schemas. That is a deliberate choice, not a shortcut:
`state.event.json` is a self-contained bundle — nothing in it `$ref`s another
file — feeding three different generators, and the Java YAML wrapper cannot
`$ref` another file at all. A cross-file `$ref` would have changed the
generation contract for every existing variant to satisfy one new one.

So the "no second, divergent copy" requirement is met **mechanically instead
of by convention**: `tests/check_state_event_sync.py` — which already existed
to keep the two state-feed files in sync — now additionally loads
`app.mission.json` and asserts that both files' `AppMissionPayload` `stage`,
`gate` and `outcome` enums equal `missionStage`, `missionGateStage` and
`gateRecords[].outcome` exactly. Any divergence fails `python tests/run_all.py`
and therefore CI. The check was verified against a deliberately corrupted copy
before being trusted: shortening the stage enum to one member produces a
failure naming the file, the property and both enums. Both schema files also
carry a comment at the payload saying the enums are app.mission.json's and
must not be edited alone.

The practical effect: adding a stage to app-studio's spine and forgetting
state-feed now breaks the suite, rather than silently forking the vocabulary
the way a hand-copied enum normally does.

### Coverage

- `tests/validate_state_event.py`: 9 new schema-level cases — 4 known-good
  (gateless `executing`; `wave-review` rejected with `gateWave`; `concept-gate`
  approved without `gateWave`, proving `gateWave` is genuinely optional;
  terminal `aborted`) and 5 known-bad (a design-studio stage name `feel-gate`
  to prove the two studios' vocabularies do not bleed; a non-gate stage used
  as `gate`; `send-back` as an `outcome`; missing `currentWave`; a themed,
  non-D002 `appName`).
- `gen/java/.../StateEventAppMissionTest.java`: 6 cases against the generated
  binding — the same shapes plus a serialize/deserialize round-trip, pinning
  that `stage`/`gate`/`outcome` really generate as enums rather than free
  strings, which is the whole point of the union member.

## Verification

- `python tests/run_all.py` — all validators pass, sync check reports
  11 event types.
- `mvn -B -f gen/java/pom.xml test` — 26 tests, 0 failures.
- `npx tsc --noEmit` in `gen/ts` after regenerating `state-event.ts`,
  re-exporting `AppMissionEvent`/`AppMissionPayload` from `index.ts`, and
  rebuilding the committed `dist/`.
- **D031 acceptance, run against the real `v0.20.0` tag on GitHub** (not a
  local build), all three languages:
  - Python: fresh venv, `pip install git+…@v0.20.0#subdirectory=gen/python`,
    parsed a wave-review event and confirmed `payload.stage == "wave-review"`
    is `True` (the `StrEnum` convention holds — a plain `Enum` would have made
    that comparison silently `False`) plus a `model_dump_json()` round-trip.
  - TypeScript: `file:` install of the tag clone's `gen/ts` into a scratch
    project, an `AppMissionEvent` literal assigned to `StateEvent`, compiled
    under `--strict`.
  - Java: fresh `-Dmaven.repo.local` install of the tag clone (its own test
    suite ran green in that clean repo), then a separate scratch consumer
    project compiled against the installed `io.platform:contracts:0.20.0`
    using `AppMissionPayload.StageEnum` / `GateEnum` / `OutcomeEnum`.

## Release and D043

Released as a normal additive contracts version tag, `v0.20.0` (commit
`9366915`), with version bumps in all three binding manifests and a
`CHANGELOG.md` entry. Nothing existing changed shape — the ten prior variants,
their payloads and `Origin` are untouched — so a consumer still on its current
pin keeps working and only needs to move to *read* the new variant.

Per D043 the release also raised its origin demand:
`contracts-20260804-state-feed-repin-app-mission-event` (commit `d91127a`),
asking `state-feed` to re-pin from 0.17.0 to v0.20.0 and close its consuming
leg. Additive release, so **only** the origin demand was raised — no
fleet-wide bump, per the same checklist (D031 pins are deliberate; an additive
release obligates no other consumer to move).

## Notes for the consumer

Three things `state-feed` should know, also written into the demand:

1. There is no `send-back` outcome and there should never be one — a send-back
   carries a note and no verdict, and app-studio keeps those in a separate
   list. Two values is the whole set.
2. `aborted` is on the `stage` enum and is terminal, sitting beside the spine
   rather than on it; `wave-review` → `executing` also moves backwards. A
   renderer assuming monotonic stage advance will be wrong on both.
3. From Java, an unknown enum value surfaces as Jackson's
   `ValueInstantiationException`, not `InvalidFormatException` —
   openapi-generator 7.23.0 routes enum parsing through a `fromValue` factory.
   This cost two red tests here before it was pinned; it is now asserted in
   `StateEventAppMissionTest` so the next session does not rediscover it.
