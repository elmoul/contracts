---
slug: inspect-tree-before-starting
title: "Check git status for a prior attempt's work before starting"
type: procedure
status: active
created: 2026-10-27
updated: 2026-10-27
provenance:
  runs: []
---
A failed earlier dispatch may have left sound uncommitted work; run git status first.
On the ci-runner demand of 2026-09-27, two earlier attempts made no commits. One of them still left schemas and tests in the working tree, and they passed every validator. Reviewing and finishing that work was faster than starting over.
