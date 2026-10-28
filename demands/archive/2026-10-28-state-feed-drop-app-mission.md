---
id: contracts-20261028-state-feed-drop-app-mission
date: 2026-10-28
from: contracts
to: [state-feed]
capability: "state-feed no longer ingests or projects app.mission, so it still builds when contracts removes the app-studio schemas"
acceptance-criteria:
  - "Found by the state-feed v2 spec review (../docs/spec-v2-review/state-feed.md finding 2, read-only): app-studio was removed (D140); contracts v0.68.0 marked the app-studio schemas retired and removes them in its next minor release (vault D146 ruling 3). Nothing emits app.mission, yet EventIngestService.java:121-132 ingests it and StateService.java:86-89 projects it; both stop compiling after the re-pin"
  - "Do: (a) remove the app.mission ingest branch, its snapshot key and projection, and their tests; an incoming app.mission event is then handled like any unknown type (say how in the report); (b) update the docs that list the types (HEXAGON.md, README, DEPLOYMENT); (c) do not re-pin contracts here: the change must compile on the current pin and on the next; (d) CHANGELOG; full test suite green; commit locally; push nothing; do not rebuild or restart the running container"
needs-owner: false
status: archived
---

# Demand - state-feed: drop the app.mission ingest

## What we need
No app.mission code in state-feed.

## Why / what's blocked
contracts' next minor release removes the app-studio schemas; state-feed would no longer build at its re-pin.

## What we do once closed
contracts removes the app-studio family in its next minor.

## Not in scope
The contracts removal itself; re-pinning state-feed.
