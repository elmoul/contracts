"""
Schema-level validation for schemas/delivery/*.json (D113 task delivery, v0.31.0)
plus a parse check of schemas/delivery-api/youtrack-delivery.openapi.yaml and a
round-trip through the generated Python binding.

Extended (v0.34.0) with schemas/delivery-api/ci-runner-results.openapi.yaml: route
presence plus validation of its component schemas (result list, not-found body).

Mirrors validate_factory.py: validates the JSON Schemas directly against example
documents, independent of any language binding.
Run: python tests/validate_delivery.py
"""
import copy
import json
import sys
from datetime import datetime
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parent.parent
SCHEMAS = ROOT / "schemas" / "delivery"
API = ROOT / "schemas" / "delivery-api" / "youtrack-delivery.openapi.yaml"
CI_API = ROOT / "schemas" / "delivery-api" / "ci-runner-results.openapi.yaml"

SHA_A = "a" * 64
SHA_B = "b" * 64
SHA_C = "c" * 64
REV_TASK = "1" * 40
REV_MERGED = "2" * 40
DELIVERY = "3c9c9b2a-2c8b-4a8b-9b3d-2f7e5b6c1a10"
NOW = "2026-09-27T10:00:00Z"

ISSUE_REF = {"vendorId": "2-17", "idReadable": "PLA-12", "project": "PLA"}

GOOD_ISSUE = {
    "issue": ISSUE_REF,
    "summary": "Show watering reminders on the dashboard",
    "description": "As an owner I want reminders.\n\n## Acceptance criteria\n- reminder card visible",
    "acceptance": "- reminder card visible",
    "type": "Task",
    "priority": "Normal",
    "state": {"field": "State", "name": "Open", "resolved": False},
    "created": "2026-09-20T09:00:00Z",
    "updated": "2026-09-27T09:00:00Z",
    "resolvedAt": None,
    "scope": {
        "fingerprint": SHA_A,
        "algorithm": "sha256-canonical-json-v1",
        "fields": ["summary", "description", "acceptance", "type", "priority", "parent", "dependencies"],
    },
    "parent": {"vendorId": "2-3", "idReadable": "PLA-1", "project": "PLA"},
    "subtasks": [],
    "dependencies": [
        {"direction": "depends-on", "issue": {"vendorId": "2-9", "idReadable": "PLA-8", "project": "PLA"}, "status": "resolved"},
    ],
    "dependenciesComplete": True,
    "deliveryLinks": [],
    "readAt": NOW,
}

# Dependency that could not be read: valid shape, but consumers must treat it as blocked.
GOOD_ISSUE_UNKNOWN_DEPENDENCY = {
    **GOOD_ISSUE,
    "dependencies": [{"direction": "depends-on", "issue": None, "status": "unknown"}],
    "dependenciesComplete": False,
}

BAD_ISSUE_DEPENDENCY_SATISFIED_BY_OMISSION = {
    **GOOD_ISSUE,
    "dependencies": [{"direction": "depends-on", "issue": None, "status": "satisfied"}],  # not an enum value
}

BAD_ISSUE_CARRIES_TOKEN = {**GOOD_ISSUE, "token": "perm:abc"}  # closed shape, no credential field

BAD_ISSUE_READABLE_AS_VENDOR_ID = {**GOOD_ISSUE, "issue": {**ISSUE_REF, "vendorId": "PLA-12"}}

GOOD_PAGE_INTERMEDIATE = {
    "items": [GOOD_ISSUE],
    "nextCursor": "opaque-1",
    "complete": False,
    "query": {"projects": ["PLA"], "openOnly": True},
    "unavailableProjects": [],
    "readAt": NOW,
}

GOOD_PAGE_LAST_PARTIAL = {
    "items": [],
    "nextCursor": None,
    "complete": False,
    "query": {"projects": ["PLA", "OPS"], "openOnly": True},
    "unavailableProjects": [{"project": "OPS", "code": "tracker_permission_denied"}],
    "readAt": NOW,
}

BAD_PAGE_NO_COMPLETE_FLAG = {k: v for k, v in GOOD_PAGE_INTERMEDIATE.items() if k != "complete"}

GOOD_WORKFLOW = {
    "project": "PLA",
    "stateField": "State",
    "states": [
        {"id": "s-1", "name": "Open", "resolved": False, "ordinal": 0, "archived": False},
        {"id": "s-2", "name": "In Progress", "resolved": False, "ordinal": 1, "archived": False},
        {"id": "s-3", "name": "Done", "resolved": True, "ordinal": 2, "archived": False},
    ],
    "complete": True,
    "readAt": NOW,
}

CORRELATION = {"deliveryId": DELIVERY, "planHash": SHA_B, "candidateRevision": REV_MERGED, "stage": "accepted"}

ACCEPTANCE_REF = {
    "decisionId": "7a1c2e3d-2c8b-4a8b-9b3d-2f7e5b6c1a10",
    "decisionHash": SHA_C,
    "kind": "owner-acceptance",
    "basis": "owner",
    "candidateRevision": REV_MERGED,
    "deploymentId": "plantpal-dev-2026-09-27-01",
    "decidedAt": NOW,
}

GOOD_SYNC_RESOLVE = {
    "operationKey": f"{DELIVERY}:resolve:accepted:1",
    "issue": ISSUE_REF,
    "correlation": CORRELATION,
    "expectedScope": SHA_A,
    "expectedState": "In Progress",
    "payload": {"kind": "resolve", "targetState": "Done", "acceptance": ACCEPTANCE_REF},
}

GOOD_SYNC_COMMENT_NO_SCOPE = {
    "operationKey": f"{DELIVERY}:comment:scope-changed:1",
    "issue": ISSUE_REF,
    "correlation": {**CORRELATION, "candidateRevision": None, "stage": "plan-invalidated"},
    "expectedScope": None,
    "expectedState": None,
    "payload": {"kind": "comment", "text": "Scope changed; plan re-approval required."},
}

