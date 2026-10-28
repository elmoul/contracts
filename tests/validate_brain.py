"""
Schema-level validation for schemas/agent-runner/brain.*.json (the brain v1 wire shapes,
D143 / spec-agent-memory-system.md v1.0). Same pattern as validate_runner.py: validates the
JSON Schemas directly against example documents, independent of any language binding.
Run: python tests/validate_brain.py
"""
import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parent.parent
SCHEMAS = ROOT / "schemas" / "agent-runner"

NAMES = [
    "run-record", "run-bundle", "change", "note", "candidate", "functions",
    "cli-result", "repo-summary", "usage", "job", "job-request",
    "settings", "settings-update", "settings-audit-entry", "stats", "job-page",
]


def load(name: str) -> dict:
    return json.loads((SCHEMAS / f"brain.{name}.json").read_text(encoding="utf-8"))


def registry() -> Registry:
    resources = []
    for path in SCHEMAS.glob("*.json"):
        schema = json.loads(path.read_text(encoding="utf-8"))
        resource = Resource.from_contents(schema)
        resources.append((schema["$id"], resource))
        resources.append((schema["$id"] + ".json", resource))
    return Registry().with_resources(resources)


REG = registry()
SCHEMA = {n: load(n) for n in NAMES}


def errors_of(name: str, doc) -> list:
    return list(Draft202012Validator(SCHEMA[name], registry=REG).iter_errors(doc))


def ok(name: str, doc, label: str) -> None:
    errs = errors_of(name, doc)
    if errs:
        raise AssertionError(f"brain.{name}: {label}: expected valid, got {errs[0].message}")
    print(f"PASS  brain.{name}: {label}")


def bad(name: str, doc, label: str) -> None:
    errs = errors_of(name, doc)
    if not errs:
        raise AssertionError(f"brain.{name}: {label}: expected invalid, but document passed")
    print(f"PASS  brain.{name}: {label} (rejected: {errs[0].message[:90]})")


def without(doc: dict, *keys: str) -> dict:
    return {k: v for k, v in doc.items() if k not in keys}


# --- brain.cli-result ----------------------------------------------------------------
CLI_OK = {
    "ok": True, "deferred": False, "uncertain": False, "error": None,
    "model": "claude-haiku-5-5", "effort": "low", "tokens": 3120,
    "writes": [".brain/runs.jsonl", ".brain/inbox/c1.md"], "details": {"verdict": "lesson"},
}
CLI_NO_AI = {**CLI_OK, "model": None, "effort": None, "tokens": 0, "writes": [".brain/notes/a.md", ".brain/changes.jsonl", "AGENT.md"], "details": {}}
CLI_DEFERRED = {**CLI_OK, "ok": False, "deferred": True, "tokens": 0, "writes": [], "details": {"resetAt": "2026-10-27T09:00:00Z"}}
CLI_FAILED = {**CLI_OK, "ok": False, "error": "model claude-x is not in the gateway catalogue", "writes": []}
CLI_UNCERTAIN = {**CLI_OK, "ok": False, "uncertain": True, "error": "gateway timed out after the response may have been produced"}

# --- brain.run-record ----------------------------------------------------------------
RUN_LINE = {
    "runId": "run-9f0e2b1a", "kind": "dispatched", "at": "2026-10-27T09:14:00Z",
    "model": "claude-sonnet-5-5", "effort": "medium", "runtime": "claude",
    "task": "Fulfil demand x", "outcome": "done", "triage": "lesson",
    "harvested": True, "candidates": 2, "brainTokens": 3120,
}
RUN_LINE_MIN = {"runId": "sess-1", "kind": "interactive", "at": "2026-10-27T09:14:00Z", "task": "t", "outcome": "partial", "triage": "deferred"}
JOB_LINE = {"runId": "run-9f0e2b1a", "kind": "brain-job", "job": "triage", "result": CLI_OK}

# --- brain.note / brain.candidate ----------------------------------------------------
NOTE = {
    "slug": "windows-maven-child-jvm-holds-port",
    "title": "Stopping a Maven task on Windows can leave a child JVM holding the port",
    "type": "gotcha", "status": "active", "created": "2026-10-27", "updated": "2026-10-27",
    "provenance": {"runs": ["run-1"], "files": ["pom.xml"], "decisions": ["D131"]},
    "body": "Kill the child JVM directly.",
}
CANDIDATE = {
    "id": "2026-10-27-0001", "slug": "x-fact", "title": "A fact", "type": "fact",
    "created": "2026-10-27", "updated": "2026-10-27", "provenance": {"runs": ["run-1"]},
    "source": "harvest", "repeat_of": None, "body": "Body.",
}

