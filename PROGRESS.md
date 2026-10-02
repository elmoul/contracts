# Progress

> Entries before 2026-07-14 (Sessions 1-23, 2026-07-02 → 2026-07-14) archived
> verbatim to `docs/archive/PROGRESS-2026-07-02_2026-07-14.md` in the
> 2026-07-16 docs compaction pass; full history also in git log.

## Current state (as of 2026-07-21)

- **v0.15.0 is current** (tagged 2026-07-21): Wave 7 session B-2 — landed the
  **Companion turn contract** (`stage.companion.turn`,
  `schemas/stage/companion.turn.yaml`) verbatim from plantpal's proven Wave 7
  A-4 implementation (`CompanionController`/`CompanionServiceImpl`), per
  doctrine §12 ("spec from working code, never the abstract"). Brand-new
  `stage/` domain — additive-only, mechanically verified (`git diff --stat --
  schemas/` against the pre-release tree touches nothing but the new file).
  Deliberately NOT landed (named in CHANGELOG so the boundary stays governed):
  the intent-bus resolution contract, the card-anatomy serialization format,
  the state→material mapping-table format — none has a working
  implementation to land from yet. All three bindings regenerated and
  D031-verified against the real tagged worktree
  (`../contracts-worktrees/v0.15.0`) — Java (`.m2` install + `jar tf`
  confirming the three new classes actually packaged), TypeScript
  (`file:`-scratch consumer project, `tsc --noEmit --strict` clean), Python
  (scratch-venv `pip install` + round-trip). Full
  `python tests/run_all.py` (11 validators + state-event sync) green. Per
  D054 (already ruled this exact ambiguity for v0.14.0), this release's D043
  origin is `platform-vault` — raised
  `demands/2026-07-21-platform-vault-b2-companion-turn-landed.md`
  (`contracts-20260721-platform-vault-b2-companion-turn-landed`, continuing
  the linked list, `prev: contracts-20260716-platform-vault-w1-gate`),
  carrying the **plantpal consumer-pin assessment** as its actual deliverable:
  plantpal (Java, pinned v0.7.0) uses six contracts
  (`app.health`/`app.manifest`/`ai.request`/`ai.response`/
  `dimension.event`/`state.event`); walked v0.7.0 → v0.15.0 against exactly
  those six and found every change additive (four unchanged outright,
  `ai.response`'s v0.13.0 `skipped` widening plantpal never triggers,
  `state.event`'s new `oneOf` members plantpal only produces from, never
  consumes as a union) — **a safe micro-session, not a real migration**. The
  repin itself is not executed here — owner-sequenced, per this session's own
  brief.
- **v0.14.0** (tagged 2026-07-16): Wave 6 "Media & Agents"
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

## 2026-07-21 — Session 28 (v0.15.0 — Companion turn contract, Wave 7 session B-2)

Owner-commissioned ("go B-2", Wave 7, `docs/WAVE_7_PACK_DRAFT.md`/D066): land
the PROVEN inhabited-stack contracts as the next minor version — scoped
strictly to what shipped and was proven live in plantpal's V2 build, per
doctrine §12.

- **State:** Read the real implementation first (read-only):
  `../plantpal/backend/.../companion/` (`CompanionController`,
  `CompanionServiceImpl`, `CompanionMessageRequest`/`Response`,
  `StageContextDto`) and `../plantpal/frontend/.../stage-kit/models/
  companion-turn.model.ts` + the app-owned `companion-message.model.ts`. New
  `schemas/stage/companion.turn.yaml` (OpenAPI 3.1): `CompanionMessageRequest`
  (`message` required, `pointableTargets`/`stageContext`/`priorCorrections`/
  `locale` all optional — matches the real DTO's own `@NotBlank`-only
  posture, not a stricter guess), `StageContext` (all fields optional,
  `coldStart` defaults `false`), `CompanionMessageResponse` (`say` required;
  `pointAt`/`evidence`/`confidence` optional). Two invariants are documented
  in the schema descriptions rather than schema-enforced, both by direct
  analogy to existing repo precedent: `pointAt`'s server-validated-against-
  the-request's-own-list rule (can't be expressed in JSON Schema at all — a
  cross-document constraint) and `evidence`/`confidence`'s travel-together-
  or-not-at-all pairing (same choice as `ai.response`'s v0.13.0 `skipped`
  shape — a producer-side convention, not worth an `if`/`then` for one
  producer). `stage/` chosen as a new domain (not a per-repo group) by
  analogy to `app/`'s existing precedent, after reading the full
  `schemas/` taxonomy first.
- **Additive-only, proven, not assumed:** `git diff --stat -- schemas/`
  against the pre-release tree is empty apart from the one new file — zero
  existing schema touched, checked mechanically before writing the CHANGELOG
  claim.
- **Bindings regenerated, all three, verified for real:** Java
  (`openapi-generator-cli` 7.23.0 `--library resttemplate`, matching
  `ai-gateway/job.yaml`'s precedent — not wired into `pom.xml`, generated via
  the documented `npx` CLI invocation; `mvn -f gen/java/pom.xml clean test`
  BUILD SUCCESS 12/12, zero `com.google.gson` imports). TypeScript
  (`openapi-typescript`, re-exported from `index.ts`, `dist/` rebuilt, `npx
  tsc --noEmit --strict` clean). Python (`datamodel-codegen --input-file-type
  openapi --target-python-version 3.11 --use-specialized-enum`; `Confidence`
  came out `StrEnum` correctly this time — no drift to fix, unlike v0.14.0's
  `state_event.py` incident). Added `tests/validate_stage_companion_turn.py`
  (10 assertions), wired into `tests/run_all.py`; full suite (11 validators +
  state-event sync) green.
- **D031 acceptance — all three languages, against the real tagged worktree,
  no unverified leg:** `git worktree add ../contracts-worktrees/v0.15.0
  v0.15.0`. Java: fresh `.m2` install from that worktree, `jar tf` confirming
  `CompanionMessageRequest`/`StageContext`/`CompanionMessageResponse`
  actually packaged (not just a green build — this repo's own v0.9.0
  empty-stub precedent). TypeScript: `file:`-scratch consumer project against
  the worktree's committed `gen/ts/dist/`, `tsc --noEmit` clean. Python:
  scratch venv, `pip install` from the worktree's `gen/python`, round-tripped
  a `CompanionMessageResponse`. All scratch dirs deleted after.
- **Conventions validator green** (`java -jar
  conventions/validator/target/conventions-validator-0.1.0.jar contracts`):
  14 checks, 0 failed, 1 pre-existing UNVERIFIED (`status-coherence` — a
  vault-owned `PLATFORM_STATE.md` text-classification gap that predates this
  session, unrelated to `stage/`).
- **Consumer-pin assessment (the B-2 gate — evidence, not execution):**
  plantpal pins `contracts` v0.7.0 (Java) and uses six contracts. Walked every
  CHANGELOG entry v0.8.0 → v0.15.0 against exactly those six:
  `app.health`/`app.manifest`/`ai.request`/`dimension.event` — zero changes.
  `ai.response` — one additive change (v0.13.0's `skipped` field,
  required→optional widening on `result`/`model`/`provider`); plantpal reads
  it via plain getters, never triggers `skipped: true` today. `state.event` —
  two additive `oneOf` widenings (v0.7.0's own `activity.count`, already
  plantpal's baseline; v0.14.0's three more members); plantpal only
  *produces* `state.event` via concrete generated classes, never deserializes
  the union, so the new members are structurally inert for it. Java
  package/artifact coordinates unchanged throughout. **Verdict: a safe
  micro-session, not a real migration** — full per-contract evidence trail in
  `CHANGELOG.md`'s v0.15.0 entry and in the demand below. Did not execute the
  repin — plantpal's own session, owner-sequenced, per this session's brief.
- **D043 duty:** per D054 (already ruled this exact ambiguity for v0.14.0 —
  a wave-commissioned release with no filed consumer demand has
  `platform-vault` as its origin, forming a linked list of origins), raised
  `demands/2026-07-21-platform-vault-b2-companion-turn-landed.md`
  (`contracts-20260721-platform-vault-b2-companion-turn-landed`,
  `prev: contracts-20260716-platform-vault-w1-gate`), carrying the
  consumer-pin assessment as its payload. Frontmatter checked against
  `schemas/demand-coordinator/demand.json` before committing.
- **Pushed:** `git push origin main --tags`.
- **Next step:** Awaiting the coordinator/owner on
  `contracts-20260721-platform-vault-b2-companion-turn-landed`. plantpal's
  own repin session (v0.7.0 → v0.15.0, six contracts, additive-only per this
  session's evidence) is next, owner-sequenced — not a `contracts` follow-up.
- **Standing:** A second real exercise of D054's linked-list-of-origins
  pattern — the mechanism holds up cleanly for a second owner-commissioned,
  no-filed-demand release. `stage/` is now a live precedent for a
  cross-tenant capability domain (alongside `app/`) — the next inhabited-stack
  landing (intent-bus or card-anatomy, whenever either has a working
  implementation to extract from) has a taxonomy slot to land into without
  re-deriving one.
- **Vault-sync:** demand raised
  contracts-20260721-platform-vault-b2-companion-turn-landed.

## Session 29 (2026-07-22) — v0.16.0, `design.designSystem` state-event member

- **Picked up an interrupted prior session:** the working tree already held a
  fully-built, uncommitted v0.16.0 (schemas, all three regenerated bindings,
  `CHANGELOG.md` entry, version bumps, extended
  `tests/validate_state_event.py`) fulfilling demand
  `design-studio-20260722-contracts-design-system-state-event` — new
  `design.designSystem` `state.event` `oneOf` member (10th), mirroring
  `design.mission`'s envelope exactly: `DesignSystemPayload` (`designSystemId`,
  `name`, `slug`, `version`, `regime` — reuses `DesignMissionPayload`'s
  existing enum verbatim, `status` new enum, `origin` new enum distinct from
  the envelope-level `Origin`, `sourceMissionId` optional, `change`). Verified
  the uncommitted state matched the demand's acceptance criteria exactly
  before proceeding (no rework needed) — see full diff review in this
  session's tool history if ever needed.
- **Verified before committing:** `python tests/run_all.py` (11 validators +
  state-event sync check) green; `mvn -f gen/java/pom.xml test` BUILD
  SUCCESS 12/12; `npx tsc --noEmit` clean in `gen/ts`.
- **Committed and tagged:** `53e43d6` "release: v0.16.0", tag `v0.16.0`,
  pushed (`git push origin main --tags`).
- **D031 acceptance — all three languages, against the real tagged
  worktree, no unverified leg:** `git worktree add
  ../contracts-worktrees/v0.16.0 v0.16.0`. Java: fresh `.m2` install from
  that worktree, `jar tf` confirmed `DesignSystemEvent`/`DesignSystemPayload`
  (+ nested enums) actually packaged; a scratch Maven consumer project
  depending on `io.platform:contracts:0.16.0` compiled and ran code
  constructing a full event. Python: fresh venv, `pip install
  git+...@v0.16.0#subdirectory=gen/python`, round-tripped a
  `DesignSystemEvent`, confirmed the `StateEvent` union accepts it, confirmed
  a bad `status` value raises `ValidationError`. TypeScript: `file:`-scratch
  consumer project against the worktree's committed `gen/ts`, assigning a
  `DesignSystemEvent` to the `StateEvent` union — `npx tsc --noEmit` clean.
  All scratch dirs and the worktree deleted after.
