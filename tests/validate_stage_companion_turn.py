"""
Schema-level validation for schemas/stage/companion.turn.yaml's
CompanionMessageRequest, StageContext, and CompanionMessageResponse schemas
(v0.15.0 addition, Wave 7 session B-2 -- landing the proven Companion rung-0
turn contract from plantpal's Wave 7 A-4 build).

Follows the pattern established in validate_ai_job.py/validate_ai_request.py:
validates the JSON Schema directly against example documents, independent of
any language binding. companion.turn.yaml is an OpenAPI document rather than
a standalone JSON Schema, so the relevant schema is pulled out of
components.schemas before validating.

CompanionMessageRequest coverage: a message-only submission (known-good,
proves pointableTargets/stageContext/priorCorrections/locale are all truly
optional -- matches CompanionMessageRequest.java, which has no @NotNull on
any of them), a fully-populated submission (known-good), a missing required
message (known-bad), a message over the 2000-char cap (known-bad, mirrors
the real @Size(max = 2000) constraint), and a priorCorrections entry over the
300-char cap (known-bad, mirrors @Size(max = 300) on each list element).

CompanionMessageResponse coverage: a plain conversational reply with only
`say` (known-good, proves pointAt/evidence/confidence are all truly optional
-- the "nothing to substantiate" case CompanionServiceImpl.parseResponse
falls back to), a reply carrying the full pointing+trust shape (known-good),
a missing required `say` (known-bad), and an unknown confidence enum value
(known-bad). `evidence` present without `confidence` is deliberately NOT
asserted invalid here -- same choice ai.response's v0.13.0 `skipped` pairing
made: the "travel together or not at all" rule is CompanionServiceImpl's own
producer-side convention (it actively drops a lone half of the pair before
ever returning it), not a schema-level constraint, so both halves validate
independently at the schema layer.

Run: python tests/validate_stage_companion_turn.py
"""
import sys
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parent.parent
COMPANION_TURN_SPEC = ROOT / "schemas" / "stage" / "companion.turn.yaml"

GOOD_REQUEST_MESSAGE_ONLY = {
    "message": "Is the garden okay right now?",
}

GOOD_REQUEST_FULL = {
    "message": "Is the garden okay right now?",
    "pointableTargets": [
        "card-action-app-health",
        "card-data-dimension-event",
        "card-data-state-event",
    ],
    "stageContext": {
        "healthStatus": "UP",
        "dimensionSummary": "3 recent plant_count events, net +2",
        "stateSummary": "no recent activity",
        "coldStart": False,
    },
    "priorCorrections": ["The health card was actually UP, not DOWN, when you said that."],
    "locale": "fr",
}

BAD_REQUEST_MISSING_MESSAGE = {
    "pointableTargets": [],
}

BAD_REQUEST_MESSAGE_TOO_LONG = {
    "message": "x" * 2001,
}

BAD_REQUEST_CORRECTION_TOO_LONG = {
    "message": "Is the garden okay?",
    "priorCorrections": ["x" * 301],
}

GOOD_RESPONSE_PLAIN = {
    "say": "I don't have anything to say to that right now.",
}

GOOD_RESPONSE_FULL = {
    "say": "Your garden looks healthy overall.",
    "pointAt": "card-action-app-health",
    "evidence": "app-health reports status UP",
    "confidence": "high",
}

BAD_RESPONSE_MISSING_SAY = {
    "pointAt": "card-action-app-health",
}

BAD_RESPONSE_UNKNOWN_CONFIDENCE = {
    "say": "Your garden looks healthy overall.",
    "evidence": "app-health reports status UP",
    "confidence": "certain",
}


def load_components() -> dict:
    return yaml.safe_load(COMPANION_TURN_SPEC.read_text(encoding="utf-8"))["components"]


def component_schema(name: str) -> dict:
    components = load_components()
    return {"components": components, "$ref": f"#/components/schemas/{name}"}


def load_request_schema() -> dict:
    return component_schema("CompanionMessageRequest")


def load_response_schema() -> dict:
    return component_schema("CompanionMessageResponse")


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
    request_schema = load_request_schema()

    expect_valid(request_schema, GOOD_REQUEST_MESSAGE_ONLY, "stage.companion.turn request: message-only (known-good, proves optionality)")
    expect_valid(request_schema, GOOD_REQUEST_FULL, "stage.companion.turn request: fully-populated (known-good)")
    expect_invalid(request_schema, BAD_REQUEST_MISSING_MESSAGE, "stage.companion.turn request: missing required message (known-bad)")
    expect_invalid(request_schema, BAD_REQUEST_MESSAGE_TOO_LONG, "stage.companion.turn request: message over 2000 chars (known-bad)")
    expect_invalid(request_schema, BAD_REQUEST_CORRECTION_TOO_LONG, "stage.companion.turn request: priorCorrections entry over 300 chars (known-bad)")

    response_schema = load_response_schema()

    expect_valid(response_schema, GOOD_RESPONSE_PLAIN, "stage.companion.turn response: plain reply, say only (known-good, proves optionality)")
    expect_valid(response_schema, GOOD_RESPONSE_FULL, "stage.companion.turn response: full pointing+trust shape (known-good)")
    expect_invalid(response_schema, BAD_RESPONSE_MISSING_SAY, "stage.companion.turn response: missing required say (known-bad)")
    expect_invalid(response_schema, BAD_RESPONSE_UNKNOWN_CONFIDENCE, "stage.companion.turn response: unknown confidence enum value (known-bad)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
