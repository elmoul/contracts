"""
Schema-level validation for schemas/agent-runner/*.json.

Mirrors validate_demand.py's pattern: validates the JSON Schemas directly
against example documents, independent of any language binding.
Run: python tests/validate_runner.py
"""
import hashlib
import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator
from referencing import Registry, Resource

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

# --- keyed dispatch, observed workspace identity, dispatch lookup -------------------
# Demand agent-runner-20260927-contracts-runner-keyed-dispatch.

DISPATCH_KEY = "factory-operation:9f0e2b1a-1111-2222-3333-444455556666"
BASE_SHA = "3f9c1a4b7d2e5f8091a2b3c4d5e6f708192a3b4c"
HEAD_SHA = "9a8b7c6d5e4f30211f2e3d4c5b6a79880a1b2c3d"

GOOD_DISPATCH_REQUEST_KEYED = {**GOOD_DISPATCH_REQUEST, "dispatchKey": DISPATCH_KEY}

# The criterion is that an UNKEYED request stays valid byte-for-byte, so the two
# documents above must differ by exactly the one added member and nothing else.
assert set(GOOD_DISPATCH_REQUEST_KEYED) - set(GOOD_DISPATCH_REQUEST) == {"dispatchKey"}, (
    "keyed fixture must be the unkeyed fixture plus dispatchKey and nothing else"
)

BAD_DISPATCH_REQUEST_SHORT_KEY = {**GOOD_DISPATCH_REQUEST, "dispatchKey": "short"}
BAD_DISPATCH_REQUEST_KEY_BAD_CHARS = {**GOOD_DISPATCH_REQUEST, "dispatchKey": "has spaces/and+slashes"}
BAD_DISPATCH_REQUEST_KEY_LEADING_PUNCT = {**GOOD_DISPATCH_REQUEST, "dispatchKey": "-leading-punct-key"}
BAD_DISPATCH_REQUEST_KEY_TOO_LONG = {**GOOD_DISPATCH_REQUEST, "dispatchKey": "a" * 201}

GOOD_RUN_RECORD_KEYED = {**GOOD_RUN_RECORD_FINISHED, "dispatchKey": DISPATCH_KEY}

GOOD_RUN_RECORD_WITH_WORKSPACE = {
    **GOOD_RUN_RECORD_KEYED,
    "workspace": {
        "baseBranch": "main",
        "baseRevision": BASE_SHA,
        "branch": "task/keyed-dispatch",
        "revision": HEAD_SHA,
        "dirty": False,
        "observedAt": "2026-09-27T10:14:00Z",
    },
}

GOOD_RUN_RECORD_WORKSPACE_NULL = {**GOOD_RUN_RECORD_KEYED, "workspace": None}

# Nothing at all observed (not a git repo / both observations failed): every field
# null, never a default. A consumer must not read this as "clean at HEAD".
GOOD_RUN_RECORD_WORKSPACE_UNOBSERVED = {
    **GOOD_RUN_RECORD_KEYED,
    "workspace": {
        "baseBranch": None,
        "baseRevision": None,
        "branch": None,
        "revision": None,
        "dirty": None,
        "observedAt": None,
    },
}

# An orphan reconciled after a restart: the pre-launch observation survived, the
# post-exit one never happened, so branch/revision/dirty/observedAt stay null.
GOOD_RUN_RECORD_WORKSPACE_ORPHAN = {
    **GOOD_RUN_RECORD_KEYED,
    "state": "failed",
    "exitCode": None,
    "error": "orphaned by runner restart; settled failed, never relaunched",
    "workspace": {
        "baseBranch": "main",
        "baseRevision": BASE_SHA,
        "branch": None,
        "revision": None,
        "dirty": None,
        "observedAt": None,
    },
}

BAD_RUN_RECORD_WORKSPACE_SHORT_SHA = {
    **GOOD_RUN_RECORD_WITH_WORKSPACE,
    "workspace": {**GOOD_RUN_RECORD_WITH_WORKSPACE["workspace"], "revision": HEAD_SHA[:12]},
}

BAD_RUN_RECORD_WORKSPACE_UPPERCASE_SHA = {
    **GOOD_RUN_RECORD_WITH_WORKSPACE,
    "workspace": {**GOOD_RUN_RECORD_WITH_WORKSPACE["workspace"], "baseRevision": BASE_SHA.upper()},
}

BAD_RUN_RECORD_WORKSPACE_MISSING_FIELD = {
    **GOOD_RUN_RECORD_WITH_WORKSPACE,
    "workspace": {
        k: v for k, v in GOOD_RUN_RECORD_WITH_WORKSPACE["workspace"].items() if k != "dirty"
    },
}

