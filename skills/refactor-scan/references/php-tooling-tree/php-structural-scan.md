# `php-structural-scan`

Node on the PHP **tooling tree** (`skills/refactor-scan/references/php-tooling-tree.md`); parents, edges, and the diagram live there. Vocabulary: `CONTEXT.md` (**node**, **required edge**, **recommended edge**).

- **Name:** PHP Structural Scan (internal — never proposed; see below)
- **Tool:** none — pure aggregation node, no fulfilment check or MR scope of its own.
- **Purpose:** the PHP tree's own contribution to `structural-scan`'s gate (`skills/refactor-scan/references/tooling-tree.md`), collapsed into one `resolved` edge instead of thirteen direct ones — see that document's `structural-scan` node for why (scales to a future second language specialization contributing its own aggregation node the same way).
- **Fulfilment check:** every one of its thirteen `resolved` parents (`composer-audit` — `composer-audit.md`;
  `phpunit` — `phpunit.md`; `test-runner-if-missing` — `test-runner-if-missing.md`; `php-cs-fixer` —
  `php-cs-fixer.md`; `phpstan-level-10`, `phpstan-deprecation-rules` — both `phpstan.md`; `rector-dead-code`,
  `rector-type-coverage`, `rector-php-set`, `rector-code-quality`, `rector-phpunit-set`, `rector-early-return`
  — all `rector.md`; `psalm-taint-analysis` — `psalm.md`) is itself resolved — fulfilled, or rejected under
  `docs/refactoring/out-of-scope/`. Identical `resolved`-edge semantics to `structural-scan`'s own gate, one
  hop down: a rejected leaf here still counts as resolved. `psalm` is deliberately **not** one of these — see
  its own node entry (`psalm.md`) for why a dedicated leaf for it turned out to be redundant; the
  `phpstan-level-10` leaf's own mutual-exclusion rejection (housekeeping on `psalm`'s own node entry) is what
  actually resolves the PHPStan/Psalm choice for this gate.
- **MR scope:** none — never proposed, never an MR. There is no real-world action to take *as* `php-structural-scan`; the thirteen leaves above are where the real work happens. `refactor-scan`/`next_candidates()`/`roadmap()` must never surface this node as a candidate — it exists only so `structural-scan`'s own gate can read one edge instead of thirteen.
