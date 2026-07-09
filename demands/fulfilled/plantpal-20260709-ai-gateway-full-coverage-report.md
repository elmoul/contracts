---
demandId: plantpal-20260709-ai-gateway-full-coverage
subDemand: plantpal-20260709-ai-gateway-full-coverage:contracts
worker: contracts
status: done
summaryRef: demands/fulfilled/plantpal-20260709-ai-gateway-full-coverage-report.md
---

# Fulfillment report — contracts: ai.model-manifest schema (gap G5)

`status: done` here is a claim, not a verdict — per DEMAND_SYSTEM.md §4, this
report is `contracts`' only output for its leg of this demand. This is a
**multi-hexagon join** (`to: [ai-gateway, contracts]`) — the coordinator will
not mark the whole demand `pending-approval` until `ai-gateway`'s sub-demand
also reports. `contracts` does not self-certify and has not notified
`plantpal` or `ai-gateway` directly.

**Scope note:** this report covers only §4 (gap G5) of the demand — the new
`ai.model-manifest` contract. Gaps G1–G4 and G6, and the streaming-session
design in §3, are entirely `ai-gateway`'s leg; nothing about them was
implemented or judged here.

## What shipped

Branch `demand/plantpal-model-manifest`, pushed to `origin`, not yet merged or
tagged (the architect tags after review/merge, per this session's brief —
version recorded in `CHANGELOG.md` as the upcoming `v0.9.0`).

Commits, in order:

1. `22837d6` — `feat(ai-gateway): v0.9.0 -- add ai.model-manifest schema (gap G5)`
   — the schema itself, `schemas/ai-gateway/model-manifest.json`.
2. `cc6dba0` — `feat(ai-gateway): wire model-manifest.json into gen/java/pom.xml (v0.9.0)`
3. `96998be` — `feat(ai-gateway): v0.9.0 -- TS model-manifest.ts binding + rebuilt dist/`
4. `908cd24` — `feat(ai-gateway): v0.9.0 -- Python model_manifest.py binding (hand-written, unverified)`
5. `3f24ec2` — `test(ai-gateway): add validate_model_manifest.py, wire into run_all.py`
6. `ae29275` — `docs(changelog): v0.9.0 -- ai.model-manifest release notes`

### Final schema shape

`schemas/ai-gateway/model-manifest.json` — a **plain JSON Schema** (not
OpenAPI), because a model manifest is a static per-app declaration file (the
demand's own proposal: `ai-model-manifest.yaml` at each app's repo root,
sibling to `app-manifest.yaml`), not a sync HTTP call. This puts it in the
same family as `hexagon.descriptor.json` validating `HEXAGON.md`'s
frontmatter, rather than the OpenAPI-document shape of `ai.request`/
`ai.preflight`. Filed under `schemas/ai-gateway/` (the existing catalog group)
since it's an ai-gateway contract by function, even though its file format
differs from its two siblings there.

```
AiModelManifest {
  appId: string            // pattern ^[a-z][a-z0-9-]+$, same as app.manifest/hexagon.descriptor
  class: enum               // low-stakes | health-class | kids-class (D010, same enum everywhere else)
  capabilities: {           // map, keyed by capability name (kebab-case) -- not an array
    <capability-name>: {
      models: string[]        // required, minItems 1, uniqueItems -- preference order, free-form identifiers
      media: enum              // required -- required | optional | none
      downshiftPolicy: enum     // required -- allow | block | skip (D023)
      streamingDesired?: bool   // optional, default false
    }
  }
}
```

