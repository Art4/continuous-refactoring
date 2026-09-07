# `php-cs-fixer`

Node on the PHP **tooling tree** (`skills/refactor-scan/references/php-tooling-tree.md`); parents, edges, and the diagram live there. Vocabulary: `CONTEXT.md` (**node**, **required edge**, **recommended edge**).

- **Name:** PHP CS Fixer
- **Tool:** php-cs-fixer
- **Purpose:** automated code style so later Rector output lands styled.
- **Fulfilment check:** dev dependency installed, config committed, runnable locally with zero reported diffs.
- **MR scope:** dependency + config + one formatting pass.
- **Recommended parent:** `editorconfig` — settle the target's most basic formatting conventions
  (indentation, charset, line endings) before this node introduces language-specific style rules. This
  node stays withheld from proposal until `editorconfig` is decided (fulfilled or rejected); a rejected
  `editorconfig` still releases this node, it just goes in without that baseline.
- **Recommended child:** `rector-php-set` (`rector.md`) — waits until this node is decided before it
  becomes proposable, on top of its own required-any static-analyzer parents, so Rector's rewrites
  land on already-styled code. This node no longer carries its own direct `resolved` edge into
  `php-structural-scan` (`php-tooling-tree.md`'s own prose above states why) — this recommended edge
  is what still forces it to be decided before structural work opens, one hop through `rector-php-set`
  → `rector-dead-code`/`rector-code-quality` instead of directly. Reverses an earlier, deliberate
  design choice (`rector-php-set` used to be the one Rector-family node with no `php-cs-fixer`
  recommended parent, "the styling-order exception in the family") — re-decided once the direct edge
  it depended on was itself removed.
