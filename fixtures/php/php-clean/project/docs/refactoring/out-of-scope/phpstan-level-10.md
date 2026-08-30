# Rejection: PHPStan level 10

**Date:** 2026-08-30
**Reason:** Fixture for the "clean repo" Tier 4 negative control (ticket 27) — level 0 is this target's declared ceiling, so the level chain past it is explicitly declined (this also resolves php-structural-scan's `resolved` gate on phpstan-level-10, ticket 43 — phpstan-level-10 replaced phpstan-level-3 as the chain's leaf).
**Scope:** subtree phpstan
