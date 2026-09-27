---
demandId: ci-runner-20260927-contracts-ci-headsha-lookup
worker: contracts
date: 2026-09-27
status: done
shipped: ["v0.34.0", "commit 9f6c2ea on main", "pinned worktree ../contracts-worktrees/v0.34.0", "schemas/state-feed/state.event.json + state-event-java.yaml (optional headSha ^[0-9a-f]{40}$ on CiRunPayload, required list unchanged)", "schemas/ci-runner/build-result.yaml (optional headSha, same pattern)", "schemas/delivery-api/ci-runner-results.openapi.yaml (new: GET /delivery/v1/ci-results/{runId}/{jobId} and GET /delivery/v1/ci-results?repository=&revision=, both -> delivery.producer-result; not-found shape CiResultNotFoundError with code const ci_result_not_found, retryable const false)", "schemas/delivery/delivery.error.json (codes ci_result_not_found + producer_unavailable documented; code stays an open string)", "docs/task-delivery.md section CI result routes + Producers ci-runner row + handoff matrix CI result row + v0.34.0 repin section", "gen/ts build-result.ts + state-event.ts + dist (headSha?: string)", "gen/java io.platform.contracts.events.CiRunPayload + pom.xml 0.30.0 -> 0.34.0 (this release changes Java output)", "gen/python ci_runner/build_result.py + state_feed/state_event.py", "tests/validate_state_event.py 3 new ci.run cases (40-hex accepted; abbreviated and uppercase rejected)", "tests/validate_delivery.py check_ci_api + a passed ci-runner producer-result fixture (63 cases)", "gen/java/src/test/.../CiHeadShaTest.java 5 cases (44 in the module)", "D031 acceptance: fresh-venv git-URL install, fresh .m2 mvn install from the pinned worktree, and a scratch file: npm install + strict tsc --noEmit, all green"]
summaryRef: "commit 9f6c2ea on main (feat(ci-runner): headSha on ci.run + BuildResult, CI-result lookup (v0.34.0))"
---

# Fulfillment — CI headSha + CI-result lookup

## State check

**Not shipped before this session.** The demand was open at the coordinator
(`GET /inbox/contracts` on port 8082 returned it `readyFor: contracts`, wave 1). Two
earlier supervisor-opened sessions had touched it and neither finished: `1130`
closed `status: failed` and `1136`/`1150` was left open with no close recorded. They
produced a real partial working tree — schemas and tests, uncommitted — which this
session reviewed, completed and released rather than redoing. Everything below that
was already in the tree is marked as such; the docs, the version bumps, the
regeneration of Java and the TS `dist/`, the tag and all three acceptance runs are
this session's.

## What shipped

Tag **`v0.34.0`** (commit `9f6c2ea` on `main`, pushed), pinned worktree
`../contracts-worktrees/v0.34.0`. **Additive** — no `required` list changed anywhere,
so every `ci.run` fixture and every `BuildResult` that validated at v0.30.0 still
validates byte-for-byte. That claim is pinned by tests in all three languages, not
just asserted.

Note the version: the demand allowed v0.32.0-or-later, but v0.32.0 and v0.33.0 were
already taken by other releases, so this is **v0.34.0**.

**1. `headSha` (acceptance criteria 1 + 2).** Optional on `CiRunPayload` (event
`ci.run`) in both `schemas/state-feed/state.event.json` and `state-event-java.yaml` —
edited together because `tests/check_state_event_sync.py` enforces structural sync —
and optional on `BuildResult` in `schemas/ci-runner/build-result.yaml`. Pattern
`^[0-9a-f]{40}$`: full 40 hex, lowercase only, matching every other revision field in
the platform. The `ci.run` payload carries it, and so does the `ci-runner` →
`control-plane` channel, so the two agree.

**2. The lookup interface (acceptance criterion 3).**
`schemas/delivery-api/ci-runner-results.openapi.yaml` (OpenAPI 3.1):

- `GET /delivery/v1/ci-results/{runId}/{jobId}` → `delivery.producer-result`.
- `GET /delivery/v1/ci-results?repository=&revision=` → `{repository, revision,
  items[]}` of `delivery.producer-result`, ordered by `observedAt` ascending.
- Both use the identity you already publish: `operationId` = `<runId>/<jobId>`,
  `nativeRef` = `ci-runner:ci.run/<runId>/<jobId>`, `repository` = platform repo name.
- **Not-found is a defined shape**, which is what the criterion asked for:
  `CiResultNotFoundError` — a `delivery.error` with `code` pinned `const:
  ci_result_not_found` and `retryable` pinned `const: false` — returned as `404`. The
  error envelope additionally names `422 invalid_request` and `503
  producer_unavailable` (your own store unreachable; that one *is* retryable).

