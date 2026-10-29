---
demandId: agent-runner-20261029-contracts-owner-questions-schema
worker: contracts
date: 2026-10-29
status: done
shipped: ["tag v0.69.0 (pushed to origin, commit d2115bb)", "schemas/agent-runner/questions.question.json (OwnerQuestion)", "schemas/agent-runner/questions.draft.json (OwnerQuestionDraft)", "schemas/agent-runner/questions.send-result.json (OwnerQuestionsSendResult)", "Python bindings questions_question / questions_draft / questions_send_result", "TypeScript bindings (incl. dist) exported from index.ts", "CHANGELOG v0.69.0", "tests/validate_questions.py registered in tests/run_all.py", "worktree ../contracts-worktrees/v0.69.0", "origin demand contracts-20261029-agent-runner-adopt-owner-questions-schemas"]
---

# Fulfilment - owner-questions inbox schemas

Checked first: not shipped (latest tag v0.68.0, no question/draft/send-result schema anywhere). Shapes were taken from agent-runner's `src/domain/ownerQuestions.ts` and `src/api/questionRoutes.ts` (read-only).

## Acceptance criteria

1. **Question row** - met: `source` spec|conflict, `ref`, `qid`, `question`, and `context`, `recommendation`, `date`, `produces`, `draft`, `acceptedRecommendation`, `draftUpdatedAt`, `draftSentDemandId` (all required, nullable), `stale` boolean. Closed.
2. **Draft body** - met: `{answer, acceptedRecommendation}`, both required, `answer` 1-20000 chars (the runner's `MAX_ANSWER_CHARS`), closed.
3. **Send result** - met: `{id, path, commit, count, skippedStale}`; `count >= 1` because the runner answers 409, not a result, when nothing is sent.
4. **Release** - met: v0.69.0 pushed (`git ls-remote` shows the tag and `main` at d2115bb).

## Notes for agent-runner's follow-up

- Additive release; nothing is re-pinned for anyone (D031). The origin demand "re-pin and adopt" is raised.
- Not modelled: the 4xx/409 error bodies (`{error, reason?}`) and `ParsedQuestion` / `QuestionDraft` (internal store types, not wire shapes).
- `draftUpdatedAt` carries `format: date-time`; the generated Python type is an aware datetime, the TS type a string. The runner already sends ISO timestamps.
- No Java binding (none of the agent-runner brain/runner shapes have one).

## Verification

`python tests/run_all.py` passed (new `validate_questions.py`: valid/invalid cases per schema, every required member removed in turn); `npx tsc --noEmit` and `npm run build` clean; `mvn -B -f gen/java/pom.xml test` 47 tests, 0 failures; Python bindings generated with datamodel-codegen (enum changed to StrEnum) and round-trip checked. **D031 clean install from the pushed tag**: Python via `pip install git+https://github.com/elmoul/contracts.git@v0.69.0#subdirectory=gen/python` in a fresh venv imported and validated the new model; TypeScript via a fresh clone of the tag and `file:` dependency compiled the three types under `tsc --strict --moduleResolution bundler`.
