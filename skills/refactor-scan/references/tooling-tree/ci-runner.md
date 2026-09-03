# `ci-runner`

Node on the generic **tooling tree** (`skills/refactor-scan/references/tooling-tree.md`); parents, edges, and the diagram live there. Vocabulary: `CONTEXT.md` (**node**, **required edge**, **recommended edge**).

- **Name:** CI Runner
- **Tool:** GitHub Actions / GitLab CI
- **Purpose:** an existing pipeline that later hosts quality jobs. Language-neutral — a CI pipeline is
  useful regardless of which language specialization (if any) ends up active, so it stays a direct
  `loop-config` child here rather than gated behind any specialization's recognition gate. Referenced
  externally by `skills/refactor-scan/references/php-tooling-tree.md` for the PHP-specific edges that hang
  off it (`ci-runner → php-minimal-version`, `ci-runner → composer-audit`) — the same way that document
  already references `editorconfig`
  (`skills/refactor-scan/references/tooling-tree/editorconfig.md`) for `editorconfig → php-cs-fixer`. Also
  a direct `resolved` parent of `structural-scan`
  (`skills/refactor-scan/references/tooling-tree/structural-scan.md`) in its own right — deterministic
  tooling settling first (this node's whole reason for existing in `structural-scan`'s gate) includes
  having somewhere for quality jobs to run at all, not just the language-specific tools that eventually run
  inside it.
- **Fulfilment check:** CI config file present; forge determined from `git remote`; unknown CI → ask, do not
  record a rejection.
- **MR scope:** pipeline file only. `composer-audit`
  (`skills/refactor-scan/references/php-tooling-tree/composer-audit.md`) is a quality-job child with two
  parents (this node + `composer`). `phpunit` and `phpstan-level-0` do not get their own two-parent
  children — once this node is fulfilled, each self-wires its own CI gate as part of its own fulfilment
  check instead.
