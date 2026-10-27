---
slug: python-regen-procedure
title: "Regenerate the Python bindings with datamodel-codegen 0.68.1"
type: procedure
status: active
created: 2026-10-27
updated: 2026-10-27
provenance:
  runs: []
  files: ["gen/python", "DEPLOYMENT.md"]
---
Regenerate gen/python with python -m datamodel_code_generator, then fix enums and diff.
1. Call it as python -m datamodel_code_generator. The shim does not run from Git Bash.
2. Pass --collapse-root-models. Without it, array-of-pattern-string fields become list[ToItem].
3. For a cross-directory $ref (delivery -> ../app), copy the delivery/ and app/ dirs into one temp dir and run directory mode on it. The output maps onto platform_contracts/{delivery,app} with real imports.
4. Directory mode emits plain Enum even with --use-specialized-enum, so sed the generated classes to StrEnum.
5. Diff the regenerated module for renamed classes before committing (see python-regen-renames-enums).
The per-schema commands are in DEPLOYMENT.md.
