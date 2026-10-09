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
    scope = x["request"].get("scope", "epics")
    suffix = "" if scope == "epics" else f":{scope}"
    d["idempotencyKey"] = hashlib.sha256(f"{d['briefHash']}:{d['project']['shortName']}{suffix}".encode()).hexdigest()

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
synthetic = [x for x in accepted if "synthetic" in x and x["request"]["brief"].get("risks")]
expect(len(synthetic) == 1, "fixture holds one synthetic exchange whose brief carries risks")
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

# scope and tasks (v0.53.0): the two synthetic exchanges carry scope all and scope tasks (replayed)
scoped = {x["request"]["scope"]: x for x in accepted if "scope" in x["request"]}
expect(set(scoped) == {"all", "tasks"}, f"fixture holds one scope all and one scope tasks exchange (got {sorted(scoped)})")
expect(all("synthetic" in x for x in scoped.values()), "the scoped exchanges are marked synthetic")
for sc, x in scoped.items():
    expect(not errors(REQ, x["request"]), f"scope {sc} request validates")
    expect(not errors(RESP, x["response"]["data"]), f"scope {sc} answer validates: {[e.message for e in errors(RESP, x['response']['data'])][:2]}")
    expect(x["response"]["data"]["scope"] == sc, f"scope {sc} answer states the scope it ran")
all_ans = scoped["all"]["response"]["data"]
expect(len(all_ans["tasks"]["created"]) >= 2 and len({t["epicKey"] for t in all_ans["tasks"]["created"]}) == 2, "scope all answer has tasks under two epics")
expect({t["epicKey"] for t in all_ans["tasks"]["created"]} <= {e["key"] for e in all_ans["epics"]["created"]}, "every task names an epic of the same answer")
rep = scoped["tasks"]["response"]["data"]
expect(rep["replayed"] and rep["tasks"]["alreadyPresent"] and not rep["tasks"]["created"], "scope tasks replay lists tasks as alreadyPresent")
expect(all_ans["idempotencyKey"] != rep["idempotencyKey"] != accepted[0]["response"]["data"]["idempotencyKey"], "scope is part of the idempotency key rule")

# old requests and answers (no scope, no tasks) still validate; omitted scope = epics
expect("scope" not in good and not errors(REQ, good), "a request without scope validates")
expect("scope" not in resp and "tasks" not in resp and not errors(RESP, resp), "an old answer without scope and tasks validates")
body = copy.deepcopy(good)
body["scope"] = "epics"
expect(not errors(REQ, body), "scope epics validates")
for bad_scope in ("everything", "", "EPICS", None, 1, ["epics"]):
    body = copy.deepcopy(good)
    body["scope"] = bad_scope
    expect(errors(REQ, body), f"unknown scope {bad_scope!r} refused")
d = copy.deepcopy(resp)
d["scope"] = "epics"
d["tasks"] = {"created": [], "alreadyPresent": [], "failed": []}
expect(not errors(RESP, d), "scope epics with an empty tasks object validates")
d["scope"] = "weird"
expect(errors(RESP, d), "unknown response scope refused")
task = copy.deepcopy(all_ans["tasks"]["created"][0])
for label, mut in [
    ("task without its parent epic key", lambda t: t.pop("epicKey")),
    ("task without its own key", lambda t: t.pop("key")),
    ("created task without id", lambda t: t.pop("id")),
    ("created task with an extra property", lambda t: t.update(token="x")),
]:
    d = copy.deepcopy(all_ans)
    t = copy.deepcopy(task)
    mut(t)
    d["tasks"]["created"] = [t]
    expect(errors(RESP, d), f"{label} refused")
    d = copy.deepcopy(all_ans)
    d["tasks"]["created"] = []
    d["tasks"]["alreadyPresent"] = [t]
    if "id" not in t or "epicKey" not in t or "key" not in t or "token" in t:
        expect(errors(RESP, d), f"{label} refused in alreadyPresent")
