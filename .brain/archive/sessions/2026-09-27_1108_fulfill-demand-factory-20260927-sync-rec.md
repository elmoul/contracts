---
session_id: 2026-09-27_1108_fulfill-demand-factory-20260927-sync-rec
agent: contracts
model: claude-sonnet-5
started: 2026-09-27T11:08:13+00:00
ended: 2026-09-27T11:19:37+00:00
task: "Fulfill demand factory-20260927-sync-recovery-retention (operation retention coverage + safe missing-operation recovery)"
priority: 2
status: done
launch: interactive
decisions: []
changes:
  - "schemas/delivery/delivery.operation-coverage.json: NEW -- coveredSince (retention coverage floor), terminalRetentionDays (minimum 90), vendorInFlightBoundSeconds"
  - "schemas/delivery/delivery.error.json: operation_not_found (conclusive, requires details.reservedAt + details.coveredSince, retryable const true) vs operation_lookup_out_of_coverage (inconclusive, reason enum, retryable const false) via if/then; tracker_outcome_unknown added and pinned retryable false"
  - "schemas/delivery/delivery.sync-operation.json: absenceProvenAt + vendorInFlightBoundSeconds; readBack.absentSince + absenceQuietUntil required exactly when effectPresent is false; attempts>=2 requires absenceProvenAt; uncertain requires tracker_outcome_unknown with retryable false; retainUntil pinned null for open statuses"
  - "schemas/delivery/delivery.sync-request.json: optional reservedAt (part of the hashed canonical body, so a replay must repeat it verbatim)"
  - "schemas/delivery-api/youtrack-delivery.openapi.yaml: NEW GET /delivery/v1/operations/coverage; reservedAt query param and write-path coverage gate; reconcile rewritten for the quiet window"
  - "docs/task-delivery.md: retention coverage + classification table + caller behaviour, absence is not non-execution, uncertain is not retryable, binding caveat, four youtrack producer obligations, handoff matrix + v0.35.0 repin block"
  - "tests/validate_delivery.py: 63 -> 88 cases; check_recovery_semantics covers both demand scenarios (restart after retention expiry, delayed vendor write) as executable cross-field checks"
  - "gen/python + gen/ts bindings regenerated (delivery_operation_coverage new; error/sync-operation/sync-request updated), versions bumped to 0.35.0, dist/ rebuilt per D031; no Java delivery binding exists"
  - "DEPLOYMENT.md + CHANGELOG.md: v0.35.0 entry and the if/then-is-not-generated codegen gotcha"
  - "demands/2026-09-27-factory-repin-sync-recovery-retention.md + demands/fulfilled/factory-20260927-sync-recovery-retention-report.md (D043 origin demand + fulfillment report)"
lessons:
  - "The generated bindings do not implement JSON Schema if/then, so a conditional is documentation unless it is asserted at the schema level. v0.35.0 moved the load-bearing recovery rules INTO if/then, which means the pydantic/TS classes happily accept exactly the shapes the schema exists to refuse (an unwindowed absence, a resend with no absenceProvenAt). The D031 acceptance script caught this only because it asserted the binding would REJECT them and it did not -- a weaker acceptance (does it accept the good shape?) would have shipped the whole release believing the rules were enforced."
  - "A tag that has not been consumed is still re-pointable, and it is better to re-point than to ship a tag whose own docs are inconsistent with it. v0.35.0 was tagged at e678d39, the acceptance pass surfaced the binding caveat, and because no D043 demand had been raised yet no consumer could have seen it -- so removing and re-tagging was safe, and the report discloses it. The window closes the moment the origin demand is pushed."
  - "Both D031 acceptances failed first for reasons unrelated to the artifact: npx resolved 'tsc' to the squatter package (install typescript in the scratch project, never npx tsc), and a fresh-clone schema test hit Unresolvable: delivery.issue-ref.json until the registry carried the https://platform/contracts/delivery/<file> alias the repo's own registry() uses. Budget for the harness, and reuse the repo's registry shape when validating from a clone."
  - "The installed Python package does not bundle schemas/, so the standard advice 'validate against the JSON Schema' is not followable from a pip install. Reported as an owner decision rather than silently fixed -- it is a packaging change (wheel data), not a delivery-schema change, and expanding scope silently is how a coordinated release goes wrong."
