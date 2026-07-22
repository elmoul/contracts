---
demandId: design-studio-20260722-contracts-design-system-state-event
worker: contracts
date: 2026-07-22
status: done
shipped: ["v0.16.0", "commit 53e43d6 on main", "tag v0.16.0"]
---

# Fulfillment report — contracts: `design.designSystem` state-event member

`status: done` here is a claim, not a verdict — per `DEMAND_SYSTEM.md` §4,
this report is `contracts`' only output for this demand. `contracts` does not
self-certify and has not notified `design-studio` directly; the coordinator
assembles and delivers the summary once the owner approves.

## What shipped

`schemas/state-feed/state.event.json` gained a tenth `oneOf` member,
`DesignSystemEvent`, following `DesignMissionEvent`'s exact envelope idiom
(`type`/`timestamp`/`payload` required, `origin` optional,
`additionalProperties: false`). Mirrored verbatim into
`schemas/state-feed/state-event-java.yaml` (the Java codegen wrapper) so both
files stay structurally in sync — enforced by
`tests/check_state_event_sync.py`, which now reports 10 event types.

`DesignSystemPayload` carries exactly the shape the demand specified:

- `designSystemId` (UUID, required)
- `name` (string, required)
- `slug` (string, required, pattern `^[a-z][a-z0-9-]+$` — reusing
  `DesignMissionPayload.targetRepo`'s functional-identifier pattern verbatim)
- `version` (string, required, pattern `^v?\d+\.\d+\.\d+$` — semver,
  optionally `v`-prefixed)
- `regime` (required, **reuses `DesignMissionPayload`'s existing `Regime`
  enum** — `console-class` / `inhabited-class` — no new enum defined; the
  Python regen confirms this by collapsing both fields onto the same
  generated `Regime` class rather than emitting a duplicate)
- `status` (required, new enum: `draft` / `validated` / `retired`)
- `origin` (required, new enum: `owner-built` / `mission-built` —
  deliberately distinct from this same file's pre-existing envelope-level
  `Origin` enum, which means `host`/`hub`, D011's which-wall field; the
  Python regen names them `Origin`/`Origin1`, never merging the two)
- `sourceMissionId` (UUID, optional — absent/null when `origin` is
  `owner-built`)
- `change` (required, new enum: `created` / `validated` / `retired` /
  `release` — the reason this particular event fired)

`DesignSystemEvent` was added to `StateEvent`'s `RootModel` union in both
places `state_event.py` lists its members (the outer `Union[...]` and the
inner `root: Union[...]`), identically, matching the file's own existing
double-listing pattern for every other member.

All three bindings regenerated and verified:

- **Python:** `DesignSystemPayload`/`DesignSystemEvent` classes added to
  `gen/python/platform_contracts/state_feed/state_event.py`; new
  `Status3`/`Origin1`/`Change` enums (following the file's own existing
  numbering precedent for same-field-name-different-values enums). The nine
  pre-existing classes picked up only a refreshed generation-timestamp
  comment. `python tests/run_all.py` — all 11 validators + the state-event
  sync check green.
- **TypeScript:** `DesignSystemEvent`/`DesignSystemPayload` added to
  `gen/ts/state-event.ts`, re-exported from `gen/ts/index.ts`, `dist/`
  rebuilt. `npx tsc --noEmit` clean.
- **Java:** `DesignSystemEvent`/`DesignSystemPayload` generated into
  `gen/java/src/main/java/io/platform/contracts/events/` via
  `openapi-generator-cli` against the hand-mirrored
  `state-event-java.yaml`, nested `RegimeEnum`/`StatusEnum`/`OriginEnum`/
  `ChangeEnum` (matching this package's existing per-class-nested-enum
  idiom — Java doesn't get Python's cross-payload `Regime` sharing, same as
  `DesignMissionPayload`'s own nested `RegimeEnum`). `mvn -f gen/java/pom.xml
  test` — BUILD SUCCESS, 12/12 (no new Java-side test added, matching this
  package's own precedent: `job.progress`/`agent.run`/`design.mission` never
  got dedicated Java tests either — coverage lives in
  `tests/validate_state_event.py` and the sync check).

Extended `tests/validate_state_event.py` with 6 cases for
`design.designSystem` (owner-built-draft and
mission-built-release-with-sourceMissionId known-good; unknown-status,
unknown-origin, bad-version-shape, missing-change known-bad).

**Versioning:** minor bump, `v0.15.0` → `v0.16.0` — one new additive `oneOf`
member, no existing member's shape touched.

## D031 acceptance — post-tag, run for real, all three languages, no unverified leg

`v0.16.0` tagged and pushed
(`git worktree add ../contracts-worktrees/v0.16.0 v0.16.0`, removed after
verification):

- **Java:** fresh `mvn -DskipTests install` from the tagged worktree into
  scratch `.m2`; confirmed via `jar tf` that
  `DesignSystemEvent`/`DesignSystemPayload` (and their nested enums) are
  actually packaged. A separate scratch Maven project depending on
  `io.platform:contracts:0.16.0` compiled and ran code constructing a full
  `DesignSystemEvent` (owner-built, draft, `console-class`) and printed it —
  `BUILD SUCCESS`.
- **Python:** fresh venv, `pip install
  "git+https://github.com/elmoul/contracts.git@v0.16.0#subdirectory=gen/python"`
  — installed cleanly (`pip show` confirms `0.16.0`). Constructed a
  `DesignSystemPayload`/`DesignSystemEvent`, round-tripped
  (`model_dump_json()` → `model_validate_json()`), confirmed the top-level
  `StateEvent` union accepts it (`type(se.root).__name__ ==
  'DesignSystemEvent'`), and confirmed an unknown `status` value raises
  `ValidationError` against the installed package.
- **TypeScript:** `file:`-scratch consumer project pointed at the tagged
  worktree's committed `gen/ts` (built `dist/`), importing
  `DesignSystemEvent`/`DesignSystemPayload`/`StateEvent` and constructing +
  assigning a `DesignSystemEvent` to the `StateEvent` union type — `npx tsc
  --noEmit` exit 0.

All scratch clones/venvs/projects deleted after verification.

## What design-studio must know

Nothing about the shape changed from what the demand's acceptance criteria
specified — no negotiation needed. Once re-pinned, `design-studio` can
replace its hand-shaped stopgap dict with the generated
`DesignSystemEvent`/`DesignSystemPayload` types directly. `regime` reuses the
platform's existing `console-class`/`inhabited-class` values (D053) — no new
regime vocabulary was introduced.

## Not done / caveats

None. The demand's acceptance criteria are met as specified; no scope was
cut.

## D043 release-notification duty

Per `CLAUDE.md`'s "Release checklist (per tag)": additive release, so per
D043 only the origin demand is required (no fleet-wide "adopt or explain" —
breaking-release-only). A demand `to: [design-studio]` ("re-pin and adopt
v0.16.0") is raised as part of this same session, standalone coordination
commit, per `DEMAND_SYSTEM.md` §3 —
`demands/2026-07-22-design-studio-repin-design-system-event.md`.
