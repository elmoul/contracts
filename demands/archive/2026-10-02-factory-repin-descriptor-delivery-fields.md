---
id: contracts-20261002-factory-repin-descriptor-delivery-fields
date: 2026-10-02
from: contracts
to: [factory]
capability: Close the consuming leg of factory-20261002-contracts-descriptor-delivery-fields - the delivery fields on app.descriptor and the registry app summary shipped in contracts v0.43.0
acceptance-criteria:
  - "factory reviews contracts v0.43.0 (code.githubSlug, tracker.workflow and urls.hostname in schemas/app/descriptor.json; repoUrl, integrationBranch, githubSlug, workflow and hostname on the app object of schemas/control-plane/registry.entry.json; the Java/Python/TypeScript bindings) and either accepts it or raises the specific gaps back to contracts."
  - "Factory re-pins to v0.43.0 and honours the rule the schema cannot check: a workflow state must be non-resolved and Done is never a Factory target."
needs-owner: false
status: archived
---

# Descriptor delivery fields: close the consuming leg

`contracts` **v0.43.0** adds the delivery fields to `app.descriptor` and mirrors them into the
optional `app` summary on `registry.entry`. Additive; nothing existing changed. Details in
`demands/fulfilled/factory-20261002-contracts-descriptor-delivery-fields-report.md`.

## Why
D043 release duty: the origin closes its consuming leg. Additive, so no other consumer is obligated to move (D031).
