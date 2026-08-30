# Rejection: PHPStan Deprecation Rules

**Date:** 2026-08-30
**Reason:** Fixture for the "clean repo" Tier 4 negative control (ticket 27) — required parent phpstan-level-5 is unreachable under this target's declared level-0 ceiling, so this node is explicitly declined rather than left permanently dangling (resolves php-structural-scan's `resolved` gate on it, ticket 43).
**Scope:** subtree phpstan
