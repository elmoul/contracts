---
demandId: app-studio-20260804-contracts-binding-direction-array
worker: contracts
date: 2026-08-04
status: done
shipped: ["v0.21.0", "commit 154bba6 on main", "tag v0.21.0", "schemas/app-studio/app.mission.json ($defs gateContext.bindingDirection: nullable string -> nullable string[])", "gen/ts/app-mission.ts + gen/ts/dist (string[] | null)", "gen/python/platform_contracts/app_studio/app_mission.py (list[str] | None)", "io.platform.contracts.appstudio.GateContext (List<String>)", "tests/fixtures/app-studio/twice-rejected-gate-mission.json", "tests/validate_app_studio.py (3 new cases: two-rejection positive, null positive, bare-string negative)", "CHANGELOG.md v0.21.0 breaking-change notice", "demand contracts-20260804-app-studio-repin-binding-direction-array (commit 4c141f6)"]
---

# Fulfillment — `contracts`: `gateContext.bindingDirection` becomes a list

`status: done` here is a claim, not a verdict — per `DEMAND_SYSTEM.md` §4 this
report is `contracts`' only output for this demand. `contracts` does not
self-certify and has not notified `app-studio` directly; the coordinator
validates and delivers the summary.

## Pre-work state check

Checked first, as instructed: the capability was **not** already shipped. At
`c48facf` (newest release `v0.20.0`), `schemas/app-studio/app.mission.json`
still declared:

```json
"bindingDirection": {
  "type": ["string", "null"],
  "description": "The direction carried from the last rejection at this gate, if any."
}
```

and all three generated bindings carried the scalar (`string | null`,
`str | None`, `String`). There was no fixture anywhere with more than one
direction at a gate. The work below was done from scratch in this session.

## What shipped

### The schema change

`gateContext.bindingDirection` is now `["array", "null"]` with
`items: {type: string}`. The description was rewritten to say what the field
actually means rather than what the scalar could hold: the directions carried
from **every** prior rejection at this gate, oldest first, `null` when the gate
has never rejected, with length tracking the sibling `priorRounds`.

The modelling defect, stated plainly for the record: the old field was "the
direction from the *last* rejection". A gate can reject more than once, and the
first direction does not stop being binding because a second arrived — the
owner is bound by both. With a scalar, the only way to represent a second
rejection was to discard the first, so a twice-rejected gate either lost a
direction or failed validation. `priorRounds` already counted the rounds; the
directions now have somewhere to go.

### The regression fixture

`tests/fixtures/app-studio/twice-rejected-gate-mission.json` — a `plan-gate`
mission with two `rejected` gate records and
`bindingDirection: ["split wave 1 — it carries two unrelated concerns", "the
verify steps must name a command, not 'check it works'"]`, `priorRounds: 2`.
It is a permanent positive case in `validate_app_studio.py`, paired with two
more cases so the list form cannot quietly regress:

- **positive** — same fixture with `bindingDirection: null`, `priorRounds: 0`:
  the never-rejected gate still validates.
- **negative** — same fixture with `bindingDirection` set back to a bare
  string: **must be rejected**. This is the case that fails loudly if anyone
  reverts the type.

### The tutor pilot fixture is untouched

`tests/fixtures/app-studio/tutor-pilot-mission.json` was not edited — it
carries `gateContext: null` (the projection omits gate context for that
record), so it is orthogonal to this change and validates exactly as before.
Its byte-for-byte-verbatim property, which D066 build-then-extract depends on,
is intact.

### Bindings regenerated

All three, from the changed schema, using the documented `DEPLOYMENT.md`
commands (`datamodel-codegen`, `json-schema-to-typescript` + `npm run build`,
`jsonschema2pojo` via Maven):

| binding | v0.20.0 | v0.21.0 |
|---|---|---|
| TypeScript | `bindingDirection?: string \| null` | `bindingDirection?: string[] \| null` |
| Python | `bindingDirection: str \| None` | `bindingDirection: list[str] \| None` |
| Java | `private String bindingDirection` | `private List<String> bindingDirection` |

## Release call — v0.21.0, minor, and it is breaking

The demand left the version class to `contracts`. The call: **minor bump,
explicitly labelled breaking.**

