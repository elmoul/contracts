---
functionalName: contracts
kind: buildtime
side: shared
status: active
deps: []
spec: spec-contracts.md
decisions:
  - D002
  - D007
  - D009
  - D015
  - D022
  - D029
---

# contracts

## Purpose

The dependency root of the platform. Defines every cross-hexagon port as a versioned schema and generates the language bindings (Java, TypeScript, Python) every other hexagon consumes. Not a runtime service.

## Responsibilities

- Define all cross-hexagon contracts as versioned schemas (OpenAPI 3.1 for sync HTTP; JSON Schema for async events and repo self-description)
- Version each contract independently (semver) and maintain the changelog
- Generate and publish language bindings (Maven artifact, npm package, pip package)
- Serve as the leaf of the dependency graph — nothing imported here, everything pins this

## Boundaries — must NOT

- No business logic, no runtime implementation
- No theme references (D002) — theme-neutral by definition
- No secrets, config, or environment values
- No outbound dependencies — contracts depends on nothing
- Not a deployed service — ships as packages only

## Ports

### Inbound

None — consumed as versioned packages, not called at runtime.

### Outbound

None.

## Data Owned

All cross-hexagon contract schemas (versioned source of truth in `schemas/`).

## Key Decisions

- [[D002]] — functional names only; this repo is where that rule is most sacred
- [[D007]] — hexagonal architecture; ports at real boundaries, no cross-hexagon imports except this repo
- [[D009]] — the five app contracts every app must implement
- [[D015]] — dependency root; built first, pinned by all
- [[D022]] — AI gateway contracts (ai.request/response, ai.preflight.*)
- [[D029]] — state-feed contracts (state.event, state.projection.guest)

## Open Questions

See spec-contracts.md §8.
