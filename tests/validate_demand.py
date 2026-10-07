"""
Schema-level validation for schemas/demand-coordinator/*.json.

Mirrors validate_control_plane.py's pattern: validates the JSON Schemas
directly against example documents, independent of any language binding.
Run: python tests/validate_demand.py
"""
import json
import sys
from datetime import date, datetime
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parent.parent
SCHEMAS = ROOT / "schemas" / "demand-coordinator"
DEMANDS = ROOT / "demands"
FIXTURES = ROOT / "tests" / "fixtures" / "demand-coordinator"

GOOD_DEMAND = {
    "id": "demand-coordinator-20260709-demand-schema",
    "date": "2026-07-09",
    "from": "demand-coordinator",
    "to": ["contracts"],
    "capability": "publish the demand + demand.fulfillment schemas",
    "acceptance-criteria": [
        "demand and demand.fulfillment JSON Schemas land under schemas/",
        "Java/TS/Python bindings generated and released under a tagged version",
    ],
    "needs-owner": False,
    "status": "open",
}

BAD_DEMAND_MISSING_FIELD_AND_BAD_STATUS = {
    # missing id, missing acceptance-criteria
    "date": "2026-07-09",
    "from": "demand-coordinator",
    "to": ["contracts"],
    "capability": "publish the demand + demand.fulfillment schemas",
    "needs-owner": False,
    "status": "ingested",  # not an origin-owned status — coordinator-internal state
}

BAD_DEMAND_MALFORMED_ID = {
    "id": "not-a-valid-id",  # missing the embedded YYYYMMDD segment
    "date": "2026-07-09",
    "from": "demand-coordinator",
    "to": ["contracts"],
    "capability": "publish the demand + demand.fulfillment schemas",
    "acceptance-criteria": ["something"],
    "needs-owner": False,
    "status": "open",
}

# v0.26.0: the optional `after` ordering field (dashboard-20260914-demand-dispatch-order).
GOOD_DEMAND_WITH_AFTER = {
    **GOOD_DEMAND,
    "after": ["contracts-20260914-factory-repin-interface-extraction"],
}

BAD_DEMAND_AFTER_EMPTY = {
    # `after` present but empty: the field's whole meaning is "wait for these", so an
    # empty list is a producer that meant to constrain something and didn't. Omit the
    # field instead — absent means unconstrained.
    **GOOD_DEMAND,
    "after": [],
}

BAD_DEMAND_AFTER_DUPLICATE = {
    # The same id twice would make a demand wait on one dependency "twice" — a producer
    # bug that should fail here, not become two identical board warnings downstream.
    **GOOD_DEMAND,
    "after": [
        "contracts-20260914-factory-repin-interface-extraction",
        "contracts-20260914-factory-repin-interface-extraction",
    ],
}

BAD_DEMAND_AFTER_MALFORMED_ID = {
    # Same shape rule as `id` itself — a bare slug can never match a real demand.
    **GOOD_DEMAND,
    "after": ["factory-repin"],
}

# One row of the dispatch queue (demand.queue-entry.json) — the shape
# demand-coordinator and agent-runner both present.
GOOD_QUEUE_ENTRY_READY = {
    "demandId": "dashboard-20260914-demand-dispatch-order",
    "date": "2026-09-14",
    "from": "dashboard",
    "to": ["contracts"],
    "wave": 1,
    "waitingOn": [],
}

GOOD_QUEUE_ENTRY_WAITING = {
    "demandId": "dashboard-20260914-demand-dispatch-order",
    "date": "2026-09-14",
    "from": "dashboard",
    "to": ["contracts", "demand-coordinator", "runtime", "agent-runner"],
    "wave": 2,
    "waitingOn": ["contracts-20260914-factory-repin-interface-extraction"],
}

GOOD_QUEUE_ENTRY_ELEVATED_WAVE_EMPTY_WAITING = {
    # The non-inverse case this schema's description exists to pin: a sub-demand can sit
    # at wave 3 with NOTHING of its own unresolved, because it is a leg of a multi-hexagon
    # demand whose preceding target is itself at wave 3. If a consumer ever "simplifies"
    # this to `wave = 1 + len(waitingOn)`, this document stops being valid.
    "demandId": "dashboard-20260914-demand-dispatch-order",
    "date": "2026-09-14",
    "from": "dashboard",
    "to": ["contracts", "demand-coordinator"],
    "wave": 3,
    "waitingOn": [],
}

