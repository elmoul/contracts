# Progress

> Entries before 2026-07-14 (Sessions 1-23, 2026-07-02 → 2026-07-14) archived
> verbatim to `docs/archive/PROGRESS-2026-07-02_2026-07-14.md` in the
> 2026-07-16 docs compaction pass; full history also in git log.

## Current state (as of 2026-07-16)

- **v0.14.0 is current** (tagged 2026-07-16): Wave 6 "Media & Agents"
  dependency-root release (`docs/MEDIA_AGENTS_WAVE_PACK.md` §5.1,
  D047/D048/D051/D053) — new `schemas/ai-gateway/job.yaml`
  (`ai.job.request`/`ai.job.status`) and three new `state.event` payload
  types (`job.progress`, `agent.run`, `design.mission`). Full detail in
  CHANGELOG.md; see Session 27 below for the release session itself.
- All three language bindings regenerated for v0.14.0. D031 acceptance this
  session covered **Java only** — fresh `.m2` install from the tagged
  worktree, jar contents inspected directly (`jar tf`) to confirm the new
  classes actually shipped, not just a green `BUILD SUCCESS` — matching the
  wave's own W1 gate ("tag + one consumer pin proven"). TypeScript/Python
  D031 acceptance were **not** independently re-run this release — flagged
  as an open leg in both CHANGELOG.md and Session 27 below.
- Live build-context worktrees:
  `../contracts-worktrees/{v0.7.0,v0.11.0,v0.13.0,v0.14.0}`. Older worktrees
  (v0.3.0-v0.6.2) were pruned 2026-07-16 as part of the platform-wide
  cleanup wave; their git tags are untouched and still resolvable.
