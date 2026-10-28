---
hexagon: contracts
kind: buildtime
spec-version: 1
contract-as-of: 2026-10-28
state-as-of: 2026-10-28
verified-against: 4cc862cff227 (contracts v0.9.0)
decisions: [D002, D007, D009, D010, D015, D022, D029]
review-window-days: 90
---

# contracts

## Contract

### 1. Purpose

`contracts` is the platform's shared kernel and the leaf of its dependency graph (D015). Every cross-hexagon port is defined here once, as a schema, and every other hexagon pins a tag of this repo. It is schema-first and language-neutral (D007): the schemas are the authority and the Java, TypeScript and Python bindings are generated from them. It exists only at build time and ships as tagged source pinned by Git tag, with no package registry (D031). It also owns the release discipline that keeps a polyrepo fleet consistent: the compatibility rule, the changelog and the re-pin demands each release raises (D043).

### 2. Responsibilities

| Responsibility | Status | Decision |
|---|---|---|
| Define every cross-hexagon contract as a schema under `schemas/`. The file is the authority for its shape | built | D015, D007 |
| OpenAPI for sync HTTP surfaces; JSON Schema for payloads, async events and repo self-description | built | D015, D013 |
| Generate Java, TypeScript and Python bindings from the same schemas | partial: Java covers only families that have a Java producer or consumer; TS and Python emit if/then and exactly-one-of rules as optional fields | D015 |
| One repo-wide semver per release across the binding version files, recorded in `CHANGELOG.md` | built | D015 |
| Distribute by Git tag: Java by local `mvn install`; TypeScript by `file:` dependency into a per-tag worktree; Python by pip Git URL with a subdirectory | built | D031, D042 |
| CI verification on push, pull request and tag: build, tests, schema validators, and a clean-install acceptance per language on tag | built | D031 |
| Raise the release-notification demands as part of every release | built | D043, D054 |
| App contracts that every app implements, including the app class | built | D009, D010 |
| AI gateway contracts: unified call, sync preflight, async jobs | built | D022 |
| State-feed contracts: SSE event union, guest projection | built | D029, D008 |
| Shapes for control-plane, demand, delivery, runner, brain, conventions and spec status, added when their owning hexagons demand them | built | D014, D144 |

### 3. Boundaries

| Invariant | Decision | How checked |
|---|---|---|
| No business logic and no runtime code: only schemas, generated types and validators | D015 | review; the reader finds no compose service, port or route |
| Not a deployed service | D015 | reader (no compose, no ports); `DEPLOYMENT.md` |
| No package registry and no publish step | D031 | the TS package is private; neither `DEPLOYMENT.md` nor CI has a publish, deploy or upload step |
| Depends on no hexagon, and nothing is imported into it. Bindings may depend only on serialization and validation libraries | D015, D007 | `deps` is empty in `HEXAGON.md`; review of the binding manifests |
| Functional names only | D002 | review only; there is no word scan (D145) |
| No secrets, config or environment values | none recorded | committed pre-commit secret scan (gitleaks) |
| Files under `gen/` are never edited by hand | none recorded | review only; nothing compares `gen/` with a fresh regeneration |
| Additive change is minor; removal, rename or a new required field is major; fixes are patch | D015 | review only; no tool computes or enforces the bump |
| A distribution path counts as working only after a real clean install through it | D031 | CI clean-install acceptance job per language on tag |
| A release is not done until its demands are raised | D043 | release checklist in `CLAUDE.md`; reports under `demands/` |

### 4. Interfaces

Nothing is called or emitted at runtime; the interface is the schema set at a pinned tag, one directory per family under `schemas/`. The consumers listed are those named in this repo's release demands; each consumer's own manifest governs its pin.

