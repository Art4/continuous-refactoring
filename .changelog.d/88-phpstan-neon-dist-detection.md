- `phpstan-level-0` detection now falls back to `phpstan.neon.dist` when `phpstan.neon` is absent
  (PHPStan's own auto-discovery order, already honored elsewhere in this tree for
  `phpunit.xml.dist`/`psalm.xml.dist`/`phpmd.xml.dist`). `phpstan.neon` still wins when both files
  exist. Fixes a false "no level configured" report on targets that only ever committed the `.dist`
  file.