GOOD_SYNC_LINK = {
    **GOOD_SYNC_COMMENT_NO_SCOPE,
    "operationKey": f"{DELIVERY}:link:delivery:1",
    "payload": {"kind": "link", "url": "http://127.0.0.1:8093/deliveries/" + DELIVERY, "title": "Factory delivery"},
}

GOOD_SYNC_TRANSITION = {
    **GOOD_SYNC_RESOLVE,
    "operationKey": f"{DELIVERY}:transition:implementing:1",
    "payload": {"kind": "transition", "targetState": "In Progress"},
}

# Ready-for-test / worker completion / policy / coordinator approval cannot stand in for acceptance.
BAD_RESOLVE_WITH_POLICY = copy.deepcopy(GOOD_SYNC_RESOLVE)
BAD_RESOLVE_WITH_POLICY["payload"]["acceptance"].update({"kind": "policy-authorization", "basis": "policy"})

BAD_RESOLVE_READY_FOR_TEST = copy.deepcopy(GOOD_SYNC_RESOLVE)
BAD_RESOLVE_READY_FOR_TEST["payload"]["acceptance"]["kind"] = "ready-for-testing"

BAD_RESOLVE_WORKER_EXIT = copy.deepcopy(GOOD_SYNC_RESOLVE)
BAD_RESOLVE_WORKER_EXIT["payload"]["acceptance"] = {"runId": "run-1", "exitCode": 0}

BAD_RESOLVE_COORDINATOR_APPROVAL = copy.deepcopy(GOOD_SYNC_RESOLVE)
BAD_RESOLVE_COORDINATOR_APPROVAL["payload"]["acceptance"]["basis"] = "coordinator"

BAD_RESOLVE_WITHOUT_ACCEPTANCE = copy.deepcopy(GOOD_SYNC_RESOLVE)
del BAD_RESOLVE_WITHOUT_ACCEPTANCE["payload"]["acceptance"]

BAD_RESOLVE_WITHOUT_SCOPE = {**GOOD_SYNC_RESOLVE, "expectedScope": None}
BAD_TRANSITION_WITHOUT_SCOPE = {**GOOD_SYNC_TRANSITION, "expectedScope": None}

BAD_SYNC_SHORT_KEY = {**GOOD_SYNC_LINK, "operationKey": "k1"}

BAD_SYNC_SHORT_SHA = copy.deepcopy(GOOD_SYNC_RESOLVE)
BAD_SYNC_SHORT_SHA["correlation"]["candidateRevision"] = "2222222"

# v0.35.0 — retention coverage. A Factory restart that looks up a key minted before
# the service's coverage floor gets a miss it must NOT read as "never used": the
# record may have been stored, completed and purged. Key provenance (reservedAt) is
# what separates the two, and it travels in the request body so the write path can be
# gated too. GOOD_SYNC_LINK_RESERVED is the recommended shape.
GOOD_SYNC_LINK_RESERVED = {**GOOD_SYNC_LINK, "reservedAt": NOW}
# A type violation, deliberately: `format: date-time` is declared on every timestamp
# in these schemas but this suite does not enforce it (`jsonschema` has no rfc3339
# checker installed, so `format` is inert -- pre-existing, repo-wide, and unchanged
# here). Only the type is actually covered. Recorded in the v0.35.0 report.
BAD_SYNC_RESERVED_AT_NOT_A_STRING = {**GOOD_SYNC_LINK, "reservedAt": 20260927}

OP_BASE = {
    "operationKey": GOOD_SYNC_RESOLVE["operationKey"],
    "requestHash": SHA_C,
    "kind": "resolve",
    "issue": ISSUE_REF,
    "correlation": CORRELATION,
    "createdAt": NOW,
    "updatedAt": NOW,
}

GOOD_OP_CONFIRMED = {
    **OP_BASE,
    "status": "confirmed",
    "attempts": 1,
    "readBack": {"observedAt": NOW, "effectPresent": True, "vendorRef": None, "observedState": "Done", "observedScope": SHA_A},
    "error": None,
    "retainUntil": "2026-12-26T10:00:00Z",
}

GOOD_OP_UNCERTAIN = {
    **OP_BASE,
    "status": "uncertain",
    "attempts": 1,
    "readBack": {"observedAt": NOW, "effectPresent": None, "vendorRef": None, "observedState": None, "observedScope": None},
    "error": {"code": "tracker_outcome_unknown", "message": "timeout after send", "retryable": False, "ownerAction": None},
    "retainUntil": None,
    "vendorInFlightBoundSeconds": 600,
}

GOOD_OP_REJECTED_SCOPE = {
    **OP_BASE,
    "status": "rejected",
    "attempts": 0,
    "readBack": None,
    "error": {
        "code": "scope_changed",
        "message": "issue description edited since plan approval",
        "retryable": False,
        "ownerAction": "Review the edited issue and re-approve the plan.",
        "details": {"currentScope": SHA_B},
    },
    "retainUntil": "2026-12-26T10:00:00Z",
}

GOOD_OP_RESERVED = {**OP_BASE, "status": "reserved", "attempts": 0, "readBack": None, "error": None, "retainUntil": None}

BAD_OP_CONFIRMED_WITHOUT_READBACK = {**GOOD_OP_CONFIRMED, "readBack": None}
BAD_OP_CONFIRMED_EFFECT_ABSENT = copy.deepcopy(GOOD_OP_CONFIRMED)
BAD_OP_CONFIRMED_EFFECT_ABSENT["readBack"]["effectPresent"] = False
BAD_OP_EXACTLY_ONCE = {**GOOD_OP_CONFIRMED, "status": "delivered-exactly-once"}

# --- v0.35.0 negative recovery fixtures -------------------------------------
# Three shapes the contract must refuse, each one a way a caller could otherwise
# be told a possibly-completed write is safe to repeat.

# (1) Absence in ONE read-back. The effect was not on the issue at one instant;
# a delayed original request can still land, so an unwindowed absence observation
# is not a recordable fact. `readBack.absentSince`/`absenceQuietUntil` are required
# whenever `effectPresent` is false.
ABSENT_SINCE = "2026-09-27T09:00:00Z"
QUIET_UNTIL = "2026-09-27T09:10:00Z"  # ABSENT_SINCE + vendorInFlightBoundSeconds (600)
OBSERVED_LATER = "2026-09-27T09:30:00Z"
BAD_OP_ABSENT_WITHOUT_WINDOW = copy.deepcopy(GOOD_OP_UNCERTAIN)
BAD_OP_ABSENT_WITHOUT_WINDOW["readBack"]["effectPresent"] = False