BAD_QUEUE_ENTRY_WAVE_ZERO = {
    # wave 0 as a "not yet scheduled" sentinel would sort ahead of every real wave.
    **GOOD_QUEUE_ENTRY_READY,
    "wave": 0,
}

BAD_QUEUE_ENTRY_MISSING_WAVE = {
    k: v for k, v in GOOD_QUEUE_ENTRY_READY.items() if k != "wave"
}

BAD_QUEUE_ENTRY_DUPLICATE_WAITING = {
    **GOOD_QUEUE_ENTRY_WAITING,
    "waitingOn": [
        "contracts-20260914-factory-repin-interface-extraction",
        "contracts-20260914-factory-repin-interface-extraction",
    ],
}

BAD_QUEUE_ENTRY_CARRIES_ENVELOPE_PROSE = {
    # The queue entry is deliberately a lean reference, not a second copy of the demand
    # envelope — a consumer that starts embedding `capability` here must fail loudly.
    **GOOD_QUEUE_ENTRY_READY,
    "capability": "a second home for the same prose",
}

GOOD_FULFILLMENT = {
    "demandId": "demand-coordinator-20260709-demand-schema",
    "worker": "contracts",
    "status": "done",
    "summaryRef": "demands/fulfilled/demand-coordinator-20260709-demand-schema-report.md",
}

GOOD_FULFILLMENT_SUB_DEMAND = {
    "demandId": "plantpal-20260709-ai-gateway-full-ai-coverage",
    "subDemand": "plantpal-20260709-ai-gateway-full-ai-coverage:ai-gateway",
    "worker": "ai-gateway",
    "status": "blocked",
    "summaryRef": "demands/fulfilled/plantpal-20260709-ai-gateway-full-ai-coverage-report.md",
}

# v0.11.0: summaryRef is optional (demand-coordinator-20260710-contracts-fulfillment-envelope-drift)
# — shipped/date are the real fleet convention (DEMAND_SYSTEM.md §5); this exercises both without
# summaryRef at all.
GOOD_FULFILLMENT_SHIPPED_DATE_NO_SUMMARY_REF = {
    "demandId": "observability-20260710-telemetry-schema",
    "worker": "contracts",
    "status": "done",
    "shipped": ["v0.10.0"],
    "date": "2026-07-10",
}

# v0.51.0: optional typed blockers, valid only when status is blocked.
GOOD_FULFILLMENT_BLOCKED_WITH_BLOCKERS = {
    "demandId": "demand-coordinator-20261007-contracts-fulfillment-blockers",
    "worker": "contracts",
    "status": "blocked",
    "blockers": [
        {"kind": "demand", "text": "needs the ai-gateway schema first", "demandId": "ai-gateway-20261007-contracts-ai-request-correlation-id"},
        {"kind": "runtime-step", "text": "needs a service restart the worker may not perform"},
        {"kind": "owner-decision", "text": "which of two shapes to ship"},
        {"kind": "other", "text": "something else"},
    ],
}
BAD_FULFILLMENT_DONE_WITH_BLOCKERS = {
    **GOOD_FULFILLMENT_BLOCKED_WITH_BLOCKERS,
    "status": "done",
}
BAD_FULFILLMENT_BLOCKER_DEMAND_NO_ID = {
    **GOOD_FULFILLMENT_BLOCKED_WITH_BLOCKERS,
    "blockers": [{"kind": "demand", "text": "no id given"}],
}
BAD_FULFILLMENT_BLOCKER_ID_ON_NON_DEMAND = {
    **GOOD_FULFILLMENT_BLOCKED_WITH_BLOCKERS,
    "blockers": [{"kind": "other", "text": "x", "demandId": "ai-gateway-20261007-contracts-ai-request-correlation-id"}],
}
BAD_FULFILLMENT_BLOCKER_BAD_KIND = {
    **GOOD_FULFILLMENT_BLOCKED_WITH_BLOCKERS,
    "blockers": [{"kind": "weather", "text": "x"}],
}
BAD_FULFILLMENT_BLOCKER_EMPTY_TEXT = {
    **GOOD_FULFILLMENT_BLOCKED_WITH_BLOCKERS,
    "blockers": [{"kind": "other", "text": ""}],
}
BAD_FULFILLMENT_BLOCKER_BAD_DEMAND_ID = {
    **GOOD_FULFILLMENT_BLOCKED_WITH_BLOCKERS,
    "blockers": [{"kind": "demand", "text": "x", "demandId": "Not A Demand"}],
}
BAD_FULFILLMENT_BLOCKER_EXTRA_PROP = {
    **GOOD_FULFILLMENT_BLOCKED_WITH_BLOCKERS,
    "blockers": [{"kind": "other", "text": "x", "why": "y"}],
}

