# 42 — `php-structural-scan`: aggregate the PHP tree's 7 `structural-scan` leaves behind one node

**What to build:** Introduce `php-structural-scan`, a new node owned entirely by
`skills/refactor-scan/references/php-tooling-tree.md`, sitting between the PHP tree's seven existing
`resolved`-edge leaves (`composer-audit`, `phpunit`, `test-runner-if-missing`, `php-cs-fixer`,
`phpstan-level-3`, `rector-dead-code`, `rector-type-coverage`) and the generic `structural-scan` node:

- Repoint the seven leaves' `resolved` edges from `structural-scan` to `php-structural-scan` (same edge
  type, same seven rows, new target).
- Add one new `resolved` edge, `php-structural-scan -> structural-scan`, declared in
  `php-tooling-tree.md` per the existing ownership rule (one endpoint — `php-structural-scan` — lives in
  the language tree).
- `structural-scan` in `tooling-tree.md` now has exactly 2 direct `resolved` parents: `editorconfig`
  (unchanged) and `php-structural-scan` (new), instead of 8 — scales cleanly to a future second language
  specialization (`js-structural-scan`, etc.), which would contribute one more direct parent the same way
  instead of N more leaf edges.
- `php-structural-scan` is resolved once every one of its seven resolved-parents is itself resolved
  (fulfilled, or rejected under `docs/refactoring/out-of-scope/`) — identical `resolved` semantics to
  `structural-scan`'s own gate today, one hop down. It has no fulfilment check of its own beyond that, no
  MR scope, no tool — pure aggregation plumbing. It must never appear in `next_candidates()`'s,
  `roadmap()`'s, or `withheld_candidates()`'s output; only `structural-scan` itself is ever proposed.
- Generalizes `tooling_tree.py`'s resolved-gate computation (currently hardcoded to the literal string
  `"structural-scan"` in `detect_nodes()`, `next_candidates()`, `roadmap()`, and (renamed target)
  `_composer_audit_extra_gate()`) so it works uniformly for any node with `resolved_parents` entries,
  derived from the edge table itself (a node aggregated away into another resolved-gated node's own
  parent list is never exposed as proposable) rather than a second hardcoded name.

