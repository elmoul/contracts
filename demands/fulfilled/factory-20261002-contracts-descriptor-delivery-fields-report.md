---
demandId: factory-20261002-contracts-descriptor-delivery-fields
worker: contracts
date: 2026-10-02
status: done
shipped: ["v0.43.0", "commit 34cef7f on main (feat(app): descriptor and registry summary delivery fields (v0.43.0))", "schemas/app/descriptor.json (code.githubSlug, tracker.workflow, urls.hostname)", "schemas/control-plane/registry.entry.json (app.repoUrl, integrationBranch, githubSlug, workflow, hostname)", "tests/validate_app_descriptor.py (6 new fixtures, 5 registry cases)", "Java, Python and TypeScript bindings 0.43.0", "pinned worktree ../contracts-worktrees/v0.43.0", "D043 origin demand demands/2026-10-02-factory-repin-descriptor-delivery-fields.md"]
---

# Fulfillment: descriptor and registry summary delivery fields

## State check

Not previously shipped. v0.42.0 carried `repo` and `integrationBranch` in the descriptor, but no GitHub slug, no stage-to-state mapping and no route hostname, and the registry `app` summary had none of the five fields.

## What shipped

Tag `v0.43.0` (commit `34cef7f`, pushed), additive.

- `app.descriptor`: optional `code.githubSlug` (`owner/name`, no further slashes or whitespace), optional `tracker.workflow` (stages `planned`, `developing`, `ready-for-test`, `accepted`; each optional, each a non-empty string, unknown stages rejected) and optional `urls.hostname` (single lowercase DNS label, max 63).
- `registry.entry.app`: optional `repoUrl`, `integrationBranch`, `githubSlug`, `workflow`, `hostname`, mirroring the descriptor. Entries without them still validate (tested).
- Fixtures in `tests/fixtures/app-descriptor/`: valid with every new field (Planotell-shaped), valid with none, invalid for an empty workflow state, a hostname with a dot, an uppercase hostname, and a `githubSlug` without a slash. Registry cases (empty state, unknown stage, bad hostname, bad slug, non-http repoUrl) in `tests/validate_app_descriptor.py`.

## Verification

- `python tests/run_all.py`: all validators pass.
- `mvn -f gen/java/pom.xml test`: exit 0 (generated `Code.java` carries `githubSlug`).
- `npx tsc` in `gen/ts`: clean, `dist/` rebuilt.
- D031 clean install from the real tag: fresh venv `pip install git+https://github.com/elmoul/contracts.git@v0.43.0#subdirectory=gen/python` exposes `Code.githubSlug`, `Tracker.workflow`, `Urls.hostname` and the five new `registry_entry` app fields; fresh clone of the tag plus `npm install` with an empty npm cache compiles a `--strict` file using the new `AppDescriptor` and `RegistryEntry` fields. A fresh-`.m2` Java install from the tag was not run.

## What the origin must know

- **Consumers must enforce what the schema cannot:** a mapped `workflow` state must be a non-resolved state, and `Done` is never a Factory target (only the owner sets Done). Stated in the `tracker.workflow` schema description and in a comment in the all-fields fixture.
- `urls.hostname` has no schema default; consumers default it to `name` when absent (stated in the description).
- Python/TS types for `if/then` rules are still not generated; validate `app.yaml` against the JSON Schema. The new fields themselves are plain properties and are typed.
- Open question for consumers, not decided here: `workflow` keys use the hyphenated stage name `ready-for-test`, so the Python attribute is `ready_for_test` with alias `ready-for-test`; round-trip with `model_dump(by_alias=True)`.

## Not done / caveats

- Java clean-install from the tag (fresh `.m2`) not run.
- `workflow` is defined twice (descriptor `$defs` and inline in the registry entry) because registry.entry has no cross-file `$ref` today; keep them in step.