GOOD_OP_ABSENT_IN_WINDOW = {
    **GOOD_OP_UNCERTAIN,
    "readBack": {
        "observedAt": OBSERVED_LATER,
        "effectPresent": False,
        "vendorRef": None,
        "observedState": "In Progress",
        "observedScope": SHA_A,
        "absentSince": ABSENT_SINCE,
        "absenceQuietUntil": QUIET_UNTIL,
    },
}

# (2) A resend WITHOUT proof of non-execution. `attempts >= 2` is only legal with a
# recorded `absenceProvenAt`; there is no way to spell "we resent and hoped".
GOOD_OP_RESENT_AFTER_QUIET = {**GOOD_OP_ABSENT_IN_WINDOW, "attempts": 2, "absenceProvenAt": QUIET_UNTIL}
BAD_OP_RESENT_WITHOUT_PROOF_NULL = {**GOOD_OP_RESENT_AFTER_QUIET, "absenceProvenAt": None}
BAD_OP_RESENT_WITHOUT_PROOF_MISSING = copy.deepcopy(GOOD_OP_RESENT_AFTER_QUIET)
del BAD_OP_RESENT_WITHOUT_PROOF_MISSING["absenceProvenAt"]
# Resend authorised before the quiet window closed. The schema cannot compare two
# timestamps, so this document is schema-VALID and `check_recovery_semantics` below
# is what refuses it.
BAD_OP_RESENT_BEFORE_QUIET = {**GOOD_OP_RESENT_AFTER_QUIET, "absenceProvenAt": ABSENT_SINCE}

# (3) Retention/purge bookkeeping. Open records are never purged (else a key could
# vanish while its outcome is still open) and terminal records always carry the
# deadline that makes the coverage floor computable.
BAD_OP_UNCERTAIN_PURGEABLE = {**GOOD_OP_UNCERTAIN, "retainUntil": "2026-12-26T10:00:00Z"}
BAD_OP_CONFIRMED_NO_RETENTION = {**GOOD_OP_CONFIRMED, "retainUntil": None}
# An unknown outcome must never be reported as safe to resubmit.
BAD_OP_UNCERTAIN_RETRYABLE = {
    **GOOD_OP_UNCERTAIN,
    "error": {"code": "tracker_outcome_unknown", "message": "timeout after send", "retryable": True, "ownerAction": None},
}
# `retryable: false` on an absent error is vacuous; the reason must be there at all.
BAD_OP_UNCERTAIN_NO_ERROR = {**GOOD_OP_UNCERTAIN, "error": None}
BAD_OP_UNCERTAIN_UNAVAILABLE_ERROR = {
    **GOOD_OP_UNCERTAIN,
    "error": {"code": "tracker_unavailable", "message": "vendor unreachable", "retryable": True, "ownerAction": None},
}

# The service's coverage statement: what a lookup miss can and cannot prove.
COVERAGE_BASE = {
    "observedAt": NOW,
    "coveredSince": "2026-06-29T10:00:00Z",  # NOW - terminalRetentionDays
    "terminalRetentionDays": 90,
    "vendorInFlightBoundSeconds": 600,
}
GOOD_COVERAGE = COVERAGE_BASE
BAD_COVERAGE_SHORT_RETENTION = {**COVERAGE_BASE, "terminalRetentionDays": 30}
BAD_COVERAGE_ZERO_BOUND = {**COVERAGE_BASE, "vendorInFlightBoundSeconds": 0}
BAD_COVERAGE_NO_FLOOR = {k: v for k, v in COVERAGE_BASE.items() if k != "coveredSince"}

# The two lookup-miss answers, and the ways a caller could be misled by them.
KEY_RESERVED_FRESH = "2026-09-27T09:55:00Z"
KEY_RESERVED_EXPIRED = "2026-03-01T10:00:00Z"  # long before coveredSince

ERR_OPERATION_NOT_FOUND = {
    "code": "operation_not_found",
    "message": "no record of key ...:transition:implementing:1",
    "retryable": True,
    "ownerAction": None,
    "details": {"reservedAt": KEY_RESERVED_FRESH, "coveredSince": COVERAGE_BASE["coveredSince"]},
}
ERR_LOOKUP_OUT_OF_COVERAGE = {
    "code": "operation_lookup_out_of_coverage",
    "message": "key predates the operation store's coverage floor; a terminal record for it may have been purged",
    "retryable": False,
    "ownerAction": "Check the issue in YouTrack for this key's marker before resending; if the write is absent, mint a new key.",
    "details": {"coveredSince": COVERAGE_BASE["coveredSince"], "reason": "reserved_at_before_coverage", "reservedAt": KEY_RESERVED_EXPIRED},
}
ERR_LOOKUP_NO_PROVENANCE = {
    "code": "operation_lookup_out_of_coverage",
    "message": "lookup miss with no reservedAt provenance; cannot be classified",
    "retryable": False,
    "ownerAction": "Re-look-up supplying the key's reservedAt from Factory's own store.",
    "details": {"coveredSince": COVERAGE_BASE["coveredSince"], "reason": "no_key_provenance", "reservedAt": None},
}
# A bare miss dressed up as a conclusive one: no provenance, no floor, so nothing
# supports "never stored". This is the exact shortcut the contract removes.
BAD_ERR_NOT_FOUND_NO_PROVENANCE = {
    "code": "operation_not_found",
    "message": "not found",
    "retryable": True,
    "details": {},
}
BAD_ERR_NOT_FOUND_NOT_RETRYABLE = {**ERR_OPERATION_NOT_FOUND, "retryable": False}
BAD_ERR_OUT_OF_COVERAGE_RETRYABLE = {**ERR_LOOKUP_OUT_OF_COVERAGE, "retryable": True}
BAD_ERR_OUT_OF_COVERAGE_NO_REASON = {**ERR_LOOKUP_OUT_OF_COVERAGE, "details": {"coveredSince": COVERAGE_BASE["coveredSince"]}}
BAD_ERR_OUT_OF_COVERAGE_BAD_REASON = {**ERR_LOOKUP_OUT_OF_COVERAGE, "details": {**ERR_LOOKUP_OUT_OF_COVERAGE["details"], "reason": "expired"}}

