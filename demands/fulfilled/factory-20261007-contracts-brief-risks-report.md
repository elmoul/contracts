---
demandId: factory-20261007-contracts-brief-risks
worker: contracts
date: 2026-10-07
status: done
shipped: ["tag v0.52.0 (local, not pushed)", "commit 323a451 on main", "schemas/youtrack/planner.brief-project-request.json (optional risks)", "TypeScript and Python bindings regenerated, Java regenerates at build", "synthetic exchange in tests/fixtures/youtrack-brief/captured-exchanges.json", "tests/validate_planner_brief.py extended", "worktree ../contracts-worktrees/v0.52.0"]
---

# Fulfilment - optional `risks` in the planner's brief record

Checked first: `risks` did not exist anywhere in the request schema (v0.51.0), so the work was done, not no-opped.

## What shipped

Tag `v0.52.0` on commit `323a451` (additive minor). Local only: nothing was pushed, neither commit nor tag. The pinned worktree `../contracts-worktrees/v0.52.0` exists.

- `planner.brief-project-request.json`, brief record: `risks` is optional, an array of strings, each 1 to 1500 characters, no maximum count (`blockers` has none either). It is not in `required`, so absent stays valid. The description says the planner rehashes the record as sent, so `risks` is part of the hash when present. `additionalProperties` stays false on the brief and everywhere else, the ten section keys are unchanged, no secret-capable property was added.
- Bindings: TypeScript (`risks?: string[]`, `dist/` rebuilt) and Python (`risks: list[constr(min_length=1, max_length=1500)] | None`) regenerated. datamodel-codegen emitted a bare `Enum` for `ChangedEnum`; restored to `StrEnum` by hand per DEPLOYMENT.md. Java is generated from the schema at build; the version is bumped to 0.52.0 in pom.xml, package.json and pyproject.toml. CHANGELOG has a v0.52.0 entry.
- Fixture: one new accepted exchange appended to `captured-exchanges.json`, marked `"synthetic"`. It is **synthetic**, not captured from the planner: built from captured exchange #0, with two `risks` added to the request brief, the hash and `approval.hash` recomputed by the documented rule, and the project key changed; the response is the planner's real shape.
- `tests/validate_planner_brief.py`: the risks brief validates; an old payload without `risks` validates; an unknown brief property is still refused (with and without `risks`); empty string, over 1500 characters, non-array and non-string `risks` are refused; 1500 characters and an empty list are accepted; the risks brief hash follows the rule, differs from the hash without `risks`, and every accepted brief hashes to its own `hash`.

Verification run: `python tests/run_all.py` all passed; `npx tsc --noEmit` clean; `mvn -f gen/java/pom.xml test` exit 0; a Python round-trip on the old and the risks payload; a fresh venv install from the local tag (`git+file://...@v0.52.0#subdirectory=gen/python`) exposes `Revision.risks`.

## What the origin must know

Factory and the planner (youtrack) must re-pin to v0.52.0 on their own demands (D031); this release moves no consumer. The hash of a brief without `risks` is unchanged on both sides.

## Not done / caveats

- Nothing pushed, so the D031 acceptance install from the real remote tag URL could not be run; the local-tag install above is the closest check. The owner pushes, then that install should be repeated.
- The D043 release-notification demand (to Factory, "close your consuming leg") was not raised: raising is a push, which this run forbids. The owner or the next session raises it after the push.
- Java: no test asserts `risks` in the generated class; it relies on jsonschema2pojo regenerating from the schema at build (the build and tests passed).
