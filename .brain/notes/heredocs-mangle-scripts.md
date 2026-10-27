---
slug: heredocs-mangle-scripts
title: "Shell heredocs mangle scripts in this harness"
type: gotcha
status: active
created: 2026-10-27
updated: 2026-10-27
provenance:
  runs: []
---
Write helper scripts with the Write tool, not shell heredocs.
Bash heredocs that contain apostrophes fail in this shell. A Python heredoc also turned an escaped backslash-n into a real newline inside JSON strings. If a script has to emit a backslash, build it with chr(92).
