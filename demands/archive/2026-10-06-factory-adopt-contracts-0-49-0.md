---
id: contracts-20261006-factory-adopt-contracts-0-49-0
date: 2026-10-06
from: contracts
to: [factory]
capability: "Factory pins contracts v0.49.0 and its Harvest hand-over request and the planner answer it stores are validated against the published planner.brief-project schemas instead of hand-written copies"
acceptance-criteria:
  - "Factory's contracts pin moves from v0.48.0 to v0.49.0 in every place the repository records it (HEXAGON.md, the requirements or pyproject pin, the Dockerfile or build script and any compose line carrying the version, found by searching for the old version string; the fleet's 'three places' pin rule). contracts v0.49.0 is a local tag only and is NOT pushed to GitHub by anyone but the owner: the worker installs the bindings from the local contracts worktree for its tests as earlier pin bumps in this repository's git log did, factory/build-image.ps1 is left working for the owner's next build (read how it resolves the pin), and the report states plainly that a fresh build resolves a git+https pin only after the owner pushes contracts and its tag"
  - "The hand-over request Factory builds (the whole approved revision record, the approval record, projectKey, projectName, appName, model, briefId) and the planner answer it stores and shows (created, alreadyPresent, failed with codes, stateFields, ownerSteps, plannerEditsEnv, replayed) and the closed error shape are validated against the generated models for planner.brief-project-request, -response and -error (gen/python in contracts v0.49.0): a request that does not validate is refused before it is sent, an answer that does not validate is recorded as planner_invalid_response exactly as an unreadable answer is today. The skipped-if-missing test that compared Factory's request with the planner repository's own builder is kept or replaced by a conformance test against the contracts models and the captured exchanges contracts ships (tests/fixtures/youtrack-brief), whichever the repository's rules allow"
  - "No change on the wire for a valid exchange and no change to any other route; the existing suite (factory/.run/venv048 only, never another interpreter) passes with added conformance tests; CHANGELOG.md and HEXAGON.md record the pin; the worker rebuilds and restarts nothing and says plainly that the running Factory keeps its image until the owner rebuilds and recreates it (a runtime step)"
needs-owner: false
status: archived
---

# Demand - factory: adopt contracts v0.49.0 for the Harvest hand-over

## What we need
contracts v0.49.0 publishes the shape of the planner's from-brief call. Factory sends and stores that shape from its own copy.

## Why / what's blocked
Nothing is blocked; the validation catches drift between Factory and the planner before the first live hand-over loses a three-minute call to a shape mistake.

## What we do once closed
Factory and the planner share one validated shape.

## Not in scope
Any change to the hand-over's behaviour, the planner's code, and pushing anything.
