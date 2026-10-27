---
slug: tsc-module-resolution-flags-acceptance
title: "Strict tsc acceptance: node10 removed, node16 needs module node16"
type: gotcha
created: 2026-10-27
updated: 2026-10-27
provenance:
  runs: ["9a3eb72a-4fdf-48d8-8d99-d5c70dcce5de"]
  files: ["gen/ts/index.ts"]
  decisions: ["D031"]
source: harvest
repeat_of: null
---
In the D031 TypeScript clean-install acceptance, the installed tsc rejects --moduleResolution node10 (TS5108, removed) and --moduleResolution node16 paired with --module commonjs (TS5110). Use --module esnext --target es2022 --moduleResolution bundler (passes), or --module node16 --moduleResolution node16. Don't burn retries on the old flag combos.