- **D043 duty:** this release fulfils a real filed demand (not a
  wave-commissioned no-demand release), so the origin is `design-studio`
  directly — no D054 linked-list needed. Wrote
  `demands/fulfilled/design-studio-20260722-contracts-design-system-state-event-report.md`
  (worker duty, §4) and raised
  `demands/2026-07-22-design-studio-repin-design-system-event.md`
  (`contracts-20260722-design-studio-repin-design-system-event`, origin duty,
  §3 — "re-pin and adopt v0.16.0"). Additive release, so per D043 only the
  origin demand is required, no fleet-wide "adopt or explain". Both
  frontmatters validated against `schemas/demand-coordinator/demand.json` /
  `demand.fulfillment.json` before committing. Committed `d45a7b6`, pushed.
- **Next step:** Awaiting the coordinator/owner on
  `contracts-20260722-design-studio-repin-design-system-event`. `design-studio`'s
  own repin-and-adopt session is next, not a `contracts` follow-up.
- **Standing:** first `contracts` release where the D043 origin demand traces
  straight back to a real filed consumer demand rather than through D054's
  linked-list fallback — the ordinary case the release checklist was written
  for.

## Session 30 — 2026-07-23

- **State:** `v0.17.0` tagged and pushed. Fulfilled
  `design-studio-20260723-contracts-atlas-class-regime-enum`: the shared
  `Regime` enum (used by both `DesignMissionPayload.regime` and
  `DesignSystemPayload.regime` in `state.event`) gained a third member,
  `atlas-class`, alongside `console-class`/`inhabited-class`. Purely
  additive — no existing enum value, required field, or payload shape
  touched (verified: `git diff --stat -- schemas/` against the pre-release
  tree touches only `state.event.json` and its `state-event-java.yaml`
  mirror). `tests/validate_state_event.py` extended with one new
  known-good fixture per payload; existing `BAD_DESIGN_MISSION_UNKNOWN_REGIME`
  (`hybrid-class`) fixture untouched and still rejected. All three bindings
  regenerated (Python: `datamodel-codegen --target-python-version 3.11
  --use-specialized-enum`, `Regime` gains `atlas_class = 'atlas-class'`;
  TypeScript: `json-schema-to-typescript` + `dist/` rebuild, `tsc --noEmit`
  clean; Java: `openapi-generator-cli` 7.23.0, `RegimeEnum` gains
  `ATLAS_CLASS` on both payload classes, `mvn test` BUILD SUCCESS 12/12).
  `python tests/run_all.py` (11 validators + state-event sync check) green.
  **D031 acceptance, real tagged worktree, no unverified leg:** `git
  worktree add ../contracts-worktrees/v0.17.0 v0.17.0`. Python: fresh venv,
  `pip install git+...@v0.17.0#subdirectory=gen/python`, constructed
  `ContractRegime('atlas-class')` directly (the exact call
  `design-studio/src/design_studio/adapters/event_sink_state_feed.py:188`/
  `:210` make), round-tripped `DesignMissionPayload`/`DesignSystemPayload`,
  confirmed the `StateEvent` union accepts an atlas-class mission event,
  confirmed `hybrid-class` still raises `ValueError`. Java: fresh `.m2`
  install from the worktree; a scratch Maven consumer compiled and ran
  code constructing `RegimeEnum.ATLAS_CLASS`. TypeScript: `file:`-scratch
  consumer against the worktree's committed `gen/ts`, assigning
  `regime: "atlas-class"` to a full `StateEvent` — `tsc --noEmit` clean.
  All scratch dirs and the worktree deleted after.
- **D043 duty:** real filed demand as origin (`design-studio`), no D054
  linked-list needed. Wrote
  `demands/fulfilled/design-studio-20260723-contracts-atlas-class-regime-enum-report.md`
  (worker duty, §4) and raised
  `demands/2026-07-23-design-studio-repin-atlas-class-regime-enum.md`
  (`contracts-20260723-design-studio-repin-atlas-class-regime-enum`, origin
  duty, §3 — "re-pin and adopt v0.17.0"). Additive release, so per D043
  only the origin demand is required. Committed `713006b`, pushed.
- **Next step:** Awaiting the coordinator/owner on
  `contracts-20260723-design-studio-repin-atlas-class-regime-enum`.
  `design-studio`'s own repin-and-adopt session is next, not a `contracts`
  follow-up.
- **Standing:** same pattern as v0.16.0/v0.17.0's predecessor — a real
  filed consumer demand traced straight through to its D043 origin demand,
  no linked-list fallback needed.

## Session 31 (2026-08-02)

Full narrative, decisions, and context trail: `.brain/sessions/2026-08-02_0155_fulfill-brain-toolkit-demand-adopt-brain.md`
(the session file is the source of truth in this D052-piloted repo -- the block
below is a **generated projection** of it, produced mechanically by
`brain session close`, not a second hand-written account).

- State: Fulfill brain-toolkit demand: adopt .brain in contracts -- status: done.
- Next step: Await coordinator validation of the fulfillment report. No contracts follow-up pending.
- Standing: TODO -- no repo convention recorded yet (seeded 2026-08-02 by brain-toolkit bin/adopt v0.6.2)
- Vault-sync: none -- adoption is additive repo tooling; no schema, version, or tag change, so no vault amendment needed
- Session: 2026-08-02_0155_fulfill-brain-toolkit-demand-adopt-brain

## Session 32 (2026-08-04)

Full narrative, decisions, and context trail: `.brain/sessions/2026-08-04_0757_fulfill-demand-design-studio-20260804-co-2.md`
(the session file is the source of truth in this D052-piloted repo -- the block
below is a **generated projection** of it, produced mechanically by
`brain session close`, not a second hand-written account).

- State: fulfill demand design-studio-20260804-contracts-guided-turn-class-regime-enum -- status: done.
- Next step: See the session file's `## Log` for open follow-ups.
- Standing: TODO -- no repo convention recorded yet (seeded 2026-08-02 by brain-toolkit bin/adopt v0.6.2)
- Vault-sync: none
- Session: 2026-08-04_0757_fulfill-demand-design-studio-20260804-co-2

## Session 33 (2026-08-04)

Full narrative, decisions, and context trail: `.brain/sessions/2026-08-04_0757_fulfill-demand-design-studio-20260804-co.md`
(the session file is the source of truth in this D052-piloted repo -- the block
below is a **generated projection** of it, produced mechanically by
agent-runner's dispatch supervisor from an auto-drafted, unconfirmed close --
not a second hand-written account, and not yet reviewed by a human or the
worker agent itself).

- State: Fulfill demand design-studio-20260804-contracts-guided-turn-class-regime-enum (capability: a fourth Regime member, guided-turn-class, on the state-feed design events, plus a pinnable release, from: design-studio, target: contracts). Acceptance criteria: - the Regime enum on the state-feed design eve... -- status: done (close: auto-drafted, unconfirmed).
- Next step: Review this session's auto-drafted close (`.brain/sessions/2026-08-04_0757_fulfill-demand-design-studio-20260804-co.md`) and confirm or correct it.
- Standing: TODO -- no repo convention recorded yet (seeded 2026-08-02 by brain-toolkit bin/adopt v0.6.2)
- Vault-sync: none
- Session: 2026-08-04_0757_fulfill-demand-design-studio-20260804-co

## Session 34 (2026-08-04)

Full narrative, decisions, and context trail: `.brain/sessions/2026-08-04_0816_fulfill-demand-app-studio-20260804-contr.md`
(the session file is the source of truth in this D052-piloted repo -- the block
below is a **generated projection** of it, produced mechanically by
`brain session close`, not a second hand-written account).

- State: Fulfill demand app-studio-20260804-contracts-app-mission-and-task-plan (capability: add app.mission and app.task-plan as additive schemas, now that a real genesis mission has proved both shapes end to end, from: app-studio, target: contracts). Acceptance criteria: - schemas/app-studio/app.mission.js... -- status: done.
- Next step: Await coordinator validation; archive demands/2026-08-04-app-studio-repin-app-mission-and-task-plan.md once app-studio's re-pin is reported satisfied.
- Standing: TODO -- no repo convention recorded yet (seeded 2026-08-02 by brain-toolkit bin/adopt v0.6.2)
- Vault-sync: none
- Session: 2026-08-04_0816_fulfill-demand-app-studio-20260804-contr

## Session 35 (2026-08-04)

Full narrative, decisions, and context trail: `.brain/sessions/2026-08-04_0842_close-the-loop-on-demand-contracts-20260.md`
(the session file is the source of truth in this D052-piloted repo -- the block
below is a **generated projection** of it, produced mechanically by
agent-runner's dispatch supervisor from an auto-drafted, unconfirmed close --
not a second hand-written account, and not yet reviewed by a human or the
worker agent itself).

- State: Close the loop on demand contracts-20260804-design-studio-repin-guided-turn-class-regime-enum. It was approved at 2026-08-04T07:24:12.825231Z -- the only thing left is this repo's own archive bookkeeping, which nobody has done yet. 1. GET http://localhost:8082/satisfied/contracts -- find contracts-2... -- status: done (close: auto-drafted, unconfirmed).
- Next step: Review this session's auto-drafted close (`.brain/sessions/2026-08-04_0842_close-the-loop-on-demand-contracts-20260.md`) and confirm or correct it.
- Standing: TODO -- no repo convention recorded yet (seeded 2026-08-02 by brain-toolkit bin/adopt v0.6.2)
- Vault-sync: none
- Session: 2026-08-04_0842_close-the-loop-on-demand-contracts-20260

## Session 36 (2026-08-04)

Full narrative, decisions, and context trail: `.brain/sessions/2026-08-04_0845_fulfill-demand-state-feed-20260804-state.md`
(the session file is the source of truth in this D052-piloted repo -- the block
below is a **generated projection** of it, produced mechanically by
`brain session close`, not a second hand-written account).

- State: fulfill demand state-feed-20260804-state-event-app-mission-member -- status: done.
- Next step: See the session file's `## Log` for open follow-ups.
- Standing: TODO -- no repo convention recorded yet (seeded 2026-08-02 by brain-toolkit bin/adopt v0.6.2)
- Vault-sync: none
- Session: 2026-08-04_0845_fulfill-demand-state-feed-20260804-state

## Session 37 (2026-08-04)

Full narrative, decisions, and context trail: `.brain/sessions/2026-08-04_0844_fulfill-demand-state-feed-20260804-state.md`
(the session file is the source of truth in this D052-piloted repo -- the block
below is a **generated projection** of it, produced mechanically by
agent-runner's dispatch supervisor from an auto-drafted, unconfirmed close --
not a second hand-written account, and not yet reviewed by a human or the
worker agent itself).

- State: Fulfill demand state-feed-20260804-state-event-app-mission-member (capability: Add an app.mission member to the state.event oneOf union (and its Java binding), so state-feed can accept an app.mission state-event type-safely, from: state-feed, target: contracts). Acceptance criteria: - schemas/state-... -- status: done (close: auto-drafted, unconfirmed).
- Next step: Review this session's auto-drafted close (`.brain/sessions/2026-08-04_0844_fulfill-demand-state-feed-20260804-state.md`) and confirm or correct it.
- Standing: TODO -- no repo convention recorded yet (seeded 2026-08-02 by brain-toolkit bin/adopt v0.6.2)
- Vault-sync: none
- Session: 2026-08-04_0844_fulfill-demand-state-feed-20260804-state

## Session 38 (2026-08-04)

Full narrative, decisions, and context trail: `.brain/sessions/2026-08-04_0855_close-the-loop-on-demand-contracts-20260.md`
(the session file is the source of truth in this D052-piloted repo -- the block
below is a **generated projection** of it, produced mechanically by
agent-runner's dispatch supervisor from an auto-drafted, unconfirmed close --
not a second hand-written account, and not yet reviewed by a human or the
worker agent itself).

