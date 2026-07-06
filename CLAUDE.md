# contracts — agent brief

@../conventions/conventions-for-agents.md

## This hexagon
The dependency root of the platform. Defines every cross-hexagon port as a
versioned schema (OpenAPI 3.1 for sync HTTP, JSON Schema for async events/repo
self-description) and generates the Java/TypeScript/Python bindings every other
hexagon pins to. Side: shared · Kind: buildtime · Status: active. Depends on:
nothing — everything else pins this, not the other way around.

Spec: `../platform-vault/spec-contracts.md` — read it fully before writing
anything; its build-notes section is your work order.

## Commands
No single build command — this repo publishes three separate language
bindings. See README.md/DEPLOYMENT.md for the per-language codegen and test
steps (Java under `gen/java` via Maven, TS under `gen/ts`, Python under
`gen/python`).

## Standing invariant (don't relax without an owner ruling)
Consumers pin a specific GitHub tag (D031 — no package registry yet); a change
here has zero effect on any consumer until they explicitly re-pin. Before
calling any release done, run the real D031 acceptance test: a clean install
from the actual tagged URL in a fresh venv/npm cache/`.m2` repo, not just a
local build. Two past releases (v0.2.1 npm, v0.6.2 Python) shipped believing an
untested packaging assumption — verify, don't assume.