BAD_FULFILLMENT = {
    "demandId": "demand-coordinator-20260709-demand-schema",
    "worker": "contracts",
    "status": "in-progress",  # not a worker-reportable status
    "summaryRef": "demands/fulfilled/demand-coordinator-20260709-demand-schema-report.md",
}


GOOD_ORIGIN_ENVELOPE = GOOD_DEMAND
GOOD_FULFILLMENT_EVIDENCE = GOOD_FULFILLMENT

GOOD_RECEIPT_FOUND = {
    "demandId": "demand-coordinator-20260913-contracts-approved-evidence-receipt",
    "found": True,
    "approvedAt": "2026-09-13T22:10:00Z",
    "provenance": {"decidedBy": "owner"},
    "originEnvelope": GOOD_ORIGIN_ENVELOPE,
    "fulfillmentEvidence": GOOD_FULFILLMENT_EVIDENCE,
    "evidenceSource": {
        "repoPath": "demands/fulfilled/demand-coordinator-20260913-contracts-approved-evidence-receipt-report.md",
        "commit": "9eb777c",
    },
    "evidenceDigest": "3b50d5f4938d671bcf0f09e8f2113ba9eb69660b7885fd7f21f357ed8c8b1b1b",
}

GOOD_RECEIPT_UNKNOWN = {
    "demandId": "demand-coordinator-20260913-contracts-nonexistent",
    "found": False,
    "unknownReason": "no-receipt-on-file",
}

BAD_RECEIPT_FOUND_MISSING_EVIDENCE = {
    # found:true but missing every approval field the allOf/if-then requires
    "demandId": "demand-coordinator-20260913-contracts-approved-evidence-receipt",
    "found": True,
}

BAD_RECEIPT_UNKNOWN_CARRYING_APPROVAL_FIELD = {
    # found:false must not carry any approval-only field — this smuggles one in
    "demandId": "demand-coordinator-20260913-contracts-nonexistent",
    "found": False,
    "unknownReason": "no-receipt-on-file",
    "approvedAt": "2026-09-13T22:10:00Z",
}


def load(name: str) -> dict:
    return json.loads((SCHEMAS / name).read_text(encoding="utf-8"))


def frontmatter(path: Path) -> dict:
    """
    A committed demand file's YAML frontmatter, as the coordinator ingests it.

    The one normalization: every committed demand file writes `date:` unquoted, which
    YAML resolves to a datetime.date object, while the schema types it as a string. Any
    YAML-aware ingest has to stringify it (this predates `after` entirely — it is a
    property of the on-disk convention, not of this field), so the coercion lives here
    rather than weakening the schema's type to accommodate the loader.
    """
    _, _, rest = path.read_text(encoding="utf-8").partition("---\n")
    body, _, _ = rest.partition("\n---")
    loaded = yaml.safe_load(body)
    return {
        key: (value.isoformat() if isinstance(value, (date, datetime)) else value)
        for key, value in loaded.items()
    }


def expect_valid(schema, doc: dict, label: str) -> None:
    validator = schema if isinstance(schema, Draft202012Validator) else Draft202012Validator(schema)
    errors = list(validator.iter_errors(doc))
    if errors:
        raise AssertionError(f"{label}: expected valid, got errors: {errors}")
    print(f"PASS  {label}")


def expect_invalid(schema, doc: dict, label: str) -> None:
    validator = schema if isinstance(schema, Draft202012Validator) else Draft202012Validator(schema)
    errors = list(validator.iter_errors(doc))
    if not errors:
        raise AssertionError(f"{label}: expected invalid, but document passed")
    print(f"PASS  {label} (rejected: {errors[0].message})")


