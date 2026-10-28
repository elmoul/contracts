# Proposed spec delta: contracts

Spec `../platform-vault/spec-contracts.md`, drafted 2026-10-28 against `495a2ab15d2b` from 6 drift item(s) in `.brain/spec/drift.json`.
Contract-zone edits only; the vault session (or the app's next Factory task) applies them, the owner approves.

## 1. 2. Responsibilities: replace
Drift: code-vs-contract-37573021
- | Generate Java, TypeScript and Python bindings from the same schemas | partial: Java covers only families that have a Java producer or consumer; TS and Python emit if/then and exactly-one-of rules as optional fields | D015 |
+ | Generate Java, TypeScript and Python bindings from the same schemas | partial: Java covers the families that have a Java producer or consumer, plus the stage family, which has neither; TS and Python emit if/then and exactly-one-of rules as optional fields | D015 |
Reason: The Java tree carries the stage bindings (CompanionMessageRequest, CompanionMessageResponse, StageContext), so the Java coverage statement must name that exception.

## 2. 10. Retired: delete
Drift: code-vs-contract-8e51e5fa
- | The app-studio schema family (`app.mission`, `app.task-plan`) | 2026-10-28 | D140, D146 | none |
Reason: The app-studio bindings are still committed and are removed only in the next minor release, which section 8 already records as planned, so listing the family as retired is false today.