BAD_RUN_RECORD_WORKSPACE_BRANCH_NUMBER = {
    **GOOD_RUN_RECORD_WITH_WORKSPACE,
    "workspace": {**GOOD_RUN_RECORD_WITH_WORKSPACE["workspace"], "branch": 5},
}

BAD_RUN_RECORD_WORKSPACE_EXTRA_FIELD = {
    **GOOD_RUN_RECORD_WITH_WORKSPACE,
    "workspace": {**GOOD_RUN_RECORD_WITH_WORKSPACE["workspace"], "untrackedFiles": ["a.txt"]},
}

# `dispatchKey` is echoed or ABSENT, never null -- null would be a second spelling
# of "unkeyed" that the closed shape does not admit.
BAD_RUN_RECORD_DISPATCH_KEY_NULL = {**GOOD_RUN_RECORD_FINISHED, "dispatchKey": None}
BAD_RUN_RECORD_DISPATCH_KEY_SHORT = {**GOOD_RUN_RECORD_FINISHED, "dispatchKey": "tiny"}

GOOD_DISPATCH_RESERVATION = {
    "dispatchKey": DISPATCH_KEY,
    "requestHash": "ebaba25539396d2af99d3ff6e410f8f295d8e956380bf1818a18d65a8a98a671",
    "runId": GOOD_RUN_RECORD_WITH_WORKSPACE["id"],
    "reservedAt": "2026-09-27T10:00:00Z",
    "run": GOOD_RUN_RECORD_WITH_WORKSPACE,
}

BAD_RESERVATION_SHORT_HASH = {**GOOD_DISPATCH_RESERVATION, "requestHash": "ebaba2553939"}
BAD_RESERVATION_UPPERCASE_HASH = {
    **GOOD_DISPATCH_RESERVATION,
    "requestHash": GOOD_DISPATCH_RESERVATION["requestHash"].upper(),
}
BAD_RESERVATION_HASH_NULL = {**GOOD_DISPATCH_RESERVATION, "requestHash": None}
BAD_RESERVATION_MISSING_RUN = {
    k: v for k, v in GOOD_DISPATCH_RESERVATION.items() if k != "run"
}
BAD_RESERVATION_RUN_NOT_A_RUN_RECORD = {
    **GOOD_DISPATCH_RESERVATION,
    "run": {"id": GOOD_RUN_RECORD_WITH_WORKSPACE["id"], "repo": "plantpal"},
}
BAD_RESERVATION_EXTRA_FIELD = {**GOOD_DISPATCH_RESERVATION, "attempts": 1}

