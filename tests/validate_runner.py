"""
Schema-level validation for schemas/agent-runner/*.json.

Mirrors validate_demand.py's pattern: validates the JSON Schemas directly
against example documents, independent of any language binding.
Run: python tests/validate_runner.py
"""
import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parent.parent
SCHEMAS = ROOT / "schemas" / "agent-runner"

GOOD_DISPATCH_REQUEST = {
    "repo": "plantpal",
    "prompt": "factory-operation:9f0e2b1a-1111-2222-3333-444455556666\nImplement and test the approved plan. Do not deploy.\n...",
    "demandId": "factory-20260911-mission-3c9c9b2a",
}

GOOD_DISPATCH_REQUEST_WITH_OVERRIDES = {
    "repo": "design-studio",
    "prompt": "Investigate the reported regression.",
    "model": "",
    "effort": "high",
    "runtime": "claude-code",
}

BAD_DISPATCH_REQUEST_MISSING_PROMPT = {
    "repo": "plantpal",
}

BAD_DISPATCH_REQUEST_BAD_REPO = {
    "repo": "Not-A-Repo!",
    "prompt": "do work",
}

GOOD_RUN_RECORD_LAUNCHED = {
    "id": "factory-operation:9f0e2b1a-1111-2222-3333-444455556666",
    "repo": "plantpal",
    "prompt": "factory-operation:9f0e2b1a-1111-2222-3333-444455556666\nImplement and test the approved plan. Do not deploy.\n...",
    "demandId": "factory-20260911-mission-3c9c9b2a",
    "state": "launched",
    "startedAt": "2026-09-11T10:00:00Z",
    "exitCode": None,
    "timedOut": False,
    "stopped": False,
    "transcriptPath": "/var/agent-runner/transcripts/9f0e2b1a.jsonl",
}

GOOD_RUN_RECORD_FINISHED = {
    **GOOD_RUN_RECORD_LAUNCHED,
    "state": "finished",
    "endedAt": "2026-09-11T10:14:00Z",
    "exitCode": 0,
    "tokensUsed": 48213,
    "tokensIn": 40000,
    "tokensOut": 8213,
    "model": "claude-sonnet-5",
    "runtime": "claude-code",
    "usageProvider": "claude-code-session",
}

BAD_RUN_RECORD_MISSING_REQUIRED = {
    "id": "run-1",
    "repo": "plantpal",
    # missing prompt, state, startedAt, exitCode, timedOut, stopped, transcriptPath
}

BAD_RUN_RECORD_BAD_STATE = {
    **GOOD_RUN_RECORD_LAUNCHED,
    "state": "queued",  # not one of agent-runner's real states (launched/finished/failed/stopped)
}

GOOD_TRANSCRIPT_SNAPSHOT_IN_PROGRESS = {
    "transcriptTail": ["{\"type\": \"system\", \"subtype\": \"init\"}"],
    "result": None,
    "resultTruncated": False,
}

GOOD_TRANSCRIPT_SNAPSHOT_FINISHED = {
    "transcriptTail": ["...", "{\"type\": \"result\", \"result\": \"Done.\"}"],
    "result": "Done.",
    "resultTruncated": False,
}

BAD_TRANSCRIPT_SNAPSHOT_MISSING_FIELDS = {
    "transcriptTail": [],
}


def load(name: str) -> dict:
    return json.loads((SCHEMAS / name).read_text(encoding="utf-8"))


def expect_valid(schema, doc: dict, label: str) -> None:
    validator = Draft202012Validator(schema)
    errors = list(validator.iter_errors(doc))
    if errors:
        raise AssertionError(f"{label}: expected valid, got errors: {errors}")
    print(f"PASS  {label}")


def expect_invalid(schema, doc: dict, label: str) -> None:
    validator = Draft202012Validator(schema)
    errors = list(validator.iter_errors(doc))
    if not errors:
        raise AssertionError(f"{label}: expected invalid, but document passed")
    print(f"PASS  {label} (rejected: {errors[0].message})")


def main() -> int:
    dispatch_schema = load("runner.dispatch-request.json")
    run_record_schema = load("runner.run-record.json")
    transcript_schema = load("runner.transcript-snapshot.json")

    expect_valid(dispatch_schema, GOOD_DISPATCH_REQUEST, "runner.dispatch-request: correlation-token-prefixed prompt (known-good)")
    expect_valid(dispatch_schema, GOOD_DISPATCH_REQUEST_WITH_OVERRIDES, "runner.dispatch-request: model/effort/runtime overrides (known-good)")
    expect_invalid(dispatch_schema, BAD_DISPATCH_REQUEST_MISSING_PROMPT, "runner.dispatch-request: missing prompt (known-bad)")
    expect_invalid(dispatch_schema, BAD_DISPATCH_REQUEST_BAD_REPO, "runner.dispatch-request: repo not a functional name (known-bad)")

    expect_valid(run_record_schema, GOOD_RUN_RECORD_LAUNCHED, "runner.run-record: launched, no result yet (known-good)")
    expect_valid(run_record_schema, GOOD_RUN_RECORD_FINISHED, "runner.run-record: finished with token usage (known-good)")
    expect_invalid(run_record_schema, BAD_RUN_RECORD_MISSING_REQUIRED, "runner.run-record: missing required fields (known-bad)")
    expect_invalid(run_record_schema, BAD_RUN_RECORD_BAD_STATE, "runner.run-record: state outside the real 4-value enum (known-bad)")

    expect_valid(transcript_schema, GOOD_TRANSCRIPT_SNAPSHOT_IN_PROGRESS, "runner.transcript-snapshot: in-progress, result null (known-good)")
    expect_valid(transcript_schema, GOOD_TRANSCRIPT_SNAPSHOT_FINISHED, "runner.transcript-snapshot: finished with result (known-good)")
    expect_invalid(transcript_schema, BAD_TRANSCRIPT_SNAPSHOT_MISSING_FIELDS, "runner.transcript-snapshot: missing result/resultTruncated (known-bad)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
