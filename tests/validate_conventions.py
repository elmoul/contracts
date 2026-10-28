"""
Schema-level validation for schemas/conventions/*.json and schemas/spec/*.json (D144: fleet
conventions compliance and living-spec status), plus the spec-sync / spec-seed brain job
commands. Same pattern as validate_brain.py: JSON Schemas against example documents,
independent of any language binding.
Run: python tests/validate_conventions.py
"""
import json
from pathlib import Path

from jsonschema import Draft202012Validator
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parent.parent
SCHEMAS = ROOT / "schemas"

NAMES = {
    "rule": "conventions/conventions.rule.json",
    "finding": "conventions/conventions.finding.json",
    "repo-result": "conventions/conventions.repo-result.json",
    "run": "conventions/conventions.run.json",
    "candidate": "conventions/conventions.candidate.json",
    "conflict": "conventions/conventions.conflict.json",
    "status": "spec/spec.status.json",
    "drift-item": "spec/spec.drift-item.json",
    "brain-job": "agent-runner/brain.job.json",
    "brain-job-page": "agent-runner/brain.job-page.json",
}


def registry() -> Registry:
    resources = []
    for path in SCHEMAS.glob("*/*.json"):
        schema = json.loads(path.read_text(encoding="utf-8"))
        if "$id" not in schema:
            continue
        resource = Resource.from_contents(schema)
        resources.append((schema["$id"], resource))
        resources.append((schema["$id"] + ".json", resource))
    return Registry().with_resources(resources)


REG = registry()
SCHEMA = {n: json.loads((SCHEMAS / p).read_text(encoding="utf-8")) for n, p in NAMES.items()}


def errors_of(name: str, doc) -> list:
    return list(Draft202012Validator(SCHEMA[name], registry=REG).iter_errors(doc))


def ok(name: str, doc, label: str) -> None:
    errs = errors_of(name, doc)
    if errs:
        raise AssertionError(f"{name}: {label}: expected valid, got {errs[0].message}")
    print(f"PASS  {name}: {label}")


def bad(name: str, doc, label: str) -> None:
    errs = errors_of(name, doc)
    if not errs:
        raise AssertionError(f"{name}: {label}: expected invalid, but document passed")
    print(f"PASS  {name}: {label} (rejected: {errs[0].message[:90]})")


def without(doc: dict, *keys: str) -> dict:
    return {k: v for k, v in doc.items() if k not in keys}


# --- conventions.rule ----------------------------------------------------------------
RULE = {
    "id": "loopback-only-ports", "category": "runtime-posture",
    "rule": "Every published container port binds 127.0.0.1, never 0.0.0.0.",
    "applies_to": {"has_file": ["docker-compose.yml"]},
    "source": ["D040"], "amended_by": ["D120"], "enforced_by": "check:loopback-ports",
    "severity": "fail", "exceptions": [{"path": "launcher/tailnet.*", "reason": "D120 tailnet listener"}],
    "status": "active", "as_of": "2026-10-27",
}
ok("rule", RULE, "catalog entry")
ok("rule", {**RULE, "applies_to": {"all": True}, "amended_by": [], "exceptions": [], "enforced_by": "none", "severity": "warn"}, "all/none/warn, no exceptions")
ok("rule", {**RULE, "applies_to": {"kind": ["runtime"], "lang": ["java"], "lite": False}, "enforced_by": "hook"}, "kind+lang+lite scope")
bad("rule", without(RULE, "source"), "missing source")
bad("rule", {**RULE, "source": []}, "empty source (a rule needs a decision)")
bad("rule", {**RULE, "rule": "x" * 301}, "rule over 300 characters")
bad("rule", {**RULE, "applies_to": {}}, "empty applies_to")
bad("rule", {**RULE, "applies_to": {"colour": ["red"]}}, "unknown applies_to member")
bad("rule", {**RULE, "enforced_by": "check:"}, "enforced_by check without id")
bad("rule", {**RULE, "enforced_by": "manual"}, "enforced_by outside the vocabulary")
bad("rule", {**RULE, "severity": "info"}, "severity outside fail|warn")
bad("rule", {**RULE, "extra": 1}, "unknown member")

# --- conventions.finding / repo-result / run -----------------------------------------
FINDING = {"checkId": "loopback-ports", "ruleId": "loopback-only-ports", "status": "fail",
           "message": "port 8080 binds 0.0.0.0", "file": "docker-compose.yml", "line": 12}
FINDING_REPO = {"checkId": "readme-present", "ruleId": None, "status": "pass", "message": "ok", "file": None, "line": None}
ok("finding", FINDING, "failing finding with file:line")
ok("finding", FINDING_REPO, "repo-level finding, no rule")
for st in ("pass", "warn", "fail", "unverified", "skipped"):
    ok("finding", {**FINDING, "status": st}, f"status {st}")
bad("finding", {**FINDING, "status": "error"}, "status outside the vocabulary")
bad("finding", without(FINDING, "ruleId"), "missing ruleId (null is required, not omission)")
bad("finding", {**FINDING, "line": 0}, "line 0")

REPO_RESULT = {"repo": "contracts", "sha": "8f5681e", "result": "fail", "checks": [FINDING, FINDING_REPO]}
ok("repo-result", REPO_RESULT, "failing repo")
ok("repo-result", {"repo": "theme-x", "sha": None, "result": "skipped", "checks": []}, "skipped repo, no sha")
bad("repo-result", {**REPO_RESULT, "result": "warn"}, "result outside pass|fail|skipped")
bad("repo-result", {**REPO_RESULT, "sha": "XYZ"}, "sha not hex")
bad("repo-result", {**REPO_RESULT, "checks": [{**FINDING, "status": "bogus"}]}, "invalid nested finding")

