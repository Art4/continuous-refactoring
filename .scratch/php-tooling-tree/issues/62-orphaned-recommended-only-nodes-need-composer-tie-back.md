# 62 — `rector-type-coverage`/`semgrep` have no `required` tie back to `composer`, so a rejected Composer can't auto-close them

**What to build:** Two tree-edge additions plus a new structural-invariant test:

1. `composer → rector-type-coverage` (`required`), added **alongside** its existing four
   `recommended` parents (`rector-dead-code`, `rector-code-quality`, `php-cs-fixer`,
   `phpstan-level-3`) — not replacing them.
2. `composer → semgrep` (`required`), added alongside its existing `recommended` parent
   (`psalm-taint-analysis`).
3. A new test in `scripts/test_tooling_tree.py` asserting the general invariant: every PHP-tree node
   that is not itself a genuine root (`composer`, and the generic-root nodes `git`/`is-php-project`/
   `loop-config`) has at least one `required`/`required-any` parent that transitively reaches
   `composer`. Fails loudly if a future edge restructuring drops the last such tie from some node,
   the same way it silently did for these two.

**Why:** Live finding on `continuous-refactoring.de` (`composer` rejected — static site, no PHP
application code): `rector-type-coverage` and `semgrep` are the only two nodes in the entire tree
(generic root + PHP specialization, all ~40 nodes checked) with **zero** `required`/`required-any`
parents but at least one `recommended` parent. `_is_effectively_rejected()` only cascades through
`required`/`required-any` chains (ticket 60), so a node with none can never be automatically
recognized as closed once `composer` is rejected — it can only ever resolve via being fulfilled or via
its own, manually-written `out-of-scope/` entry.

Concretely: `rector-type-coverage` is also a `php-structural-scan` leaf, so this isn't just churn —
it's the *only* leaf of the eleven that can't auto-resolve, meaning `structural-scan` can never open
on a Composer-rejected target without an issue being filed, immediately closed `wontfix`, and a
dedicated `out-of-scope/rector-type-coverage.md` entry written by hand (observed live: issue #4,
MR !19, on `continuous-refactoring.de`). `semgrep` isn't a resolved-gate leaf (Signal-producing node,
ADR-0040) so it doesn't block `structural-scan`, but would produce the identical file-then-close churn
the first time `psalm-taint-analysis` cascades to effectively-rejected on a Composer-rejected target —
not yet observed live, found by the same tree-wide scan.

Both gaps trace to a deliberate design choice made without this consequence in view:
[ADR-0019](../../../docs/adr/0019-static-analyzer-mutual-exclusion-and-taint-analysis-node.md) dropped
`rector-type-coverage`'s direct `required: rector-php-set` edge (explicitly confirmed with the user at
the time — "a real, deliberate loosening... confirmed with the user before implementing"), and
[ADR-0045](../../../docs/adr/0045-semgrep-owasp-top-ten-node.md) never gave `semgrep` one at all,
considering only a `composer`-required edge that *replaces* its `recommended` edge to
`psalm-taint-analysis` (rejected there, for ordering reasons) — never a `composer`-required edge added
*alongside* the existing `recommended` edge, which is what this ticket proposes instead.

**Why adding `composer` as an additional `required` parent is safe, not a re-litigation of either
ADR:**

- In the ordinary case (`composer` genuinely adopted), the new edge never binds: by the time any of
  `rector-type-coverage`'s four `recommended` parents (or `semgrep`'s one) reaches a *decided* state,
  `composer` must already be fulfilled — every one of them already has its own real `required`/
  `required-any` chain back to `composer`. The new edge is pure redundancy there.
- It only ever fires in the one scenario that currently has no automatic closure at all: `composer`
  itself rejected. `required` and `recommended` combine via AND, so this doesn't touch the ordering
  `recommended` already enforces (ADR-0045's "settle Psalm's own scope first" for `semgrep`; ADR-0019's
  "don't require `rector-php-set` specifically" for `rector-type-coverage`) — both stay exactly as
  decided.
- Rejected alternative: extending `_is_effectively_rejected()`'s own semantics so a node with *no*
  `required` parent at all auto-closes once *every* `recommended` parent is individually
  decided-rejected. Would also close today's gap, but tree-wide and speculatively — a human who
  deliberately, individually rejects `rector-dead-code` and `rector-code-quality` while `composer` is
  still fully adopted (a case ADR-0019 explicitly wanted to keep open) would have `rector-type-coverage`
  silently auto-rejected too, with no chance to weigh in on that node specifically. The targeted
  `composer`-edge addition avoids this: it only fires when the PHP-stack signal itself is gone, never
  when a human is selectively deciding among siblings.

