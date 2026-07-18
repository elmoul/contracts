---
id: contracts-20260716-platform-vault-w1-gate
date: 2026-07-16
from: contracts
to: [platform-vault]
capability: platform-vault records v0.14.0 tagged and Wave 6 W1's gate met (tag + one consumer/Java pin D031-proven), confirming the wave's dependency root landed so W2+ can proceed
acceptance-criteria:
  - "PLATFORM_STATE.md's `contracts` row reads v0.14.0, citing this release, D047/D048/D051/D053, and this demand"
  - "PLATFORM_GANTT.md's Wave 6 entry (or MEDIA_AGENTS_WAVE_PACK.md §6's W1 row) records W1 as complete, not just \"landing/planned\""
  - Wave sessions W2+ are understood to be unblocked now that the dependency root (§5.1) has shipped
needs-owner: true
status: archived
---

# Demand — close W1: `contracts` v0.14.0 tagged, wave dependency root landed

## What we need

Per `contracts`' own D043 release-notification duty (`CLAUDE.md` "Release
checklist (per tag)"; mirrored in `DEPLOYMENT.md` step 6): every release
raises a demand `to: [<origin>]` ("close your consuming leg: re-pin and
adopt"), additive or breaking; **on an additive release this is the only
demand raised — no fleet-wide "everyone bump"** (D031 pins are deliberate).
`v0.14.0` is additive (new schema group + three new `oneOf` members; no
existing required field touched).

**Naming `platform-vault` as the origin is a judgment call, flagged for
ruling (see "Owner-ruling candidate" below) rather than assumed silently.**
Every past exercise of this duty (v0.9.0 → `ai-gateway`, v0.10.0 →
`observability`, v0.11.0 → `demand-coordinator`, v0.13.0 → `ai-gateway`) had
a single downstream-consumer repo that had raised a real demand file asking
`contracts` for the thing. `v0.14.0` doesn't: the ask is
`docs/MEDIA_AGENTS_WAVE_PACK.md` §5.1 ("`contracts` → v0.14.0 (demand to
`contracts`)"), a wave-level amendment brief landed by `platform-vault`'s own
W0 session (which mints D047-D053, the three new specs, and the wave's
Gantt/state entries) rather than filed from any one consumer's own
`demands/` outbox. `platform-vault` is the closest real analogue to "whoever
asked," and precedent for a `platform-vault` <-> `contracts` demand
relationship already exists (`demands/fulfilled/platform-vault-20260713-contracts-release-notification-duty-report.md`
— platform-vault as origin, contracts as worker, for the D043 checklist
mirror itself).

**What shipped:**
- New `schemas/ai-gateway/job.yaml`: `ai.job.request`/`ai.job.status` (async
  job envelope, D047) — `error` conditionally required when `status:
  failed` (D023 pattern).
- Three new `state.event` payload types: `job.progress` (D047,
  `media-generation`), `agent.run` (D048, `agent-runner`), `design.mission`
  (D051, `design-studio`).
- All three bindings regenerated and green (`mvn test` 12/12;
  `npx tsc --noEmit` clean; `python tests/run_all.py` — all validators
  passed). Python's `state_event.py` regen converted 5 pre-existing enums
  (`Status`/`Phase`/`Conclusion`/`Status1`/`Origin`) from plain `Enum` to
  `StrEnum` as a documented side effect — behaviorally additive, see
  `CHANGELOG.md` v0.14.0.
- Tagged `v0.14.0` (commit `3a210cf`); worktree
  `../contracts-worktrees/v0.14.0` created (D042 mechanism); Java binding
  installed to local `.m2` (D031) at `io.platform:contracts:0.14.0` and
  verified — the jar's contents were inspected directly
  (`jar tf`), confirming `AiJobRequest`, `AiJobStatus`, `JobProgressEvent`,
  `AgentRunEvent`, `DesignMissionEvent` (plus nested enums) are actually
  packaged, not just a green `BUILD SUCCESS` (this repo has shipped a
  build-succeeds-but-generates-wrong empty-stub defect before, v0.9.0's
  `capabilities` bug). This satisfies the wave's own W1 gate — **"tag + one
  consumer pin proven"** (`MEDIA_AGENTS_WAVE_PACK.md` §6) — the one consumer
  proven is the Java `.m2` install, the mechanism `ai-gateway` (W5,
  Java/Spring) will pin against.

## Why / what's blocked

Nothing is hard-blocked on `contracts`' side. Per the wave pack's own §5.1
sequence note, "nothing else builds until the wave tag lands" — this demand
exists to confirm that landing, back to whoever is coordinating the wave's
gates, so W2+ know they're unblocked. `contracts` itself has no further work
queued for Wave 6 until a later wave turn needs another schema change.

**Explicitly out of scope for this demand (D043's additive-release rule —
origin only, no fleet-wide "everyone bump"):** separate re-pin-and-adopt
demands to `ai-gateway` (wave pack §5.2, its own W5 amendment brief),
`state-feed`/`dashboard` (§5.6, their own W7 amendment brief), or any hub
Python consumer. Each of those is the wave pack's own separately-scheduled
demand, meant to be raised at that repo's own wave turn — not fabricated
here. Raising them now, from W1, would both violate D043's additive-release
scope and jump ahead of the wave's own sequencing: `state-feed`'s re-pin is
explicitly meant to land *before* any producer emits the three new event
types, and none of the producing repos (`media-generation`, `agent-runner`,
`design-studio`) exist yet — there is nothing for a strict validator to
reject today, and no consumer for whom "adopt" is even actionable yet.

## Owner-ruling candidate

D043 (`CLAUDE.md`/`DEPLOYMENT.md`/`PLATFORM_DECISIONS.md`) was written and
first exercised (v0.13.0) against a single-consumer-demand release. It does
not say what "the origin" means for a **wave-commissioned, dependency-root**
release that precedes all of its consumers rather than fulfilling one
existing consumer's filed ask. This session resolved the ambiguity by
targeting `platform-vault` rather than guessing a downstream consumer
(`ai-gateway` was the other candidate considered — rejected because it has
no more claim to "the origin" here than `state-feed`/`dashboard`, all three
being wave-scheduled consumers per §5.2/§5.6, not askers). Flagging for an
explicit ruling on whether "target `platform-vault` for a wave-dependency-root
release" should become the standing D043 convention, so the next
dependency-root release in this wave (if any) doesn't have to re-derive it.

## Acceptance criteria

See frontmatter.

## What we do once closed

`contracts` archives this file to `demands/archive/` once the coordinator
reports it satisfied. No further action expected on `contracts`' side for
W1. `ai-gateway`'s (W5) and `state-feed`/`dashboard`'s (W7) own re-pins
remain their own separately-scheduled demands per the wave pack — `contracts`
does not raise or track those from here.
