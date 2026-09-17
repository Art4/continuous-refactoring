# Rejection: PHPStan level 10

**Date:** 2026-08-30
**Reason:** Fixture for the "clean repo" Tier 4 negative control — level 0 is this target's declared ceiling, so the level chain past it is explicitly declined rather than left dangling. Ordinary, non-gating chain node: `php-safety-net`'s `resolved` gate is resolved via `phpstan-level-5` instead (see that level's own entry).
**Scope:** subtree phpstan
