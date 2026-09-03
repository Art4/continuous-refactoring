# `is-php-project`

Node on the generic **tooling tree** (`skills/refactor-scan/references/tooling-tree.md`); parents, edges, and the diagram live there. Vocabulary: `CONTEXT.md` (**node**, **required edge**, **recommended edge**).

- **Name:** PHP Project Recognition
- **Tool:** none — recognition-only, the tree's own gate, not a third-party tool.
- **Purpose:** a **recognition gate** — hold the PHP specialization's entire tree closed until there's a
  genuine signal the target actually uses PHP, instead of proposing its nodes (`composer` and everything
  beneath it) on every target regardless of language and relying on a human to reject each one by hand as it
  becomes reachable. One gate per specialization; this is the first (a future CSS/JS specialization adds its
  own sibling the same way). The gate's *role* is generic — evaluated fresh every pass, regardless of which
  specializations exist — even though what this particular gate detects is necessarily PHP-specific.
- **Fulfilment check:** `composer.json` (or `composer/composer.json`) present, **or** at least one `*.php`
  file anywhere in the tree, `vendor/` excluded. Deliberately not `composer.json`-only: a PHP project that
  hasn't adopted Composer yet should still open this tree — including the `composer` node
  (`skills/refactor-scan/references/php-tooling-tree.md`) that proposes adopting it in the first place.
  Re-derived fresh every pass, so a target that only later becomes a PHP project opens the tree
  retroactively — no separate mechanism needed for that.
- **MR scope:** none — never proposed as a candidate (`tooling_tree.py`'s `_NEVER_PROPOSED`, the same set
  `git` is in). Rejecting a `required` parent by hand never unblocks its children (unlike a `resolved`
  parent — see `structural-scan`'s own node entry,
  `skills/refactor-scan/references/tooling-tree/structural-scan.md`), so there is nothing to gain from a human ever filing an
  `out-of-scope/is-php-project.md` entry in the Refactoring Notes: leaving it unfulfilled already does
  everything a rejection could.
- **Known gap, not fixed by this node:** `php-structural-scan`'s own `resolved` gate
  (`skills/refactor-scan/references/php-tooling-tree.md`) checks each of its thirteen leaves for "fulfilled,
  or explicitly rejected under `out-of-scope/`" — it does not understand a leaf permanently closed by an
  unfulfilled `required` ancestor as a form of resolution. A leaf gated shut by this node (e.g.
  `composer-audit`) therefore counts as neither fulfilled nor rejected there; `structural-scan` still cannot
  open via the PHP path on a non-PHP target without a human filing all thirteen leaf-level rejections by
  hand. This predates `is-php-project` (a target where a human rejected `composer` itself already hit the
  same wall, since `composer`'s own children never even got proposed to reject) and isn't worsened by it.
