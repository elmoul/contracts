---
demandId: dashboard-20260914-demand-dispatch-order
subDemand: dashboard-20260914-demand-dispatch-order:contracts
worker: contracts
date: 2026-09-14
status: done
shipped: ["v0.26.0", "contracts@3623357 on main", "demand.after (optional array of demand ids)", "DemandQueueEntry schema + Java/TypeScript bindings", "8 new Java tests (34 total, all passing)", "22 demand validator cases in tests/validate_demand.py (all passing)", "D031 clean install verified from the tagged URL for both changed languages"]
summaryRef: "demands/fulfilled/dashboard-20260914-demand-dispatch-order-report.md"
---

# Fulfillment — Dispatch order (contracts leg)

## What shipped

**v0.26.0**, tag `v0.26.0` at `contracts@3623357`, additive, Java +
TypeScript bindings. This covers **criteria 1–2** of the demand — the
`contracts:`-scoped items. Criteria 3–8 belong to the other targets of this
multi-hexagon demand and are **not** claimed here.

1. **`schemas/demand-coordinator/demand.json` gains optional `after`** — an
   array of demand ids (`pattern` identical to `id`'s, `uniqueItems: true`,
   `minItems: 1`). Optional, so every demand file written before it remains
   valid; `tests/validate_demand.py` proves that against a **real committed
   demand file read off disk** (`demands/2026-09-14-factory-repin-interface-
   extraction.md`), not a hand-written pre-`after` sample. An empty list is
   rejected rather than read as "unconstrained" — omitting the field is how
   you say that.
2. **`schemas/demand-coordinator/demand.queue-entry.json`** (new,
   `DemandQueueEntry`) — one dispatch-queue row: `demandId`, `date`, `from`,
   `to`, **`wave`** (`integer`, `minimum: 1`) and **`waitingOn`** (the ids
   from `after` not yet owner-approved). Java
   (`io.platform.contracts.demandcoordinator.DemandQueueEntry`, wired into the
   existing `demand-coordinator` execution in `gen/java/pom.xml`) and
   TypeScript (`gen/ts/demand-queue-entry.ts`, re-exported from `index.ts`,
   `dist/` rebuilt and committed per D031) so both consumers use generated
   types instead of hand-rolling the new fields.

**D031 acceptance, run for real.** Cloned
`https://github.com/elmoul/contracts.git` at `v0.26.0` into a scratch dir and
installed clean, for both changed languages:

- **TypeScript** — fresh npm cache, scratch consumer with `"@platform/
  contracts": "file:<tagged-checkout>/gen/ts"`; installed as `0.26.0`,
  typechecked under `--strict` against `DemandQueueEntry` and an optional
  `after`, and ran. A negative control (`wave: "2"`) fails to compile, so the
  pass is not vacuous.
- **Java** — `mvn install -f gen/java/pom.xml` into a **fresh `.m2`**
  (`io.platform:contracts:0.26.0`), then a scratch consumer depending on it,
  which deserialized a waiting row (`wave=2`, `waitingOn=[…]`), an elevated
  row (`wave=3`, `waitingOn=[]`) and both a pre-`after` and an `after`-gated
  `Demand`.

Python packaging did not change, so no Python install test was run — see the
caveat below.

## What the origin must know

- **`wave` and `waitingOn` are not each other's inverse.** This is the one
  thing that will bite an implementer, so it is pinned in the schema
  description, in `validate_demand.py` as a known-good document, and in a
  round-trip assertion in `DemandDispatchOrderContractsTest`. `wave` is raised
  by two independent causes: this demand's own unresolved `after` edges (what
  `waitingOn` reports) **and** sequence position within a multi-hexagon demand
  (a sub-demand never shows a lower wave than the target before it). A
  sub-demand can therefore legitimately sit at **wave 3 with an empty
  `waitingOn`**. Rendering the Order column as `waitingOn.length + 1` is wrong;
  read `wave`.
- **`wave` is `minimum: 1` and an unset `wave` is omitted, never `0`.**
  The Java POJO is `@JsonInclude(NON_NULL)`, so a null wave does not reach the
  wire. `0` is a bug, not a "not yet scheduled" sentinel — a consumer treating
  a missing wave as `0` would sort it ahead of everything.
