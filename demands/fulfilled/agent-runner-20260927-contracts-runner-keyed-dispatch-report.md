---
demandId: agent-runner-20260927-contracts-runner-keyed-dispatch
worker: contracts
date: 2026-09-27
status: done
shipped: ["v0.33.0", "commit 3d72989 on main", "pinned worktree ../contracts-worktrees/v0.33.0", "schemas/agent-runner/runner.dispatch-request.json (optional dispatchKey, required list unchanged)", "schemas/agent-runner/runner.run-record.json (optional dispatchKey + nullable observed workspace)", "schemas/agent-runner/runner.dispatch-reservation.json (new: lookup body + requestHash canonicalization)", "docs/task-delivery.md section Runner routes (route table, status codes, no-relaunch rule)", "gen/ts runner-dispatch-request.ts + runner-run-record.ts + runner-dispatch-reservation.ts (new bindings; runner schemas had none before)", "gen/python platform_contracts.agent_runner.runner_dispatch_reservation", "tests/validate_runner.py 37 cases incl. an executable requestHash conformance check", "D031 acceptance: fresh-venv git-URL install and fresh-cache npm file: install both green"]
summaryRef: "commit 3d72989 on main (feat(agent-runner): keyed dispatch, dispatch-key lookup, observed workspace (v0.33.0))"
---

# Fulfillment — agent-runner keyed dispatch, dispatch lookup, observed workspace

## State check

Not shipped before this session. Two supervisor-opened sessions
(`2026-09-27_1130`, `_1136`) left no commits and no files; no `dispatchKey`,
`dispatch-reservation` or workspace-on-the-wire existed anywhere in this repo, and
`gen/ts` had no runner module at all. This session did the work.

## What shipped

Tag **`v0.33.0`** (commit `3d72989` on `main`, pushed), pinned worktree
`../contracts-worktrees/v0.33.0`. Additive: no existing required list changed and
no consumer is obligated to move (D031). Java untouched — no Java producer or
consumer of these shapes exists (`gen/java/pom.xml` stays at 0.30.0).

Against the five acceptance criteria:

1. **`runner.dispatch-request` gains optional `dispatchKey`**, pattern
   `^[A-Za-z0-9][A-Za-z0-9._:-]{7,199}$` (8–200 chars; admits Factory's
   `<caller>-operation:<uuid>` token, so one token can serve both mechanisms).
   `required` is still `["repo","prompt"]`. A test guard asserts the keyed fixture
   differs from the unkeyed one by `dispatchKey` alone, and asserts the `required`
   list verbatim, so the byte-for-byte claim is checked rather than asserted in prose.
2. **`runner.run-record` gains optional `dispatchKey` and nullable `workspace`**
   (`baseBranch`, `baseRevision`, `branch`, `revision`, `dirty`, `observedAt`).
   Revisions are `^[0-9a-f]{40}$`; `null` means *not observed*, never a default.
   `dispatchKey` is echoed and is **absent, not null**, when the run was unkeyed —
   null is a second spelling of "unkeyed" that the closed shape does not admit.
   Existing required fields unchanged.
3. **New `runner.dispatch-reservation`** — the `GET /dispatches/{dispatchKey}` body
   (`dispatchKey`, `requestHash`, `runId`, `reservedAt`, `run`) with `run` a real
   `$ref` to `runner.run-record.json`, so the two cannot drift; plus the exact
   `requestHash` canonicalization and a worked example of it.
4. **Docs.** `docs/task-delivery.md` §Runner routes carries the route/status table
   (`202` new · `200` replay · `409` conflicting reuse · `409` repo locked · `429`
   cap · `404` no reservation), reserve-before-spawn, the 409-is-not-a-retry rule,
   the 404-is-safe-to-resend rule, the uncertain-dispatch **no-relaunch** rule, and
   names `GET /runs/{id}/producer-result` and `GET /dispatches/{dispatchKey}/producer-result`
   as the `delivery.producer-result` lookups. §Producers and the handoff matrix were
   updated: the runner gap is **closed**, the implementation is not. The schema
   descriptions carry the same semantics.
5. **Released, with regenerated bindings.** See the repin section below.

## What the origin must know

**1. The TS bindings for these schemas are NEW in v0.33.0.** This was the real
blocker on criterion 5: the runner schemas were published as JSON Schema only, so
`gen/ts` had no `runner-*.ts` to import and no repin to `gen/ts` could have worked.
v0.33.0 adds `runner-dispatch-request.ts`, `runner-run-record.ts` and
`runner-dispatch-reservation.ts`, re-exported from `index.ts` and built into
`dist/`. Repin to `../contracts-worktrees/v0.33.0/gen/ts` and import
`RunnerDispatchRequest`, `RunnerRunRecord`, `RunnerRunWorkspace`,
`RunnerDispatchReservation`.

