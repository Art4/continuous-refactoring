# `is-php-project`

Node on the generic **tooling tree** (`../tooling-tree.md`); parents, edges, and the diagram live there. Vocabulary: `CONTEXT.md` (**node**, **required edge**, **recommended edge**).

- **Name:** PHP Project Recognition
- **Tool:** none — recognition-only, the tree's own gate, not a third-party tool.
- **Purpose:** a **recognition gate** — hold the PHP specialization's entire tree closed until there's a
  genuine signal the target actually uses PHP, instead of proposing its nodes (`composer` and everything
  beneath it) on every target regardless of language and relying on a human to reject each one by hand as it
  becomes reachable. One gate per specialization; this is the first (a future CSS/JS specialization adds its
  own sibling the same way). The gate's *role* is generic — judged again in every scan, regardless of which
  specializations exist — even though what this particular gate detects is necessarily PHP-specific.
- **Fulfilment check:** `composer.json` (or `composer/composer.json`) present, **or** at least one `*.php`
  file anywhere in the tree, `vendor/` excluded. Deliberately not `composer.json`-only: a PHP project that
  hasn't adopted Composer yet should still open this tree — including the `composer` node
  (`../php-tooling-tree.md`) that proposes adopting it in the first place.
  Judged again in every scan, so a target that only later becomes a PHP project opens the tree
  then — no separate mechanism needed for that.
- **MR scope:** none — recognition-only, never a ticket. Declining it would gain nothing: a rejected
  `required` parent never unblocks its children (unlike a `resolved` parent — see `structural-scan`'s own
  node entry, `structural-scan.md`), and leaving it unfulfilled already does everything a rejection could.
- **Known gap, not fixed by this node:** on a target that is not a PHP project the PHP leaves wait behind
  this node, neither fulfilled nor rejected. A scan names them as out of reach and files no ticket for
  them, and `php-safety-net` (`../php-tooling-tree.md`) stays unfulfilled, and with it `structural-scan`:
  Safety Net never comes out of a scan as fulfilled on such a target, so an autonomous run that scanned
  stops there and a human chooses the Track. The same gap keeps the PHP-specific **Guardrails** nodes (`phpmd`, `coverage-floor`,
  `php-minimal-version`, `phpstan-level-6`, `composer-audit`, `phpstan-deprecation-rules`, `semgrep`)
  closed on such a target with no further mechanism: `php-safety-net` can only be fulfilled through this
  node's own recognition path.
