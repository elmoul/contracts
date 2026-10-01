"""
Schema-level validation for schemas/launcher/command.*.json (D115 command-execution port).

Run: python tests/validate_command.py
"""
import copy
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parent.parent
SCHEMAS = ROOT / "schemas" / "launcher"
SHA = "0123456789abcdef0123456789abcdef01234567"


def load(name):
    return json.loads((SCHEMAS / name).read_text(encoding="utf-8"))


REQUEST, RESULT, ERROR = (load(f"command.{n}.json") for n in ("request", "result", "error"))


def errors(schema, doc):
    return list(Draft202012Validator(schema).iter_errors(doc))


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


def request_hash(req):
    body = {"command": req["command"]}
    if "parameters" in req:
        body["parameters"] = req["parameters"]
    text = json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(text.encode("utf-8")).hexdigest(), len(text.encode("utf-8"))


REQ = {
    "commandKey": "factory-operation:9f0e2b1a-1111-2222-3333-444455556666",
    "command": "deploy-plantpal",
    "parameters": {"commit": SHA},
    "demandId": "factory-20260930-some-demand",
}

RES_EXITED = {
    "commandKey": REQ["commandKey"],
    "requestHash": "32cd1ff2c7399c376014f82724aa99855c9b245fd1ea2d066201602b33a59311",
    "executionId": "exec-0001",
    "command": "deploy-plantpal",
    "state": "exited",
    "exitCode": 0,
    "evidence": {"kind": "log", "location": "commands/exec-0001.log", "sha256": "a" * 64},
    "reservedAt": "2026-09-30T10:00:00Z",
    "startedAt": "2026-09-30T10:00:01Z",
    "finishedAt": "2026-09-30T10:00:30Z",
    "replayed": False,
}


def mutate(base, **kw):
    d = copy.deepcopy(base)
    d.update(kw)
    return d


def main():
    # request
    expect_valid(REQUEST, REQ, "request: full")
    expect_valid(REQUEST, {"commandKey": REQ["commandKey"], "command": "deploy-plantpal"}, "request: minimal")
    expect_invalid(REQUEST, {"command": "deploy-plantpal"}, "request: commandKey required")
    expect_invalid(REQUEST, {"commandKey": REQ["commandKey"]}, "request: command required")
    expect_invalid(REQUEST, mutate(REQ, commandKey="short"), "request: key too short")
    expect_invalid(REQUEST, mutate(REQ, command="rm -rf /"), "request: command is a name, not shell text")
    expect_invalid(REQUEST, mutate(REQ, command="Deploy"), "request: command name lowercase")
    expect_invalid(REQUEST, mutate(REQ, parameters={"n": 1}), "request: parameter values are strings")
    expect_invalid(REQUEST, mutate(REQ, env={"A": "b"}), "request: no env / unknown member")
    expect_invalid(REQUEST, mutate(REQ, demandId="not a demand"), "request: demandId pattern")

    # requestHash worked examples (documented in command.request)
    h, n = request_hash(REQ)
    assert (h, n) == ("32cd1ff2c7399c376014f82724aa99855c9b245fd1ea2d066201602b33a59311", 96), (h, n)
    h2, _ = request_hash({"command": "deploy-plantpal"})
    assert h2 == "289e2c287969f78079c011a5b655361aa58dfbbb5f95412ad7098cd9d81f2501", h2
    assert request_hash({"command": "x", "parameters": {}})[0] != request_hash({"command": "x"})[0]
    assert request_hash(mutate(REQ, commandKey="another-key-0001", demandId="x-20260101-y"))[0] == h
    assert request_hash({"command": "c", "parameters": {"b": "é", "a": "1"}})[0] == request_hash(
        {"command": "c", "parameters": {"a": "1", "b": "é"}})[0]
    print("PASS  requestHash worked examples and canonicalization rules")

    # result
    expect_valid(RESULT, RES_EXITED, "result: exited 0 with evidence")
    expect_valid(RESULT, mutate(RES_EXITED, exitCode=2), "result: exited non-zero")
    expect_valid(RESULT, mutate(RES_EXITED, replayed=True), "result: replay")
    expect_valid(RESULT, mutate(RES_EXITED, state="running", exitCode=None, evidence=None,
                                finishedAt=None), "result: running")
    expect_valid(RESULT, mutate(RES_EXITED, state="unknown", exitCode=None, evidence=None,
                                startedAt=None, finishedAt=None), "result: unknown, nothing left behind")
    expect_invalid(RESULT, mutate(RES_EXITED, exitCode=None), "result: exited needs an exit code")
    expect_invalid(RESULT, mutate(RES_EXITED, evidence=None), "result: exited needs evidence")
    expect_invalid(RESULT, mutate(RES_EXITED, finishedAt=None), "result: exited needs finishedAt")
    expect_invalid(RESULT, mutate(RES_EXITED, state="unknown", evidence=None, finishedAt=None),
                   "result: unknown must not report an exit code (never 0 for not reported)")
    expect_invalid(RESULT, mutate(RES_EXITED, state="running", exitCode=0, evidence=None, finishedAt=None),
                   "result: running must not report an exit code")
    expect_invalid(RESULT, mutate(RES_EXITED, state="done"), "result: state is closed")
    expect_invalid(RESULT, mutate(RES_EXITED, exitCode="0"), "result: exitCode is an integer")
    expect_invalid(RESULT, mutate(RES_EXITED, evidence={"kind": "log"}), "result: evidence needs location")
    expect_invalid(RESULT, mutate(RES_EXITED, evidence={"kind": "ftp", "location": "x"}), "result: evidence kind closed")
    expect_invalid(RESULT, mutate(RES_EXITED, requestHash="ABC"), "result: requestHash is 64 lowercase hex")
    bad = copy.deepcopy(RES_EXITED)
    del bad["executionId"]
    expect_invalid(RESULT, bad, "result: executionId required")

    # errors
    expect_valid(ERROR, {"code": "unknown_command", "message": "no such command", "retryable": False,
                         "command": "nope", "ownerAction": "Add 'nope' to the allowlist."}, "error: unknown_command")
    expect_valid(ERROR, {"code": "command_refused", "message": "disabled", "retryable": False,
                         "reason": "disabled"}, "error: command_refused with reason")
    expect_valid(ERROR, {"code": "command_key_conflict", "message": "key reserved", "retryable": False},
                 "error: command_key_conflict")
    expect_valid(ERROR, {"code": "invalid_request", "message": "bad body", "retryable": False}, "error: invalid_request")
    expect_invalid(ERROR, {"code": "command_refused", "message": "x", "retryable": False},
                   "error: command_refused requires reason")
    expect_invalid(ERROR, {"code": "command_refused", "message": "x", "retryable": False, "reason": "because"},
                   "error: reason is closed")
    expect_invalid(ERROR, {"code": "teapot", "message": "x", "retryable": False}, "error: code is closed")
    expect_invalid(ERROR, {"code": "unknown_command", "message": "x"}, "error: retryable required")
    print("All command schema checks passed.")


if __name__ == "__main__":
    main()