EVIDENCE_BASE = {
    "id": "5d1e2f3a-2c8b-4a8b-9b3d-2f7e5b6c1a10",
    "deliveryId": DELIVERY,
    "issue": ISSUE_REF,
    "criteria": [{"criterionId": "reminder-card", "evaluableAt": "tests"}],
    "scope": {"planHash": SHA_B, "issueScope": SHA_A},
    "repository": "plantpal",
    "observer": "ci-runner",
    "observedAt": NOW,
    "recordedAt": NOW,
    "summary": "CI workflow `test` concluded success at the task revision",
    "supersedes": None,
    "legacyReceipt": None,
    "hash": SHA_C,
}

GOOD_EVIDENCE_CI_TASK = {
    **EVIDENCE_BASE,
    "stage": "ci",
    "basis": "machine-observation",
    "result": "passed",
    "exitCode": 0,
    "branch": "factory/pla-12",
    "revision": REV_TASK,
    "revisionRole": "task",
    "source": {"producer": "ci-runner", "recordRef": "ci-runner:ci.run/9001/42", "runId": "9001", "artifactRef": None, "url": None},
    "environment": None,
}

GOOD_EVIDENCE_LIVE = {
    **EVIDENCE_BASE,
    "stage": "live",
    "basis": "machine-observation",
    "result": "passed",
    "exitCode": None,
    "criteria": [{"criterionId": "reminder-card", "evaluableAt": "live"}],
    "branch": "dev",
    "revision": REV_MERGED,
    "revisionRole": "merged",
    "source": {"producer": "app-deploy", "recordRef": "plantpal:deployments/plantpal-dev-2026-09-27-01", "runId": None, "artifactRef": "sha256:" + "d" * 64, "url": None},
    "environment": {
        "name": "dev",
        "appIdentity": "plantpal",
        "deploymentId": "plantpal-dev-2026-09-27-01",
        "deployedRevision": REV_MERGED,
        "url": "http://planotell.platform.localhost",
    },
    "summary": "Smoke check: reminder card rendered on the deployed dev candidate",
}

# Missing exit code stays unknown; a worker's report is only a claim.
GOOD_EVIDENCE_WORKER_CLAIM_UNKNOWN = {
    **GOOD_EVIDENCE_CI_TASK,
    "stage": "tests",
    "basis": "worker-claim",
    "result": "unknown",
    "exitCode": None,
    "source": {"producer": "agent-runner", "recordRef": None, "runId": "run-77", "artifactRef": None, "url": None},
    "summary": "Agent report says tests pass; run record has no exit code",
}

GOOD_EVIDENCE_FROM_LEGACY = {
    **GOOD_EVIDENCE_CI_TASK,
    "stage": "implementation",
    "basis": "owner-attestation",
    "source": {"producer": "owner", "recordRef": None, "runId": None, "artifactRef": None, "url": None},
    "legacyReceipt": {"id": "6f8f2e2a-2c8b-4a8b-9b3d-2f7e5b6c1a10", "hash": SHA_B},
}

BAD_EVIDENCE_LIVE_NO_ENV = {**GOOD_EVIDENCE_LIVE, "environment": None}
BAD_EVIDENCE_LIVE_TASK_REVISION = {**GOOD_EVIDENCE_LIVE, "revisionRole": "task"}
BAD_EVIDENCE_MERGE_TASK_REVISION = {**GOOD_EVIDENCE_CI_TASK, "stage": "merge", "revisionRole": "task"}
BAD_EVIDENCE_SHORT_SHA = {**GOOD_EVIDENCE_CI_TASK, "revision": "1111111"}
BAD_EVIDENCE_ACCEPTANCE_STAGE = {**GOOD_EVIDENCE_CI_TASK, "stage": "acceptance"}  # acceptance is a decision
BAD_EVIDENCE_POLICY_BASIS = {**GOOD_EVIDENCE_CI_TASK, "basis": "policy-authorization"}
BAD_EVIDENCE_MACHINE_NO_RECORD = copy.deepcopy(GOOD_EVIDENCE_CI_TASK)
BAD_EVIDENCE_MACHINE_NO_RECORD["source"]["recordRef"] = None
BAD_EVIDENCE_PROD_ENV = copy.deepcopy(GOOD_EVIDENCE_LIVE)
BAD_EVIDENCE_PROD_ENV["environment"]["name"] = "production"
BAD_EVIDENCE_URL_AS_DEPLOYMENT = copy.deepcopy(GOOD_EVIDENCE_LIVE)
del BAD_EVIDENCE_URL_AS_DEPLOYMENT["environment"]["deploymentId"]
BAD_EVIDENCE_PRE_DEPLOY_WITH_ENV = {**GOOD_EVIDENCE_CI_TASK, "environment": GOOD_EVIDENCE_LIVE["environment"]}

DECISION_BASE = {
    "id": ACCEPTANCE_REF["decisionId"],
    "deliveryId": DELIVERY,
    "issue": ISSUE_REF,
    "actor": "owner",
    "policy": None,
    "scope": {"planHash": SHA_B, "issueScope": SHA_A},
    "decidedAt": NOW,
    "note": "Tested on dev; accepted.",
    "hash": SHA_C,
}

GOOD_DECISION_ACCEPT = {
    **DECISION_BASE,
    "kind": "owner-acceptance",
    "basis": "owner",
    "candidateRevision": REV_MERGED,
    "deploymentId": "plantpal-dev-2026-09-27-01",
    "evidence": [SHA_A],
}

GOOD_DECISION_PLAN = {**DECISION_BASE, "kind": "plan-approval", "basis": "owner", "candidateRevision": None, "deploymentId": None, "evidence": []}

