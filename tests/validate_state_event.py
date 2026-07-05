"""
Schema-level validation for schemas/state-feed/state.event.json's ActivityCountEvent
(v0.7.0, sixth oneOf member).

Follows the pattern established in validate_dimension_event.py: validates the JSON
Schema directly against example documents, independent of any language binding.

count is a delta since the last emission for a (componentId, activity) pair, not a
cumulative total — orchestrator/sentinel-hub previously repurposed load pulses
(clamped to 100) for this; activity.count gives it a proper unbounded-count shape.

Run: python tests/validate_state_event.py
"""
import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parent.parent
STATE_EVENT_SPEC = ROOT / "schemas" / "state-feed" / "state.event.json"

GOOD_EVENT_WITH_ORIGIN = {
    "type": "activity.count",
    "timestamp": "2026-07-05T12:00:00Z",
    "payload": {
        "componentId": "sentinel-hub",
        "activity": "scan.message",
        "count": 7,
    },
    "origin": "hub",
}

GOOD_EVENT_WITHOUT_ORIGIN = {
    "type": "activity.count",
    "timestamp": "2026-07-05T12:00:00Z",
    "payload": {
        "componentId": "orchestrator",
        "activity": "tool.call",
        "count": 0,
    },
}

BAD_EVENT_NEGATIVE_COUNT = {
    "type": "activity.count",
    "timestamp": "2026-07-05T12:00:00Z",
    "payload": {
        "componentId": "orchestrator",
        "activity": "tool.call",
        "count": -1,
    },
}

BAD_EVENT_MISSING_ACTIVITY = {
    "type": "activity.count",
    "timestamp": "2026-07-05T12:00:00Z",
    "payload": {
        "componentId": "orchestrator",
        "count": 1,
    },
}

BAD_EVENT_UNKNOWN_PROPERTY = {
    "type": "activity.count",
    "timestamp": "2026-07-05T12:00:00Z",
    "payload": {
        "componentId": "orchestrator",
        "activity": "tool.call",
        "count": 1,
        "unexpected": "nope",
    },
}


def load_state_event_schema() -> dict:
    return json.loads(STATE_EVENT_SPEC.read_text(encoding="utf-8"))


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
    schema = load_state_event_schema()

    expect_valid(schema, GOOD_EVENT_WITH_ORIGIN, "activity.count: known-good event with origin")
    expect_valid(schema, GOOD_EVENT_WITHOUT_ORIGIN, "activity.count: known-good event without origin")
    expect_invalid(schema, BAD_EVENT_NEGATIVE_COUNT, "activity.count: negative count (known-bad)")
    expect_invalid(schema, BAD_EVENT_MISSING_ACTIVITY, "activity.count: missing activity (known-bad)")
    expect_invalid(schema, BAD_EVENT_UNKNOWN_PROPERTY, "activity.count: unknown extra property (known-bad)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
