"""
Schema-level validation for schemas/ai-gateway/request.yaml's AiRequest schema.

Follows the pattern established in validate_control_plane.py (v0.3.0): validates
the JSON Schema directly against example documents, independent of any language
binding. request.yaml is an OpenAPI document rather than a standalone JSON Schema,
so the AiRequest schema is pulled out of components.schemas before validating.

Covers the v0.4.0 addition of the optional `media` field (PlantPal photo-based
identification): a known-good request with media, a known-good request without
media (proves it's truly optional), and a known-bad media item (missing
mimeType) that must be rejected.

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


def load_ai_request_schema() -> dict:
    spec = yaml.safe_load(REQUEST_SPEC.read_text(encoding="utf-8"))
    return spec["components"]["schemas"]["AiRequest"]


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
    schema = load_ai_request_schema()

    expect_valid(schema, GOOD_WITH_MEDIA, "ai.request: AiRequest with media (known-good)")
    expect_valid(schema, GOOD_WITHOUT_MEDIA, "ai.request: AiRequest without media (known-good, proves optional)")
    expect_invalid(schema, BAD_MEDIA_MISSING_MIMETYPE, "ai.request: media item missing mimeType (known-bad)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
