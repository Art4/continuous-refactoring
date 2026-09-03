# `editorconfig`

Node on the generic **tooling tree** (`skills/refactor-scan/references/tooling-tree.md`); parents, edges, and the diagram live there. Vocabulary: `CONTEXT.md` (**node**, **required edge**, **recommended edge**).

- **Name:** `.editorconfig`
- **Tool:** none — plain-text convention file, read by any EditorConfig-aware editor, not a runnable tool.
- **Purpose:** settle the most basic formatting conventions (indentation, charset, line endings) before a
  language specialization's own style tool introduces language-specific rules — the same way `php-cs-fixer`
  exists so "later Rector output lands styled." Language-independent, so it lives at the generic root and
  its `required` parent (`loop-config`,
  `skills/refactor-scan/references/tooling-tree/loop-config.md`) is declared in `tooling-tree.md`'s own edge
  table. Two outgoing edges: `editorconfig → structural-scan` (`resolved`, see `structural-scan`'s own node
  entry, `skills/refactor-scan/references/tooling-tree/structural-scan.md`) stays declared in
  `tooling-tree.md` too, since `structural-scan` is itself a generic-root node; only `editorconfig →
  php-cs-fixer` crosses into a language tree (`skills/refactor-scan/references/php-tooling-tree.md`'s edge
  table: `editorconfig → php-cs-fixer` recommended), since `php-cs-fixer` is a PHP-tree node.
- **Fulfilment check:** `.editorconfig` exists at the repo root. Pure presence check, no tool run, no
  equivalent-detection nuance.
- **MR scope:** create a default `.editorconfig` when missing — one language-neutral `[*]` section, no
  per-language stanza:
  ```
  root = true

  [*]
  charset = utf-8
  end_of_line = lf
  insert_final_newline = true
  trim_trailing_whitespace = true
  indent_style = space
  indent_size = 4
  ```
  Ordinary node like any other — rejectable as `wontfix` (an `out-of-scope/editorconfig.md` entry in the
  Refactoring Notes) like any other node, no special carve-out.
