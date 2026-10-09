"""
Schema-level validation for the planner's setup routes and the delivery `startable` answer (v0.55.0):
schemas/youtrack/planner.setup-{progress-request,progress-response,gate,error}.json and the optional
`startable` on schemas/delivery/delivery.{workflow,issue}.json.

Run: python tests/validate_setup_gate.py
"""
import copy
import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parent.parent
S = ROOT / "schemas"


def load(rel):
    schema = json.loads((S / rel).read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema, format_checker=FormatChecker())


REQ = load("youtrack/planner.setup-progress-request.json")
RESP = load("youtrack/planner.setup-progress-response.json")
GATE = load("youtrack/planner.setup-gate.json")
ERR = load("youtrack/planner.setup-error.json")
SETUP = load("factory/factory.handover-setup.json")
WF = load("delivery/delivery.workflow.json")

failures = []


def expect(ok, label):
    if not ok:
        failures.append(label)
        print(f"FAIL  {label}")


def bad(v, doc):
    return bool(list(v.iter_errors(doc)))


STEPS = ["app-repo", "hexagon-repo", "onboard", "register-project", "verify-discovery"]


def setup(state="pending", step_states=None):
    step_states = step_states or ["pending"] * 5
    return {"name": "Set up repositories", "state": state, "localOnly": False,
            "steps": [{"id": i, "state": s} for i, s in zip(STEPS, step_states)],
            "updatedAt": "2026-10-09T10:00:00Z"}


# ---- request
for step in STEPS:
    expect(not bad(REQ, {"step": step, "state": "running"}), f"request step {step} validates")
for st in ("pending", "running", "done", "skipped"):
    expect(not bad(REQ, {"step": "onboard", "state": st}), f"request state {st} validates")
expect(not bad(REQ, {"step": "onboard", "state": "failed", "reason": "onboard_failed", "detail": "x"}), "failed with reason and detail validates")
expect(not bad(REQ, {"step": "onboard", "state": "failed", "reason": "timeout"}), "failed with reason only validates")
for label, doc in [
    ("unknown step", {"step": "deploy", "state": "done"}),
    ("unknown state", {"step": "onboard", "state": "stuck"}),
    ("missing step", {"state": "done"}),
    ("missing state", {"step": "onboard"}),
    ("failed without reason", {"step": "onboard", "state": "failed"}),
    ("reason on a non-failed step", {"step": "onboard", "state": "done", "reason": "timeout"}),
    ("detail on a non-failed step", {"step": "onboard", "state": "done", "detail": "x"}),
    ("unknown reason", {"step": "onboard", "state": "failed", "reason": "boom"}),
    ("detail over 500 characters", {"step": "onboard", "state": "failed", "reason": "timeout", "detail": "x" * 501}),
    ("extra property", {"step": "onboard", "state": "done", "at": "2026-10-09T10:00:00Z"}),
]:
    expect(bad(REQ, doc), f"request with {label} refused")

# ---- response is the setup object, kept equal to the standalone schema
expect(not bad(RESP, setup()), "response: a setup object validates")
expect(not bad(RESP, setup("done", ["done"] * 5)), "response: a done setup validates")
expect(bad(RESP, {**setup(), "extra": 1}), "response: extra property refused")
expect(bad(RESP, {"data": setup()}), "response: the data wrapper is not part of the payload")
strip = lambda s: {k: v for k, v in s.schema.items() if k not in ("$id", "title", "description")}
expect(strip(RESP) == strip(SETUP), "response schema equals factory.handover-setup apart from id, title, description")

# ---- gate
closed = {"projectKey": "APP", "open": False, "reason": "setup-not-done", "setupIssue": "APP-1", "setup": setup("running", ["done", "skipped", "running", "pending", "pending"])}
opened = {"projectKey": "APP", "open": True, "reason": None, "setupIssue": "APP-1", "setup": setup("done", ["done"] * 5)}
none_held = {"projectKey": "APP", "open": True, "reason": None, "setupIssue": None, "setup": None}
for label, doc in [
    ("closed gate", closed), ("open gate", opened), ("no setup task held", none_held),
    ("closed gate, other issue", {**closed, "startable": {"value": False, "reason": "setup-not-done"}}),
    ("the setup task itself", {**opened, "startable": {"value": False, "reason": "setup-task"}}),
    ("startable true", {**opened, "startable": {"value": True, "reason": None}}),
]:
    expect(not bad(GATE, doc), f"gate: {label} validates")
for label, doc in [
    ("unknown gate reason", {**closed, "reason": "other"}),
    ("missing open", {k: v for k, v in closed.items() if k != "open"}),
    ("missing setup", {k: v for k, v in closed.items() if k != "setup"}),
    ("extra property", {**closed, "extra": 1}),
    ("startable with unknown reason", {**closed, "startable": {"value": False, "reason": "nope"}}),
    ("startable without reason", {**closed, "startable": {"value": True}}),
    ("startable with extra property", {**closed, "startable": {"value": True, "reason": None, "x": 1}}),
    ("an invalid embedded setup", {**closed, "setup": {**setup(), "name": "Other"}}),
]:
    expect(bad(GATE, doc), f"gate: {label} refused")

# ---- error
for code in ("setup_project_unknown", "setup_step_unknown", "setup_progress_invalid"):
    expect(not bad(ERR, {"code": code, "message": "m"}), f"error code {code} validates")
expect(bad(ERR, {"code": "unknown_project", "message": "m"}), "error: a code outside the three refused")
expect(bad(ERR, {"code": "setup_step_unknown"}), "error: message required")
expect(bad(ERR, {"code": "setup_step_unknown", "message": "m", "details": []}), "error: extra property refused")

# ---- delivery startable
workflow = {"project": "APP", "stateField": "State", "states": [], "complete": True, "readAt": "2026-10-09T10:00:00Z"}
for v in ({"value": True, "reason": None}, {"value": False, "reason": "setup-not-done"}, {"value": False, "reason": "setup-task"}):
    expect(not bad(WF, {**workflow, "startable": v}), f"workflow startable {v} validates")
expect(not bad(WF, workflow), "workflow without startable still validates")
for label, v in [("unknown reason", {"value": False, "reason": "x"}), ("missing reason", {"value": True}),
                 ("extra property", {"value": True, "reason": None, "x": 1}), ("non-boolean value", {"value": "yes", "reason": None})]:
    expect(bad(WF, {**workflow, "startable": v}), f"workflow startable with {label} refused")

# delivery.issue carries the identical property
issue = json.loads((S / "delivery/delivery.issue.json").read_text(encoding="utf-8"))
wf = json.loads((S / "delivery/delivery.workflow.json").read_text(encoding="utf-8"))
expect(issue["properties"]["startable"] == wf["properties"]["startable"], "delivery.issue and delivery.workflow define startable identically")
expect("startable" not in issue["required"] and "startable" not in wf["required"], "startable is optional on both")

if failures:
    print(f"{len(failures)} failure(s)")
    sys.exit(1)
print("validate_setup_gate: all checks passed")
