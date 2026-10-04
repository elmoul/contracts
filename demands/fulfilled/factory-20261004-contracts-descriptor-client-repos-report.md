---
demandId: factory-20261004-contracts-descriptor-client-repos
worker: contracts
date: 2026-10-04
status: done
shipped: ["v0.48.0 (local tag on ef9c765, NOT pushed; owner pushes)", "commit 6dc0370 feat(app): client-repository fields on app.descriptor and registry.entry.app (v0.48.0)", "commit ef9c765 docs(changelog): v0.48.0 descriptor client-repository fields", "schemas/app/descriptor.json (code.access, code.slug, code.host, code.credential, delivery.pr, policy.ai, conditional rules)", "schemas/control-plane/registry.entry.json (app.access, slug, host, pr, aiPolicy; no credential)", "tests/validate_app_descriptor.py plus 8 valid and 16 invalid fixtures in tests/fixtures/app-descriptor and registry cases", "Python, TypeScript bindings regenerated; Java version bumped, output unchanged; all three at 0.48.0", "CHANGELOG v0.48.0 entry", "pinned worktree ../contracts-worktrees/v0.48.0", "D043 origin demand demands/2026-10-04-factory-repin-descriptor-client-repos.md (committed locally, not pushed)"]
---

# Fulfillment: descriptor fields for client and employer repositories

## State check

Not shipped before this session: latest tag was v0.47.0 and `descriptor.json` had none of `code.access`, `slug`, `host`,
`credential`, `delivery.pr` or `policy`.

## Acceptance criteria

1. **Fields** (all optional, `app.descriptor/1` unchanged): `code.access` enum fork|push; `code.slug` pattern
   `^[^/\s]+(/[^/\s]+)+$` (two or more segments); `code.host` lowercase DNS name, no scheme/port/path;
   `code.credential` `^[a-z][a-z0-9-]*$`, max 64, described as a name never the secret; `delivery.pr` open|draft|hold
   (default open when absent); `policy` object with `ai` allowed|forbidden (default allowed), `additionalProperties: false`. Met.
2. **Conditional rules:** third-party keeps `delivery.mode: pr-only`; third-party with access absent/fork still requires a
   non-empty `fork`; third-party with `push` requires `fork` absent or null; owned with `fork` is invalid; `delivery.pr`
   draft/hold requires pr-only; existing rules untouched. `githubSlug` unchanged and described as github.com, with the
   prefer-`slug` note in the schema description, the field description, CHANGELOG, and a comment in
   `valid-wrapped-slug-and-github-slug.yaml`. Met.
3. **`registry.entry.app`** gains `access`, `slug`, `host`, `pr`, `aiPolicy`; no credential (a registry test confirms a
   `credential` key is rejected). Entries without them and every existing registry fixture still pass. Met.
4. **Fixtures:** valid: third-party push+draft (client shape), explicit fork, push with `fork: null`, hold, nested GitLab
   slug with host gitlab.com, `policy.ai` forbidden and allowed, slug with githubSlug. Invalid: push with fork set, owned
   with access fork, unknown access, push with mode full, hold/draft with mode full, unknown pr, credential with spaces /
   uppercase / token-like / too long, one-segment slug, host with path, uppercase host, unknown `policy.ai`, extra `policy`
   property. All existing fixtures unchanged and still give the same result. Each invalid fixture was checked to be
   rejected for the intended reason. Met.
5. **Release:** v0.48.0 (next minor after v0.47.0), CHANGELOG describes each field and rule; bindings rebuilt. Met, with
   one stated limit: the tag and branch are **not pushed** (owner pushes, per run rules), so the clean-install check was run
   from the **local tag** over a `file://` URL instead of the GitHub URL. No consumer was re-pinned.

## Evidence

- `python tests/run_all.py`: all validators passed (74 PASS lines in `validate_app_descriptor.py`).
- `mvn -f gen/java/pom.xml test`: exit 0.
- Clean install from tag `v0.48.0` (clone at the tag, fresh venv, fresh npm cache, fresh `-Dmaven.repo.local`):
  pip install of `gen/python` gives `platform-contracts 0.48.0`; `registry_entry.App` accepts access/slug/host/pr/aiPolicy and
  rejects `access=clone`; `descriptor.Code` has access, slug, host, credential; `npm ci` then `tsc --noEmit` passes with the
  new `access`, `pr`, `credential` types; Java build in the clone passes.
- Binding caveat (already documented): generated Python/TS types do not enforce the `if/then` rules; validate against the schema.
- Re-run after push: the same install from `git+https://github.com/elmoul/contracts.git@v0.48.0` is still owed once the owner pushes the tag.

## Consuming leg

D043 origin demand `contracts-20261004-factory-repin-descriptor-client-repos` written to `demands/` and committed locally
(not pushed; the push is the raise, so the owner's push raises it). Additive release: no fleet-wide consumer demand.
