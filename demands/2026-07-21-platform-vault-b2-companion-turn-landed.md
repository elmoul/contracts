---
id: contracts-20260721-platform-vault-b2-companion-turn-landed
date: 2026-07-21
from: contracts
to: [platform-vault]
capability: platform-vault records v0.15.0 tagged (Wave 7 session B-2 — the Companion turn contract, `stage.companion.turn`), and holds the plantpal consumer-pin assessment evidence for the owner's own repin-sequencing decision
acceptance-criteria:
  - "PLATFORM_STATE.md's `contracts` row reads v0.15.0, citing this release and Wave 7 session B-2"
  - "the plantpal consumer-pin assessment below (v0.7.0 -> v0.15.0, all six used contracts) is available to whoever sequences plantpal's own repin session, without needing to re-derive it from CHANGELOG.md"
needs-owner: true
status: open
---

# Demand — close B-2: `contracts` v0.15.0 tagged, Companion turn contract landed

## What we need

Per this repo's own D043 release-notification duty (`CLAUDE.md` "Release
checklist (per tag)"), every release raises a demand `to: [<origin>]`. This
release, like v0.14.0 before it, has **no single filed consumer demand to
point back to** — it is an owner-commissioned session ("go B-2", Wave 7,
`platform-vault`'s own `docs/WAVE_7_PACK_DRAFT.md` / D066), not a fulfillment
of something plantpal (or any other repo) asked `contracts` for in its own
`demands/` outbox.

**Per D054** (which already ruled this exact ambiguity for v0.14.0): "the
origin" for a wave-commissioned `contracts` release with no filed consumer
demand is `platform-vault`, and such releases form a linked list of origins
backpointing by demand-id. This demand continues that list:
**`prev: contracts-20260716-platform-vault-w1-gate`** (v0.14.0's HEAD,
archived, D054-ruled 2026-07-18).

**What shipped:**
- New `schemas/stage/companion.turn.yaml` — `stage.companion.turn`
  (`CompanionMessageRequest`/`StageContext`/`CompanionMessageResponse`), the
  rung-0 Companion turn contract, landed verbatim from plantpal's own proven
  Wave 7 A-4 implementation (`CompanionController`/`CompanionServiceImpl`),
  per doctrine §12 ("spec from working code, never the abstract"). Brand-new
  `stage/` domain (a cross-tenant UI-pattern group, matching `app/`'s
  existing precedent — not a single-repo-owned group).
- Deliberately **not** landed this release (named in `CHANGELOG.md` v0.15.0
  so the boundary is governed, not forgotten): the intent-bus resolution
  contract (`{cards, data, arrangement, confidence}`, no implementation
  yet), the card-anatomy serialization format (no implementation yet), the
  state→material mapping-table format (stays studio-local, D066).
- **Additive-only, mechanically verified**: `git diff --stat -- schemas/`
  against the pre-release tree is empty apart from the one new file — zero
  existing schema touched.
- All three bindings regenerated and green: Java (`mvn -f gen/java/pom.xml
  clean test`, BUILD SUCCESS, 12/12; zero `com.google.gson` imports), fresh
  `.m2` install with `jar tf` confirming `CompanionMessageRequest`/
  `StageContext`/`CompanionMessageResponse` actually packaged (not just a
  green build). TypeScript (`openapi-typescript`, `npx tsc --noEmit --strict`
  clean, `file:`-scratch consumer project built against the real `dist/`).
  Python (`datamodel-codegen`, `Confidence` came out `StrEnum` correctly,
  scratch-venv `pip install ./gen/python` + round-trip verified). Full
  `python tests/run_all.py` (11 validators + state-event sync check) green,
  including the new `tests/validate_stage_companion_turn.py` (10 assertions).
- Tagged `v0.15.0`.

## Consumer-pin assessment (the actual deliverable this demand carries)

plantpal (Java binding) pins **v0.7.0** and uses six contracts: `app.health`,
`app.manifest`, `ai.request`, `ai.response`, `dimension.event`,
`state.event`. Walked every intervening CHANGELOG entry (v0.8.0 -> v0.15.0)
against exactly those six schemas:

- `app.health`, `app.manifest`, `ai.request`, `dimension.event`: **zero
  changes** since v0.7.0.
- `ai.response`: **one additive change** (v0.13.0 — optional `skipped`
  field; `result`/`model`/`provider` required -> optional, a backward-
  compatible widening). plantpal's `GatewayClient`/`ChatServiceImpl` read it
  via plain getters, no exhaustive-shape assertion — unaffected. plantpal
  never declares `downshiftPolicy: skip`, so `skipped: true` never actually
  reaches it today.
- `state.event`: **two additive changes** (v0.7.0's own `activity.count`,
  already plantpal's baseline; v0.14.0's three more `oneOf` members). plantpal
  only **produces** `state.event` (`app.status`/`activity.count`, via the
  concrete generated classes, never the union type) — the new members are
  structurally inert for it.
- Java package/artifact coordinates unchanged across every intervening
  release — no existing import path would move.

**Assessment: a safe micro-session, not a real migration.** Full detail,
including the per-contract evidence trail, is in `CHANGELOG.md`'s v0.15.0
entry (section "plantpal consumer-pin assessment"). This demand does not
itself request or schedule plantpal's repin — that sequencing decision stays
the owner's, per this session's own brief.

## Why / what's blocked

Nothing is hard-blocked on `contracts`' side. This demand exists to close the
loop back to the coordinating record (same pattern as v0.14.0's W1-gate
demand) and to hand the consumer-pin evidence to whoever sequences plantpal's
own repin session next, without that session needing to re-derive the
six-contract diff from scratch.

## What we do once closed

`contracts` archives this file to `demands/archive/` once the coordinator
reports it satisfied. No further action expected on `contracts`' side for
B-2. A future `stage/` domain addition (if the intent-bus or card-anatomy
contracts get a working implementation to land from) would continue this
same linked list, `prev: contracts-20260721-platform-vault-b2-companion-turn-landed`.
