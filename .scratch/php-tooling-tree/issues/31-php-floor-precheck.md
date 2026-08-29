# 31 — Check the PHP floor once before walking the deterministic PHP tooling leaves individually

**What to build:** Before proposing `php-cs-fixer`, `phpunit`, `composer-audit`, `phpstan-level-0-baseline`, or `test-runner-if-missing` one at a time, check the target's current PHP floor (`composer.json`'s `require.php` / `config.platform.php`) once against each leaf's known minimum version. A leaf whose minimum isn't met yet is skipped (or batch-recorded as out-of-scope with a `**Blocked by:** PHP >= X.Y` entry, ticket 10's mechanical-reversal shape) in one pass instead of five separate propose → design → implement → reject cycles.

**Why:** Observed on a real dry run (`Art4/legacy-todo`, PHP 5.6 floor): all five deterministic PHP tooling leaves got individually proposed, individually filed as candidates, and individually rejected as `wontfix` across five separate passes — each rejection citing the same underlying PHP-version wall (`docs/refactoring/out-of-scope/{php-cs-fixer,phpunit,composer-audit,phpstan-level-0-baseline,test-runner-if-missing}.md`). Five round trips to discover one fact five times.

**Blocked by:** 06 ✓ done — first-wave node walk (ADR-0005); reuses ticket 10's `**Blocked by:** PHP >= X.Y` out-of-scope field and `detect_nodes()`'s version-comparison helpers (`refactor/composer-audit-eligibility` branch) as the mechanical building blocks — this ticket is their forward counterpart (skip/batch-reject up front) to that branch's reversal detection (un-reject once the floor rises).

**Status:** ready-for-agent

- [ ] `tooling_tree.py` (or the manual tree-walk fallback) checks the target's current PHP floor once per pass, against a per-leaf minimum-version table for the five deterministic PHP tooling leaves
- [ ] A leaf below the floor is skipped from `next`/proposals without a separate propose/design/implement/reject cycle per leaf
- [ ] Recorded out-of-scope entries (if any get filed at all under this design) carry `**Blocked by:** PHP >= X.Y` from the start, consistent with ticket 10's format
- [ ] Design decision: skip silently (no out-of-scope entry until something actually asks) vs. batch-file all five `out-of-scope/` entries in one pass — pick one, document the reasoning

## Comments

> **2026-08-29:** Filed while reviewing `.scratch/legacy-todo-loop-observation/findings.md` before deleting it (its Runde 8 finding) — not implemented in `refactor/composer-audit-eligibility`, which only built the reversal direction (ticket 10). Recorded here so the idea survives the findings-log cleanup without being built prematurely.
