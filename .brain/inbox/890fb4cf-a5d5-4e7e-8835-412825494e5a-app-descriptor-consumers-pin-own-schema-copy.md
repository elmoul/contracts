---
slug: app-descriptor-consumers-pin-own-schema-copy
title: "Schema changes to app.descriptor must be tracked in downstream pinned copies"
type: fact
created: 2026-10-29
updated: 2026-10-29
provenance:
  runs: ["890fb4cf-a5d5-4e7e-8835-412825494e5a"]
  files: ["schemas/app/descriptor.json"]
source: harvest
repeat_of: null
---
Several repos validate app.yaml against their own copy of app.descriptor, not the contracts tag directly: factory (vendored src/factory/contract_schemas/app/descriptor.json), control-plane (generated AppDescriptor binding), launcher (hand-written validator in launcher/descriptors.js), conventions (validator reads ../contracts-worktrees/<contracts.pin>/schemas/app/descriptor.json, so each app's contracts.pin must be >= the release that adds the field). brain-toolkit has no copy. List these in the fulfillment report when changing app.descriptor.