**Design decisions** (full rationale in `CHANGELOG.md`'s `v0.9.0` entry —
summarized here for the origin's follow-up):

- **Map, not array, for `capabilities`.** Keying by capability name lets the
  gateway do a direct lookup at request time (`manifest.capabilities[capability]`)
  and makes "no capability declared twice" a free property of JSON objects,
  rather than a `uniqueItems`-style rule bolted onto an array.
- **Three explicit axes per capability**, exactly the ones the demand's §4
  asked for: `models` (preference-ordered, free-form strings — deliberately
  not an enum, so a new provider model never forces a schema bump),
  `media` (`required | optional | none`, no default — the gateway must never
  have to *infer* whether a missing `media` array on an incoming `ai.request`
  is expected or an error), `downshiftPolicy` (`allow | block | skip`, D023 —
  `skip` is new relative to the demand's own illustrative YAML's bare
  `downshift: skip` value; formalized as a first-class enum member alongside
  `allow`/`block` since PlantPal's own worked example already uses it for
  `annotation`).
- **`streamingDesired` is a plain boolean**, not the demand draft's bare
  `streaming: desired` marker — only two meaningful states exist (wanted /
  not), so a three-value enum would have been dead weight. Default `false`.
  Advisory only: a capability may declare `streamingDesired: true` today and
  keep calling the buffered `/ai/request` endpoint until §3's session flow
  ships — this schema does not enforce or gate on it.
- **Casing decision (asked to be explicit about, since v0.8.0 left one
  casing question open for a future ruling):** this schema's own field names
  are **camelCase** (`appId`, `downshiftPolicy`, `streamingDesired`),
  matching `ai.request`/`ai.preflight`/`app.manifest` — its structural
  siblings, all camelCase. This is the opposite choice from `demand`'s
  kebab-case fields, and deliberately so: that decision was preserving an
  on-disk convention *already live* in committed `demands/*.md` files before
  the schema existed. No `ai-model-manifest.yaml` has been committed
  anywhere yet (PlantPal's is still just the demand's illustrative draft) —
  there is no pre-existing convention to preserve, so this schema defaults to
  the repo's dominant camelCase instead of inventing a third style. Capability
  *names* (the map's keys, e.g. `vision-identification`) stay kebab-case,
  since they're enum-shaped identifier values, matching how `class`'s own
  enum values (`health-class`) are kebab-case in an otherwise-camelCase
  schema — a value-vs-field-name distinction, not an inconsistency.
- **`class` included at the top level**, mirroring `app.manifest`/
  `hexagon.descriptor`'s D010 field exactly. Advisory to the
  gateway/control-plane (e.g. a `health-class` app declaring `downshift:
  allow` on a diagnostic capability is a stronger review signal than the same
  declaration from a `low-stakes` app) — not schema-enforced here; policy
  belongs to the gateway/conventions-validator layer, the same split
  `hexagon.descriptor.json` already draws for its own `class` field.

## What ai-gateway (the next target) needs to know

1. **Consume via:** `pip install`/`npm`/`mvn` pin per D031 once this branch is
   reviewed, merged, and tagged `v0.9.0` — the architect cuts the tag, not
   this session. Add the usual `contracts:` block (`pin: v0.9.0`, `binding`,
   `used: [ai.model-manifest, ...]`) to `ai-gateway/HEXAGON.md` once pinned.
2. **Lookup pattern:** at startup, parse each registered app's
   `ai-model-manifest.yaml` against this schema, then index
   `capabilities[requestedCapability]`. An incoming `ai.request`'s
   `modelHint` should be checked against that capability's `models` array —
   unknown `modelHint` → 400, which is what closes G6's "unmapped appId gets
   no guardrail" and "unknown modelHint silently falls back to Anthropic"
   holes. This schema does not itself implement that validation — it only
   makes the declaration a first-class, checkable structure instead of
   free-text `modelHint` improvisation.
3. **`downshiftPolicy` is the gateway's D023 policy input**, not a suggestion:
   `block` must produce the existing explicit block response (never a silent
   downshift); `skip` means the gateway should omit the call rather than
   either downshift or hard-block — this is new behavior beyond what
   `ai.preflight`'s existing `allow/downshift/block` decision enum covers on
   its own, since `skip` is a capability-level policy decision made *before*
   preflight is even called, not a preflight outcome.
4. **`media` is advisory input for request-shape validation**, not enforced
   by this schema — if `ai-gateway` wants to reject an `ai.request` whose
   `media` array is empty/absent for a capability declared `media: required`,
   that check lives in `ai-gateway`, reading this manifest; `contracts`
   provides the declared value, not the enforcement.
5. **`streamingDesired` has no consumer yet** — it exists so the manifest is
   forward-compatible with the demand's §3 session/streaming design once
   `ai-gateway` builds `POST /ai/session`; until then it's inert metadata.
6. **The illustrative YAML in the demand is not this schema verbatim** — most
   notably `downshift` → `downshiftPolicy`, and `media`/`streaming` are now
   fully-specified enums/booleans rather than bare present/absent markers.
   Point PlantPal (once it writes its real `ai-model-manifest.yaml`) at this
   schema, not at its own demand draft.

## Verification status — read before trusting anything above as "tested"

This sandbox had **no JDK/Maven and no Python interpreter available** (both
confirmed absent from PATH; Python resolves only to the Windows Store
install-stub, no local install found on disk anywhere). Toolchain reality is
worse this session than v0.8.0's (which at least had Python for the real
`jsonschema`/pydantic checks).

- **Schema itself:** verified sound. Six fixtures (2 valid, 4 invalid —
  missing required capability field, non-kebab-case capability key, unknown
  `downshiftPolicy` value, empty `models` list, missing top-level
  `appId`/`class`) were checked directly against
  `schemas/ai-gateway/model-manifest.json` using `ajv-cli`
  (`npx ajv-cli@5 validate --spec=draft2020`, matching this schema's declared
  draft). All six behaved as expected.
- **TypeScript: fully verified.** `npx tsc --noEmit --strict` clean; `npx tsc`
  (the actual `dist/` rebuild used for D031 consumption) also clean. `dist/`
  committed.
- **Java: NOT verified.** No `mvn`/`java` in this sandbox. Beyond the routine
  gap (same as v0.8.0), this release carries a genuinely new risk: this
  schema's `capabilities` field is the first pure schema-typed dictionary
  (object with no declared `properties`, only `additionalProperties` as a
  `$ref`) anywhere in this repo's Java codegen. Every prior Map-typed field
  here was a *permissive bag* (`additionalProperties: true`) needing an
  explicit `existingJavaType` override. This is structurally different, and
  I deliberately did **not** add an override — doing so risked
  short-circuiting `CapabilityDeclaration`'s own generation (its only `$ref`
  in this schema is inside `capabilities.additionalProperties`). Trusting
  jsonschema2pojo's documented native dictionary-schema handling is the
  lower-risk call, but it is untested. **Run `mvn clean test` in `gen/java`
  from a real JDK 21 + Maven environment and confirm
  `AiModelManifest.getCapabilities()` compiles as `Map<String,
  CapabilityDeclaration>`** before any Java consumer (possibly `ai-gateway`
  itself) pins this tag.
