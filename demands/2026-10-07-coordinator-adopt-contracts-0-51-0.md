---
id: contracts-20261007-coordinator-adopt-contracts-0-51-0
date: 2026-10-07
from: contracts
to: [demand-coordinator]
capability: "The coordinator pins contracts v0.51.0 and validates the optional typed 'blockers' of a blocked fulfillment report against the published demand.fulfillment schema instead of parsing the field only by itself"
acceptance-criteria:
  - "The coordinator's contracts pin moves to v0.51.0 in EVERY place the repository records it (pom.xml, the Dockerfile contracts-m2 COPY destination, HEXAGON.md and any other found by searching the repository for the old version string): the repository's own comment says 'a pom repin is only half a repin'. contracts v0.51.0 is a local tag only and is NOT pushed to GitHub by anyone but the owner: tests resolve the artifact from the local ~/.m2 (the way earlier pin bumps did), and the report states plainly which compose line in runtime/docker-compose.local.yml (service demand-coordinator) must also move to 0.51.0 and that it is runtime's (a demand to runtime is raised from the report, the worker edits no other repository)"
  - "A blocked report whose blockers validate against the schema keeps working exactly as shipped; a blocked report whose blockers do NOT validate is shown as blocked with cause 'blockers invalid' and the validation reason (never silently dropped, never an error that hides the demand); a report with blockers on a non-blocked status is refused as the schema says; an old blocked report without blockers still reads as 'blocked, cause not recorded'. No change to any route or response shape, and the existing suite (mvn -q -o test) passes with the added conformance tests; CHANGELOG.md and HEXAGON.md record the pin; nothing is rebuilt or restarted, and the report says the running coordinator keeps the old behaviour until the owner rebuilds and recreates it (a runtime step, which also needs the compose pin above)"
needs-owner: false
status: open
---

# Demand - demand-coordinator: adopt contracts v0.51.0 for blockers

## What we need
contracts v0.51.0 publishes the optional typed blockers on demand.fulfillment. The coordinator parsed the field itself because the schema did not carry it; now it should validate against the schema.

## Why / what's blocked
Nothing is blocked; two copies of one shape drift, and the coordinator is the component the owner trusts for approval.

## What we do once closed
The coordinator and the workers' reports share one validated blocker shape.

## Not in scope
Any new behaviour, the dashboard, and pushing anything.
