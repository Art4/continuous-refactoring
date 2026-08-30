# Rejection: PHPStan level 3

**Date:** 2026-08-30
**Reason:** Fixture for the "clean repo" Tier 4 negative control (ticket 27) — level 0 is this target's declared ceiling, so the level chain past it is explicitly declined (this also resolves structural-scan's `resolved` gate on phpstan-level-3, ADR-0008).
**Scope:** subtree phpstan