**2. The wire `workspace` is the FLATTENING of your internal nested shape.** Your
`RunWorkspace` is `{base, head}` of `WorkspaceIdentity`. The published record is one
flat object: `baseBranch`/`baseRevision` are the `base` observation,
`branch`/`revision`/`dirty` are the `head` observation, `observedAt` is the `head`
observation's time. All six are required *inside* `workspace` (which is itself
optional and nullable), so write the projection rather than passing `RunWorkspace`
through. `toRunRecordWire` should stop stripping the field and start projecting it;
for a run with `head: null` (orphan reconciled at startup) emit the base pair and
leave `branch`/`revision`/`dirty`/`observedAt` null — the schema has a fixture for
exactly that case. Your `normalizeRevision` already produces the required full
lowercase 40-hex or null, so it maps over unchanged.

**3. Compute `requestHash` before wiring the ledger, and check the example.**
The canonicalization is fixed in `runner.dispatch-reservation.json`: the six
execution-defining fields (`repo`, `prompt`, `demandId`, `model`, `effort`,
`runtime`), present-only — an explicitly empty string IS present and included,
because `"model": ""` differs from an absent `model`; absent means omitted, never
nulled; `dispatchKey` excluded; keys sorted; no insignificant whitespace; non-ASCII
left as UTF-8. All six are strings, so no number or boolean formatting is left for
two languages to disagree about.

This session verified that claim rather than asserting it: a TypeScript
implementation written independently from the schema's own prose reproduces the
documented canonical bytes and digest exactly
(`{"model":"claude-sonnet-5","prompt":"do the thing","repo":"plantpal"}` →
`ebaba25539396d2af99d3ff6e410f8f295d8e956380bf1818a18d65a8a98a671`), and so does the
Python recipe in `tests/validate_runner.py`, which also fails if that documented
example ever stops matching the executable recipe. **A caller and the runner that
disagree on this hash will see every replay as a conflict** — so reproduce the
example in your own language before building on it.

**4. Status codes are fixed, and `409` is overloaded.** Conflicting reuse (`409`)
and repo-locked (`409`) share a code; distinguish them in the body, as your
existing error shape already does. Neither starts a process, and neither overwrites
or creates a reservation — the lock and cap are applied *before* the reservation is
written, which is what keeps the same key reusable after a `409 repo locked` or
`429`.

**5. `run` is the full record.** The reservation serves the whole `runner.run-record`,
not a summary, so `GET /dispatches/{dispatchKey}` is a complete answer to a lost
`POST /dispatch` response — no second call to `GET /runs/{id}` needed. While the run
is still `launched`, the lookup returns the reservation with `run.state: launched`;
that is "poll again", never "lost dispatch".

## D031 acceptance (real tag, not a local build)

- **Python:** fresh venv, `pip install --no-cache-dir "platform-contracts @
  git+https://github.com/elmoul/contracts.git@v0.33.0#subdirectory=gen/python"`
  → `platform-contracts-0.33.0`, built from the tagged URL. The installed binding
  validates a keyed and an unkeyed request, round-trips a run record with workspace
  and a full reservation, and rejects a short `dispatchKey` and a short revision.
- **TypeScript:** a scratch npm project with a **fresh cache** installed
  `file:C:/Users/pc/Desktop/platform/contracts-worktrees/v0.33.0/gen/ts` →
  `@platform/contracts@0.33.0`. `tsc --strict --noEmit` passes on a file importing
  all four new types and building real-shaped documents; the independent
  canonicalization check above ran from that same install.

## Not done / caveats

- **The bindings do not enforce `pattern` in TypeScript.** `RunnerDispatchRequest.dispatchKey`,
  the revision fields and `requestHash` are plain `string` in TS — only the Python
  binding enforces the patterns (`constr`). This is the same class of caveat as
  v0.31.0's "bindings do not enforce `if/then`": `agent-runner` **must** validate an
  incoming `dispatchKey` against the schema (or re-implement the pattern) rather than
  trusting the type.
- **`json-schema-to-typescript` inlines the reservation's `$ref`.** It resolves
  `runner.run-record.json` by writing a second copy of `RunnerRunRecord` and
  `RunnerRunWorkspace` into `runner-dispatch-reservation.ts` (the duplication
  `delivery-producer-result.ts` already has for `DeliveryEnvironment`). Only the
  canonical module's copies are re-exported from `index.ts`, so there is no export
  collision, and both come from one file in one generation run. The Python binding
  imports the real class instead — no duplication there.
- **No `/dispatches` or producer-result route exists because of this release.** It
  publishes the interface; `agent-runner` implements it. Nothing here makes an
  endpoint live.
- **No fleet-wide consumer demand was raised.** The release is additive, so per
  D031/D043 only the origin demand
  (`contracts-20260927-agent-runner-repin-keyed-dispatch`) was raised. `factory`
  keeps consuming `agent_runner.*` at whatever pin it holds until it chooses to move.
- **`runner_transcript_snapshot.py` was left untouched.** It was regenerated as part
  of the directory batch, but its only difference was the datamodel-codegen
  timestamp comment, so it was reverted rather than committed as a no-op change.

## Next step for the origin

Repin to v0.33.0, implement reserve/replay/conflict/lookup and the two
producer-result routes per `docs/task-delivery.md` §Runner routes, keep unkeyed
dispatch unchanged, then report `factory-20260927-agent-runner-delivery-results`
naming v0.33.0. Raise a new demand to `contracts` if any published shape turns out
to be wrong for the implementation — do not work around it locally.
