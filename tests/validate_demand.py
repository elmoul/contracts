"""
Schema-level validation for schemas/demand-coordinator/*.json.

Mirrors validate_control_plane.py's pattern: validates the JSON Schemas
directly against example documents, independent of any language binding.
Run: python tests/validate_demand.py
"""
import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parent.parent
SCHEMAS = ROOT / "schemas" / "demand-coordinator"

GOOD_DEMAND = {
    "id": "demand-coordinator-20260709-demand-schema",
    "date": "2026-07-09",
    "from": "demand-coordinator",
    "to": ["contracts"],
    "capability": "publish the demand + demand.fulfillment schemas",
    "acceptance-criteria": [
        "demand and demand.fulfillment JSON Schemas land under schemas/",
        "Java/TS/Python bindings generated and released under a tagged version",
    ],
    "needs-owner": False,
    "status": "open",
}

BAD_DEMAND_MISSING_FIELD_AND_BAD_STATUS = {
    # missing id, missing acceptance-criteria
    "date": "2026-07-09",
    "from": "demand-coordinator",
    "to": ["contracts"],
    "capability": "publish the demand + demand.fulfillment schemas",
    "needs-owner": False,
    "status": "ingested",  # not an origin-owned status — coordinator-internal state
}

BAD_DEMAND_MALFORMED_ID = {
    "id": "not-a-valid-id",  # missing the embedded YYYYMMDD segment
    "date": "2026-07-09",
    "from": "demand-coordinator",
    "to": ["contracts"],
    "capability": "publish the demand + demand.fulfillment schemas",
    "acceptance-criteria": ["something"],
    "needs-owner": False,
    "status": "open",
}

GOOD_FULFILLMENT = {
    "demandId": "demand-coordinator-20260709-demand-schema",
    "worker": "contracts",
    "status": "done",
    "summaryRef": "demands/fulfilled/demand-coordinator-20260709-demand-schema-report.md",
}

GOOD_FULFILLMENT_SUB_DEMAND = {
    "demandId": "plantpal-20260709-ai-gateway-full-ai-coverage",
    "subDemand": "plantpal-20260709-ai-gateway-full-ai-coverage:ai-gateway",
    "worker": "ai-gateway",
    "status": "blocked",
    "summaryRef": "demands/fulfilled/plantpal-20260709-ai-gateway-full-ai-coverage-report.md",
}

# v0.11.0: summaryRef is optional (demand-coordinator-20260710-contracts-fulfillment-envelope-drift)
# — shipped/date are the real fleet convention (DEMAND_SYSTEM.md §5); this exercises both without
# summaryRef at all.
GOOD_FULFILLMENT_SHIPPED_DATE_NO_SUMMARY_REF = {
    "demandId": "observability-20260710-telemetry-schema",
    "worker": "contracts",
    "status": "done",
    "shipped": ["v0.10.0"],
    "date": "2026-07-10",
}

BAD_FULFILLMENT = {
    "demandId": "demand-coordinator-20260709-demand-schema",
    "worker": "contracts",
    "status": "in-progress",  # not a worker-reportable status
    "summaryRef": "demands/fulfilled/demand-coordinator-20260709-demand-schema-report.md",
}


GOOD_ORIGIN_ENVELOPE = GOOD_DEMAND
GOOD_FULFILLMENT_EVIDENCE = GOOD_FULFILLMENT

GOOD_RECEIPT_FOUND = {
    "demandId": "demand-coordinator-20260913-contracts-approved-evidence-receipt",
    "found": True,
    "approvedAt": "2026-09-13T22:10:00Z",
    "provenance": {"decidedBy": "owner"},
    "originEnvelope": GOOD_ORIGIN_ENVELOPE,
    "fulfillmentEvidence": GOOD_FULFILLMENT_EVIDENCE,
    "evidenceSource": {
        "repoPath": "demands/fulfilled/demand-coordinator-20260913-contracts-approved-evidence-receipt-report.md",
        "commit": "9eb777c",
    },
    "evidenceDigest": "3b50d5f4938d671bcf0f09e8f2113ba9eb69660b7885fd7f21f357ed8c8b1b1b",
}

GOOD_RECEIPT_UNKNOWN = {
    "demandId": "demand-coordinator-20260913-contracts-nonexistent",
    "found": False,
    "unknownReason": "no-receipt-on-file",
}

