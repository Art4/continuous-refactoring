# Rejection: PHPStan Deprecation Rules

**Date:** 2026-08-30
**Reason:** Fixture for the "clean repo" Tier 4 negative control (ticket 27) — required parent phpstan-level-5 is unreachable under this target's declared level-0 ceiling, so this node is explicitly declined rather than left permanently dangling (ticket 43). This node has since moved to the Signal wave (an additional php-safety-net required parent, no longer a `resolved` leaf) — the required-parent-unreachable rejection above stays the actual reason regardless, since phpstan-level-5 was already permanently blocking it either way.
**Scope:** subtree phpstan
