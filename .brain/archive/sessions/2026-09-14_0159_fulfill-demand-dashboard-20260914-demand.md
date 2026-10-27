---
session_id: 2026-09-14_0159_fulfill-demand-dashboard-20260914-demand
agent: contracts
model: claude-code
started: 2026-09-14T01:59:23+01:00
ended: 2026-09-14T02:07:13+01:00
task: "Fulfill demand dashboard-20260914-demand-dispatch-order (capability: Demands can declare which other demands must be owner-approved before they are dispatched, and the dispatch queue carries a governed order number (wave) plus the still-waiting demands, so the /agents Dispatch queue can show an Orde..."
priority: 2
status: done
launch: supervised
decisions:
  - id: D-2026-09-14-01
    text: "Did NOT regenerate the Python binding: datamodel-codegen 0.68.1 also rewrites the unrelated `to` field to list[ToItem] (verified as pure generator drift against the unmodified v0.25.0 schema), which would be a breaking change for Python consumers inside an additive release. pyproject stays 0.25.0; documented as a named gap with the fix path in CHANGELOG v0.26.0 and the fulfillment report."
    supersedes: null
changes:
  - "demand.json gains optional `after` (array of demand ids, uniqueItems, minItems 1); new demand.queue-entry.json (DemandQueueEntry) with wave (integer, minimum 1) and waitingOn; Java + TypeScript bindings, dist rebuilt; 8 new Java tests, 14 new validator cases; CHANGELOG/DEPLOYMENT updated"
  - "Released v0.26.0 (Java+TS); D031 clean-install verified from the tagged URL for both changed languages incl. a TS negative control; D043 origin demand raised to dashboard (8c2c55e); fulfillment report committed (8d07cbd)"
lessons:
  - "YAML parses an unquoted `date: 2026-09-14` frontmatter value into a datetime.date, so validating raw parsed demand frontmatter against demand.json (which types date as string) fails on every committed demand file — a pre-existing ingest detail, not something `after` introduced."
  - "A demand queue row cannot encode wave as 1 + len(waitingOn): a multi-hexagon sub-demand's wave is also raised by sequence position, so it can sit at wave 3 with an empty waitingOn. Pinned in the schema description and asserted in tests so the simplification fails loudly."
  - "npm install of a `file:` dependency given an MSYS-style /c/... path exits 0 and reports \"added 2 packages\" while creating a BROKEN symlink (/c/c/Users/...). Use a native C:/ path — the D031 acceptance test caught this only because it installed for real."
context_missing: []
notes_used: []
vault_sync: none
close: confirmed
---


## Log

**01:59 Session opened by agent-runner's dispatch supervisor** (launch: supervised) -- task: "Fulfill demand dashboard-20260914-demand-dispatch-order (capability: Demands can declare which other demands must be owner-approved before they are dispatched, and the dispatch queue carries a governed order number (wave) plus the still-waiting demands, so the /agents Dispatch queue can show an Orde...".

**02:07 Session closed via `brain session close` (status: done).**
