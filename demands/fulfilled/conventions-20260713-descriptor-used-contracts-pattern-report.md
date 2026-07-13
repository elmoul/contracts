---
demandId: conventions-20260713-descriptor-used-contracts-pattern
worker: contracts
status: done
shipped: ["v0.12.0"]
date: 2026-07-13
---

# Fulfillment report — contracts: pattern-constrain `hexagon.descriptor`'s `contracts.used` items

`status: done` here is a claim, not a verdict — per `DEMAND_SYSTEM.md` §4,
this report is `contracts`' only output for this demand. `contracts` does not
self-certify and has not notified `conventions` directly; the coordinator
assembles and delivers the summary once the owner approves.

## What shipped

`schemas/control-plane/hexagon.descriptor.json`'s `contracts.used` items
schema changed from a bare `{"type": "string"}` to:

```json
{ "type": "string", "pattern": "^[a-z][a-z0-9]*([.-][a-z0-9]+)*$" }
```

exactly the pattern the demand proposed — no changes needed, it already
matched every real id in fleet use and rejected every audited free-text form.
Description also updated to state the field is a machine-readable contract
id, not free text.

All three bindings regenerated and verified (full detail in `CHANGELOG.md`'s
`v0.12.0` entry — summarizing here):

- **Java:** `mvn -B -f gen/java/pom.xml clean test` — `BUILD SUCCESS`,
  `Tests run: 12, Failures: 0, Errors: 0` (unchanged; no existing test
  touches `Contracts.used`). `Contracts.java` inspected directly: confirmed
  jsonschema2pojo 1.2.1 does **not** emit a `@Pattern` annotation for this
  field even with `useJakartaValidation=true` — same pre-existing behavior as
  `functionalName`'s and `decisions`' own `pattern` constraints in this same
  schema, not a regression. Only the field's Javadoc/description changed.
- **TypeScript:** `npx json-schema-to-typescript` regenerated
  `hexagon-descriptor.ts`; `dist/` rebuilt (`npm run build`, committed per
  D031). `npx tsc --noEmit --strict` clean. `used: string[]` unchanged
  type-wise — the tool doesn't encode `pattern` into the type system, same as
  `functionalName`.
- **Python:** `datamodel-codegen ... --target-python-version 3.11
  --use-specialized-enum` regenerated `hexagon_descriptor.py`.
  `Contracts.used` is now `list[constr(pattern=r'^[a-z][a-z0-9]*([.-][a-z0-9]+)*$')]`
  — Python is the one binding that actually enforces the constraint at
  parse/construction time, consistent with how `functionalName`/`decisions`
  already behave in this same model. Full `python tests/run_all.py` — all
  validators pass, including the updated `validate_control_plane.py`.

### tests/validate_control_plane.py

Added `GOOD_USED_CONTRACT_IDS` (the six real ids the demand named:
`state.event`, `ai.preflight.request`, `build-command`, `registry.entry`,
`usage.event`, `state.event.activity.count`) and `BAD_USED_CONTRACT_IDS` (the
three audited free-text forms: `sentinel-hub`'s `"ai.request / ai.response /
ai.blocked"`, `publishing`'s `"ai.preflight (blocked-response shape only, via
ai-gateway's 402)"`, and the generic `"state.event (activity.count)"`
shape), each exercised against `hexagon.descriptor.json` via the existing
`expect_valid`/`expect_invalid` helpers. All pass, matching every clause of
the demand's acceptance criteria exactly.

## Owner ruling recorded (per acceptance criterion 3)

**Breaking, not additive.** `sentinel-hub`'s and `publishing`'s existing
`HEXAGON.md` descriptors carry the exact free-text `used` entries this
schema now rejects — re-validating either against this schema fails. Owner
ruling accepted that cost: the field is mechanically unusable as the D015
rebuild-set input otherwise, and the repo-side `conventions` validator
already treats the same shapes as defects, so this isn't introducing a new
standard, just making the existing one schema-enforceable.

**Versioning:** bumped minor (`v0.11.0` → `v0.12.0`), not the major digit.
This repo's own precedent (`CHANGELOG.md`'s `v0.2.0` entry) reserves an
actual major-version bump for a `1.0.0` stability declaration — a separate
decision from classifying a given change as breaking while the package sits
at `0.y.z`. This release is arguably the real trigger that precedent
anticipated (unlike `v0.2.0`, this one has genuine fleet documents that fail
against the new schema, not just an unused type), but declaring `contracts`
platform-wide 1.0 stability is a bigger decision than this demand asked for
and is left to an explicit owner call, not inferred here. Full reasoning in
`CHANGELOG.md`'s `v0.12.0` entry.

