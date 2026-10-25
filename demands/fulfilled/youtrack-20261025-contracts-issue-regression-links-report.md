---
demandId: youtrack-20261025-contracts-issue-regression-links
worker: contracts
date: 2026-10-25
status: done
shipped: ["tag v0.61.0 on commit 9bb4ce4 (local only, not pushed)", "schemas/delivery/delivery.issue.json: optional arrays fixesBugIntroducedBy and introducedBugFixedBy of delivery.issue-ref (not in required; additionalProperties false)", "Python and TypeScript bindings (incl. dist), versions 0.61.0 on Java, TS and Python", "CHANGELOG v0.61.0", "4 new cases in tests/validate_delivery.py", "worktree ../contracts-worktrees/v0.61.0"]
---

# Fulfilment - regression links on delivery.issue

Checked first: not shipped (latest tag v0.60.0, no such properties). Additive minor **v0.61.0**.

## Acceptance criteria

1. **Properties** - met. Both are optional arrays of `delivery.issue-ref`, absent from `required`, `additionalProperties` still false. Descriptions state: `fixesBugIntroducedBy` = issues this one fixes a bug of (inward Regression link); `introducedBugFixedBy` = fix tasks of bugs this issue introduced (outward); absent = producer does not say, consumer must not infer; empty array = none; same additive-and-optional (D043) and rollout-order wording as `tags` and `startable`.
2. **Bindings and changelog** - met. Python and TypeScript (source and dist) updated by hand for these members; CHANGELOG v0.61.0.

## Verification

`python tests/run_all.py` passed (both lists, empty lists, string element rejected, null rejected); `npx tsc --noEmit` clean; `mvn -f gen/java/pom.xml test` passed. Not run: D031 acceptance from the real GitHub tag URL, since the tag is local until the owner pushes it. Repeat after the push.

No origin or consumer demand raised: additive release (the origin, youtrack, re-pins from this report).
