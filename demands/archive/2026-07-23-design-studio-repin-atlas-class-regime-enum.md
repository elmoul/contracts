---
id: contracts-20260723-design-studio-repin-atlas-class-regime-enum
date: 2026-07-23
from: contracts
to: [design-studio]
capability: design-studio re-pins contracts to v0.17.0 and adopts the third atlas-class Regime member on design.mission/design.designSystem state-event emissions
acceptance-criteria:
  - "design-studio's contracts pin (requirements.txt or equivalent per-language manifest) reads 0.17.0"
  - "design-studio's event_sink_state_feed.py adapter (or its TS/Java equivalent) can construct ContractRegime('atlas-class') / the generated Regime.atlas_class member without a schema validation error"
  - "any workaround, stopgap, or comment in design-studio's producer code that predates atlas-class support is removed once the mission/design-system emission paths that need it are updated"
needs-owner: false
status: archived
---

# Demand — re-pin `contracts` v0.17.0 and adopt the `atlas-class` `Regime` member

## What we need

Per `contracts`' own D043 release-notification duty (`CLAUDE.md` "Release
checklist (per tag)"): every release closes its own loop by raising a demand
to the origin whose need it fulfils. `v0.17.0` fulfilled `design-studio`'s
own demand (`design-studio-20260723-contracts-atlas-class-regime-enum`) —
this is that demand's "re-pin and adopt" close-the-loop, not a new ask.

`state.event`'s shared `Regime` enum (used by both `DesignMissionPayload`
and `DesignSystemPayload`) gained a third member, `atlas-class`, alongside
the existing `console-class`/`inhabited-class`. No other field, required-ness,
or payload shape changed in this release. Full detail: `CHANGELOG.md`'s
`v0.17.0` entry and
`demands/fulfilled/design-studio-20260723-contracts-atlas-class-regime-enum-report.md`
(this repo).

## Why / what's blocked

Nothing is hard-blocked on `contracts`' side. `design-studio`'s
`event_sink_state_feed.py:188` and `:210` construct `ContractRegime(...)`
on every mission and design-system state event; until `design-studio`
re-pins to `v0.17.0`, any attempt to emit an `atlas-class` regime event
will keep failing against the older, two-member enum.

## Acceptance criteria

See the frontmatter `acceptance-criteria` list above.

## What we do once closed

`contracts` archives
`demands/2026-07-23-design-studio-repin-atlas-class-regime-enum.md` to
`demands/archive/` once the coordinator reports this satisfied. No further
action expected on this repo's side — this demand exists purely to close
the release-notification duty, not to request new work from `contracts`
itself.