## What conventions (the origin) needs to know

1. **Consume via:** re-pin `contracts` to `v0.12.0`, per the demand's "what
   we do once closed." The schema-side constraint is now live; the
   `rules.yaml` `contracts_hygiene.contracts_pin_declared.schema_side_note`
   update described there is `conventions`' own follow-up, out of scope for
   this report.
2. **Not done by this report, out of scope for a `contracts` session:**
   fixing `sentinel-hub`'s and `publishing`'s non-conforming `used` entries.
   Both repos' descriptors will fail validation against `v0.12.0` the next
   time anything validates them against this schema (today: the
   `conventions` validator repo-side; going forward, potentially
   control-plane or any tooling that parses `HEXAGON.md` frontmatter through
   this contract). Flagging so `conventions` can route the fix or a
   transition-period accommodation to those two repos directly — `contracts`
   does not reach into consumer repos.
3. **Validator rule stays regardless**, per the demand's own note — it
   remains load-bearing for repos still pinned to a pre-`v0.12.0` tag.

## Verification status — D031 real acceptance test, post-tag, all three languages

Owner instruction for this session explicitly authorized cutting and pushing
the tag as part of this demand's fulfillment. `v0.12.0` tagged and pushed;
**post-tag D031 acceptance run for real against the pushed tag, no
unverified leg:**

- **Java:** independent fresh `git clone --branch v0.12.0` (no relationship
  to the working session's tree), `mvn -B clean install -DskipTests` into a
  scratch `.m2` — `BUILD SUCCESS`, installed `io.platform:contracts:0.12.0`.
  A second, fully independent scratch Maven project declaring that
  coordinate as an ordinary dependency compiled and ran code constructing a
  `Contracts` object with `used: ["ai.preflight.request", "state.event"]` —
  `BUILD SUCCESS`, printed object confirms the value round-tripped through
  the real installed jar.
- **Python:** fresh venv, `pip install
  "git+https://github.com/elmoul/contracts.git@v0.12.0#subdirectory=gen/python"`
  — installed cleanly. Constructed a `HexagonDescriptor`, round-tripped via
  `model_dump_json()` → `model_validate_json()`, and confirmed the new
  pattern rejects `"ai.request / ai.response / ai.blocked"` with a real
  `ValidationError` raised by the installed package (not the local dev
  checkout).
- **TypeScript:** scratch project depending on `"@platform/contracts":
  "file:<tagged-checkout>/gen/ts"` (the tagged checkout's committed `dist/`,
  per D031, not the local working copy), `npm install`, then a `.ts` file
  constructing a `HexagonDescriptor` object literal with a real
  `contracts.used` array — `npx tsc --noEmit --strict` clean (exit 0).
- No unverified leg anywhere in this release. Scratch clones/venvs/projects
  deleted after verification.

## Acceptance criteria — self-check against the demand

- [x] `contracts.used` items carry a `pattern`
      (`^[a-z][a-z0-9]*([.-][a-z0-9]+)*$`) instead of a bare `{type: string}`.
- [x] Pattern accepts all six real ids named in the demand, rejects all three
      audited free-text entries — exercised in
      `tests/validate_control_plane.py`, all pass.
- [x] Owner ruling recorded: breaking (major), not additive — see above and
      `CHANGELOG.md`'s `v0.12.0` entry.
- [x] All three language bindings regenerated + D031 acceptance run per the
      standing invariant; `v0.12.0` tagged and pushed
      (`git tag v0.12.0 && git push origin main --tags`). **`v0.12.0` is now
      pinnable per D031.**
