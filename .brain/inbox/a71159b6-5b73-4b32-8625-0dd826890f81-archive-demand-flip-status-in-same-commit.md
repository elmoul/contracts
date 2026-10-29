---
slug: archive-demand-flip-status-in-same-commit
title: "Archiving a demand needs status: open to archived flip alongside git mv"
type: procedure
created: 2026-10-29
updated: 2026-10-29
provenance:
  runs: ["a71159b6-5b73-4b32-8625-0dd826890f81"]
  files: ["demands/archive/"]
source: harvest
repeat_of: archive-satisfied-demands
---
When archiving a satisfied demand, do both in ONE commit: git mv the file to demands/archive/ AND change frontmatter `status: open` to `status: archived` (prior archive commits such as 2d346a9 do this). Edit the file BEFORE or then `git add` it again after git mv, otherwise the edit is left unstaged and the commit contains only the rename, forcing a second follow-up commit (do not force-push main). Verify afterwards with GET /board by exact demand id; substring searches also match other demands that merely mention the name.
