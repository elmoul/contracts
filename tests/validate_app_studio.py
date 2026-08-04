"""
Schema-level validation for schemas/app-studio/*.json.

Mirrors validate_demand.py's pattern: validates the JSON Schemas directly
against example documents, independent of any language binding.

Unlike the other validators here, the two positive fixtures are not
hand-written — they are the tutor genesis pilot's OWN records, copied verbatim
into tests/fixtures/app-studio/ at extraction time:

  * tutor-pilot-mission.json — app-studio's `projection.project()` of mission
    d34de281-c5c5-4e44-b3c5-6085c225adea, read straight from its ledger. Three
    owner-approved gates (concept, architecture, plan) with the plan gate's
    binding amendment in its notes.
  * tutor-pilot-plan.json — the owner-approved plan.json of that same mission,
    round 1, six waves (wave 1 detailed, 2-6 outline-only).

That is the point of D066 build-then-extract: the schemas describe a shape a
real build produced, so the fixture is the proof rather than an illustration.
Note the plan fixture carries no `deferredToDispatch` — it predates that field,
which is exactly why the schema leaves it optional.

Run: python tests/validate_app_studio.py
"""
import json
import sys
from copy import deepcopy
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parent.parent
SCHEMAS = ROOT / "schemas" / "app-studio"
FIXTURES = Path(__file__).resolve().parent / "fixtures" / "app-studio"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


PILOT_MISSION = load(FIXTURES / "tutor-pilot-mission.json")
PILOT_PLAN = load(FIXTURES / "tutor-pilot-plan.json")

# A gate that has rejected twice. The defect this fixture exists to prevent:
# `gateContext.bindingDirection` was typed as a single nullable string, so the
# second rejection could only be represented by discarding the first direction —
# which does not stop being binding because a later one arrived. Kept as a
# permanent positive case so the list form can never quietly regress to a scalar.
TWICE_REJECTED_MISSION = load(FIXTURES / "twice-rejected-gate-mission.json")

BAD_MISSION_BINDING_DIRECTION_AS_STRING = deepcopy(TWICE_REJECTED_MISSION)
BAD_MISSION_BINDING_DIRECTION_AS_STRING["gateContext"]["bindingDirection"] = (
    "split wave 1 — it carries two unrelated concerns"
)

GOOD_MISSION_NEVER_REJECTED = deepcopy(TWICE_REJECTED_MISSION)
GOOD_MISSION_NEVER_REJECTED["gateContext"]["bindingDirection"] = None
GOOD_MISSION_NEVER_REJECTED["gateContext"]["priorRounds"] = 0
GOOD_MISSION_NEVER_REJECTED["gateRecords"] = []

# --- mission negatives -------------------------------------------------------

BAD_MISSION_UNKNOWN_STAGE = deepcopy(PILOT_MISSION)
BAD_MISSION_UNKNOWN_STAGE["stage"] = "implementing"  # not on the spine

BAD_MISSION_SEND_BACK_AS_OUTCOME = deepcopy(PILOT_MISSION)
BAD_MISSION_SEND_BACK_AS_OUTCOME["gateRecords"][0]["outcome"] = "send-back"

BAD_MISSION_REWIND_TO_NON_GATE = deepcopy(PILOT_MISSION)
BAD_MISSION_REWIND_TO_NON_GATE["rewinds"] = [
    {
        "fromStage": "executing",
        "toStage": "architecture",  # a rewind lands on a GATE, never a work stage
        "direction": "reconsider the guardrail layer",
        "recordedAt": "2026-08-04T07:00:00+00:00",
    }
]

BAD_MISSION_MISSING_LEDGERS = {
    "id": "d34de281-c5c5-4e44-b3c5-6085c225adea",
    "class": "genesis",
    "appName": "tutor",
    "stage": "executing",
    "currentWave": 1,
    # gateRecords / sendBacks / rewinds all absent — the append-only spine is
    # not optional, an empty list is how "nothing happened yet" is said.
}

# A send-back is a note with NO verdict and lives on its own list. Proving the
# lists are genuinely distinct shapes: a send-back record cannot pass as a gate
# record, because it has no `outcome` and carries `recordedAt`, not `decidedAt`.
BAD_MISSION_SEND_BACK_IN_GATE_RECORDS = deepcopy(PILOT_MISSION)
BAD_MISSION_SEND_BACK_IN_GATE_RECORDS["gateRecords"] = [
    {
        "gate": "plan-gate",
        "notes": "cannot evaluate this gate as instrumented",
        "recordedAt": "2026-08-04T07:00:00+00:00",
        "wave": 1,
    }
]

