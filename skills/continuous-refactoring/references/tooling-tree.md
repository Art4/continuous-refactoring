# Tooling Tree

The generic root of every language specialization's **tooling tree**: two prerequisites the parser settles itself (`git`, `onboarding-setup`), one **recognition gate** per language specialization (PHP: `is-php-project`; a later specialization adds its own sibling), two language-neutral **Safety Net** nodes (`editorconfig`, `ci-runner`), the aggregation node `structural-scan`, and one language-neutral **Guardrails** node behind it (`secret-detection`). A recognition gate lives here because its role is generic — "is this specialization's tree reachable on this target?" is judged in every scan — even though what a given gate detects is specific to its language. A specialization's own nodes (PHP: `php-tooling-tree.md`) attach beneath its gate and reach `structural-scan` through an aggregation node of their own. Vocabulary: `CONTEXT.md` (**node**, **required edge**, **recommended edge**, **tooling tree**, **aggregation node**, **signal**, **Onboarding**, **Safety Net**, **Guardrails**).

## Diagram

```mermaid
graph TD
    git[git]
    lc[onboarding-setup]
    ipp[is-php-project]
    ci[ci-runner]
    edc[editorconfig]
    sd[secret-detection]
    ss[structural-scan]

    git -->|required| lc
    lc -->|required| ipp
    lc -->|required| ci
    lc -->|required| edc
    edc -.->|resolved| ss
    ci -.->|resolved| ss
    ipp -.->|"(language tree's own aggregation node attaches here)"| ss
    ss -->|required| sd
```

