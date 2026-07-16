"""
Schema-level validation for schemas/state-feed/state.event.json's oneOf members.

Follows the pattern established in validate_dimension_event.py: validates the JSON
Schema directly against example documents, independent of any language binding.

Originally covered only ActivityCountEvent (v0.7.0, sixth oneOf member); count is a
delta since the last emission for a (componentId, activity) pair, not a cumulative
total — orchestrator/sentinel-hub previously repurposed load pulses (clamped to 100)
for this; activity.count gives it a proper unbounded-count shape.

Extended (v0.14.0, Media & Agents wave W1) to cover the three new oneOf members:
JobProgressEvent (D047, media-generation), AgentRunEvent (D048, agent-runner), and
DesignMissionEvent (D051, design-studio) — each with known-good and known-bad cases,
matching the density of the existing activity.count coverage.

Run: python tests/validate_state_event.py
"""
import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parent.parent
STATE_EVENT_SPEC = ROOT / "schemas" / "state-feed" / "state.event.json"

GOOD_EVENT_WITH_ORIGIN = {
    "type": "activity.count",
    "timestamp": "2026-07-05T12:00:00Z",
    "payload": {
        "componentId": "sentinel-hub",
        "activity": "scan.message",
        "count": 7,
    },
    "origin": "hub",
}

GOOD_EVENT_WITHOUT_ORIGIN = {
    "type": "activity.count",
    "timestamp": "2026-07-05T12:00:00Z",
    "payload": {
        "componentId": "orchestrator",
        "activity": "tool.call",
        "count": 0,
    },
}

BAD_EVENT_NEGATIVE_COUNT = {
    "type": "activity.count",
    "timestamp": "2026-07-05T12:00:00Z",
    "payload": {
        "componentId": "orchestrator",
        "activity": "tool.call",
        "count": -1,
    },
}

BAD_EVENT_MISSING_ACTIVITY = {
    "type": "activity.count",
    "timestamp": "2026-07-05T12:00:00Z",
    "payload": {
        "componentId": "orchestrator",
        "count": 1,
    },
}

BAD_EVENT_UNKNOWN_PROPERTY = {
    "type": "activity.count",
    "timestamp": "2026-07-05T12:00:00Z",
    "payload": {
        "componentId": "orchestrator",
        "activity": "tool.call",
        "count": 1,
        "unexpected": "nope",
    },
}

GOOD_JOB_PROGRESS_FULL = {
    "type": "job.progress",
    "timestamp": "2026-07-16T01:00:00Z",
    "payload": {
        "jobId": "8f14e45f-ceea-467e-adde-3fb5ba8a4b1a",
        "capability": "image-to-3d",
        "status": "running",
        "queueDepth": 2,
        "progressPct": 40,
        "vramFreeMb": 3072,
    },
    "origin": "host",
}

GOOD_JOB_PROGRESS_MINIMAL = {
    "type": "job.progress",
    "timestamp": "2026-07-16T01:00:00Z",
    "payload": {
        "jobId": "8f14e45f-ceea-467e-adde-3fb5ba8a4b1a",
        "capability": "text-to-image",
        "status": "queued",
        "queueDepth": 0,
    },
}

BAD_JOB_PROGRESS_NEGATIVE_QUEUE_DEPTH = {
    "type": "job.progress",
    "timestamp": "2026-07-16T01:00:00Z",
    "payload": {
        "jobId": "8f14e45f-ceea-467e-adde-3fb5ba8a4b1a",
        "capability": "text-to-image",
        "status": "queued",
        "queueDepth": -1,
    },
}

BAD_JOB_PROGRESS_UNKNOWN_CAPABILITY = {
    "type": "job.progress",
    "timestamp": "2026-07-16T01:00:00Z",
    "payload": {
        "jobId": "8f14e45f-ceea-467e-adde-3fb5ba8a4b1a",
        "capability": "video-gen",
        "status": "queued",
        "queueDepth": 0,
    },
}

