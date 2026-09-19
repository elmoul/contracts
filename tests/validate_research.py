"""
Schema-level validation for schemas/ai-gateway/research.yaml's
ResearchJobRequest and ResearchJobStatus schemas -- fulfils demand
ai-gateway-20260917-contracts-research-evidence-envelope: an additive async
job envelope for evidence-gathering (URL-retrieval) requests, distinct from
ai.request/ai.job's existing shapes.

Follows the pattern established in validate_ai_job.py: validates the JSON
Schema directly against example documents, independent of any language
binding. research.yaml is an OpenAPI document rather than a standalone JSON
Schema, so the relevant schema is pulled out of components.schemas before
validating.

ResearchJobRequest coverage: a two-source submission (known-good), a missing
sources array (known-bad, required field), an empty sources array (known-bad,
minItems: 1), and a source missing its required maxBytesPerSource
(known-bad).

ResearchJobStatus coverage: a freshly-queued status carrying only the
required fields (known-good, proves evidence/error/startedAt/finishedAt are
all truly optional), a succeeded status with a full evidence array mixing
retrieved/unavailable/rejected entries (known-good, proves EvidenceItem's
status-dependent fields), a failed status with a populated error (known-good,
also proves the "with error is valid" side of the conditional-required
clause), a missing required submittedAt (known-bad), an unknown status enum
value (known-bad), an evidence item with an unknown status enum value
(known-bad), and a failed status with no error at all (known-bad, proves the
new if/then "status: failed requires error" clause, same idiom as
ai.job.status's D023 pattern).
"""
import sys
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parent.parent
RESEARCH_SPEC = ROOT / "schemas" / "ai-gateway" / "research.yaml"

GOOD_REQUEST = {
    "jobId": "8f14e45f-ceea-467e-adde-3fb5ba8a4b1a",
    "appId": "plantpal",
    "sources": [
        {
            "url": "https://example.com/plant-care-guide",
            "maxDurationMs": 5000,
            "maxBytesPerSource": 1048576,
        },
        {
            "url": "https://example.org/soil-ph-reference",
            "maxDurationMs": 3000,
            "maxBytesPerSource": 524288,
        },
    ],
}

BAD_REQUEST_MISSING_SOURCES = {
    "jobId": "8f14e45f-ceea-467e-adde-3fb5ba8a4b1a",
    "appId": "plantpal",
}

BAD_REQUEST_EMPTY_SOURCES = {
    "jobId": "8f14e45f-ceea-467e-adde-3fb5ba8a4b1a",
    "appId": "plantpal",
    "sources": [],
}

BAD_REQUEST_SOURCE_MISSING_MAX_BYTES = {
    "jobId": "8f14e45f-ceea-467e-adde-3fb5ba8a4b1a",
    "appId": "plantpal",
    "sources": [
        {"url": "https://example.com/plant-care-guide", "maxDurationMs": 5000},
    ],
}

GOOD_QUEUED_STATUS = {
    "jobId": "8f14e45f-ceea-467e-adde-3fb5ba8a4b1a",
    "status": "queued",
    "submittedAt": "2026-09-17T09:00:00Z",
}

GOOD_SUCCEEDED_STATUS = {
    "jobId": "8f14e45f-ceea-467e-adde-3fb5ba8a4b1a",
    "status": "succeeded",
    "evidence": [
        {
            "url": "https://example.com/plant-care-guide",
            "status": "retrieved",
            "fetchedAt": "2026-09-17T09:00:02Z",
            "excerpt": "Pothos prefers indirect light and moist, well-drained soil.",
            "enforcedMaxDurationMs": 5000,
            "enforcedMaxBytes": 1048576,
        },
        {
            "url": "https://example.org/soil-ph-reference",
            "status": "unavailable",
            "enforcedMaxDurationMs": 3000,
            "enforcedMaxBytes": 524288,
            "reason": "timed out after 3000ms",
        },
        {
            "url": "https://example.net/blocked-page",
            "status": "rejected",
            "reason": "disallowed by robots.txt",
        },
    ],
    "submittedAt": "2026-09-17T09:00:00Z",
    "startedAt": "2026-09-17T09:00:01Z",
    "finishedAt": "2026-09-17T09:00:05Z",
}

