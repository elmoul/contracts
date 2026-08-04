---
demandId: app-studio-20260804-contracts-verify-step-channel
worker: contracts
date: 2026-08-04
status: done
shipped: ["v0.22.0", "commit 507e4ff on main", "tag v0.22.0", "schemas/app-studio/app.task-plan.json ($defs.verifyStep.channel: optional string)", "gen/ts/app-task-plan.ts + gen/ts/dist (channel?: string)", "gen/python/platform_contracts/app_studio/app_task_plan.py (channel: str | None = None)", "io.platform.contracts.appstudio.VerifyStep (private String channel)", "tests/validate_app_studio.py (3 new cases: absence-step-with-channel positive, channel-omitted positive, channel-as-list negative)", "CHANGELOG.md v0.22.0 additive entry", "demand contracts-20260804-app-studio-repin-verify-step-channel (commit f42d00b)"]
---

# Fulfillment — `contracts`: verify step gains an optional `channel`

`status: done` here is a claim, not a verdict — per `DEMAND_SYSTEM.md` §4 this
report is `contracts`' only output for this demand. `contracts` does not
self-certify and has not notified `app-studio` directly; the coordinator
validates and delivers the summary.

## Pre-work state check

Checked first, as instructed: the capability was **not** already shipped. At
`7c96e68` (newest release `v0.21.0`), `$defs.verifyStep` in
`schemas/app-studio/app.task-plan.json` declared exactly three properties —
`run`, `manual`, `expect` — under `additionalProperties: false`, so a step
carrying `channel` was not merely undocumented, it was actively rejected. All
three generated bindings agreed (no `channel` in the TS interface, the pydantic
model, or the Java pojo). The work below was done from scratch in this session.

## What shipped

### The schema change

`$defs.verifyStep` gains:

```json
"channel": {
  "type": "string",
  "description": "For an absence claim only: the input path (field, map key, header, argument) that could carry the thing being excluded. Optional, and meaningless on a positive step — a step asserting something IS there needs no channel. An absence step without one is unfalsifiable: \"the secret never reaches the provider\" is only checkable once you name where it would have travelled if it did."
}
```

The demand's wording is carried verbatim as the first sentence; the rest states
why the field is optional rather than required, so the next reader does not
"tighten" it into a required property.

The modelling point, for the record: `expect` says what must not be true, and
on an absence step that is only half a pass condition. "The API key never
reaches the provider" cannot be checked until the step names where the key
would have travelled if it had — the `metadata` map on the outbound request,
the `Authorization` header, the argument handed to the tool. `channel` is that
path. On a positive step there is nothing to name, which is why it is optional
by construction and not conditionally required on some absence flag: the schema
has no way to tell an absence claim from a positive one (`expect` is prose),
and inventing one would have been a second, larger change than the demand
asked for.

### Optionality — asserted, not assumed

`channel` is absent from `verifyStep.required` and every existing artifact
validates unchanged. Three new cases in `tests/validate_app_studio.py` pin
this down (32 app-studio checks now, up from 29):

- **positive** — an absence step carrying
  `channel: "the \`metadata\` map on the outbound provider request"` validates.
  This is the case that fails if anyone drops the property while
  `additionalProperties: false` is in force.
- **positive** — the identical step with `channel` deleted still validates:
  optional, not conditionally required.
- **negative** — `channel` as a list of paths is **rejected**. It is one input
  path stated in words; typed loosely it becomes the free-form dumping ground
  the description exists to prevent.

The pre-existing pilot-plan positive (`tutor-pilot-plan.json`, the real
owner-approved artifact, which carries no `channel` on any of its steps)
is the standing proof of the "every existing plan artifact validates unchanged"
criterion. That fixture was **not edited** — its byte-for-byte-verbatim
property, which D066 build-then-extract depends on, is intact.

### Bindings regenerated

All three, from the changed schema, using the documented `DEPLOYMENT.md`
commands (`json-schema-to-typescript` + `npm run build`, `datamodel-codegen`,
`jsonschema2pojo` via Maven):

