"""
Schema-level validation for schemas/app/dimension.event.json's DimensionEvent schema.

Follows the pattern established in validate_ai_request.py (v0.4.0): validates the
JSON Schema directly against example documents, independent of any language binding.

Covers the v0.5.0 introduction of dimension.event: a known-good event, a known-bad
event missing a required field, and a known-good event with a negative delta (the
one field in this schema that deliberately has no `minimum` constraint, unlike every
other numeric field in the contract set — Treasury's DimensionCounter accepts
negative deltas by design, to support soft-delete decrements).

Run: python tests/validate_dimension_event.py
"""
import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parent.parent
DIMENSION_EVENT_SPEC = ROOT / "schemas" / "app" / "dimension.event.json"

GOOD_EVENT = {
    "eventId": "11111111-1111-1111-1111-111111111111",
    "appId": "plantpal",
    "userId": "u-123",
    "dimensionKey": "plant_count",
    "delta": 1,
    "timestamp": "2026-07-04T12:00:00Z",
}

GOOD_EVENT_NEGATIVE_DELTA = {
    "eventId": "22222222-2222-2222-2222-222222222222",
    "appId": "plantpal",
    "userId": "u-123",
    "dimensionKey": "plant_count",
    "delta": -1,
    "timestamp": "2026-07-04T12:05:00Z",
}

BAD_EVENT_MISSING_DIMENSION_KEY = {
    "eventId": "33333333-3333-3333-3333-333333333333",
    "appId": "plantpal",
    "userId": "u-123",
    "delta": 1,
    "timestamp": "2026-07-04T12:00:00Z",
}


def load_dimension_event_schema() -> dict:
    return json.loads(DIMENSION_EVENT_SPEC.read_text(encoding="utf-8"))


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
    schema = load_dimension_event_schema()

    expect_valid(schema, GOOD_EVENT, "dimension.event: known-good event")
    expect_valid(
        schema,
        GOOD_EVENT_NEGATIVE_DELTA,
        "dimension.event: known-good event with negative delta (soft-delete)",
    )
    expect_invalid(
        schema,
        BAD_EVENT_MISSING_DIMENSION_KEY,
        "dimension.event: event missing required dimensionKey (known-bad)",
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
