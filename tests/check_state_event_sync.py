"""
Structural sync check: schemas/state-feed/state.event.json (source of truth for
TypeScript/Python/validators) vs schemas/state-feed/state-event-java.yaml (the
OpenAPI wrapper that exists only to drive the Java binding, since jsonschema2pojo
cannot generate per-variant classes from a oneOf union — see that file's own
header comment).

The two files are hand-maintained in parallel (different keywords: JSON Schema
`definitions` + `oneOf` vs OpenAPI `components.schemas`), so nothing enforces
they stay in sync except discipline. This script makes that mechanical: for
every event type in state.event.json's oneOf, confirm state-event-java.yaml
declares the same event, and that the payload's required fields and property
names match exactly. It does not compare property types/formats/descriptions —
just event-type coverage and payload field/required sync, which is the class of
drift that has actually happened in this repo's history (adding origin/a new
event to one file and not the other).

Run: python tests/check_state_event_sync.py
"""
import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
STATE_EVENT_JSON = ROOT / "schemas" / "state-feed" / "state.event.json"
STATE_EVENT_JAVA_YAML = ROOT / "schemas" / "state-feed" / "state-event-java.yaml"


def load_json_schema() -> dict:
    return json.loads(STATE_EVENT_JSON.read_text(encoding="utf-8"))


def load_java_yaml() -> dict:
    return yaml.safe_load(STATE_EVENT_JAVA_YAML.read_text(encoding="utf-8"))


def event_defs_from_json_schema(schema: dict) -> dict:
    """Return {EventTypeName: definition-dict} for every oneOf member."""
    defs = schema["definitions"]
    refs = schema["oneOf"]
    events = {}
    for ref in refs:
        name = ref["$ref"].rsplit("/", 1)[-1]
        events[name] = defs[name]
    return events


def event_defs_from_java_yaml(doc: dict) -> dict:
    """Return {EventTypeName: schema-dict} for every *Event schema in components.schemas."""
    schemas = doc["components"]["schemas"]
    return {name: body for name, body in schemas.items() if name.endswith("Event") and name != "Origin"}


def payload_ref_name(event_def: dict) -> str:
    payload_prop = event_def["properties"]["payload"]
    ref = payload_prop["$ref"] if "$ref" in payload_prop else payload_prop["$ref"]
    return ref.rsplit("/", 1)[-1]


def payload_def(defs_or_schemas: dict, ref_name: str) -> dict:
    return defs_or_schemas[ref_name]


def main() -> int:
    json_schema = load_json_schema()
    java_yaml = load_java_yaml()

    json_events = event_defs_from_json_schema(json_schema)
    java_events = event_defs_from_java_yaml(java_yaml)
    json_defs = json_schema["definitions"]
    java_schemas = java_yaml["components"]["schemas"]

    errors = []

    json_names = set(json_events)
    java_names = set(java_events)

    only_in_json = json_names - java_names
    only_in_java = java_names - json_names
    if only_in_json:
        errors.append(f"Event types in state.event.json but missing from state-event-java.yaml: {sorted(only_in_json)}")
    if only_in_java:
        errors.append(f"Event types in state-event-java.yaml but missing from state.event.json: {sorted(only_in_java)}")

    for name in sorted(json_names & java_names):
        json_event = json_events[name]
        java_event = java_events[name]

        # envelope-level required fields
        json_required = set(json_event.get("required", []))
        java_required = set(java_event.get("required", []))
        if json_required != java_required:
            errors.append(
                f"{name}: envelope 'required' differs — state.event.json={sorted(json_required)}, "
                f"state-event-java.yaml={sorted(java_required)}"
            )

        # payload definitions
        json_payload_name = payload_ref_name(json_event)
        java_payload_name = payload_ref_name(java_event)
        if json_payload_name != java_payload_name:
            errors.append(
                f"{name}: payload $ref name differs — state.event.json={json_payload_name}, "
                f"state-event-java.yaml={java_payload_name}"
            )
            continue

        json_payload = payload_def(json_defs, json_payload_name)
        java_payload = payload_def(java_schemas, java_payload_name)

        json_payload_props = set(json_payload.get("properties", {}).keys())
        java_payload_props = set(java_payload.get("properties", {}).keys())
        if json_payload_props != java_payload_props:
            errors.append(
                f"{json_payload_name}: payload property names differ — state.event.json={sorted(json_payload_props)}, "
                f"state-event-java.yaml={sorted(java_payload_props)}"
            )

        json_payload_required = set(json_payload.get("required", []))
        java_payload_required = set(java_payload.get("required", []))
        if json_payload_required != java_payload_required:
            errors.append(
                f"{json_payload_name}: payload 'required' differs — state.event.json={sorted(json_payload_required)}, "
                f"state-event-java.yaml={sorted(java_payload_required)}"
            )

    if errors:
        for e in errors:
            print(f"FAIL  {e}")
        return 1

    print(f"PASS  state.event.json <-> state-event-java.yaml structurally in sync ({len(json_names)} event types)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
