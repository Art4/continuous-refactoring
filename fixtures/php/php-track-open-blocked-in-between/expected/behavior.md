# Expected behavior — Track Open: blocked node in between

Confirms `refactor-scan`'s own `Open` walk
(`skills/refactor-scan/references/track-open-processing.md`) skips non-workable nodes with a
reason and continues walking to collect them for the pass report, even after finding a workable node.

Not deterministically checkable via `tooling_tree.py` — checked the same non-CI, local-only,
advisory way `safety-net-track`/`guardrails-track` already are. Run via
`fixtures/harness/run.sh safety-net-track php-track-open-blocked-in-between --opencode`.

## Seeded state

`composer.json` — only `php` itself required, no dev dependencies:
`composer`/`psr-4` read fulfilled (ordinary small namespaced project), but `phpunit`, `php-cs-fixer`,
`phpstan-level-0`, `test-runner-if-missing`, `ci-runner` are all genuinely missing. `static-code-analyzer`
is also missing, which blocks `phpstan-level-0` (required parent per `php-tooling-tree.md`).

`.scratch/refactor/bookkeeping.md`'s `## Safety Net` section: `Last scan: 2026-01-01`, `Open` as a list:
- `phpunit (#6)` — workable (no required parent blocking it)
- `phpstan-level-0 (#7)` — blocked by `static-code-analyzer` (required parent not fulfilled)
- `php-cs-fixer (#5)` — workable (recommended parent `editorconfig` not yet decided, but
  recommended edges don't block — only required edges do)

## Expected: `refactor-scan` pass

Run `/refactor-scan` with the Safety Net Track selected. It should:

1. Read `## Safety Net`'s `Open` list — three entries.
2. Walk the list top to bottom per `skills/refactor-scan/references/track-open-processing.md`:
   - **phpunit (#6)** — workable (unblocked, no `needs-info`, no PHP floor). Re-run Fulfilment:
     not fulfilled (no `phpunit/phpunit` dependency, no CI workflow). → Work this node: hand it to
     `refactor-design` (which files its issue; the walk files nothing).
   - **phpstan-level-0 (#7)** — **not workable**: blocked by `static-code-analyzer` (required parent
     not fulfilled). → Skip, collect with reason for pass report.
   - **php-cs-fixer (#5)** — workable but **not worked**: exactly one node is worked per pass.
     (The walk continues to collect skipped nodes but does not work a second node.)
3. The closing report's **Status** line must mention the skipped node: "phpstan-level-0 (blocked by
   static-code-analyzer)".
4. Only `phpunit` has a merge request opened for it — `phpstan-level-0` and `php-cs-fixer` do not.

## The behavior this regression-tests

Without the walk collecting skipped nodes after finding the worked one, the pass report would be
incomplete — a human reviewing the report wouldn't know why phpstan-level-0 wasn't worked even
though it appeared in `Open`.

## Verified

Not yet manually confirmed live against an opencode model run — see the implementing pull request's
own report for what was attempted and observed.
