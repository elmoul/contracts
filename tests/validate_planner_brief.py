"""
Schema-level validation for schemas/youtrack/planner.brief-project-{request,response,error}.json
(`POST /plans/from-brief`, v0.49.0).

tests/fixtures/youtrack-brief/captured-exchanges.json holds real exchanges captured from the
planner's own test suite (youtrack/planner/tests/test_brief_project.py, test helper `request_body`
and the app's actual answers) by wrapping the test client; one exchange per distinct outcome.
Every captured request the planner accepted (200) must validate against the request schema, every
200 answer against the response schema, every error against the error schema. Negative cases:
an extra property, a section outside the ten, a missing section, an unknown error code.

Run: python tests/validate_planner_brief.py
"""
import copy
import hashlib
import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parent.parent
DIR = ROOT / "schemas" / "youtrack"
FIX = ROOT / "tests" / "fixtures" / "youtrack-brief" / "captured-exchanges.json"


def load(name):
    schema = json.loads((DIR / name).read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema, format_checker=FormatChecker())


REQ = load("planner.brief-project-request.json")
RESP = load("planner.brief-project-response.json")
ERR = load("planner.brief-project-error.json")

failures = []


def expect(ok, label):
    if not ok:
        failures.append(label)
        print(f"FAIL  {label}")


def errors(v, doc):
    return list(v.iter_errors(doc))


exchanges = json.loads(FIX.read_text(encoding="utf-8"))
accepted = [x for x in exchanges if x["status"] == 200]
refused = [x for x in exchanges if x["status"] != 200]
expect(len(accepted) >= 6 and len(refused) >= 8, "fixture holds the captured exchanges")

for x in accepted:
    # The stored copies omit idempotencyKey (a sha256 that secret scanners mistake for a key); it is
    # rebuilt from the documented rule, which the planner's real answers were checked against.
    d = x["response"]["data"]
    d["idempotencyKey"] = hashlib.sha256(f"{d['briefHash']}:{d['project']['shortName']}".encode()).hexdigest()

for i, x in enumerate(accepted):
    expect(not errors(REQ, x["request"]), f"captured request #{i} validates: {[e.message for e in errors(REQ, x['request'])][:2]}")
    expect(not errors(RESP, x["response"]["data"]), f"captured 200 answer #{i} validates: {[e.message for e in errors(RESP, x['response']['data'])][:2]}")
    expect(set(x["response"]) == {"data"}, f"answer #{i} is a data envelope")

codes = set()
for x in refused:
    err = x["response"]["error"]
    codes.add(err["code"])
    expect(not errors(ERR, err), f"captured error {err['code']} validates: {[e.message for e in errors(ERR, err)][:2]}")
expect({"approval_invalid", "actor_not_owner", "brief_invalid", "brief_hash_mismatch", "unknown_model", "epics_invalid", "tracker_unavailable"} <= codes,
      f"captured errors cover the main codes (got {sorted(codes)})")

# a captured request the planner refused for the ten sections is refused by the schema too
for x in refused:
    if x["response"]["error"]["code"] == "brief_invalid" and isinstance(x["request"].get("brief"), dict):
        expect(errors(REQ, x["request"]), "a captured brief_invalid request is refused by the request schema")

# negative cases on a real accepted request
good = accepted[0]["request"]
body = copy.deepcopy(good)
body["extra"] = 1
expect(errors(REQ, body), "extra top-level property refused")
body = copy.deepcopy(good)
body["brief"]["sections"]["bonus"] = "twelve chars"
expect(errors(REQ, body), "a section outside the ten refused")
body = copy.deepcopy(good)
del body["brief"]["sections"]["users"]
expect(errors(REQ, body), "a missing section refused")
body = copy.deepcopy(good)
body["brief"]["sections"]["purpose"] = "tiny"
expect(errors(REQ, body), "a section under 5 characters refused")
body = copy.deepcopy(good)
body["brief"]["sections"]["purpose"] = "x" * 12001
expect(errors(REQ, body), "a section over 12000 characters refused")
body = copy.deepcopy(good)
body["brief"]["sections"]["purpose"] = "x" * 12000
expect(not errors(REQ, body), "a 12000-character section accepted")
body = copy.deepcopy(good)
body["approval"]["token"] = "x"
expect(errors(REQ, body), "extra approval property refused")
body = copy.deepcopy(good)
body["brief"]["extra"] = 1
expect(errors(REQ, body), "extra brief property refused")
body = copy.deepcopy(good)
body["brief"]["metadata"] = {"nested": {"a": 1}}
expect(errors(REQ, body), "nested metadata refused")
body = copy.deepcopy(good)
del body["approval"]
expect(errors(REQ, body), "missing approval refused")
body = copy.deepcopy(good)
body["approval"]["hash"] = "nothex"
expect(errors(REQ, body), "malformed approval hash refused")

