"""
Schema-level validation for schemas/app/telemetry.json.

Follows the pattern established in validate_dimension_event.py: validates the
JSON Schema directly against example documents, independent of any language
binding. Covers the v0.10.0 finalization of telemetry.json (STUB -> full
schema, fulfilling demand observability-20260710-telemetry-schema): the root
TelemetryLogRecord shape (the structured JSON log line every hexagon emits to
stdout), plus the two documentation-only $defs that are not root-reachable and
so generate no Java/TypeScript class (see schemas/app/telemetry.json's own
description) -- PrometheusMetricLabels and MetricName. Both are still real
JSON Schema fragments and validated here directly by JSON pointer, matching
observability/docs/telemetry-conventions.md.

Run: python tests/validate_telemetry.py
"""
import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parent.parent
TELEMETRY_SPEC = ROOT / "schemas" / "app" / "telemetry.json"

GOOD_LOG_RECORD = {
    "timestamp": "2026-07-02T12:34:56.789Z",
    "level": "INFO",
    "message": "Preflight authorized",
    "component_id": "ai-gateway",
    "appId": "plantpal",
}

GOOD_LOG_RECORD_MINIMAL = {
    "timestamp": "2026-07-02T12:34:56.789Z",
    "level": "DEBUG",
    "message": "Scrape completed",
    "component_id": "observability",
}

BAD_LOG_RECORD_BAD_LEVEL_MISSING_MESSAGE = {
    "timestamp": "2026-07-02T12:34:56.789Z",
    "level": "TRACE",
    "component_id": "ai-gateway",
}

GOOD_PROMETHEUS_LABELS = {
    "component_id": "treasury",
    "env": "prod",
    "app_id": "plantpal",
}

GOOD_PROMETHEUS_LABELS_WITH_EXTRA = {
    "component_id": "treasury",
    "env": "local",
    "cpu_core": "0",
}

BAD_PROMETHEUS_LABELS_MISSING_ENV = {
    "component_id": "treasury",
}

BAD_PROMETHEUS_LABELS_BAD_ENV = {
    "component_id": "treasury",
    "env": "development",
}

GOOD_METRIC_NAMES = [
    "platform_ai_gateway_requests_total",
    "platform_treasury_preflight_duration_seconds",
    "platform_ci_runner_pipeline_runs_total",
    "platform_observability_scrape_errors_total",
]

BAD_METRIC_NAMES = [
    "ai_gateway_requests_total",  # missing platform_ prefix
    "platform_ai-gateway_requests_total",  # hyphen not allowed
    "platform_treasury_preflight_duration",  # missing unit suffix
]


def load_telemetry_schema() -> dict:
    return json.loads(TELEMETRY_SPEC.read_text(encoding="utf-8"))


def expect_valid(schema: dict, doc, label: str) -> None:
    errors = list(Draft202012Validator(schema).iter_errors(doc))
    if errors:
        raise AssertionError(f"{label}: expected valid, got errors: {errors}")
    print(f"PASS  {label}")


def expect_invalid(schema: dict, doc, label: str) -> None:
    errors = list(Draft202012Validator(schema).iter_errors(doc))
    if not errors:
        raise AssertionError(f"{label}: expected invalid, but document passed")
    print(f"PASS  {label} (rejected: {errors[0].message})")


def main() -> int:
    schema = load_telemetry_schema()
    prometheus_labels_schema = schema["$defs"]["PrometheusMetricLabels"]
    metric_name_schema = schema["$defs"]["MetricName"]

    expect_valid(schema, GOOD_LOG_RECORD, "telemetry: known-good log record")
    expect_valid(
        schema,
        GOOD_LOG_RECORD_MINIMAL,
        "telemetry: known-good log record without optional appId/traceId",
    )
    expect_invalid(
        schema,
        BAD_LOG_RECORD_BAD_LEVEL_MISSING_MESSAGE,
        "telemetry: log record with bad level enum + missing message (known-bad)",
    )

    expect_valid(
        prometheus_labels_schema,
        GOOD_PROMETHEUS_LABELS,
        "telemetry: known-good Prometheus metric labels",
    )
    expect_valid(
        prometheus_labels_schema,
        GOOD_PROMETHEUS_LABELS_WITH_EXTRA,
        "telemetry: Prometheus metric labels with an extra metric-specific label (known-good, additionalProperties: true)",
    )
    expect_invalid(
        prometheus_labels_schema,
        BAD_PROMETHEUS_LABELS_MISSING_ENV,
        "telemetry: Prometheus metric labels missing required env (known-bad)",
    )
    expect_invalid(
        prometheus_labels_schema,
        BAD_PROMETHEUS_LABELS_BAD_ENV,
        "telemetry: Prometheus metric labels with env outside local|staging|prod (known-bad)",
    )

    for name in GOOD_METRIC_NAMES:
        expect_valid(metric_name_schema, name, f"telemetry: known-good metric name {name!r}")
    for name in BAD_METRIC_NAMES:
        expect_invalid(metric_name_schema, name, f"telemetry: known-bad metric name {name!r}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
