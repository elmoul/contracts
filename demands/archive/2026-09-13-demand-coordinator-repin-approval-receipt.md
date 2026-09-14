---
id: contracts-20260913-demand-coordinator-repin-approval-receipt
date: 2026-09-13
from: contracts
to: [demand-coordinator]
capability: demand-coordinator re-pins contracts to v0.24.0 and consumes the new `DemandApprovalReceipt` Java binding for its exact-`demandId` approval lookup instead of a hand-rolled DTO
acceptance-criteria:
  - "demand-coordinator's Maven dependency on io.platform:contracts reads 0.24.0 (installed from the tagged git checkout per DEPLOYMENT.md, not a stale local .m2 copy)"
  - "demand-coordinator's approval-lookup endpoint returns io.platform.contracts.demandcoordinator.DemandApprovalReceipt (found:true/false per the schema's discriminant), not a locally-defined receipt class"
  - "any existing hand-rolled receipt/lookup DTO in demand-coordinator is deleted, or the gap from doing so is written down with a reason"
needs-owner: false
status: archived
---

# Demand — re-pin `contracts` v0.24.0 and adopt `DemandApprovalReceipt`

## What we need

Per `contracts`' D043 release-notification duty (`CLAUDE.md` "Release
checklist (per tag)"): every release closes its own loop by raising a demand
to the origin whose need it fulfils. `v0.24.0` fulfils demand-coordinator's
own demand `demand-coordinator-20260913-contracts-approved-evidence-receipt`
— this is that demand's "re-pin and adopt" close-the-loop, not a new ask.

Additive release, brand-new schema — no other consumer of the
`demand-coordinator` contract group is obligated to move (D031 pins are
deliberate); this demand goes to the origin only.

The one-line re-pin (Java is demand-coordinator's stack per
spec-demand-coordinator.md's "Tech" line):

```bash
git clone https://github.com/elmoul/contracts.git ../contracts-v0.24.0
cd ../contracts-v0.24.0 && git checkout v0.24.0
mvn install -f gen/java/pom.xml
```

```xml
<dependency>
  <groupId>io.platform</groupId>
  <artifactId>contracts</artifactId>
  <version>0.24.0</version>
</dependency>
```

```java
import io.platform.contracts.demandcoordinator.DemandApprovalReceipt;
import io.platform.contracts.demandcoordinator.ApprovalProvenance;
import io.platform.contracts.demandcoordinator.ApprovalEvidenceSource;
```

## What shipped

New schema `schemas/demand-coordinator/demand.approval-receipt.json` →
`DemandApprovalReceipt`: the durable, immutable record of the owner gate for
exactly one demand — what an exact-`demandId` (optionally `subDemand`) lookup
returns.

- `found: true` requires `approvedAt`, `provenance` (`decidedBy` is a
  `const: "owner"` — spec-demand-coordinator.md's gate is explicit that a
  worker's `done` is a claim never a verdict, "no self-certification, ever,"
  so the contract states that structurally), the origin `Demand` envelope and
  the approved `DemandFulfillment` envelope both embedded verbatim
  (`originEnvelope`/`fulfillmentEvidence` — reuse `Demand`/`DemandFulfillment`
  via cross-file `$ref`, not a duplicated shape), `evidenceSource` (the exact
  git blob the owner read: `repoPath` + `commit`), and `evidenceDigest` (a
  SHA-256 hex digest over that blob's full bytes at approval time — a report
  edited after approval no longer matches this digest, surfacing the drift
  rather than letting the receipt silently reattach).
- `found: false` requires `unknownReason` (`no-receipt-on-file` today,
  extensible) and forbids every approval-only field via an
  `allOf`/`if`/`then`/`not` block — a not-yet-approved lookup can never look
  partially approved.
- Because `demand.id` is itself never reused, one receipt answers a given
  `demandId`/`subDemand` for all time.

Full Java binding regenerated, `mvn -f gen/java/pom.xml test` green, real
D031 acceptance run against the actual tagged git URL in a fresh clone/`.m2`
(not just a local build) — see `CHANGELOG.md` v0.24.0 and
`demands/fulfilled/demand-coordinator-20260913-contracts-approved-evidence-receipt-report.md`.
TS/Python bindings untouched this release (demand-coordinator is Java/Spring
and the only consumer — mirrors the v0.6.1 single-binding precedent).

## What we do once closed

Nothing further from `contracts` — this is the whole loop for this demand.
When demand-coordinator's re-pin lands, archive this file per the demand
system's loop-close step.