| Family | Contract ids | Owner / producer | Known consumers | Decision |
|---|---|---|---|---|
| App | `app.manifest`, `app.identity`, `app.health`, `app.descriptor`, `usage.event`, `dimension.event`, `telemetry`, deployment identity | apps | control-plane, treasury (`usage.event` over Kafka), observability, factory, plantpal | D009, D010, D022 |
| AI gateway | `ai.request`/`ai.response`, `ai.preflight.request`/`ai.preflight.response`, AI job, research job, model manifest | ai-gateway; treasury answers preflight | apps, agents | D022, D023 |
| State feed | `state.event` (oneOf union; Java through an OpenAPI wrapper), `state.projection.guest` | emitting hexagons | state-feed, dashboard, design-studio, app-studio, plantpal | D029, D008 |
| Control plane | `hexagon.descriptor`, `registry.entry` | control-plane | control-plane | D014, D010 |
| Demand coordination | demand, fulfillment, queue entry, approval receipt | demand-coordinator | dashboard, factory | none recorded |
| Delivery and delivery API | issue, page, ref, sync request and operation, decision, evidence, error, defect task, deployment receipt, producer result, workflow, operation coverage; OpenAPI documents for YouTrack delivery, CI-runner results and app-deploy lookup | youtrack | factory, ci-runner, plantpal | none recorded |
| YouTrack planner | planner request, plan, run, model, project, brief, setup gate | youtrack | factory | none recorded |
| Factory | continuation, evidence receipt, handover setup, outcome, recovery checkpoint | factory | factory | none recorded |
| Agent runner | runner dispatch request, reservation, run record, transcript snapshot, parked-run set | agent-runner | factory, platform-vault | D115 |
| Brain | `brain.job`, `brain.job-page`, `brain.settings`, `brain.settings-update`, `brain.stats`, `brain.functions`, `brain.usage` and run, note and summary shapes | agent-runner, brain-toolkit | brain-toolkit, dashboard | D143, D144 |
| Conventions and spec | `conventions.rule`, `.finding`, `.repo-result`, `.run`, `.candidate`, `.conflict`; `spec.status`, `spec.drift-item` | control-plane | agent-runner, brain-toolkit, dashboard | D144 |
| Launcher | command request, result, error; review-environment OpenAPI | launcher | platform-vault | D115 |
| Connector | vocabulary, invoke request, invoke response | connectors | connector callers | none recorded |
| CI runner | build command, build result | ci-runner | ci-runner | none recorded |
| App studio, stage | app mission, task plan; companion turn | app-studio; stage | app-studio, platform-vault | none recorded |

Shape rules carried by the schemas:
- `app.health` follows the Spring Actuator shape (status plus a per-component breakdown). Non-Spring apps conform to it.
- `ai.preflight.response` answers allow, downshift or block. A block always carries an explicit limit reason (D023).
- `state.projection.guest` is a strict allow-list, never the full feed (D008).
- Event schemas evolve additively only.

### 5. Data owned

- `schemas/`: the authority for every shape.
- `gen/java`, `gen/ts` (including the committed `dist/`), `gen/python`: generated bindings, committed at release.
- `CHANGELOG.md` and the release tags: the authority for what changed in each tag.
- `tests/`: Python schema validators and the state-event sync check. Java round-trip tests live under `gen/java/src/test`.
- `demands/`: fulfilment reports and archived release demands.

### 6. Dependencies

| Kind | Dependency | Failure posture |
|---|---|---|
| Runtime | none | not applicable |
| Inherited by consumers | Java: Jackson (Jakarta validation and annotation are optional). Python: pydantic. TS: none | the consumer's install or build fails; there is no runtime fallback |
| Build | Maven with the jsonschema2pojo plugin; openapi-generator CLI through npx; json-schema-to-typescript, openapi-typescript and the TypeScript compiler; datamodel-code-generator | release blocked until regenerated; versions locked in `gen/java/pom.xml`, `openapitools.json` and `gen/ts/package.json` |
| Build | Python with `jsonschema` (CI also installs `pyyaml`); JUnit | release blocked |
| Build | GitHub Actions `verify.yml` | a red run is visible; whether it blocks a tag is not set (Q6) |
| Distribution | GitHub remote with pushed tags | Python pins cannot install an unpushed tag; Java and TS need a local checkout or worktree |
| Optional | gitleaks for the pre-commit hook | behaviour when gitleaks is absent is not stated (Q7) |
| Optional | demand-coordinator inbox | if a release demand cannot be raised, the release is not done (D043) |

### 7. Owner switches and policies

