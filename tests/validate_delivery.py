"""
Schema-level validation for schemas/delivery/*.json (D113 task delivery, v0.31.0)
plus a parse check of schemas/delivery-api/youtrack-delivery.openapi.yaml and a
round-trip through the generated Python binding.

Extended (v0.34.0) with schemas/delivery-api/ci-runner-results.openapi.yaml: route
presence plus validation of its component schemas (result list, not-found body).

Extended (v0.37.0) with schemas/delivery-api/app-deploy-lookup.openapi.yaml: route
presence, the verbatim-receipt and mapped-result payloads, and the miss body that must
be distinguishable from "could not ask" (check_app_deploy_api).

Extended (v0.38.0) with the review environment: `environment.name: review` + `revisionRole:
task` on the receipt and evidence, and schemas/launcher/review-environment.openapi.yaml
(check_review_api, check_review_evidence_semantics).

Extended (v0.36.0) with delivery.deployment-receipt + app/deployment-identity, the
cross-field deployment rules (check_deployment_semantics) and an executable
reference of the receipt -> producer-result mapping (receipt_to_producer_result).

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
DEPLOY_API = ROOT / "schemas" / "delivery-api" / "app-deploy-lookup.openapi.yaml"
REVIEW_API = ROOT / "schemas" / "launcher" / "review-environment.openapi.yaml"
APP_SCHEMAS = ROOT / "schemas" / "app"
IDENTITY = "../app/deployment-identity.json"  # resolved relative to SCHEMAS

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

# --- v0.36.0: app-deploy receipt + running-app identity -----------------------------

DEPLOY_ID = "pla-dev-20260927120000-222222222222"
DEPLOY_PREV = "pla-dev-20260926090000-111111111111"
DIGEST_BE = "sha256:" + "e" * 64
DIGEST_FE = "sha256:" + "f" * 64

GOOD_IDENTITY = {"appIdentity": "plantpal", "revision": REV_MERGED, "deploymentId": DEPLOY_ID, "environment": "dev"}
# A developer's local run: nothing reported but the name. Valid, and verifies nothing.
GOOD_IDENTITY_UNREPORTED = {"appIdentity": "plantpal", "revision": None, "deploymentId": None, "environment": None}
BAD_IDENTITY_SHORT_SHA = {**GOOD_IDENTITY, "revision": "2222222"}
BAD_IDENTITY_NO_APP = {**GOOD_IDENTITY, "appIdentity": None}
BAD_IDENTITY_OMITS_REVISION = {k: v for k, v in GOOD_IDENTITY.items() if k != "revision"}  # absent != null
BAD_IDENTITY_EXTRA = {**GOOD_IDENTITY, "buildTime": NOW}

GOOD_RECEIPT_PASSED = {
    "deploymentId": DEPLOY_ID,
    "kind": "deploy",
    "repository": "plantpal",
    "branch": "dev",
    "mergedRevision": REV_MERGED,
    "imageDigests": {"backend": DIGEST_BE, "frontend": DIGEST_FE},
    "digestKind": "local-image-id",
    "result": "passed",
    "exitCode": 0,
    "startedAt": "2026-09-27T12:00:00Z",
    "finishedAt": "2026-09-27T12:04:00Z",
    "observedAt": "2026-09-27T12:03:30Z",
    "environment": {"name": "dev", "url": "http://planotell.platform.localhost"},
    "observed": GOOD_IDENTITY,
    "checks": [
        {"name": "ci:Backend CI", "criterionId": None, "outcome": "passed", "exitCode": None},
        {"name": "identity:revision", "criterionId": None, "outcome": "passed", "exitCode": None},
        {"name": "smoke:backend-health", "criterionId": None, "outcome": "passed", "exitCode": None},
        {"name": "criterion:AC-1", "criterionId": "AC-1", "outcome": "passed", "exitCode": None},
    ],
    "correlation": {"deliveryId": DELIVERY, "operationKey": f"{DELIVERY}:deploy:1"},
    "rollback": {"deploymentId": DEPLOY_PREV, "revision": REV_TASK, "imageDigests": {"backend": "sha256:" + "0" * 64, "frontend": "sha256:" + "9" * 64}},
    "rollbackOf": None,
    "restores": None,
    "nativeRef": f"plantpal:deployments/{DEPLOY_ID}",
}

# Reserved, not yet settled: first deployment ever, so no rollback identity exists.
GOOD_RECEIPT_PENDING_FIRST = {
    **GOOD_RECEIPT_PASSED,
    "imageDigests": {"backend": None, "frontend": None},
    "result": "pending",
    "exitCode": None,
    "finishedAt": None,
    "observedAt": None,
    "environment": {"name": "dev", "url": "http://127.0.0.1:8184"},
    "observed": None,
    "checks": [],
    "correlation": {"deliveryId": None, "operationKey": None},
    "rollback": None,
}

# The app answered but did not report its revision: settled as unknown, never passed.
GOOD_RECEIPT_UNKNOWN_UNREPORTED = {
    **GOOD_RECEIPT_PASSED,
    "result": "unknown",
    "environment": {"name": "dev", "url": "http://127.0.0.1:8184"},
    "observed": {**GOOD_IDENTITY, "revision": None},
    "checks": [{"name": "identity:revision", "criterionId": None, "outcome": "unknown", "exitCode": None}],
}

# Timed-out deploy: exit status not reported, endpoint never answered.
GOOD_RECEIPT_TIMEOUT = {**GOOD_RECEIPT_UNKNOWN_UNREPORTED, "exitCode": None, "observed": None}

GOOD_RECEIPT_ROLLBACK = {
    **GOOD_RECEIPT_PASSED,
    "deploymentId": "pla-dev-20260927130000-111111111111",
    "kind": "rollback",
    "mergedRevision": REV_TASK,
    "imageDigests": GOOD_RECEIPT_PASSED["rollback"]["imageDigests"],
    "observed": {**GOOD_IDENTITY, "revision": REV_TASK, "deploymentId": "pla-dev-20260927130000-111111111111"},
    "rollback": {"deploymentId": DEPLOY_ID, "revision": REV_MERGED, "imageDigests": GOOD_RECEIPT_PASSED["imageDigests"]},
    "rollbackOf": DEPLOY_ID,
    "restores": DEPLOY_PREV,
    "nativeRef": "plantpal:deployments/pla-dev-20260927130000-111111111111",
}

BAD_RECEIPT_PROD = {**GOOD_RECEIPT_PASSED, "environment": {"name": "prod", "url": "https://planotell.example"}}
BAD_RECEIPT_NULL_REVISION = {**GOOD_RECEIPT_PASSED, "mergedRevision": None}
BAD_RECEIPT_SHORT_REVISION = {**GOOD_RECEIPT_PASSED, "mergedRevision": "2222222"}
BAD_RECEIPT_ACCEPTED = {**GOOD_RECEIPT_PASSED, "result": "accepted"}
BAD_RECEIPT_PASSED_EXIT_UNREPORTED = {**GOOD_RECEIPT_PASSED, "exitCode": None}
BAD_RECEIPT_PASSED_NOT_OBSERVED = {**GOOD_RECEIPT_PASSED, "observed": None}
BAD_RECEIPT_PASSED_DIGEST_MISSING = {**GOOD_RECEIPT_PASSED, "imageDigests": {"backend": DIGEST_BE, "frontend": None}}
BAD_RECEIPT_SETTLED_UNTIMED = {**GOOD_RECEIPT_UNKNOWN_UNREPORTED, "observedAt": None}
BAD_RECEIPT_NO_COMPONENTS = {**GOOD_RECEIPT_PASSED, "imageDigests": {}}
BAD_RECEIPT_TAG_AS_DIGEST = {**GOOD_RECEIPT_PASSED, "imageDigests": {"backend": "plantpal-backend:latest", "frontend": DIGEST_FE}}
BAD_RECEIPT_ROLLBACK_WITHOUT_REVISION = {**GOOD_RECEIPT_PASSED, "rollback": {**GOOD_RECEIPT_PASSED["rollback"], "revision": None}}
BAD_RECEIPT_ROLLBACK_KIND_UNLINKED = {**GOOD_RECEIPT_ROLLBACK, "restores": None}
BAD_RECEIPT_DEPLOY_WITH_RESTORES = {**GOOD_RECEIPT_PASSED, "restores": DEPLOY_PREV}
BAD_RECEIPT_NATIVE_FIELDS = {**GOOD_RECEIPT_PASSED, "schema": "plantpal.dev-deployment-receipt/1"}  # closed shape
BAD_RECEIPT_NATIVEREF_OTHER = {**GOOD_RECEIPT_PASSED, "nativeRef": f"agent-runner:runs/{DEPLOY_ID}"}


# --- review environment (v0.38.0): an UNMERGED PR head served for review -------------------
REV_PR = "3" * 40
REVIEW_ID = "pla-review-20260930120000-333333333333"
REVIEW_URL = "http://pr-42.plantpal.review.localhost"
GOOD_IDENTITY_REVIEW = {"appIdentity": "plantpal", "revision": REV_PR, "deploymentId": REVIEW_ID, "environment": "review"}

GOOD_RECEIPT_REVIEW = {
    **GOOD_RECEIPT_PASSED,
    "deploymentId": REVIEW_ID,
    "branch": "factory/pla-42",
    "mergedRevision": REV_PR,
    "revisionRole": "task",
    "review": {"pullRequest": 42, "pullRequestUrl": "https://github.com/elmoul/plantpal/pull/42"},
    "environment": {"name": "review", "url": REVIEW_URL, "apiDocsUrl": REVIEW_URL + "/swagger-ui/index.html"},
    "observed": GOOD_IDENTITY_REVIEW,
    "rollback": None,
    "nativeRef": f"plantpal:deployments/{REVIEW_ID}",
}
# A revision mismatch: the URL serves the merged revision, not the PR head. Recorded as
# reported, settled `failed`; never corrected and never passed.
GOOD_RECEIPT_REVIEW_MISMATCH = {
    **GOOD_RECEIPT_REVIEW,
    "result": "failed",
    "observed": {**GOOD_IDENTITY_REVIEW, "revision": REV_MERGED},
    "checks": [{"name": "identity:revision", "criterionId": None, "outcome": "failed", "exitCode": None}],
}
# The app did not report its identity: stays null, settles unknown, never passed.
GOOD_RECEIPT_REVIEW_UNREPORTED = {
    **GOOD_RECEIPT_REVIEW,
    "result": "unknown",
    "observed": {**GOOD_IDENTITY_REVIEW, "revision": None, "deploymentId": None, "environment": None},
    "checks": [{"name": "identity:revision", "criterionId": None, "outcome": "unknown", "exitCode": None}],
}
GOOD_RECEIPT_REVIEW_NO_DOCS = {**GOOD_RECEIPT_REVIEW, "environment": {"name": "review", "url": REVIEW_URL, "apiDocsUrl": None}}
GOOD_RECEIPT_REVIEW_BRANCH_ONLY = {**GOOD_RECEIPT_REVIEW, "review": {"pullRequest": None, "pullRequestUrl": None}}
GOOD_RECEIPT_DEV_EXPLICIT_MERGED = {**GOOD_RECEIPT_PASSED, "revisionRole": "merged"}

BAD_RECEIPT_REVIEW_MERGED_ROLE = {**GOOD_RECEIPT_REVIEW, "revisionRole": "merged"}
BAD_RECEIPT_REVIEW_NO_ROLE = {k: v for k, v in GOOD_RECEIPT_REVIEW.items() if k != "revisionRole"}
BAD_RECEIPT_REVIEW_NO_REFERENCE = {k: v for k, v in GOOD_RECEIPT_REVIEW.items() if k != "review"}
BAD_RECEIPT_REVIEW_ROLLBACK = {**GOOD_RECEIPT_REVIEW, "kind": "rollback", "rollbackOf": DEPLOY_ID, "restores": DEPLOY_PREV}
BAD_RECEIPT_REVIEW_WITH_ROLLBACK_IDENTITY = {**GOOD_RECEIPT_REVIEW, "rollback": GOOD_RECEIPT_PASSED["rollback"]}
BAD_RECEIPT_REVIEW_PASSED_NOT_OBSERVED = {**GOOD_RECEIPT_REVIEW, "observed": None}
BAD_RECEIPT_DEV_WITH_REVIEW_BLOCK = {**GOOD_RECEIPT_PASSED, "review": GOOD_RECEIPT_REVIEW["review"]}
BAD_RECEIPT_DEV_TASK_ROLE = {**GOOD_RECEIPT_PASSED, "revisionRole": "task"}
BAD_RECEIPT_DEV_API_DOCS = {**GOOD_RECEIPT_PASSED, "environment": {"name": "dev", "url": "http://127.0.0.1:8184", "apiDocsUrl": "http://127.0.0.1:8184/docs"}}
BAD_RECEIPT_REVIEW_PR_ZERO = {**GOOD_RECEIPT_REVIEW, "review": {"pullRequest": 0, "pullRequestUrl": None}}

GOOD_EVIDENCE_REVIEW = {
    **GOOD_EVIDENCE_LIVE,
    "stage": "deployment",
    "criteria": [],
    "branch": "factory/pla-42",
    "revision": REV_PR,
    "revisionRole": "task",
    "source": {"producer": "app-deploy", "recordRef": f"plantpal:deployments/{REVIEW_ID}", "runId": None, "artifactRef": DIGEST_BE, "url": None},
    "environment": {"name": "review", "appIdentity": "plantpal", "deploymentId": REVIEW_ID, "deployedRevision": REV_PR, "url": REVIEW_URL},
    "summary": "The review URL serves PR head 3333333 (identity endpoint agreed)",
}
GOOD_EVIDENCE_REVIEW_LIVE = {**GOOD_EVIDENCE_REVIEW, "stage": "live", "criteria": [{"criterionId": "reminder-card", "evaluableAt": "live"}]}
# The URL serves a different revision than the PR head: recorded as `failed`.
GOOD_EVIDENCE_REVIEW_MISMATCH = {
    **GOOD_EVIDENCE_REVIEW,
    "result": "failed",
    "environment": {**GOOD_EVIDENCE_REVIEW["environment"], "deployedRevision": REV_MERGED},
    "summary": "The review URL serves 2222222, not PR head 3333333 (mismatch)",
}
BAD_EVIDENCE_REVIEW_MERGED_ROLE = {**GOOD_EVIDENCE_REVIEW, "revisionRole": "merged"}
BAD_EVIDENCE_DEV_TASK_ROLE = {**GOOD_EVIDENCE_LIVE, "stage": "deployment", "revisionRole": "task"}
BAD_EVIDENCE_REVIEW_NO_ENV = {**GOOD_EVIDENCE_REVIEW, "environment": None}
BAD_EVIDENCE_REVIEW_UNKNOWN_ENV = {**GOOD_EVIDENCE_REVIEW, "environment": {**GOOD_EVIDENCE_REVIEW["environment"], "name": "staging"}}
BAD_EVIDENCE_CI_WITH_REVIEW_ENV = {**GOOD_EVIDENCE_CI_TASK, "environment": GOOD_EVIDENCE_REVIEW["environment"]}


def receipt_to_producer_result(receipt: dict, primary_component: str = "backend") -> dict:
    """The app-deploy mapping in `docs/task-delivery.md` §App-deploy, as executable reference.

    `environment` is built ONLY from what the running app reported (`observed`), never
    from the receipt's own `deploymentId`/`mergedRevision`: a producer that fills it
    from its intentions would report a deployment verified that nobody observed.
    """
    observed = receipt["observed"]
    environment = None
    if observed is not None and observed["revision"] is not None and observed["deploymentId"] is not None:
        environment = {
            "name": receipt["environment"]["name"],
            "appIdentity": observed["appIdentity"],
            "deploymentId": observed["deploymentId"],
            "deployedRevision": observed["revision"],
            "url": receipt["environment"]["url"],
        }
    return {
        "producer": "app-deploy",
        "operationId": receipt["deploymentId"],
        "correlation": receipt["correlation"],
        "repository": receipt["repository"],
        "branch": receipt["branch"],
        "revision": receipt["mergedRevision"],
        "outcome": receipt["result"],
        "exitCode": receipt["exitCode"],
        "observedAt": receipt["observedAt"] or receipt["startedAt"],
        "nativeRef": receipt["nativeRef"],
        "artifactRef": receipt["imageDigests"].get(primary_component),
        "environment": environment,
        "checks": receipt["checks"],
    }


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
    (IDENTITY, GOOD_IDENTITY, True),
    (IDENTITY, GOOD_IDENTITY_UNREPORTED, True),
    (IDENTITY, BAD_IDENTITY_SHORT_SHA, False),
    (IDENTITY, BAD_IDENTITY_NO_APP, False),
    (IDENTITY, BAD_IDENTITY_OMITS_REVISION, False),
    (IDENTITY, BAD_IDENTITY_EXTRA, False),
    ("delivery.deployment-receipt.json", GOOD_RECEIPT_PASSED, True),
    ("delivery.deployment-receipt.json", GOOD_RECEIPT_PENDING_FIRST, True),
    ("delivery.deployment-receipt.json", GOOD_RECEIPT_UNKNOWN_UNREPORTED, True),
    ("delivery.deployment-receipt.json", GOOD_RECEIPT_TIMEOUT, True),
    ("delivery.deployment-receipt.json", GOOD_RECEIPT_ROLLBACK, True),
    ("delivery.deployment-receipt.json", BAD_RECEIPT_PROD, False),
    ("delivery.deployment-receipt.json", BAD_RECEIPT_NULL_REVISION, False),
    ("delivery.deployment-receipt.json", BAD_RECEIPT_SHORT_REVISION, False),
    ("delivery.deployment-receipt.json", BAD_RECEIPT_ACCEPTED, False),
    ("delivery.deployment-receipt.json", BAD_RECEIPT_PASSED_EXIT_UNREPORTED, False),
    ("delivery.deployment-receipt.json", BAD_RECEIPT_PASSED_NOT_OBSERVED, False),
    ("delivery.deployment-receipt.json", BAD_RECEIPT_PASSED_DIGEST_MISSING, False),
    ("delivery.deployment-receipt.json", BAD_RECEIPT_SETTLED_UNTIMED, False),
    ("delivery.deployment-receipt.json", BAD_RECEIPT_NO_COMPONENTS, False),
    ("delivery.deployment-receipt.json", BAD_RECEIPT_TAG_AS_DIGEST, False),
    ("delivery.deployment-receipt.json", BAD_RECEIPT_ROLLBACK_WITHOUT_REVISION, False),
    ("delivery.deployment-receipt.json", BAD_RECEIPT_ROLLBACK_KIND_UNLINKED, False),
    ("delivery.deployment-receipt.json", BAD_RECEIPT_DEPLOY_WITH_RESTORES, False),
    ("delivery.deployment-receipt.json", BAD_RECEIPT_NATIVE_FIELDS, False),
    ("delivery.deployment-receipt.json", BAD_RECEIPT_NATIVEREF_OTHER, False),
    ("delivery.deployment-receipt.json", GOOD_RECEIPT_REVIEW, True),
    ("delivery.deployment-receipt.json", GOOD_RECEIPT_REVIEW_MISMATCH, True),
    ("delivery.deployment-receipt.json", GOOD_RECEIPT_REVIEW_UNREPORTED, True),
    ("delivery.deployment-receipt.json", GOOD_RECEIPT_REVIEW_NO_DOCS, True),
    ("delivery.deployment-receipt.json", GOOD_RECEIPT_REVIEW_BRANCH_ONLY, True),
    ("delivery.deployment-receipt.json", GOOD_RECEIPT_DEV_EXPLICIT_MERGED, True),
    ("delivery.deployment-receipt.json", BAD_RECEIPT_REVIEW_MERGED_ROLE, False),
    ("delivery.deployment-receipt.json", BAD_RECEIPT_REVIEW_NO_ROLE, False),
    ("delivery.deployment-receipt.json", BAD_RECEIPT_REVIEW_NO_REFERENCE, False),
    ("delivery.deployment-receipt.json", BAD_RECEIPT_REVIEW_ROLLBACK, False),
    ("delivery.deployment-receipt.json", BAD_RECEIPT_REVIEW_WITH_ROLLBACK_IDENTITY, False),
    ("delivery.deployment-receipt.json", BAD_RECEIPT_REVIEW_PASSED_NOT_OBSERVED, False),
    ("delivery.deployment-receipt.json", BAD_RECEIPT_DEV_WITH_REVIEW_BLOCK, False),
    ("delivery.deployment-receipt.json", BAD_RECEIPT_DEV_TASK_ROLE, False),
    ("delivery.deployment-receipt.json", BAD_RECEIPT_DEV_API_DOCS, False),
    ("delivery.deployment-receipt.json", BAD_RECEIPT_REVIEW_PR_ZERO, False),
    ("delivery.evidence.json", GOOD_EVIDENCE_REVIEW, True),
    ("delivery.evidence.json", GOOD_EVIDENCE_REVIEW_LIVE, True),
    ("delivery.evidence.json", GOOD_EVIDENCE_REVIEW_MISMATCH, True),
    ("delivery.evidence.json", BAD_EVIDENCE_REVIEW_MERGED_ROLE, False),
    ("delivery.evidence.json", BAD_EVIDENCE_DEV_TASK_ROLE, False),
    ("delivery.evidence.json", BAD_EVIDENCE_REVIEW_NO_ENV, False),
    ("delivery.evidence.json", BAD_EVIDENCE_REVIEW_UNKNOWN_ENV, False),
    ("delivery.evidence.json", BAD_EVIDENCE_CI_WITH_REVIEW_ENV, False),
    (IDENTITY, GOOD_IDENTITY_REVIEW, True),
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
    # The receipt's `observed` $refs ../app/deployment-identity.json (v0.36.0).
    identity = Resource.from_contents(json.loads((APP_SCHEMAS / "deployment-identity.json").read_text(encoding="utf-8")))
    reg = reg.with_resource(identity.contents["$id"], identity)
    reg = reg.with_resource("https://platform/contracts/app/deployment-identity.json", identity)
    return reg


def schema_for(name: str) -> dict:
    return json.loads((SCHEMAS / name).read_text(encoding="utf-8"))


def check_bindings() -> list[str]:
    """Round-trip the positive fixtures through the generated Python models."""
    sys.path.insert(0, str(ROOT / "gen" / "python"))
    from platform_contracts.app import deployment_identity
    from platform_contracts.delivery import (
        delivery_decision,
        delivery_deployment_receipt,
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
        "delivery.deployment-receipt.json": delivery_deployment_receipt.DeliveryDeploymentReceipt,
        IDENTITY: deployment_identity.AppDeploymentIdentity,
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


def check_deployment_semantics(reg: Registry) -> list[str]:
    """The app-deploy rules JSON Schema cannot express, plus the receipt -> producer-result mapping.

    Equality between two fields of one document (the revision the app reports vs the
    one that was deployed) has no draft 2020-12 keyword, and it is exactly the claim a
    deployment receipt exists to prove, so it is checked here rather than left as prose.
    """
    failures = []

    def violations(r: dict) -> list[str]:
        out = []
        if r["nativeRef"] != f"{r['repository']}:deployments/{r['deploymentId']}":
            out.append("nativeRef must be <repository>:deployments/<deploymentId>")
        if r["rollback"] is not None and r["rollback"]["deploymentId"] == r["deploymentId"]:
            out.append("rollback identity must name an EARLIER deployment")
        if r["kind"] == "rollback" and r["deploymentId"] in (r["restores"], r["rollbackOf"]):
            out.append("a rollback is a new deployment, never the one it restores or replaces")
        if r["result"] == "passed":
            obs = r["observed"] or {}
            if obs.get("revision") != r["mergedRevision"]:
                out.append("passed requires the running app to report mergedRevision")
            if obs.get("deploymentId") != r["deploymentId"]:
                out.append("passed requires the running app to report this deploymentId")
            if r["environment"]["name"] != obs.get("environment"):
                out.append("passed requires the running app to report the receipt's environment")
        return out

    for name, doc in [
        ("GOOD_RECEIPT_PASSED", GOOD_RECEIPT_PASSED),
        ("GOOD_RECEIPT_PENDING_FIRST", GOOD_RECEIPT_PENDING_FIRST),
        ("GOOD_RECEIPT_UNKNOWN_UNREPORTED", GOOD_RECEIPT_UNKNOWN_UNREPORTED),
        ("GOOD_RECEIPT_TIMEOUT", GOOD_RECEIPT_TIMEOUT),
        ("GOOD_RECEIPT_ROLLBACK", GOOD_RECEIPT_ROLLBACK),
        ("GOOD_RECEIPT_REVIEW", GOOD_RECEIPT_REVIEW),
        ("GOOD_RECEIPT_REVIEW_MISMATCH", GOOD_RECEIPT_REVIEW_MISMATCH),
        ("GOOD_RECEIPT_REVIEW_UNREPORTED", GOOD_RECEIPT_REVIEW_UNREPORTED),
    ]:
        failures += [f"deployment: {name}: {v}" for v in violations(doc)]

    # Schema-valid, semantically wrong: each must be caught here.
    for name, doc in [
        ("passed serving the previous revision", {**GOOD_RECEIPT_PASSED, "observed": {**GOOD_IDENTITY, "revision": REV_TASK}}),
        ("passed serving another deployment", {**GOOD_RECEIPT_PASSED, "observed": {**GOOD_IDENTITY, "deploymentId": DEPLOY_PREV}}),
        ("passed with unreported revision", {**GOOD_RECEIPT_PASSED, "observed": {**GOOD_IDENTITY, "revision": None}}),
        ("rollback identity names itself", {**GOOD_RECEIPT_PASSED, "rollback": {**GOOD_RECEIPT_PASSED["rollback"], "deploymentId": DEPLOY_ID}}),
        ("nativeRef names another deployment", {**GOOD_RECEIPT_PASSED, "nativeRef": f"plantpal:deployments/{DEPLOY_PREV}"}),
        ("review passed serving the merged revision", {**GOOD_RECEIPT_REVIEW, "observed": {**GOOD_IDENTITY_REVIEW, "revision": REV_MERGED}}),
        ("review passed with unreported identity", {**GOOD_RECEIPT_REVIEW_UNREPORTED, "result": "passed"}),
        ("review passed reporting the dev environment", {**GOOD_RECEIPT_REVIEW, "observed": {**GOOD_IDENTITY_REVIEW, "environment": "dev"}}),
    ]:
        if not violations(doc):
            failures.append(f"deployment: '{name}' was not caught")

    # The written mapping must yield a schema-valid producer-result for every receipt,
    # and must never report an environment the app did not report.
    validator = Draft202012Validator(schema_for("delivery.producer-result.json"), registry=reg, format_checker=FormatChecker())
    for name, doc in [
        ("GOOD_RECEIPT_PASSED", GOOD_RECEIPT_PASSED),
        ("GOOD_RECEIPT_PENDING_FIRST", GOOD_RECEIPT_PENDING_FIRST),
        ("GOOD_RECEIPT_UNKNOWN_UNREPORTED", GOOD_RECEIPT_UNKNOWN_UNREPORTED),
        ("GOOD_RECEIPT_TIMEOUT", GOOD_RECEIPT_TIMEOUT),
        ("GOOD_RECEIPT_ROLLBACK", GOOD_RECEIPT_ROLLBACK),
        ("GOOD_RECEIPT_REVIEW", GOOD_RECEIPT_REVIEW),
        ("GOOD_RECEIPT_REVIEW_MISMATCH", GOOD_RECEIPT_REVIEW_MISMATCH),
        ("GOOD_RECEIPT_REVIEW_UNREPORTED", GOOD_RECEIPT_REVIEW_UNREPORTED),
    ]:
        mapped = receipt_to_producer_result(doc)
        errors = list(validator.iter_errors(mapped))
        if errors:
            failures.append(f"mapping: {name} -> producer-result invalid: {errors[0].message}")
        if (mapped["environment"] is None) != (doc["observed"] is None or doc["observed"]["revision"] is None):
            failures.append(f"mapping: {name} environment must be present exactly when the app reported a revision")
    review = receipt_to_producer_result(GOOD_RECEIPT_REVIEW)
    if review["environment"]["name"] != "review" or review["revision"] != REV_PR:
        failures.append("mapping: a review receipt must map to environment review at the PR head")
    if receipt_to_producer_result(GOOD_RECEIPT_REVIEW_UNREPORTED)["environment"] is not None:
        failures.append("mapping: an unreported review identity must stay null, not be filled from the receipt")
    mismatch = receipt_to_producer_result(GOOD_RECEIPT_REVIEW_MISMATCH)
    if mismatch["outcome"] != "failed" or mismatch["environment"]["deployedRevision"] != REV_MERGED:
        failures.append("mapping: a revision mismatch must be failed and keep the revision the app reported")
    mapped = receipt_to_producer_result(GOOD_RECEIPT_PASSED)
    if mapped["environment"]["deployedRevision"] != GOOD_RECEIPT_PASSED["observed"]["revision"]:
        failures.append("mapping: deployedRevision must come from observed.revision")
    if mapped["artifactRef"] != DIGEST_BE:
        failures.append("mapping: artifactRef must be the primary component's digest")
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


def check_app_deploy_api(reg: Registry) -> list[str]:
    """v0.37.0 app-deploy HTTP lookup: routes, payloads, and a machine-distinguishable miss."""
    text = DEPLOY_API.read_text(encoding="utf-8")
    api = yaml.safe_load(text)
    failures = []

    receipt_route = "/delivery/v1/app-deploys/{deploymentId}/receipt"
    result_route = "/delivery/v1/app-deploys/{deploymentId}"
    for route, op in [(result_route, "getAppDeployResult"), (receipt_route, "getAppDeployReceipt")]:
        get = api["paths"].get(route, {}).get("get", {})
        if get.get("operationId") != op:
            failures.append(f"app-deploy openapi: missing GET {route} ({op})")
            continue
        if "404" not in get["responses"]:
            failures.append(f"app-deploy openapi: {op} has no 404 response")

    # The two 200 payloads: the receipt verbatim, and its producer-result mapping.
    def data_ref(route):
        resp = api["paths"][route]["get"]["responses"]["200"]
        target = resp["$ref"].removeprefix("#/components/responses/")
        schema = api["components"]["responses"][target]["content"]["application/json"]["schema"]
        return schema["properties"]["data"]["$ref"]

    if data_ref(receipt_route) != "../delivery/delivery.deployment-receipt.json":
        failures.append("app-deploy openapi: the receipt route must serve delivery.deployment-receipt verbatim")
    if data_ref(result_route) != "../delivery/delivery.producer-result.json":
        failures.append("app-deploy openapi: the result route must serve delivery.producer-result")

    # A miss must be a named code, never retryable-looking, and never confusable with
    # "could not ask": the other three codes have to be on the published surface too.
    for code in ["deployment_not_found", "caller_not_authorized", "producer_unavailable", "invalid_request"]:
        if code not in text:
            failures.append(f"app-deploy openapi: status table does not name {code}")

    comps = api["components"]["schemas"]
    miss = {"code": "deployment_not_found", "message": "no receipt for pla-dev-1", "retryable": False}
    cases = [
        ("DeploymentNotFoundError", miss, True),
        ("DeploymentNotFoundError", {**miss, "code": "producer_unavailable"}, False),
        ("DeploymentNotFoundError", {**miss, "retryable": True}, False),
    ]
    for name, doc, ok in cases:
        schema = {"$schema": "https://json-schema.org/draft/2020-12/schema", **_rewrite_refs(comps[name])}
        errors = list(Draft202012Validator(schema, registry=reg, format_checker=FormatChecker()).iter_errors(doc))
        if ok and errors:
            failures.append(f"app-deploy openapi {name}: expected valid, got {errors[0].message}")
        if not ok and not errors:
            failures.append(f"app-deploy openapi {name}: expected INVALID fixture to be rejected")

    # Both 200 payloads must accept the same deployment the mapping test uses.
    envelope_cases = [
        ("delivery.deployment-receipt.json", GOOD_RECEIPT_PASSED),
        ("delivery.producer-result.json", receipt_to_producer_result(GOOD_RECEIPT_PASSED)),
    ]
    for name, doc in envelope_cases:
        errors = list(Draft202012Validator(schema_for(name), registry=reg, format_checker=FormatChecker()).iter_errors(doc))
        if errors:
            failures.append(f"app-deploy openapi: {name} payload rejected: {errors[0].message}")
    return failures


def check_review_evidence_semantics() -> list[str]:
    """`passed` deployment/live evidence must show the URL serving the recorded revision."""
    failures = []

    def violations(e: dict) -> list[str]:
        env = e["environment"]
        if env is None or e["result"] != "passed":
            return []
        out = []
        if env["deployedRevision"] != e["revision"]:
            out.append("passed requires environment.deployedRevision == revision")
        return out

    for name, doc in [("GOOD_EVIDENCE_LIVE", GOOD_EVIDENCE_LIVE), ("GOOD_EVIDENCE_REVIEW", GOOD_EVIDENCE_REVIEW), ("GOOD_EVIDENCE_REVIEW_LIVE", GOOD_EVIDENCE_REVIEW_LIVE), ("GOOD_EVIDENCE_REVIEW_MISMATCH", GOOD_EVIDENCE_REVIEW_MISMATCH)]:
        failures += [f"review evidence: {name}: {v}" for v in violations(doc)]
    if not violations({**GOOD_EVIDENCE_REVIEW_MISMATCH, "result": "passed"}):
        failures.append("review evidence: a revision mismatch recorded as passed was not caught")
    return failures


def check_review_api(reg: Registry) -> list[str]:
    """v0.38.0 launcher review-environment port: routes, status/receipt coupling, miss body."""
    api = yaml.safe_load(REVIEW_API.read_text(encoding="utf-8"))
    failures = []
    for route, method, op in [
        ("/review/v1/environments", "post", "startReviewEnvironment"),
        ("/review/v1/environments/{idempotencyKey}", "get", "getReviewEnvironment"),
        ("/review/v1/environments/{idempotencyKey}", "delete", "stopReviewEnvironment"),
    ]:
        if api["paths"].get(route, {}).get(method, {}).get("operationId") != op:
            failures.append(f"review openapi: missing {method.upper()} {route} ({op})")
    if "404" not in api["paths"]["/review/v1/environments/{idempotencyKey}"]["get"]["responses"]:
        failures.append("review openapi: lookup has no 404 response")

    components = api["components"]

    def validate(name: str, doc: dict) -> list:
        schema = {"$schema": "https://json-schema.org/draft/2020-12/schema", "$id": "https://platform/contracts/launcher/review-environment", **components["schemas"][name], "components": components}
        return list(Draft202012Validator(schema, registry=reg, format_checker=FormatChecker()).iter_errors(doc))

    request = {"repository": "plantpal", "branch": "factory/pla-42", "pullRequest": {"number": 42, "url": None}, "expectedRevision": REV_PR, "idempotencyKey": "pla-42-3333333"}
    env = {
        "idempotencyKey": "pla-42-3333333", "repository": "plantpal", "branch": "factory/pla-42",
        "pullRequest": {"number": 42, "url": None}, "expectedRevision": REV_PR, "status": "ready",
        "receipt": GOOD_RECEIPT_REVIEW, "error": None, "startedAt": NOW, "updatedAt": NOW,
    }
    err = {"code": "build_failed", "message": "image build failed", "retryable": True}
    not_found = {"code": "review_environment_not_found", "message": "no environment for that key", "retryable": False}
    cases = [
        ("StartReviewEnvironmentRequest", request, True),
        ("StartReviewEnvironmentRequest", {**request, "pullRequest": None}, True),
        ("StartReviewEnvironmentRequest", {**request, "expectedRevision": "3333333"}, False),
        ("StartReviewEnvironmentRequest", {k: v for k, v in request.items() if k != "idempotencyKey"}, False),
        ("ReviewEnvironment", env, True),
        ("ReviewEnvironment", {**env, "status": "starting", "receipt": None}, True),
        ("ReviewEnvironment", {**env, "status": "starting", "receipt": {**GOOD_RECEIPT_REVIEW, "result": "pending"}}, True),
        ("ReviewEnvironment", {**env, "status": "failed", "receipt": GOOD_RECEIPT_REVIEW_MISMATCH}, True),
        ("ReviewEnvironment", {**env, "status": "failed", "receipt": None, "error": err}, True),
        ("ReviewEnvironment", {**env, "status": "stopped"}, True),
        ("ReviewEnvironment", {**env, "receipt": None}, False),
        ("ReviewEnvironment", {**env, "receipt": GOOD_RECEIPT_REVIEW_MISMATCH}, False),
        ("ReviewEnvironment", {**env, "receipt": GOOD_RECEIPT_REVIEW_UNREPORTED}, False),
        ("ReviewEnvironment", {**env, "receipt": GOOD_RECEIPT_PASSED}, False),
        ("ReviewEnvironment", {**env, "status": "failed", "receipt": None, "error": None}, False),
        ("ReviewEnvironment", {**env, "status": "failed", "receipt": GOOD_RECEIPT_REVIEW}, False),
        ("ReviewEnvironment", {**env, "status": "starting", "receipt": None, "error": err}, False),
        ("ReviewEnvironmentNotFoundError", not_found, True),
        ("ReviewEnvironmentNotFoundError", {**not_found, "retryable": True}, False),
        ("ReviewEnvironmentNotFoundError", {**not_found, "code": "launcher_unavailable"}, False),
    ]
    for name, doc, ok in cases:
        errors = validate(name, doc)
        if ok and errors:
            failures.append(f"review openapi {name}: expected valid, got {errors[0].message}")
        if not ok and not errors:
            failures.append(f"review openapi {name}: expected INVALID fixture to be rejected")

    if env["receipt"]["observed"]["revision"] != env["expectedRevision"]:
        failures.append("review openapi: the ready fixture does not serve expectedRevision")
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
    failures += check_app_deploy_api(reg)
    failures += check_review_api(reg)
    failures += check_review_evidence_semantics()
    failures += check_bindings()
    failures += check_recovery_semantics()
    failures += check_deployment_semantics(reg)

    for f in failures:
        print("FAIL ", f)
    print(f"{len(CASES)} schema cases, {len(failures)} failures")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
