"""
Schema-level validation for schemas/agent-runner/parked.*.json (D115 parked work).

Validates the JSON Schemas directly against example documents, independent of any
language binding. Run: python tests/validate_parked.py
"""
import copy
import hashlib
import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parent.parent
SCHEMAS = ROOT / "schemas" / "agent-runner"

SHA = "0123456789abcdef0123456789abcdef01234567"
DEMAND_A = "dashboard-20260930-d115-parked-work"
DEMAND_B = "ci-runner-20260930-d115-parked-work"


def load(name):
    return json.loads((SCHEMAS / name).read_text(encoding="utf-8"))


def registry():
    resources = []
    for path in SCHEMAS.glob("*.json"):
        schema = load(path.name)
        resource = Resource.from_contents(schema)
        resources.append((schema["$id"], resource))
        resources.append((schema["$id"] + ".json", resource))
    return Registry().with_resources(resources)


REG = registry()


def errors(schema, doc):
    return list(Draft202012Validator(schema, registry=REG).iter_errors(doc))


def expect_valid(schema, doc, label):
    errs = errors(schema, doc)
    if errs:
        raise AssertionError(f"{label}: expected valid, got {errs}")
    print(f"PASS  {label}")


def expect_invalid(schema, doc, label):
    errs = errors(schema, doc)
    if not errs:
        raise AssertionError(f"{label}: expected invalid, but document passed")
    print(f"PASS  {label} (rejected: {errs[0].message[:90]})")


CONDITIONS = {
    "ci-run": {"kind": "ci-run", "repo": "plantpal", "commit": SHA, "pullRequest": 92},
    "pull-request": {"kind": "pull-request", "repo": "plantpal", "pullRequest": 92, "until": "merged-or-closed"},
    "repository-created": {"kind": "repository-created", "repo": "new-service"},
    "owner-decision": {"kind": "owner-decision", "decisionId": "decision-plantpal-92", "question": "Ship the schema change?"},
    "demands-all": {"kind": "demands", "mode": "all", "demands": [
        {"demandId": DEMAND_A, "state": "satisfied"}, {"demandId": DEMAND_B, "state": "approved"}]},
    "demands-any": {"kind": "demands", "mode": "any", "demands": [
        {"demandId": DEMAND_A, "state": "satisfied"}, {"demandId": DEMAND_B, "state": "archived"}]},
}

OUTCOMES = {
    "ci-run-failure": {"kind": "ci-run", "repo": "plantpal", "commit": SHA, "runId": "88001", "result": "failure",
                       "pullRequest": 92, "url": "https://example.test/runs/88001", "failedChecks": ["backend-tests"]},
    "ci-run-success": {"kind": "ci-run", "repo": "plantpal", "commit": SHA, "runId": "88002", "result": "success"},
    "pr-merged": {"kind": "pull-request", "repo": "plantpal", "pullRequest": 92, "result": "merged", "mergeCommit": SHA},
    "pr-closed": {"kind": "pull-request", "repo": "plantpal", "pullRequest": 92, "result": "closed", "mergeCommit": None},
    "repo-created": {"kind": "repository-created", "repo": "new-service", "result": "created",
                     "remoteUrl": "https://example.test/org/new-service"},
    "decision": {"kind": "owner-decision", "decisionId": "decision-plantpal-92", "result": "approved",
                 "decidedBy": "owner", "answer": None},
    "demands": {"kind": "demands", "mode": "any", "result": "satisfied",
                "demands": [{"demandId": DEMAND_A, "state": "satisfied"}]},
}


def event(outcome, key="ci-run:plantpal:" + SHA + ":88001", source="ci-runner"):
    return {"eventKey": key, "source": source, "observedAt": "2026-09-30T20:00:00Z", "outcome": outcome}


def parked(condition):
    return {
        "state": "parked", "runId": "run-1", "dispatchKey": "factory-operation:9f0e2b1a-1111-2222-3333-444455556666",
        "repo": "plantpal", "demandId": "factory-20260929-plantpal-92", "resumeOwner": "factory",
        "parkedAt": "2026-09-30T19:00:00Z",
        "wait": {"waitId": "wait-plantpal-pr-92", "condition": condition, "deadline": "2026-10-01T19:00:00Z"},
        "reference": {"repo": "plantpal", "branch": "task/pla-92", "pullRequest": 92, "commit": SHA, "demandIds": [DEMAND_A]},
        "checkpoint": SHA,
        "resumeNote": "PR opened; waiting for CI. On failure read the failed checks and fix.",
    }


def resume_key(wait_id, event_key):
    return "resume:" + hashlib.sha256(f"{wait_id}\n{event_key}".encode("utf-8")).hexdigest()


def resume_request(ev, action, wait_id="wait-plantpal-pr-92"):
    return {
        "waitId": wait_id, "runId": "run-1", "resumeOwner": "factory", "action": action,
        "resumeNote": "PR opened; waiting for CI.", "event": ev,
        "dispatch": {"repo": "plantpal", "prompt": "Resume: CI failed on backend-tests. Fix it.",
                     "dispatchKey": resume_key(wait_id, ev["eventKey"])},
    }


