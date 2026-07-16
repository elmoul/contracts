# Progress

> Entries before 2026-07-14 (Sessions 1-23, 2026-07-02 → 2026-07-14) archived
> verbatim to `docs/archive/PROGRESS-2026-07-02_2026-07-14.md` in the
> 2026-07-16 docs compaction pass; full history also in git log.

## Current state (as of 2026-07-16)

- **v0.13.0 is current** (tagged 2026-07-14): additive optional `skipped`
  field on `AiResponse` (`schemas/ai-gateway/request.yaml`); `result`/
  `model`/`provider` moved required → optional, absent when `skipped` is
  `true`. Fulfills ai-gateway's demand
  (`ai-gateway-20260714-contracts-skip-shape`).
- All three language bindings (Java/TS/Python) regenerated for v0.13.0; D031
  post-tag acceptance re-verified clean on all three, no unverified leg.
- Live build-context worktrees: `../contracts-worktrees/{v0.7.0,v0.11.0,v0.13.0}`.
  Older worktrees (v0.3.0-v0.6.2) were pruned 2026-07-16 as part of the
  platform-wide cleanup wave; their git tags are untouched and still
  resolvable.
- **D043 release-notification duty** — first exercised on v0.13.0: origin
  re-pin demand raised to ai-gateway (`contracts-20260714-ai-gateway-repin-skip-shape`)
  and archived to `demands/archive/` per the coordinator's `/satisfied/contracts`
  (see Session 25 below). **Flagged discrepancy:** `platform-vault/PLATFORM_STATE.md`
  (refreshed through 2026-07-15) still records ai-gateway's own Java pin at
  v0.11.0 with the v0.13.0 re-pin "not yet adopted" — the coordinator's
  satisfied-signal and ai-gateway's actual repo state disagree. Not
  adjudicated here; flagging for owner/vault reconciliation.