- There are no runtime switches and no environment flags.
- The owner pushes tags. A tag cut locally cannot be consumed by Python pins until it is pushed.
- The owner decides every major bump and any change to the versioning rule.
- The owner approves and sequences consumer re-pins, which are deliberate (D031). An additive release raises only the origin's re-pin-and-adopt demand. A breaking release also raises an adopt-or-explain-by-when demand to every consumer of the changed schemas, found through the control-plane consumer graph (D043, D014). A fleet-wide bump is not the convention.
- A wave-commissioned root release, cut before its consumers exist, has `platform-vault` as its origin. Its demand backpoints to the previous such release's demand (D054).
- Widening a closed enum is a minor bump, but a strict consumer rejects the new value until it re-pins. The consumer must re-pin before any producer emits that value.
- Release order: changelog, regenerate, tests, tag and push, raise demands. Detail is in `CLAUDE.md`.

### 8. Planned, not built

- Automatic regeneration of the bindings in CI when a schema changes, with a diff check against `gen/`.
- Java bindings for the brain, delivery, factory, YouTrack-planner and runner dispatch, reservation and run-record families, added when a Java producer or consumer appears.
- Avro or Protobuf with a schema registry for event encoding. Deferred to the go-commercial milestone; no schema-registry service before then.

### 9. Open owner questions

1. `HEXAGON.md` and the D015 wording call for per-contract independent versioning, but the repo has one version. Should the per-contract intent be retired and `HEXAGON.md` reworded?
2. Does every release move all three binding version files, or only the files whose generated output changed?
3. Event encoding: stay with JSON Schema, or move to Avro or Protobuf with a registry? Which milestone triggers the change?
4. Should binding regeneration move into CI, and when?
5. `gen/java/pom.xml` holds a self-pin of `contracts` that lags the binding version (see the state zone). What is it for, and should it track the release?
6. Does a red `verify.yml` run block a tag?
7. What should the pre-commit hook do when gitleaks is missing?
8. TS and Python leave if/then and exactly-one-of rules as optional fields. Is schema-only enforcement acceptable, or must generators or a runtime validator close the gap?
9. `HEXAGON.md` lists none of D031, D042, D043, D054 or D144, and it says the bindings are published. Should the list be extended and the wording aligned with D031?
10. `brain.settings` lists only the original brain functions, while `brain.functions` now also has spec-sync and spec-seed. Should they be aligned?
11. The v1 spec placed the D003 theme-swap acceptance test on `state.event`. Does that test still stand after D145?

### 10. Retired

- The theme framing of D002, the skin-name table and the theme word scan (D145). Functional names only stands.
- The 3D renderer as a consumer of `state.event` (D145 amending D029). The consumers are the dashboard and the guest projection.
- Publishing to a registry (Maven deploy, npm publish, pip upload), replaced by Git-tag pinning (D031).
- The npm Git-URL dependency and the shared sibling checkout for TypeScript, replaced by a `file:` dependency into a per-tag worktree (D031, D042).

<!-- state:begin (generated by spec sync; do not edit) -->
## Current state

Verified against `4cc862cff227` (contracts 0.9.0), `2026-10-28`. Facts read by brain-toolkit's own reader (validator `--facts` unavailable).

### Status

| Item | Value | Source |
|---|---|---|
| Status | active | HEXAGON.md:5 |
| Kind / side | buildtime / shared | HEXAGON.md:3-4 |
| Deps | none | HEXAGON.md:6 |
| Commit | 4cc862cff227 | reader |
| Tracked files | 758 | reader |

### Version and tag

| Location | Value |
|---|---|
| gen/java/pom.xml | 0.67.0 |
| gen/ts/package.json | 0.67.0 |
| gen/python/pyproject.toml | 0.67.0 |
| Latest tag | v0.67.0 |
| Earlier tags | v0.66.0, v0.65.0, v0.64.0, v0.63.0 |
| CHANGELOG.md top entry | v0.67.0, 2026-10-28, additive |

All three version files, the latest tag and the changelog agree.

### `contracts` pin

| File:line | Pin | Agrees with the binding version? |
|---|---|---|
| gen/java/pom.xml:219 | 0.9.0 | no: the bindings are at 0.67.0. The sources do not state its purpose (contract Q5) |

This is the only pin location. Consumer pins live in each consumer's manifest and were not read for this revision.

### Runtime surface, services and data stores

| Item | Value |
|---|---|
| Compose services | none |
| Ports | none |
| Routes | none |
| Migration files | 0 |
| Data stores | none |

### Repository counts

| Schema files | Test files | Test cases |
|---|---|---|
| 89 | 88 | 47 |

### Java binding coverage

