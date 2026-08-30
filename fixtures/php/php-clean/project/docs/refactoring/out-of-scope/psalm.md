# Rejection: Psalm

**Date:** 2026-08-30
**Reason:** Mutual exclusion (ticket 37) — this target adopted PHPStan as its static analyzer (`phpstan-level-0-baseline` fulfilled via the real PHPStan path, not the Psalm equivalence); the `psalm` path does not apply. Written alongside the rest of this fixture's rejected leaves so `php-structural-scan`'s thirteenth resolved-leaf resolves like the other twelve.
**Scope:** subtree phpstan