**3. Docs (acceptance criterion 4).** `docs/task-delivery.md`: new §CI result routes
(route table, and the three rules that matter — `revision` is `headSha` or `null` and
never `ref`; a `null` revision cannot pass a revision gate; an empty by-revision
`items` is missing evidence, not a pass); the §Producers `ci-runner` row and the
handoff matrix row both updated to record the gap as **closed at the interface level**
with implementation explicitly remaining yours. A v0.34.0 repin section was added, and
the file's `Bindings` note was corrected: it previously said these shapes had no Java
binding, which is false for `ci.run`/`BuildResult` (`ci-runner` and `control-plane`
are Java services).

**4. Bindings regenerated (criterion 5).** TypeScript `build-result.ts` and
`state-event.ts` gain `headSha?: string` and `dist/` was rebuilt (D031 — committed,
not gitignored). Java: `events/CiRunPayload.java` regenerated via
openapi-generator-cli 7.23.0, and `gen/java/pom.xml` **bumped 0.30.0 → 0.34.0** —
this release changes Java output, unlike v0.33.0 which was TS+Python only.
`BuildResult` is jsonschema2pojo-generated into `target/` at build time and is not
committed. Python: `ci_runner/build_result.py` and `state_feed/state_event.py`
regenerated with the same flags as their previous generation, so the only diff is the
new field plus the codegen timestamp.

**5. Tests.** `tests/validate_state_event.py`: three `ci.run` cases — a 40-hex
`headSha` accepted, an abbreviated SHA and an uppercase SHA rejected, so the
lowercase-only pattern is enforced rather than assumed. `tests/validate_delivery.py`:
a `passed` `ci-runner` producer-result fixture and a new `check_ci_api` that asserts
both lookup routes and the `404` response exist and validates
`CiResultList`/`CiResultNotFoundError` against positive *and* negative fixtures
(63 cases total). `gen/java/src/test/.../CiHeadShaTest.java`: 5 JUnit cases, 44 in the
module, all green. Full suite: `python tests/run_all.py` → all validators passed;
`mvn -B -f gen/java/pom.xml test` → BUILD SUCCESS.

## D031 acceptance (measured, not assumed)

Run against the actual pushed tag, not a local build:

- **Python** — fresh venv, `pip install
  "git+https://github.com/elmoul/contracts.git@v0.34.0#subdirectory=gen/python"` →
  resolved to commit `9f6c2ea`, installed `platform-contracts-0.34.0`. `headSha` is on
  both models, absent → `None`, and a short SHA is rejected by the pattern.
- **TypeScript** — scratch project, `"@platform/contracts":
  "file:.../contracts-worktrees/v0.34.0/gen/ts"` → installed `0.34.0`;
  `tsc --noEmit --strict` passes on a consumer using `BuildResult`/`CiRunPayload`
  both with and without `headSha`.
- **Java** — `mvn install` from the pinned worktree into a **fresh**
  `-Dmaven.repo.local` → `io/platform/contracts/0.34.0/contracts-0.34.0.jar` and
  `.pom` produced.

## For the origin's next session

**Emit a real `headSha` or omit it — never reconstruct one from `ref`.** This is the
substantive ask. `ref` is a moving name: `main` at 09:00 and `main` at 11:00 are
different revisions under one string, which is exactly why a CI result could not be
correlated before this release. `headSha` is optional precisely so that "not
available" is expressible as absence — a zero SHA, a short SHA, or the value of `ref`
would all be worse than `null`, because they look like evidence and are not. The
schema rejects the first two outright and the docs pin `null` as the only alternative.

**The not-found rule is a correctness rule, not a convenience.** `404
ci_result_not_found` means *this service holds no record of that job* — never
observed, or past your retention. It is not a verdict about the build, and Factory is
instructed to record it as `unknown`. Do not upgrade it to `failed`, and do not let an
empty by-revision listing read as a pass: an empty `items` array is a `200` meaning
"no job is known for this revision", and a revision gate that passes on it is worse
than one that has no data at all.

**`503 producer_unavailable` is the retryable one.** Keep the two distinct — a caller
that cannot tell "your store is down" from "never ran" will either retry a
non-existent job forever or give up on one that exists.

**Repin and confirm the additive claim on your side.** Whatever binding you read these
from — `gen/ts` at `../contracts-worktrees/v0.34.0`, `io.platform:contracts:0.34.0`,
or the Python `@v0.34.0` pin — re-pin it and re-run your existing contract tests
against a `ci.run`/`BuildResult` document **without** `headSha`. That it still
validates is the whole basis of the additive claim; if it does not, that is a
contracts bug and a demand back to us.

**The release was additive, so no other consumer is obligated to move (D031)** and no
fleet-wide demand was raised. `factory` keeps consuming `delivery.producer-result` at
whatever pin it holds until it chooses to move — the by-revision lookup is useful to
it only once your side is live, which is a `ci-runner` leg, not a `contracts` one.