GOOD_DECISION_POLICY = {
    **GOOD_DECISION_PLAN,
    "kind": "policy-authorization",
    "basis": "policy",
    "actor": "factory-policy",
    "policy": {"policyId": "routine-v1", "policyVersion": 1, "policyHash": SHA_A},
}

BAD_DECISION_POLICY_AS_ACCEPTANCE = {**GOOD_DECISION_ACCEPT, "basis": "policy", "policy": GOOD_DECISION_POLICY["policy"]}
BAD_DECISION_POLICY_AS_OWNER_CLICK = {**GOOD_DECISION_POLICY, "basis": "owner", "policy": None}
BAD_DECISION_POLICY_NO_REF = {**GOOD_DECISION_POLICY, "policy": None}
BAD_DECISION_ACCEPT_NO_CANDIDATE = {**GOOD_DECISION_ACCEPT, "candidateRevision": None}
BAD_DECISION_ACCEPT_NO_EVIDENCE = {**GOOD_DECISION_ACCEPT, "evidence": []}
BAD_DECISION_COORDINATOR = {**GOOD_DECISION_ACCEPT, "kind": "coordinator-approval"}
BAD_DECISION_READY_FOR_TEST = {**GOOD_DECISION_ACCEPT, "kind": "ready-for-testing"}

GOOD_PRODUCER_RUNNER_UNKNOWN = {
    "producer": "agent-runner",
    "operationId": "run-77",
    "correlation": {"deliveryId": DELIVERY, "operationKey": f"{DELIVERY}:dispatch:implement:1"},
    "repository": "plantpal",
    "branch": "factory/pla-12",
    "revision": None,
    "outcome": "unknown",
    "exitCode": None,
    "observedAt": NOW,
    "nativeRef": "agent-runner:runs/run-77",
    "artifactRef": None,
    "environment": None,
    "checks": [],
}

GOOD_PRODUCER_DEPLOY = {
    "producer": "app-deploy",
    "operationId": "plantpal-dev-2026-09-27-01",
    "correlation": {"deliveryId": DELIVERY, "operationKey": None},
    "repository": "plantpal",
    "branch": "dev",
    "revision": REV_MERGED,
    "outcome": "passed",
    "exitCode": None,
    "observedAt": NOW,
    "nativeRef": "plantpal:deployments/plantpal-dev-2026-09-27-01",
    "artifactRef": None,
    "environment": GOOD_EVIDENCE_LIVE["environment"],
    "checks": [{"name": "smoke:reminder-card", "criterionId": "reminder-card", "outcome": "passed", "exitCode": 0}],
}

GOOD_PRODUCER_CI_UNAVAILABLE = {
    **GOOD_PRODUCER_RUNNER_UNKNOWN,
    "producer": "ci-runner",
    "operationId": "9001/42",
    "outcome": "unavailable",
    "nativeRef": "ci-runner:ci.run/9001/42",
}

GOOD_PRODUCER_CI_PASSED = {
    "producer": "ci-runner",
    "operationId": "9001/42",
    "correlation": {"deliveryId": None, "operationKey": None},
    "repository": "plantpal",
    "branch": "factory/pla-12",
    "revision": REV_TASK,
    "outcome": "passed",
    "exitCode": None,
    "observedAt": NOW,
    "nativeRef": "ci-runner:ci.run/9001/42",
    "artifactRef": None,
    "environment": None,
    "checks": [{"name": "Run tests", "criterionId": None, "outcome": "passed", "exitCode": None}],
}

BAD_PRODUCER_EXIT_DEFAULTED = {**GOOD_PRODUCER_RUNNER_UNKNOWN, "exitCode": "0"}
BAD_PRODUCER_ACCEPTED = {**GOOD_PRODUCER_DEPLOY, "outcome": "accepted"}
BAD_PRODUCER_OTHER = {**GOOD_PRODUCER_DEPLOY, "producer": "demand-coordinator"}

GOOD_ERROR = {"code": "operation_key_conflict", "message": "same key, different body", "retryable": False}
BAD_ERROR_NO_RETRYABLE = {"code": "scope_changed", "message": "changed"}

