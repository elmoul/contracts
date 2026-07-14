"""
Schema-level validation for schemas/ai-gateway/request.yaml's AiRequest and
AiResponse schemas.

Follows the pattern established in validate_control_plane.py (v0.3.0): validates
the JSON Schema directly against example documents, independent of any language
binding. request.yaml is an OpenAPI document rather than a standalone JSON Schema,
so the relevant schema is pulled out of components.schemas before validating.

Covers the v0.4.0 addition of the optional `media` field (PlantPal photo-based
identification): a known-good request with media, a known-good request without
media (proves it's truly optional), and a known-bad media item (missing
mimeType) that must be rejected.

Covers the v0.13.0 addition of AiResponse's `skipped` field (fulfilling
ai-gateway-20260714-contracts-skip-shape): a known-good completed-call response
(result/model/provider present, skipped absent — proves the pre-existing shape
still validates unchanged), a known-good skipped response (result/model/
provider absent, tokensIn/tokensOut/computedCost zeroed, skipped: true), and a
known-bad response missing a still-required field (tokensIn) — result/model/
provider became optional but tokensIn/tokensOut/computedCost did not.
"skipped: true with result also present" is deliberately NOT asserted invalid:
"absent when skipped" is documented behavior for producers, not a schema-level
constraint (JSON Schema conditional-required was judged not worth the added
complexity for a producer-side convention — see CHANGELOG.md's v0.13.0 entry).

Run: python tests/validate_ai_request.py
"""
import json
import sys
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parent.parent
REQUEST_SPEC = ROOT / "schemas" / "ai-gateway" / "request.yaml"

GOOD_WITH_MEDIA = {
    "prompt": "What plant is this and is it healthy?",
    "appId": "plantpal",
    "userId": "u-123",
    "media": [
        {
            "data": "/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAMCAgICAgMCAgIDAwMDBAYEBAQEBAgGBgUGCQgKCgkI",
            "mimeType": "image/jpeg",
        }
    ],
}

GOOD_WITHOUT_MEDIA = {
    "prompt": "What's the best watering schedule for a pothos?",
    "appId": "plantpal",
    "userId": "u-123",
}

BAD_MEDIA_MISSING_MIMETYPE = {
    "prompt": "What plant is this?",
    "appId": "plantpal",
    "userId": "u-123",
    "media": [
        {
            "data": "/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAMCAgICAgMCAgIDAwMDBAYEBAQEBAgGBgUGCQgKCgkI",
        }
    ],
}

GOOD_COMPLETED_RESPONSE = {
    "result": "Looks like a healthy pothos.",
    "model": "claude-sonnet-4-6",
    "provider": "anthropic",
    "tokensIn": 42,
    "tokensOut": 18,
    "computedCost": 0.0031,
}

GOOD_SKIPPED_RESPONSE = {
    "tokensIn": 0,
    "tokensOut": 0,
    "computedCost": 0,
    "skipped": True,
}

BAD_RESPONSE_MISSING_TOKENS_IN = {
    "tokensOut": 0,
    "computedCost": 0,
    "skipped": True,
}


def load_ai_request_schema() -> dict:
    spec = yaml.safe_load(REQUEST_SPEC.read_text(encoding="utf-8"))
    return spec["components"]["schemas"]["AiRequest"]


def load_ai_response_schema() -> dict:
    spec = yaml.safe_load(REQUEST_SPEC.read_text(encoding="utf-8"))
    return spec["components"]["schemas"]["AiResponse"]


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
    request_schema = load_ai_request_schema()

    expect_valid(request_schema, GOOD_WITH_MEDIA, "ai.request: AiRequest with media (known-good)")
    expect_valid(request_schema, GOOD_WITHOUT_MEDIA, "ai.request: AiRequest without media (known-good, proves optional)")
    expect_invalid(request_schema, BAD_MEDIA_MISSING_MIMETYPE, "ai.request: media item missing mimeType (known-bad)")

    response_schema = load_ai_response_schema()

    expect_valid(response_schema, GOOD_COMPLETED_RESPONSE, "ai.response: completed call (known-good, proves pre-existing shape unaffected)")
    expect_valid(response_schema, GOOD_SKIPPED_RESPONSE, "ai.response: skipped call, result/model/provider absent (known-good)")
    expect_invalid(response_schema, BAD_RESPONSE_MISSING_TOKENS_IN, "ai.response: missing still-required tokensIn (known-bad)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
