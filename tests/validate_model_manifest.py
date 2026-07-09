"""
Schema-level validation for schemas/ai-gateway/model-manifest.json.

Mirrors validate_demand.py's / validate_control_plane.py's pattern: validates
the JSON Schema directly against example documents, independent of any
language binding. Run: python tests/validate_model_manifest.py
"""
import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = ROOT / "schemas" / "ai-gateway" / "model-manifest.json"

GOOD_MANIFEST = {
    "appId": "plantpal",
    "class": "low-stakes",
    "capabilities": {
        "vision-identification": {
            "models": ["gpt-4o", "claude-sonnet-4-6", "gpt-4.1", "gemma3:4b", "plantnet"],
            "media": "required",
            "downshiftPolicy": "block",
        },
        "annotation": {
            "models": ["gpt-4o-mini"],
            "media": "required",
            "downshiftPolicy": "skip",
        },
        "reasoning-json": {
            "models": ["DeepSeek-R1", "o4-mini", "gpt-4.1-mini", "claude-sonnet-4-6", "gemma3:4b"],
            "media": "none",
            "downshiftPolicy": "allow",
        },
        "chat": {
            "models": ["gemma3:4b"],
            "media": "none",
            "streamingDesired": True,
            "downshiftPolicy": "allow",
        },
    },
}

GOOD_MANIFEST_DEFAULT_STREAMING = {
    # streamingDesired omitted entirely -- proves the field is truly optional
    "appId": "plantpal",
    "class": "low-stakes",
    "capabilities": {
        "reasoning-json": {
            "models": ["DeepSeek-R1"],
            "media": "none",
            "downshiftPolicy": "allow",
        },
    },
}

BAD_MANIFEST_MISSING_REQUIRED_CAPABILITY_FIELD = {
    # chat capability is missing `media` (required per CapabilityDeclaration)
    "appId": "plantpal",
    "class": "low-stakes",
    "capabilities": {
        "chat": {
            "models": ["gemma3:4b"],
            "downshiftPolicy": "allow",
        },
    },
}

BAD_MANIFEST_CAPABILITY_NAME_CASING = {
    # capability keys must be kebab-case per propertyNames pattern
    "appId": "plantpal",
    "class": "low-stakes",
    "capabilities": {
        "Vision_Identification": {
            "models": ["gpt-4o"],
            "media": "required",
            "downshiftPolicy": "block",
        },
    },
}

BAD_MANIFEST_UNKNOWN_DOWNSHIFT_POLICY = {
    # downshiftPolicy must be one of allow | block | skip (D023)
    "appId": "plantpal",
    "class": "low-stakes",
    "capabilities": {
        "chat": {
            "models": ["gemma3:4b"],
            "media": "none",
            "downshiftPolicy": "silently-fallback",
        },
    },
}

BAD_MANIFEST_EMPTY_MODELS = {
    # models must have at least one entry -- an empty preference list means nothing to route to
    "appId": "plantpal",
    "class": "low-stakes",
    "capabilities": {
        "chat": {
            "models": [],
            "media": "none",
            "downshiftPolicy": "allow",
        },
    },
}

BAD_MANIFEST_MISSING_APP_FIELDS = {
    # missing appId and class entirely
    "capabilities": {
        "chat": {
            "models": ["gemma3:4b"],
            "media": "none",
            "downshiftPolicy": "allow",
        },
    },
}


def load_schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


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
    schema = load_schema()

    expect_valid(schema, GOOD_MANIFEST, "model-manifest: PlantPal's full declaration (known-good)")
    expect_valid(
        schema,
        GOOD_MANIFEST_DEFAULT_STREAMING,
        "model-manifest: streamingDesired omitted (known-good, proves optionality)",
    )
    expect_invalid(
        schema,
        BAD_MANIFEST_MISSING_REQUIRED_CAPABILITY_FIELD,
        "model-manifest: capability missing required `media` (known-bad)",
    )
    expect_invalid(
        schema,
        BAD_MANIFEST_CAPABILITY_NAME_CASING,
        "model-manifest: capability key not kebab-case (known-bad)",
    )
    expect_invalid(
        schema,
        BAD_MANIFEST_UNKNOWN_DOWNSHIFT_POLICY,
        "model-manifest: unknown downshiftPolicy value (known-bad)",
    )
    expect_invalid(
        schema,
        BAD_MANIFEST_EMPTY_MODELS,
        "model-manifest: empty models preference list (known-bad)",
    )
    expect_invalid(
        schema,
        BAD_MANIFEST_MISSING_APP_FIELDS,
        "model-manifest: missing appId/class (known-bad)",
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