| Family | Java binding | Source |
|---|---|---|
| ai-gateway, app, state-feed (events), stage | committed sources | gen/java/src/main/java |
| usage.event, dimension.event, telemetry | generated at build | gen/java/pom.xml jsonschema2pojo sources |
| ci-runner, control-plane, connector, demand-coordinator, app-studio | generated at build | DEPLOYMENT.md |
| conventions, spec | yes (`lastJob` is `Object`) | CHANGELOG.md v0.66.0 |
| brain.* (including brain.job, brain.functions) | none | CHANGELOG.md v0.66.0, v0.67.0 |
| delivery, factory, youtrack planner, runner dispatch, reservation and run record | none | hexagon page §7 |

### Toolchain

| Item | Value | Source |
|---|---|---|
| Java target | 21 | gen/java/pom.xml:19-20 |
| Jackson | 2.17.0 | gen/java/pom.xml:22 |
| jsonschema2pojo | 1.2.1 | gen/java/pom.xml, DEPLOYMENT.md |
| openapi-generator-cli | 7.23.0 | DEPLOYMENT.md (openapitools.json) |
| Python | >=3.11, pydantic>=2.0 | gen/python/pyproject.toml |
| TypeScript | ^5.0.0; package private | gen/ts/package.json |
| CI | verify.yml: push to main, tag v*, PR to main; Java 21, Node 20, Python 3.12 | hexagon page §4 (read at v0.62.0) |

### Owner switches

| Switch | Live default |
|---|---|
| Runtime switches and env flags | none |
| Tag push | manual, by the owner |
| Binding regeneration | manual |

### Where code and contract disagree

| Kind | Where | Finding |
|---|---|---|
| code-vs-contract | HEXAGON.md:27 vs CHANGELOG.md:3-9 | HEXAGON.md says each contract is versioned independently; the repo has one version for the whole repo |
| code-vs-contract | HEXAGON.md:28 vs DEPLOYMENT.md:3-6 | HEXAGON.md says the Maven, npm and pip packages are published; DEPLOYMENT.md says there is no registry and no publish step (D031) |
| code-vs-contract | HEXAGON.md:8-15 | the decisions list omits D031, D042, D043, D054 and D144 |
| code-vs-contract | gen/java/pom.xml:69 | the plugin comment names usage.event and state.event; the plugin actually generates usage.event, dimension.event and telemetry, and state.event comes from openapi-generator |
| code-vs-contract | gen/java/pom.xml:219 | the self-pin is 0.9.0 while the bindings are at 0.67.0 |
| code-vs-contract | gen/ts/index.ts:1 | the header reads v0.1.0 (per the hexagon page at v0.62.0; not re-read) |
| code-vs-contract | CHANGELOG.md v0.67.0 | brain.settings still lists only the original functions; brain.functions gains spec-sync and spec-seed |
| fact-mismatch | hexagon page §3, §4 | the page gives v0.62.0 as the latest tag and 0.62.0 in the version files; the facts are v0.67.0 and 0.67.0 |
| fact-mismatch | hexagon page §3 | the page counts 79 schema files; the reader counts 89 |
| fact-mismatch | v1 spec header | says v0.13.0 is live; the latest tag is v0.67.0 |
| fact-mismatch | PLATFORM_STATE.md:1418 (per hexagon page) | the row reads v0.15.0; the latest tag is v0.67.0 |
| fact-mismatch | DEPLOYMENT.md pin examples | the commands use v0.7.0; they are illustrations, not the current tag |

### Planned items the code now contains

| Planned in | Item | Now |
|---|---|---|
| v1 spec §4, §8 | CI for the bindings | verify.yml builds, tests and runs a clean-install acceptance on tag; regeneration is still manual |
| v1 spec §4 | Python binding | gen/python, gen/python/pyproject.toml |
| v1 spec self-describing checklist (D013) | README, HEXAGON, DEPLOYMENT and CHANGELOG files | all tracked |
| v1 spec §9 stubs | telemetry, hexagon.descriptor, registry.entry, state.projection.guest | present: gen/python/platform_contracts/app/telemetry.py and control_plane/hexagon_descriptor.py and registry_entry.py; guest projection per hexagon page §3 |
<!-- state:end -->

## Spec changelog

- 2026-10-28 v1: Seeded as v2 from the v1 spec, the hexagon page and the repository at 4cc862cff227 (D144).
