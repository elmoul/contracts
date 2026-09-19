---
id: contracts-20260919-ai-gateway-repin-research-evidence-envelope
date: 2026-09-19
from: contracts
to: [ai-gateway]
capability: Re-pin and adopt the ResearchJobRequest/ResearchJobStatus evidence envelope published in contracts v0.27.0 for ai-gateway-20260917-contracts-research-evidence-envelope
acceptance-criteria:
  - "ai-gateway re-pins its contracts dependency to v0.27.0 or later (Java and/or TypeScript/Python binding, whichever it consumes)."
  - "ai-gateway confirms it routes POST /ai/research-jobs and GET /ai/research-jobs/{id} through the generated ResearchJobRequest/ResearchJobStatus types instead of hand-rolling the shape, or explains by when/why not."
  - "ai-gateway acknowledges that EvidenceItem carries no model-narrative field by design, so any narrative/summary text produced about the evidence must live in a field this schema does not define -- never folded into EvidenceItem.excerpt, which is reserved for verbatim retrieved content."
needs-owner: false
status: archived
---

# Research evidence envelope — close the consuming leg

## What we need

`contracts` v0.27.0 published exactly the capability
`ai-gateway-20260917-contracts-research-evidence-envelope` asked for: a new,
additive schema pair distinct from `ai.request`/`ai.job.request`/
`ai.job.status` (none of which changed).

`schemas/ai-gateway/research.yaml` (OpenAPI 3.1, same idiom as `job.yaml`):

- `POST /ai/research-jobs` accepts `ResearchJobRequest` (`jobId` caller-
  generated, `appId`, `sources`: array of `SourceRequest` — `url`,
  `maxDurationMs`, `maxBytesPerSource`, all required) and returns `202` with
  a `ResearchJobStatus`.
- `GET /ai/research-jobs/{id}` answers with the current `ResearchJobStatus`
  by the same caller-generated `jobId` — the reconciliation route so an
  interrupted caller never has to guess whether the (paid) retrieval already
  ran.
- `ResearchJobStatus.evidence` is an array of `EvidenceItem`: `url`, `status`
  (`retrieved | unavailable | rejected`), `fetchedAt`/`excerpt` when
  retrieved, `reason` when not, and `enforcedMaxDurationMs`/
  `enforcedMaxBytes` echoing back what bound was actually enforced for that
  source. This array has no field for model-generated narrative text at
  all — the structural separation the demand asked for is that there is
  nowhere for an invented citation to go inside it, not a convention to
  remember on the producer side.
- `status: failed` requires `error` (`ResearchJobError`: `code`/`message`),
  same conditional-required idiom as `AiJobStatus`'s D023 pattern.

Java (`io.platform.contracts.aigateway.ResearchJobRequest` /
`ResearchJobStatus` / `SourceRequest` / `EvidenceItem` / `ResearchJobError`),
TypeScript (`AiGatewayResearchPaths` / `AiGatewayResearchComponents` from
`@platform/contracts`), and Python
(`platform_contracts.ai_gateway.research`) bindings all regenerated and
D031-verified against the real `v0.27.0` tag this session (fresh clone +
`mvn install` + independent consumer project; fresh venv + pip install +
round-trip; `file:`-dependency scratch project against committed `dist/` —
all green, see `CHANGELOG.md` v0.27.0 for detail).

## Why / what's blocked

Whatever caller submits evidence-gathering work through `ai-gateway` has
nothing to route through until this is adopted — hand-rolling the request/
response shape locally is exactly what this demand was raised to avoid.

## What we do once closed

Per D043, this is the origin demand only (additive release — no fleet-wide
"everyone re-pin" per D031/D043 scope). Once `ai-gateway` re-pins and adopts,
act on its follow-up per the coordinator's assembled summary, then archive
this file.
