---
slug: archive-satisfied-demands
title: "Satisfied demands stay listed until moved to demands/archive/"
type: procedure
status: active
created: 2026-10-27
updated: 2026-10-27
provenance:
  runs: []
  files: ["demands", "demands/archive"]
---
Move each satisfied demand file to demands/archive/, even when no follow-up is owed.
GET /satisfied keeps listing a demand until the origin's demands/<file>.md is moved. It also returns demands that are already archived, so diff its answer against the open files in demands/ before acting. Commit the archive on its own, with only the rename and its status flip (precedent b776f41).
