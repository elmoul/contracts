# contracts — architecture (stable facts)

<!--
Hand-maintained (this file + conventions.md + overrides.md + config.yml are
the hand-edited files under .brain/ -- see conventions.md for the source of
truth this repo's `.brain` follows). Seeded by `brain-toolkit`'s `bin/adopt`
on 2026-08-02 (toolkit v0.6.2) from this repo's own HEXAGON.md and README.md at
adoption time. FRESH ADOPTION -- no history, no build-order churn, and no
decisions have been captured here yet; this is a skeleton, not a record of
anything that happened before adoption. Keep this file to STABLE design
facts as they're established -- build-order and open-questions churn
belongs in the spec / session log, not here.
-->

## Purpose

The platform's shared contract kernel. Schema-first; every other hexagon pins a version of this repo.

## Stable identity facts (seeded from HEXAGON.md at adoption time)

- functionalName: `contracts` · kind: `buildtime` · side: `shared`
- Deps (from HEXAGON.md): `[`, `]`
- Governing decisions (from HEXAGON.md): D002, D007, D009, D010, D015, D022, D029
- Full spec: `../platform-vault/spec-contracts.md` -- this file is a
  stable-facts seed, not a replacement; the spec is still the authoritative
  work order.

<!-- Nothing else has been established yet. Add stable facts here as this
     repo's own sessions confirm them. -->
