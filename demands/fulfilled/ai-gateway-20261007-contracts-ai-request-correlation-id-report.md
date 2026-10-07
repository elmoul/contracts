---
demandId: ai-gateway-20261007-contracts-ai-request-correlation-id
worker: contracts
date: 2026-10-07
status: done
shipped: ["tag v0.50.0 (local, not pushed)", "commit bfec7b9 on main (schemas, bindings, tests)", "commit b0ee522 on main (CHANGELOG)", "schemas/ai-gateway/request.yaml AiRequest.correlationId", "same optional field on job.yaml AiJobRequest and research.yaml ResearchJobRequest", "Java, TypeScript and Python bindings regenerated", "tests/validate_ai_request.py extended", "worktree ../contracts-worktrees/v0.50.0"]
---

# Fulfilment - optional correlation id on ai.request

Checked first: no correlation field existed on any ai-gateway request schema (`grep correlationId schemas/ai-gateway` was empty; only ci-runner had one), so the work was done, not no-opped.

## What shipped

Tag `v0.50.0` (additive minor), local only: commits `bfec7b9` and `b0ee522` and the tag are not pushed.

- `AiRequest.correlationId` in `schemas/ai-gateway/request.yaml`: optional string, `minLength` 1, `maxLength` 128, pattern `^[A-Za-z0-9._:/-]+$`. The description says it is an opaque identifier, never user content (no prompt text, names, emails), safe to store and display, that the gateway does not interpret it and may echo it into its call ledger, and that it is additive and optional. Not in `required`, so existing requests validate unchanged.
- The same field with the same rules on `AiJobRequest` (`job.yaml`) and `ResearchJobRequest` (`research.yaml`), noted as distinct from `jobId`.
- Bindings regenerated: Java (`AiRequest`, `AiJobRequest`, `ResearchJobRequest`, via openapi-generator 7.23.0 resttemplate, only those three files copied in), TypeScript (`ai-gateway-{request,job,research}.ts`, `dist/` rebuilt), Python (`ai_gateway/{request,job,research}.py`, with `--target-python-version 3.11 --use-specialized-enum` so existing enums stay `StrEnum`). Versions are 0.50.0 in `gen/java/pom.xml`, `gen/ts/package.json` and `gen/python/pyproject.toml`.
- `CHANGELOG.md` has a v0.50.0 entry.

## Acceptance criteria

1. Optional string with documented format and max length, additive: met.
2. Documented as safe to store and display, opaque, never user content: met (field description on all three schemas).
3. A release tag containing the field so ai-gateway can re-pin: tag `v0.50.0` exists locally and the pinned worktree exists; it is not published until the owner pushes it, as this run forbids pushing.

## Verification

- `python tests/validate_ai_request.py` and `python tests/run_all.py`: all validators passed. New cases cover absent, valid, exactly 128 characters, 129 characters, empty, and free text with a space or email, on all three request shapes.
- `mvn -B -f gen/java/pom.xml test`: exit 0. `cd gen/ts && npx tsc --noEmit`: clean.
- D031 install: a fresh venv `pip install` of `git+file:///...contracts@v0.50.0#subdirectory=gen/python` exposed `correlationId` on all three models and rejected `bad id`. It used a local file URL because the tag is unpushed; the GitHub-URL install (and npm/Maven clean installs) remain to do after the owner pushes.

## Not done / next steps

- Owner pushes `main` and tag `v0.50.0`.
- D043 duty: the "close your consuming leg: re-pin and adopt" demand to ai-gateway is not raised, since raising it needs a pushed commit. Additive release, so no consumer-wide demand.
- Contract only: ai-gateway must re-pin and copy the field into its ledger. dashboard-20261007-ai-gateway-call-ledger depends on that.
- Session note: `.brain/sessions/2026-10-07_1450_...` was already open untracked before this run; this run opened `..._1350_...` and `brain` overrode the pointer to it.
