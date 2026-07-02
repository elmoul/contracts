# Changelog

All contract versions are tracked here. Each contract is versioned independently (semver).

Format: `[contract] vX.Y.Z — YYYY-MM-DD — description`

Breaking changes (removals, renames, new required fields) bump major.
Additive changes (new optional fields) bump minor.
Fixes/clarifications bump patch.

---

## Unreleased

### usage.event
- Initial schema: appId, userId, provider, model, tokensIn, tokensOut, computedCost, timestamp.

### ai.request / ai.response
- Initial schema: unified AI call shape through ai-gateway.

### ai.preflight.request / ai.preflight.response
- Initial schema: gateway ↔ Treasury synchronous authorization (allow / downshift / block).

### app.manifest
- Initial schema: app registration payload (name, version, routes, owner, plan, class).

### app.health
- Initial schema: health response shape.

### state.event
- Initial schema: SSE event envelope for the state feed.
