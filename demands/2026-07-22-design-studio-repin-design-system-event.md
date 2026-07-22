---
id: contracts-20260722-design-studio-repin-design-system-event
date: 2026-07-22
from: contracts
to: [design-studio]
capability: design-studio re-pins contracts to v0.16.0 and adopts the generated DesignSystemEvent/DesignSystemPayload types, closing the consuming leg of its own demand
acceptance-criteria:
  - "design-studio's contracts pin (requirements.txt / equivalent per-language manifest) reads 0.16.0"
  - "DesignSystem registry emissions (S-B1) construct platform_contracts.state_feed.state_event.DesignSystemEvent / DesignSystemPayload (or the TS/Java equivalents, whichever design-studio's producer is written in) instead of the hand-shaped stopgap dict"
  - "the stopgap-dict code path and any comment documenting it as a workaround is removed"
needs-owner: false
status: open
---

# Demand — re-pin `contracts` v0.16.0 and adopt `design.designSystem`

## What we need

Per `contracts`' own D043 release-notification duty (`CLAUDE.md` "Release
checklist (per tag)"): every release closes its own loop by raising a demand
to the origin whose need it fulfils. `v0.16.0` fulfilled `design-studio`'s
own demand (`design-studio-20260722-contracts-design-system-state-event`) —
this is that demand's "re-pin and adopt" close-the-loop, not a new ask.

`state.event`'s `oneOf` union gained a tenth member, `design.designSystem`
(`DesignSystemEvent`/`DesignSystemPayload`), mirroring `design.mission`'s
existing envelope shape exactly: `designSystemId` (UUID), `name`, `slug`
(D002-style functional-identifier pattern), `version` (semver, optionally
`v`-prefixed), `regime` (reuses `DesignMissionPayload`'s existing
`console-class`/`inhabited-class` enum verbatim — no new regime vocabulary),
`status` (new enum: `draft`/`validated`/`retired`), `origin` (new enum:
`owner-built`/`mission-built` — distinct from `state.event`'s own unrelated
envelope-level `Origin` field, which means `host`/`hub`), `sourceMissionId`
(optional UUID, null when `origin` is `owner-built`), `change` (new enum:
`created`/`validated`/`retired`/`release`). Additive, non-breaking — no
existing `state.event` member's shape changed.

Full detail: `CHANGELOG.md`'s `v0.16.0` entry and
`demands/fulfilled/design-studio-20260722-contracts-design-system-state-event-report.md`
(this repo).

## Why / what's blocked

Nothing is hard-blocked on `contracts`' side. The technical debt
`design-studio`'s own demand described (S-B1's DesignSystem registry
emitting a hand-shaped stopgap dict instead of a schema-valid event) stays
live until `design-studio` re-pins and swaps the stopgap for the shipped
`DesignSystemEvent`/`DesignSystemPayload` shape.

## Acceptance criteria

See the frontmatter `acceptance-criteria` list above.

## What we do once closed

`contracts` archives `demands/2026-07-22-design-studio-repin-design-system-event.md`
to `demands/archive/` once the coordinator reports this satisfied. No further
action expected on this repo's side — this demand exists purely to close the
release-notification duty, not to request new work from `contracts` itself.