CASES = [
    ("delivery.issue-ref.json", ISSUE_REF, True),
    ("delivery.issue.json", GOOD_ISSUE, True),
    ("delivery.issue.json", GOOD_ISSUE_UNKNOWN_DEPENDENCY, True),
    ("delivery.issue.json", BAD_ISSUE_DEPENDENCY_SATISFIED_BY_OMISSION, False),
    ("delivery.issue.json", BAD_ISSUE_CARRIES_TOKEN, False),
    ("delivery.issue.json", BAD_ISSUE_READABLE_AS_VENDOR_ID, False),
    ("delivery.issue-page.json", GOOD_PAGE_INTERMEDIATE, True),
    ("delivery.issue-page.json", GOOD_PAGE_LAST_PARTIAL, True),
    ("delivery.issue-page.json", BAD_PAGE_NO_COMPLETE_FLAG, False),
    ("delivery.workflow.json", GOOD_WORKFLOW, True),
    ("delivery.sync-request.json", GOOD_SYNC_RESOLVE, True),
    ("delivery.sync-request.json", GOOD_SYNC_COMMENT_NO_SCOPE, True),
    ("delivery.sync-request.json", GOOD_SYNC_LINK, True),
    ("delivery.sync-request.json", GOOD_SYNC_TRANSITION, True),
    ("delivery.sync-request.json", BAD_RESOLVE_WITH_POLICY, False),
    ("delivery.sync-request.json", BAD_RESOLVE_READY_FOR_TEST, False),
    ("delivery.sync-request.json", BAD_RESOLVE_WORKER_EXIT, False),
    ("delivery.sync-request.json", BAD_RESOLVE_COORDINATOR_APPROVAL, False),
    ("delivery.sync-request.json", BAD_RESOLVE_WITHOUT_ACCEPTANCE, False),
    ("delivery.sync-request.json", BAD_RESOLVE_WITHOUT_SCOPE, False),
    ("delivery.sync-request.json", BAD_TRANSITION_WITHOUT_SCOPE, False),
    ("delivery.sync-request.json", BAD_SYNC_SHORT_KEY, False),
    ("delivery.sync-request.json", BAD_SYNC_SHORT_SHA, False),
    ("delivery.sync-request.json", GOOD_SYNC_LINK_RESERVED, True),
    ("delivery.sync-request.json", BAD_SYNC_RESERVED_AT_NOT_A_STRING, False),
    ("delivery.sync-operation.json", GOOD_OP_CONFIRMED, True),
    ("delivery.sync-operation.json", GOOD_OP_UNCERTAIN, True),
    ("delivery.sync-operation.json", GOOD_OP_REJECTED_SCOPE, True),
    ("delivery.sync-operation.json", GOOD_OP_RESERVED, True),
    ("delivery.sync-operation.json", BAD_OP_CONFIRMED_WITHOUT_READBACK, False),
    ("delivery.sync-operation.json", BAD_OP_CONFIRMED_EFFECT_ABSENT, False),
    ("delivery.sync-operation.json", BAD_OP_EXACTLY_ONCE, False),
    ("delivery.sync-operation.json", GOOD_OP_ABSENT_IN_WINDOW, True),
    ("delivery.sync-operation.json", GOOD_OP_RESENT_AFTER_QUIET, True),
    ("delivery.sync-operation.json", BAD_OP_ABSENT_WITHOUT_WINDOW, False),
    ("delivery.sync-operation.json", BAD_OP_RESENT_WITHOUT_PROOF_NULL, False),
    ("delivery.sync-operation.json", BAD_OP_RESENT_WITHOUT_PROOF_MISSING, False),
    # Schema-valid on purpose: the quiet-window ordering is a cross-field timestamp
    # comparison, refused by check_recovery_semantics rather than by the schema.
    ("delivery.sync-operation.json", BAD_OP_RESENT_BEFORE_QUIET, True),
    ("delivery.sync-operation.json", BAD_OP_UNCERTAIN_PURGEABLE, False),
    ("delivery.sync-operation.json", BAD_OP_CONFIRMED_NO_RETENTION, False),
    ("delivery.sync-operation.json", BAD_OP_UNCERTAIN_RETRYABLE, False),
    ("delivery.sync-operation.json", BAD_OP_UNCERTAIN_NO_ERROR, False),
    ("delivery.sync-operation.json", BAD_OP_UNCERTAIN_UNAVAILABLE_ERROR, False),
    ("delivery.operation-coverage.json", GOOD_COVERAGE, True),
    ("delivery.operation-coverage.json", BAD_COVERAGE_SHORT_RETENTION, False),
    ("delivery.operation-coverage.json", BAD_COVERAGE_ZERO_BOUND, False),
    ("delivery.operation-coverage.json", BAD_COVERAGE_NO_FLOOR, False),
    ("delivery.error.json", ERR_OPERATION_NOT_FOUND, True),
    ("delivery.error.json", ERR_LOOKUP_OUT_OF_COVERAGE, True),
    ("delivery.error.json", ERR_LOOKUP_NO_PROVENANCE, True),
    ("delivery.error.json", BAD_ERR_NOT_FOUND_NO_PROVENANCE, False),
    ("delivery.error.json", BAD_ERR_NOT_FOUND_NOT_RETRYABLE, False),
    ("delivery.error.json", BAD_ERR_OUT_OF_COVERAGE_RETRYABLE, False),
    ("delivery.error.json", BAD_ERR_OUT_OF_COVERAGE_NO_REASON, False),
    ("delivery.error.json", BAD_ERR_OUT_OF_COVERAGE_BAD_REASON, False),
    ("delivery.evidence.json", GOOD_EVIDENCE_CI_TASK, True),
    ("delivery.evidence.json", GOOD_EVIDENCE_LIVE, True),
    ("delivery.evidence.json", GOOD_EVIDENCE_WORKER_CLAIM_UNKNOWN, True),
    ("delivery.evidence.json", GOOD_EVIDENCE_FROM_LEGACY, True),
    ("delivery.evidence.json", BAD_EVIDENCE_LIVE_NO_ENV, False),
    ("delivery.evidence.json", BAD_EVIDENCE_LIVE_TASK_REVISION, False),
    ("delivery.evidence.json", BAD_EVIDENCE_MERGE_TASK_REVISION, False),
    ("delivery.evidence.json", BAD_EVIDENCE_SHORT_SHA, False),
    ("delivery.evidence.json", BAD_EVIDENCE_ACCEPTANCE_STAGE, False),
    ("delivery.evidence.json", BAD_EVIDENCE_POLICY_BASIS, False),
    ("delivery.evidence.json", BAD_EVIDENCE_MACHINE_NO_RECORD, False),
    ("delivery.evidence.json", BAD_EVIDENCE_PROD_ENV, False),
    ("delivery.evidence.json", BAD_EVIDENCE_URL_AS_DEPLOYMENT, False),
    ("delivery.evidence.json", BAD_EVIDENCE_PRE_DEPLOY_WITH_ENV, False),
    ("delivery.decision.json", GOOD_DECISION_ACCEPT, True),
    ("delivery.decision.json", GOOD_DECISION_PLAN, True),
    ("delivery.decision.json", GOOD_DECISION_POLICY, True),
    ("delivery.decision.json", BAD_DECISION_POLICY_AS_ACCEPTANCE, False),
    ("delivery.decision.json", BAD_DECISION_POLICY_AS_OWNER_CLICK, False),
    ("delivery.decision.json", BAD_DECISION_POLICY_NO_REF, False),
    ("delivery.decision.json", BAD_DECISION_ACCEPT_NO_CANDIDATE, False),
    ("delivery.decision.json", BAD_DECISION_ACCEPT_NO_EVIDENCE, False),
    ("delivery.decision.json", BAD_DECISION_COORDINATOR, False),
    ("delivery.decision.json", BAD_DECISION_READY_FOR_TEST, False),
    ("delivery.producer-result.json", GOOD_PRODUCER_RUNNER_UNKNOWN, True),
    ("delivery.producer-result.json", GOOD_PRODUCER_DEPLOY, True),
    ("delivery.producer-result.json", GOOD_PRODUCER_CI_UNAVAILABLE, True),
    ("delivery.producer-result.json", GOOD_PRODUCER_CI_PASSED, True),
    ("delivery.producer-result.json", BAD_PRODUCER_EXIT_DEFAULTED, False),
    ("delivery.producer-result.json", BAD_PRODUCER_ACCEPTED, False),
    ("delivery.producer-result.json", BAD_PRODUCER_OTHER, False),
    ("delivery.error.json", GOOD_ERROR, True),
    ("delivery.error.json", BAD_ERROR_NO_RETRYABLE, False),
]


