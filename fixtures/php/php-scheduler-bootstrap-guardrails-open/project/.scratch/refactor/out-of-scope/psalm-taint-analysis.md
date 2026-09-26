# Rejection: Psalm Taint Analysis

**Date:** 2026-08-30
**Reason:** Fixture for the "clean repo" Tier 4 negative control — this target adopted PHPStan (not Psalm) and never adopted `vimeo/psalm` for taint scanning either. Rejected explicitly, same shape as `psalm.md` alongside it, so this leaf of `php-safety-net`'s nine resolves like the other eight.
**Scope:** subtree phpstan