- **Real-world lesson from this release:** an additive schema change can still
  break strict-pydantic (`extra='forbid'`) Python consumers pinned to an older
  tag — sentinel-hub and orchestrator both hit live 500s on 2026-07-14 until
  re-pinned to v0.13.0 (Session 26 below; also recorded in the platform
  vault's late-evening addendum the same date).
- `demands/` currently holds: `README.md`, `archive/` (one closed-loop
  demand), `fulfilled/` (seven reports, most still awaiting demand-coordinator
  owner approval) — clean resting state, nothing stale (structural audit was
  Session 23, archived; counts here re-checked 2026-07-16).

## 2026-07-14 — Session 24 (v0.13.0 — ai.response `skipped` field, fulfilling ai-gateway's demand)

Fulfillment session for `ai-gateway-20260714-contracts-skip-shape` (`to: [contracts]`, confirmed live at the coordinator's `GET /inbox/contracts` before starting — read directly from `../ai-gateway/demands/2026-07-14-contracts-ai-response-skip-shape.md`).

- **State:** `schemas/ai-gateway/request.yaml`'s `AiResponse` gained the demand's own recommended shape (its owner-delegated ruling, applied verbatim): new optional `skipped: boolean` (default `false`); `result`/`model`/`provider` moved required → optional (absent when `skipped` is true); `tokensIn`/`tokensOut`/`computedCost` stayed required, valued `0` on a skipped call. Minor bump 0.12.0 → 0.13.0 (same precedent as v0.11.0's required→optional loosening — widens the accepted set, not a major-bump trigger). All three bindings regenerated and verified for real: Java (`mvn -B -f gen/java/pom.xml clean test`, `BUILD SUCCESS`, 12/12), TypeScript (`openapi-typescript` regen, `npx tsc --noEmit --strict` clean, also trued up `gen/ts/package-lock.json` to 0.13.0), Python (`datamodel-codegen --input-file-type openapi`, `result`/`model`/`provider` now `str | None`, `skipped: bool | None = False`). `tests/validate_ai_request.py` widened to cover `AiResponse` (3 new fixtures); full `python tests/run_all.py` clean. `CHANGELOG.md` v0.13.0 entry with full rationale (incl. the deliberate choice NOT to add JSON Schema conditional-required for "skipped implies result absent" — documented producer convention, not schema-enforced).
- **Tagged and pushed this same session** (`git tag v0.13.0 && git push origin main --tags`), then **full post-tag D031 acceptance test run for real, all three languages, no unverified leg**: Java (fresh `git clone --branch v0.13.0`, scratch `.m2` install, independent second scratch Maven consumer project constructing `AiResponse` both completed and skipped ways — `BUILD SUCCESS`), Python (fresh venv, `pip install git+...@v0.13.0#subdirectory=gen/python`, round-tripped both shapes, confirmed missing `tokensIn` rejected), TypeScript (`file:`-scratch project against the tagged checkout's committed `dist/`, `tsc --noEmit --strict` exit 0). All scratch dirs deleted after. Fulfillment report: `demands/fulfilled/ai-gateway-20260714-contracts-skip-shape-report.md` (status `done` — a claim, not a verdict; confirmed via the coordinator's `GET /pending-approval` that it landed correctly).
- **D043 release-notification duty — first exercise since it went live 2026-07-13:** raised `demands/2026-07-14-ai-gateway-repin-skip-shape.md` (`contracts-20260714-ai-gateway-repin-skip-shape`, `to: [ai-gateway]`, "re-pin and adopt v0.13.0"), pushed as its own standalone coordination commit. Additive release, so per D043's own scope this is origin-only — no fleet-wide "adopt or explain" (that's breaking-release-only). Confirmed live via `GET /inbox/ai-gateway`.
- **Toolchain reality:** local Maven 3.9.16 + JDK 21, Node/npm, and the pre-provisioned `.venv` (Python 3.11.9, `datamodel-code-generator` installed) all available — no unverified leg.
- **Next step:** Both the fulfillment report and the re-pin demand await the owner's coordinator approval — not this session's action to take. `ai-gateway`'s next session (once approved) re-pins to v0.13.0 and swaps `BrokerService.skippedResponse()`'s sentinel-value stopgap for `skipped: true`, per both reports' "what we do once closed."
- **Standing:** This is the template for D043 going forward — every future `contracts` tag now raises its origin demand (and, on a breaking release, the fleet-wide consumer demands) as part of the same session that cuts the tag, not a later audit.
- **Vault-sync:** none — no owner ruling made, no spec contradiction, no repo/port layout change; a routine additive schema release plus its own repo's already-vault-recorded D043 duty. `contracts`' own CLAUDE.md/spec/HEXAGON.md needed no edits.

## Session 25 — loop-close: ai-gateway repin+skip-shape demand satisfied
- State: coordinator's `/satisfied/contracts` confirmed ai-gateway re-pinned to v0.13.0 and adopted `AiResponse.skipped` (all 4 acceptance criteria met, 87/87 tests green in ai-gateway per its fulfillment report); demand envelope archived to `demands/archive/2026-07-14-ai-gateway-repin-skip-shape.md`.
- Next step: none — this closes the D043 release-notification duty for v0.13.0; no further action expected on contracts' side.
- Standing: D043 release checklist keeps working as designed — verify future releases still raise the origin demand and close loops this way.
- Vault-sync: none

## 2026-07-14 — Session 26 (worktree v0.13.0 for Python Docker build-contexts)

Owner-dispatched: architect found `sentinel-hub` and `orchestrator` both still pinned to `contracts` v0.7.0 (python), which predates the additive `skipped` field (v0.13.0) — their pydantic `AiResponse` model has `extra='forbid'`, so any live `ai-gateway` call now 500s with `ValidationError: skipped Extra inputs are not permitted`. Their `docker-compose.local.yml` Python service builds point `additional_contexts` at `../contracts-worktrees/<tag>/gen/python`, so the v0.13.0 checkout had to exist before either repo could re-pin.

- **State:** `git worktree add ../contracts-worktrees/v0.13.0 v0.13.0` — checkout at `a55cd9c` (tag v0.13.0), detached HEAD, matches the existing v0.3.0–v0.11.0 worktrees. Verified `gen/python/pyproject.toml` reads `version = "0.13.0"` and `gen/python/platform_contracts/ai_gateway/request.py`'s `AiResponse` carries the `skipped: bool | None = False` field plus `result`/`model`/`provider` as optional — matches the v0.13.0 CHANGELOG entry. Did not modify anything under `gen/`/`schemas/`; worktree creation produces no commit in the main repo (`git status` confirms working tree clean both before and after). Did not touch `sentinel-hub`, `orchestrator`, or `runtime` — those repos' own sessions re-pin and adopt.
- **Next step:** `sentinel-hub` and `orchestrator` re-pin their Python `contracts` dependency to v0.13.0 (via the now-existing worktree's `gen/python`) and drop any workaround for the `skipped` field being unrecognized. Not this repo's action to take further.
- **Standing:** Same as Session 21's note — worktrees are the established distribution mechanism for build-contexts (Java/Python Docker) and TS `file:` pins; add one per new consumed tag, never edit files inside a worktree.
- **Vault-sync:** none — no schema/version change, no owner ruling, no port/layout change; a pure local-checkout operation enabling two other repos' own re-pin work.

## 2026-07-16 — docs compaction (platform cleanup wave)

- **State:** Owner-commissioned platform-wide docs cleanup. `PROGRESS.md`
  compacted: Sessions 1-23 (2026-07-02 → 2026-07-14) moved verbatim to
  `docs/archive/PROGRESS-2026-07-02_2026-07-14.md`; this file now carries a
  Current-state summary plus the 3 newest entries (Sessions 24-26) verbatim.
  `CHANGELOG.md` slimmed in place (process-narration cut: command transcripts,
  D031 acceptance play-by-play, toolchain-availability notes); every version
  heading, date, breaking-change/migration note, and schema/binding bullet
  kept. Full unabridged original preserved verbatim at
  `docs/archive/CHANGELOG-verbose-pre-compaction.md`. No `schemas/`, `gen/`,
  or `demands/` content touched; no version bump.
- **Next step:** None pending from this session. Next release still owes the
  D043 checklist as normal.
- **Standing:** Same doc-hygiene lesson as Session 23's package-lock note —
  compaction is a between-tags/no-release activity; don't let it drift into
  touching schema or binding content.
- **Vault-sync:** none — no owner ruling, no schema/version/port change, no
  cross-repo-visible artifact moved (PROGRESS/CHANGELOG reorganization is
  internal to this repo's own docs).
