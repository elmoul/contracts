---
demandId: youtrack-20261015-contracts-delivery-issue-tags
worker: contracts
date: 2026-10-15
status: done
shipped: ["tag v0.56.0 on commit 79e7f45 (local only, not pushed)", "schemas/delivery/delivery.issue.json: optional tags (array of strings)", "Python and TypeScript bindings (incl. dist .d.ts), versions 0.56.0", "CHANGELOG v0.56.0 with the startable-style rollout note", "three tags cases in tests/validate_delivery.py", "worktree ../contracts-worktrees/v0.56.0"]
---

# Fulfilment - `tags` on delivery.issue

Checked first: `tags` was not shipped (latest tag was v0.55.0, no `tags` property). Additive minor **v0.56.0**.

## Acceptance criteria

1. **Schema** - met: optional top-level `tags`, array of strings, not in `required`; description says absent means the producer does not say, empty array means no tags.
2. **Bindings, changelog, rollout note** - met: Python and TypeScript bindings carry it; CHANGELOG v0.56.0 states consumers pin the release before any producer sends `tags` (closed shape). `delivery.issue-page` picks it up via `$ref`.
3. **OpenAPI consistency** - met with no edit: `youtrack-delivery.openapi.yaml` references `delivery.issue` and `delivery.issue-page` by `$ref`.

## Verification

`python tests/run_all.py` passed (including new cases: tags list ok, empty list ok, non-string items rejected); `npx tsc --noEmit` clean. Not run: Java `mvn test` (no Java change beyond the pom version; Java regenerates from schemas), and the D031 clean install from the real GitHub tag URL, because the tag is local until the owner pushes it. Repeat after the push.