BAD_JOB_PROGRESS_MISSING_STATUS = {
    "type": "job.progress",
    "timestamp": "2026-07-16T01:00:00Z",
    "payload": {
        "jobId": "8f14e45f-ceea-467e-adde-3fb5ba8a4b1a",
        "capability": "text-to-image",
        "queueDepth": 0,
    },
}

GOOD_AGENT_RUN_LAUNCHED = {
    "type": "agent.run",
    "timestamp": "2026-07-16T02:00:00Z",
    "payload": {
        "runId": "3b241101-e2bb-4255-8caf-4136c566a962",
        "repo": "media-generation",
        "phase": "launched",
    },
}

GOOD_AGENT_RUN_FINISHED_WITH_DEMAND = {
    "type": "agent.run",
    "timestamp": "2026-07-16T02:30:00Z",
    "payload": {
        "runId": "3b241101-e2bb-4255-8caf-4136c566a962",
        "repo": "media-generation",
        "demandId": "demand-coordinator-20260709-demand-schema",
        "phase": "finished",
        "durationMs": 1800000,
        "tokensUsed": 42000,
    },
    "origin": "host",
}

BAD_AGENT_RUN_UNKNOWN_PHASE = {
    "type": "agent.run",
    "timestamp": "2026-07-16T02:00:00Z",
    "payload": {
        "runId": "3b241101-e2bb-4255-8caf-4136c566a962",
        "repo": "media-generation",
        "phase": "running",
    },
}

BAD_AGENT_RUN_MISSING_REPO = {
    "type": "agent.run",
    "timestamp": "2026-07-16T02:00:00Z",
    "payload": {
        "runId": "3b241101-e2bb-4255-8caf-4136c566a962",
        "phase": "launched",
    },
}

BAD_AGENT_RUN_BAD_DEMAND_ID_SHAPE = {
    "type": "agent.run",
    "timestamp": "2026-07-16T02:00:00Z",
    "payload": {
        "runId": "3b241101-e2bb-4255-8caf-4136c566a962",
        "repo": "media-generation",
        "demandId": "not-a-valid-demand-id",
        "phase": "launched",
    },
}

GOOD_DESIGN_MISSION_HARVEST_STAGE = {
    "type": "design.mission",
    "timestamp": "2026-07-16T03:00:00Z",
    "payload": {
        "missionId": "c9c1b1f0-9c3a-4b7e-8b0a-6f7d8e9f0a1b",
        "targetRepo": "dashboard",
        "regime": "console-class",
        "stage": "harvest",
    },
}

GOOD_DESIGN_MISSION_THEME_GATE_APPROVED = {
    "type": "design.mission",
    "timestamp": "2026-07-16T04:00:00Z",
    "payload": {
        "missionId": "c9c1b1f0-9c3a-4b7e-8b0a-6f7d8e9f0a1b",
        "targetRepo": "plantpal",
        "regime": "inhabited-class",
        "stage": "theme-gate",
        "gateOutcome": "approved",
    },
    "origin": "host",
}

BAD_DESIGN_MISSION_UNKNOWN_REGIME = {
    "type": "design.mission",
    "timestamp": "2026-07-16T03:00:00Z",
    "payload": {
        "missionId": "c9c1b1f0-9c3a-4b7e-8b0a-6f7d8e9f0a1b",
        "targetRepo": "dashboard",
        "regime": "hybrid-class",
        "stage": "harvest",
    },
}

BAD_DESIGN_MISSION_UNKNOWN_STAGE = {
    "type": "design.mission",
    "timestamp": "2026-07-16T03:00:00Z",
    "payload": {
        "missionId": "c9c1b1f0-9c3a-4b7e-8b0a-6f7d8e9f0a1b",
        "targetRepo": "dashboard",
        "regime": "console-class",
        "stage": "review",
    },
}

