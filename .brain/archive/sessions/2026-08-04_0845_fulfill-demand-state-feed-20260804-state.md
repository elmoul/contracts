---
session_id: 2026-08-04_0845_fulfill-demand-state-feed-20260804-state
agent: contracts
model: claude-code
started: 2026-08-04T08:45:29+01:00
ended: 2026-08-04T08:53:21+01:00
task: "fulfill demand state-feed-20260804-state-event-app-mission-member"
priority: 1
status: done
launch: interactive
decisions:
  - "Wrote the stage/gate/outcome enums out in state.event.json and state-event-java.yaml rather than $ref-ing app.mission.json: the bundle is self-contained for three generators and the Java YAML wrapper cannot $ref another file at all. The demand's no-divergent-copy requirement is met mechanically instead, by extending check_state_event_sync.py to compare both copies against app.mission.json."
  - "Additive release v0.20.0 -> D043 origin demand only, no fleet-wide bump."
changes:
  - "schemas/state-feed/state.event.json + state-event-java.yaml: AppMissionEvent/AppMissionPayload as the 11th oneOf member"
  - "tests/check_state_event_sync.py: enum-identity check vs schemas/app-studio/app.mission.json"
  - "tests/validate_state_event.py: 9 app.mission cases; gen/java StateEventAppMissionTest: 6 cases"
  - "regenerated all three bindings, bumped to 0.20.0, CHANGELOG entry, tag v0.20.0"
  - "demands/2026-08-04-state-feed-repin-app-mission-event.md + demands/fulfilled/state-feed-20260804-state-event-app-mission-member-report.md"
lessons:
  - "openapi-generator 7.23.0 routes enum parsing through a fromValue factory, so an unknown enum value surfaces as Jackson ValueInstantiationException, not InvalidFormatException. Cost two red tests; now asserted in StateEventAppMissionTest."
  - "Rewriting state.event.json with json.dump reflows the whole file (~450 lines of churn) because it is hand-formatted with one-line $ref objects. Edit it textually."
context_missing: []
notes_used: []
vault_sync: none
close: confirmed
---


## Log

**08:45 Session opened** via `brain session open`.

**08:47 Schema + Java YAML** — added the 11th oneOf member, both files.

**08:48 Sync check extended** — verified it fails on a deliberately corrupted enum copy before trusting it.

**08:49 Bindings regenerated** — mvn 26/26 green after fixing the exception-type assumption; tsc --noEmit clean; Python StrEnum confirmed.

**08:52 Released v0.20.0** — D031 acceptance run from the real GitHub tag in all three languages (fresh venv, file: npm install, fresh .m2 + scratch consumer). All green.

**08:55 D043 origin demand raised** and fulfillment report written; both pushed.

**08:53 Session closed via `brain session close` (status: done).**
