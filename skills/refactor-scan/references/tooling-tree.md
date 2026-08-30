# Tooling Tree

The generic root of every language specialization's **tooling tree**. Two ordinary prerequisites (`git`, `loop-config`) and one downstream gate (`structural-scan`). Language specializations (PHP: `skills/refactor-scan/references/php-tooling-tree.md`) attach their first-wave nodes beneath `loop-config`, not beneath `git` directly, and declare the edges into `structural-scan` themselves — this document stays language-neutral. Vocabulary: `CONTEXT.md` (**node**, **required edge**, **recommended edge**, **tooling tree**).

## Diagram

```mermaid
graph TD
    git[git]
    lc[loop-config]
    edc[editorconfig]
    ss[structural-scan]

    git -->|required| lc
    lc -->|required| edc
    edc -.->|resolved| ss
    lc -.->|"(language tree attaches here)"| ss
```

Two dotted edges point into `structural-scan` above. `editorconfig -.->|resolved| ss` is real — declared in this document's own edge table below, since both endpoints are generic-root nodes. `loop-config -.-> ss` (unlabeled) is illustrative only, standing in for the language tree's own leaf edges — the real ones (for PHP: see `skills/refactor-scan/references/php-tooling-tree.md`'s edge table) aren't drawn here. Both kinds use the `resolved` type described under `structural-scan` below, not `required` or `recommended`.

## Edges

| from (parent) | to (child) | type |
|---|---|---|
| `git` | `loop-config` | required |
| `loop-config` | `editorconfig` | required |
| `editorconfig` | `structural-scan` | resolved |

The table above is this document's own — every row here is generic-to-generic (both endpoints live in this document, `structural-scan` included). Ownership rule: an edge belongs to the file where *both* its endpoints already live as generic-root nodes; an edge with one endpoint in a language tree belongs to that language tree's own edge table instead, even when the other endpoint (`editorconfig`, `structural-scan`) lives here. `editorconfig → php-cs-fixer` is declared in `php-tooling-tree.md` under that rule (`php-cs-fixer` is a PHP-tree node). `structural-scan`'s other seven `resolved` edges — one per PHP-tree leaf — are declared in `php-tooling-tree.md` too, for the same reason: each edge's *other* endpoint is a PHP-tree leaf, not a generic-root node. `editorconfig → structural-scan` above is the one `resolved` edge into `structural-scan` that belongs here instead, because both its endpoints — `editorconfig` and `structural-scan` itself — are already generic-root nodes.

## Nodes

### `git`

- **Name:** Git
- **Tool:** git
- **Purpose:** version control — the loop reads history from it and delivers through it.
- **Fulfilment check:** target is a git repository.
- **MR scope:** never an MR — the only hard requirement; without it the suite does not run. If missing, `refactor-scan` stops the pass immediately and reports it; nothing is filed.

### `loop-config`

- **Name:** Refactoring Config
- **Tool:** none — this is the suite's own state, not a third-party tool.
- **Purpose:** the continuous-refactoring loop's own configuration exists in the target repo, so a pass has somewhere to read/write cadence, last-run date, and create-mode.
- **Fulfilment check:** `docs/refactoring/config.md` exists in the target repo.
- **MR scope:** one MR — create `docs/refactoring/config.md` (see `skills/continuous-refactoring/references/refactoring-config.md` for its shape; there is deliberately no stored cadence — the loop never triggers itself). Ordinary node like any other: `refactor-scan` files it as a single `refactor:candidate` issue when missing, same as a PHP tree node, and it is the only candidate filed that pass.

### `editorconfig`

- **Name:** `.editorconfig`
- **Tool:** none — plain-text convention file, read by any EditorConfig-aware editor, not a runnable tool.
- **Purpose:** settle the most basic formatting conventions (indentation, charset, line endings) before a
  language specialization's own style tool introduces language-specific rules — the same way `php-cs-fixer`
  exists so "later Rector output lands styled." Language-independent, so it lives at the generic root and
  its `required` parent (`loop-config`, above) is declared in this document's own edge table. Two outgoing
  edges: `editorconfig → structural-scan` (`resolved`, see `structural-scan` below) stays in this document
  too, since `structural-scan` is itself a generic-root node; only `editorconfig → php-cs-fixer` crosses
  into a language tree (`skills/refactor-scan/references/php-tooling-tree.md`'s edge table: `editorconfig →
  php-cs-fixer` recommended), since `php-cs-fixer` is a PHP-tree node.
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
  Ordinary node like any other — rejectable as `wontfix` (`docs/refactoring/out-of-scope/editorconfig.md`)
  like any other node, no special carve-out.

### `structural-scan`

- **Name:** Structural Scan
- **Tool:** none — this node represents the loop's own structural-deepening work (the `refactor-scan`/`refactor-design`/`refactor-implement`/`refactor-review` cycle applied to the target's own code), not a third-party tool.
- **Purpose:** hold structural refactoring back until deterministic tooling has had its say — static analysis and a test suite catch regressions that an agent-driven structural change could otherwise introduce silently. Deterministic tools settle first, agent-driven scanning follows.
- **Fulfilment check:** every node with a `resolved` edge into this one is **resolved** — fulfilled, or explicitly rejected and recorded under `docs/refactoring/out-of-scope/`. Most of that leaf set is the active language specialization's own tree (for PHP: `skills/refactor-scan/references/php-tooling-tree.md` declares both the leaf set and the edges). One leaf lives at the generic root instead: `editorconfig` (above), whose `resolved` edge into this node is declared in this document's own edge table, not the language tree's.
- **Edge type — read this carefully, it deviates from the standard rule:** a standard **required edge** closes the child permanently once a parent is rejected. The edges into `structural-scan` do **not** do that: a rejected leaf still counts as resolved and still unblocks this node once every other leaf also reaches a resolved state. This is deliberate — one declined tooling branch (e.g. Rector rejected as not worth it here) should not permanently forbid ever doing structural work. These edges are labelled `resolved`, never `required` or `recommended` — declared in a language tree's own edge table for each language-tree leaf (PHP: `php-tooling-tree.md`), or in this document's own edge table for a generic-root leaf like `editorconfig` (above).
- **MR scope:** never an MR by itself — fulfilling this node just opens the gate. Once open, `refactor-scan` proposes it like any other node name; the actual codebase walk (hot spots, module/interface/depth/seam vocabulary) that turns it into one concrete candidate is `refactor-design`'s job, run only for the node the human actually picked.