def python_binding_round_trip(demand_schema: dict, pre_after_file: dict) -> None:
    """
    v0.32.0 (factory-20260927-demand-after-binding): the Python Demand binding was left
    stale for `after` in v0.26.0 and, with extra='forbid', rejected any demand carrying
    it. Pin that it now accepts and preserves `after` (order included), that a demand
    without `after` still round-trips without gaining one, and that `to` stays a plain
    list of str (the generator drift v0.26.0 refused to ship).
    """
    sys.path.insert(0, str(ROOT / "gen" / "python"))
    from pydantic import ValidationError

    from platform_contracts.demand_coordinator.demand import Demand

    fixture = json.loads((FIXTURES / "demand-with-after.json").read_text(encoding="utf-8"))
    expect_valid(demand_schema, fixture, "demand fixture: demand-with-after.json (known-good)")

    for label, doc in (
        ("fixture with `after`", fixture),
        ("real pre-`after` demand file", pre_after_file),
    ):
        model = Demand.model_validate(doc)
        dumped = json.loads(model.model_dump_json(by_alias=True, exclude_none=True))
        if dumped != doc:
            raise AssertionError(f"python Demand round-trip ({label}): {dumped!r} != {doc!r}")
        again = Demand.model_validate_json(model.model_dump_json(by_alias=True))
        if again != model:
            raise AssertionError(f"python Demand re-parse ({label}) changed the model")
        expect_valid(demand_schema, dumped, f"python Demand round-trip output re-validates ({label})")
        print(f"PASS  python Demand round-trip preserves document ({label})")

    model = Demand.model_validate(fixture)
    if model.after != fixture["after"] or model.to != ["contracts"]:
        raise AssertionError(f"python Demand: after={model.after!r} to={model.to!r}")
    print("PASS  python Demand: `after` order preserved, `to` is list[str]")

    for label, bad in (
        ("empty `after`", BAD_DEMAND_AFTER_EMPTY),
        ("malformed `after` id", BAD_DEMAND_AFTER_MALFORMED_ID),
    ):
        try:
            Demand.model_validate(bad)
        except ValidationError:
            print(f"PASS  python Demand rejects {label}")
        else:
            raise AssertionError(f"python Demand accepted {label}")


