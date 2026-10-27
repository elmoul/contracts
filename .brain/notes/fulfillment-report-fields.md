---
slug: fulfillment-report-fields
title: "Fulfillment report frontmatter must match demand.fulfillment"
type: gotcha
status: active
created: 2026-10-27
updated: 2026-10-27
provenance:
  runs: []
  files: ["schemas/demand-coordinator/demand.fulfillment.json", "demands/fulfilled"]
---
A fulfillment report that fails demand.fulfillment.json never reaches owner approval.
The required keys are demandId, worker and status. date is optional, and no other key is allowed (additionalProperties false). status is done or blocked, never fulfilled or approved. Quote any scalar that contains ': ', or YAML parses it as an object. Check GET /board: the file must be in data.fulfillments and absent from data.errors.