def registry() -> Registry:
    reg = Registry()
    for path in SCHEMAS.glob("*.json"):
        resource = Resource.from_contents(json.loads(path.read_text(encoding="utf-8")))
        # Resolve both the $id and the bare relative filename used in cross-file $refs.
        reg = reg.with_resource(resource.contents["$id"], resource)
        reg = reg.with_resource(path.name, resource)
        reg = reg.with_resource("https://platform/contracts/delivery/" + path.name, resource)
    return reg


def schema_for(name: str) -> dict:
    return json.loads((SCHEMAS / name).read_text(encoding="utf-8"))


def check_bindings() -> list[str]:
    """Round-trip the positive fixtures through the generated Python models."""
    sys.path.insert(0, str(ROOT / "gen" / "python"))
    from platform_contracts.delivery import (
        delivery_decision,
        delivery_evidence,
        delivery_issue,
        delivery_issue_page,
        delivery_operation_coverage,
        delivery_producer_result,
        delivery_sync_operation,
        delivery_sync_request,
        delivery_workflow,
    )

    models = {
        "delivery.issue.json": delivery_issue.DeliveryIssue,
        "delivery.issue-page.json": delivery_issue_page.DeliveryIssuePage,
        "delivery.workflow.json": delivery_workflow.DeliveryWorkflow,
        "delivery.sync-request.json": delivery_sync_request.DeliverySyncRequest,
        "delivery.sync-operation.json": delivery_sync_operation.DeliverySyncOperation,
        "delivery.operation-coverage.json": delivery_operation_coverage.DeliveryOperationCoverage,
        "delivery.evidence.json": delivery_evidence.DeliveryEvidence,
        "delivery.decision.json": delivery_decision.DeliveryDecision,
        "delivery.producer-result.json": delivery_producer_result.DeliveryProducerResult,
    }
    failures = []
    for name, doc, ok in CASES:
        model = models.get(name)
        if model is None or not ok:
            continue
        try:
            obj = model.model_validate(doc)
            again = model.model_validate_json(obj.model_dump_json(by_alias=True))
            assert again == obj
        except Exception as exc:  # noqa: BLE001
            failures.append(f"binding {name}: {exc}")
    return failures


def check_recovery_semantics() -> list[str]:
    """The two recovery rules JSON Schema cannot express, as executable checks.

    Both are comparisons over timestamps, which draft 2020-12 has no vocabulary for.
    They are the rules that stop a caller repeating a possibly-completed write, so
    leaving them as prose in a doc would mean nothing fails when they erode. The two
    scenarios the demand names — a Factory restart after terminal retention expiry,
    and a delayed vendor write — are each exercised below.
    """
    failures = []

    def parse(ts: str) -> datetime:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))

    def lookup_answer(reserved_at, covered_since) -> str:
        """The only legal answer to a by-key miss (`docs/task-delivery.md` §Retention coverage)."""
        if reserved_at is None or parse(reserved_at) < parse(covered_since):
            return "operation_lookup_out_of_coverage"
        return "operation_not_found"

    def resend_authorized(doc) -> bool:
        """A resend is justified only by recorded proof of non-execution."""
        read_back = doc.get("readBack") or {}
        if doc.get("attempts", 0) < 2 or read_back.get("effectPresent") is not False:
            return False
        proven, quiet = doc.get("absenceProvenAt"), read_back.get("absenceQuietUntil")
        if not proven or not quiet:
            return False
        # Proof of absence must have reached the quiet deadline. Proving it earlier is
        # proving it while a delayed original request could still take effect.
        return parse(proven) >= parse(quiet)

    floor = COVERAGE_BASE["coveredSince"]

    # Scenario 1 — Factory restarts after the record's terminal retention expired.
    # The purged record is simply gone, so the classification below is the ONLY thing
    # between the restart and a duplicate write under a completed key.
    if lookup_answer(KEY_RESERVED_FRESH, floor) != "operation_not_found":
        failures.append("lookup: a key inside coverage must answer operation_not_found")
    if lookup_answer(KEY_RESERVED_EXPIRED, floor) != "operation_lookup_out_of_coverage":
        failures.append("lookup: a key older than the coverage floor must answer operation_lookup_out_of_coverage")
    if lookup_answer(None, floor) != "operation_lookup_out_of_coverage":
        failures.append("lookup: a miss with no reservedAt must answer operation_lookup_out_of_coverage")
    if lookup_answer(ERR_OPERATION_NOT_FOUND["details"]["reservedAt"], floor) != "operation_not_found":
        failures.append("lookup: ERR_OPERATION_NOT_FOUND's own provenance must be inside coverage")
    if lookup_answer(ERR_LOOKUP_OUT_OF_COVERAGE["details"]["reservedAt"], floor) != "operation_lookup_out_of_coverage":
        failures.append("lookup: ERR_LOOKUP_OUT_OF_COVERAGE's own provenance must be outside coverage")

    # Only a conclusive miss may be retryable, and every miss must echo the floor it
    # was judged against so the caller can audit (or contest) the classification.
    for name, doc in [
        ("ERR_OPERATION_NOT_FOUND", ERR_OPERATION_NOT_FOUND),
        ("ERR_LOOKUP_OUT_OF_COVERAGE", ERR_LOOKUP_OUT_OF_COVERAGE),
        ("ERR_LOOKUP_NO_PROVENANCE", ERR_LOOKUP_NO_PROVENANCE),
    ]:
        if doc["retryable"] is not (doc["code"] == "operation_not_found"):
            failures.append(f"lookup: {name} has the wrong `retryable` for its code")
        if "coveredSince" not in doc.get("details", {}):
            failures.append(f"lookup: {name} must echo details.coveredSince")

    # Scenario 2 — a delayed vendor write. Absence seen once, inside the quiet window,
    # is not non-execution, so it must not authorise anything.
    if resend_authorized(GOOD_OP_ABSENT_IN_WINDOW):
        failures.append("recovery: absence inside the quiet window must not authorise a resend")
    if not resend_authorized(GOOD_OP_RESENT_AFTER_QUIET):
        failures.append("recovery: absence proven at the quiet deadline must authorise the one resend")
    if resend_authorized(BAD_OP_RESENT_BEFORE_QUIET):
        failures.append("recovery: a resend authorised before the quiet window closed must be refused")
    if resend_authorized(BAD_OP_RESENT_WITHOUT_PROOF_MISSING):
        failures.append("recovery: a resend with no recorded proof must be refused")
    if resend_authorized({**GOOD_OP_RESENT_AFTER_QUIET, "readBack": {**GOOD_OP_ABSENT_IN_WINDOW["readBack"], "effectPresent": True}}):
        failures.append("recovery: a resend after a read-back that saw the effect must be refused")
    return failures


