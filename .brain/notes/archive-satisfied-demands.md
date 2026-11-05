---
slug: archive-satisfied-demands
title: "Satisfied demands stay listed until moved to demands/archive/"
type: procedure
status: active
created: 2026-10-27
updated: 2026-11-05
provenance:
  runs: ["a71159b6-5b73-4b32-8625-0dd826890f81"]
  files: ["demands", "demands/archive"]
---
Satisfied demands stay listed until moved to demands/archive/
In ONE commit, git mv the demand file to demands/archive/ and flip frontmatter status: open to status: archived (precedent 2d346a9). Edit the file and git add it again after git mv, or the commit holds only the rename and needs a follow-up (do not force-push main).
GET /satisfied keeps listing a demand until the file is moved, and also returns already-archived ones, so diff its answer against the open files in demands/. Verify with GET /board by exact demand id; substring searches also match demands that merely mention the name.