GOOD_MISSION_SEND_BACK = deepcopy(PILOT_MISSION)
GOOD_MISSION_SEND_BACK["sendBacks"] = [
    {
        "gate": "plan-gate",
        "notes": "the plan renders, but the gate cannot see the wave's dispatch state",
        "recordedAt": "2026-08-04T07:00:00+00:00",
        "wave": 1,
    }
]

GOOD_MISSION_ABORTED = {
    "id": "07d875a5-42eb-41d6-a0df-b27ef22f7248",
    "class": "genesis",
    "appName": "tutor",
    "stage": "aborted",
    "stageKind": "terminal",
    "intake": "test",
    "targetRepo": None,
    "designMissionId": None,
    "currentWave": 0,
    "isTerminal": True,
    "abortedFrom": "intake",
    "abortReason": "scratch mission from a quoting test",
    "gateContext": None,
    "gateRecords": [],
    "sendBacks": [],
    "rewinds": [],
    "rewindTargets": [],
}

GOOD_MISSION_WAVE_REVIEW = deepcopy(PILOT_MISSION)
GOOD_MISSION_WAVE_REVIEW["stage"] = "wave-review"
GOOD_MISSION_WAVE_REVIEW["stageKind"] = "gate"
GOOD_MISSION_WAVE_REVIEW["gateRecords"].append(
    {
        "gate": "wave-review",
        "outcome": "approved",
        "notes": "wave 1 shipped; replan wave 2 before dispatching it",
        "decidedAt": "2026-08-04T09:00:00+00:00",
        "waveReviewNext": "replan",
        "wave": 1,
    }
)
GOOD_MISSION_WAVE_REVIEW["gateContext"] = {
    "gate": "wave-review",
    "subject": "the wave's shipped increment",
    "bindingDirection": None,
    "priorRounds": 0,
    "wave": 1,
    "approvalRequires": ["next-wave", "replan", "accept"],
}

BAD_MISSION_UNKNOWN_WAVE_REVIEW_NEXT = deepcopy(GOOD_MISSION_WAVE_REVIEW)
BAD_MISSION_UNKNOWN_WAVE_REVIEW_NEXT["gateRecords"][-1]["waveReviewNext"] = "continue"

# --- plan negatives ----------------------------------------------------------

BAD_PLAN_UNIT_WITHOUT_VERIFY = deepcopy(PILOT_PLAN)
BAD_PLAN_UNIT_WITHOUT_VERIFY["waves"][0]["units"][0]["verify"] = []

BAD_PLAN_UNIT_VERIFY_ABSENT = deepcopy(PILOT_PLAN)
del BAD_PLAN_UNIT_VERIFY_ABSENT["waves"][0]["units"][0]["verify"]

BAD_PLAN_UNIT_MODE_ABSENT = deepcopy(PILOT_PLAN)
del BAD_PLAN_UNIT_MODE_ABSENT["waves"][0]["units"][1]["mode"]

BAD_PLAN_UNKNOWN_MODE = deepcopy(PILOT_PLAN)
BAD_PLAN_UNKNOWN_MODE["waves"][0]["units"][0]["mode"] = "human"

BAD_PLAN_VERIFY_WITHOUT_PASS_CONDITION = deepcopy(PILOT_PLAN)
BAD_PLAN_VERIFY_WITHOUT_PASS_CONDITION["waves"][0]["units"][2]["verify"] = [
    {"run": "mvn test", "manual": None, "expect": ""}
]

BAD_PLAN_VERIFY_WITH_NEITHER_RUN_NOR_MANUAL = deepcopy(PILOT_PLAN)
BAD_PLAN_VERIFY_WITH_NEITHER_RUN_NOR_MANUAL["waves"][0]["units"][2]["verify"] = [
    {"run": None, "manual": None, "expect": "it works"}
]

# The defect the two-list split exists to prevent: a planner with nowhere to
# record a deliberately-deferred item files it under openDecisions and the gate
# reads correct behaviour as a blocker. The schema keeps both lists, so the
# honest form validates...
GOOD_PLAN_DEFERRED_TO_DISPATCH = deepcopy(PILOT_PLAN)
GOOD_PLAN_DEFERRED_TO_DISPATCH["waves"][0]["deferredToDispatch"] = [
    "the exact contracts tag",
    "the ports",
    "the baseline migration number",
]
GOOD_PLAN_DEFERRED_TO_DISPATCH["waves"][0]["openDecisions"] = []
GOOD_PLAN_DEFERRED_TO_DISPATCH["waves"][0]["canAuthorize"] = True

