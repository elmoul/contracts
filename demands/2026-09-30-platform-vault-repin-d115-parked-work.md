---
id: contracts-20260930-platform-vault-repin-d115-parked-work
date: 2026-09-30
from: contracts
to: [platform-vault]
capability: Close the consuming leg of platform-vault-20260930-contracts-d115-parked-work - the D115 parked-work shapes shipped in contracts v0.39.0
acceptance-criteria:
  - "platform-vault reviews contracts v0.39.0 (schemas/agent-runner/parked.wait-condition.json, parked.run-result.json, parked.condition-event.json, parked.resume-request.json) and either accepts it or raises the specific gaps back to contracts."
  - "platform-vault's follow-up demands (ci-runner, demand-coordinator, dashboard, agent-runner, factory), each after the contracts demand, name v0.39.0 as the tag to pin."
needs-owner: false
status: open
---

# D115 parked work: close the consuming leg

`contracts` **v0.39.0** shipped what `platform-vault-20260930-contracts-d115-parked-work`
asked for. It is additive: no existing schema changed, and `demand.after` is untouched.

- **`parked.wait-condition`:** `ci-run`, `pull-request` (`until` merged / closed /
  merged-or-closed), `repository-created`, `owner-decision`, and `demands` (`mode`
  all / any over `{demandId, state}`, state `approved | satisfied | archived`).
- **`parked.run-result`:** `state: parked`, `resumeOwner` (`factory | agent-runner`),
  `wait` (`waitId`, `condition`, required `deadline`), exact `reference`, `checkpoint`,
  `resumeNote`.
- **`parked.condition-event`:** stable `eventKey`, `source` (`ci-runner |
  demand-coordinator | owner-ui`), `observedAt`, per-kind `outcome`.
- **`parked.resume-request`:** the event, `action` (`continue | fix | reassess`),
  `resumeNote`, and a keyed `dispatch` whose `dispatchKey` is derived as `"resume:" +
  sha256(waitId + "\n" + eventKey)`.

Install: `platform-contracts @ git+https://github.com/elmoul/contracts.git@v0.39.0#subdirectory=gen/python`
(D031-verified from the tagged URL in a clean venv). Choices the demand left open are
listed in `demands/fulfilled/platform-vault-20260930-contracts-d115-parked-work-report.md`.

## Why

D043 release duty: the origin closes its consuming leg. Additive release, so no other
consumer is obligated to move (D031).