The rationale is the v0.11.0 precedent already recorded in `CHANGELOG.md`: the
"breaking = major" line at the top of that file is the 1.0+ rule, and while
this package sits at `0.y.z` standard semver treats it as initial development,
where breaking changes ride a minor bump. A major is reserved for the first
genuinely 1.0-era break. This release follows that precedent rather than
inventing a second convention.

The release notes say the breakage plainly, as the acceptance criteria
required — the `v0.21.0` entry opens with "**Breaking release, all three
bindings** — read this before re-pinning" and states: *a consumer typing this
field as a string will break.* Not "may". TS and Java call sites fail to
compile, Python fails at parse time with a pydantic `ValidationError`, and
anything hand-parsing the JSON silently receives a list where it expected a
string. The mechanical migration (`bindingDirection?.[0]`) is given alongside
the note that it re-introduces the defect — reading one direction is the bug;
render all of them.

## D031 acceptance — run against the real tag, not a local build

Per the standing invariant, all three bindings were installed from the pushed
`v0.21.0` tag into a fresh venv / npm cache / `.m2`, and the type was confirmed
in each *installed* artifact:

- **Python** — `pip install --no-cache-dir
  "git+https://github.com/elmoul/contracts.git@v0.21.0#subdirectory=gen/python"`
  in a fresh venv. `GateContext(bindingDirection=["first","second"])`
  constructs; `bindingDirection` omitted yields `None`;
  `bindingDirection="oops"` raises `ValidationError`. All three as expected.
- **TypeScript** — fresh `git clone --branch v0.21.0`, then a `file:` dependency
  on `../checkout/gen/ts` per `DEPLOYMENT.md` (npm's `github:owner/repo#tag`
  form does not work for this repo — `package.json` lives at `gen/ts`, not the
  repo root; that failure was re-confirmed live in this session, so the
  `github:` form quoted in an earlier demand template is wrong and this demand
  quotes the `file:` form). Under `strict`, assigning `["first","second"]` and
  `null` compiles; assigning `"first"` fails with
  `TS2322: Type 'string' is not assignable to type 'string[]'`.
- **Java** — `mvn install -Dmaven.repo.local=<fresh>` from the tagged checkout.
  `contracts-0.21.0.jar` installs, and the compiled `GateContext` in the jar
  carries `getBindingDirection ()Ljava/util/List;` with generic signature
  `Ljava/util/List<Ljava/lang/String;>;`.

Repo test suites green before the tag: `python tests/run_all.py` (all
validators, 29 app-studio checks) and `mvn -B -f gen/java/pom.xml test`.

## D043 release notification

Raised and pushed as its own standalone coordination commit (`4c141f6`):
`demands/2026-08-04-app-studio-repin-binding-direction-array.md`, id
`contracts-20260804-app-studio-repin-binding-direction-array`, to `app-studio`
— re-pin to v0.21.0 and read the field as a list.

On the breaking leg (demand *every* consumer of the changed schema): it
resolves to `app-studio` alone. The only other reader of `app.mission` is
state-feed's `AppMissionEvent` payload, added in v0.20.0, which carries
`missionId` / `appName` / `stage` / `currentWave` / `gate` / `outcome` /
`gateWave` — no `gateContext`, so no exposure to this change. **Caveat for the
coordinator:** D043 says to enumerate consumers from control-plane's
`GET /registry` consumer graph rather than a guess, and that service was not
reachable from this session — the enumeration above is from the schemas in this
repo. If the registry shows another `gateContext` reader, a second demand is
owed.

## Acceptance criteria

| criterion | status |
|---|---|
| accepts an array of strings, still accepts null | met — schema `["array","null"]`; both covered as positive cases |
| two-rejection fixture validates, added as a permanent positive fixture | met — `twice-rejected-gate-mission.json`, plus a bare-string negative so the list form cannot be lost again |
| tutor pilot fixture still validates unchanged | met — file not edited; `gateContext: null`; validates |
| released as its own version, notes say a string-typed consumer will break | met — v0.21.0, minor-with-breaking per the v0.11.0 precedent; notes state it in those words |
| D043 re-pin demand back to app-studio | met — `contracts-20260804-app-studio-repin-binding-direction-array`, commit `4c141f6`, pushed |

## Nothing outside this repo was touched

No change was made in `app-studio` or any other repo. The consuming leg is
`app-studio`'s to close, via the demand above.
