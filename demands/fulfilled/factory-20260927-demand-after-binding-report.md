---
demandId: factory-20260927-demand-after-binding
worker: contracts
date: 2026-09-27
status: done
shipped: ["v0.32.0", "commit 908ab04 on main", "gen/python/platform_contracts/demand_coordinator/demand.py (Demand.after)", "tests/fixtures/demand-coordinator/demand-with-after.json", "tests/validate_demand.py (schema + Python binding round-trip)", "pinned worktree ../contracts-worktrees/v0.32.0"]
summaryRef: "commit 908ab04 on main (feat(demand-coordinator): Python Demand binding gains `after` (v0.32.0))"
---

# Fulfillment: Python Demand binding supports `after`

## State check

No earlier session had shipped this. At v0.31.0 the `after` field existed in
`schemas/demand-coordinator/demand.json` (since v0.26.0) and in the Java/TS
bindings, but the Python `Demand` model had not been regenerated. That was a
deliberate choice recorded in the v0.26.0 CHANGELOG caveat. The model sets
`extra='forbid'`, so it rejected any demand carrying `after`
(`extra_forbidden`). The supervisor-opened session `2026-09-27_1035` left no
commits. This session did the work.

## What shipped

Tag **`v0.32.0`** (commit `908ab04`, pushed to `origin/main`), pinned worktree
`../contracts-worktrees/v0.32.0`. It is additive and Python-only.

1. **Tagged Python binding accepts and preserves `after`.** `Demand` gains
   `after: list[constr(pattern=<demand id>)] | None` with `min_length=1`.
   The file was regenerated from the unchanged schema with datamodel-codegen
   0.68.1 plus `--collapse-root-models`. That flag avoids what blocked v0.26.0:
   `to` stays `list[constr(...)]` rather than becoming `list[ToItem]`. The diff
   against v0.31.0 is the `after` field plus the header timestamp only.
   `pyproject.toml` is now `0.32.0`.
2. **Regression fixture; compatibility kept; v0.31.0 not mutated.**
   `tests/fixtures/demand-coordinator/demand-with-after.json` is validated
   against the JSON Schema. It is then round-tripped through the Python
   `Demand`: the dump with `by_alias` and `exclude_none` is identical to the
   input and re-validates against the schema. The same check runs on a real
   pre-`after` demand file read from disk, which still round-trips without
   gaining the field. The test also checks that `after` order is preserved,
   that `to` is a plain `list[str]`, and that empty or malformed `after` is
   rejected. It fails against the v0.31.0 binding with `extra_forbidden`.
   `python tests/run_all.py` is green. No schema, Java or TS file changed.
   The `v0.31.0` tag still resolves to `19a2dbc`.

## D031 acceptance

I installed from a fresh venv with `--no-cache-dir` from
`git+https://github.com/elmoul/contracts.git@v0.32.0#subdirectory=gen/python`.
`importlib.metadata` reported `0.32.0`. The fixture round-tripped exactly,
with `after` preserved in order and `to[0] == "contracts"`.

## Caveat

The pydantic model does **not** enforce `after`'s `uniqueItems`. The field is
kept as a `list` so order is preserved; `--use-unique-items-as-set` would lose
order. The JSON Schema still rejects duplicates, so validate against it if that
matters. No Python binding for `demand.queue-entry` was added because this
demand did not ask for one.

## D043

Additive release, so only the origin demand is raised:
`demands/2026-09-27-factory-repin-demand-after-binding.md` (to: factory).
