---
slug: brain-session-close-noop-dispatched
title: "brain session close is a no-op in dispatched runs; write PROGRESS.md by hand"
type: gotcha
created: 2026-10-27
updated: 2026-10-27
provenance:
  runs: ["9a3eb72a-4fdf-48d8-8d99-d5c70dcce5de"]
  files: ["PROGRESS.md"]
source: harvest
repeat_of: null
---
In a dispatched run, `brain session close` does nothing, so the PROGRESS.md handoff is not written. Add the handoff entry to PROGRESS.md manually and commit it as its own commit after the release commit.