def main() -> int:
    demand_schema = load("demand.json")
    fulfillment_schema = load("demand.fulfillment.json")
    receipt_schema = load("demand.approval-receipt.json")
    queue_entry_schema = load("demand.queue-entry.json")

    # demand.approval-receipt.json $refs its siblings by on-disk filename ("demand.json",
    # "demand.fulfillment.json") rather than by their own $id ("…/demand",
    # "…/demand.fulfillment", no ".json") — deliberate, see the schema's own field
    # descriptions: jsonschema2pojo (Java codegen) resolves relative $refs as same-directory
    # file paths, not by $id. Mirror that here: register each sibling under the *filename*
    # URI ($id's directory + literal ".json" name) that a relative "demand.json" $ref
    # resolves to from demand.approval-receipt.json's own $id, not under the sibling's own
    # $id string.
    registry = Registry().with_resources(
        [
            (demand_schema["$id"] + ".json", Resource.from_contents(demand_schema)),
            (fulfillment_schema["$id"] + ".json", Resource.from_contents(fulfillment_schema)),
        ]
    )
    receipt_validator = Draft202012Validator(receipt_schema, registry=registry)

    expect_valid(demand_schema, GOOD_DEMAND, "demand: contracts bootstrap demand (known-good)")
    expect_invalid(
        demand_schema,
        BAD_DEMAND_MISSING_FIELD_AND_BAD_STATUS,
        "demand: missing id/acceptance-criteria + coordinator-internal status (known-bad)",
    )
    expect_invalid(
        demand_schema,
        BAD_DEMAND_MALFORMED_ID,
        "demand: id missing embedded YYYYMMDD segment (known-bad)",
    )
    expect_valid(demand_schema, GOOD_DEMAND_WITH_AFTER, "demand: optional `after` ordering field (known-good)")
    expect_invalid(
        demand_schema,
        BAD_DEMAND_AFTER_EMPTY,
        "demand: `after` present but empty (known-bad)",
    )
    expect_invalid(
        demand_schema,
        BAD_DEMAND_AFTER_DUPLICATE,
        "demand: `after` repeating the same id (known-bad)",
    )
    expect_invalid(
        demand_schema,
        BAD_DEMAND_AFTER_MALFORMED_ID,
        "demand: `after` entry not shaped like a demand id (known-bad)",
    )
    # The backwards-compatibility claim made concrete: a real demand file committed
    # BEFORE `after` existed, read off disk and validated unmodified. Not a hand-written
    # sample of a pre-`after` file — the actual artifact other repos are pinned against
    # (archived after it was satisfied; the archived copy is the same committed file).
    expect_valid(
        demand_schema,
        frontmatter(DEMANDS / "archive" / "2026-09-14-factory-repin-interface-extraction.md"),
        "demand: real pre-`after` demand file on disk still validates (known-good)",
    )
    python_binding_round_trip(
        demand_schema,
        frontmatter(DEMANDS / "archive" / "2026-09-14-factory-repin-interface-extraction.md"),
    )
    expect_valid(
        queue_entry_schema,
        GOOD_QUEUE_ENTRY_READY,
        "demand.queue-entry: ready, wave 1, nothing waiting (known-good)",
    )
    expect_valid(
        queue_entry_schema,
        GOOD_QUEUE_ENTRY_WAITING,
        "demand.queue-entry: waiting, wave 2 with one unresolved dependency (known-good)",
    )
    expect_valid(
        queue_entry_schema,
        GOOD_QUEUE_ENTRY_ELEVATED_WAVE_EMPTY_WAITING,
        "demand.queue-entry: wave>1 with empty waitingOn — the non-inverse case (known-good)",
    )
    expect_invalid(
        queue_entry_schema,
        BAD_QUEUE_ENTRY_WAVE_ZERO,
        "demand.queue-entry: wave 0 (known-bad)",
    )
    expect_invalid(
        queue_entry_schema,
        BAD_QUEUE_ENTRY_MISSING_WAVE,
        "demand.queue-entry: missing wave (known-bad)",
    )
    expect_invalid(
        queue_entry_schema,
        BAD_QUEUE_ENTRY_DUPLICATE_WAITING,
        "demand.queue-entry: waitingOn repeating the same id (known-bad)",
    )
    expect_invalid(
        queue_entry_schema,
        BAD_QUEUE_ENTRY_CARRIES_ENVELOPE_PROSE,
        "demand.queue-entry: carrying envelope prose instead of referencing it (known-bad)",
    )
    expect_valid(fulfillment_schema, GOOD_FULFILLMENT, "demand.fulfillment: single-target report (known-good)")
    expect_valid(
        fulfillment_schema,
        GOOD_FULFILLMENT_SUB_DEMAND,
        "demand.fulfillment: multi-hexagon sub-demand report (known-good)",
    )
    expect_valid(
        fulfillment_schema,
        GOOD_FULFILLMENT_SHIPPED_DATE_NO_SUMMARY_REF,
        "demand.fulfillment: shipped+date, no summaryRef (known-good, proves v0.11.0 optionality)",
    )
    expect_valid(
        fulfillment_schema,
        GOOD_FULFILLMENT_BLOCKED_WITH_BLOCKERS,
        "demand.fulfillment: blocked report with blockers (known-good)",
    )
    for bad, label in [
        (BAD_FULFILLMENT_DONE_WITH_BLOCKERS, "done report carrying blockers"),
        (BAD_FULFILLMENT_BLOCKER_DEMAND_NO_ID, "demand blocker without demandId"),
        (BAD_FULFILLMENT_BLOCKER_ID_ON_NON_DEMAND, "demandId on a non-demand blocker"),
        (BAD_FULFILLMENT_BLOCKER_BAD_KIND, "unknown blocker kind"),
        (BAD_FULFILLMENT_BLOCKER_EMPTY_TEXT, "empty blocker text"),
        (BAD_FULFILLMENT_BLOCKER_BAD_DEMAND_ID, "malformed blocker demandId"),
        (BAD_FULFILLMENT_BLOCKER_EXTRA_PROP, "extra blocker property"),
    ]:
        expect_invalid(fulfillment_schema, bad, f"demand.fulfillment: {label} (known-bad)")
    expect_invalid(
        fulfillment_schema,
        BAD_FULFILLMENT,
        "demand.fulfillment: bad status (known-bad)",
    )
    expect_valid(
        receipt_validator,
        GOOD_RECEIPT_FOUND,
        "demand.approval-receipt: found, full receipt with embedded envelope+evidence (known-good)",
    )
    expect_valid(
        receipt_validator,
        GOOD_RECEIPT_UNKNOWN,
        "demand.approval-receipt: not found, demandId with no receipt on file (known-good)",
    )
    expect_invalid(
        receipt_validator,
        BAD_RECEIPT_FOUND_MISSING_EVIDENCE,
        "demand.approval-receipt: found:true missing approval fields (known-bad)",
    )
    expect_invalid(
        receipt_validator,
        BAD_RECEIPT_UNKNOWN_CARRYING_APPROVAL_FIELD,
        "demand.approval-receipt: found:false smuggling an approval field (known-bad)",
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
