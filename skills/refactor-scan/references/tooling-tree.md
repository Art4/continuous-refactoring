# Tooling Tree

The generic root of every language specialization's **tooling tree**. Two ordinary prerequisites (`git`, `loop-config`), one **recognition gate** per language specialization (PHP: `is-php-project`, below — a future CSS/JS specialization adds its own sibling the same way), one ordinary language-neutral first-wave node (`ci-runner`, below), and one downstream gate (`structural-scan`). A recognition gate's *role* is generic — "should this specialization's tree even be reachable on this target" is evaluated fresh every pass regardless of which specializations exist — which is why it lives here rather than in the specialization's own tree doc, even though what a given gate actually detects (PHP files/`composer.json`, for `is-php-project`) is naturally specific to that language. `ci-runner` lives here for a different reason: its content is genuinely language-neutral, but a language tree still references it externally for the language-specific edges hanging off it — the same way `editorconfig` (also below) already works. Everything past a specialization's own recognition gate — its real tooling nodes (PHP: `skills/refactor-scan/references/php-tooling-tree.md`) — attaches beneath that gate instead of beneath `loop-config` directly, and declares its own edges into `structural-scan` itself; this document otherwise stays language-neutral. Vocabulary: `CONTEXT.md` (**node**, **required edge**, **recommended edge**, **tooling tree**).

## Diagram

```mermaid
graph TD
    git[git]
    lc[loop-config]
    ipp[is-php-project]
    ci[ci-runner]
    edc[editorconfig]
    ss[structural-scan]

    git -->|required| lc
    lc -->|required| ipp
    lc -->|required| ci
    lc -->|required| edc
    edc -.->|resolved| ss
    ci -.->|resolved| ss
    ipp -.->|"(language tree's own aggregation node attaches here)"| ss
```