# The canonicalization, executable. `runner.dispatch-reservation.json` documents the
# exact recipe and states this hash as a worked example; recomputing it here is what
# keeps that prose from drifting away from a form a real caller can reproduce.
CANONICALIZATION_CASE = {
    "request": {"repo": "plantpal", "prompt": "do the thing", "model": "claude-sonnet-5"},
    "canonical": '{"model":"claude-sonnet-5","prompt":"do the thing","repo":"plantpal"}',
    "sha256": "ebaba25539396d2af99d3ff6e410f8f295d8e956380bf1818a18d65a8a98a671",
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


def registry() -> Registry:
    """Sibling-file `$ref` resolution (runner.dispatch-reservation -> runner.run-record).

    Each schema is registered under its `$id` AND under the `<id>.json` spelling a
    relative `"<file>.json"` `$ref` resolves to from a sibling's base URI: this repo's
    `$id`s omit the `.json` suffix while its `$ref`s carry it (`delivery.producer-result`
    -> `delivery.evidence.json` is the same pattern). The bindings' generators resolve
    by file path and never hit this; a strict `$id`-based validator does.
    """
    resources = []
    for path in SCHEMAS.glob("*.json"):
        schema = load(path.name)
        resource = Resource.from_contents(schema)
        resources.append((schema["$id"], resource))
        resources.append((schema["$id"] + ".json", resource))
    return Registry().with_resources(resources)


def expect_valid(schema, doc: dict, label: str, reg: Registry | None = None) -> None:
    validator = Draft202012Validator(schema, registry=reg) if reg else Draft202012Validator(schema)
    errors = list(validator.iter_errors(doc))
    if errors:
        raise AssertionError(f"{label}: expected valid, got errors: {errors}")
    print(f"PASS  {label}")


def expect_invalid(schema, doc: dict, label: str, reg: Registry | None = None) -> None:
    validator = Draft202012Validator(schema, registry=reg) if reg else Draft202012Validator(schema)
    errors = list(validator.iter_errors(doc))
    if not errors:
        raise AssertionError(f"{label}: expected invalid, but document passed")
    print(f"PASS  {label} (rejected: {errors[0].message})")


def canonical_request_json(request: dict) -> str:
    """The exact canonicalization `runner.dispatch-reservation.json` fixes for `requestHash`.

    Six execution-defining fields, present-only: an explicitly empty string is present
    and IS included (`"model": ""` means "no --model argument", which is a different
    request from an absent `model`); an absent field is omitted, never written as null.
    Keys sorted, no insignificant whitespace, non-ASCII left as UTF-8. All six fields
    are strings, so no number or boolean formatting is left for two languages to
    disagree about. `dispatchKey` is deliberately not part of the execution identity.
    """
    fields = ("repo", "prompt", "demandId", "model", "effort", "runtime")
    subset = {k: request[k] for k in fields if k in request}
    return json.dumps(subset, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def main() -> int:
    reg = registry()
    dispatch_schema = load("runner.dispatch-request.json")
    run_record_schema = load("runner.run-record.json")
    transcript_schema = load("runner.transcript-snapshot.json")
    reservation_schema = load("runner.dispatch-reservation.json")

    expect_valid(dispatch_schema, GOOD_DISPATCH_REQUEST, "runner.dispatch-request: correlation-token-prefixed prompt (known-good)")
    expect_valid(dispatch_schema, GOOD_DISPATCH_REQUEST_WITH_OVERRIDES, "runner.dispatch-request: model/effort/runtime overrides (known-good)")
    expect_invalid(dispatch_schema, BAD_DISPATCH_REQUEST_MISSING_PROMPT, "runner.dispatch-request: missing prompt (known-bad)")
    expect_invalid(dispatch_schema, BAD_DISPATCH_REQUEST_BAD_REPO, "runner.dispatch-request: repo not a functional name (known-bad)")

    # Keyed dispatch is additive: the same documents that were valid before still are.
    if dispatch_schema["required"] != ["repo", "prompt"]:
        raise AssertionError("runner.dispatch-request: the required list changed -- unkeyed requests must stay valid")
    expect_valid(dispatch_schema, GOOD_DISPATCH_REQUEST_KEYED, "runner.dispatch-request: keyed, Factory operation token as dispatchKey (known-good)")
    expect_invalid(dispatch_schema, BAD_DISPATCH_REQUEST_SHORT_KEY, "runner.dispatch-request: dispatchKey under 8 chars (known-bad)")
    expect_invalid(dispatch_schema, BAD_DISPATCH_REQUEST_KEY_BAD_CHARS, "runner.dispatch-request: dispatchKey outside the allowed charset (known-bad)")
    expect_invalid(dispatch_schema, BAD_DISPATCH_REQUEST_KEY_LEADING_PUNCT, "runner.dispatch-request: dispatchKey not starting alphanumeric (known-bad)")
    expect_invalid(dispatch_schema, BAD_DISPATCH_REQUEST_KEY_TOO_LONG, "runner.dispatch-request: dispatchKey over 200 chars (known-bad)")

    expect_valid(run_record_schema, GOOD_RUN_RECORD_LAUNCHED, "runner.run-record: launched, no result yet (known-good)")
    expect_valid(run_record_schema, GOOD_RUN_RECORD_FINISHED, "runner.run-record: finished with token usage (known-good)")
    expect_invalid(run_record_schema, BAD_RUN_RECORD_MISSING_REQUIRED, "runner.run-record: missing required fields (known-bad)")
    expect_invalid(run_record_schema, BAD_RUN_RECORD_BAD_STATE, "runner.run-record: state outside the real 4-value enum (known-bad)")

    expect_valid(run_record_schema, GOOD_RUN_RECORD_KEYED, "runner.run-record: dispatchKey echoed, unkeyed fields untouched (known-good)")
    expect_invalid(run_record_schema, BAD_RUN_RECORD_DISPATCH_KEY_NULL, "runner.run-record: dispatchKey null rather than absent (known-bad)")
    expect_invalid(run_record_schema, BAD_RUN_RECORD_DISPATCH_KEY_SHORT, "runner.run-record: dispatchKey outside the request pattern (known-bad)")

    expect_valid(run_record_schema, GOOD_RUN_RECORD_WITH_WORKSPACE, "runner.run-record: observed base+head workspace (known-good)")
    expect_valid(run_record_schema, GOOD_RUN_RECORD_WORKSPACE_NULL, "runner.run-record: workspace null = never observed (known-good)")
    expect_valid(run_record_schema, GOOD_RUN_RECORD_WORKSPACE_UNOBSERVED, "runner.run-record: every workspace field null, no defaults (known-good)")
    expect_valid(run_record_schema, GOOD_RUN_RECORD_WORKSPACE_ORPHAN, "runner.run-record: orphan, base observed but no post-exit observation (known-good)")
    expect_invalid(run_record_schema, BAD_RUN_RECORD_WORKSPACE_SHORT_SHA, "runner.run-record: workspace revision not a full 40-hex SHA (known-bad)")
    expect_invalid(run_record_schema, BAD_RUN_RECORD_WORKSPACE_UPPERCASE_SHA, "runner.run-record: workspace revision uppercase hex (known-bad)")
    expect_invalid(run_record_schema, BAD_RUN_RECORD_WORKSPACE_MISSING_FIELD, "runner.run-record: workspace missing dirty (known-bad)")
    expect_invalid(run_record_schema, BAD_RUN_RECORD_WORKSPACE_BRANCH_NUMBER, "runner.run-record: workspace branch not a string (known-bad)")
    expect_invalid(run_record_schema, BAD_RUN_RECORD_WORKSPACE_EXTRA_FIELD, "runner.run-record: workspace carries an unobserved extra field (known-bad)")

    expect_valid(reservation_schema, GOOD_DISPATCH_RESERVATION, "runner.dispatch-reservation: key/reservation/run lookup body (known-good)", reg)
    expect_invalid(reservation_schema, BAD_RESERVATION_SHORT_HASH, "runner.dispatch-reservation: requestHash not 64 hex (known-bad)", reg)
    expect_invalid(reservation_schema, BAD_RESERVATION_UPPERCASE_HASH, "runner.dispatch-reservation: requestHash uppercase hex (known-bad)", reg)
    expect_invalid(reservation_schema, BAD_RESERVATION_HASH_NULL, "runner.dispatch-reservation: requestHash null (known-bad)", reg)
    expect_invalid(reservation_schema, BAD_RESERVATION_MISSING_RUN, "runner.dispatch-reservation: no run bound to the key (known-bad)", reg)
    expect_invalid(reservation_schema, BAD_RESERVATION_RUN_NOT_A_RUN_RECORD, "runner.dispatch-reservation: run is not a runner.run-record (known-bad)", reg)
    expect_invalid(reservation_schema, BAD_RESERVATION_EXTRA_FIELD, "runner.dispatch-reservation: reservation carries an unmodelled field (known-bad)", reg)

    # Canonicalization conformance: the recipe the schema documents, executed, and
    # checked against the worked example stated in that same schema's prose.
    case = CANONICALIZATION_CASE
    canonical = canonical_request_json(case["request"])
    if canonical != case["canonical"]:
        raise AssertionError(f"canonicalization: canonical bytes drifted: {canonical!r} != {case['canonical']!r}")
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    if digest != case["sha256"]:
        raise AssertionError(f"canonicalization: sha256 drifted: {digest} != {case['sha256']}")
    if case["canonical"] not in reservation_schema["description"] or case["sha256"] not in reservation_schema["description"]:
        raise AssertionError("runner.dispatch-reservation: the documented worked example no longer matches the executable recipe")
    print("PASS  runner.dispatch-reservation: requestHash recipe is reproducible and matches the documented example")

    # The one place a naive canonicalizer silently diverges from this contract.
    if canonical_request_json({"repo": "plantpal", "prompt": "x", "model": ""}) == canonical_request_json(
        {"repo": "plantpal", "prompt": "x"}
    ):
        raise AssertionError("canonicalization: an explicit empty model must not hash like an absent one")
    if canonical_request_json({**case["request"], "dispatchKey": DISPATCH_KEY}) != canonical:
        raise AssertionError("canonicalization: dispatchKey must not enter the hash")
    print("PASS  runner.dispatch-reservation: absent vs empty-string field, and dispatchKey excluded")

    expect_valid(transcript_schema, GOOD_TRANSCRIPT_SNAPSHOT_IN_PROGRESS, "runner.transcript-snapshot: in-progress, result null (known-good)")
    expect_valid(transcript_schema, GOOD_TRANSCRIPT_SNAPSHOT_FINISHED, "runner.transcript-snapshot: finished with result (known-good)")
    expect_invalid(transcript_schema, BAD_TRANSCRIPT_SNAPSHOT_MISSING_FIELDS, "runner.transcript-snapshot: missing result/resultTruncated (known-bad)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
