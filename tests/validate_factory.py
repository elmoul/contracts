"""
Schema-level validation for schemas/factory/*.json.

Mirrors validate_demand.py's pattern: validates the JSON Schemas directly
against example documents, independent of any language binding.
Run: python tests/validate_factory.py
"""
import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parent.parent
SCHEMAS = ROOT / "schemas" / "factory"

GOOD_CHECKPOINT_EMPTY = {"branch": "", "commits": [], "summary": "", "remainingChecks": []}

GOOD_CHECKPOINT = {
    "branch": "factory/mission-abc",
    "commits": ["a1b2c3d", "e4f5a6b"],
    "summary": "Implementation and tests landed; deployment still outstanding",
    "remainingChecks": ["deploy candidate", "record deployment ID", "verify live"],
}

GOOD_CONTINUATION = {
    "system": "app-studio",
    "id": "app-studio-plantpal-mission-1",
    "receipts": {"mission": {"hash": "abc123"}, "plan.json": {"hash": "def456"}},
    "approvedWaves": [1],
    "outstandingWaves": [{"wave": 2, "goal": "Protected pages"}],
    "claimBoundary": "Only wave 1 is claimed complete.",
    "legacyStage": "closed",
}

BAD_CONTINUATION_WRONG_SYSTEM = {
    **GOOD_CONTINUATION,
    "system": "app-builder",  # not the fixed const "app-studio"
}

BAD_CONTINUATION_MISSING_REQUIRED = {
    "system": "app-studio",
    # missing id, legacyStage
}

GOOD_EVIDENCE_RECEIPT = {
    "id": "6f8f2e2a-2c8b-4a8b-9b3d-2f7e5b6c1a10",
    "kind": "implementation",
    "criteria": ["wave-2"],
    "result": "passed",
    "revision": "a1b2c3d",
    "deployment": "",
    "summary": "Implemented the outstanding redirects for wave 2",
    "source": "PR #42, CI run 1234",
    "observer": "agent-runner session 9f0e",
    "recordedAt": "2026-09-11T10:00:00Z",
    "provenance": "owner-attestation",
    "planHash": "a" * 64,
    "hash": "b" * 64,
}

BAD_EVIDENCE_RECEIPT_BAD_PROVENANCE = {
    **GOOD_EVIDENCE_RECEIPT,
    "provenance": "ci-verified",  # only "owner-attestation" is a valid value in this slice
}

BAD_EVIDENCE_RECEIPT_MISSING_FIELDS = {
    "id": "6f8f2e2a-2c8b-4a8b-9b3d-2f7e5b6c1a10",
    "kind": "implementation",
    "result": "passed",
    # missing criteria, revision, deployment, summary, source, observer, recordedAt, provenance, planHash, hash
}

GOOD_OUTCOME = {
    "id": "3c9c9b2a-2c8b-4a8b-9b3d-2f7e5b6c1a10",
    "version": 2,
    "app": "plantpal",
    "kind": "feature",
    "risk": "high",
    "title": "Finish protected pages & inactivity sessions",
    "plan": "Inspect the current app against the preserved approved architecture and implement the outstanding waves.",
    "criteria": [
        {"id": "wave-2", "outcome": "Protected pages redirect unauthenticated users", "acceptance": "Manual + automated redirect check on every protected route"},
    ],
    "phase": "implement",
    "status": "active",
    "createdAt": "2026-09-11T09:00:00Z",
    "candidate": "",
    "paused": False,
    "checkpoint": GOOD_CHECKPOINT_EMPTY,
    "source": GOOD_CONTINUATION,
    "approvals": [
        {"kind": "plan", "planHash": "a" * 64, "revision": "", "autoRelease": False, "at": "2026-09-11T09:05:00Z", "note": "Bounded plan reviewed and approved"},
    ],
}

BAD_OUTCOME_MISSING_CHECKPOINT = {k: v for k, v in GOOD_OUTCOME.items() if k != "checkpoint"}

BAD_OUTCOME_BAD_KIND = {**GOOD_OUTCOME, "kind": "chore"}  # not one of bug/feature/new-app


def load(name: str) -> dict:
    return json.loads((SCHEMAS / name).read_text(encoding="utf-8"))


def expect_valid(schema, doc: dict, label: str) -> None:
    validator = schema if isinstance(schema, Draft202012Validator) else Draft202012Validator(schema)
    errors = list(validator.iter_errors(doc))
    if errors:
        raise AssertionError(f"{label}: expected valid, got errors: {errors}")
    print(f"PASS  {label}")


def expect_invalid(schema, doc: dict, label: str) -> None:
    validator = schema if isinstance(schema, Draft202012Validator) else Draft202012Validator(schema)
    errors = list(validator.iter_errors(doc))
    if not errors:
        raise AssertionError(f"{label}: expected invalid, but document passed")
    print(f"PASS  {label} (rejected: {errors[0].message})")


def main() -> int:
    checkpoint_schema = load("factory.recovery-checkpoint.json")
    continuation_schema = load("factory.continuation.json")
    evidence_schema = load("factory.evidence-receipt.json")
    outcome_schema = load("factory.outcome.json")

    # factory.outcome.json $refs its siblings by on-disk filename ("factory.continuation.json",
    # "factory.recovery-checkpoint.json"), same convention as demand.approval-receipt.json —
    # register each sibling under the filename URI that a relative $ref from outcome_schema's
    # own $id resolves to, not under the sibling's own shorter $id string.
    registry = Registry().with_resources(
        [
            (continuation_schema["$id"] + ".json", Resource.from_contents(continuation_schema)),
            (checkpoint_schema["$id"] + ".json", Resource.from_contents(checkpoint_schema)),
        ]
    )
    outcome_validator = Draft202012Validator(outcome_schema, registry=registry)

    expect_valid(checkpoint_schema, GOOD_CHECKPOINT_EMPTY, "factory.recovery-checkpoint: empty checkpoint (known-good)")
    expect_valid(checkpoint_schema, GOOD_CHECKPOINT, "factory.recovery-checkpoint: in-progress checkpoint (known-good)")

    expect_valid(continuation_schema, GOOD_CONTINUATION, "factory.continuation: PlantPal-shaped continuation (known-good)")
    expect_invalid(continuation_schema, BAD_CONTINUATION_WRONG_SYSTEM, "factory.continuation: system other than app-studio (known-bad)")
    expect_invalid(continuation_schema, BAD_CONTINUATION_MISSING_REQUIRED, "factory.continuation: missing required fields (known-bad)")

    expect_valid(evidence_schema, GOOD_EVIDENCE_RECEIPT, "factory.evidence-receipt: passed implementation evidence (known-good)")
    expect_invalid(evidence_schema, BAD_EVIDENCE_RECEIPT_BAD_PROVENANCE, "factory.evidence-receipt: non-owner-attestation provenance (known-bad)")
    expect_invalid(evidence_schema, BAD_EVIDENCE_RECEIPT_MISSING_FIELDS, "factory.evidence-receipt: missing required fields (known-bad)")

    expect_valid(outcome_validator, GOOD_OUTCOME, "factory.outcome: high-risk continuation outcome with plan approval (known-good)")
    expect_invalid(outcome_validator, BAD_OUTCOME_MISSING_CHECKPOINT, "factory.outcome: missing required checkpoint (known-bad)")
    expect_invalid(outcome_validator, BAD_OUTCOME_BAD_KIND, "factory.outcome: kind outside bug/feature/new-app (known-bad)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
