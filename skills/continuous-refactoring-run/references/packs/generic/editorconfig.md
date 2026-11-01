# .editorconfig

The Tool for the Role Editor Settings in the generic Pack: EditorConfig. Not a runnable tool, a plain-text convention file any EditorConfig-aware editor reads. Language-neutral, so it is in the generic Pack.

**Why this order.** It settles the most basic formatting conventions (indentation, charset, line endings) before a language's own style tool adds language-specific rules, the same way PHP CS Fixer exists so that later Rector output lands styled. PHP CS Fixer waits until this Stage is decided; a rejection releases it, and it goes in without that baseline.

### `editorconfig`

- **Purpose:** settle the most basic formatting conventions before a language's own style tool adds its rules.
- **Fulfilment check:** `.editorconfig` exists at the repo root. A pure presence check: no tool run, no equivalent to look for.
- **MR scope:** create a default `.editorconfig` when missing, one language-neutral `[*]` section and no per-language stanza:
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
  It can be declined like any other Stage.
