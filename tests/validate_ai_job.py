"""
Schema-level validation for schemas/ai-gateway/job.yaml's AiJobRequest and
AiJobStatus schemas (v0.14.0 addition, Media & Agents wave W1 -- D047).

Follows the pattern established in validate_ai_request.py: validates the JSON
Schema directly against example documents, independent of any language
binding. job.yaml is an OpenAPI document rather than a standalone JSON
Schema, so the relevant schema is pulled out of components.schemas before
validating -- same approach as validate_ai_request.py uses for request.yaml.

AiJobRequest coverage: a text-to-image submission and an image-to-3d
submission (known-good, prove both capability shapes validate), a missing
jobClass (known-bad, required field), an unknown capability enum value
(known-bad), and an unexpected property inside `input` (known-bad, proves
input's additionalProperties: false).

AiJobStatus coverage: a freshly-queued status carrying only the required
fields (known-good, proves progressPct/resultRefs/usage/startedAt/finishedAt
are all truly optional, and that `error` is optional outside status=failed),
a succeeded status with resultRefs + usage + full timestamps (known-good), a
failed status with a populated error (known-good), a missing required
submittedAt (known-bad), an unknown status enum value (known-bad), an
out-of-range progressPct (known-bad), and an error object missing its
required `message` (known-bad, proves JobError's own required fields).

Also covers the D023 conditional-requirement added to `AiJobStatus` (mirrors
preflight.yaml's `PreflightResponse` "reason required when decision: block"
pattern): a failed status with no `error` at all is rejected (known-bad, proves
the new `if: status == failed / then: required: [error]` clause), and the
existing failed-with-error case above doubles as the "still valid when
present" side of that same rule.

Run: python tests/validate_ai_job.py
"""
import json
import sys
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parent.parent
JOB_SPEC = ROOT / "schemas" / "ai-gateway" / "job.yaml"

GOOD_TEXT_TO_IMAGE_REQUEST = {
    "jobId": "8f14e45f-ceea-467e-adde-3fb5ba8a4b1a",
    "appId": "plantpal",
    "capability": "text-to-image",
    "input": {"prompt": "a healthy pothos on a sunlit windowsill"},
    "params": {"steps": 4, "aspectRatio": "1:1"},
    "jobClass": "interactive",
}

GOOD_IMAGE_TO_3D_REQUEST = {
    "jobId": "3b241101-e2bb-4255-8caf-4136c566a962",
    "appId": "design-studio",
    "capability": "image-to-3d",
    "input": {"imageRef": "asset://uploads/plant-photo-42.jpg"},
    "params": {"max_num_view": 6, "resolution": 512},
    "jobClass": "batch",
}

BAD_REQUEST_MISSING_JOB_CLASS = {
    "jobId": "8f14e45f-ceea-467e-adde-3fb5ba8a4b1a",
    "appId": "plantpal",
    "capability": "text-to-image",
    "input": {"prompt": "a pothos"},
    "params": {},
}

BAD_REQUEST_UNKNOWN_CAPABILITY = {
    "jobId": "8f14e45f-ceea-467e-adde-3fb5ba8a4b1a",
    "appId": "plantpal",
    "capability": "video-gen",
    "input": {"prompt": "a pothos"},
    "params": {},
    "jobClass": "interactive",
}

BAD_REQUEST_UNKNOWN_INPUT_FIELD = {
    "jobId": "8f14e45f-ceea-467e-adde-3fb5ba8a4b1a",
    "appId": "plantpal",
    "capability": "text-to-image",
    "input": {"prompt": "a pothos", "unexpected": "nope"},
    "params": {},
    "jobClass": "interactive",
}

GOOD_QUEUED_STATUS = {
    "jobId": "8f14e45f-ceea-467e-adde-3fb5ba8a4b1a",
    "status": "queued",
    "submittedAt": "2026-07-16T09:00:00Z",
}

GOOD_SUCCEEDED_STATUS = {
    "jobId": "8f14e45f-ceea-467e-adde-3fb5ba8a4b1a",
    "status": "succeeded",
    "progressPct": 100,
    "resultRefs": ["jobs/8f14e45f/artifacts/output.png"],
    "usage": {"durationMs": 4200, "vramPeakMb": 14336},
    "submittedAt": "2026-07-16T09:00:00Z",
    "startedAt": "2026-07-16T09:00:05Z",
    "finishedAt": "2026-07-16T09:00:09Z",
}

GOOD_FAILED_STATUS = {
    "jobId": "3b241101-e2bb-4255-8caf-4136c566a962",
    "status": "failed",
    "error": {"code": "vram-exhausted", "message": "Requested reservation exceeds free VRAM"},
    "submittedAt": "2026-07-16T01:00:00Z",
    "startedAt": "2026-07-16T01:00:02Z",
    "finishedAt": "2026-07-16T01:00:03Z",
}