def _rewrite_refs(node):
    """Point the OpenAPI document's `../delivery/<file>` refs at the registry's bare filenames."""
    if isinstance(node, dict):
        return {k: (v.removeprefix("../delivery/") if k == "$ref" and isinstance(v, str) else _rewrite_refs(v)) for k, v in node.items()}
    if isinstance(node, list):
        return [_rewrite_refs(v) for v in node]
    return node


def check_ci_api(reg: Registry) -> list[str]:
    api = yaml.safe_load(CI_API.read_text(encoding="utf-8"))
    failures = []
    for route, op in [
        ("/delivery/v1/ci-results/{runId}/{jobId}", "getCiJobResult"),
        ("/delivery/v1/ci-results", "listCiJobResultsByRevision"),
    ]:
        if api["paths"].get(route, {}).get("get", {}).get("operationId") != op:
            failures.append(f"ci openapi: missing GET {route} ({op})")
    if "404" not in api["paths"]["/delivery/v1/ci-results/{runId}/{jobId}"]["get"]["responses"]:
        failures.append("ci openapi: by-id lookup has no 404 response")

    comps = api["components"]["schemas"]
    listing = {
        "repository": "plantpal",
        "revision": REV_TASK,
        "items": [GOOD_PRODUCER_CI_PASSED, {**GOOD_PRODUCER_CI_PASSED, "operationId": "9002/43", "nativeRef": "ci-runner:ci.run/9002/43", "outcome": "pending"}],
    }
    not_found = {"code": "ci_result_not_found", "message": "no record of job 9001/42", "retryable": False}
    cases = [
        ("CiResultList", listing, True),
        ("CiResultList", {**listing, "items": []}, True),
        ("CiResultList", {**listing, "revision": "abc1234"}, False),
        ("CiResultList", {**listing, "items": [{**GOOD_PRODUCER_CI_PASSED, "revision": "2" * 39}]}, False),
        ("CiResultNotFoundError", not_found, True),
        ("CiResultNotFoundError", {**not_found, "code": "issue_not_found"}, False),
        ("CiResultNotFoundError", {**not_found, "retryable": True}, False),
    ]
    for name, doc, ok in cases:
        schema = {"$schema": "https://json-schema.org/draft/2020-12/schema", **_rewrite_refs(comps[name])}
        errors = list(Draft202012Validator(schema, registry=reg, format_checker=FormatChecker()).iter_errors(doc))
        if ok and errors:
            failures.append(f"ci openapi {name}: expected valid, got {errors[0].message}")
        if not ok and not errors:
            failures.append(f"ci openapi {name}: expected INVALID fixture to be rejected")
    return failures


def main() -> int:
    reg = registry()
    failures = []
    for name, doc, expect_valid in CASES:
        validator = Draft202012Validator(schema_for(name), registry=reg, format_checker=FormatChecker())
        errors = list(validator.iter_errors(doc))
        if expect_valid and errors:
            failures.append(f"{name}: expected valid, got {errors[0].message}")
        if not expect_valid and not errors:
            failures.append(f"{name}: expected INVALID fixture to be rejected")

    api = yaml.safe_load(API.read_text(encoding="utf-8"))
    for route in [
        "/delivery/v1/projects/{project}/workflow",
        "/delivery/v1/issues",
        "/delivery/v1/issues/{vendorId}",
        "/delivery/v1/operations/coverage",
        "/delivery/v1/operations/{operationKey}",
        "/delivery/v1/operations/{operationKey}/reconcile",
        "/delivery/v1/operations",
    ]:
        if route not in api["paths"]:
            failures.append(f"openapi: missing route {route}")

    # The coverage route must not be shadowed by the templated operation-key path.
    if api["paths"]["/delivery/v1/operations/coverage"]["get"]["operationId"] != "getDeliveryOperationCoverage":
        failures.append("openapi: coverage route lost its getDeliveryOperationCoverage operationId")
    if api["paths"]["/delivery/v1/operations/{operationKey}"]["get"]["operationId"] != "getDeliveryOperation":
        failures.append("openapi: operation lookup route lost its getDeliveryOperation operationId")
    reserved_at = api["paths"]["/delivery/v1/operations/{operationKey}"]["get"].get("parameters", [])
    if not any(p.get("name") == "reservedAt" for p in reserved_at):
        failures.append("openapi: operation lookup has no reservedAt provenance parameter")
    if "operation_lookup_out_of_coverage" not in API.read_text(encoding="utf-8"):
        failures.append("openapi: the inconclusive-miss code is not documented on the surface")

    failures += check_ci_api(reg)
    failures += check_bindings()
    failures += check_recovery_semantics()

    for f in failures:
        print("FAIL ", f)
    print(f"{len(CASES)} schema cases, {len(failures)} failures")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
