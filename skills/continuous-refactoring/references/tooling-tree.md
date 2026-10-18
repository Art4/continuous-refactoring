# Tooling Tree

The prose for the generic Pack's Tools and for the suite's two prerequisites, `git` and `onboarding-setup`. **The edges, the Stages and their order live in `packs/generic/pack.json` now** (`tooling-model.md`); this document and the files under `tooling-tree/` keep what is prose. Paragraphs below that describe edges, parents, children or aggregation nodes describe the model before `tooling-model.md` and are superseded by it; they leave when the Tool files move into the Packs. Vocabulary: `CONTEXT.md`.

## Nodes

A Stage may span several merge requests. Reopening a rejected Stage is reversing its recorded rejection (`rejection.md`, *Reversing*). A Tool's full definition lives in its own file under `tooling-tree/` (sibling to this document), named by the `details` field of the Tool in the Pack. A **Name** is the label tickets, merge requests and reports use instead of the slug, and the stub keeps it with Tool and Purpose so it is at hand without opening the file; Fulfilment check and MR scope are in the file.

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