context_missing: []
notes_used: []
vault_sync: none
close: confirmed
---


## Log

**11:08 Session opened** via `brain session open`.

**11:10 State check first.** Not previously shipped: the two supervisor-opened
sessions on this demand (`2026-09-27_1108` interactive, `2026-09-27_1207` from
agent-runner's dispatch supervisor) left no commits, no tag and no report, and the
gap was live in the tree -- `docs/task-delivery.md` still told Factory that a lookup
miss meant "the request never arrived, so Factory may submit that key", and nothing
in `schemas/delivery/` distinguished a never-stored key from a purged terminal
record. Confirmed the demand envelope from `GET /inbox/contracts`
(127.0.0.1:8082), open, `readyFor: contracts`, three acceptance criteria verbatim.

**11:12 Designed the distinction.** A lookup miss is only safe to act on if the
service can prove the key was never stored, so the contract now publishes what the
store can answer rather than leaving the caller to infer it: a coverage floor
(`delivery.operation-coverage`, `coveredSince`), and a classified miss --
`operation_not_found` (conclusive, requires caller `reservedAt` at or after the
floor, `retryable: true`) vs `operation_lookup_out_of_coverage` (inconclusive,
`retryable: false`). The schema makes the unsafe reading unrepresentable rather than
merely discouraged: a bare conclusive-looking 404 cannot validate. Gated the write
path on the same `reservedAt` too, because a re-PUT is another way to repeat a write.

**11:16 Absence is not non-execution.** An `effectPresent: false` read-back now must
carry `absentSince` + `absenceQuietUntil`, `attempts >= 2` without `absenceProvenAt`
is invalid, and `uncertain` must carry `tracker_outcome_unknown` with
`retryable: false`. That last one closed a live hole: `tracker_unavailable` is pinned
`retryable: true` and was usable to report a post-send timeout, which is exactly the
case that must never be retried blindly. The two cross-field timestamp rules are
arithmetic JSON Schema cannot express, so they are executable checks in
`tests/validate_delivery.py` §`check_recovery_semantics`, covering both scenarios the
demand names (restart after retention expiry, delayed vendor write).

**11:18 Released v0.35.0.** 88 schema cases (from 63), docs §Retention coverage /
§Absence is not non-execution / §Producer obligations, CHANGELOG, three bindings
regenerated (Python + TS; no Java delivery binding exists).

**11:19 The tag was re-pointed -- disclosed in the report.** `v0.35.0` was first
tagged at `e678d39`; the D031 acceptance pass then surfaced that neither codegen
implements `if/then`, so every v0.35.0 recovery rule is inert in the generated
bindings. Rather than weaken the check I rewrote the acceptance to test at the
schema level against a fresh clone, documented the caveat in three places, and
because the tag was minutes old and no D043 demand had been raised (no consumer could
have seen it) removed and re-tagged so the tagged artifact is self-consistent.
`v0.35.0` now points at `d4b3ce3`; worktree recreated and re-verified.

**11:20 Both D031 legs green at the tag.** Python: fresh venv, git-URL install,
0.35.0, round-trips the new fields and still loads a v0.34.0-shaped record. TS:
scratch project, fresh cache, `file:../contracts-worktrees/v0.35.0/gen/ts`,
`tsc --strict --noEmit` green, `dist/` carries the new type. Schema level: 12 checks
against a fresh `--branch v0.35.0` clone.

**11:21 Raised the D043 origin demand and reported.** Coordination commit `8d9334a`
("demands: fulfilled factory-20260927-sync-recovery-retention; raise factory
consuming-leg demand (D043)") carries both files and is pushed -- the push *is* the
raise. Additive release, so only the origin demand: `factory` re-pins and adopts, no
fleet-wide consumer demand. Coordinator board: 0 errors, demand registered `open`,
fulfillment registered.

**11:22 Session closed via `brain session close` (status: done).** Nothing left
running: no servers, watchers or Compose stacks were started this session, and the
`npm`/`tsc`/`pip` invocations were all foreground and exited.

**11:19 Session closed via `brain session close` (status: done).**
