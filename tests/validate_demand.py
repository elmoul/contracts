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

BAD_FULFILLMENT = {
    "demandId": "demand-coordinator-20260709-demand-schema",
    "worker": "contracts",
    "status": "in-progress",  # not a worker-reportable status
    # missing summaryRef
}


def load(name: str) -> dict:
    return json.loads((SCHEMAS / name).read_text(encoding="utf-8"))


def expect_valid(schema: dict, doc: dict, label: str) -> None:
    errors = list(Draft202012Validator(schema).iter_errors(doc))
    if errors:
        raise AssertionError(f"{label}: expected valid, got errors: {errors}")
    print(f"PASS  {label}")


def expect_invalid(schema: dict, doc: dict, label: str) -> None:
    errors = list(Draft202012Validator(schema).iter_errors(doc))
    if not errors:
        raise AssertionError(f"{label}: expected invalid, but document passed")
    print(f"PASS  {label} (rejected: {errors[0].message})")


def main() -> int:
    demand_schema = load("demand.json")
    fulfillment_schema = load("demand.fulfillment.json")

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
    expect_invalid(
        fulfillment_schema,
        BAD_FULFILLMENT,
        "demand.fulfillment: bad status + missing summaryRef (known-bad)",
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