**Why:** ADR-0008 designed `structural-scan` as a shared gate across future language specializations
(`tooling-tree.md`'s intro paragraph, `tree-walk-prompt.md`'s tree-loading step) — but wired PHP's
contribution as 7 direct edges into the generic node instead of one aggregated edge, so `structural-scan`'s
own doc already has to hedge its leaf-set prose around "the active language specialization's own tree"
(awkward once a second specialization exists, since the leaf set becomes open-ended and not locally
enumerable from `tooling-tree.md` alone). One aggregation node per specialization keeps
`structural-scan`'s own resolved-parent count fixed at "one per specialization plus `editorconfig`",
regardless of how many leaves any one specialization's tree grows to. Raised by the user directly (not a
`/grill-me` round): they asked why `resolved` needs to be its own edge type at all rather than something
expressible via `required`/`recommended`; a generic aggregate node with `recommended` fan-out was examined
and rejected (edge-direction ambiguity, and a new "auto-fulfilled once decided" node kind the engine
doesn't have), but this PHP-tree-local variant — an aggregation node reusing the existing `resolved` edge
type, not `recommended` — keeps the existing mechanism and fixes a real scaling gap.

**Priority:** medium — not urgent (nothing is broken today), but worth doing before a second language
specialization exists, since retrofitting this shape after two specializations both have direct leaf
edges into `structural-scan` is strictly more edits than doing it now with one.

**Status:** done

- [x] `skills/refactor-scan/references/tooling-tree.md`: reworded the ownership-rule paragraph and
      `structural-scan`'s Fulfilment-check/Edge-type bullets — 2 direct resolved parents
      (`editorconfig`, `php-structural-scan`), not 8; reworded the illustrative dotted-diagram line's label.
- [x] `skills/refactor-scan/references/php-tooling-tree.md`: repointed the 7 leaf `resolved` edges (table +
      diagram) from `structural-scan` to `php-structural-scan`; added the new `php-structural-scan ->
      structural-scan` row; added the `php-structural-scan` node entry (inline, not extracted); reworded the
      "seven resolved rows" prose paragraph after the table; reworded `composer-audit`'s Stop-conditions
      bullet ("every other leaf feeding `php-structural-scan`", dropped `editorconfig` from that named list —
      it's no longer a sibling under the new shape).
- [x] `skills/refactor-scan/SKILL.md`: reworded the `structural-scan` bullet for the two-hop aggregation
      shape; states explicitly `php-structural-scan` is never itself proposed.
- [x] `skills/refactor-scan/references/tree-walk-prompt.md`: generalized the resolved-edge-clears rule
      (previously `structural-scan`-specific) to any node with resolved edges; added an explicit rule that an
      aggregation node (one whose only outgoing edge is itself a `resolved` edge into another node) is
      never collected into the proposable/withheld sets even once resolved.
- [x] `skills/refactor-scan/references/tooling_tree.py`: added a generic `_resolved_gate_status()` helper
      (replacing `detect_nodes()`'s structural-scan-only block), computed in dependency order so
      `php-structural-scan` is resolved before `structural-scan` reads it; renamed
      `_composer_audit_extra_gate()`'s hardcoded `"structural-scan"` lookup to `"php-structural-scan"`
      (composer-audit's true sibling set under the new shape); added a derived
      `exposed_resolved_gate_nodes` set to `load_tree()` (a resolved-gated node that is itself another
      resolved-gated node's resolved-parent is never exposed) and used it in `next_candidates()`,
      `roadmap()`, `withheld_candidates()` to keep `php-structural-scan` out of all three outputs.
- [x] `scripts/test_tooling_tree.py`: updated `LoadTreeTests` (repointed edges, new
      `resolved_parents["php-structural-scan"]`/`["structural-scan"]` and `exposed_resolved_gate_nodes`
      assertions); added `PhpStructuralScanAggregationTests` class (resolves-only-when-all-7-resolved,
      rejected-leaf-still-resolves, two-hop structural-scan regression, never-in-next/roadmap/withheld);
      fixed `StructuralScanGateTests.test_unfulfilled_when_leaves_missing`'s `unresolved` assertion (now
      reports `php-structural-scan`, not the flat leaf name); reworded
      `ComposerAuditGateTests.test_eligible_via_fallback_when_every_other_leaf_resolved`'s comments
      (fixture itself left unchanged, harmless either way).
- [x] `fixtures/php/*/expected/roadmap.json` (all 7): regenerated against `fixtures/harness/run.sh`'s own
      sandboxes; verified each with `fixtures/harness/run.sh roadmap <name>` — 7/7 green, no roadmap
      step-count or order shift in any of them (confirmed per fixture, not assumed).
- [x] New ADR: `docs/adr/0017-php-structural-scan-aggregation-node.md`, amending ADR-0008.
- [x] `python3 -m unittest discover -s scripts -p 'test_*.py'` — 167/167 pass. `python3
      scripts/validate_skills.py .` — clean.

## Comments

> **2026-08-30:** Filed following the shape ticket 41 left open — `structural-scan`'s doc already hedges
> its leaf-set prose around "the active language specialization's own tree" (an open-ended, not-locally-
> enumerable set once a second specialization exists), and this generalizes the resolved-gate mechanism
> the same way ADR-0016 generalized recommended-edge gating, rather than growing a second
> hardcoded-node-name special case in `tooling_tree.py`. Raised directly by the user during a `/plan`
> session questioning why `resolved` needs its own edge type at all; a generic cross-cutting aggregate
> node (with `recommended` fan-out) was considered and rejected first, this PHP-tree-local variant (still
> using `resolved`) is what got approved.
