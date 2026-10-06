---
id: contracts-20261006-youtrack-adopt-contracts-0-49-0
date: 2026-10-06
from: contracts
to: [youtrack]
capability: "The planner pins contracts v0.49.0 and its POST /plans/from-brief request, response and error are validated against the published planner.brief-project schemas instead of hand-written copies"
acceptance-criteria:
  - "The planner's contracts pin moves from v0.47.0 to v0.49.0 in every place the repository records it (planner/requirements.txt, HEXAGON.md and any Dockerfile or compose line that carries the version, found by searching the repository for the old version string; the fleet's 'three places' pin rule), and the pin is installable the way the repository's other pins are: contracts v0.49.0 exists as a local tag (contracts commit ec53f01 region, tag v0.49.0) and is NOT pushed to GitHub by anyone but the owner, so the worker installs the bindings from the local contracts worktree for its tests exactly as other repos did before an owner push (read how an earlier pin bump in this repository's git log did it) and states plainly in the report that a fresh image build resolves the git+https pin only after the owner pushes contracts and its tag"
  - "The planner's from-brief request model and response builder are checked against the new generated bindings (schemas/youtrack/planner.brief-project-request.json, planner.brief-project-response.json, planner.brief-project-error.json, bindings under gen/python): a conformance test builds the planner's real request body and real response and error payloads (the ones its own tests already produce) and validates them against the contracts models; the hand-written duplicate shapes are removed where the contracts models can replace them without changing behaviour, and kept (with a one-line reason) where they cannot. No behaviour change on the wire: the 374-test planner suite passes unchanged apart from added conformance tests, and the response of every existing route is byte-identical"
  - "CHANGELOG.md and HEXAGON.md record the pin and the conformance; the worker rebuilds and restarts nothing and says plainly that the running planner keeps its current image until the owner rebuilds and recreates it (a runtime step)"
needs-owner: false
status: archived
---

# Demand - youtrack: adopt contracts v0.49.0 for the from-brief call

## What we need
contracts v0.49.0 publishes the shape of `POST /plans/from-brief`. The planner still carries its own copy and an older pin.

## Why / what's blocked
Nothing is blocked; two copies of one shape drift. The first live use of the call is imminent, so the conformance test is the cheap guard.

## What we do once closed
The planner's shape is the contract's, and Factory (a separate demand) validates its request against the same schema.

## Not in scope
Any change to the endpoint's behaviour, Factory's code, and pushing anything.