- **Python: NOT verified, and more seriously than the routine gap.**
  `platform_contracts/ai_gateway/model_manifest.py` was **hand-written** to
  match `datamodel-code-generator`'s established style in this package (not
  generator output) because no Python interpreter existed to run the
  generator. It has never been imported, round-tripped, or run against a
  known-bad document. Before any Python consumer pins this tag: regenerate
  via `datamodel-code-generator` from `model-manifest.json` and diff against
  this file; independently, `pip install ./gen/python` in a fresh venv and
  round-trip an `AiModelManifest` instance.
- **D031 real acceptance test (clean install from the tagged URL, all three
  languages) not run — cannot be, until this release is tagged.**

## Acceptance criteria — self-check against the demand's §4

- [x] `ai.model-manifest` schema exists under `schemas/`, covering all three
      axes named in the task brief (model sets/preference order, media
      requirement, streaming desire, per-capability downshift policy).
- [x] Bindings drafted for all three languages (Java/TS/Python), wired into
      `pom.xml`/`index.ts`/`__init__.py` respectively.
- [x] Tests added and wired into `tests/run_all.py`.
- [x] CHANGELOG entry written as `v0.9.0` (tag **not** cut — architect's
      call, per instructions).
- [ ] Java binding compiled/tested — **not done, flagged above**.
- [ ] Python binding executed/round-tripped — **not done, flagged above**.
- [ ] `ai-gateway`'s consuming leg (validating `modelHint` against this
      manifest, keying guardrails off it) — out of scope for this report
      entirely; that's `ai-gateway`'s sub-demand, still open.

## Open questions for the architect

1. **Java Map-shaped-schema handling is unverified and untested anywhere in
   this repo before now** — worth a deliberate first real-JDK verification
   pass on this specific execution before the tag is cut, given it's a new
   pattern (not just a routine "no JDK available" repeat).
2. **Should `ai-model-manifest.yaml`'s file location be codified somewhere
   machine-checkable** (e.g. added to `hexagon.descriptor.json`'s
   `contracts.used` convention, or a new top-level field), or does prose in
   this report / the eventual `ai-gateway` spec suffice? Not something I
   should decide unilaterally, since it touches `hexagon.descriptor`'s shape.
3. **`downshiftPolicy: skip`** is new relative to `ai.preflight`'s existing
   `allow/downshift/block` decision vocabulary — worth confirming with
   whoever specs `ai-gateway`'s consuming logic that "skip" is understood as
   a pre-preflight capability-level decision, not a fourth preflight outcome,
   before that spec gets written.