def main():
    wait_s, run_s, event_s, resume_s = (load(n) for n in (
        "parked.wait-condition.json", "parked.run-result.json",
        "parked.condition-event.json", "parked.resume-request.json"))

    for name, cond in CONDITIONS.items():
        expect_valid(wait_s, cond, f"wait-condition: {name} (known-good)")
    expect_invalid(wait_s, {**CONDITIONS["ci-run"], "commit": "abc123"}, "wait-condition: ci-run with a short SHA (known-bad)")
    expect_invalid(wait_s, {**CONDITIONS["pull-request"], "until": "rejected"}, "wait-condition: unknown pull-request until (known-bad)")
    expect_invalid(wait_s, {"kind": "demands", "mode": "all", "demands": []}, "wait-condition: demands with no demands (known-bad)")
    expect_invalid(wait_s, {**CONDITIONS["demands-all"], "mode": "none"}, "wait-condition: unknown demands mode (known-bad)")
    expect_invalid(wait_s, {**CONDITIONS["demands-any"], "demands": [{"demandId": "Not A Demand", "state": "satisfied"}]},
                   "wait-condition: malformed demand id (known-bad)")
    expect_invalid(wait_s, {"kind": "timer", "seconds": 60}, "wait-condition: unmodelled kind (known-bad)")
    expect_invalid(wait_s, {**CONDITIONS["repository-created"], "extra": 1}, "wait-condition: extra member (known-bad)")

    for name, cond in CONDITIONS.items():
        expect_valid(run_s, parked(cond), f"run-result: parked on {name} (known-good)")
    no_deadline = parked(CONDITIONS["ci-run"])
    del no_deadline["wait"]["deadline"]
    expect_invalid(run_s, no_deadline, "run-result: wait without a deadline (known-bad)")
    no_ref = parked(CONDITIONS["ci-run"])
    del no_ref["reference"]
    expect_invalid(run_s, no_ref, "run-result: no exact reference (known-bad)")
    no_note = parked(CONDITIONS["ci-run"])
    del no_note["resumeNote"]
    expect_invalid(run_s, no_note, "run-result: no resume note (known-bad)")
    expect_invalid(run_s, {**parked(CONDITIONS["ci-run"]), "state": "finished"}, "run-result: state is not parked (known-bad)")
    expect_invalid(run_s, {**parked(CONDITIONS["ci-run"]), "resumeOwner": "demand-coordinator"},
                   "run-result: coordinator cannot be the resume owner (known-bad)")

    for name, outcome in OUTCOMES.items():
        expect_valid(event_s, event(outcome), f"condition-event: {name} (known-good)")
    expect_invalid(event_s, {k: v for k, v in event(OUTCOMES["pr-merged"]).items() if k != "eventKey"},
                   "condition-event: no stable eventKey (known-bad)")
    expect_invalid(event_s, event(OUTCOMES["pr-merged"], key="short"), "condition-event: eventKey too short (known-bad)")
    expect_invalid(event_s, event(OUTCOMES["pr-merged"], source="agent-runner"), "condition-event: agent-runner is not a producer (known-bad)")
    expect_invalid(event_s, event({**OUTCOMES["ci-run-failure"], "result": "flaky"}), "condition-event: unknown CI result (known-bad)")
    no_outcome = event(OUTCOMES["pr-merged"])
    del no_outcome["outcome"]
    expect_invalid(event_s, no_outcome, "condition-event: no observed outcome (known-bad)")

    # the keyed resume: same wait + same event -> same key; different event -> different key
    ev = event(OUTCOMES["ci-run-failure"])
    req = resume_request(ev, "fix")
    expect_valid(resume_s, req, "resume-request: CI failed -> fix (known-good)")
    expect_valid(resume_s, resume_request(event(OUTCOMES["pr-merged"], key="pull-request:plantpal:92:merged", source="ci-runner"), "continue"),
                 "resume-request: PR merged -> continue (known-good)")
    expect_valid(resume_s, resume_request(event(OUTCOMES["pr-closed"], key="pull-request:plantpal:92:closed"), "reassess"),
                 "resume-request: PR closed -> reassess (known-good)")
    no_key = copy.deepcopy(req)
    del no_key["dispatch"]["dispatchKey"]
    expect_invalid(resume_s, no_key, "resume-request: dispatch without a dispatchKey (known-bad)")
    no_note = copy.deepcopy(req)
    del no_note["resumeNote"]
    expect_invalid(resume_s, no_note, "resume-request: no resume note (known-bad)")
    no_event = copy.deepcopy(req)
    del no_event["event"]
    expect_invalid(resume_s, no_event, "resume-request: no outcome/event (known-bad)")
    expect_invalid(resume_s, {**req, "action": "wait"}, "resume-request: unknown action (known-bad)")

    k1 = resume_key("wait-plantpal-pr-92", ev["eventKey"])
    if k1 != req["dispatch"]["dispatchKey"] or resume_key("wait-plantpal-pr-92", ev["eventKey"]) != k1:
        raise AssertionError("resume key derivation is not deterministic")
    if resume_key("wait-plantpal-pr-92", "ci-run:plantpal:" + SHA + ":88002") == k1:
        raise AssertionError("two different events must not share a resume key")
    if resume_key("wait-other-wait-1", ev["eventKey"]) == k1:
        raise AssertionError("two different waits must not share a resume key")
    documented = resume_key("wait-plantpal-pr-92", "ci-run:plantpal:" + SHA + ":88001")
    if documented not in resume_s["description"]:
        raise AssertionError("resume-request: the documented worked-example key no longer matches the recipe")
    print("PASS  resume-request: key derivation is deterministic, per-event, per-wait and matches the documented example")

    # the envelope's `after` edge is unchanged by this release
    after = json.loads((ROOT / "schemas" / "demand-coordinator" / "demand.json").read_text(encoding="utf-8"))["properties"]["after"]
    if after["type"] != "array" or after["items"].get("type") != "string" or "minItems" not in after:
        raise AssertionError("demand.after must stay an array of demand-id strings")
    print("PASS  demand.after is still an ordering-only array of demand ids")
    return 0


if __name__ == "__main__":
    sys.exit(main())
