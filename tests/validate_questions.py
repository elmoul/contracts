"""
Schema-level validation for schemas/agent-runner/questions.*.json (the owner-questions inbox:
GET /questions row, PUT draft body, POST /questions/send result).
Run: python tests/validate_questions.py
"""
import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

SCHEMAS = Path(__file__).resolve().parent.parent / "schemas" / "agent-runner"
SCHEMA = {n: json.loads((SCHEMAS / f"questions.{n}.json").read_text(encoding="utf-8")) for n in ("question", "draft", "send-result")}

SPEC_ROW = {
    "source": "spec", "ref": "agent-runner", "qid": "Q1", "question": "Ship it?", "context": None,
    "recommendation": "Yes", "date": "2026-10-29", "produces": "a decision", "draft": None,
    "acceptedRecommendation": None, "draftUpdatedAt": None, "draftSentDemandId": None, "stale": False,
}
CONFLICT_ROW = {
    **SPEC_ROW, "source": "conflict", "ref": "c-001", "qid": "conflict", "context": "a note", "recommendation": None,
    "date": None, "produces": None, "draft": "Do X", "acceptedRecommendation": False,
    "draftUpdatedAt": "2026-10-29T10:00:00Z", "draftSentDemandId": "owner-answers-20261029-1", "stale": True,
}
DRAFT = {"answer": "Yes", "acceptedRecommendation": True}
SENT = {"id": "owner-answers-20261029-1", "path": "demands/2026-10-29-platform-vault-owner-answers.md", "commit": "abc1234", "count": 2, "skippedStale": 0}


def without(doc, *keys):
    return {k: v for k, v in doc.items() if k not in keys}


def errs(name, doc):
    return list(Draft202012Validator(SCHEMA[name]).iter_errors(doc))


def ok(name, doc, label):
    e = errs(name, doc)
    assert not e, f"questions.{name}: {label}: expected valid, got {e[0].message}"
    print(f"PASS  questions.{name}: {label}")


def bad(name, doc, label):
    e = errs(name, doc)
    assert e, f"questions.{name}: {label}: expected invalid, but document passed"
    print(f"PASS  questions.{name}: {label} (rejected: {e[0].message[:90]})")


def main() -> int:
    ok("question", SPEC_ROW, "spec question, no draft")
    ok("question", CONFLICT_ROW, "stale conflict with a sent draft")
    for k in SPEC_ROW:
        bad("question", without(SPEC_ROW, k), f"{k} missing")
    bad("question", {**SPEC_ROW, "source": "vault"}, "source outside spec|conflict")
    bad("question", {**SPEC_ROW, "stale": None}, "stale not boolean")
    bad("question", {**SPEC_ROW, "question": ""}, "empty question")
    bad("question", {**SPEC_ROW, "acceptedRecommendation": "yes"}, "acceptedRecommendation not boolean/null")
    bad("question", {**SPEC_ROW, "extra": 1}, "unmodelled member")

    ok("draft", DRAFT, "accepted recommendation")
    ok("draft", {"answer": "Other", "acceptedRecommendation": False}, "own answer")
    bad("draft", {"answer": "x"}, "acceptedRecommendation missing")
    bad("draft", {"acceptedRecommendation": True}, "answer missing")
    bad("draft", {**DRAFT, "answer": ""}, "empty answer")
    bad("draft", {**DRAFT, "answer": "a" * 20001}, "answer over 20000 chars")
    bad("draft", {**DRAFT, "acceptedRecommendation": None}, "acceptedRecommendation null")
    bad("draft", {**DRAFT, "extra": 1}, "unmodelled member")

    ok("send-result", SENT, "two drafts sent")
    ok("send-result", {**SENT, "count": 1, "skippedStale": 3}, "stale drafts skipped")
    for k in SENT:
        bad("send-result", without(SENT, k), f"{k} missing")
    bad("send-result", {**SENT, "count": 0}, "count 0 (nothing sent is a 409, not a result)")
    bad("send-result", {**SENT, "skippedStale": -1}, "negative skippedStale")
    bad("send-result", {**SENT, "extra": 1}, "unmodelled member")
    return 0


if __name__ == "__main__":
    sys.exit(main())
