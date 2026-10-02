---
demandId: factory-20261002-contracts-summary-required-checks
worker: contracts
date: 2026-10-02
status: done
shipped: ["v0.44.0", "commit 1d35444 on main (feat(registry): app summary carries requiredChecks, appRoot, releaseBranch (v0.44.0))", "schemas/control-plane/registry.entry.json (app.requiredChecks, app.appRoot, app.releaseBranch)", "tests/validate_app_descriptor.py (2 valid and 5 invalid registry cases)", "Python and TypeScript bindings 0.44.0 (Java version bumped, output unchanged)", "pinned worktree ../contracts-worktrees/v0.44.0", "D043 origin demand demands/2026-10-02-factory-repin-summary-required-checks.md"]
---

# Fulfillment: registry app summary carries requiredChecks, appRoot, releaseBranch

## State check

Not previously shipped. v0.43.0's registry `app` summary had `repoUrl`, `integrationBranch`, `githubSlug`, `workflow` and `hostname`, but none of these three; the descriptor already had all three.

## What shipped

Tag `v0.44.0` (commit `1d35444`, pushed), additive. `registry.entry.app` gains optional `requiredChecks` (array of unique non-empty strings), `appRoot` (`.` or `app`) and `releaseBranch` (non-empty string), mirroring `delivery.requiredChecks`, `code.appRoot` and `code.releaseBranch`. Entries without them still validate (tested). The descriptor is unchanged.

Cases: the repo keeps summary fixtures inline in `tests/validate_app_descriptor.py` (not as files), so the summaries are there: all three fields; none (pre-existing case); empty `requiredChecks` for a pr-only app; invalid for an empty check name, a duplicate check name, `appRoot` `src`, `appRoot` `./app`, and an empty `releaseBranch`.

## Verification

- `python tests/run_all.py`: all validators pass.
- `mvn -f gen/java/pom.xml test`: exit 0.
- TS regenerated, `npx tsc` rebuilt `dist/`.
- D031 clean install from the real tag: fresh venv `pip install git+https://github.com/elmoul/contracts.git@v0.44.0#subdirectory=gen/python` exposes `requiredChecks`, `appRoot`, `releaseBranch` on `App`; fresh clone of the tag plus `npm install` with an empty npm cache compiles a `--strict` file using the three fields. Fresh-`.m2` Java install not run (Java output unchanged).

## What the origin must know

- The summary cannot enforce "empty `requiredChecks` only when `deliveryMode` is `pr-only`", nor "`appRoot` matches `layout`"; the descriptor enforces both. The registry populating the summary must copy from a valid descriptor.
- Python types `requiredChecks` as `list[RequiredCheck]` (a RootModel wrapper), same as the descriptor binding.

## Not done / caveats

- Java clean-install from the tag (fresh `.m2`) not run.