BAD_RECEIPT_FOUND_MISSING_EVIDENCE = {
    # found:true but missing every approval field the allOf/if-then requires
    "demandId": "demand-coordinator-20260913-contracts-approved-evidence-receipt",
    "found": True,
}

BAD_RECEIPT_UNKNOWN_CARRYING_APPROVAL_FIELD = {
    # found:false must not carry any approval-only field — this smuggles one in
    "demandId": "demand-coordinator-20260913-contracts-nonexistent",
    "found": False,
    "unknownReason": "no-receipt-on-file",
    "approvedAt": "2026-09-13T22:10:00Z",
}


def load(name: str) -> dict:
    return json.loads((SCHEMAS / name).read_text(encoding="utf-8"))


def expect_valid(schema, doc: dict, label: str) -> None:
    validator = schema if isinstance(schema, Draft202012Validator) else Draft202012Validator(schema)
    errors = list(validator.iter_errors(doc))
    if errors:
        raise AssertionError(f"{label}: expected valid, got errors: {errors}")
    print(f"PASS  {label}")


def expect_invalid(schema, doc: dict, label: str) -> None:
    validator = schema if isinstance(schema, Draft202012Validator) else Draft202012Validator(schema)
    errors = list(validator.iter_errors(doc))
    if not errors:
        raise AssertionError(f"{label}: expected invalid, but document passed")
    print(f"PASS  {label} (rejected: {errors[0].message})")


def main() -> int:
    demand_schema = load("demand.json")
    fulfillment_schema = load("demand.fulfillment.json")
    receipt_schema = load("demand.approval-receipt.json")

    # demand.approval-receipt.json $refs its siblings by on-disk filename ("demand.json",
    # "demand.fulfillment.json") rather than by their own $id ("…/demand",
    # "…/demand.fulfillment", no ".json") — deliberate, see the schema's own field
    # descriptions: jsonschema2pojo (Java codegen) resolves relative $refs as same-directory
    # file paths, not by $id. Mirror that here: register each sibling under the *filename*
    # URI ($id's directory + literal ".json" name) that a relative "demand.json" $ref
    # resolves to from demand.approval-receipt.json's own $id, not under the sibling's own
    # $id string.
    registry = Registry().with_resources(
        [
            (demand_schema["$id"] + ".json", Resource.from_contents(demand_schema)),
            (fulfillment_schema["$id"] + ".json", Resource.from_contents(fulfillment_schema)),
        ]
    )
    receipt_validator = Draft202012Validator(receipt_schema, registry=registry)

    expect_valid(demand_schema, GOOD_DEMAND, "demand: contracts bootstrap demand (known-good)")
    expect_invalid(
        demand_schema,
        BAD_DEMAND_MISSING_FIELD_AND_BAD_STATUS,
        "demand: missing id/acceptance-criteria + coordinator-internal status (known-bad)",
    )
    expect_invalid(
        demand_schema,
        BAD_DEMAND_MALFORMED_ID,
        "demand: id missing embedded YYYYMMDD segment (known-bad)",
    )
    expect_valid(fulfillment_schema, GOOD_FULFILLMENT, "demand.fulfillment: single-target report (known-good)")
    expect_valid(
        fulfillment_schema,
        GOOD_FULFILLMENT_SUB_DEMAND,
        "demand.fulfillment: multi-hexagon sub-demand report (known-good)",
    )
    expect_valid(
        fulfillment_schema,
        GOOD_FULFILLMENT_SHIPPED_DATE_NO_SUMMARY_REF,
        "demand.fulfillment: shipped+date, no summaryRef (known-good, proves v0.11.0 optionality)",
    )
    expect_invalid(
        fulfillment_schema,
        BAD_FULFILLMENT,
        "demand.fulfillment: bad status (known-bad)",
    )
    expect_valid(
        receipt_validator,
        GOOD_RECEIPT_FOUND,
        "demand.approval-receipt: found, full receipt with embedded envelope+evidence (known-good)",
    )
    expect_valid(
        receipt_validator,
        GOOD_RECEIPT_UNKNOWN,
        "demand.approval-receipt: not found, demandId with no receipt on file (known-good)",
    )
    expect_invalid(
        receipt_validator,
        BAD_RECEIPT_FOUND_MISSING_EVIDENCE,
        "demand.approval-receipt: found:true missing approval fields (known-bad)",
    )
    expect_invalid(
        receipt_validator,
        BAD_RECEIPT_UNKNOWN_CARRYING_APPROVAL_FIELD,
        "demand.approval-receipt: found:false smuggling an approval field (known-bad)",
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
