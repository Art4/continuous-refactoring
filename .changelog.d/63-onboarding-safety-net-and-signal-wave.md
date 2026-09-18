- `php-structural-scan` renamed `php-safety-net`. `CONTEXT.md` gains **Onboarding** (the bounded
  phase before `structural-scan` opens) and its narrower **Safety Net**, plus a new **Signal wave**:
  `composer-audit`/`phpstan-deprecation-rules` move out of the PHP Safety Net into the Signal wave
  (gated on `php-safety-net` closing, in addition to their existing required parent, so a rejected
  parent still permanently closes them); `phpmd`/`coverage-floor`/`php-minimal-version`/
  `phpstan-level-6` join the Signal wave the same additive way; `semgrep` is fully repointed onto
  `php-safety-net` alone (its old `composer` required parent dropped); the generic root's
  `secret-detection` now waits for `structural-scan` itself to open instead of proposing from the
  very first pass. `composer-audit`/`semgrep` also gain a Housekeeping-line fulfilment fallback (a
  committed `housekeeping-template.md` line naming the node, no CI run required).