- **D043 release-notification duty — exercised a second time (v0.14.0), and
  for the first time with no single downstream-consumer origin to re-pin.**
  v0.13.0 fulfilled `ai-gateway`'s own filed demand, so the origin was
  obvious. v0.14.0 is a wave-commissioned dependency-root release (the ask
  is wave pack §5.1 prose, landed via `platform-vault`'s own W0 session, not
  a demand filed from any one consumer's outbox) — `ai-gateway`,
  `state-feed`, and `dashboard` are all just wave-scheduled consumers
  (§5.2/§5.6), none of them "the origin" any more than the others. Raised
  `demands/2026-07-16-platform-vault-w1-gate.md`
  (`contracts-20260716-platform-vault-w1-gate`, `to: [platform-vault]`,
  `needs-owner: true`) instead — closes the W1 gate back to the wave's
  landing session and explicitly flags the origin-identification ambiguity
  for an owner ruling, rather than raising the fleet-wide re-pin demands a
  literal reading of the release brief pointed at (which D043 forbids for
  an additive release — "no fleet-wide everyone-bump"). See Session 27.
- `demands/` now holds: `README.md`, `archive/` (one closed-loop demand),
  `fulfilled/` (seven reports), and one new **open** demand
  (`2026-07-16-platform-vault-w1-gate.md`) awaiting the coordinator/owner.
- **Still standing from v0.13.0, unresolved:** the ai-gateway Java-pin
  register/actual-state discrepancy flagged 2026-07-15 (below), and the
  additive-schema-vs-strict-pydantic lesson from the same release (Session
  26 below) — neither is this session's to adjudicate.

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

## 2026-07-16 — Session 27 (v0.14.0 — Wave 6 job envelope + 3 state-event types; batch C release finalization)

Release-finalization session for Wave 6 "Media & Agents" W1
(`docs/MEDIA_AGENTS_WAVE_PACK.md` §5.1, D047/D048/D051/D053). Batches A+B
(schema authoring, the D023 error-required-on-failed amendment, all three
binding regens, test coverage — commits `c400f53`..`a4a9f02`) landed earlier
the same day; this session did the release mechanics only: version bump,
CHANGELOG, tag, worktree, `.m2` install, and the D043 duty.

- **State:** Version bumped 0.13.0 → 0.14.0 across `gen/java/pom.xml`,
  `gen/ts/package.json`, `gen/ts/package-lock.json` (both version fields —
  continuing the v0.13.0 precedent of trueing this file up),
  `gen/python/pyproject.toml`. `CHANGELOG.md` v0.14.0 entry added, written
  from the actual diffs (`git show` on all 7 pending commits, the raw
  `schemas/ai-gateway/job.yaml` and `schemas/state-feed/state.event.json`
  content), not transcribed from a summary — every claim in it
  (BUILD SUCCESS/12 tests, zero `com.google.gson` imports, "all validators
  passed", the 5-enum StrEnum conversion by name) was independently
  re-verified this session: `./.venv/Scripts/python.exe tests/run_all.py`
  (repo's own pre-provisioned venv — the global toolchain's `python312` is
  missing `pyyaml`, flagged for whoever next needs it), `mvn -B -f
  gen/java/pom.xml clean test` (BUILD SUCCESS, 12/12), `grep -rl
  com.google.gson gen/java/src` (zero hits). Committed as `3a210cf`
  ("release: v0.14.0 ..."). Tagged `v0.14.0` on that commit. Worktree
  `../contracts-worktrees/v0.14.0` created (D042 mechanism), confirmed
  `<version>0.14.0</version>`. `mvn -f
  .../contracts-worktrees/v0.14.0/gen/java/pom.xml clean install
  -DskipTests`: BUILD SUCCESS, installed to
  `~/.m2/repository/io/platform/contracts/0.14.0/`; contents verified with
  `jar tf` — `AiJobRequest`, `AiJobStatus`, `JobProgressEvent`,
  `AgentRunEvent`, `DesignMissionEvent` (+ nested enums) all actually
  present, not just a green build (this repo's own v0.9.0 history has a
  BUILD-SUCCESS-but-empty-stub precedent). This satisfies the wave's W1
  gate, "tag + one consumer pin proven" (`MEDIA_AGENTS_WAVE_PACK.md` §6).
  TypeScript/Python D031 acceptance (`file:` scratch project; fresh-venv
  git-URL install) were **not** run this session — out of the scope this
  release's own instructions set for STEP 2, and arguably consistent with
  the wave's "one consumer" framing, but flagged rather than silently
  assumed covered.
- **D043 duty — the one deliberate deviation from this session's own initial
  brief, flagged in full:** the release brief this session started from
  asked for a single demand file that nonetheless targeted three consumers
  with explicit sequencing (`state-feed` first, then `dashboard`, then
  `ai-gateway`) plus notes on `media-generation`/`agent-runner`/
  `design-studio` and the Python hub repos — a fleet-wide fan-out. Cross-
  checked against `CLAUDE.md`'s actual "Release checklist (per tag) — D043"
  section, `DEPLOYMENT.md`'s numbered step 6, `PLATFORM_DECISIONS.md`'s D043
  entry itself, and the fulfillment report that put the checklist in place
  (`demands/fulfilled/platform-vault-20260713-contracts-release-notification-duty-report.md`)
  — all four independently agree: **an additive release raises exactly one
  demand, to the origin, and explicitly not a fleet-wide "everyone bump."**
  v0.14.0 is additive. Further cross-checked
  `docs/MEDIA_AGENTS_WAVE_PACK.md` §5 and found `ai-gateway`'s (§5.2) and
  `state-feed`/`dashboard`'s (§5.6) re-pins are each already the wave pack's
  **own separately-scheduled demand**, due at their own later wave turn
  (W5, W7) — not something W1 should pre-empt. Followed the real checklist
  instead of the literal brief: raised exactly one demand,
  `demands/2026-07-16-platform-vault-w1-gate.md`
  (`contracts-20260716-platform-vault-w1-gate`, `to: [platform-vault]`,
  `needs-owner: true` — flags the origin-identification judgment call itself
  for a ruling, since D043 was never tested against a dependency-root
  release with no single filed origin demand behind it). Frontmatter
  validated for real against `schemas/demand-coordinator/demand.json`
  (`jsonschema` 4.26.0, Draft 2020-12) before committing — passes. Committed
  standalone as `aa183a3` ("chore(demands): raise D043 release-notification
  demand to platform-vault (v0.14.0)"), per `DEMAND_SYSTEM.md` §3.
- **Pushed:** `git push origin main --tags` — `ad985bc..aa183a3 main -> main`
  plus new tag `v0.14.0`. Verified no other local tag was pushed
  incidentally (`git ls-remote --tags origin` diffed against local `git tag
  -l` first — v0.1.0-v0.13.0 already matched remote). Post-push: `git
  status` clean, up to date with `origin/main`, 0 ahead/0 behind.
- **Next step:** Awaiting the coordinator/owner on
  `contracts-20260716-platform-vault-w1-gate` — both its stated acceptance
  criteria and its `needs-owner: true` origin-identification question.
  `ai-gateway` (W5) and `state-feed`+`dashboard` (W7) own their own re-pins
  next, per the wave pack, not a contracts follow-up.
- **Standing:** When a release's own brief and this repo's actual D043
  checklist disagree, the checklist wins — this is the second time that's
  been true this repo's history (see Session 24's owner-ruling-conflict note
  for the first). D043's "the origin" is well-defined for a
  demand-fulfillment release; it is *not* yet well-defined for a
  wave-commissioned dependency-root release — that gap is now flagged
  in-band (this demand's `needs-owner: true`) rather than quietly resolved
  by guessing.
- **Vault-sync:** demand raised contracts-20260716-platform-vault-w1-gate.
