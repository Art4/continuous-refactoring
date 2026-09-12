# 60 — `_is_effectively_rejected`/`_is_permanently_gated` mis-treat a diamond as a cycle, causing a false negative

**What to build:** `_is_effectively_rejected()` and `_is_permanently_gated()` (`tooling_tree.py`)
each thread a single, mutable `_seen` set into every sibling call inside their `any(...)` (over
`required_parents`) and `all(...)` (over `required_any_parents`) checks. The set is meant to guard
against a cycle (a well-formed tree never has one), but a **diamond** — two siblings that
independently re-converge on a shared ancestor further up, not a cycle at all — trips the same guard:
the first sibling's traversal adds the shared ancestor to `_seen`, and the second sibling's legitimate
revisit of that same node is then wrongly treated as "already seen" and short-circuits to `False`,
even when continuing would find the real rejection/gate.

Fix: pass an isolated copy of `_seen` (e.g. `set(_seen)`) into each sibling's recursive call inside
both generator expressions, in both functions — preserves same-path cycle detection while letting
independent siblings each traverse the shared ancestor on their own terms.

**Why:** Live case, `continuous-refactoring.de` (GitLab, static HTML/CSS/JS site with one `deploy.php`
Deployer recipe): `is-php-project` correctly detects PHP, `composer` is correctly rejected as
out-of-scope (`docs/refactoring/out-of-scope/composer.md`). Everything downstream of `composer`
should cascade-resolve per [Ticket 53](53-rejected-required-parent-should-cascade-resolve-gate.md) —
but `rector-php-set`'s `required-any(phpstan-level-0, psalm)` gate is exactly this diamond
(`phpstan-level-0` and `psalm` both require `static-code-analyzer` → `composer`), so
`_is_effectively_rejected('rector-php-set', ...)` wrongly returns `False`. `php-structural-scan` and
`structural-scan` both sit stuck in `unresolved`, `next_candidates()` returns `[]`, and the loop has
no proposable candidate at all despite `composer` being legitimately, permanently rejected.

Confirmed via direct reproduction against the real tree:
```python
seen = set()
_is_effectively_rejected('phpstan-level-0', tree, {'composer'}, seen)  # True
_is_effectively_rejected('psalm', tree, {'composer'}, seen)            # False (bug) — shared seen
```
Isolated calls (fresh `_seen` each) correctly return `True` for both.

Ticket 53's own test coverage was a **linear** chain (`phpstan-level-6` behind rejected
`phpstan-level-2`) and never exercised a `required-any` diamond, so it never caught this.

`_is_permanently_gated()` has the structurally identical pattern and reproduces the same false
negative under a synthetic diamond (fake tree, two siblings sharing a gated ancestor). On the real
tree it currently doesn't manifest — purely because both `static-code-analyzer` and `psalm` (the
diamond's shared ancestor and one of its own siblings) happen to be `_NEVER_PROPOSED` nodes
themselves, so the self-gate check fires before the polluted `_seen` is ever consulted. That's
incidental, not a structural protection — fix both functions, not just the one currently observed
live.

**Blocked by:** none.

**Priority:** high — a target can detect PHP correctly, reject Composer correctly, and still never
reach `structural-scan` at all; the loop has zero proposable candidates with no way out short of a
code fix.

**Status:** open

- [ ] `_is_effectively_rejected()`: pass `set(_seen)` (not `_seen`) into each sibling's recursive call
  in both the `required_parents` `any(...)` and `required_any_parents` `all(...)` checks.
- [ ] `_is_permanently_gated()`: same fix, same two call sites.
- [ ] Regression test: `rector-php-set`'s real `required-any(phpstan-level-0, psalm)` diamond against
  a rejected `composer` — was `False`, must become `True`.
- [ ] Regression test: same diamond shape for `_is_permanently_gated()` (synthetic tree is fine, since
  the real tree doesn't currently expose it live).
- [ ] Full suite (`python3 -m unittest discover -s scripts -p 'test_*.py'`) and
  `python3 scripts/validate_skills.py` stay green.
- [ ] Live sanity check: re-run `tooling_tree.py` against `/home/artur/projects/continuous-refactoring.de`
  and confirm `next_candidates()` is no longer empty.

## Comments

> **2026-09-12:** Root-caused via an analysis-only request ("bitte analysieren", no code changes) on
> the live `continuous-refactoring.de` stuck-loop report. Filed for `/implement` once the user
> confirmed proceeding with the fix.