RUN = {"id": "conv-run-1", "startedAt": "2026-10-28T02:00:00Z", "finishedAt": "2026-10-28T02:04:10Z",
       "validatorSource": "a1b2c3d", "catalogHash": "sha256:9f86d081", "trigger": "nightly", "repos": [REPO_RESULT]}
ok("run", RUN, "nightly run")
ok("run", {**RUN, "finishedAt": None, "trigger": "manual", "repos": []}, "manual run in progress")
ok("run", {**RUN, "trigger": "landing"}, "landing trigger")
bad("run", {**RUN, "trigger": "weekly"}, "trigger outside the vocabulary")
bad("run", without(RUN, "catalogHash"), "missing catalogHash")
bad("run", {**RUN, "repos": [{**REPO_RESULT, "repo": "Bad Name"}]}, "invalid nested repo name")

# --- conventions.candidate / conflict ------------------------------------------------
CAND = {"id": "cand-17", "rule": "Run git tag before choosing a release version.",
        "evidence": ["contracts note check-tags-before-versioning", "control-plane note x"],
        "status": "proposed", "decidedAt": None, "reason": None}
ok("candidate", CAND, "proposed")
ok("candidate", {**CAND, "status": "rejected", "decidedAt": "2026-10-28T09:00:00Z", "reason": "repo-local"}, "rejected with reason")
bad("candidate", {**CAND, "status": "pending"}, "status outside the vocabulary")
bad("candidate", {**CAND, "evidence": []}, "no evidence")
bad("candidate", without(CAND, "reason"), "missing reason")

CONFLICT = {"id": "c-04", "summary": "README says lite apps skip CI; conventions says required.", "status": "open", "source": "proposal 3.4"}
ok("conflict", CONFLICT, "open conflict")
ok("conflict", {**CONFLICT, "status": "ruled"}, "ruled conflict")
bad("conflict", {**CONFLICT, "status": "closed"}, "status outside open|ruled")
bad("conflict", without(CONFLICT, "source"), "missing source")

# --- spec.drift-item / spec.status ---------------------------------------------------
DRIFT = {"id": "d-1", "kind": "code-vs-contract", "summary": "Route /x exists but the contract forbids it.",
         "file": "src/main/java/X.java", "line": 42, "contractSection": "3. Boundaries"}
ok("drift-item", DRIFT, "code-vs-contract with location")
for k in ("planned-now-built", "fact-mismatch"):
    ok("drift-item", {**DRIFT, "kind": k, "file": None, "line": None, "contractSection": None}, f"{k} without location")
bad("drift-item", {**DRIFT, "kind": "stale"}, "kind outside the vocabulary")
bad("drift-item", without(DRIFT, "contractSection"), "missing contractSection")

JOB = {"id": "job-9", "repo": "agent-runner", "command": "spec-sync", "runId": None, "state": "queued", "attempts": 0,
       "nextAttemptAt": None, "model": None, "effort": None, "result": None,
       "createdAt": "2026-10-28T02:00:00Z", "updatedAt": "2026-10-28T02:00:00Z"}
STATUS = {"hexagon": "agent-runner", "kind": "runtime", "specPath": "spec-agent-runner.md", "specVersion": "7",
          "contractAsOf": "2026-10-27", "stateAsOf": "2026-10-27", "verifiedAgainst": "8f5681e (contracts v0.65.0)",
          "commitsSince": 4, "driftCount": 2, "openQuestions": 1, "reviewWindowDays": 90, "due": False,
          "lastJob": JOB, "v2": True}
STATUS_V1 = {**STATUS, "hexagon": "ai-gateway", "specVersion": None, "contractAsOf": None, "stateAsOf": None,
             "verifiedAgainst": None, "commitsSince": None, "driftCount": 0, "due": True, "lastJob": None, "v2": False}
ok("status", STATUS, "v2 spec with a spec-sync job")
ok("status", STATUS_V1, "v1 spec, no v2 fields")
for k in ("runtime", "buildtime", "app", "capability"):
    ok("status", {**STATUS, "kind": k}, f"kind {k}")
bad("status", {**STATUS, "kind": "service"}, "kind outside the vocabulary")
bad("status", {**STATUS, "driftCount": -1}, "negative driftCount")
bad("status", {**STATUS, "reviewWindowDays": 0}, "reviewWindowDays 0")
bad("status", without(STATUS, "v2"), "missing v2")
bad("status", {**STATUS, "lastJob": {**JOB, "state": "weird"}}, "invalid nested lastJob")

# --- brain job command enum: spec-sync and spec-seed (additive) -----------------------
for cmd in ("spec-sync", "spec-seed", "triage", "harvest", "curate", "seed", "migrate", "note-action"):
    ok("brain-job", {**JOB, "command": cmd}, f"job command {cmd}")
bad("brain-job", {**JOB, "command": "spec"}, "job command 'spec' (only the two modes)")
PAGE = {"items": [JOB], "total": 1, "page": 1, "pageSize": 50,
        "filters": {"repo": None, "command": "spec-seed", "state": None, "from": None, "to": None}}
ok("brain-job-page", PAGE, "page filtered by spec-seed")
ok("brain-job-page", {**PAGE, "filters": {**PAGE["filters"], "command": "spec-sync"}}, "page filtered by spec-sync")
bad("brain-job-page", {**PAGE, "filters": {**PAGE["filters"], "command": "spec"}}, "page filter 'spec'")

print("All D144 conventions/spec checks passed.")
