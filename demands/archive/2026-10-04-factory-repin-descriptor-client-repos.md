---
id: contracts-20261004-factory-repin-descriptor-client-repos
date: 2026-10-04
from: contracts
to: [factory]
capability: Close the consuming leg of factory-20261004-contracts-descriptor-client-repos - optional client-repository fields on app.descriptor and registry.entry.app shipped in contracts v0.48.0
acceptance-criteria:
  - "factory reviews contracts v0.48.0 (app.descriptor gains optional code.access fork|push, code.slug, code.host, code.credential, delivery.pr open|draft|hold and policy.ai allowed|forbidden, with the conditional rules in schemas/app/descriptor.json; registry.entry.app mirrors access, slug, host, pr, aiPolicy but not the credential name) and either accepts it or raises the specific gaps back to contracts."
  - "Factory re-pins to v0.48.0 when it is ready to read the new fields; it treats absent access as fork, absent delivery.pr as open and absent policy.ai as allowed, and prefers code.slug over code.githubSlug when both are present (the schema cannot check agreement)."
needs-owner: false
status: archived
---

# app.descriptor client-repository fields: close the consuming leg

`contracts` **v0.48.0** adds the optional descriptor fields for client and employer repositories. Additive; nothing
existing changed, so no other consumer is obligated to move (D031). Details in
`demands/fulfilled/factory-20261004-contracts-descriptor-client-repos-report.md`.

## Why
D043 release duty: the origin closes its consuming leg. The tag and branch are local until the owner pushes them.
