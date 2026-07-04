"""
Schema-level validation for schemas/connector/*.json (v0.6.0).

Follows the pattern established in validate_control_plane.py / validate_dimension_event.py:
validates the JSON Schemas directly against example documents, independent of any
language binding. Covers connector.vocabulary and both connector.invoke envelopes,
including the deliberately-loose `params`/`result` fields and the optional
`confirmationToken`/`reason` fields.

Run: python tests/validate_connector.py
"""
import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parent.parent
SCHEMAS = ROOT / "schemas" / "connector"

GOOD_VOCABULARY = {
    "connectorId": "connector-gmail",
    "verbs": [
        {
            "name": "list",
            "mode": "read",
            "description": "List messages in a folder.",
            "params": {"type": "object", "properties": {"folder": {"type": "string"}}},
            "returns": "Array of message headers.",
        },
        {
            "name": "send",
            "mode": "write",
            "description": "Send an email.",
            "params": {"type": "object"},
            "returns": "The sent message's provider ID.",
        },
    ],
}

BAD_VOCABULARY_EMPTY_VERBS = {
    "connectorId": "connector-gmail",
    "verbs": [],
}

BAD_VOCABULARY_UNDECLARED_MODE = {
    "connectorId": "connector-gmail",
    "verbs": [
        {
            "name": "delete",
            "mode": "destroy",
            "description": "Not a real mode.",
            "params": {},
            "returns": "n/a",
        }
    ],
}

GOOD_INVOKE_REQUEST_READ = {
    "requestId": "11111111-1111-1111-1111-111111111111",
    "caller": "orchestrator",
    "verb": "list",
    "params": {"folder": "inbox"},
}

GOOD_INVOKE_REQUEST_WRITE_WITH_TOKEN = {
    "requestId": "22222222-2222-2222-2222-222222222222",
    "caller": "orchestrator",
    "verb": "send",
    "params": {"to": "owner@example.com"},
    "confirmationToken": "signed-token-abc",
}

BAD_INVOKE_REQUEST_MISSING_VERB = {
    "requestId": "33333333-3333-3333-3333-333333333333",
    "caller": "orchestrator",
    "params": {},
}

GOOD_INVOKE_RESPONSE_OK = {
    "requestId": "11111111-1111-1111-1111-111111111111",
    "status": "ok",
    "result": {"messageId": "abc-123"},
}

GOOD_INVOKE_RESPONSE_REFUSED = {
    "requestId": "22222222-2222-2222-2222-222222222222",
    "status": "refused",
    "reason": "verb 'delete' is not in this connector's declared vocabulary",
}

BAD_INVOKE_RESPONSE_MISSING_STATUS = {
    "requestId": "33333333-3333-3333-3333-333333333333",
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
    vocabulary_schema = load("connector.vocabulary.json")
    request_schema = load("connector.invoke.request.json")
    response_schema = load("connector.invoke.response.json")

    expect_valid(vocabulary_schema, GOOD_VOCABULARY, "connector.vocabulary: connector-gmail (known-good)")
    expect_invalid(vocabulary_schema, BAD_VOCABULARY_EMPTY_VERBS, "connector.vocabulary: empty verbs array (known-bad)")
    expect_invalid(vocabulary_schema, BAD_VOCABULARY_UNDECLARED_MODE, "connector.vocabulary: mode outside read|write enum (known-bad)")

    expect_valid(request_schema, GOOD_INVOKE_REQUEST_READ, "connector.invoke.request: read verb, no token (known-good)")
    expect_valid(request_schema, GOOD_INVOKE_REQUEST_WRITE_WITH_TOKEN, "connector.invoke.request: write verb with confirmationToken (known-good)")
    expect_invalid(request_schema, BAD_INVOKE_REQUEST_MISSING_VERB, "connector.invoke.request: missing verb (known-bad)")

    expect_valid(response_schema, GOOD_INVOKE_RESPONSE_OK, "connector.invoke.response: ok status with result (known-good)")
    expect_valid(response_schema, GOOD_INVOKE_RESPONSE_REFUSED, "connector.invoke.response: refused status with reason (known-good)")
    expect_invalid(response_schema, BAD_INVOKE_RESPONSE_MISSING_STATUS, "connector.invoke.response: missing status (known-bad)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