| binding | v0.22.0 |
|---|---|
| TypeScript | `channel?: string` on `VerifyStep` |
| Python | `channel: str \| None = None` |
| Java | `private String channel` on `VerifyStep` |

The Python regeneration was diffed against the previous file per DEPLOYMENT.md's
warning: the only changes are the header timestamp and the four added lines —
no silent convention drift.

Repo suites green before the tag: `python tests/run_all.py` (all validators,
32 app-studio checks, state-event sync) and `mvn -B -f gen/java/pom.xml test`
(26 tests).

## Release call — v0.22.0, additive

Additive change (a new optional field) bumps minor, per the rule at the top of
`CHANGELOG.md`. Nothing here breaks: no removal, no rename, no new required
field. The one wrinkle worth naming, and named in the release notes, is
Java-specific and source-level only — jsonschema2pojo's all-args `VerifyStep`
constructor gains a fourth parameter, so a Java call site using that
constructor (rather than no-arg + setters) needs the extra argument. Getters,
setters and JSON round-tripping are unchanged, and no consumer is obligated to
move at all: D031 pins are deliberate and this release is additive.

## D031 acceptance — run against the real tag, not a local build

Per the standing invariant, all three bindings were installed from the pushed
`v0.22.0` tag into a fresh venv / npm cache / `.m2`, and the field confirmed in
each *installed* artifact:

- **Python** — `pip install --no-cache-dir
  "git+https://github.com/elmoul/contracts.git@v0.22.0#subdirectory=gen/python"`
  in a fresh venv. `VerifyStep(..., channel="the metadata map")` constructs and
  reads back; `channel` omitted yields `None`; `channel=["a"]` raises
  `ValidationError`. All three as expected.
- **TypeScript** — fresh `git clone --branch v0.22.0`, then a `file:` dependency
  on the checkout's `gen/ts` per `DEPLOYMENT.md` (npm's `github:owner/repo#tag`
  form does not work for this repo — `package.json` lives at `gen/ts`, not the
  repo root). Under `strict`, a step with `channel: "…"` and a step without it
  both compile; `channel: ["a"]` fails with
  `TS2322: Type 'string[]' is not assignable to type 'string'`.
- **Java** — `mvn install -Dmaven.repo.local=<fresh>` from the tagged checkout.
  `contracts-0.22.0.jar` installs, and `javap` on the compiled `VerifyStep`
  inside the jar shows `private java.lang.String channel`,
  `public java.lang.String getChannel()`, `public void setChannel(String)`.

## D043 release notification

Raised and pushed as its own standalone coordination commit (`f42d00b`):
`demands/2026-08-04-app-studio-repin-verify-step-channel.md`, id
`contracts-20260804-app-studio-repin-verify-step-channel`, to `app-studio` —
re-pin to v0.22.0, fill `channel` on absence steps, drop the recorded gap.

Origin demand only. D043's consumer-wide leg fires on breaking releases; this
one is additive, so there is deliberately no fleet-wide "everyone bump".
`app.task-plan` has no reader in this repo other than `app-studio` — state-feed's
`AppMissionEvent` payload reads mission fields, not the plan. **Caveat for the
coordinator:** D043 says to enumerate consumers from control-plane's
`GET /registry` consumer graph rather than a guess, and that service was not
reachable from this session; the enumeration above is from the schemas in this
repo. It only affects the additive case's already-empty consumer list, so
nothing is owed unless the registry shows an unexpected `app.task-plan` reader.

## Acceptance criteria

| criterion | status |
|---|---|
| verify-step object accepts an optional string `channel`, documented as the demand words it | met — property added with the demand's wording as its first sentence |
| optional — every existing plan artifact validates unchanged | met — not in `required`; pilot-plan fixture untouched and still passing, plus an explicit channel-omitted positive case |
| a version bump is published and pinnable so app-studio can re-pin | met — `v0.22.0` tagged and pushed; all three bindings installed from the tag and verified (D031) |

## Nothing outside this repo was touched

No change was made in `app-studio` or any other repo. The consuming leg —
re-pinning and dropping the recorded gap — is `app-studio`'s to close, via the
demand above.
