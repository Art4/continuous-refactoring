- The PHP tooling tree's three propose-time stop conditions are now recognition-only gate nodes in the
  shipped tree (`skills/refactor-scan/references/php-tooling-tree.md`), modeled on `is-php-project`:
  `has-real-dependency` (the project has a real, non-platform dependency) gates `composer-audit`,
  `phpstan-baseline-empty` (the current PHPStan baseline is empty) gates every PHPStan level above zero,
  and `phpstan-not-psalm` (PHPStan, not Psalm, is the project's analyzer) gates the first level above
  zero. Each is never proposed — only a required parent carrying a Purpose and an agent-judged
  Fulfilment check in its tree doc — and the graph logic carries no special-case flag for these
  situations any more; what gets proposed on any target is unchanged.