BAD_DESIGN_MISSION_MISSING_TARGET_REPO = {
    "type": "design.mission",
    "timestamp": "2026-07-16T03:00:00Z",
    "payload": {
        "missionId": "c9c1b1f0-9c3a-4b7e-8b0a-6f7d8e9f0a1b",
        "regime": "console-class",
        "stage": "harvest",
    },
}


def load_state_event_schema() -> dict:
    return json.loads(STATE_EVENT_SPEC.read_text(encoding="utf-8"))


def expect_valid(schema: dict, doc: dict, label: str) -> None:
    errors = list(Draft202012Validator(schema).iter_errors(doc))
    if errors:
        raise AssertionError(f"{label}: expected valid, got errors: {errors}")
    print(f"PASS  {label}")


def expect_invalid(schema: dict, doc: dict, label: str) -> None:
    errors = list(Draft202012Validator(schema).iter_errors(doc))
    if not errors:
        raise AssertionError(f"{label}: expected invalid, but document passed")
    print(f"PASS  {label} (rejected: {errors[0].message})")


def main() -> int:
    schema = load_state_event_schema()

    expect_valid(schema, GOOD_EVENT_WITH_ORIGIN, "activity.count: known-good event with origin")
    expect_valid(schema, GOOD_EVENT_WITHOUT_ORIGIN, "activity.count: known-good event without origin")
    expect_invalid(schema, BAD_EVENT_NEGATIVE_COUNT, "activity.count: negative count (known-bad)")
    expect_invalid(schema, BAD_EVENT_MISSING_ACTIVITY, "activity.count: missing activity (known-bad)")
    expect_invalid(schema, BAD_EVENT_UNKNOWN_PROPERTY, "activity.count: unknown extra property (known-bad)")

    expect_valid(schema, GOOD_JOB_PROGRESS_FULL, "job.progress: known-good event, full fields with origin")
    expect_valid(schema, GOOD_JOB_PROGRESS_MINIMAL, "job.progress: known-good event, required fields only (proves optionality)")
    expect_invalid(schema, BAD_JOB_PROGRESS_NEGATIVE_QUEUE_DEPTH, "job.progress: negative queueDepth (known-bad)")
    expect_invalid(schema, BAD_JOB_PROGRESS_UNKNOWN_CAPABILITY, "job.progress: unknown capability enum value (known-bad)")
    expect_invalid(schema, BAD_JOB_PROGRESS_MISSING_STATUS, "job.progress: missing status (known-bad)")

    expect_valid(schema, GOOD_AGENT_RUN_LAUNCHED, "agent.run: known-good event, launched with required fields only")
    expect_valid(schema, GOOD_AGENT_RUN_FINISHED_WITH_DEMAND, "agent.run: known-good event, finished with demandId/durationMs/tokensUsed")
    expect_invalid(schema, BAD_AGENT_RUN_UNKNOWN_PHASE, "agent.run: unknown phase enum value (known-bad)")
    expect_invalid(schema, BAD_AGENT_RUN_MISSING_REPO, "agent.run: missing repo (known-bad)")
    expect_invalid(schema, BAD_AGENT_RUN_BAD_DEMAND_ID_SHAPE, "agent.run: demandId not matching id shape (known-bad)")

    expect_valid(schema, GOOD_DESIGN_MISSION_HARVEST_STAGE, "design.mission: known-good event, harvest stage, no gateOutcome")
    expect_valid(schema, GOOD_DESIGN_MISSION_THEME_GATE_APPROVED, "design.mission: known-good event, theme-gate approved, inhabited-class")
    expect_invalid(schema, BAD_DESIGN_MISSION_UNKNOWN_REGIME, "design.mission: unknown regime enum value (known-bad)")
    expect_invalid(schema, BAD_DESIGN_MISSION_UNKNOWN_STAGE, "design.mission: unknown stage enum value (known-bad)")
    expect_invalid(schema, BAD_DESIGN_MISSION_MISSING_TARGET_REPO, "design.mission: missing targetRepo (known-bad)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