Three dotted edges point into `structural-scan` above. `editorconfig -.->|resolved| ss` and `ci-runner -.->|resolved| ss` are both real — declared in this document's own edge table below, since every endpoint involved is a generic-root node. `is-php-project -.-> ss` (unlabeled) is illustrative only, standing in for the language tree's own aggregation node — the real edge (for PHP: `php-safety-net -> structural-scan`, see `php-tooling-tree.md`'s edge table) isn't drawn here; it's anchored at `is-php-project` rather than `onboarding-setup` because that's where the PHP tree itself now attaches (its recognition gate), not because `is-php-project` is itself a resolved-parent of `structural-scan` — it isn't, it's a `required` parent of `composer`/`php-minimal-version` only (see its own node entry below). A language specialization's own leaves no longer point directly at `ss` — they resolve into a specialization-owned aggregation node (PHP: `php-safety-net`) which itself has exactly one `resolved` edge into `ss`. All three kinds use the `resolved` type described under `structural-scan` below, not `required` or `recommended`.

## Edges

| from (parent) | to (child) | type |
|---|---|---|
| `git` | `onboarding-setup` | required |
| `onboarding-setup` | `is-php-project` | required |
| `onboarding-setup` | `ci-runner` | required |
| `onboarding-setup` | `editorconfig` | required |
| `editorconfig` | `structural-scan` | resolved |
| `ci-runner` | `structural-scan` | resolved |
| `structural-scan` | `secret-detection` | required |

The table above is this document's own — every row here is generic-to-generic (both endpoints live in this document, `structural-scan` included). Ownership rule: an edge belongs to the file where *both* its endpoints already live as generic-root nodes; an edge with one endpoint in a language tree belongs to that language tree's own edge table instead, even when the other endpoint (`editorconfig`, `structural-scan`) lives here. `editorconfig → php-cs-fixer` is declared in `php-tooling-tree.md` under that rule (`php-cs-fixer` is a PHP-tree node). `structural-scan`'s other `resolved` edge is declared in `php-tooling-tree.md` instead: `php-safety-net → structural-scan`, for the same reason — `php-safety-net`'s other endpoint is a PHP-tree node, not a generic-root one. `php-safety-net` is itself the PHP tree's own aggregation of its nine leaves; see `php-tooling-tree.md`'s own edge table and `php-safety-net` node entry for the full picture. A future language specialization attaches the same way — one `<language>-safety-net` aggregation node, one `resolved` edge into this one — rather than contributing its own leaf count directly here. `editorconfig → structural-scan` and `ci-runner → structural-scan` above are the two `resolved` edges into `structural-scan` that belong here instead, because both endpoints of each — `editorconfig`/`ci-runner` and `structural-scan` itself — are already generic-root nodes. `structural-scan → secret-detection` also belongs here — both endpoints are generic-root nodes — and is a `required` edge, not `resolved`: `secret-detection` is a **Guardrails** node (`CONTEXT.md`), workable only once `structural-scan` is fulfilled, not one of the nodes that decide *when* it is.

## Nodes

A node's full definition lives in its own file under `tooling-tree/` (sibling to this document) — this
document's version of the per-node-file split `php-tooling-tree.md` already uses
(`php-tooling-tree`). Every node also carries a **Name** — the
human-readable label ticket titles, merge requests, and a run's reports use instead of the node's slug. The stub
left behind here keeps Name, Tool, and Purpose inline so that label is available without opening the
extracted file; Fulfilment check, MR scope, and any further node-specific fields move to the extracted file.

### `git`

- **Name:** Git
- **Tool:** git
- **Purpose:** version control — the suite reads history from it and delivers through it.

Full definition (Fulfilment check, MR scope): `tooling-tree/git.md`.

### `onboarding-setup`

- **Name:** Onboarding Setup
- **Tool:** none — the suite's own prerequisite, not a third-party tool.
- **Purpose:** the target says how the suite reaches its tickets and merge requests, so a run can search the tracker and the forge. Fulfilled by the onboarding interview, the first thing a run checks.

Full definition (Fulfilment check, MR scope): `tooling-tree/onboarding-setup.md`.

### `is-php-project`

- **Name:** PHP Project Recognition
- **Tool:** none — recognition-only, the tree's own gate, not a third-party tool.
- **Purpose:** a **recognition gate** — hold the PHP specialization's entire tree closed until there's a
  genuine signal the target actually uses PHP, instead of proposing its nodes (`composer` and everything
  beneath it) on every target regardless of language and relying on a human to reject each one by hand as it
  becomes reachable. One gate per specialization; this is the first (a future CSS/JS specialization adds its
  own sibling the same way). The gate's *role* is generic — judged again in every scan, regardless of which
  specializations exist — even though what this particular gate detects is necessarily PHP-specific.

Full definition (Fulfilment check, MR scope, Known gap): `tooling-tree/is-php-project.md`.

### `ci-runner`

- **Name:** CI Runner
- **Tool:** GitHub Actions / GitLab CI
- **Purpose:** an existing pipeline that later hosts quality jobs. Language-neutral — a CI pipeline is
  useful regardless of which language specialization (if any) ends up active, so it stays a direct
  `onboarding-setup` child here rather than gated behind any specialization's recognition gate. Referenced
  externally by `php-tooling-tree.md` for the PHP-specific edges that hang
  off it (`ci-runner → php-minimal-version`, `ci-runner → composer-audit`) — the same way that document
  already references `editorconfig` (below) for `editorconfig → php-cs-fixer`. Also a direct `resolved`
  parent of `structural-scan` (below) in its own right — deterministic tooling settling first (this node's
  whole reason for existing in `structural-scan`'s gate) includes having somewhere for quality jobs to run
  at all, not just the language-specific tools that eventually run inside it.

Full definition (Fulfilment check, MR scope): `tooling-tree/ci-runner.md`.

### `editorconfig`

- **Name:** `.editorconfig`
- **Tool:** EditorConfig
- **Purpose:** settle the most basic formatting conventions (indentation, charset, line endings) before a
  language specialization's own style tool introduces language-specific rules — the same way `php-cs-fixer`
  exists so "later Rector output lands styled." Language-independent, so it lives at the generic root and
  its `required` parent (`onboarding-setup`, above) is declared in this document's own edge table. Two outgoing
  edges: `editorconfig → structural-scan` (`resolved`, see `structural-scan` below) stays in this document
  too, since `structural-scan` is itself a generic-root node; only `editorconfig → php-cs-fixer` crosses
  into a language tree (`php-tooling-tree.md`'s edge table: `editorconfig →
  php-cs-fixer` recommended), since `php-cs-fixer` is a PHP-tree node.
  Not a runnable tool: a plain-text convention file, read by any EditorConfig-aware editor.

Full definition (Fulfilment check, MR scope): `tooling-tree/editorconfig.md`.

### `secret-detection`

- **Name:** Secret Detection
- **Tool:** any secret scanner
- **Purpose:** CI-gated protection against committing secrets/credentials — a Signal-producing node
  for the search for structural candidates, not a Safety Net one. Deliberately carries **no** `resolved`
  edge into `structural-scan`, unlike its generic-root siblings `editorconfig`/`ci-runner` above:
  adopting it strengthens candidate selection (the Security signal), it never gates structural work.
  A **Guardrails** node (`CONTEXT.md`): required parent is `structural-scan` itself, not `onboarding-setup`
  — workable only once the Safety Net is fulfilled, so a target's earliest
  runs aren't asked to wire up a secret scanner before `phpunit`/`phpstan` even exist. Language-neutral by nature (reads git
  history/file contents directly), so it lives at the generic root rather than any language
  specialization's own tree — a future language specialization inherits it automatically, no
  re-declaration needed.
  A generic node, like `test-runner-if-missing`'s own `any test runner` (`php-tooling-tree/test-runner-if-missing.md`); a concrete tool (gitleaks, detect-secrets, trufflehog, …) is decided at adoption time, not pinned here.
- **Signal:** Security — `signals.md`'s own entry. Once this
  node is fulfilled, the search for structural candidates reads the scanner's findings as the
  evidence for this factor, in place of the generic (reading-the-code) recognition method.

Full definition (Fulfilment check, MR scope): `tooling-tree/secret-detection.md`.

### `structural-scan`

- **Name:** Structural Scan
- **Tool:** none — an aggregation node, not a third-party tool.
- **Purpose:** the Safety Net's gate — fulfilled once deterministic tooling has had its say: static analysis and a test suite catch regressions that an agent-driven structural change could otherwise introduce silently. Deterministic tools settle first; "is Safety Net fulfilled?" is this node's computed state.

Full definition (Fulfilment check, Edge type, MR scope): `tooling-tree/structural-scan.md`.
