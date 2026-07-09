---
demandId: demand-coordinator-20260709-demand-schema
worker: contracts
status: done
summaryRef: demands/fulfilled/demand-coordinator-20260709-demand-schema-report.md
---

# Fulfillment report — contracts: demand + demand.fulfillment schemas

`status: done` here is a claim, not a verdict — per DEMAND_SYSTEM.md §4, this
report is `contracts`' only output; the coordinator marks it
`pending-approval` and only the owner's approval makes it real. `contracts`
does not self-certify and has not notified `demand-coordinator` directly.

## What shipped

Tag `v0.8.0` (https://github.com/elmoul/contracts.git@v0.8.0), pushed to
`main` at commit `85c227f`.

- **New schema group** `schemas/demand-coordinator/`:
  - `demand.json` — validates `demands/*.md` frontmatter: `id`, `date`,
    `from`, `to[]`, `capability`, `acceptance-criteria[]`, `needs-owner`,
    `status` (`open | satisfied | archived`).
  - `demand.fulfillment.json` — validates
    `demands/fulfilled/<demand-id>-report.md` frontmatter: `demandId`,
    `subDemand` (optional, multi-hexagon joins only), `worker`, `status`
    (`done | blocked`), `summaryRef`.
- **Bindings, all three languages**, wired the same way as the existing
  `control-plane` schema group (`hexagon.descriptor`/`registry.entry`
  precedent):
  - **Java:** new `jsonschema2pojo` execution in `gen/java/pom.xml`
    (`io.platform.contracts.demandcoordinator`, package `Demand`/
    `DemandFulfillment`).
  - **TypeScript:** `demand.ts`/`demand-fulfillment.ts`, re-exported from
    `index.ts`, `dist/` rebuilt and committed (D031).
  - **Python:** `platform_contracts/demand_coordinator/{demand,
    demand_fulfillment}.py`, wired into the package `__init__.py`.
- **Tests:** `tests/validate_demand.py` (known-good/known-bad documents for
  both schemas), wired into `tests/run_all.py`.

Full design rationale, including a **deliberate casing split** between the
two schemas (kebab-case in `demand`, matching already-committed demand-file
frontmatter; camelCase in `demand.fulfillment`, matching
spec-demand-coordinator.md §7's interim convention verbatim) and the exact
codegen invocations, is in `CHANGELOG.md`'s `v0.8.0` entry — not repeated
here.

## What the origin (demand-coordinator) needs to know

1. **Pin `v0.8.0`** in `demand-coordinator/pom.xml`, then add the
   `contracts:` block to its `HEXAGON.md` (`pin: v0.8.0`, `binding: java`,
   `used: [demand, demand.fulfillment]`) per your own "What we do once
   closed."
2. **Java binding is unverified.** This sandbox had no JDK/Maven available
   (`mvn`/`java` absent from PATH, no local `.m2`/JDK found) — the
   `jsonschema2pojo` execution was hand-wired by exact analogy to the
   existing `control-plane` execution (same shape: plain object schemas, no
   `oneOf`, no `int64`/Map-typed fields needing extensions), but `mvn clean
   test` was never actually run against it. **Run it yourself as the first
   real Java consumer** before building `DemandEnvelopeParser`'s replacement
   against the generated `Demand`/`DemandFulfillment` classes — if it doesn't
   compile clean, that's a `contracts` defect to raise back as a new demand,
   not something to patch from your repo.
3. **Python was verified two ways**, but not the real D031 acceptance path:
   a fresh-venv `pip install ./gen/python` (local path, not the tag) plus
   import/round-trip/rejection checks. The actual consumer command (`pip
   install "git+https://github.com/elmoul/contracts.git@v0.8.0#subdirectory=gen/python"`)
   was not run this session — only relevant if you end up needing the Python
   binding too, but noted for completeness.
4. **TypeScript was fully verified**: `tsc --noEmit --strict` clean against
   the rebuilt, committed `dist/`.
5. The `acceptance-criteria` field is new structure — not present in the
   interim envelope your own `DEMAND_SYSTEM.md` §5 describes (there it's a
   markdown body section). Demands raised before this schema existed (this
   very demand's own file, and PlantPal's first) won't validate against it —
   expected, matches your own ingest design's tolerant fallback tiers.

## Acceptance criteria — self-check against the original ask

- [x] `demand` and `demand.fulfillment` JSON Schemas land under
      `schemas/demand-coordinator/`.
- [x] Java/TS/Python bindings generated (Java **not** compiled/verified —
      see above) and released under tag `v0.8.0`, per `CHANGELOG.md`.
- [ ] `demand-coordinator`'s next ingest chunk binds `Demand`/
      `DemandFulfillment` directly — that's your follow-up, not something
      this report can claim done on your behalf.