- State: Close the loop on demand contracts-20260804-app-studio-repin-app-mission-and-task-plan. It was approved at 2026-08-04T07:55:27.080241Z -- the only thing left is this repo's own archive bookkeeping, which nobody has done yet. 1. GET http://localhost:8082/satisfied/contracts -- find contracts-20260804... -- status: done (close: auto-drafted, unconfirmed).
- Next step: Review this session's auto-drafted close (`.brain/sessions/2026-08-04_0855_close-the-loop-on-demand-contracts-20260.md`) and confirm or correct it.
- Standing: TODO -- no repo convention recorded yet (seeded 2026-08-02 by brain-toolkit bin/adopt v0.6.2)
- Vault-sync: none
- Session: 2026-08-04_0855_close-the-loop-on-demand-contracts-20260

## Session 39 (2026-08-04)

Full narrative, decisions, and context trail: `.brain/sessions/2026-08-04_0903_fulfill-demand-app-studio-20260804-contr.md`
(the session file is the source of truth in this D052-piloted repo -- the block
below is a **generated projection** of it, produced mechanically by
`brain session close`, not a second hand-written account).

- State: Fulfill demand app-studio-20260804-contracts-binding-direction-array (capability: correct app.mission's gateContext.bindingDirection from a nullable string to a nullable array of strings, so a gate that has rejected more than once validates, from: app-studio, target: contracts). Acceptance criteria:... -- status: done.
- Next step: See the session file's `## Log` for open follow-ups.
- Standing: TODO -- no repo convention recorded yet (seeded 2026-08-02 by brain-toolkit bin/adopt v0.6.2)
- Vault-sync: none
- Session: 2026-08-04_0903_fulfill-demand-app-studio-20260804-contr

## Session 40 (2026-08-04)

Full narrative, decisions, and context trail: `.brain/sessions/2026-08-04_0950_close-the-loop-on-demand-contracts-20260.md`
(the session file is the source of truth in this D052-piloted repo -- the block
below is a **generated projection** of it, produced mechanically by
agent-runner's dispatch supervisor from an auto-drafted, unconfirmed close --
not a second hand-written account, and not yet reviewed by a human or the
worker agent itself).

- State: Close the loop on demand contracts-20260804-state-feed-repin-app-mission-event. It was approved at 2026-08-04T08:07:38.887506Z -- the only thing left is this repo's own archive bookkeeping, which nobody has done yet. 1. GET http://localhost:8082/satisfied/contracts -- find contracts-20260804-state-f... -- status: done (close: auto-drafted, unconfirmed).
- Next step: Review this session's auto-drafted close (`.brain/sessions/2026-08-04_0950_close-the-loop-on-demand-contracts-20260.md`) and confirm or correct it.
- Standing: TODO -- no repo convention recorded yet (seeded 2026-08-02 by brain-toolkit bin/adopt v0.6.2)
- Vault-sync: none
- Session: 2026-08-04_0950_close-the-loop-on-demand-contracts-20260

## Session 41 (2026-08-04)

Full narrative, decisions, and context trail: `.brain/sessions/2026-08-04_1011_close-the-loop-on-demand-contracts-20260.md`
(the session file is the source of truth in this D052-piloted repo -- the block
below is a **generated projection** of it, produced mechanically by
agent-runner's dispatch supervisor from an auto-drafted, unconfirmed close --
not a second hand-written account, and not yet reviewed by a human or the
worker agent itself).

- State: Close the loop on demand contracts-20260804-app-studio-repin-binding-direction-array. It was approved at 2026-08-04T09:04:42.247772Z -- the only thing left is this repo's own archive bookkeeping, which nobody has done yet. 1. GET http://localhost:8082/satisfied/contracts -- find contracts-20260804-a... -- status: done (close: auto-drafted, unconfirmed).
- Next step: Review this session's auto-drafted close (`.brain/sessions/2026-08-04_1011_close-the-loop-on-demand-contracts-20260.md`) and confirm or correct it.
- Standing: TODO -- no repo convention recorded yet (seeded 2026-08-02 by brain-toolkit bin/adopt v0.6.2)
- Vault-sync: none
- Session: 2026-08-04_1011_close-the-loop-on-demand-contracts-20260

## Session 42 (2026-08-04)

Full narrative, decisions, and context trail: `.brain/sessions/2026-08-04_1505_fulfill-demand-app-studio-20260804-contr.md`
(the session file is the source of truth in this D052-piloted repo -- the block
below is a **generated projection** of it, produced mechanically by
`brain session close`, not a second hand-written account).

- State: Fulfill demand app-studio-20260804-contracts-verify-step-channel (capability: `app.task-plan`'s verify step gains an optional `channel` — the input path that could carry the thing an absence criterion excludes, from: app-studio, target: contracts). Acceptance criteria: - `app.task-plan`'s verify-ste... -- status: done.
- Next step: app-studio closes the consuming leg: re-pin v0.22.0, fill channel on absence steps, drop the recorded gap
- Standing: TODO -- no repo convention recorded yet (seeded 2026-08-02 by brain-toolkit bin/adopt v0.6.2)
- Vault-sync: none
- Session: 2026-08-04_1505_fulfill-demand-app-studio-20260804-contr

## Session 43 (2026-08-04)

Full narrative, decisions, and context trail: `.brain/sessions/2026-08-04_2255_archive-demand-contracts-20260804-app-st.md`
(the session file is the source of truth in this D052-piloted repo -- the block
below is a **generated projection** of it, produced mechanically by
`brain session close`, not a second hand-written account).

- State: archive demand contracts-20260804-app-studio-repin-verify-step-channel -- status: done.
- Next step: See the session file's `## Log` for open follow-ups.
- Standing: TODO -- no repo convention recorded yet (seeded 2026-08-02 by brain-toolkit bin/adopt v0.6.2)
- Vault-sync: none
- Session: 2026-08-04_2255_archive-demand-contracts-20260804-app-st

## Session 44 (2026-08-04)

Full narrative, decisions, and context trail: `.brain/sessions/2026-08-04_2255_close-the-loop-on-demand-contracts-20260.md`
(the session file is the source of truth in this D052-piloted repo -- the block
below is a **generated projection** of it, produced mechanically by
agent-runner's dispatch supervisor from an auto-drafted, unconfirmed close --
not a second hand-written account, and not yet reviewed by a human or the
worker agent itself).

- State: Close the loop on demand contracts-20260804-app-studio-repin-verify-step-channel. It was approved at 2026-08-04T21:55:07.195085Z -- the only thing left is this repo's own archive bookkeeping, which nobody has done yet. 1. GET http://localhost:8082/satisfied/contracts -- find contracts-20260804-app-s... -- status: done (close: auto-drafted, unconfirmed).
- Next step: Review this session's auto-drafted close (`.brain/sessions/2026-08-04_2255_close-the-loop-on-demand-contracts-20260.md`) and confirm or correct it.
- Standing: TODO -- no repo convention recorded yet (seeded 2026-08-02 by brain-toolkit bin/adopt v0.6.2)
- Vault-sync: none
- Session: 2026-08-04_2255_close-the-loop-on-demand-contracts-20260

## Session 45 (2026-08-05)

Full narrative, decisions, and context trail: `.brain/sessions/2026-08-05_0407_fulfill-demand-app-studio-20260805-contr.md`
(the session file is the source of truth in this D052-piloted repo -- the block
below is a **generated projection** of it, produced mechanically by
`brain session close`, not a second hand-written account).

- State: Fulfill demand app-studio-20260805-contracts-mission-consistency: add optional consistency object to app.mission -- status: done.
- Next step: See the session file's `## Log` for open follow-ups.
- Standing: TODO -- no repo convention recorded yet (seeded 2026-08-02 by brain-toolkit bin/adopt v0.6.2)
- Vault-sync: none
- Session: 2026-08-05_0407_fulfill-demand-app-studio-20260805-contr

## Session 46 (2026-08-05)

Full narrative, decisions, and context trail: `.brain/sessions/2026-08-05_0405_fulfill-demand-app-studio-20260805-contr.md`
(the session file is the source of truth in this D052-piloted repo -- the block
below is a **generated projection** of it, produced mechanically by
agent-runner's dispatch supervisor from an auto-drafted, unconfirmed close --
not a second hand-written account, and not yet reviewed by a human or the
worker agent itself).

- State: Fulfill demand app-studio-20260805-contracts-mission-consistency (capability: `app.mission` gains an optional `consistency` object — the ledger-vs-artifact divergence report, so a console reading a mission sees a contradiction without having to ask a second question, from: app-studio, target: contra... -- status: done (close: auto-drafted, unconfirmed).
- Next step: Review this session's auto-drafted close (`.brain/sessions/2026-08-05_0405_fulfill-demand-app-studio-20260805-contr.md`) and confirm or correct it.
- Standing: TODO -- no repo convention recorded yet (seeded 2026-08-02 by brain-toolkit bin/adopt v0.6.2)
- Vault-sync: none
- Session: 2026-08-05_0405_fulfill-demand-app-studio-20260805-contr

## Session 47 (2026-08-05)

Full narrative, decisions, and context trail: `.brain/sessions/2026-08-05_0459_close-the-loop-on-demand-contracts-20260.md`
(the session file is the source of truth in this D052-piloted repo -- the block
below is a **generated projection** of it, produced mechanically by
agent-runner's dispatch supervisor from an auto-drafted, unconfirmed close --
not a second hand-written account, and not yet reviewed by a human or the
worker agent itself).

- State: Close the loop on demand contracts-20260805-app-studio-repin-mission-consistency. It was approved at 2026-08-05T03:53:13.481916Z -- the only thing left is this repo's own archive bookkeeping, which nobody has done yet. 1. GET http://localhost:8082/satisfied/contracts -- find contracts-20260805-app-s... -- status: done (close: auto-drafted, unconfirmed).
- Next step: Review this session's auto-drafted close (`.brain/sessions/2026-08-05_0459_close-the-loop-on-demand-contracts-20260.md`) and confirm or correct it.
- Standing: TODO -- no repo convention recorded yet (seeded 2026-08-02 by brain-toolkit bin/adopt v0.6.2)
- Vault-sync: none
- Session: 2026-08-05_0459_close-the-loop-on-demand-contracts-20260

## Session 48 (2026-09-14)

Full narrative, decisions, and context trail: `.brain/sessions/2026-09-13_2352_fulfill-demand-demand-coordinator-202609.md`
(the session file is the source of truth in this D052-piloted repo -- the block
below is a **generated projection** of it, produced mechanically by
`brain session close`, not a second hand-written account).

- State: Fulfill demand demand-coordinator-20260913-contracts-approved-evidence-receipt (capability: Define a governed approval-evidence receipt for exact-ID durable approval lookup, from: demand-coordinator, target: contracts). Acceptance criteria: - A versioned contract defines an immutable approval receip... -- status: done.
- Next step: demand-coordinator re-pins to v0.24.0 and adopts DemandApprovalReceipt per the raised demand
- Standing: TODO -- no repo convention recorded yet (seeded 2026-08-02 by brain-toolkit bin/adopt v0.6.2)
- Vault-sync: none
- Session: 2026-09-13_2352_fulfill-demand-demand-coordinator-202609

## Session 49 (2026-09-14)

Full narrative, decisions, and context trail: `.brain/sessions/2026-09-14_0052_fulfill-demand-factory-20260911-interfac.md`
(the session file is the source of truth in this D052-piloted repo -- the block
below is a **generated projection** of it, produced mechanically by
`brain session close`, not a second hand-written account).

- State: Fulfill demand factory-20260911-interface-extraction (capability: Govern Factory delivery and runner idempotency interfaces before cross-repo consumption, from: factory, target: contracts). Acceptance criteria: - Review the proven local Factory models and publish additive outcome, evidence, continua... -- status: done.
- Next step: See the session file's `## Log` for open follow-ups.
- Standing: TODO -- no repo convention recorded yet (seeded 2026-08-02 by brain-toolkit bin/adopt v0.6.2)
- Vault-sync: none
- Session: 2026-09-14_0052_fulfill-demand-factory-20260911-interfac

## Session 50 (2026-09-14)

Full narrative, decisions, and context trail: `.brain/sessions/2026-09-14_0144_close-the-loop-on-demand-contracts-20260.md`
(the session file is the source of truth in this D052-piloted repo -- the block
below is a **generated projection** of it, produced mechanically by
`brain session close`, not a second hand-written account).

- State: Close the loop on demand contracts-20260913-demand-coordinator-repin-approval-receipt. It was approved at 2026-09-14T00:10:51.057726Z -- the only thing left is this repo's own archive bookkeeping, which nobody has done yet. 1. GET http://localhost:8082/satisfied/contracts -- find contracts-20260913-... -- status: done.
- Next step: See the session file's `## Log` for open follow-ups.
- Standing: TODO -- no repo convention recorded yet (seeded 2026-08-02 by brain-toolkit bin/adopt v0.6.2)
- Vault-sync: none
- Session: 2026-09-14_0144_close-the-loop-on-demand-contracts-20260

## Session 51 (2026-09-14)

Full narrative, decisions, and context trail: `.brain/sessions/2026-09-14_0159_fulfill-demand-dashboard-20260914-demand.md`
(the session file is the source of truth in this D052-piloted repo -- the block
below is a **generated projection** of it, produced mechanically by
`brain session close`, not a second hand-written account).

- State: Fulfill demand dashboard-20260914-demand-dispatch-order (capability: Demands can declare which other demands must be owner-approved before they are dispatched, and the dispatch queue carries a governed order number (wave) plus the still-waiting demands, so the /agents Dispatch queue can show an Orde... -- status: done.
- Next step: Coordinator should advance dashboard-20260914-demand-dispatch-order past the contracts leg and dispatch the remaining targets (demand-coordinator -> runtime -> agent-runner). Any Python consumer needing `after`/DemandQueueEntry must raise a demand rather than regenerate blindly.
- Standing: TODO -- no repo convention recorded yet (seeded 2026-08-02 by brain-toolkit bin/adopt v0.6.2)
- Vault-sync: none
- Session: 2026-09-14_0159_fulfill-demand-dashboard-20260914-demand

## Session 52 (2026-09-14)

Full narrative, decisions, and context trail: `.brain/sessions/2026-09-14_0231_close-the-loop-on-demand-contracts-20260.md`
(the session file is the source of truth in this D052-piloted repo -- the block
below is a **generated projection** of it, produced mechanically by
`brain session close`, not a second hand-written account).

- State: Close the loop on demand contracts-20260914-factory-repin-interface-extraction. It was approved at 2026-09-14T01:29:58.822673Z -- the only thing left is this repo's own archive bookkeeping, which nobody has done yet. 1. GET http://localhost:8082/satisfied/contracts -- find contracts-20260914-factory... -- status: done.
- Next step: See the session file's `## Log` for open follow-ups.
- Standing: TODO -- no repo convention recorded yet (seeded 2026-08-02 by brain-toolkit bin/adopt v0.6.2)
- Vault-sync: none
- Session: 2026-09-14_0231_close-the-loop-on-demand-contracts-20260

## Session 53 (2026-09-14)

Full narrative, decisions, and context trail: `.brain/sessions/2026-09-14_0330_close-the-loop-on-demand-contracts-20260.md`
(the session file is the source of truth in this D052-piloted repo -- the block
below is a **generated projection** of it, produced mechanically by
`brain session close`, not a second hand-written account).

- State: Close the loop on demand contracts-20260914-dashboard-repin-dispatch-order. It was approved at 2026-09-14T02:30:30.614675Z -- the only thing left is this repo's own archive bookkeeping, which nobody has done yet. 1. GET http://localhost:8082/satisfied/contracts -- find contracts-20260914-dashboard-r... -- status: done.
- Next step: See the session file's `## Log` for open follow-ups.
- Standing: TODO -- no repo convention recorded yet (seeded 2026-08-02 by brain-toolkit bin/adopt v0.6.2)
- Vault-sync: none
- Session: 2026-09-14_0330_close-the-loop-on-demand-contracts-20260

## Session 54 (2026-09-14)

Full narrative, decisions, and context trail: `.brain/sessions/2026-09-14_1559_test-pin-no-model.md`
(the session file is the source of truth in this D052-piloted repo -- the block
below is a **generated projection** of it, produced mechanically by
`brain session close`, not a second hand-written account).

- State: test-pin-no-model -- status: done.
- Next step: See the session file's `## Log` for open follow-ups.
- Standing: TODO -- no repo convention recorded yet (seeded 2026-08-02 by brain-toolkit bin/adopt v0.6.2)
- Vault-sync: none
- Session: 2026-09-14_1559_test-pin-no-model

## Session 55 (2026-09-14)

Full narrative, decisions, and context trail: `.brain/sessions/2026-09-14_1559_fulfill-demand-brain-toolkit-20260914-fl.md`
(the session file is the source of truth in this D052-piloted repo -- the block
below is a **generated projection** of it, produced mechanically by
agent-runner's dispatch supervisor from an auto-drafted, unconfirmed close --
not a second hand-written account, and not yet reviewed by a human or the
worker agent itself).

- State: Fulfill demand brain-toolkit-20260914-fleet-repin-v063 (capability: Every .brain repo moves its .brain/toolkit-pin to v0.6.3 — the fleet re-pin sweep for the session-model-field fix. The whole fleet is currently on v0.6.2; v0.6.3 fixes brain session open recording a false model: claude-code on every... -- status: done (close: auto-drafted, unconfirmed).
- Next step: Review this session's auto-drafted close (`.brain/sessions/2026-09-14_1559_fulfill-demand-brain-toolkit-20260914-fl.md`) and confirm or correct it.
- Standing: TODO -- no repo convention recorded yet (seeded 2026-08-02 by brain-toolkit bin/adopt v0.6.2)
- Vault-sync: none
- Session: 2026-09-14_1559_fulfill-demand-brain-toolkit-20260914-fl

## Session 56 (2026-09-19)

Full narrative, decisions, and context trail: `.brain/sessions/2026-09-19_0251_fulfill-demand-ai-gateway-20260917-contr.md`
(the session file is the source of truth in this D052-piloted repo -- the block
below is a **generated projection** of it, produced mechanically by
`brain session close`, not a second hand-written account).

- State: Fulfill demand ai-gateway-20260917-contracts-research-evidence-envelope (capability: An additive async job envelope for evidence-gathering (URL-retrieval) requests, distinct from ai.request/ai.job's existing shapes, from: ai-gateway, target: contracts). Acceptance criteria: - A caller-generated dura... -- status: partial.
- Next step: See the session file's `## Log` for open follow-ups.
- Standing: TODO -- no repo convention recorded yet (seeded 2026-08-02 by brain-toolkit bin/adopt v0.6.2)
- Vault-sync: none
- Session: 2026-09-19_0251_fulfill-demand-ai-gateway-20260917-contr

## Session 57 (2026-09-19) -- CORRECTED, see below

**This block was wrong and is superseded by Session 58.** A `brain session
close` invocation without `--session-id` mistakenly targeted
`.brain/sessions/2026-09-14_1559_test-pin-v0-6-3.md` instead of the session
actually running (its own file already had `ended:` set from an earlier
close, so the tool fell through to the next open session file) and wrote
that session's content here under the wrong session id. The real content
belongs to `2026-09-19_0251_fulfill-demand-ai-gateway-20260917-contr` and
now appears correctly in Session 58. `.brain/sessions/2026-09-14_1559_test-pin-v0-6-3.md`
has been corrected to `status: abandoned` with an explanatory lesson entry.

- Session: 2026-09-14_1559_test-pin-v0-6-3

## Session 58 (2026-09-19)

Full narrative, decisions, and context trail: `.brain/sessions/2026-09-19_0251_fulfill-demand-ai-gateway-20260917-contr.md`
(the session file is the source of truth in this D052-piloted repo -- the block
below is a **generated projection** of it, produced mechanically by
`brain session close`, not a second hand-written account).

- State: Fulfill demand ai-gateway-20260917-contracts-research-evidence-envelope (capability: An additive async job envelope for evidence-gathering (URL-retrieval) requests, distinct from ai.request/ai.job's existing shapes, from: ai-gateway, target: contracts). Acceptance criteria: - A caller-generated dura... -- status: done.
- Next step: ai-gateway re-pins to contracts v0.27.0 and adopts ResearchJobRequest/ResearchJobStatus per the raised demand
- Standing: TODO -- no repo convention recorded yet (seeded 2026-08-02 by brain-toolkit bin/adopt v0.6.2)
- Vault-sync: none
- Session: 2026-09-19_0251_fulfill-demand-ai-gateway-20260917-contr

## Session 59 (2026-09-19)

Full narrative, decisions, and context trail: `.brain/sessions/2026-09-19_1324_archive-approved-demand-contracts-202609.md`
(the session file is the source of truth in this D052-piloted repo -- the block
below is a **generated projection** of it, produced mechanically by
`brain session close`, not a second hand-written account).

- State: Archive approved demand contracts-20260919-ai-gateway-repin-research-evidence-envelope -- status: done.
- Next step: None -- the approved origin demand loop is closed.
- Standing: TODO -- no repo convention recorded yet (seeded 2026-08-02 by brain-toolkit bin/adopt v0.6.2)
- Vault-sync: none
- Session: 2026-09-19_1324_archive-approved-demand-contracts-202609

## Session 60 (2026-09-26)

Full narrative, decisions, and context trail: `.brain/sessions/2026-09-26_0831_fulfill-demand-youtrack-20260926-contrac.md`
(the session file is the source of truth in this D052-piloted repo -- the block
below is a **generated projection** of it, produced mechanically by
`brain session close`, not a second hand-written account).

- State: fulfill demand youtrack-20260926-contracts-planner-plan-run-note -- status: done.
- Next step: await coordinator verdict on youtrack-20260926-contracts-planner-plan-run-note; fix validate_demand.py archived-path reference
- Standing: TODO -- no repo convention recorded yet (seeded 2026-08-02 by brain-toolkit bin/adopt v0.6.2)
- Vault-sync: none needed
- Session: 2026-09-26_0831_fulfill-demand-youtrack-20260926-contrac

## Session 61 (2026-09-26)

Full narrative, decisions, and context trail: `.brain/sessions/2026-09-26_0834_fix-tests-validate-demand-py-archived-de.md`
(the session file is the source of truth in this D052-piloted repo -- the block
below is a **generated projection** of it, produced mechanically by
`brain session close`, not a second hand-written account).

- State: fix tests/validate_demand.py archived demand path -- status: done.
- Next step: await coordinator verdict on youtrack-20260926-contracts-planner-plan-run-note
- Standing: TODO -- no repo convention recorded yet (seeded 2026-08-02 by brain-toolkit bin/adopt v0.6.2)
- Vault-sync: none needed
- Session: 2026-09-26_0834_fix-tests-validate-demand-py-archived-de

## Session 62 (2026-09-26)

Full narrative, decisions, and context trail: `.brain/sessions/2026-09-26_0845_add-v0-29-0-pinned-worktree-document-wor.md`
(the session file is the source of truth in this D052-piloted repo -- the block
below is a **generated projection** of it, produced mechanically by
`brain session close`, not a second hand-written account).

- State: add v0.29.0 pinned worktree; document worktree step in release checklist -- status: done.
- Next step: await coordinator verdict on youtrack-20260926-contracts-planner-plan-run-note
- Standing: TODO -- no repo convention recorded yet (seeded 2026-08-02 by brain-toolkit bin/adopt v0.6.2)
- Vault-sync: none needed
- Session: 2026-09-26_0845_add-v0-29-0-pinned-worktree-document-wor

## Session 63 (2026-09-26)

Full narrative, decisions, and context trail: `.brain/sessions/2026-09-26_0957_close-the-loop-on-demand-contracts-20260.md`
(the session file is the source of truth in this D052-piloted repo -- the block
below is a **generated projection** of it, produced mechanically by
agent-runner's dispatch supervisor from an auto-drafted, unconfirmed close --
not a second hand-written account, and not yet reviewed by a human or the
worker agent itself).

- State: Close the loop on demand contracts-20260926-youtrack-repin-planner-plan-run-note. It was approved at 2026-09-26T08:41:02.864164Z -- the only thing left is this repo's own archive bookkeeping, which nobody has done yet. 1. GET http://localhost:8082/satisfied/contracts -- find contracts-20260926-youtr... -- status: done (close: auto-drafted, unconfirmed).
- Next step: Review this session's auto-drafted close (`.brain/sessions/2026-09-26_0957_close-the-loop-on-demand-contracts-20260.md`) and confirm or correct it.
- Standing: TODO -- no repo convention recorded yet (seeded 2026-08-02 by brain-toolkit bin/adopt v0.6.2)
- Vault-sync: none
- Session: 2026-09-26_0957_close-the-loop-on-demand-contracts-20260

## Session 64 (2026-09-27)

Full narrative, decisions, and context trail: `.brain/sessions/2026-09-27_0431_fulfill-demand-plantpal-20260927-contrac.md`
(the session file is the source of truth in this D052-piloted repo -- the block
below is a **generated projection** of it, produced mechanically by
`brain session close`, not a second hand-written account).

- State: Fulfill demand plantpal-20260927-contracts-ci-run-steps: optional jobId + steps[] on ci.run CiRunPayload -- status: done.
- Next step: Await coordinator validation of plantpal-20260927-contracts-ci-run-steps; the older 2026-09-27_0531 supervised session file is still open (no changes) and can be marked abandoned by the supervisor.
- Standing: TODO -- no repo convention recorded yet (seeded 2026-08-02 by brain-toolkit bin/adopt v0.6.2)
- Vault-sync: none
- Session: 2026-09-27_0431_fulfill-demand-plantpal-20260927-contrac

## Session 65 (2026-09-27)

Full narrative, decisions, and context trail: `.brain/sessions/2026-09-27_0531_fulfill-demand-plantpal-20260927-contrac.md`
(the session file is the source of truth in this D052-piloted repo -- the block
below is a **generated projection** of it, produced mechanically by
agent-runner's dispatch supervisor from an auto-drafted, unconfirmed close --
not a second hand-written account, and not yet reviewed by a human or the
worker agent itself).

- State: Fulfill demand plantpal-20260927-contracts-ci-run-steps (capability: An additive, optional `steps[]` (plus `jobId`) on the `ci.run` state.event's CiRunPayload, so a CI job's per-step progress can travel to the dashboard as a Jenkins-style stage view., from: plantpal, target: contracts). Before worki... -- status: done (close: auto-drafted, unconfirmed).
- Next step: Review this session's auto-drafted close (`.brain/sessions/2026-09-27_0531_fulfill-demand-plantpal-20260927-contrac.md`) and confirm or correct it.
- Standing: TODO -- no repo convention recorded yet (seeded 2026-08-02 by brain-toolkit bin/adopt v0.6.2)
- Vault-sync: none
- Session: 2026-09-27_0531_fulfill-demand-plantpal-20260927-contrac

## Session 66 (2026-09-27)

Full narrative, decisions, and context trail: `.brain/sessions/2026-09-27_0508_close-the-loop-on-demand-contracts-20260.md`
(the session file is the source of truth in this D052-piloted repo -- the block
below is a **generated projection** of it, produced mechanically by
`brain session close`, not a second hand-written account).

- State: Close the loop on demand contracts-20260927-plantpal-repin-ci-run-steps (archive) -- status: done.
- Next step: No contracts-side follow-up. plantpal's report did not explicitly address acceptance criterion 3 (state-feed/dashboard re-pin before ci-runner emits); ci-runner's own fulfillment shows a CI_RUN_STEPS flag defaulting false until state-feed re-pins, so the chain carries it.
- Standing: TODO -- no repo convention recorded yet (seeded 2026-08-02 by brain-toolkit bin/adopt v0.6.2)
- Vault-sync: none needed
- Session: 2026-09-27_0508_close-the-loop-on-demand-contracts-20260

## Session 67 (2026-09-27)

Full narrative, decisions, and context trail: `.brain/sessions/2026-09-27_0607_close-the-loop-on-demand-contracts-20260.md`
(the session file is the source of truth in this D052-piloted repo -- the block
below is a **generated projection** of it, produced mechanically by
agent-runner's dispatch supervisor from an auto-drafted, unconfirmed close --
not a second hand-written account, and not yet reviewed by a human or the
worker agent itself).

- State: Close the loop on demand contracts-20260927-plantpal-repin-ci-run-steps. It was approved at 2026-09-27T05:06:44.465795Z -- the only thing left is this repo's own archive bookkeeping, which nobody has done yet. 1. GET http://localhost:8082/satisfied/contracts -- find contracts-20260927-plantpal-repin... -- status: done (close: auto-drafted, unconfirmed).
- Next step: Review this session's auto-drafted close (`.brain/sessions/2026-09-27_0607_close-the-loop-on-demand-contracts-20260.md`) and confirm or correct it.
- Standing: TODO -- no repo convention recorded yet (seeded 2026-08-02 by brain-toolkit bin/adopt v0.6.2)
- Vault-sync: none
- Session: 2026-09-27_0607_close-the-loop-on-demand-contracts-20260

## Session 68 (2026-09-27)

Full narrative, decisions, and context trail: `.brain/sessions/2026-09-27_0808_fulfill-demand-factory-20260927-task-del.md`
(the session file is the source of truth in this D052-piloted repo -- the block
below is a **generated projection** of it, produced mechanically by
agent-runner's dispatch supervisor from an auto-drafted, unconfirmed close --
not a second hand-written account, and not yet reviewed by a human or the
worker agent itself).

- State: Fulfill demand factory-20260927-task-delivery-contracts (capability: Publish D113 task delivery interfaces and recoverable operation semantics with tagged bindings, from: factory, target: contracts). Acceptance criteria: - Publish versioned YouTrack delivery interfaces for paginated issue reads, sta... -- status: done (close: auto-drafted, unconfirmed).
- Next step: Review this session's auto-drafted close (`.brain/sessions/2026-09-27_0808_fulfill-demand-factory-20260927-task-del.md`) and confirm or correct it.
- Standing: TODO -- no repo convention recorded yet (seeded 2026-08-02 by brain-toolkit bin/adopt v0.6.2)
- Vault-sync: none
- Session: 2026-09-27_0808_fulfill-demand-factory-20260927-task-del

## Session 69 (2026-09-27)

Full narrative, decisions, and context trail: `.brain/sessions/2026-09-27_1035_fulfill-demand-factory-20260927-demand-a.md`
(the session file is the source of truth in this D052-piloted repo -- the block
below is a **generated projection** of it, produced mechanically by
`brain session close`, not a second hand-written account).

- State: Fulfill demand factory-20260927-demand-after-binding (capability: Restore Python Demand support for the published after dependency field, from: factory, target: contracts). Acceptance criteria: - Publish a new tagged Python Demand binding that accepts and preserves the after field already present in... -- status: done.
- Next step: factory closes consuming leg (re-pin v0.32.0); optional: Python binding for demand.queue-entry if someone demands it
- Standing: TODO -- no repo convention recorded yet (seeded 2026-08-02 by brain-toolkit bin/adopt v0.6.2)
- Vault-sync: none
- Session: 2026-09-27_1035_fulfill-demand-factory-20260927-demand-a

## Session 70 (2026-09-27)

Full narrative, decisions, and context trail: `.brain/sessions/2026-09-27_1130_fulfill-demand-ci-runner-20260927-contra.md`
(the session file is the source of truth in this D052-piloted repo -- the block
below is a **generated projection** of it, produced mechanically by
agent-runner's dispatch supervisor from an auto-drafted, unconfirmed close --
not a second hand-written account, and not yet reviewed by a human or the
worker agent itself).

- State: Fulfill demand ci-runner-20260927-contracts-ci-headsha-lookup (capability: contracts publishes headSha on CiRunPayload and BuildResult, and a ci-runner CI-result lookup interface (by run/job id and by repository+revision) returning delivery.producer-result, in a tagged release with TS bindings., fro... -- status: failed (close: auto-drafted, unconfirmed).
- Next step: Review this session's auto-drafted close (`.brain/sessions/2026-09-27_1130_fulfill-demand-ci-runner-20260927-contra.md`) and confirm or correct it.
- Standing: TODO -- no repo convention recorded yet (seeded 2026-08-02 by brain-toolkit bin/adopt v0.6.2)
- Vault-sync: none
- Session: 2026-09-27_1130_fulfill-demand-ci-runner-20260927-contra

## Session 71 (2026-09-27)

Full narrative, decisions, and context trail: `.brain/sessions/2026-09-27_1039_fulfill-demand-agent-runner-20260927-con.md`
(the session file is the source of truth in this D052-piloted repo -- the block
below is a **generated projection** of it, produced mechanically by
`brain session close`, not a second hand-written account).

- State: Fulfill demand agent-runner-20260927-contracts-runner-keyed-dispatch (keyed dispatch, dispatch-key lookup, observed workspace identity, producer-result routes) -- status: done.
- Next step: Owner validates the v0.33.0 fulfillment; agent-runner repins to ../contracts-worktrees/v0.33.0/gen/ts and implements reserve/replay/conflict/lookup per docs/task-delivery.md section Runner routes. Note: the working tree still carries UNCOMMITTED changes from the failed ci-runner session (schemas/ci-runner/build-result.yaml, schemas/delivery/delivery.error.json, schemas/state-feed/*, tests/validate_delivery.py, tests/validate_state_event.py, schemas/delivery-api/ci-runner-results.openapi.yaml) -- left untouched, and tests/run_all.py passes with them in place.
- Standing: TODO -- no repo convention recorded yet (seeded 2026-08-02 by brain-toolkit bin/adopt v0.6.2)
- Vault-sync: none
- Session: 2026-09-27_1039_fulfill-demand-agent-runner-20260927-con

## Session 72 (2026-09-27)

Full narrative, decisions, and context trail: `.brain/sessions/2026-09-27_1136_fulfill-demand-agent-runner-20260927-con.md`
(the session file is the source of truth in this D052-piloted repo -- the block
below is a **generated projection** of it, produced mechanically by
agent-runner's dispatch supervisor from an auto-drafted, unconfirmed close --
not a second hand-written account, and not yet reviewed by a human or the
worker agent itself).

- State: Fulfill demand agent-runner-20260927-contracts-runner-keyed-dispatch (capability: An additive, tagged contracts release that publishes agent-runner's keyed-dispatch request field, dispatch-key lookup, observed workspace identity on the run record, and the producer-result lookup routes, from: agent-r... -- status: done (close: auto-drafted, unconfirmed).
- Next step: Review this session's auto-drafted close (`.brain/sessions/2026-09-27_1136_fulfill-demand-agent-runner-20260927-con.md`) and confirm or correct it.
- Standing: TODO -- no repo convention recorded yet (seeded 2026-08-02 by brain-toolkit bin/adopt v0.6.2)
- Vault-sync: none
- Session: 2026-09-27_1136_fulfill-demand-agent-runner-20260927-con

## Session 73 (2026-09-27)

Full narrative, decisions, and context trail: `.brain/sessions/2026-09-27_1050_fulfill-demand-ci-runner-20260927-contra.md`
(the session file is the source of truth in this D052-piloted repo -- the block
below is a **generated projection** of it, produced mechanically by
`brain session close`, not a second hand-written account).

- State: Fulfill demand ci-runner-20260927-contracts-ci-headsha-lookup (headSha on ci.run/BuildResult + ci-runner result lookup interface, release v0.34.0) -- status: done.
- Next step: See the session file's `## Log` for open follow-ups.
- Standing: TODO -- no repo convention recorded yet (seeded 2026-08-02 by brain-toolkit bin/adopt v0.6.2)
- Vault-sync: none
- Session: 2026-09-27_1050_fulfill-demand-ci-runner-20260927-contra

## Session 74 (2026-09-27)

Full narrative, decisions, and context trail: `.brain/sessions/2026-09-27_1150_fulfill-demand-ci-runner-20260927-contra.md`
(the session file is the source of truth in this D052-piloted repo -- the block
below is a **generated projection** of it, produced mechanically by
agent-runner's dispatch supervisor from an auto-drafted, unconfirmed close --
not a second hand-written account, and not yet reviewed by a human or the
worker agent itself).

- State: Fulfill demand ci-runner-20260927-contracts-ci-headsha-lookup (capability: contracts publishes headSha on CiRunPayload and BuildResult, and a ci-runner CI-result lookup interface (by run/job id and by repository+revision) returning delivery.producer-result, in a tagged release with TS bindings., fro... -- status: done (close: auto-drafted, unconfirmed).
- Next step: Review this session's auto-drafted close (`.brain/sessions/2026-09-27_1150_fulfill-demand-ci-runner-20260927-contra.md`) and confirm or correct it.
- Standing: TODO -- no repo convention recorded yet (seeded 2026-08-02 by brain-toolkit bin/adopt v0.6.2)
- Vault-sync: none
- Session: 2026-09-27_1150_fulfill-demand-ci-runner-20260927-contra

## Session 75 (2026-09-27)

Full narrative, decisions, and context trail: `.brain/sessions/2026-09-27_1108_fulfill-demand-factory-20260927-sync-rec.md`
(the session file is the source of truth in this D052-piloted repo -- the block
below is a **generated projection** of it, produced mechanically by
`brain session close`, not a second hand-written account).

- State: Fulfill demand factory-20260927-sync-recovery-retention (operation retention coverage + safe missing-operation recovery) -- status: done.
- Next step: Session closed status done. Open follow-ups in the report: (1) owner decision on bundling schemas/ into the Python wheel -- filed, not fixed; (2) repo-wide decision on the inert format: date-time checker; (3) the D043 origin demand to factory is open and the youtrack producer obligations land when that service implements the operation store. Also noted at session start: a NEW plantpal demand (plantpal-20260927-contracts-app-deploy-receipt-and-identity) is in /inbox/contracts and was NOT worked this session.
- Standing: TODO -- no repo convention recorded yet (seeded 2026-08-02 by brain-toolkit bin/adopt v0.6.2)
- Vault-sync: none
- Session: 2026-09-27_1108_fulfill-demand-factory-20260927-sync-rec

## Session 76 (2026-09-27)

Full narrative, decisions, and context trail: `.brain/sessions/2026-09-27_1207_fulfill-demand-factory-20260927-sync-rec.md`
(the session file is the source of truth in this D052-piloted repo -- the block
below is a **generated projection** of it, produced mechanically by
agent-runner's dispatch supervisor from an auto-drafted, unconfirmed close --
not a second hand-written account, and not yet reviewed by a human or the
worker agent itself).

- State: Fulfill demand factory-20260927-sync-recovery-retention (capability: Clarify task delivery operation retention and safe missing-operation recovery, from: factory, target: contracts). Acceptance criteria: - Publish a tagged clarification or additive interface distinguishing a never-seen operation fro... -- status: done (close: auto-drafted, unconfirmed).
- Next step: Review this session's auto-drafted close (`.brain/sessions/2026-09-27_1207_fulfill-demand-factory-20260927-sync-rec.md`) and confirm or correct it.
- Standing: TODO -- no repo convention recorded yet (seeded 2026-08-02 by brain-toolkit bin/adopt v0.6.2)
- Vault-sync: none
- Session: 2026-09-27_1207_fulfill-demand-factory-20260927-sync-rec

## Session 77 (2026-09-27)

Full narrative, decisions, and context trail: `.brain/sessions/2026-09-27_2257_close-loop-on-4-satisfied-contracts-dema.md`
(the session file is the source of truth in this D052-piloted repo -- the block
below is a **generated projection** of it, produced mechanically by
`brain session close`, not a second hand-written account).

- State: close loop on 4 satisfied contracts demands -- status: done.
- Next step: fulfill inbox demand plantpal-20260927-contracts-app-deploy-receipt-and-identity; archive factory-repin-sync-recovery-retention once satisfied
- Standing: TODO -- no repo convention recorded yet (seeded 2026-08-02 by brain-toolkit bin/adopt v0.6.2)
- Vault-sync: none
- Session: 2026-09-27_2257_close-loop-on-4-satisfied-contracts-dema

## Session 78 (2026-09-27)

Full narrative, decisions, and context trail: `.brain/sessions/2026-09-28_0000_fulfill-demand-plantpal-20260927-contrac.md`
(the session file is the source of truth in this D052-piloted repo -- the block
below is a **generated projection** of it, produced mechanically by
`brain session close`, not a second hand-written account).

- State: Fulfill demand plantpal-20260927-contracts-app-deploy-receipt-and-identity (capability: Tagged shapes for the app-deploy producer: a dev deployment receipt (with rollback identity), its lookup, and a running-app identity/revision record, so Factory and runtime never consume plantpal's native JSON, f... -- status: done.
- Next step: plantpal closes its leg (contracts-20260928-plantpal-repin-app-deploy-receipt-and-identity); archive the origin demand once satisfied
- Standing: TODO -- no repo convention recorded yet (seeded 2026-08-02 by brain-toolkit bin/adopt v0.6.2)
- Vault-sync: none
- Session: 2026-09-28_0000_fulfill-demand-plantpal-20260927-contrac

## Session 79 (2026-09-28)

Full narrative, decisions, and context trail: `.brain/sessions/2026-09-28_0219_close-the-loop-on-demand-contracts-20260.md`
(the session file is the source of truth in this D052-piloted repo -- the block
below is a **generated projection** of it, produced mechanically by
`brain session close`, not a second hand-written account).

- State: Close the loop on demand contracts-20260927-factory-repin-sync-recovery-retention. It was approved at 2026-09-28T00:08:19.768157Z -- the only thing left is this repo's own archive bookkeeping, which nobody has done yet. 1. GET http://localhost:8082/satisfied/contracts -- find contracts-20260927-fact... -- status: done.
- Next step: Await plantpal's consuming-leg fulfillment of contracts-20260928-plantpal-repin-app-deploy-receipt-and-identity, then archive it; no other contracts-origin demand is outstanding.
- Standing: TODO -- no repo convention recorded yet (seeded 2026-08-02 by brain-toolkit bin/adopt v0.6.2)
- Vault-sync: none
- Session: 2026-09-28_0219_close-the-loop-on-demand-contracts-20260

## Session 80 (2026-09-28)

Full narrative, decisions, and context trail: `.brain/sessions/2026-09-28_0357_close-the-loop-on-demand-contracts-20260.md`
(the session file is the source of truth in this D052-piloted repo -- the block
below is a **generated projection** of it, produced mechanically by
`brain session close`, not a second hand-written account).

- State: Close the loop on demand contracts-20260928-plantpal-repin-app-deploy-receipt-and-identity. It was approved at 2026-09-28T02:56:08.755198Z -- the only thing left is this repo's own archive bookkeeping, which nobody has done yet. 1. GET http://localhost:8082/satisfied/contracts -- find contracts-2026... -- status: done.
- Next step: See the session file's `## Log` for open follow-ups.
- Standing: TODO -- no repo convention recorded yet (seeded 2026-08-02 by brain-toolkit bin/adopt v0.6.2)
- Vault-sync: none
- Session: 2026-09-28_0357_close-the-loop-on-demand-contracts-20260

## Session 81 (2026-09-28)

Full narrative, decisions, and context trail: `.brain/sessions/2026-09-28_0349_fulfill-demand-plantpal-20260928-contrac.md`
(the session file is the source of truth in this D052-piloted repo -- the block
below is a **generated projection** of it, produced mechanically by
`brain session close`, not a second hand-written account).

- State: fulfill demand plantpal-20260928-contracts-app-deploy-lookup-route -- status: done.
- Next step: Nothing owed by contracts. plantpal has two open legs: the v0.36.0 receipt repin and implementing the v0.37.0 route (host/port/credential are theirs). Watch for a gap raised back.
- Standing: TODO -- no repo convention recorded yet (seeded 2026-08-02 by brain-toolkit bin/adopt v0.6.2)
- Vault-sync: none
- Session: 2026-09-28_0349_fulfill-demand-plantpal-20260928-contrac

## Session 82 (2026-09-28)

Full narrative, decisions, and context trail: `.brain/sessions/2026-09-28_0448_fulfill-demand-plantpal-20260928-contrac.md`
(the session file is the source of truth in this D052-piloted repo -- the block
below is a **generated projection** of it, produced mechanically by
agent-runner's dispatch supervisor from an auto-drafted, unconfirmed close --
not a second hand-written account, and not yet reviewed by a human or the
worker agent itself).

- State: Fulfill demand plantpal-20260928-contracts-app-deploy-lookup-route (capability: A published route interface for the app-deploy lookup, so Factory can re-fetch delivery.deployment-receipt from where it runs instead of executing a process inside the plantpal checkout on the deploying host, from: plant... -- status: done (close: auto-drafted, unconfirmed).
- Next step: Review this session's auto-drafted close (`.brain/sessions/2026-09-28_0448_fulfill-demand-plantpal-20260928-contrac.md`) and confirm or correct it.
- Standing: TODO -- no repo convention recorded yet (seeded 2026-08-02 by brain-toolkit bin/adopt v0.6.2)
- Vault-sync: none
- Session: 2026-09-28_0448_fulfill-demand-plantpal-20260928-contrac

## Session 83 (2026-09-28)

Full narrative, decisions, and context trail: `.brain/sessions/2026-09-28_0436_close-the-loop-on-demand-contracts-20260.md`
(the session file is the source of truth in this D052-piloted repo -- the block
below is a **generated projection** of it, produced mechanically by
`brain session close`, not a second hand-written account).

- State: Close the loop on demand contracts-20260928-plantpal-implement-app-deploy-lookup-route (approved 2026-09-28T04:13:17Z): archive the origin's own demand file (git mv + status flip) and push -- status: done.
- Next step: See the session file's `## Log` for open follow-ups.
- Standing: TODO -- no repo convention recorded yet (seeded 2026-08-02 by brain-toolkit bin/adopt v0.6.2)
- Vault-sync: none
- Session: 2026-09-28_0436_close-the-loop-on-demand-contracts-20260

## Session 84 (2026-09-28)

Full narrative, decisions, and context trail: `.brain/sessions/2026-09-28_0535_close-the-loop-on-demand-contracts-20260.md`
(the session file is the source of truth in this D052-piloted repo -- the block
below is a **generated projection** of it, produced mechanically by
agent-runner's dispatch supervisor from an auto-drafted, unconfirmed close --
not a second hand-written account, and not yet reviewed by a human or the
worker agent itself).

- State: Close the loop on demand contracts-20260928-plantpal-implement-app-deploy-lookup-route. It was approved at 2026-09-28T04:13:17.791411Z -- the only thing left is this repo's own archive bookkeeping, which nobody has done yet. 1. GET http://localhost:8082/satisfied/contracts -- find contracts-20260928... -- status: done (close: auto-drafted, unconfirmed).
- Next step: Review this session's auto-drafted close (`.brain/sessions/2026-09-28_0535_close-the-loop-on-demand-contracts-20260.md`) and confirm or correct it.
- Standing: TODO -- no repo convention recorded yet (seeded 2026-08-02 by brain-toolkit bin/adopt v0.6.2)
- Vault-sync: none
- Session: 2026-09-28_0535_close-the-loop-on-demand-contracts-20260

## Session 85 (2026-09-30)

Full narrative, decisions, and context trail: `.brain/sessions/2026-09-30_1547_fulfill-demand-factory-20260930-contract.md`
(the session file is the source of truth in this D052-piloted repo -- the block
below is a **generated projection** of it, produced mechanically by
`brain session close`, not a second hand-written account).

- State: Fulfill demand factory-20260930-contracts-review-deployment (capability: Publish the shapes for a review environment that runs an unmerged PR revision, so launcher, apps and Factory can prove which revision a review URL serves, from: factory, target: contracts). Acceptance criteria: - A tagged relea... -- status: done.
- Next step: factory re-pins v0.38.0 and records review evidence; launcher implements the port
- Standing: TODO -- no repo convention recorded yet (seeded 2026-08-02 by brain-toolkit bin/adopt v0.6.2)
- Vault-sync: none: launcher port registration would need a platform-vault demand
- Session: 2026-09-30_1547_fulfill-demand-factory-20260930-contract

## Session 86 (2026-09-30)

Full narrative, decisions, and context trail: `.brain/sessions/2026-09-30_1644_close-the-loop-on-demand-contracts-20260.md`
(the session file is the source of truth in this D052-piloted repo -- the block
below is a **generated projection** of it, produced mechanically by
agent-runner's dispatch supervisor from an auto-drafted, unconfirmed close --
not a second hand-written account, and not yet reviewed by a human or the
worker agent itself).

- State: Close the loop on demand contracts-20260930-factory-repin-review-deployment. It was approved at 2026-09-30T15:20:51.801664Z -- the only thing left is this repo's own archive bookkeeping, which nobody has done yet. 1. GET http://localhost:8082/satisfied/contracts -- find contracts-20260930-factory-re... -- status: done (close: auto-drafted, unconfirmed).
- Next step: Review this session's auto-drafted close (`.brain/sessions/2026-09-30_1644_close-the-loop-on-demand-contracts-20260.md`) and confirm or correct it.
- Standing: TODO -- no repo convention recorded yet (seeded 2026-08-02 by brain-toolkit bin/adopt v0.6.2)
- Vault-sync: none
- Session: 2026-09-30_1644_close-the-loop-on-demand-contracts-20260

## Session 87 (2026-09-30)

Full narrative, decisions, and context trail: `.brain/sessions/2026-09-30_2143_fulfill-demand-platform-vault-20260930-c.md`
(the session file is the source of truth in this D052-piloted repo -- the block
below is a **generated projection** of it, produced mechanically by
agent-runner's dispatch supervisor from an auto-drafted, unconfirmed close --
not a second hand-written account, and not yet reviewed by a human or the
worker agent itself).

- State: Fulfill demand platform-vault-20260930-contracts-d115-parked-work (capability: tagged shapes for D115: parked run result, wait condition (incl. ALL-of/ANY-of over demands), condition event, resume request, from: platform-vault, target: contracts). Acceptance criteria: - a tagged release publishes th... -- status: done (close: auto-drafted, unconfirmed).
- Next step: Review this session's auto-drafted close (`.brain/sessions/2026-09-30_2143_fulfill-demand-platform-vault-20260930-c.md`) and confirm or correct it.
- Standing: TODO -- no repo convention recorded yet (seeded 2026-08-02 by brain-toolkit bin/adopt v0.6.2)
- Vault-sync: none
- Session: 2026-09-30_2143_fulfill-demand-platform-vault-20260930-c

## Session 88 (2026-09-30)

Full narrative, decisions, and context trail: `.brain/sessions/2026-09-30_2215_close-the-loop-on-demand-contracts-20260.md`
(the session file is the source of truth in this D052-piloted repo -- the block
below is a **generated projection** of it, produced mechanically by
agent-runner's dispatch supervisor from an auto-drafted, unconfirmed close --
not a second hand-written account, and not yet reviewed by a human or the
worker agent itself).

- State: Close the loop on demand contracts-20260930-platform-vault-repin-d115-parked-work. It was approved at 2026-09-30T21:15:11.172728Z -- the only thing left is this repo's own archive bookkeeping, which nobody has done yet. 1. GET http://localhost:8082/satisfied/contracts -- find contracts-20260930-plat... -- status: done (close: auto-drafted, unconfirmed).
- Next step: Review this session's auto-drafted close (`.brain/sessions/2026-09-30_2215_close-the-loop-on-demand-contracts-20260.md`) and confirm or correct it.
- Standing: TODO -- no repo convention recorded yet (seeded 2026-08-02 by brain-toolkit bin/adopt v0.6.2)
- Vault-sync: none
- Session: 2026-09-30_2215_close-the-loop-on-demand-contracts-20260

## Session 89 (2026-09-30)

Full narrative, decisions, and context trail: `.brain/sessions/2026-09-30_2148_fulfill-demand-platform-vault-20260930-c.md`
(the session file is the source of truth in this D052-piloted repo -- the block
below is a **generated projection** of it, produced mechanically by
`brain session close`, not a second hand-written account).

- State: fulfill demand platform-vault-20260930-contracts-d115-java-bindings -- status: done.
- Next step: See the session file's `## Log` for open follow-ups.
- Standing: TODO -- no repo convention recorded yet (seeded 2026-08-02 by brain-toolkit bin/adopt v0.6.2)
- Vault-sync: none
- Session: 2026-09-30_2148_fulfill-demand-platform-vault-20260930-c

## Session 90 (2026-09-30)

Full narrative, decisions, and context trail: `.brain/sessions/2026-09-30_2248_fulfill-demand-platform-vault-20260930-c.md`
(the session file is the source of truth in this D052-piloted repo -- the block
below is a **generated projection** of it, produced mechanically by
agent-runner's dispatch supervisor from an auto-drafted, unconfirmed close --
not a second hand-written account, and not yet reviewed by a human or the
worker agent itself).

- State: Fulfill demand platform-vault-20260930-contracts-d115-java-bindings (capability: the D115 parked.* shapes (wait-condition, run-result, condition-event, resume-request) are generated into the Java bindings and released under a new tag, from: platform-vault, target: contracts). Acceptance criteria: - ... -- status: done (close: auto-drafted, unconfirmed).
- Next step: Review this session's auto-drafted close (`.brain/sessions/2026-09-30_2248_fulfill-demand-platform-vault-20260930-c.md`) and confirm or correct it.
- Standing: TODO -- no repo convention recorded yet (seeded 2026-08-02 by brain-toolkit bin/adopt v0.6.2)
- Vault-sync: none
- Session: 2026-09-30_2248_fulfill-demand-platform-vault-20260930-c

## Session 91 (2026-09-30)

Full narrative, decisions, and context trail: `.brain/sessions/2026-09-30_2252_close-the-loop-on-demand-contracts-20260.md`
(the session file is the source of truth in this D052-piloted repo -- the block
below is a **generated projection** of it, produced mechanically by
agent-runner's dispatch supervisor from an auto-drafted, unconfirmed close --
not a second hand-written account, and not yet reviewed by a human or the
worker agent itself).

- State: Close the loop on demand contracts-20260930-platform-vault-repin-d115-java-bindings. It was approved at 2026-09-30T21:51:49.274832Z -- the only thing left is this repo's own archive bookkeeping, which nobody has done yet. 1. GET http://localhost:8082/satisfied/contracts -- find contracts-20260930-pl... -- status: done (close: auto-drafted, unconfirmed).
- Next step: Review this session's auto-drafted close (`.brain/sessions/2026-09-30_2252_close-the-loop-on-demand-contracts-20260.md`) and confirm or correct it.
- Standing: TODO -- no repo convention recorded yet (seeded 2026-08-02 by brain-toolkit bin/adopt v0.6.2)
- Vault-sync: none
- Session: 2026-09-30_2252_close-the-loop-on-demand-contracts-20260

## Session 92 (2026-09-30)

Full narrative, decisions, and context trail: `.brain/sessions/2026-09-30_2321_fulfill-demand-platform-vault-20260930-c.md`
(the session file is the source of truth in this D052-piloted repo -- the block
below is a **generated projection** of it, produced mechanically by
agent-runner's dispatch supervisor from an auto-drafted, unconfirmed close --
not a second hand-written account, and not yet reviewed by a human or the
worker agent itself).

- State: Fulfill demand platform-vault-20260930-contracts-d115-command-port (capability: tagged shapes for the D115 command-execution port: command request, result, errors, from: platform-vault, target: contracts). Acceptance criteria: - a command request shape keyed like runner.dispatch-reservation so a ret... -- status: failed (close: auto-drafted, unconfirmed).
- Next step: Review this session's auto-drafted close (`.brain/sessions/2026-09-30_2321_fulfill-demand-platform-vault-20260930-c.md`) and confirm or correct it.
- Standing: TODO -- no repo convention recorded yet (seeded 2026-08-02 by brain-toolkit bin/adopt v0.6.2)
- Vault-sync: none
- Session: 2026-09-30_2321_fulfill-demand-platform-vault-20260930-c

## Session 93 (2026-10-01)

Full narrative, decisions, and context trail: `.brain/sessions/2026-10-01_0916_fulfill-demand-platform-vault-20260930-c.md`
(the session file is the source of truth in this D052-piloted repo -- the block
below is a **generated projection** of it, produced mechanically by
agent-runner's dispatch supervisor from an auto-drafted, unconfirmed close --
not a second hand-written account, and not yet reviewed by a human or the
worker agent itself).

- State: Fulfill demand platform-vault-20260930-contracts-d115-command-port (capability: tagged shapes for the D115 command-execution port: command request, result, errors, from: platform-vault, target: contracts). Acceptance criteria: - a command request shape keyed like runner.dispatch-reservation so a ret... -- status: done (close: auto-drafted, unconfirmed).
- Next step: Review this session's auto-drafted close (`.brain/sessions/2026-10-01_0916_fulfill-demand-platform-vault-20260930-c.md`) and confirm or correct it.
- Standing: TODO -- no repo convention recorded yet (seeded 2026-08-02 by brain-toolkit bin/adopt v0.6.2)
- Vault-sync: none
- Session: 2026-10-01_0916_fulfill-demand-platform-vault-20260930-c

## Session 94 (2026-10-01)

Full narrative, decisions, and context trail: `.brain/sessions/2026-10-01_0945_close-the-loop-on-demand-contracts-20261.md`
(the session file is the source of truth in this D052-piloted repo -- the block
below is a **generated projection** of it, produced mechanically by
agent-runner's dispatch supervisor from an auto-drafted, unconfirmed close --
not a second hand-written account, and not yet reviewed by a human or the
worker agent itself).

- State: Close the loop on demand contracts-20261001-platform-vault-repin-d115-command-port. It was approved at 2026-10-01T08:45:15.13057Z -- the only thing left is this repo's own archive bookkeeping, which nobody has done yet. 1. GET http://localhost:8082/satisfied/contracts -- find contracts-20261001-plat... -- status: done (close: auto-drafted, unconfirmed).
- Next step: Review this session's auto-drafted close (`.brain/sessions/2026-10-01_0945_close-the-loop-on-demand-contracts-20261.md`) and confirm or correct it.
- Standing: TODO -- no repo convention recorded yet (seeded 2026-08-02 by brain-toolkit bin/adopt v0.6.2)
- Vault-sync: none
- Session: 2026-10-01_0945_close-the-loop-on-demand-contracts-20261

## Session 95 (2026-10-02)

Full narrative, decisions, and context trail: `.brain/sessions/2026-10-02_1406_fulfill-demand-factory-20261002-contract.md`
(the session file is the source of truth in this D052-piloted repo -- the block
below is a **generated projection** of it, produced mechanically by
`brain session close`, not a second hand-written account).

- State: Fulfill demand factory-20261002-contracts-app-descriptor (capability: A contracts schema app.descriptor describes where an app's code lives, who owns it, how Factory may deliver it, and the commands the launcher runs to review and deploy it; plus an optional app summary on the control-plane registry... -- status: partial.
- Next step: See the session file's `## Log` for open follow-ups.
- Standing: TODO -- no repo convention recorded yet (seeded 2026-08-02 by brain-toolkit bin/adopt v0.6.2)
- Vault-sync: none
- Session: 2026-10-02_1406_fulfill-demand-factory-20261002-contract

## Session 96 (2026-10-02)

Full narrative, decisions, and context trail: `.brain/sessions/2026-10-02_1433_close-the-loop-on-demand-contracts-20261.md`
(the session file is the source of truth in this D052-piloted repo -- the block
below is a **generated projection** of it, produced mechanically by
agent-runner's dispatch supervisor from an auto-drafted, unconfirmed close --
not a second hand-written account, and not yet reviewed by a human or the
worker agent itself).

- State: Close the loop on demand contracts-20261002-factory-repin-app-descriptor. It was approved at 2026-10-02T13:30:45.561166Z -- the only thing left is this repo's own archive bookkeeping, which nobody has done yet. 1. GET http://localhost:8082/satisfied/contracts -- find contracts-20261002-factory-repin... -- status: done (close: auto-drafted, unconfirmed).
- Next step: Review this session's auto-drafted close (`.brain/sessions/2026-10-02_1433_close-the-loop-on-demand-contracts-20261.md`) and confirm or correct it.
- Standing: TODO -- no repo convention recorded yet (seeded 2026-08-02 by brain-toolkit bin/adopt v0.6.2)
- Vault-sync: none
- Session: 2026-10-02_1433_close-the-loop-on-demand-contracts-20261

## Session 97 (2026-10-02)

Full narrative, decisions, and context trail: `.brain/sessions/2026-10-02_1446_fulfill-demand-factory-20261002-contract.md`
(the session file is the source of truth in this D052-piloted repo -- the block
below is a **generated projection** of it, produced mechanically by
`brain session close`, not a second hand-written account).

- State: fulfill demand factory-20261002-contracts-descriptor-delivery-fields -- status: done.
- Next step: See the session file's `## Log` for open follow-ups.
- Standing: TODO -- no repo convention recorded yet (seeded 2026-08-02 by brain-toolkit bin/adopt v0.6.2)
- Vault-sync: none
- Session: 2026-10-02_1446_fulfill-demand-factory-20261002-contract

## Session 98 (2026-10-02)

Full narrative, decisions, and context trail: `.brain/sessions/2026-10-02_1545_fulfill-demand-factory-20261002-contract.md`
(the session file is the source of truth in this D052-piloted repo -- the block
below is a **generated projection** of it, produced mechanically by
agent-runner's dispatch supervisor from an auto-drafted, unconfirmed close --
not a second hand-written account, and not yet reviewed by a human or the
worker agent itself).

- State: Fulfill demand factory-20261002-contracts-descriptor-delivery-fields (capability: The app descriptor and the registry app summary carry what Factory needs to deliver without reading app.yaml itself: the GitHub slug, the YouTrack stage-to-state mapping, the route hostname, the integration branch and ... -- status: done (close: auto-drafted, unconfirmed).
- Next step: Review this session's auto-drafted close (`.brain/sessions/2026-10-02_1545_fulfill-demand-factory-20261002-contract.md`) and confirm or correct it.
- Standing: TODO -- no repo convention recorded yet (seeded 2026-08-02 by brain-toolkit bin/adopt v0.6.2)
- Vault-sync: none
- Session: 2026-10-02_1545_fulfill-demand-factory-20261002-contract

## Session 99 (2026-10-02)

Full narrative, decisions, and context trail: `.brain/sessions/2026-10-02_1655_close-the-loop-on-demand-contracts-20261.md`
(the session file is the source of truth in this D052-piloted repo -- the block
below is a **generated projection** of it, produced mechanically by
agent-runner's dispatch supervisor from an auto-drafted, unconfirmed close --
not a second hand-written account, and not yet reviewed by a human or the
worker agent itself).

- State: Close the loop on demand contracts-20261002-factory-repin-descriptor-delivery-fields. It was approved at 2026-10-02T15:55:32.009776Z -- the only thing left is this repo's own archive bookkeeping, which nobody has done yet. 1. GET http://localhost:8082/satisfied/contracts -- find contracts-20261002-f... -- status: done (close: auto-drafted, unconfirmed).
- Next step: Review this session's auto-drafted close (`.brain/sessions/2026-10-02_1655_close-the-loop-on-demand-contracts-20261.md`) and confirm or correct it.
- Standing: TODO -- no repo convention recorded yet (seeded 2026-08-02 by brain-toolkit bin/adopt v0.6.2)
- Vault-sync: none
- Session: 2026-10-02_1655_close-the-loop-on-demand-contracts-20261

## Session 100 (2026-10-02)

Full narrative, decisions, and context trail: `.brain/sessions/2026-10-02_1616_fulfill-demand-factory-20261002-contract.md`
(the session file is the source of truth in this D052-piloted repo -- the block
below is a **generated projection** of it, produced mechanically by
`brain session close`, not a second hand-written account).

- State: fulfill demand factory-20261002-contracts-summary-required-checks -- status: done.
- Next step: See the session file's `## Log` for open follow-ups.
- Standing: TODO -- no repo convention recorded yet (seeded 2026-08-02 by brain-toolkit bin/adopt v0.6.2)
- Vault-sync: none
- Session: 2026-10-02_1616_fulfill-demand-factory-20261002-contract

## Session 101 (2026-10-02)

Full narrative, decisions, and context trail: `.brain/sessions/2026-10-02_1716_fulfill-demand-factory-20261002-contract.md`
(the session file is the source of truth in this D052-piloted repo -- the block
below is a **generated projection** of it, produced mechanically by
agent-runner's dispatch supervisor from an auto-drafted, unconfirmed close --
not a second hand-written account, and not yet reviewed by a human or the
worker agent itself).

- State: Fulfill demand factory-20261002-contracts-summary-required-checks (capability: The registry app summary also carries requiredChecks, appRoot and releaseBranch, so Factory can build agent instructions and verify pull requests from the app record instead of three hard-coded check names and a fixed bra... -- status: done (close: auto-drafted, unconfirmed).
- Next step: Review this session's auto-drafted close (`.brain/sessions/2026-10-02_1716_fulfill-demand-factory-20261002-contract.md`) and confirm or correct it.
- Standing: TODO -- no repo convention recorded yet (seeded 2026-08-02 by brain-toolkit bin/adopt v0.6.2)
- Vault-sync: none
- Session: 2026-10-02_1716_fulfill-demand-factory-20261002-contract

## Session 102 (2026-10-02)

Full narrative, decisions, and context trail: `.brain/sessions/2026-10-02_2030_close-the-loop-on-demand-contracts-20261.md`
(the session file is the source of truth in this D052-piloted repo -- the block
below is a **generated projection** of it, produced mechanically by
agent-runner's dispatch supervisor from an auto-drafted, unconfirmed close --
not a second hand-written account, and not yet reviewed by a human or the
worker agent itself).

- State: Close the loop on demand contracts-20261002-factory-repin-summary-required-checks. It was approved at 2026-10-02T19:28:57.843974Z -- the only thing left is this repo's own archive bookkeeping, which nobody has done yet. 1. GET http://localhost:8082/satisfied/contracts -- find contracts-20261002-fact... -- status: done (close: auto-drafted, unconfirmed).
- Next step: Review this session's auto-drafted close (`.brain/sessions/2026-10-02_2030_close-the-loop-on-demand-contracts-20261.md`) and confirm or correct it.
- Standing: TODO -- no repo convention recorded yet (seeded 2026-08-02 by brain-toolkit bin/adopt v0.6.2)
- Vault-sync: none
- Session: 2026-10-02_2030_close-the-loop-on-demand-contracts-20261

## Session 103 (2026-10-02)

Full narrative, decisions, and context trail: `.brain/sessions/2026-10-02_2212_fulfill-demand-factory-20261002-contract.md`
(the session file is the source of truth in this D052-piloted repo -- the block
below is a **generated projection** of it, produced mechanically by
agent-runner's dispatch supervisor from an auto-drafted, unconfirmed close --
not a second hand-written account, and not yet reviewed by a human or the
worker agent itself).

- State: Fulfill demand factory-20261002-contracts-commands-working-directory (capability: The app descriptor can say whether its review and deploy commands run in the hexagon root or in the app root, so a wrapped app's product-owned tools run inside the product repository, from: factory, target: contracts).... -- status: done (close: auto-drafted, unconfirmed).
- Next step: Review this session's auto-drafted close (`.brain/sessions/2026-10-02_2212_fulfill-demand-factory-20261002-contract.md`) and confirm or correct it.
- Standing: TODO -- no repo convention recorded yet (seeded 2026-08-02 by brain-toolkit bin/adopt v0.6.2)
- Vault-sync: none
- Session: 2026-10-02_2212_fulfill-demand-factory-20261002-contract

## Session 104 (2026-10-02)

Full narrative, decisions, and context trail: `.brain/sessions/2026-10-02_2220_close-the-loop-on-demand-contracts-20261.md`
(the session file is the source of truth in this D052-piloted repo -- the block
below is a **generated projection** of it, produced mechanically by
agent-runner's dispatch supervisor from an auto-drafted, unconfirmed close --
not a second hand-written account, and not yet reviewed by a human or the
worker agent itself).

- State: Close the loop on demand contracts-20261002-factory-repin-commands-working-directory. It was approved at 2026-10-02T21:19:54.610452Z -- the only thing left is this repo's own archive bookkeeping, which nobody has done yet. 1. GET http://localhost:8082/satisfied/contracts -- find contracts-20261002-f... -- status: done (close: auto-drafted, unconfirmed).
- Next step: Review this session's auto-drafted close (`.brain/sessions/2026-10-02_2220_close-the-loop-on-demand-contracts-20261.md`) and confirm or correct it.
- Standing: TODO -- no repo convention recorded yet (seeded 2026-08-02 by brain-toolkit bin/adopt v0.6.2)
- Vault-sync: none
- Session: 2026-10-02_2220_close-the-loop-on-demand-contracts-20261
