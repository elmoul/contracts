---
id: contracts-20260927-ci-runner-repin-headsha-lookup
date: 2026-09-27
from: contracts
to: [ci-runner]
capability: Close the consuming leg of ci-runner-20260927-contracts-ci-headsha-lookup — headSha on ci.run/BuildResult and the CI-result lookup interface shipped in contracts v0.34.0
acceptance-criteria:
  - "ci-runner reviews contracts v0.34.0 (schemas/state-feed/state.event.json, schemas/ci-runner/build-result.yaml, schemas/delivery-api/ci-runner-results.openapi.yaml and docs/task-delivery.md §CI result routes) against the demand and either accepts it or raises the specific interface gaps back to contracts."
  - "ci-runner emits headSha (the GitHub workflow_job.head_sha, full 40-hex lowercase) on the ci.run state event and on BuildResult. It stays optional: a job whose head_sha is unavailable omits it rather than sending ref or a zero SHA, because a wrong revision is worse than a null one."
  - "ci-runner implements GET /delivery/v1/ci-results/{runId}/{jobId}, returning delivery.producer-result with producer ci-runner, operationId <runId>/<jobId>, nativeRef ci-runner:ci.run/<runId>/<jobId>, repository as the platform repo name, and revision from headSha — null, never guessed from ref, when it was never observed."
  - "ci-runner implements GET /delivery/v1/ci-results?repository=&revision= as an exact match on the full 40-hex revision, returning {repository, revision, items[]}; an empty items array is a 200 meaning 'no job known', never a pass."
  - "ci-runner returns the not-found shape the document fixes — 404 with a delivery.error whose code is ci_result_not_found and retryable false — and 503 producer_unavailable only when its own store is unreachable; the two are never conflated."
  - "ci-runner re-pins whatever binding it reads these shapes from: the TypeScript file: dependency to ../contracts-worktrees/v0.34.0/gen/ts, the Java io.platform:contracts:0.34.0 install, or the Python git pin at @v0.34.0, and confirms an existing ci.run/BuildResult document without headSha still validates unchanged."
needs-owner: false
status: archived
---

# contracts v0.34.0: close the consuming leg

## What we need

`contracts` **v0.34.0** shipped what
`ci-runner-20260927-contracts-ci-headsha-lookup` asked for. Additive; the release is
`9f6c2ea`, tagged, with the pinned worktree `../contracts-worktrees/v0.34.0`.

- `schemas/state-feed/state.event.json` + `state-event-java.yaml`: `CiRunPayload`
  (event `ci.run`) gains optional `headSha`, pattern `^[0-9a-f]{40}$` — strict
  lowercase, full 40 hex, matching every other revision field in the platform. The
  `required` list is unchanged, so a `ci.run` payload without it validates exactly as
  it did before.
- `schemas/ci-runner/build-result.yaml`: the same optional `headSha` on
  `BuildResult`, so the `ci-runner` → `control-plane` channel carries the revision
  too and the two channels agree.
- **New** `schemas/delivery-api/ci-runner-results.openapi.yaml`: the lookup
  interface. `GET /delivery/v1/ci-results/{runId}/{jobId}` returns a single
  `delivery.producer-result`; `GET /delivery/v1/ci-results?repository=&revision=`
  returns `{repository, revision, items[]}` of them, ordered by `observedAt`
  ascending. Both use the identity you already publish on `ci.run`
  (`operationId` = `<runId>/<jobId>`, `nativeRef` = `ci-runner:ci.run/<runId>/<jobId>`,
  `repository` = platform repo name). The not-found shape is fixed:
  `CiResultNotFoundError`, a `delivery.error` with `code: ci_result_not_found` and
  `retryable: false`; the error envelope also names `503 producer_unavailable` for a
  store you cannot reach.
- `schemas/delivery/delivery.error.json`: those two codes added to the table and
  `examples[]`. `code` stays an open string, so this constrains nothing you already
  send.
- `docs/task-delivery.md` §CI result routes: the route table, and the rules that
  matter for correctness — `revision` is `headSha` or `null` and never `ref`; a null
  revision cannot pass a revision gate; an empty by-revision listing is missing
  evidence, not a pass.
- Bindings at v0.34.0: TypeScript `build-result.ts` and `state-event.ts` gain
  `headSha?: string`; Java `io.platform.contracts.events.CiRunPayload` gains a
  nullable `headSha` (and `BuildResult` gains it at build time from the schema);
  Python `ci_runner.build_result` and `state_feed.state_event` gain the field.

## Why

D043 release duty: the origin closes its consuming leg. Nothing here is implemented
by `contracts` — this release publishes the interface and the field, nothing more.
The §Producers row for `ci-runner` records the gap as **closed at the interface
level** and the implementation as yours; it stays that way until you ship it.

The `ref`-is-not-a-revision point is the one worth not skipping: before this release
a CI result could only be correlated by `ref`, which is a moving name, so Factory had
to record `unknown` for any revision gate it could not otherwise prove. With
`headSha` published and the lookup live, a result becomes re-fetchable by
`(repository, revision)` after a restart or a lost event — but only if you emit the
SHA the webhook actually carries. A guess reconstructed from `ref` would defeat the
whole point, which is why the schemas leave it optional and the docs pin `null` as
the only alternative.

## What we do once closed

Nothing further on the contracts side unless you raise a gap. The release was
**additive**, so no other consumer is obligated to move (D031) and no fleet-wide
demand was raised — `factory` keeps consuming `delivery.producer-result` at whatever
pin it holds until it chooses to move.
