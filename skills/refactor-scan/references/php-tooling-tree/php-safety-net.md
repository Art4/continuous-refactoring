# `php-safety-net`

Node on the PHP **tooling tree** (`skills/refactor-scan/references/php-tooling-tree.md`); parents, edges, and the diagram live there. Vocabulary: `CONTEXT.md` (**node**, **required edge**, **recommended edge**, **Safety Net**, **Signal wave**).

- **Name:** PHP Safety Net (internal — never proposed; see below)
- **Tool:** none — pure aggregation node, no fulfilment check or MR scope of its own.
- **Purpose:** the PHP tree's own contribution to `structural-scan`'s gate (`skills/refactor-scan/references/tooling-tree.md`), collapsed into one `resolved` edge instead of nine direct ones — see that document's `structural-scan` node for why (scales to a future second language specialization contributing its own aggregation node the same way). Renamed from `php-structural-scan` — same node, same mechanism, still resolved once its leaves are resolved, still the PHP tree's sole `resolved` contribution to `structural-scan`; new name because other nodes now read its resolved-ness too (the **Signal wave**, below), not just `structural-scan`.
- **Fulfilment check:** every one of its nine `resolved` parents (`psr-4` — `psr-4.md`;
  `phpunit` — `phpunit.md`; `phpstan-level-5` — `phpstan.md`; `rector-dead-code`,
  `rector-type-coverage`, `rector-php-set`, `rector-code-quality`, `rector-phpunit-set`
  — all `rector.md`; `psalm-taint-analysis` — `psalm.md`) is itself resolved — fulfilled, or rejected under
  the Refactoring Notes' `out-of-scope/`. Identical `resolved`-edge semantics to `structural-scan`'s own gate, one
  hop down: a rejected leaf here still counts as resolved. `psalm` is deliberately **not** one of these — see
  its own node entry (`psalm.md`) for why a dedicated leaf for it turned out to be redundant; the
  `phpstan-level-5` leaf's own mutual-exclusion rejection (housekeeping on `psalm`'s own node entry) is what
  actually resolves the PHPStan/Psalm choice for this gate. `test-runner-if-missing` and `php-cs-fixer` no
  longer carry direct `resolved` edges here (see `php-tooling-tree.md`'s own closing prose for the full
  reasoning). `composer-audit` and `phpstan-deprecation-rules` were both leaves once too — both moved to the
  **Signal wave** instead: their findings
  (third-party CVEs; deprecated-API calls) don't have the "could collide with agent-driven structural work"
  property this gate's remaining leaves share, unlike `psalm-taint-analysis`'s own taint-flow findings, which
  do and stays a leaf. `phpmd` and the generic root's `secret-detection` are Signal-producing nodes adjacent
  to this tree that deliberately never became leaves here at all.
- **Signal wave:** this node's own resolved-ness is what several other PHP-tree nodes now wait on instead of
  (or alongside) their own domain-specific required parent — `phpmd`, `coverage-floor`,
  `php-minimal-version`, `phpstan-level-6`, `composer-audit`, and `phpstan-deprecation-rules` keep their
  existing required parent and additionally require this node; `semgrep` requires this node alone (its one
  full-replacement case). See each node's own entry for its exact edge shape, and `CONTEXT.md`'s **Signal
  wave** entry for the vocabulary.
- **MR scope:** none — never proposed, never an MR. There is no real-world action to take *as* `php-safety-net`; the nine leaves above are where the real work happens. `refactor-scan`/`next_candidates()`/`roadmap()` must never surface this node as a candidate — it exists only so `structural-scan`'s own gate can read one edge instead of nine (plus every Signal wave node's own required edge, above).
