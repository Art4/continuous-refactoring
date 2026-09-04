# Drop the `rector-early-return` node, fold its scope into `rector-code-quality`

> Amends [ADR-0019](0019-static-analyzer-mutual-exclusion-and-taint-analysis-node.md) and
> [ADR-0021](0021-remaining-php-tooling-tree-nodes-extracted.md), the two ADRs that established and
> then extracted `rector-early-return` as its own tooling-tree node/reference file. Neither ADR's
> reasoning was wrong at the time; this one records a fact that has since changed upstream, not a
> correction of either.

A live reviewer-loop run surfaced this directly: a candidate merge request adopting
`SetList::EARLY_RETURN` (`Art4/legacy-todo` PR #112) landed no actual code change — its own body
honestly disclosed that the rule set is currently empty under the pinned Rector version. Checking
upstream (`rectorphp/rector-src`) confirmed this is not a version-specific accident:
`config/set/early-return.php` is `$rectorConfig->rules([])`, with the comment "all early return
rules were moved to code quality set or deprecated." The commit history shows a steady, multi-year
depopulation (individual rules removed or deprecated for readability/risk reasons since 2022), with
the last remaining rules folded into `SetList::CODE_QUALITY` or deprecated outright as of early
August 2026. There is no indication this reverses — the set is being kept only so existing configs
that still reference the constant don't break.

Modeling `rector-early-return` as its own tooling-tree node implies a distinct, reviewable rewrite
step. It no longer is one: adopting it is a no-op config addition, every time, on every target.

## Considered Options

- **Keep the node, treat the empty set as a transient, version-specific artifact.** Rejected — the
  upstream removal has been deliberate and ongoing for years, not a one-off gap expected to reverse
  in a future release; treating it as temporary doesn't match the evidence.
- **Keep the node, but make its Fulfilment check detect the known-empty case and skip cleanly**
  instead of landing a no-op MR. Rejected — every other node in this tree (including every other
  Rector node) detects fulfilment by simple, version-independent presence in `rector.php`/
  `rector.neon` (`tooling_tree.py`'s substring checks); this would be the only node needing
  version-aware logic to answer "does this rule set actually contain anything," a new category of
  fulfilment check for one permanently-empty node. Dissolving the node removes the need for that
  category entirely rather than introducing it.
- **Drop the node, but don't touch `rector-type-coverage`'s gate** (just remove
  `rector-early-return` from its recommended parents, don't replace it). Rejected — that gate's
  stated rationale ("type-coverage rewrites touch messier code" without dead code removed or
  control flow flattened first) would silently lose the "flattened first" half of its own reasoning,
  not just the node that used to carry it. `rector-code-quality` now performs that flattening, so it
  takes over the gate slot instead of the slot disappearing.

## Decision

`rector-early-return` is retired as a tooling-tree node. Its Purpose — flattening nested
conditionals into early returns — folds into `rector-code-quality`'s own Purpose text, since that is
where Rector's rules for it now actually live.

Mechanically:
- `skills/refactor-scan/references/php-tooling-tree/rector.md`: `rector-early-return`'s section
  removed; `rector-code-quality`'s Purpose text gains the early-return description;
  `rector-type-coverage`'s recommended-parent gate swaps `rector-early-return` for
  `rector-code-quality`; `rector-php-set`'s "three direct children" prose becomes two.
- `skills/refactor-scan/references/php-tooling-tree.md`: the node's diagram entry, its four edge-table
  rows, and its stub in the *Nodes* section are removed; a new `rector-code-quality →
  rector-type-coverage` recommended edge replaces the dropped one; `php-structural-scan`'s
  resolved-parent count changes from thirteen to twelve (not "thirteen with a different member").
- `skills/refactor-scan/references/php-tooling-tree/php-structural-scan.md` and `composer-audit.md`:
  their leaf lists/counts updated to match.
- `skills/refactor-scan/references/tooling_tree.py`: the `has_rector_early_return` detection and its
  `set_node` call removed.
- `scripts/test_tooling_tree.py`: tests updated to match the new edge/leaf shape; fixtures no longer
  need an `EarlyReturn` marker.

An existing target repo that already has `rector-early-return` fulfilled in its own
`bookkeeping.md`'s `Fulfilled nodes` (e.g. `Art4/legacy-todo`, via the PR #112 finding that prompted
this) needs no migration — `Fulfilled nodes` is a cache the deterministic parser fully re-derives
from the tree on every pass with parser access (`refactoring-bookkeeping.md`); the orphaned slug
simply stops appearing the next time that happens.

## Consequences

The tree has one fewer node; adopting Rector's code-quality set now also covers what used to be a
separate, always-empty adoption step. No target repo loses any real capability — the underlying
Rector rules were already reachable via `rector-code-quality` before this change, just also
nominally reachable (with zero effect) via the now-retired node too. A target that rejected
`rector-early-return` outright (an `out-of-scope/rector-early-return.md` entry) keeps that file as
an inert historical record — nothing reads it once the slug is gone from the tree.

This ADR is maintainer-facing paper trail only — no skill cites it by number, matching ADR-0011,
ADR-0028, and ADR-0029; the rule itself is stated inline, in plain prose, in `rector.md` and
`php-tooling-tree.md`.
