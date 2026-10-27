---
slug: python-regen-renames-enums
title: "datamodel-codegen renumbers inline enums on every regen"
type: gotcha
status: active
created: 2026-10-27
updated: 2026-10-27
provenance:
  runs: []
  files: ["gen/python", "schemas/state-feed/state.event.json"]
---
A regen can rename public Python enum classes (TaskWorkspaceState -> State1, Status1..N).
datamodel-codegen numbers clashing inline enum names in definition order. A regen or a new inline enum can rename existing classes, which turns an additive release into a breaking one. Give new enums a named $defs entry and $ref it. Diff the generated module for renames and restore the old names by hand before committing.
