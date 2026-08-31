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