Three dotted edges point into `structural-scan` above. `editorconfig -.->|resolved| ss` and `ci-runner -.->|resolved| ss` are both real — declared in this document's own edge table below, since every endpoint involved is a generic-root node. `is-php-project -.-> ss` (unlabeled) is illustrative only, standing in for the language tree's own aggregation node — the real edge (for PHP: `php-structural-scan -> structural-scan`, see `skills/refactor-scan/references/php-tooling-tree.md`'s edge table) isn't drawn here; it's anchored at `is-php-project` rather than `loop-config` because that's where the PHP tree itself now attaches (its recognition gate), not because `is-php-project` is itself a resolved-parent of `structural-scan` — it isn't, it's a `required` parent of `composer`/`php-minimal-version` only (see its own node entry below). A language specialization's own leaves no longer point directly at `ss` — they resolve into a specialization-owned aggregation node (PHP: `php-structural-scan`) which itself has exactly one `resolved` edge into `ss`. All three kinds use the `resolved` type described under `structural-scan` below, not `required` or `recommended`.

## Edges

| from (parent) | to (child) | type |
|---|---|---|
| `git` | `loop-config` | required |
| `loop-config` | `is-php-project` | required |
| `loop-config` | `ci-runner` | required |
| `loop-config` | `editorconfig` | required |
| `editorconfig` | `structural-scan` | resolved |
| `ci-runner` | `structural-scan` | resolved |

The table above is this document's own — every row here is generic-to-generic (both endpoints live in this document, `structural-scan` included). Ownership rule: an edge belongs to the file where *both* its endpoints already live as generic-root nodes; an edge with one endpoint in a language tree belongs to that language tree's own edge table instead, even when the other endpoint (`editorconfig`, `structural-scan`) lives here. `editorconfig → php-cs-fixer` is declared in `php-tooling-tree.md` under that rule (`php-cs-fixer` is a PHP-tree node). `structural-scan`'s other `resolved` edge is declared in `php-tooling-tree.md` instead: `php-structural-scan → structural-scan`, for the same reason — `php-structural-scan`'s other endpoint is a PHP-tree node, not a generic-root one. `php-structural-scan` is itself the PHP tree's own aggregation of its thirteen leaves; see `php-tooling-tree.md`'s own edge table and `php-structural-scan` node entry for the full picture. A future language specialization attaches the same way — one `<language>-structural-scan` aggregation node, one `resolved` edge into this one — rather than contributing its own leaf count directly here. `editorconfig → structural-scan` and `ci-runner → structural-scan` above are the two `resolved` edges into `structural-scan` that belong here instead, because both endpoints of each — `editorconfig`/`ci-runner` and `structural-scan` itself — are already generic-root nodes.

## Nodes

A node's full definition lives in its own file under `tooling-tree/` (sibling to this document) — this
document's version of the per-node-file split `php-tooling-tree.md` already uses
(`skills/refactor-scan/references/php-tooling-tree/`). Every node also carries a **Name** — the
human-readable label issue titles, merge requests, and chat status use instead of the node's slug. The stub
left behind here keeps Name, Tool, and Purpose inline so that label is available without opening the
extracted file; Fulfilment check, MR scope, and any further node-specific fields move to the extracted file.

### `git`

- **Name:** Git
- **Tool:** git
- **Purpose:** version control — the loop reads history from it and delivers through it.

Full definition (Fulfilment check, MR scope): `skills/refactor-scan/references/tooling-tree/git.md`.

### `loop-config`

- **Name:** Refactoring Config
- **Tool:** none — this is the suite's own state, not a third-party tool.
- **Purpose:** the continuous-refactoring loop's own configuration exists in the target repo, so a pass has somewhere to read/write focus areas and merge-request create-mode.

Full definition (Fulfilment check, MR scope): `skills/refactor-scan/references/tooling-tree/loop-config.md`.

### `is-php-project`

- **Name:** PHP Project Recognition
- **Tool:** none — recognition-only, the tree's own gate, not a third-party tool.
- **Purpose:** a **recognition gate** — hold the PHP specialization's entire tree closed until there's a
  genuine signal the target actually uses PHP, instead of proposing its nodes (`composer` and everything
  beneath it) on every target regardless of language and relying on a human to reject each one by hand as it
  becomes reachable. One gate per specialization; this is the first (a future CSS/JS specialization adds its
  own sibling the same way). The gate's *role* is generic — evaluated fresh every pass, regardless of which
  specializations exist — even though what this particular gate detects is necessarily PHP-specific.

Full definition (Fulfilment check, MR scope, Known gap): `skills/refactor-scan/references/tooling-tree/is-php-project.md`.

### `ci-runner`

- **Name:** CI Runner
- **Tool:** GitHub Actions / GitLab CI
- **Purpose:** an existing pipeline that later hosts quality jobs. Language-neutral — a CI pipeline is
  useful regardless of which language specialization (if any) ends up active, so it stays a direct
  `loop-config` child here rather than gated behind any specialization's recognition gate. Referenced
  externally by `skills/refactor-scan/references/php-tooling-tree.md` for the PHP-specific edges that hang
  off it (`ci-runner → php-minimal-version`, `ci-runner → composer-audit`) — the same way that document
  already references `editorconfig` (below) for `editorconfig → php-cs-fixer`. Also a direct `resolved`
  parent of `structural-scan` (below) in its own right — deterministic tooling settling first (this node's
  whole reason for existing in `structural-scan`'s gate) includes having somewhere for quality jobs to run
  at all, not just the language-specific tools that eventually run inside it.

Full definition (Fulfilment check, MR scope): `skills/refactor-scan/references/tooling-tree/ci-runner.md`.

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

Full definition (Fulfilment check, MR scope): `skills/refactor-scan/references/tooling-tree/editorconfig.md`.

### `structural-scan`

- **Name:** Structural Scan
- **Tool:** none — this node represents the loop's own structural-deepening work (the `refactor-scan`/`refactor-design`/`refactor-implement`/`refactor-review` cycle applied to the target's own code), not a third-party tool.
- **Purpose:** hold structural refactoring back until deterministic tooling has had its say — static analysis and a test suite catch regressions that an agent-driven structural change could otherwise introduce silently. Deterministic tools settle first, agent-driven scanning follows.

Full definition (Fulfilment check, Edge type, MR scope): `skills/refactor-scan/references/tooling-tree/structural-scan.md`.