# --- brain.job -----------------------------------------------------------------------
JOB = {
    "id": "job-1", "repo": "agent-runner", "command": "triage", "runId": "run-9f0e2b1a",
    "state": "done", "attempts": 1, "nextAttemptAt": None, "model": None, "effort": None,
    "result": CLI_OK, "createdAt": "2026-10-27T09:15:00Z", "updatedAt": "2026-10-27T09:15:20Z",
}
JOB_DEFERRED = {**JOB, "state": "deferred", "attempts": 3, "nextAttemptAt": "2026-10-27T10:15:00Z", "result": CLI_DEFERRED}
JOB_QUEUED = {**JOB, "command": "curate", "runId": None, "state": "queued", "attempts": 0, "model": "claude-opus-5-5", "effort": "high", "result": None}

FUNCTIONS = {
    "version": 1,
    "functions": {
        "triage": {"model": "claude-haiku-5-5", "effort": "low", "reason": "many calls; yes/no plus a category on ~3k tokens"},
        "harvest": {"model": "claude-sonnet-5-5", "effort": "medium", "reason": "extraction quality at moderate volume on ~20k tokens"},
        "curate": {"model": "claude-opus-5-5", "effort": "high", "reason": "judgment: merge, contradict, retire, write the brief; few calls"},
        "seed": {"model": "claude-opus-5-5", "effort": "high", "reason": "one time per repo"},
    },
}

SUMMARY = {
    "repo": "contracts", "migrated": True, "briefUpdatedAt": "2026-10-27T09:00:00Z", "briefTokens": 2400,
    "notes": 12, "inbox": 2,
    "lastRun": {"runId": "run-1", "at": "2026-10-27T09:14:00Z", "outcome": "done", "triage": "none"},
    "deferredJobs": 1, "lastJob": JOB_DEFERRED,
}
SUMMARY_UNMIGRATED = {
    "repo": "ai-gateway", "migrated": False, "briefUpdatedAt": None, "briefTokens": None,
    "notes": 0, "inbox": 0, "lastRun": None, "deferredJobs": 0, "lastJob": None,
}


# --- settings, stats, job page (D143 addendum 2026-10-27) -----------------------------
AUDIT = {"at": "2026-10-27T11:00:00Z", "actor": "owner", "field": "functions.curate.model", "from": None, "to": "claude-opus-5-5"}
FN = {"model": "claude-haiku-5-5", "effort": "low", "default": {"model": "claude-haiku-5-5", "effort": "low"}}
SETTINGS = {
    "functions": {"triage": FN, "harvest": FN, "curate": FN, "seed": FN},
    "triageOnRunExit": True, "autoCurate": False,
    "updatedAt": "2026-10-27T11:00:00Z", "updatedBy": "owner",
}
SETTINGS_NEVER_SAVED = {**SETTINGS, "updatedAt": None, "updatedBy": None}
ROW = {
    "repo": "contracts", "migrated": True, "notes": 12, "pinned": 2, "inbox": 1, "briefTokens": 2400,
    "briefUpdatedAt": "2026-10-27T09:00:00Z", "briefOverBudget": False, "briefStale": False,
    "runsTriaged": 5, "lessonsFound": 2, "repeatIncidents": 0, "curations": 1, "deferredJobs": 0, "failedJobs": 0,
}
ROW_UNMIGRATED = {**ROW, "repo": "ai-gateway", "migrated": False, "notes": 0, "pinned": 0, "inbox": 0, "briefTokens": None,
                  "briefUpdatedAt": None, "runsTriaged": 0, "lessonsFound": 0, "curations": 0}
