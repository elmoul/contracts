---
id: contracts-20260804-design-studio-repin-guided-turn-class-regime-enum
date: 2026-08-04
from: contracts
to: [design-studio]
capability: design-studio re-pins contracts to v0.18.0 and adopts the fourth guided-turn-class Regime member on design.mission/design.designSystem state-event emissions
acceptance-criteria:
  - "design-studio's contracts pin (requirements.txt or equivalent per-language manifest) reads 0.18.0"
  - "design-studio's event_sink_state_feed.py adapter (or its TS/Java equivalent) can construct ContractRegime('guided-turn-class') / the generated Regime.guided_turn_class member without a schema validation error"
  - "design-studio's value-projection emits the regime verbatim as 'guided-turn-class' — no mapping table, since the contracts spelling matches the three existing members"
  - "any workaround, stopgap, or comment in design-studio's producer code that predates guided-turn-class support is removed once the mission/design-system emission paths that need it are updated"
needs-owner: false
status: archived
---

# Demand — re-pin `contracts` v0.18.0 and adopt the `guided-turn-class` `Regime` member

## What we need

Per `contracts`' own D043 release-notification duty (`CLAUDE.md` "Release
checklist (per tag)"): every release closes its own loop by raising a demand
to the origin whose need it fulfils. `v0.18.0` fulfilled `design-studio`'s
own demand
(`design-studio-20260804-contracts-guided-turn-class-regime-enum`) — this is
that demand's "re-pin and adopt" close-the-loop, not a new ask.

`state.event`'s shared `Regime` enum (used by both `DesignMissionPayload`
and `DesignSystemPayload`) gained a fourth member, `guided-turn-class`,
alongside the existing `console-class`/`inhabited-class`/`atlas-class`. No
other field, required-ness, or payload shape changed in this release — it is
an enum widening, so every existing three-regime producer and consumer keeps
validating unchanged. Full detail: `CHANGELOG.md`'s `v0.18.0` entry and
`demands/fulfilled/design-studio-20260804-contracts-guided-turn-class-regime-enum-report.md`
(this repo).

The one-line re-pin:

```
platform-contracts @ git+https://github.com/elmoul/contracts.git@v0.18.0#subdirectory=gen/python
```

## Why / what's blocked

Nothing is hard-blocked on `contracts`' side. `design-studio`'s
`event_sink_state_feed.py` constructs `ContractRegime(...)` on every mission
and design-system state event; until `design-studio` re-pins to `v0.18.0`,
any attempt to emit a `guided-turn-class` regime event will keep failing
against the older, three-member enum.

## Acceptance criteria

See the frontmatter `acceptance-criteria` list above.

## What we do once closed

`contracts` archives
`demands/2026-08-04-design-studio-repin-guided-turn-class-regime-enum.md` to
`demands/archive/` once the coordinator reports this satisfied. No further
action expected on this repo's side — this demand exists purely to close the
release-notification duty, not to request new work from `contracts` itself.