# ...and the two lists must not be interchangeable at the type level either.
BAD_PLAN_DEFERRED_NOT_A_LIST = deepcopy(GOOD_PLAN_DEFERRED_TO_DISPATCH)
BAD_PLAN_DEFERRED_NOT_A_LIST["waves"][0]["deferredToDispatch"] = "the exact contracts tag"

BAD_PLAN_COLLAPSED_LISTS = deepcopy(PILOT_PLAN)
BAD_PLAN_COLLAPSED_LISTS["waves"][0]["decisions"] = ["the exact contracts tag"]

BAD_PLAN_UNKNOWN_LAZY_NAMESPACE = deepcopy(PILOT_PLAN)
BAD_PLAN_UNKNOWN_LAZY_NAMESPACE["waves"][0]["units"][2]["lazyAllocations"] = ["schema"]

BAD_PLAN_UNKNOWN_WAVE_STATUS = deepcopy(PILOT_PLAN)
BAD_PLAN_UNKNOWN_WAVE_STATUS["waves"][0]["status"] = "started"

GOOD_PLAN_ADVISORY_UNIT_WITHOUT_VERIFY = deepcopy(PILOT_PLAN)
GOOD_PLAN_ADVISORY_UNIT_WITHOUT_VERIFY["waves"][0]["units"].append(
    {
        "id": "T1.9",
        "title": "Note: the kids-class template is the long pole",
        "mode": "advisory",
        "mark": "\U0001f4a1",
        "branch": None,
        "dependsOn": [],
        "parallelOk": True,
        "diagnoseFirst": [],
        "lazyAllocations": [],
        "prompt": "",
        "verify": [],
        "model": None,
        "status": "pending",
    }
)

# An absence claim — "the secret never reaches the provider" — is only
# checkable once the step names the input path the excluded thing would have
# travelled on. `channel` is that path. Optional by construction: every plan
# artifact that predates it (PILOT_PLAN included) carries no channel on any
# step and must keep validating, which the pilot-plan positive above asserts.
GOOD_PLAN_ABSENCE_STEP_WITH_CHANNEL = deepcopy(PILOT_PLAN)
GOOD_PLAN_ABSENCE_STEP_WITH_CHANNEL["waves"][0]["units"][0]["verify"] = [
    {
        "run": None,
        "manual": "send a prompt carrying an API key and read the gateway's outbound request log",
        "expect": "no request to the provider contains the key",
        "channel": "the `metadata` map on the outbound provider request",
    }
]

# The same step with the channel dropped: still valid — the property is
# optional, not conditionally required.
GOOD_PLAN_ABSENCE_STEP_WITHOUT_CHANNEL = deepcopy(GOOD_PLAN_ABSENCE_STEP_WITH_CHANNEL)
del GOOD_PLAN_ABSENCE_STEP_WITHOUT_CHANNEL["waves"][0]["units"][0]["verify"][0]["channel"]

# It is one input path, stated in words — not a list of them, and not a
# structured locator. Typed loosely enough and it becomes the free-form dumping
# ground the description exists to prevent.
BAD_PLAN_CHANNEL_AS_LIST = deepcopy(GOOD_PLAN_ABSENCE_STEP_WITH_CHANNEL)
BAD_PLAN_CHANNEL_AS_LIST["waves"][0]["units"][0]["verify"][0]["channel"] = [
    "the `metadata` map"
]

