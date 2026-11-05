---
slug: app-descriptor-consumers-pin-own-schema-copy
title: "app.descriptor changes need downstream pinned copies"
type: fact
status: active
created: 2026-11-05
updated: 2026-11-05
provenance:
  runs: ["890fb4cf-a5d5-4e7e-8835-412825494e5a"]
---
Several repos validate app.yaml against their own app.descriptor copy.
Factory vendors src/factory/contract_schemas/app/descriptor.json. Control-plane has a generated AppDescriptor binding. Launcher has a hand-written validator in launcher/descriptors.js. Conventions reads ../contracts-worktrees/<contracts.pin>/schemas/app/descriptor.json, so each app's contracts.pin must be >= the release adding the field. brain-toolkit has no copy. List these in the fulfillment report when changing app.descriptor.