- **Java gets `Set<String>`, not `List<String>`.** `uniqueItems: true` makes
  jsonschema2pojo 1.2.1 emit `Set`/`LinkedHashSet` for both `Demand.after` and
  `DemandQueueEntry.waitingOn`, while TypeScript gets a plain array. (`to`,
  which has no `uniqueItems`, stays a `List` in Java.) The test asserts the
  field types outright so a future generator that flattens them fails loudly.
- **The queue entry is a lean reference, deliberately.** It carries no copy of
  `capability`/`acceptance-criteria` — the envelope has exactly one home, and
  duplicating it would give the fleet two records of the same demand that can
  disagree. Consumers needing the prose join back on `demandId`. The schema
  rejects an entry carrying envelope prose, and the Java test asserts an entry
  never serializes those fields.
- **D043 release demands: raised, origin-only.** v0.26.0 is additive (a new
  optional field and a new schema — no removals, renames, or new required
  fields), so per D043's additive scope only the origin demand was raised:
  `demands/2026-09-14-dashboard-repin-dispatch-order.md` → `to: [dashboard]`,
  pushed as its own standalone coordination commit (`8c2c55e`). No fleet-wide
  bump demand — D031 pins are deliberate and nothing obligates another repo to
  move.
- **Remaining legs are not yours to raise.** Criteria 3–8
  (`demand-coordinator`, `runtime`, `agent-runner`) are the other targets of
  this same demand, which the coordinator sequences — this report closes only
  the `contracts` leg (`subDemand: …:contracts`). The whole demand must not be
  read as satisfied on this report alone.

## Not done / caveats

- **The Python binding for `demand` is now stale for `after`, on purpose, and
  this is the one real gap.** Because `gen/python/platform_contracts/
  demand_coordinator/demand.py` sets `extra='forbid'`, a Python consumer
  validating a demand file that carries `after` would be **rejected**. It was
  left alone because regenerating it with the installed `datamodel-codegen`
  **0.68.1** also rewrites the pre-existing `to` field from
  `list[constr(...)]` to `list[ToItem]` (a `RootModel` wrapper) — verified to
  be pure generator-version drift by regenerating from the *unmodified* v0.25.0
  schema and reproducing the same diff. That is an unrelated breaking change
  (`demand.to[0] == "factory"` would become `False` for every Python consumer)
  and no part of this demand asks for it, so shipping it inside an additive
  release would have been the wrong trade. No repo in the fleet imports
  `platform_contracts.demand_coordinator` (checked across `../platform/` — the
  only hits are copies of this repo's own pinned tree), so nothing is broken
  today by the staleness. `pyproject.toml` therefore stays at `0.25.0`,
  consistent with this repo's per-language versioning. **If any of the
  remaining targets is Python and needs `after`/`DemandQueueEntry`, raise a
  demand** — the fix is either a deliberate, separately-reviewed acceptance of
  the `ToItem` change or a pinned older generator, and it should not ride
  along with this contract.
- **No `DemandQueueEntry` Python module was generated.** The demand names Java
  and TypeScript bindings specifically, and no Python consumer exists or is
  named. Same reasoning as above: ask rather than assume.
- **`useJakartaValidation` emits no annotations on the generated POJOs** —
  pre-existing and uniform across this repo, not introduced here. `wave`'s
  `minimum: 1` is therefore a schema/contract guarantee that a consumer must
  enforce (bean validation is not wired to Jackson deserialization), not one
  the Java binding fails on at parse time. Worth knowing if `demand-coordinator`
  expected `@Min(1)` to reject a bad row on the way in.
- **A pre-existing YAML detail surfaced while writing the backwards-compat
  test**: every committed demand file writes `date:` unquoted, so a YAML loader
  resolves it to a `datetime.date`, while `demand.json` types it as a string.
  The test normalizes it on read. This predates `after` entirely and is not a
  defect this release introduced — but any consumer validating raw parsed YAML
  frontmatter against `demand.json` directly will hit it.
