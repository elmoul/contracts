"""
Schema-level validation for schemas/control-plane/*.json.

No test framework existed in this repo before v0.3.0 (prior releases verified
generated bindings by compiling/typechecking them). This validates the JSON
Schemas themselves against example documents, independent of any language
binding. Run: python tests/validate_control_plane.py
"""
import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator, ValidationError

ROOT = Path(__file__).resolve().parent.parent
SCHEMAS = ROOT / "schemas" / "control-plane"

GOOD_DESCRIPTOR = {
    "functionalName": "treasury",
    "kind": "runtime",
    "side": "host",
    "status": "active",
    "deps": ["contracts", "state-feed"],
    "contracts": {
        "pin": "v0.2.2",
        "binding": "java",
        "used": ["ai.preflight", "usage.event", "state.event"],
    },
}

BAD_DESCRIPTOR = {
    # missing functionalName
    "kind": "runtime",
    "side": "invalid",
    "status": "active",
    "deps": [],
}

# contracts.used items pattern (conventions-20260713-descriptor-used-contracts-pattern):
# real ids from across the fleet today must validate...
GOOD_USED_CONTRACT_IDS = [
    "state.event",
    "ai.preflight.request",
    "build-command",
    "registry.entry",
    "usage.event",
    "state.event.activity.count",
]

# ...and the audited free-text entries found in the fleet (sentinel-hub, publishing)
# must be rejected — this is the defect the pattern exists to catch.
BAD_USED_CONTRACT_IDS = [
    "ai.request / ai.response / ai.blocked",
    "ai.preflight (blocked-response shape only, via ai-gateway's 402)",
    "state.event (activity.count)",
]

GOOD_REGISTRY_ENTRY = {
    "functionalName": "treasury",
    "kind": "runtime",
    "side": "host",
    "status": "active",
    "repoUrl": "https://github.com/elmoul/treasury",
    "version": "v0.2.2",
    "contractsPin": "v0.2.2",
    "updatedAt": "2026-07-03T00:00:00Z",
}

BAD_REGISTRY_ENTRY = {
    "functionalName": "treasury",
    "kind": "runtime",
    "side": "invalid",
    "status": "active",
    # missing repoUrl, version, updatedAt
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
    descriptor_schema = load("hexagon.descriptor.json")
    registry_schema = load("registry.entry.json")

    expect_valid(descriptor_schema, GOOD_DESCRIPTOR, "hexagon.descriptor: treasury (known-good)")
    expect_invalid(descriptor_schema, BAD_DESCRIPTOR, "hexagon.descriptor: missing name + bad side (known-bad)")
    expect_valid(registry_schema, GOOD_REGISTRY_ENTRY, "registry.entry: treasury (known-good)")
    expect_invalid(registry_schema, BAD_REGISTRY_ENTRY, "registry.entry: bad side + missing required fields (known-bad)")

    for contract_id in GOOD_USED_CONTRACT_IDS:
        doc = {**GOOD_DESCRIPTOR, "contracts": {**GOOD_DESCRIPTOR["contracts"], "used": [contract_id]}}
        expect_valid(descriptor_schema, doc, f"hexagon.descriptor: contracts.used real id {contract_id!r} (known-good)")

    for contract_id in BAD_USED_CONTRACT_IDS:
        doc = {**GOOD_DESCRIPTOR, "contracts": {**GOOD_DESCRIPTOR["contracts"], "used": [contract_id]}}
        expect_invalid(descriptor_schema, doc, f"hexagon.descriptor: contracts.used free-text {contract_id!r} (known-bad)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
