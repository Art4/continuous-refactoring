# Rejection: PHPStan level 5

**Date:** 2026-08-30
**Reason:** Fixture for the "clean repo" Tier 4 negative control (ticket 27) — level 0 is this target's declared ceiling, so the level chain past it is explicitly declined rather than left dangling (this also resolves php-structural-scan's `resolved` gate on phpstan-level-5, signals ticket 2 — phpstan-level-5 replaced phpstan-level-10 as the chain's leaf).
**Scope:** subtree phpstan
