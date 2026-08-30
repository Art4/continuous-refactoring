# Rejection: Psalm Taint Analysis

**Date:** 2026-08-30
**Reason:** Fixture for the "clean repo" Tier 4 negative control (ticket 27) — this target adopted PHPStan (not Psalm) and never adopted `vimeo/psalm` for taint scanning either. Rejected explicitly, same shape as `psalm.md` alongside it, so `php-structural-scan`'s fourteenth resolved-leaf resolves like the other thirteen.
**Scope:** subtree phpstan