CASES = [
    # (schema file, label, document, should_validate)
    ("app.mission.json", "tutor pilot mission (real, from the ledger)", PILOT_MISSION, True),
    ("app.mission.json", "aborted mission", GOOD_MISSION_ABORTED, True),
    ("app.mission.json", "mission with a send-back", GOOD_MISSION_SEND_BACK, True),
    ("app.mission.json", "mission at wave-review with waveReviewNext", GOOD_MISSION_WAVE_REVIEW, True),
    ("app.mission.json", "gate rejected twice — bindingDirection carries both", TWICE_REJECTED_MISSION, True),
    ("app.mission.json", "gate never rejected — bindingDirection null", GOOD_MISSION_NEVER_REJECTED, True),
    ("app.mission.json", "bindingDirection as a bare string (the pre-v0.21.0 form)", BAD_MISSION_BINDING_DIRECTION_AS_STRING, False),
    ("app.mission.json", "unknown stage", BAD_MISSION_UNKNOWN_STAGE, False),
    ("app.mission.json", "send-back smuggled in as a gate outcome", BAD_MISSION_SEND_BACK_AS_OUTCOME, False),
    ("app.mission.json", "send-back record placed in gateRecords", BAD_MISSION_SEND_BACK_IN_GATE_RECORDS, False),
    ("app.mission.json", "rewind targeting a non-gate stage", BAD_MISSION_REWIND_TO_NON_GATE, False),
    ("app.mission.json", "missing the append-only record lists", BAD_MISSION_MISSING_LEDGERS, False),
    ("app.mission.json", "unknown waveReviewNext", BAD_MISSION_UNKNOWN_WAVE_REVIEW_NEXT, False),
    ("app.task-plan.json", "tutor pilot plan.json (real, owner-approved)", PILOT_PLAN, True),
    ("app.task-plan.json", "wave with deferredToDispatch kept separate", GOOD_PLAN_DEFERRED_TO_DISPATCH, True),
    ("app.task-plan.json", "advisory unit with no verify step", GOOD_PLAN_ADVISORY_UNIT_WITHOUT_VERIFY, True),
    ("app.task-plan.json", "dispatched unit with an empty verify list", BAD_PLAN_UNIT_WITHOUT_VERIFY, False),
    ("app.task-plan.json", "unit with no verify key at all", BAD_PLAN_UNIT_VERIFY_ABSENT, False),
    ("app.task-plan.json", "unit with no mode", BAD_PLAN_UNIT_MODE_ABSENT, False),
    ("app.task-plan.json", "unknown mode", BAD_PLAN_UNKNOWN_MODE, False),
    ("app.task-plan.json", "verify step with no pass condition", BAD_PLAN_VERIFY_WITHOUT_PASS_CONDITION, False),
    ("app.task-plan.json", "verify step with neither run nor manual", BAD_PLAN_VERIFY_WITH_NEITHER_RUN_NOR_MANUAL, False),
    ("app.task-plan.json", "deferredToDispatch as a bare string", BAD_PLAN_DEFERRED_NOT_A_LIST, False),
    ("app.task-plan.json", "the two decision lists collapsed into one", BAD_PLAN_COLLAPSED_LISTS, False),
    ("app.task-plan.json", "unknown lazy namespace", BAD_PLAN_UNKNOWN_LAZY_NAMESPACE, False),
    ("app.task-plan.json", "unknown wave status", BAD_PLAN_UNKNOWN_WAVE_STATUS, False),
    ("app.task-plan.json", "absence verify step naming its channel", GOOD_PLAN_ABSENCE_STEP_WITH_CHANNEL, True),
    ("app.task-plan.json", "the same step with channel omitted (optional)", GOOD_PLAN_ABSENCE_STEP_WITHOUT_CHANNEL, True),
    ("app.task-plan.json", "channel as a list rather than one input path", BAD_PLAN_CHANNEL_AS_LIST, False),
]


def main() -> int:
    failures = 0
    validators: dict[str, Draft202012Validator] = {}

    for name in ("app.mission.json", "app.task-plan.json"):
        schema = load(SCHEMAS / name)
        Draft202012Validator.check_schema(schema)
        validators[name] = Draft202012Validator(schema)
        print(f"OK    {name} is itself a valid Draft 2020-12 schema")

    for schema_name, label, doc, should_pass in CASES:
        errors = sorted(validators[schema_name].iter_errors(doc), key=lambda e: e.path)
        if should_pass and errors:
            failures += 1
            print(f"FAIL  {schema_name}: '{label}' should validate but did not:")
            for e in errors:
                print(f"        {list(e.path)}: {e.message}")
        elif not should_pass and not errors:
            failures += 1
            print(f"FAIL  {schema_name}: '{label}' should have been rejected but validated")
        else:
            verb = "validates" if should_pass else "correctly rejected"
            print(f"OK    {schema_name}: '{label}' {verb}")

    # The pilot plan predates deferredToDispatch — assert that, so this test
    # keeps documenting *why* the field is optional rather than merely passing.
    if "deferredToDispatch" in PILOT_PLAN["waves"][0]:
        failures += 1
        print(
            "FAIL  the pilot plan fixture now carries deferredToDispatch — it was "
            "copied verbatim and should not have; re-check the fixture."
        )
    else:
        print("OK    pilot plan fixture omits deferredToDispatch, as the real artifact does")

    if failures:
        print(f"\n{failures} failure(s).")
        return 1
    print(f"\nAll {len(CASES) + 3} app-studio schema checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
