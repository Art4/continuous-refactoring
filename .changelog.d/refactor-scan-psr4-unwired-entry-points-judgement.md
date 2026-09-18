- `refactor-scan`'s tooling-tree step now applies `php-tooling-tree/psr-4.md`'s own judgement call
  before treating a non-empty `unwired_entry_points` result as real unaddressed work: files that never
  reference the target's own PSR-4 root namespace and are self-evidently dev/CI/build utilities are
  exempt. Fixes a false "PSR-4 autoloader not wired" report on targets (e.g. Laravel-style repos) whose
  entry-point sweep also picks up framework config/migration files that were never meant to require
  the autoloader themselves.