**Blocked by:** none. Branched on `tickets/60-diamond-seen-false-negative` (#79) rather than off
`main`, since this is a direct continuation of that ticket's own `tooling_tree.py`/`php-tooling-tree.md`
work and depends on its diamond-cascade fix to have any effect (without ticket 60, the new edges would
still leave `rector-dead-code`/`rector-code-quality` themselves stuck as neither fulfilled nor rejected,
so `rector-type-coverage` would still never resolve either way).

**Priority:** medium — not currently blocking any live target (the one observed occurrence already
resolved itself, at the one-time cost of issue #4/MR !19), but a real, silent gap that will recur on
every future Composer-rejected PHP target and has no test coverage guarding against a third
recurrence via some other future edge change.

**Status:** done — PR pending

- [x] `php-tooling-tree.md`'s edge table: add `composer → rector-type-coverage (required)` and
  `composer → semgrep (required)` rows; update the diagram; update both nodes' own doc entries
  (`rector.md`, `semgrep.md`) to state the new required parent alongside their existing recommended
  one(s), and correct `rector-type-coverage`'s own entry's "No required parent" framing (it now has
  one — `composer` — the "no tie to `rector-php-set` specifically" nuance ADR-0019 established stays,
  worded to survive this addition).
- [x] `tooling_tree.py`: confirm no code change needed — `required_parents` is parsed generically from
  the edge table; `_is_unblocked()`/`_is_effectively_rejected()`/`_resolved_gate_status()` all already
  handle multiple required parents on one node (e.g. `composer-audit`'s existing `[composer,
  ci-runner]`).
- [x] New invariant test (`scripts/test_tooling_tree.py`): every PHP-tree node except the genuine roots
  has a `required`/`required-any` chain that transitively reaches `composer`. Written generically
  (walks `tree['order']`/`required_parents`/`required_any_parents`), not hardcoded to today's two
  fixed exceptions, so it actually catches a *future* regression, not just re-asserts this one.
- [x] Regression test: on `continuous-refactoring.de`'s exact scenario (or an equivalent fixture with
  `composer` rejected), `rector-type-coverage` and `semgrep` both now read as effectively rejected
  automatically (no issue/out-of-scope entry needed) — extends ticket 60's own
  `EffectivelyRejectedRequiredAnyTests`-style coverage.
- [x] Regression test: on a target where `composer` **is** fulfilled and `rector-dead-code`/
  `rector-code-quality` are explicitly, individually rejected by a human (composer otherwise fine),
  `rector-type-coverage` still becomes proposable exactly as ADR-0019 intended — confirms the new edge
  is inert in that case, not a re-tightening.
- [x] Fixture fallout check: re-run `fixtures/harness/run.sh roadmap` (or `tier2`) across the existing
  PHP fixtures — the new required edge could shift `rector-type-coverage`'s/`semgrep`'s own position
  in a 10-step roadmap simulation the same way ADR-0019's/ADR-0045's edge changes each already did;
  regenerate `expected/roadmap.json` snapshots only where the new edge genuinely changes reachability
  timing (it shouldn't, per the redundancy argument above, but confirm rather than assume).
- [x] `python3 -m unittest discover -s scripts -p 'test_*.py'` and `python3 scripts/validate_skills.py`
  stay green.
- [x] Live sanity re-check against `/home/artur/projects/continuous-refactoring.de`: `next_candidates()`
  no longer needs a manual `rector-type-coverage` decision at all — `structural-scan` should already
  read as open once the fresh edges are loaded, entirely from the existing `composer` rejection.

## Comments

> **2026-09-12:** Filed after the user asked, following the live issue #4/MR !19 observation, whether
> other nodes share this structural shape, how to guard against reintroducing it via a future edge
> change, and whether a direct `composer → rector-type-coverage` edge would work. Answered inline
> (this ticket is that answer, formalized): exactly two nodes tree-wide (`rector-type-coverage`,
> `semgrep`), both traced to ADR-0019/ADR-0045 respectively, both fixable the same way, plus a new
> invariant test as the requested guardrail. Branched directly on `tickets/60-diamond-seen-false-
> negative` (#79) per the user's explicit instruction, not off `main`.

> **2026-09-12 (later):** Implemented on branch `tickets/62-composer-required-edge-orphaned-nodes`.
> Both edges added alongside existing recommended parents (not replacing), both node docs updated
> preserving each ADR's own nuance, generic invariant test written (walks the tree, not hardcoded to
> these two names), both regression directions covered. 313/313 tests green, `non-php-project`'s
> `expected/roadmap.json` regenerated (the only fixture affected — `rector-type-coverage`/`semgrep`
> correctly drop out of its 10-step simulation), all 7 other fixtures re-checked unaffected. Live
> sanity against `continuous-refactoring.de`: `next_candidates()` now returns `[structural-scan]`
> directly, no further manual decision needed.
>
> `/code-review` (Standards + Spec axes): Spec axis clean, no findings. Standards axis found one hard
> violation (missing `.changelog.d/*.md` fragment, CI-enforced) — fixed. Two judgement calls noted and
> left as-is: the new test's `_reaches_composer` helper mirrors `_is_effectively_rejected()`'s
> traversal shape (a deliberate, independent structural check on raw edges, not runtime rejection
> state — extracting a shared helper would couple a test-only invariant to the rejection engine for no
> real benefit); a near-verbatim closing sentence in both `rector.md`/`semgrep.md` was already checked
> against `validate_skills.py`'s own duplication advisory and didn't trip it.
