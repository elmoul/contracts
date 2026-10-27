---
slug: tsc-flags-for-strict-acceptance
title: "Strict tsc acceptance: use bundler resolution"
type: gotcha
status: active
created: 2026-10-27
updated: 2026-10-27
provenance:
  runs: ["9a3eb72a-4fdf-48d8-8d99-d5c70dcce5de"]
---
In the TS acceptance, run tsc with --module esnext --moduleResolution bundler.
The installed tsc rejects --moduleResolution node10 (TS5108, removed) and node16 paired with --module commonjs (TS5110). Passing combos: --module esnext --target es2022 --moduleResolution bundler, or --module node16 --moduleResolution node16. Do not spend retries on the old flags.