GOOD_FAILED_STATUS = {
    "jobId": "3b241101-e2bb-4255-8caf-4136c566a962",
    "status": "failed",
    "error": {"code": "backend-unavailable", "message": "Retrieval backend did not respond"},
    "submittedAt": "2026-09-17T01:00:00Z",
    "startedAt": "2026-09-17T01:00:02Z",
    "finishedAt": "2026-09-17T01:00:03Z",
}

BAD_STATUS_MISSING_SUBMITTED_AT = {
    "jobId": "8f14e45f-ceea-467e-adde-3fb5ba8a4b1a",
    "status": "queued",
}

BAD_STATUS_UNKNOWN_ENUM = {
    "jobId": "8f14e45f-ceea-467e-adde-3fb5ba8a4b1a",
    "status": "paused",
    "submittedAt": "2026-09-17T09:00:00Z",
}

BAD_STATUS_EVIDENCE_UNKNOWN_ENUM = {
    "jobId": "8f14e45f-ceea-467e-adde-3fb5ba8a4b1a",
    "status": "running",
    "evidence": [
        {"url": "https://example.com/plant-care-guide", "status": "pending-review"},
    ],
    "submittedAt": "2026-09-17T09:00:00Z",
}

BAD_STATUS_FAILED_MISSING_ERROR = {
    "jobId": "3b241101-e2bb-4255-8caf-4136c566a962",
    "status": "failed",
    "submittedAt": "2026-09-17T01:00:00Z",
    "startedAt": "2026-09-17T01:00:02Z",
    "finishedAt": "2026-09-17T01:00:03Z",
}


def load_components() -> dict:
    return yaml.safe_load(RESEARCH_SPEC.read_text(encoding="utf-8"))["components"]


def component_schema(name: str) -> dict:
    components = load_components()
    return {"components": components, "$ref": f"#/components/schemas/{name}"}


def load_research_job_request_schema() -> dict:
    return component_schema("ResearchJobRequest")


def load_research_job_status_schema() -> dict:
    return component_schema("ResearchJobStatus")


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
    request_schema = load_research_job_request_schema()

    expect_valid(request_schema, GOOD_REQUEST, "research.job.request: two-source submission (known-good)")
    expect_invalid(request_schema, BAD_REQUEST_MISSING_SOURCES, "research.job.request: missing required sources (known-bad)")
    expect_invalid(request_schema, BAD_REQUEST_EMPTY_SOURCES, "research.job.request: empty sources array (known-bad, minItems)")
    expect_invalid(request_schema, BAD_REQUEST_SOURCE_MISSING_MAX_BYTES, "research.job.request: source missing maxBytesPerSource (known-bad)")

    status_schema = load_research_job_status_schema()

    expect_valid(status_schema, GOOD_QUEUED_STATUS, "research.job.status: freshly-queued, only required fields (known-good, proves optionality)")
    expect_valid(status_schema, GOOD_SUCCEEDED_STATUS, "research.job.status: succeeded with retrieved/unavailable/rejected evidence (known-good)")
    expect_valid(status_schema, GOOD_FAILED_STATUS, "research.job.status: failed with populated error (known-good; also proves conditional-required 'with error is valid' side)")
    expect_invalid(status_schema, BAD_STATUS_MISSING_SUBMITTED_AT, "research.job.status: missing required submittedAt (known-bad)")
    expect_invalid(status_schema, BAD_STATUS_UNKNOWN_ENUM, "research.job.status: unknown status enum value (known-bad)")
    expect_invalid(status_schema, BAD_STATUS_EVIDENCE_UNKNOWN_ENUM, "research.job.status: evidence item with unknown status enum value (known-bad)")
    expect_invalid(status_schema, BAD_STATUS_FAILED_MISSING_ERROR, "research.job.status: failed with no error at all (known-bad, conditional-required)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
