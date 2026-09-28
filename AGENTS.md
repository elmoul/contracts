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

- Java: `mvn -f gen/java/pom.xml test`
- TypeScript: `cd gen/ts && npm ci && npx tsc --noEmit`
- Python schema validators + state-event sync check (one command, stops at first failure):
  `python tests/run_all.py`

## Demand system
Cross-repo needs are raised as **demands** (never fix another repo from here).
Full reference: `../DEMAND_SYSTEM.md`.
- **Session start:** check for demand traffic — any demand dispatched *to*
  `contracts` (owner tells you at launch until the coordinator service exists),
  and any demand `contracts` raised that is now satisfied (do follow-ups, then
  move the file to `demands/archive/`).
- **To raise (origin):** write `demands/YYYY-MM-DD-<target>-<slug>.md` (envelope
  in §5), then commit it to `main` as its own standalone coordination commit
  (separate from feature work) and push — that push *is* the raise. Never
  implement any part of it in the target repo.
- **To fulfill (worker):** do the work in this repo on normal branches, then
  write `demands/fulfilled/<demand-id>-report.md` and commit to `main`. `done`
  is a claim, not a verdict — never self-certify/approve, and never notify the
  origin directly; the coordinator validates and delivers the summary.

## Release checklist (per tag) — D043 release-notification duty
A tag is not "done" at push. Per `PLATFORM_DECISIONS.md` D043
(`spec-contracts.md` §9), the release session **must also raise targeted
demands as part of the release itself**, same commit discipline as any other
demand (§ Demand system above — standalone coordination commit, push *is* the
raise):
1. **Always — to the ORIGIN** whose demand this release fulfils: *"close your
   consuming leg: re-pin and adopt."*
2. **On a BREAKING release only — additionally to every consumer** of the
   changed schema(s): *"adopt or explain by when."* Enumerate consumers via
   control-plane's `GET /registry` consumer graph (D014), not a guess.
   Additive releases raise **only** the origin demand — no fleet-wide
   "everyone bump" (D031 pins are deliberate; an additive release obligates no
   consumer to move).
3. The tag itself, `CHANGELOG.md`, and D031 acceptance can all be green and
   the release is still incomplete until these demands are raised and pushed.

Prospective only (per D043's own recorded scope) — this does not retroactively
manufacture consumer demands for releases that shipped before this checklist
step existed.

## Standing invariant (don't relax without an owner ruling)
Consumers pin a specific GitHub tag (D031 — no package registry yet); a change
here has zero effect on any consumer until they explicitly re-pin. Before
calling any release done, run the real D031 acceptance test: a clean install
from the actual tagged URL in a fresh venv/npm cache/`.m2` repo, not just a
local build. Two past releases (v0.2.1 npm, v0.6.2 Python) shipped believing an
untested packaging assumption — verify, don't assume.

<!-- brain-adopt:section -->
## `.brain` — operational memory (adopted 2026-08-02, brain-toolkit v0.6.2)

This repo carries `.brain/`, the platform's operational-memory system
(`../platform-vault/spec-agent-memory-system.md`, governed by D052/D061).
Every session opens a session file before any code change and closes it
before ending -- see `.brain/conventions.md` (references the platform's
full worker-agent conventions rather than duplicating them) and
`.brain/architecture.md`.

**Always invoke the shims through `python`.** `.brain/bin/brain` is an
extensionless Python script: PowerShell (this platform's primary shell) will
not execute it, and depending on how it is invoked you may get no output and
no session file rather than a clear error -- so an unprefixed shim call can
look like it worked when nothing at all was written. Always
prefix `python`, and check that a new file appeared under
`.brain/sessions/`.

- **Open** (PowerShell / cmd, from the repo root):
  `python .brain\bin\brain session open "<task>" --priority <1-3>` before
  any code change. Under bash/sh use forward slashes:
  `python .brain/bin/brain session open "<task>" --priority <1-3>`.
- **Close:** `python .brain\bin\brain session close` (bash:
  `python .brain/bin/brain session close`) -- fills/confirms `status`,
  `changes`, `lessons`, `vault_sync`; the `PROGRESS.md` handoff block is a
  generated projection of the session file, never hand-authored separately.
- **Pin mechanism:** `.brain/bin/brain` and `.brain/bin/structurer` are thin
  shims resolving `../brain-toolkit-worktrees/<pin>/bin/<tool>` via
  `.brain/toolkit-pin` (currently `v0.6.2`) -- a fix or version bump is a
  one-line edit to `.brain/toolkit-pin`, never a hand-edit of the shim
  itself.
- Never hand-edit generated files (`AGENT.md`, `.brain/knowledge/*`,
  `.brain/graph.md`, `.brain/index.db`) -- human overrides go in
  `.brain/overrides.md`.

Adopted via `brain-toolkit`'s `bin/adopt` on 2026-08-02. Fresh adoption -- no
session history yet.