failed_task = {"key": "k", "epicKey": "e", "title": "t", "code": "not_attempted", "reason": "its epic failed"}
d = copy.deepcopy(all_ans)
d["status"] = "partial"
d["tasks"]["failed"] = [failed_task]
expect(not errors(RESP, d), "a failed task with parent epic key and closed code validates")
for label, mut in [("without epicKey", lambda t: t.pop("epicKey")), ("with unknown code", lambda t: t.update(code="weird")), ("without reason", lambda t: t.pop("reason"))]:
    d = copy.deepcopy(all_ans)
    t = copy.deepcopy(failed_task)
    mut(t)
    d["tasks"]["failed"] = [t]
    expect(errors(RESP, d), f"a failed task {label} refused")
d = copy.deepcopy(all_ans)
d["tasks"]["extra"] = []
expect(errors(RESP, d), "extra property on tasks refused")

# ---- v0.54.0: localOnly and the setup step (task 0) ----
SETUP = Draft202012Validator(json.loads((ROOT / "schemas" / "factory" / "factory.handover-setup.json").read_text(encoding="utf-8")), format_checker=FormatChecker())
base_req = copy.deepcopy(accepted[0]["request"])
base_req.pop("localOnly", None)
expect(not errors(REQ, base_req), "request without localOnly validates")
for val in (True, False):
    r = copy.deepcopy(base_req)
    r["localOnly"] = val
    expect(not errors(REQ, r), f"localOnly {val} validates")
for bad in ("yes", 1, None):
    r = copy.deepcopy(base_req)
    r["localOnly"] = bad
    expect(errors(REQ, r), f"localOnly {bad!r} refused")

IDS = ["app-repo", "hexagon-repo", "onboard", "register-project", "verify-discovery"]
T = "2026-10-09T10:00:00Z"


def make_setup(local_only=False, states=None):
    states = states or ["done"] * 5
    steps = []
    for i, st in zip(IDS, states):
        step = {"id": i, "state": st, "at": T}
        if st == "failed":
            step.update(reason="remote_unavailable", detail="remote said no")
        steps.append(step)
    return {"name": "Set up repositories", "state": "running", "localOnly": local_only, "steps": steps, "updatedAt": T}


def both(setup):
    ans = copy.deepcopy(accepted[0]["response"]["data"])
    ans["setup"] = setup
    return errors(SETUP, setup) + errors(RESP, ans)


expect(not errors(RESP, accepted[0]["response"]["data"]), "answer without setup validates")
expect(not both(make_setup()), "a complete setup validates in both schemas")
expect(not both(make_setup(True, ["skipped", "skipped", "done", "done", "done"])), "localOnly setup with skipped repo steps validates")
for st in ("pending", "running", "done", "failed", "skipped"):
    expect(not both(make_setup(False, [st] * 5)), f"every step in state {st} validates")
for st in ("pending", "running", "done", "failed"):
    s = make_setup()
    s["state"] = st
    expect(not both(s), f"setup state {st} validates")
for label, mut in [
    ("an unknown step id", lambda s: s["steps"][0].update(id="publish")),
    ("an unknown step state", lambda s: s["steps"][0].update(state="paused")),
    ("an unknown setup state", lambda s: s.update(state="skipped")),
    ("a different name", lambda s: s.update(name="Set up repos")),
    ("a missing localOnly", lambda s: s.pop("localOnly")),
    ("an unknown failure reason", lambda s: s["steps"][0].update(state="failed", reason="weird")),
    ("a failed step without a reason", lambda s: s["steps"][0].update(state="failed")),
    ("an extra step property", lambda s: s["steps"][0].update(token="x")),
    ("an extra setup property", lambda s: s.update(extra=1)),
    ("six steps", lambda s: s["steps"].append({"id": "onboard", "state": "pending"})),
]:
    s = make_setup()
    mut(s)
    expect(both(s), f"setup with {label} refused (in both schemas)")
expect(RESP.schema["$defs"]["setup"] == {k: v for k, v in SETUP.schema.items() if k not in ("$schema", "$id", "title", "$defs")} | {"description": RESP.schema["$defs"]["setup"]["description"]}
       and RESP.schema["$defs"]["setupStep"] == SETUP.schema["$defs"]["setupStep"], "embedded setup definition equals the standalone factory schema")

if failures:
    print(f"{len(failures)} failure(s)")
    sys.exit(1)
print(f"planner brief schemas OK: {len(accepted)} accepted exchanges, {len(refused)} refused exchanges, negative cases refused")
