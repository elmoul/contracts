---
demandId: brain-toolkit-20260802-contracts-brain-adoption
worker: contracts
date: 2026-08-02
status: done
shipped: [.brain/, .claude/settings.json, .githooks/pre-commit, CLAUDE.md]
---

# Fulfillment report — adopt `.brain` in `contracts`

## Prior state

Checked first, as instructed. `contracts` had **no** `.brain/`, no
`.claude/`, and no `.githooks/` before this session. Nothing was already
shipped; the capability was built here.

## What was done

Ran the installer, not a hand-scaffold:

```
python brain-toolkit/bin/adopt contracts        # --dry-run first, then for real
```

Toolkit pin resolved from `brain-toolkit`'s own newest semver tag: **v0.6.2**
(matches the demand). `--dry-run` output was reviewed and matched the real run
exactly.

Created:

- `.brain/conventions.md`, `.brain/architecture.md`, `.brain/sessions/` —
  the three required members — plus `.brain/config.yml`,
  `.brain/overrides.md`, `.brain/.gitignore`, `.brain/toolkit-pin` (`v0.6.2`),
  byte-identical `.brain/bin/brain` + `.brain/bin/structurer` shims, and the
  `derived/` `knowledge/` `events/` `quarantine/` telemetry dirs.
- `.claude/settings.json` with the `Read|Grep|Glob` PostToolUse hook.
- `.githooks/pre-commit` (gitleaks, verbatim copy of
  `conventions/hooks/gitleaks/pre-commit`).
- `CLAUDE.md` — `.brain` protocol section appended under the
  `<!-- brain-adopt:section -->` marker; all pre-existing content preserved.

Shim resolution verified live: `python .brain/bin/brain --help` resolves
through `../brain-toolkit-worktrees/v0.6.2/bin/brain` and prints usage. A
session was opened and closed through the CLI this session, so
`.brain/sessions/` is no longer empty going forward.

## Acceptance criteria

**1. Installed by `bin/adopt`, three required members present** — yes, see
above. No file under `.brain/` was hand-authored.

**2. `.claude/settings.json` merged, not overwritten** — `contracts` had **no
pre-existing `.claude/settings.json`**, so adopt reported it as `Created`
rather than `Merged`; there was no other key that could have been lost. The
merge path was therefore not exercised here — noting this honestly rather than
claiming a merge that did not happen. The file now contains exactly the one
`hooks.PostToolUse` entry.

**3. gitleaks pre-commit hook wired** — `.githooks/pre-commit` present, and
the per-clone config step (which adopt deliberately never runs itself) was run
explicitly in this clone:

```
git config core.hooksPath .githooks     # verified: core.hooksPath = .githooks
```

**4. Conventions validator** — run after adoption:

```
java -jar conventions/validator/target/conventions-validator-0.1.0.jar contracts
→ FAIL (14 checks, 1 failed, 2 unverified)
```

The `.brain` checks behaved exactly as the criterion requires — **no validator
regression**:

- `brain-session-file` → `[UNVERIFIED] WARN — .brain/sessions/ has no session
  files yet; freshly-adopted .brain/, not drift`. This is the fresh-adoption
  **ADVISORY** (conventions `14f3ae7`), **not** a FAIL. Correct.
- `brain-projection-equality` → `PASS (skipped — no session file to project)`.

The single **FAIL is pre-existing and unrelated to adoption**:
`vault-sync-handoff` — the most recent `PROGRESS.md` entry (Session 30,
v0.17.0) ends without a `Vault-sync:` line. That entry predates this session
and this work touched nothing that could affect it. This session's own handoff
carries a proper `Vault-sync:` line, which clears it.

The other `UNVERIFIED` (`status-coherence`) is likewise long-standing and
unrelated.

Re-run after this session's `brain session close` wrote its session file and
the `PROGRESS.md` Session 31 projection:

```
→ PASS (15 checks, 0 failed, 1 unverified)
  [PASS] vault-sync-handoff          most recent PROGRESS.md entry has a Vault-sync: line
  [PASS] brain-session-file          v0.6 format, valid frontmatter; .brain/ complete
  [PASS] brain-session-lessons       non-empty, non-TBD lessons entry
  [PASS] brain-projection-equality   vault_sync matches PROGRESS.md's Vault-sync line — projection intact
```

`contracts` now validates clean; the one remaining `UNVERIFIED` is
`status-coherence`, which predates this work.

**5. Published artifacts exclude `.brain/`** — confirmed, and the mechanism is
structural rather than an ignore list: **`.brain/` lives at the repo root,
while every published package root is a subdirectory** (`gen/ts`, `gen/python`,
`gen/java`). Per repo, per D031's three consumption mechanisms:

- **npm** — `npm pack --dry-run` from `gen/ts` lists **66 files, zero matching
  `brain`**. The package root is `gen/ts/`, so root-level `.brain/` is outside
  the pack tree by construction; the same holds for the `file:../contracts/gen/ts`
  dependency form consumers actually use (D031 amendment, v0.2.1).
- **Python** — pip installs via
  `git+…#subdirectory=gen/python`, so the sdist root is `gen/python/`; on top of
  that `pyproject.toml` carries
  `[tool.setuptools.packages.find] include = ["platform_contracts*"]`.
  `platform_contracts.egg-info/SOURCES.txt` contains zero `brain` matches.
- **Java** — the jar is built from `gen/java` sources by Maven; repo-root paths
  are not on any source or resource root.

`.brain/` is session telemetry and does not reach any consumer of this
version-pinned dependency root.

**6. CLAUDE.md documents `python .brain/bin/brain`** — satisfied. Toolkit
v0.6.2's appended section already leads with **"Always invoke the shims through
`python`"**, explains that the bare extensionless form can produce no output
and no session file under PowerShell (i.e. fails silently), and gives every
example in both `python .brain\bin\brain …` (PowerShell/cmd) and
`python .brain/bin/brain …` (bash) form. No hand-correction of the template was
needed in this repo.

**7. No schema, version, or tag changes** — confirmed.
`git status --short -- schemas gen CHANGELOG.md` is **empty**. No tag was cut,
no version bumped in `gen/ts/package.json` (`0.17.0`), `gen/python/pyproject.toml`
(`0.17.0`), or `gen/java/pom.xml`. The published surface is untouched; adoption
here is purely additive repo tooling. Nothing about it required touching the
published surface, so no stop-and-report was needed.

## Notes for the coordinator

- Criterion 2's merge path is untested in this repo (no pre-existing
  `.claude/settings.json`). If the demand's intent was to prove adopt's merge
  behaviour, that evidence has to come from a repo that already had one.
- Minor, non-blocking, possibly fleet-wide: this repo's `.gitattributes`
  normalises `.githooks/*` to LF but does not cover `.brain/bin/*`, so the
  extensionless `brain`/`structurer` shims will check out CRLF on a Windows
  clone. Python tolerates CRLF so the shims still run, and the committed blobs
  stay byte-identical to the toolkit's — flagging it only in case
  `brain-toolkit` wants adopt to write a `.gitattributes` entry.
- The validator's overall `FAIL` for `contracts` is the pre-existing
  `vault-sync-handoff` finding, not an adoption defect. Reading the exit status
  alone would misattribute it.
