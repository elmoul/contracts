---
slug: mvn-needs-absolute-pom-path
title: "mvn -f with a relative pom path runs no tests"
type: gotcha
status: active
created: 2026-10-27
updated: 2026-10-27
provenance:
  runs: []
  files: ["gen/java/pom.xml"]
---
Call mvn -f with an absolute pom path and grep the 'Tests run' summary.
With a relative path and the shell cwd somewhere else, mvn exits 1 without running a single test, and that is easy to miss. From the repo root: mvn -f $PWD/gen/java/pom.xml test | grep 'Tests run'
