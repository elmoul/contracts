---
id: contracts-20260714-ai-gateway-repin-skip-shape
date: 2026-07-14
from: contracts
to: [ai-gateway]
capability: ai-gateway re-pins contracts to v0.13.0 and adopts AiResponse.skipped, closing the consuming leg of its own demand
acceptance-criteria:
  - ai-gateway's contracts pin (pom.xml dependency version / HEXAGON.md contracts.pin) reads 0.13.0
  - "BrokerService.skippedResponse() sets skipped=true (result/model/provider omitted, tokensIn/tokensOut/computedCost zeroed) instead of the sentinel model=\"skipped\"/provider=\"none\" strings"
  - Existing tests asserting on the sentinel values are updated/replaced to assert on skipped instead
  - The stopgap note in BrokerService's javadoc documenting the sentinel-value workaround is removed
needs-owner: false
status: open
---

# Demand — re-pin `contracts` v0.13.0 and adopt `ai.response.skipped`

## What we need

Per `contracts`' own D043 release-notification duty (`CLAUDE.md` "Release
checklist (per tag)" — live for the first time on this tag): every release
closes its own loop by raising a demand to the origin whose need it fulfils.
`v0.13.0` fulfilled `ai-gateway`'s own demand
(`ai-gateway-20260714-contracts-skip-shape`, `demands/2026-07-14-contracts-ai-response-skip-shape.md`
in that repo) — this is that demand's "re-pin and adopt" close-the-loop, not a
new ask.

`AiResponse` gained an optional `skipped: boolean` field (default `false`);
`result`/`model`/`provider` moved from required to optional (absent when
`skipped` is `true`). Additive, non-breaking — no existing consumer needs new
status-code handling; a `skipped` field a caller doesn't check yet simply
doesn't appear (absent/false).

## Why / what's blocked

Nothing is hard-blocked (this is an additive release, and `ai-gateway`'s
`BrokerService.skippedResponse()` stopgap keeps working either way) — but the
technical debt `ai-gateway`'s own demand described (every consumer having to
string-match `model == "skipped"`) stays live until `ai-gateway` re-pins and
swaps its stopgap for the shipped shape.

## Acceptance criteria

See the frontmatter `acceptance-criteria` list above.

## What we do once closed

`contracts` archives `demands/2026-07-14-ai-gateway-repin-skip-shape.md` to
`demands/archive/` once the coordinator reports this satisfied. No further
action expected on this repo's side — this demand exists purely to close the
release-notification duty, not to request new work from `contracts` itself.
