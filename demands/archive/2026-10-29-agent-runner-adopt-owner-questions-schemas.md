---
id: contracts-20261029-agent-runner-adopt-owner-questions-schemas
date: 2026-10-29
from: contracts
to: [agent-runner]
capability: "agent-runner swaps its hand-rolled owner-questions types for the generated ones from contracts v0.69.0"
acceptance-criteria:
  - "Closes your consuming leg of agent-runner-20261029-contracts-owner-questions-schema: contracts v0.69.0 (pushed) adds schemas/agent-runner/questions.question.json (OwnerQuestion), questions.draft.json (OwnerQuestionDraft) and questions.send-result.json (OwnerQuestionsSendResult), with TypeScript and Python bindings"
  - "Do: re-pin contracts to v0.69.0 (D031), replace the local row, draft-body and send-result types in src/domain/ownerQuestions.ts and the route bodies in src/api/questionRoutes.ts with the generated ones; the 201 body of POST /questions/send is the send-result, the PUT draft body is the draft, GET /questions rows are the question. Additive release: no other consumer is obliged to move"
needs-owner: false
status: archived
---

# Demand - agent-runner: adopt the owner-questions schemas

## What we need
Re-pin to contracts v0.69.0 and use the generated owner-questions types.

## Why / what's blocked
The routes shipped ahead of the schema; the shapes are now in contracts and the hand-rolled copies can go.

## What we do once closed
Nothing further.

## Not in scope
Changing the wire shapes; the `ParsedQuestion` / `QuestionDraft` store types (internal, not wire).
