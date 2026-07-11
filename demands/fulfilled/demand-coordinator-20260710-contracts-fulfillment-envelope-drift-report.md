---
demandId: demand-coordinator-20260710-contracts-fulfillment-envelope-drift
worker: contracts
status: done
shipped: ["v0.11.0 (schema/bindings/CHANGELOG committed to main; tag/push pending explicit go-ahead)"]
date: 2026-07-11
---

# Fulfillment report — contracts: reconcile `demand.fulfillment`'s fields with real fleet usage

`status: done` here is a claim, not a verdict — per DEMAND_SYSTEM.md §4, this
report is `contracts`' only output for this demand. `contracts` does not
self-certify and has not notified `demand-coordinator` directly; the
coordinator assembles and delivers the summary once the owner approves.

This report itself uses the new `shipped`/`date` fields and omits
`summaryRef` — the change it documents, exercised on itself.

## What shipped

`schemas/demand-coordinator/demand.fulfillment.json` updated per the demand's
already-landed owner ruling (resolve via schema, not fleet migration — option
(a) of the two the demand flagged): `summaryRef` required → optional;
new optional `shipped` (`array` of `string`) and `date` (`string`, `format:
date`). `additionalProperties: false` unchanged. `DEMAND_SYSTEM.md` §5 needed
no correction, per the demand's own acceptance criteria — it already
documented this shape; only the schema was out of step.

All three bindings regenerated and verified (full detail in `CHANGELOG.md`'s
`v0.11.0` entry — summarizing here):

- **Java:** `mvn -B -f gen/java/pom.xml clean test` — `BUILD SUCCESS`,
  `Tests run: 12, Failures: 0, Errors: 0` (unchanged; no existing test
  touches `DemandFulfillment`). `DemandFulfillment.java` inspected directly:
  `summaryRef` no longer `(Required)`, `shipped: List<String>` and
  `date: String` present.
- **TypeScript:** `npx json-schema-to-typescript` regenerated
  `demand-fulfillment.ts`; `dist/` rebuilt (`npm run build`, committed per
  D031). `npx tsc --noEmit --strict` clean. `summaryRef?: string`,
  `shipped?: string[]`, `date?: string` in the interface.
- **Python:** `datamodel-codegen ... --target-python-version 3.11
  --use-specialized-enum` regenerated `demand_fulfillment.py`. The two flags
  matter: without them this session's installed `datamodel-code-generator`
  (0.68.1) emits a plain `Enum` for `Status`, diverging from every other
  generated module in this repo (`demand.py`, `telemetry.py`, etc., all
  `StrEnum`) — caught by diffing the regenerated file against the prior one
  before committing, since no existing test would have caught the drift (no
  test round-trips `status` through JSON serialization, only schema-level
  validation, which doesn't care about the Python enum base class). Full
  `python tests/run_all.py` — all validators pass, including the updated
  `validate_demand.py`.

### tests/validate_demand.py

Found and fixed a test correctness issue while touching this file: the
existing `BAD_FULFILLMENT` fixture's label said "missing summaryRef" as part
of why it was invalid — true before this change, no longer true after
(`summaryRef` is optional now; the fixture is invalid solely on its bad
`status: "in-progress"` value). Relabeled, and added
`GOOD_FULFILLMENT_SHIPPED_DATE_NO_SUMMARY_REF` to positively exercise the new
fields together with `summaryRef`'s absence.

## What demand-coordinator (the origin) needs to know

1. **Consume via:** re-pin `contracts` to `v0.11.0` once the D031 acceptance
   test below has run for real against the pushed tag (not yet — see below).
2. **Your own follow-ups, per the demand's "what we do once closed"** (not
   done by this report — `demand-coordinator` repo, out of scope for a
   `contracts` session):
   - Remove `DemandEnvelopeParser`'s `shipped`/`date` side-channel
     `JsonNode` extraction; bind them directly off the regenerated
     `DemandFulfillment` class instead.
   - Drop this demand's workaround note from the parser's javadoc and
     `CHANGELOG.md`'s 2026-07-10 entry.
   - Move `demands/2026-07-10-contracts-fulfillment-envelope-drift.md` to
     `demands/archive/` in your own repo.
3. **Wire format is backward compatible.** Every existing fulfillment report
   in the fleet that set `summaryRef` (and none did) still validates; the
   change only relaxes a requirement and adds two optional fields —
   `additionalProperties: false` was not touched, so no other shape drift is
   possible.

## Verification status

Local toolchain available this session: Maven 3.9.16 + JDK 21 (no Docker
needed, unlike some prior releases), Node/npm, Python 3.11 venv with
`datamodel-code-generator` 0.68.1 pre-installed. No unverified leg on the
local-build side.

- **Java:** real `mvn clean test`, not Docker-simulated — see above.
- **TypeScript:** real `tsc --noEmit --strict`, `dist/` rebuilt and diffed
  (confirmed only `demand-fulfillment.d.ts` has real content changes;
  `telemetry.d.ts`/`telemetry.js`/`index.d.ts` showed as modified in `git
  status` from a stray rebuild but diffed byte-identical, no line-ending
  drift committed).
- **Python:** real `pip`-installed toolchain in this repo's own `.venv`,
  full `tests/run_all.py` run, not just the one new fixture.
- **D031 real acceptance test — NOT yet run.** No tag exists yet. Per the
  standing invariant, this must be run for real against the pushed
  `v0.11.0` tag (Java: fresh `.m2` install from a clean clone; Python: fresh
  venv + git-URL pip install; TS: the `file:`-dependency form can be
  exercised pre-tag, matching the v0.10.0 precedent) before any consumer
  re-pins.

## Acceptance criteria — self-check against the demand

- [x] `demand.fulfillment.json` gains optional `shipped` (array of strings)
      and `date` (`format: date`); `summaryRef` no longer required.
      `additionalProperties: false` unchanged.
- [x] New `contracts` tag prepared with the updated schema + regenerated
      Java/TS/Python bindings, per the existing per-language versioning
      convention (`v0.11.0`, minor — additive only). **Tag not yet cut/pushed
      — pending explicit go-ahead, per this repo's own tagging/push
      convention (owner or session operator authorizes the actual `git tag`
      + `git push --tags` step separately from the code change).**
- [x] `DEMAND_SYSTEM.md` §5 needed no correction — confirmed; not touched.

## Open items for the architect / next session

1. **Tag/push still pending.** Schema, bindings, tests, and CHANGELOG are
   done and verified locally; `git tag v0.11.0 && git push origin main
   --tags` per `DEPLOYMENT.md`'s release checklist, then the post-tag D031
   acceptance run, are the only remaining steps.

## Fixed in passing

`DEPLOYMENT.md`'s Python regeneration section didn't record
`--target-python-version 3.11 --use-specialized-enum`, and this session's
installed `datamodel-code-generator` (0.68.1) defaults to a plain `Enum`
without them — diverging from every other generated module's `StrEnum`.
Added a paragraph noting the flags and why, so a future session's toolchain
doesn't silently reintroduce the drift.
