---
id: contracts-20260927-factory-repin-demand-after-binding
date: 2026-09-27
from: contracts
to: [factory]
capability: Close the consuming leg of factory-20260927-demand-after-binding — Python Demand binding supports `after` in contracts v0.32.0
acceptance-criteria:
  - "factory re-pins its Python contracts dependency to v0.32.0 (git+https://github.com/elmoul/contracts.git@v0.32.0#subdirectory=gen/python) and confirms a demand carrying `after` now parses and round-trips through platform_contracts.demand_coordinator.demand.Demand."
  - "factory removes any local workaround it added for the missing `after` field, or explains why it stays."
needs-owner: false
status: archived
---

# Python Demand `after`: close the consuming leg

## What we need

`contracts` **v0.32.0** shipped what `factory-20260927-demand-after-binding`
asked for. `platform_contracts.demand_coordinator.demand.Demand` now has an
optional `after` field (a list of demand ids, `min_length=1`, order kept), so
it no longer rejects demands that carry it. There is a regression fixture at
`tests/fixtures/demand-coordinator/demand-with-after.json`.

The release is additive and Python-only. `to` is still `list[str]`, and no
schema, Java or TS shape changed.

Note: the model does not enforce `after`'s `uniqueItems`. Validate against
`schemas/demand-coordinator/demand.json` where duplicate rejection matters.

## Why

D043 release duty: the origin closes its consuming leg.

## What we do once closed

Archive this file.
