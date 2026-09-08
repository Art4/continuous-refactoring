# Rejection: PHPStan level 10

**Date:** 2026-08-30
**Reason:** Fixture for the "clean repo" Tier 4 negative control (ticket 27) — level 0 is this target's declared ceiling, so the level chain past it is explicitly declined rather than left dangling. Ordinary, non-gating chain node (signals ticket 2): `php-structural-scan`'s `resolved` gate is resolved via `phpstan-level-5` instead (see that level's own entry).
**Scope:** subtree phpstan
