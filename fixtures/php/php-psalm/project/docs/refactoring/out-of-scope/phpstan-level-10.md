# Rejection: PHPStan Level 10

**Date:** 2026-08-30
**Reason:** Mutual exclusion (ticket 37) — this target adopted Psalm as its static analyzer (`psalm` node fulfilled); the PHPStan level chain does not apply (see `php-tooling-tree.md`'s `phpstan` equivalents section). Written by the recognition-pass housekeeping described on the `psalm` node's own entry, since `psalm` has no tree-proposed MR of its own to attach the write to. Demonstrates ticket 37's fix: without this entry, `phpstan-level-10` was neither fulfilled nor rejected and `php-structural-scan`/`structural-scan` stayed permanently blocked for a Psalm-only target.
**Scope:** subtree phpstan
