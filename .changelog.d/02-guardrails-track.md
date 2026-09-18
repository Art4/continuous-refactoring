- Guardrails Track: `refactor-scan` now judges a Guardrails Track node's Fulfilment check against its
  own Purpose statement, the same mechanism ticket 01 established for the Safety Net, applied to the
  seven nodes required on `structural-scan`/`php-safety-net` themselves (`composer-audit`, `phpmd`,
  `coverage-floor`, `php-minimal-version`, `phpstan-level-6` and above, `phpstan-deprecation-rules`,
  `semgrep`) — proposed only once the Safety Net has closed. `bookkeeping.md` gains a `## Guardrails`
  section (`Cadence: 60`, `Last scan`, `Open`, `Out-of-scope`), independent of `## Safety Net`;
  `refactor-learn` writes into it with the identical merge/rejection symmetry
  `safety-net-write.md` already established. A repo mid-migration — `## Safety Net` already closed, `##
  Guardrails` never run — runs a normal pass, unaffected.