STATS = {
    "generatedAt": "2026-10-27T12:00:00Z", "windowDays": 7,
    "totals": {"repos": 2, "migrated": 1, "notes": 12, "pinned": 2, "inbox": 1, "briefsOverBudget": 0, "briefsStale": 0,
               "runsTriaged": 5, "lessonsFound": 2, "repeatIncidents": 0, "curations": 1},
    "jobs": {"byState": {"queued": 0, "running": 1, "done": 9, "deferred": 2, "failed": 1}},
    "tokens": {"ceiling": 1000000, "days": [{"date": "2026-10-27", "tokens": 41200}]},
    "repos": [ROW, ROW_UNMIGRATED],
}
FILTERS = {"repo": None, "command": None, "state": None, "from": None, "to": None}
PAGE = {"items": [JOB, JOB_DEFERRED], "total": 2, "page": 1, "pageSize": 25, "filters": FILTERS}


def main() -> int:
    # every schema is itself a valid 2020-12 schema and a closed object (or a oneOf of closed objects)
    for n, s in SCHEMA.items():
        Draft202012Validator.check_schema(s)
        branches = s["oneOf"] if "oneOf" in s else [s]
        for b in branches:
            if b.get("additionalProperties") is not False:
                raise AssertionError(f"brain.{n}: top-level object is not closed")
    print("PASS  all 16 brain.* schemas are valid and closed")

    # brain.cli-result
    ok("cli-result", CLI_OK, "ok result (known-good)")
    ok("cli-result", CLI_NO_AI, "no AI call: model/effort null, tokens 0 (known-good)")
    ok("cli-result", CLI_DEFERRED, "deferred (known-good)")
    ok("cli-result", CLI_FAILED, "failed with error (known-good)")
    ok("cli-result", CLI_UNCERTAIN, "uncertain (known-good)")
    for k in CLI_OK:
        bad("cli-result", without(CLI_OK, k), f"missing {k}")
    bad("cli-result", {**CLI_OK, "extra": 1}, "unmodelled member")
    bad("cli-result", {**CLI_OK, "deferred": True}, "ok and deferred together")
    bad("cli-result", {**CLI_OK, "uncertain": True}, "ok and uncertain together")
    bad("cli-result", {**CLI_OK, "error": "boom"}, "ok with an error")
    bad("cli-result", {**CLI_DEFERRED, "ok": True}, "deferred but ok")
    bad("cli-result", {**CLI_FAILED, "error": None}, "failure without an error")
    bad("cli-result", {**CLI_FAILED, "error": ""}, "failure with an empty error")
    bad("cli-result", {**CLI_OK, "effort": "max"}, "effort outside the CLI vocabulary")
    bad("cli-result", {**CLI_OK, "tokens": -1}, "negative tokens")
    bad("cli-result", {**CLI_OK, "tokens": 1.5}, "fractional tokens")
    bad("cli-result", {**CLI_OK, "writes": "AGENT.md"}, "writes not a list")
    for p in ["/etc/passwd", "C:/x", "C:\\x", "..\\x", "a/../b", "../a", "a\\b", ""]:
        bad("cli-result", {**CLI_OK, "writes": [p]}, f"write path {p!r}")
    bad("cli-result", {**CLI_OK, "details": None}, "details null")
    bad("cli-result", {**CLI_OK, "tokensIn": 1}, "demand-text member tokensIn is not in the closed shape")

    # brain.run-record
    ok("run-record", RUN_LINE, "dispatched run line (spec section 2.4 example)")
    ok("run-record", RUN_LINE_MIN, "minimal interactive line, model/effort/runtime absent")
    ok("run-record", JOB_LINE, "brain-job follow-up line")
    for k in ["runId", "kind", "at", "task", "outcome", "triage"]:
        bad("run-record", without(RUN_LINE, k), f"run line missing {k}")
    for k in ["runId", "kind", "job", "result"]:
        bad("run-record", without(JOB_LINE, k), f"job line missing {k}")
    bad("run-record", {**RUN_LINE, "kind": "brain-job"}, "run line claiming kind brain-job")
    bad("run-record", {**JOB_LINE, "kind": "dispatched"}, "job line claiming kind dispatched")
    bad("run-record", {**RUN_LINE, "outcome": "queued"}, "outcome outside the enum")
    bad("run-record", {**RUN_LINE, "triage": "yes"}, "triage outside the enum")
    bad("run-record", {**RUN_LINE, "task": "x" * 201}, "task over 200 chars")
    ok("run-record", {**RUN_LINE, "task": "x" * 200}, "task of exactly 200 chars")
    bad("run-record", {**RUN_LINE, "model": None}, "model null rather than absent")
    bad("run-record", {**RUN_LINE, "model": ""}, "model empty")
    bad("run-record", {**RUN_LINE, "brainTokens": -5}, "negative brainTokens")
    bad("run-record", {**RUN_LINE, "candidates": "2"}, "candidates not an integer")
    bad("run-record", {**RUN_LINE, "extra": 1}, "run line with an unmodelled member")
    bad("run-record", {**JOB_LINE, "job": "curate"}, "job line for a job that is not retried per run")
    bad("run-record", {**JOB_LINE, "result": {"ok": True}}, "job line result is not a cli-result")
    bad("run-record", {**JOB_LINE, "extra": 1}, "job line with an unmodelled member")
    bad("run-record", {**RUN_LINE, **{"job": "triage", "result": CLI_OK}}, "run line mixed with job-line members")

    # brain.run-bundle
    BUNDLE = {
        "runId": "run-1", "repo": "contracts", "kind": "dispatched", "task": "t", "model": "claude-sonnet-5-5",
        "effort": "medium", "runtime": "claude", "outcome": "done", "finalAnswer": "Done.",
        "errorLines": ["E: boom"], "diffStat": " 1 file changed", "transcriptPath": "/var/agent-runner/transcripts/1.jsonl",
    }
    ok("run-bundle", BUNDLE, "dispatched bundle (known-good)")
    ok("run-bundle", {**without(BUNDLE, "model", "effort", "runtime"), "kind": "interactive", "errorLines": [], "diffStat": "", "transcriptPath": None}, "interactive: no transcript, no model (known-good)")
    for k in ["runId", "repo", "kind", "task", "outcome", "finalAnswer", "errorLines", "diffStat", "transcriptPath"]:
        bad("run-bundle", without(BUNDLE, k), f"missing {k}")
    bad("run-bundle", {**BUNDLE, "repo": "Not A Repo"}, "bad repo name")
    bad("run-bundle", {**BUNDLE, "kind": "brain-job"}, "kind brain-job")
    bad("run-bundle", {**BUNDLE, "errorLines": "E: boom"}, "errorLines not a list")
    bad("run-bundle", {**BUNDLE, "transcriptPath": ""}, "empty transcriptPath")
    bad("run-bundle", {**BUNDLE, "extra": 1}, "unmodelled member")

    # brain.change
    CHANGE = {"at": "2026-10-27T09:20:00Z", "actor": "curate", "op": "merge", "slug": "a-note", "fromRuns": ["run-1", "run-2"], "diff": "--- a\n+++ b\n"}
    ok("change", CHANGE, "curate merge with diff (known-good)")
    ok("change", {**CHANGE, "actor": "owner", "op": "pin", "fromRuns": [], "diff": None}, "owner pin, no diff (known-good)")
    ok("change", {**CHANGE, "op": "brief", "slug": None}, "brief change, no slug (known-good)")
    for k in CHANGE:
        bad("change", without(CHANGE, k), f"missing {k}")
    bad("change", {**CHANGE, "actor": "agent"}, "actor outside the enum")
    bad("change", {**CHANGE, "op": "delete"}, "op outside the enum")
    bad("change", {**CHANGE, "slug": "Bad Slug"}, "slug not a slug")
    bad("change", {**CHANGE, "fromRuns": None}, "fromRuns null")
    bad("change", {**CHANGE, "extra": 1}, "unmodelled member")

    # brain.note
    ok("note", NOTE, "active note (spec section 2.2 example, known-good)")
    ok("note", {**NOTE, "status": "pinned", "provenance": {"runs": []}, "raw": "---\nslug: x\n---\nBody"}, "pinned, empty provenance, raw (known-good)")
    ok("note", {**NOTE, "status": "retired", "type": "procedure"}, "retired procedure (known-good)")
    for k in ["slug", "title", "type", "status", "created", "updated", "provenance", "body"]:
        bad("note", without(NOTE, k), f"missing {k}")
    bad("note", {**NOTE, "status": "archived"}, "status outside the enum")
    bad("note", {**NOTE, "type": "lesson"}, "type outside the enum")
    bad("note", {**NOTE, "slug": "Not_A_Slug"}, "slug not kebab-case")
    bad("note", {**NOTE, "slug": "-lead"}, "slug with a leading hyphen")
    bad("note", {**NOTE, "created": "27/10/2026"}, "created not a date")
    bad("note", {**NOTE, "provenance": {"files": ["a"]}}, "provenance without runs")
    bad("note", {**NOTE, "provenance": {"runs": [], "extra": 1}}, "provenance with an unmodelled member")
    bad("note", {**NOTE, "provenance": {"runs": [], "decisions": ["131"]}}, "decision not a D-number")
    bad("note", {**NOTE, "body": ""}, "empty body")
    bad("note", {**NOTE, "pinned": True}, "demand-text member pinned (status carries it)")

    # brain.candidate
    ok("candidate", CANDIDATE, "harvest candidate (known-good)")
    ok("candidate", {**CANDIDATE, "source": "session-close", "repeat_of": "windows-maven-child-jvm-holds-port", "status": "active"}, "repeat of a note, with status (known-good)")
    for k in ["id", "slug", "title", "type", "created", "updated", "provenance", "source", "repeat_of", "body"]:
        bad("candidate", without(CANDIDATE, k), f"missing {k}")
    bad("candidate", {**CANDIDATE, "source": "curate"}, "source outside the enum")
    bad("candidate", {**CANDIDATE, "repeat_of": "Not A Slug"}, "repeat_of not a slug")
    bad("candidate", {**CANDIDATE, "id": "../x"}, "id with a path separator")
    bad("candidate", {**CANDIDATE, "repeatOf": None}, "camelCase repeatOf is not the spec spelling")

    # brain.functions
    ok("functions", FUNCTIONS, "spec section 3 table (known-good)")
    for k in ["triage", "harvest", "curate", "seed"]:
        bad("functions", {**FUNCTIONS, "functions": without(FUNCTIONS["functions"], k)}, f"function {k} missing")
    SPEC_FN = {"model": "claude-sonnet-5-5", "effort": "medium", "reason": "spec-sync"}
    ok("functions", {**FUNCTIONS, "functions": {**FUNCTIONS["functions"], "spec-sync": SPEC_FN, "spec-seed": {**SPEC_FN, "model": "claude-opus-5-5", "effort": "high"}}}, "six-row table (D144)")
    bad("functions", {**FUNCTIONS, "functions": {**FUNCTIONS["functions"], "spec-sync": {"model": "m", "effort": "max", "reason": "x"}}}, "spec-sync effort outside the vocabulary")
    bad("functions", {**FUNCTIONS, "functions": {**FUNCTIONS["functions"], "spec-seed": {"model": "m", "effort": "high"}}}, "spec-seed without reason")
    bad("functions", without(FUNCTIONS, "version"), "version missing")
    bad("functions", {**FUNCTIONS, "functions": {**FUNCTIONS["functions"], "extra": FUNCTIONS["functions"]["seed"]}}, "unknown function")
    bad("functions", {**FUNCTIONS, "functions": {**FUNCTIONS["functions"], "seed": {"model": "m", "effort": "high", "why": "x"}}}, "demand-text `why` instead of `reason`")
    bad("functions", {**FUNCTIONS, "functions": {**FUNCTIONS["functions"], "seed": {"model": "m", "effort": "max", "reason": "x"}}}, "effort outside the vocabulary")
    bad("functions", {**FUNCTIONS, "functions": {**FUNCTIONS["functions"], "seed": {"model": "", "effort": "high", "reason": "x"}}}, "empty model")
    bad("functions", {**FUNCTIONS, "version": 0}, "version 0")

    # brain.job / brain.job-request
    ok("job", JOB, "done job with result (known-good)")
    ok("job", JOB_DEFERRED, "deferred job with nextAttemptAt (known-good)")
    ok("job", JOB_QUEUED, "queued owner curate with override, no run (known-good)")
    for k in JOB:
        bad("job", without(JOB, k), f"missing {k}")
    bad("job", {**JOB, "command": "record-run"}, "command outside the enum")
    bad("job", {**JOB, "state": "failed-permanently"}, "state outside the enum")
    bad("job", {**JOB, "attempts": -1}, "negative attempts")
    bad("job", {**JOB, "result": {"ok": True}}, "result is not a cli-result")
    bad("job", {**JOB, "repo": "Bad Repo"}, "bad repo")
    bad("job", {**JOB, "extra": 1}, "unmodelled member")
    ok("job-request", {}, "empty body (known-good)")
    ok("job-request", {"model": "claude-opus-5-5", "effort": "xhigh"}, "override (known-good)")
    bad("job-request", {"command": "curate"}, "command in the body (the route carries it)")
    bad("job-request", {"effort": "extreme"}, "effort outside the vocabulary")
    bad("job-request", {"model": ""}, "empty model")
    bad("job-request", {"model": None}, "model null")

    # brain.repo-summary
    ok("repo-summary", SUMMARY, "migrated repo (known-good)")
    ok("repo-summary", SUMMARY_UNMIGRATED, "unmigrated repo, nulls (known-good)")
    for k in SUMMARY:
        bad("repo-summary", without(SUMMARY, k), f"missing {k}")
    bad("repo-summary", {**SUMMARY, "migrated": "v1"}, "migrated as the demand-text enum rather than a boolean")
    bad("repo-summary", {**SUMMARY, "notes": -1}, "negative notes")
    bad("repo-summary", {**SUMMARY, "lastRun": {"runId": "r"}}, "lastRun incomplete")
    bad("repo-summary", {**SUMMARY, "lastJob": {"id": "j"}}, "lastJob is not a brain.job")
    ok("repo-summary", {**SUMMARY, "v06Leftovers": ["derived", "events"]}, "v06Leftovers list")
    ok("repo-summary", {**SUMMARY, "v06Leftovers": []}, "v06Leftovers empty")
    bad("repo-summary", {**SUMMARY, "v06Leftovers": "derived"}, "v06Leftovers not an array")
    bad("repo-summary", {**SUMMARY, "v06Leftovers": [1]}, "v06Leftovers non-string element")
    bad("repo-summary", {**SUMMARY, "v06Leftovers": [""]}, "v06Leftovers empty name")
    bad("repo-summary", {**SUMMARY, "v06Leftovers": None}, "v06Leftovers null")
    bad("repo-summary", {**SUMMARY, "extra": 1}, "unmodelled member")

    # brain.usage
    ok("usage", {"ceiling": 1000000, "days": [{"date": "2026-10-26", "tokens": 0}, {"date": "2026-10-27", "tokens": 41200}]}, "two days (known-good)")
    ok("usage", {"ceiling": None, "days": []}, "unknown ceiling, no days (known-good)")
    bad("usage", {"days": []}, "ceiling missing")
    bad("usage", {"ceiling": 0, "days": []}, "ceiling 0")
    bad("usage", {"ceiling": 1000000, "days": [{"date": "26-10-2026", "tokens": 1}]}, "bad day")
    bad("usage", {"ceiling": 1000000, "days": [{"date": "2026-10-26", "tokens": -1}]}, "negative tokens")
    bad("usage", {"ceiling": 1000000, "days": [{"date": "2026-10-26", "tokens": 1, "calls": 2}]}, "unmodelled day member")
    # brain.settings
    ok("settings", SETTINGS, "saved record (known-good)")
    ok("settings", SETTINGS_NEVER_SAVED, "never-saved record, updatedAt/updatedBy null")
    ok("settings", {**SETTINGS, "audit": [AUDIT]}, "with audit trail")
    bad("settings", without(SETTINGS, "autoCurate"), "autoCurate missing")
    bad("settings", without(SETTINGS, "triageOnRunExit"), "triageOnRunExit missing")
    bad("settings", {**SETTINGS, "functions": without(SETTINGS["functions"], "seed")}, "a function missing")
    bad("settings", {**SETTINGS, "functions": {**SETTINGS["functions"], "triage": without(FN, "default")}}, "shipped default missing")
    bad("settings", {**SETTINGS, "functions": {**SETTINGS["functions"], "triage": {**FN, "effort": "max"}}}, "effort outside the vocabulary")
    bad("settings", {**SETTINGS, "functions": {**SETTINGS["functions"], "triage": {**FN, "model": ""}}}, "empty model")
    bad("settings", {**SETTINGS, "functions": {**SETTINGS["functions"], "repoX": FN}}, "a per-repo or extra function row")
    bad("settings", {**SETTINGS, "autoCurate": "yes"}, "switch not boolean")
    bad("settings", {**SETTINGS, "audit": [{"at": "x"}]}, "audit entry incomplete")
    bad("settings", {**SETTINGS, "extra": 1}, "unmodelled member")

    # brain.settings-update
    ok("settings-update", {"autoCurate": True}, "one switch")
    ok("settings-update", {"functions": {"curate": {"model": "claude-opus-5-5"}}}, "one function member")
    ok("settings-update", {"functions": {"triage": {"model": None, "effort": None}}, "triageOnRunExit": False}, "reset to default with null")
    bad("settings-update", {}, "empty update")
    bad("settings-update", {"functions": {}}, "empty functions")
    bad("settings-update", {"functions": {"triage": {}}}, "empty function entry")
    bad("settings-update", {"functions": {"triage": {"effort": "max"}}}, "effort outside the vocabulary")
    bad("settings-update", {"functions": {"triage": {"model": ""}}}, "empty model")
    bad("settings-update", {"updatedBy": "owner"}, "server-owned member sent")
    bad("settings-update", {"autoCurate": None}, "switch cannot be null")

    # brain.settings-audit-entry
    ok("settings-audit-entry", AUDIT, "model change (known-good)")
    ok("settings-audit-entry", {**AUDIT, "field": "autoCurate", "from": True, "to": False}, "switch change")
    bad("settings-audit-entry", {**AUDIT, "field": "functions.curate.reason"}, "field outside the editable members")
    bad("settings-audit-entry", {**AUDIT, "field": "functions.other.model"}, "unknown function")
    bad("settings-audit-entry", without(AUDIT, "actor"), "actor missing")
    bad("settings-audit-entry", {**AUDIT, "to": 3}, "to not string/boolean/null")
    bad("settings-audit-entry", {**AUDIT, "extra": 1}, "unmodelled member")

    # brain.stats
    ok("stats", STATS, "two repos, one unmigrated (known-good)")
    ok("stats", {**STATS, "repos": [], "tokens": {"ceiling": None, "days": []}}, "empty fleet, unknown ceiling")
    bad("stats", without(STATS, "tokens"), "tokens missing")
    bad("stats", without(STATS, "jobs"), "jobs missing")
    bad("stats", {**STATS, "windowDays": 0}, "windowDays 0")
    bad("stats", {**STATS, "totals": without(STATS["totals"], "repeatIncidents")}, "a total missing")
    bad("stats", {**STATS, "totals": {**STATS["totals"], "notes": -1}}, "negative total")
    bad("stats", {**STATS, "jobs": {"byState": without(STATS["jobs"]["byState"], "failed")}}, "failed count missing")
    bad("stats", {**STATS, "jobs": {"byState": {**STATS["jobs"]["byState"], "paused": 1}}}, "unknown job state")
    bad("stats", {**STATS, "tokens": {"ceiling": 0, "days": []}}, "tokens is a brain.usage (ceiling 0)")
    bad("stats", {**STATS, "repos": [without(ROW, "briefStale")]}, "repo row incomplete")
    bad("stats", {**STATS, "repos": [{**ROW, "briefOverBudget": "no"}]}, "repo flag not boolean")
    bad("stats", {**STATS, "extra": 1}, "unmodelled member")

    # brain.job-page
    ok("job-page", PAGE, "unfiltered page (known-good)")
    ok("job-page", {**PAGE, "items": [], "total": 0}, "empty page")
    ok("job-page", {**PAGE, "filters": {"repo": "contracts", "command": "triage", "state": "deferred",
                                        "from": "2026-10-26T00:00:00Z", "to": "2026-10-27T00:00:00Z"}}, "all filters applied")
    bad("job-page", {**PAGE, "items": [{"id": "j"}]}, "item is not a brain.job")
    bad("job-page", {**PAGE, "page": 0}, "page 0")
    bad("job-page", {**PAGE, "pageSize": 0}, "pageSize 0")
    bad("job-page", {**PAGE, "total": -1}, "negative total")
    bad("job-page", without(PAGE, "filters"), "filters missing")
    bad("job-page", {**PAGE, "filters": without(FILTERS, "to")}, "a filter missing")
    bad("job-page", {**PAGE, "filters": {**FILTERS, "state": "paused"}}, "unknown state filter")
    bad("job-page", {**PAGE, "filters": {**FILTERS, "command": "build"}}, "unknown command filter")
    bad("job-page", {**PAGE, "extra": 1}, "unmodelled member")

    return 0


if __name__ == "__main__":
    sys.exit(main())
