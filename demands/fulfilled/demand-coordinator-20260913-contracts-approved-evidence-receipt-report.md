---
demandId: demand-coordinator-20260913-contracts-approved-evidence-receipt
worker: contracts
date: 2026-09-13
status: done
shipped: ["v0.24.0", "commit 907238d on main (schema+bindings+tests+changelog)", "D031 acceptance verified in a fresh clone/.m2"]
summaryRef: "demands/fulfilled/demand-coordinator-20260913-contracts-approved-evidence-receipt-report.md"
---

# Fulfillment — DemandApprovalReceipt contract

## What shipped

New schema `schemas/demand-coordinator/demand.approval-receipt.json` →
`DemandApprovalReceipt`, released as `contracts` v0.24.0 (Java binding only —
demand-coordinator is Java/Spring per spec-demand-coordinator.md and the only
current consumer of the `demand-coordinator` contract group).

**Immutable receipt, keyed by exact `demandId`** (`subDemand` when the lookup
concerns one target of a multi-hexagon demand):

- `found: true` — an approval exists. Requires:
  - `approvedAt` (date-time) — when the owner gate moved
    `pending-approval` → `satisfied`.
  - `provenance.decidedBy`, a fixed `const: "owner"` (not free text) —
    spec-demand-coordinator.md's gate states a worker's `done` is a claim
    never a verdict and "no self-certification, ever"; the contract encodes
    that structurally rather than trusting a caller to type it correctly.
    `provenance.notes` is an optional free-text field.
  - `originEnvelope` — the exact origin `Demand` envelope, embedded verbatim
    via a `$ref` to the existing `demand.json` schema (reused, not
    duplicated).
  - `fulfillmentEvidence` — the exact approved `DemandFulfillment` envelope,
    embedded verbatim via `$ref` to `demand.fulfillment.json`.
  - `evidenceSource` (`repoPath` + `commit`) — the exact git blob of the
    fulfillment report the owner actually read.
  - `evidenceDigest` — a SHA-256 hex digest over that blob's full bytes
    (frontmatter + markdown body) at approval time. This is what binds the
    receipt to *that one* approved revision: if the report file is edited
    afterward, recomputing the digest over its current content no longer
    matches, surfacing the drift rather than letting the receipt silently
    reattach to whatever the file now says.
- `found: false` — no receipt on file for this `demandId`. Requires
  `unknownReason` (one enum value today, `no-receipt-on-file`, left
  extensible for a future finer distinction — the coordinator does not yet
  distinguish "never raised" from "raised but not yet approved" at this
  lookup). An `allOf`/`if`/`then`/`not` block **forbids** every
  approval-only field (`approvedAt`, `provenance`, `originEnvelope`,
  `fulfillmentEvidence`, `evidenceSource`, `evidenceDigest`) when
  `found: false`, so a caller can never mistake a not-yet-approved lookup
  for a partially-approved one.

**Why exact-ID lookup needs no revision disambiguation of its own:**
`demand.json`'s `id` field is itself documented as "stable, never reused" —
so a `demandId` maps to at most one receipt for all time; there is no
"which revision" ambiguity at the identifier level. The revision binding
problem `evidenceDigest`/`evidenceSource` actually solve is narrower and
real: a demand can be sent back and re-claimed with an amended report
*before* approval (spec-demand-coordinator.md's fold-in step), and even
after approval nothing stops the report file itself from being edited later.
Embedding the full evidence plus its content digest — rather than a mutable
pointer like a bare file path — is what keeps the receipt anchored to the
one revision actually approved.

**Java bindings:** generated via `jsonschema2pojo`, reusing the existing
`Demand`/`DemandFulfillment` classes through cross-file `$ref` (no
duplicated DTO) — `DemandApprovalReceipt`, `ApprovalProvenance`,
`ApprovalEvidenceSource`. Note: the `$ref`s use the sibling schemas'
on-disk filenames (`demand.json`, `demand.fulfillment.json`), not their own
shorter `$id` strings (`.../demand-coordinator/demand`,
`.../demand-coordinator/demand.fulfillment`, no `.json`) — jsonschema2pojo
resolves relative `$ref`s as same-directory file paths, so this is what
actually makes generation succeed; the `$id` strings remain each schema's
own separate JSON-Schema identity, unrelated to this sourcing choice
(discovered by running the generation and hitting the mismatch, not
assumed up front — see the schema's own field descriptions and
`CHANGELOG.md` v0.24.0 for the full note).

**Verification performed, not assumed:**
- `mvn -f gen/java/pom.xml test` — green, all existing suites plus the new
  classes generated correctly.
- `python tests/run_all.py` — green; `tests/validate_demand.py` gained four
  new fixture cases (`found: true` full receipt, `found: false` unknown,
  `found: true` missing evidence rejected, `found: false` smuggling an
  approval field rejected), using the `referencing` library to resolve the
  same cross-file `$ref`s a real consumer would hit.
- **D031 acceptance test actually run**, per the standing invariant in
  `CLAUDE.md` (two past releases shipped on an untested packaging
  assumption): cloned `https://github.com/elmoul/contracts.git` fresh into
  a scratch directory, checked out tag `v0.24.0`, ran
  `mvn install -f gen/java/pom.xml` against that clean checkout (not the
  working tree), and confirmed `io/platform/contracts/demandcoordinator/{DemandApprovalReceipt,ApprovalProvenance,ApprovalEvidenceSource}.class`
  are present in the resulting `.m2`-installed jar.

Tag `v0.24.0` pushed to `main`. `CHANGELOG.md` updated. Per D043, the
"close your consuming leg" demand back to the origin is raised in the same
release: `demands/2026-09-13-demand-coordinator-repin-approval-receipt.md`
(commit `9289059`).

## What the origin must know

- Re-pin to `io.platform:contracts:0.24.0` (Java only — TS/Python untouched
  this release, same precedent as v0.6.1).
- `DemandApprovalReceipt.found` is the single discriminant; branch on it
  rather than checking for `null` fields.
- `provenance.decidedBy` is always the literal string `"owner"` — there is
  no other value to check for, by design.
- If demand-coordinator already has a hand-rolled receipt/lookup DTO, this
  contract is meant to replace it (per this demand's own acceptance
  criteria) — see the re-pin demand's acceptance criteria for the concrete
  ask.

## Not done / caveats

- TS/Python bindings were **not** generated for this schema — demand-
  coordinator is Java/Spring per `spec-demand-coordinator.md` and the only
  named consumer of this capability; no other repo currently needs this
  contract in another language. If that changes, it's a follow-up release,
  not a gap in this one.
- This release defines the **contract shape only**. It does not implement
  demand-coordinator's own storage/query logic for producing a
  `DemandApprovalReceipt` (out of scope for `contracts` per its own
  boundaries — "no business logic, no implementation").
- `unknownReason` carries exactly one enum value today
  (`no-receipt-on-file`). If demand-coordinator's actual ledger needs to
  distinguish "never raised" from "raised but short of the owner gate" at
  this same lookup, that's an additive follow-up demand, not something this
  release anticipated speculatively.