BAD_STATUS_MISSING_SUBMITTED_AT = {
    "jobId": "8f14e45f-ceea-467e-adde-3fb5ba8a4b1a",
    "status": "queued",
}

BAD_STATUS_UNKNOWN_ENUM = {
    "jobId": "8f14e45f-ceea-467e-adde-3fb5ba8a4b1a",
    "status": "paused",
    "submittedAt": "2026-07-16T09:00:00Z",
}

BAD_STATUS_PROGRESS_OUT_OF_RANGE = {
    "jobId": "8f14e45f-ceea-467e-adde-3fb5ba8a4b1a",
    "status": "running",
    "progressPct": 150,
    "submittedAt": "2026-07-16T09:00:00Z",
}

BAD_STATUS_ERROR_MISSING_MESSAGE = {
    "jobId": "8f14e45f-ceea-467e-adde-3fb5ba8a4b1a",
    "status": "failed",
    "error": {"code": "vram-exhausted"},
    "submittedAt": "2026-07-16T09:00:00Z",
}

BAD_STATUS_FAILED_MISSING_ERROR = {
    "jobId": "3b241101-e2bb-4255-8caf-4136c566a962",
    "status": "failed",
    "submittedAt": "2026-07-16T01:00:00Z",
    "startedAt": "2026-07-16T01:00:02Z",
    "finishedAt": "2026-07-16T01:00:03Z",
}


def load_components() -> dict:
    return yaml.safe_load(JOB_SPEC.read_text(encoding="utf-8"))["components"]


def component_schema(name: str) -> dict:
    """
    Wrap a single named component as {"components": ..., "$ref": "#/components/schemas/<name>"}
    rather than returning the bare component dict. AiJobStatus's `error`/`usage` fields
    $ref sibling components (JobError/JobUsage) by path from the document root
    (#/components/schemas/...) -- validating the bare AiJobStatus dict standalone (as
    validate_ai_request.py does for AiRequest/AiResponse, which have no such internal
    $refs) leaves those pointers unresolvable. Carrying `components` alongside the $ref
    keeps the same root shape the pointers expect, so Draft202012Validator resolves them.
    """
    components = load_components()
    return {"components": components, "$ref": f"#/components/schemas/{name}"}


def load_ai_job_request_schema() -> dict:
    return component_schema("AiJobRequest")


def load_ai_job_status_schema() -> dict:
    return component_schema("AiJobStatus")


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
    request_schema = load_ai_job_request_schema()

    expect_valid(request_schema, GOOD_TEXT_TO_IMAGE_REQUEST, "ai.job.request: text-to-image submission (known-good)")
    expect_valid(request_schema, GOOD_IMAGE_TO_3D_REQUEST, "ai.job.request: image-to-3d submission (known-good)")
    expect_invalid(request_schema, BAD_REQUEST_MISSING_JOB_CLASS, "ai.job.request: missing required jobClass (known-bad)")
    expect_invalid(request_schema, BAD_REQUEST_UNKNOWN_CAPABILITY, "ai.job.request: unknown capability enum value (known-bad)")
    expect_invalid(request_schema, BAD_REQUEST_UNKNOWN_INPUT_FIELD, "ai.job.request: unexpected property inside input (known-bad)")

    status_schema = load_ai_job_status_schema()

    expect_valid(status_schema, GOOD_QUEUED_STATUS, "ai.job.status: freshly-queued, only required fields (known-good, proves optionality)")
    expect_valid(status_schema, GOOD_SUCCEEDED_STATUS, "ai.job.status: succeeded with resultRefs/usage/full timestamps (known-good)")
    expect_valid(status_schema, GOOD_FAILED_STATUS, "ai.job.status: failed with populated error (known-good; also proves D023 conditional-required 'with error is valid' side)")
    expect_invalid(status_schema, BAD_STATUS_MISSING_SUBMITTED_AT, "ai.job.status: missing required submittedAt (known-bad)")
    expect_invalid(status_schema, BAD_STATUS_UNKNOWN_ENUM, "ai.job.status: unknown status enum value (known-bad)")
    expect_invalid(status_schema, BAD_STATUS_PROGRESS_OUT_OF_RANGE, "ai.job.status: progressPct exceeds 100 (known-bad)")
    expect_invalid(status_schema, BAD_STATUS_ERROR_MISSING_MESSAGE, "ai.job.status: error missing required message (known-bad)")
    expect_invalid(status_schema, BAD_STATUS_FAILED_MISSING_ERROR, "ai.job.status: failed with no error at all (known-bad, D023 conditional-required)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
