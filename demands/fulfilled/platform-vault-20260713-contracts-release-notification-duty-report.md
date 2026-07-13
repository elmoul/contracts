---
demandId: platform-vault-20260713-contracts-release-notification-duty
worker: contracts
status: done
shipped: ["CLAUDE.md + DEPLOYMENT.md updated on main (commit landing this report)"]
date: 2026-07-13
---

# Fulfillment report — contracts: mirror the D043 release-notification duty into the repo-side release checklist

`status: done` here is a claim, not a verdict — per `DEMAND_SYSTEM.md` §4,
this report is `contracts`' only output for this demand. `contracts` does not
self-certify and has not notified `platform-vault` directly; the coordinator
validates and delivers the summary once the owner approves.

## What shipped

`CLAUDE.md` gained a new **"Release checklist (per tag) — D043
release-notification duty"** section (placed before the existing "Standing
invariant" section, right after "Demand system", since it's operationally the
same reflex): on every tag, raise a demand `to: [<origin>]` ("re-pin and
adopt"); on a **breaking** release additionally raise a demand to every
consumer of the changed schema(s) ("adopt or explain by when"), enumerated
via control-plane's `GET /registry` consumer graph (D014) rather than
guessed; additive releases raise only the origin demand (no fleet-wide
"everyone bump" — D031 pins stay deliberate). States explicitly that the tag,
`CHANGELOG.md`, and D031 acceptance can all be green and the release is still
incomplete until those demands are raised and pushed. Also states the
prospective-only scope verbatim (no retroactive demands for pre-existing
releases), matching D043's own recorded consequence.

`DEPLOYMENT.md`'s existing numbered "Releasing (tag + version bump)"
checklist — the doc that actually holds the step-by-step release procedure —
gained a new step 6 pointing at the same rule, so the operational checklist a
release session works from top-to-bottom carries the duty too, not just the
prose summary in `CLAUDE.md`.

No schema, binding, or `CHANGELOG.md` change — this is a pure process/docs
fulfillment, so no version bump per this repo's own versioning convention
(versions track schema/binding changes, not process docs).

## Owner-ruling conflict surfaced and resolved before acting

The session that received this demand was also asked (by its user, not by
this demand) to retroactively raise the v0.12.0 re-pin/consumer-adopt demands
this duty describes. Reading the demand's full body and
`PLATFORM_DECISIONS.md`'s D043 entry directly first surfaced that D043's own
recorded "Consequences" clause is explicit: *"Does not retroactively
manufacture consumer demands for the already-shipped v0.9.0–v0.12.0 (the
register already tracks their re-pin state); the duty is prospective."*
Flagged that conflict to the user before acting rather than either silently
complying or silently ignoring the recorded ruling; the user chose to honor
the recorded ruling and skip the retroactive demands. Noting this here so the
vault (and any future audit) can see the conflict was seen and resolved in
the owner-ruling's favor, not missed.

## Acceptance criteria — self-check against the demand

- [x] `contracts`' `CLAUDE.md` gains a release-checklist step citing D043: on
      every tag, raise a demand to the ORIGIN whose need the release fulfils
      — "re-pin and adopt."
- [x] The same step states a BREAKING release additionally raises a demand to
      every consumer of the changed schema(s) — "adopt or explain by when" —
      via the control-plane / `GET /registry` consumer graph (D014); an
      ADDITIVE release raises only the origin demand.
- [x] The checklist makes clear the tag is not "done" until those demands are
      raised and pushed (a standalone coordination commit per
      `DEMAND_SYSTEM.md` §3).

## What platform-vault (the origin) needs to know

Nothing further expected from `contracts` — per the demand's own "what we do
once closed," the vault archives this demand once it sees the checklist step
landed; no vault-side change is implied (D-log entry and spec amendment were
already shipped before this demand was raised). This is the first `contracts`
release session since D043 landed; the next tagged release from this repo is
where the duty is actually exercised for real, not this docs-only session.