resp = accepted[0]["response"]["data"]
for label, mut in [
    ("extra response property", lambda d: d.update(token="x")),
    ("unknown failed code", lambda d: d["epics"]["failed"].append({"key": "k", "title": "t", "code": "weird", "reason": "r"})),
    ("unknown owner step", lambda d: d["ownerSteps"].append({"code": "other", "what": "w", "setting": None, "value": None, "command": None})),
    ("plannerEditsEnv true", lambda d: d.update(plannerEditsEnv=True)),
    ("status outside the pair", lambda d: d.update(status="done")),
]:
    d = copy.deepcopy(resp)
    mut(d)
    expect(errors(RESP, d), f"{label} refused")
for bad in ({"code": "not_a_code", "message": "m"}, {"code": "approval_invalid", "message": "m", "extra": 1}, {"code": "approval_invalid"}):
    expect(errors(ERR, bad), f"bad error {bad} refused")

# risks (v0.52.0): optional, validated on the synthetic exchange (the one marked "synthetic")
synthetic = [x for x in accepted if "synthetic" in x]
expect(len(synthetic) == 1 and synthetic[0]["request"]["brief"].get("risks"), "fixture holds one synthetic exchange whose brief carries risks")
with_risks = synthetic[0]["request"]
expect(not errors(REQ, with_risks), "a brief with risks validates")
expect("risks" not in good["brief"] and not errors(REQ, good), "an old payload without risks still validates")
body = copy.deepcopy(with_risks)
body["brief"]["extra"] = 1
expect(errors(REQ, body), "a brief with risks and an unknown property still refused")
body = copy.deepcopy(good)
body["brief"]["unknownList"] = ["x"]
expect(errors(REQ, body), "a brief with an unknown property (no risks) still refused")
for label, value in [("empty risk string", [""]), ("risk over 1500 characters", ["x" * 1501]), ("risks not an array", "text"), ("non-string risk", [1])]:
    body = copy.deepcopy(with_risks)
    body["brief"]["risks"] = value
    expect(errors(REQ, body), f"{label} refused")
body = copy.deepcopy(with_risks)
body["brief"]["risks"] = ["x" * 1500, "y"]
expect(not errors(REQ, body), "a 1500-character risk accepted")
body = copy.deepcopy(with_risks)
body["brief"]["risks"] = []
expect(not errors(REQ, body), "an empty risks list accepted")


def digest(record):
    rest = {k: v for k, v in record.items() if k != "hash"}
    return hashlib.sha256(json.dumps(rest, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


expect(digest(with_risks["brief"]) == with_risks["brief"]["hash"] == with_risks["approval"]["hash"], "the risks brief hash follows the documented rule, risks included")
stripped = copy.deepcopy(with_risks["brief"])
del stripped["risks"]
expect(digest(stripped) != with_risks["brief"]["hash"], "risks is part of the hash when present")
expect(all(digest(x["request"]["brief"]) == x["request"]["brief"]["hash"] for x in accepted), "every accepted brief hashes to its own hash by the documented rule")

if failures:
    print(f"{len(failures)} failure(s)")
    sys.exit(1)
print(f"planner brief schemas OK: {len(accepted)} accepted exchanges, {len(refused)} refused exchanges, negative cases refused")
