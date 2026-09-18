# Expected behavior — Safety Net Track purpose-based recognition

This fixture is the concrete regression case ADR-0055 (`docs/adr/0055-purpose-based-fulfilment-and-scheduled-tracks.md`)
was raised against: a target already running Laravel Pint should never be proposed `php-cs-fixer`
just because `tooling_tree.py`'s dependency-name matching doesn't recognize Pint by name.

Not deterministically checkable via `tooling_tree.py` — that parser still reports `php-cs-fixer`
`fulfilled: false` here (no `friendsofphp/php-cs-fixer` dependency), on purpose: the fix under test is
that `refactor-scan`'s own Safety Net Track step no longer takes that raw value at face value for a
node in its scope (`skills/refactor-scan/references/safety-net-track.md`). Run via
`fixtures/harness/run.sh safety-net-track php-safety-net-purpose-recognition --opencode`, same
non-CI, local-only, advisory posture as `decision-gate-bypass`/`judge`/`lift`.

## Seeded state

`composer.json`/`composer.lock` — `require-dev.laravel/pint`, no `friendsofphp/php-cs-fixer` anywhere
in the tree; `composer`, `psr-4` (`src/Greeter.php` under the mapped `App\` namespace),
`static-code-analyzer` (its own Fulfilment check only needs `composer` fulfilled) all read fulfilled
via the deterministic parser as a result — no PSR-4/mapping trickery involved, just an ordinary small
project. `pint.json` — a committed Pint config (`{"preset": "psr12"}`). No CI workflow, no PHPUnit, no
PHPStan/Psalm — `ci-runner`, `phpunit`, `test-runner-if-missing`, `phpstan-level-0` are genuinely still
missing, so this fixture isn't "Track fully clean" (`php-safety-net-first-run` covers that) — only the
one node under test, `php-cs-fixer`, has anything nonstandard about it.

## Expected: `refactor-scan` pass

Run `/refactor-scan`. It should:

1. Run `tooling_tree.py` (or the manual tree-walk fallback) and note `php-cs-fixer` comes back
   `fulfilled: false`.
2. Per the Safety Net Track's own judgement step, read `php-cs-fixer`'s Purpose line ("automated code
   style so later Rector output lands styled") and judge the actual repo against it — not the raw
   `Tool:` name.
3. Recognize Laravel Pint (`laravel/pint` installed, `pint.json` committed) as genuinely serving that
   Purpose — Pint wraps PHP CS Fixer internally.
4. **Never propose `php-cs-fixer`** as a candidate this pass, or any future pass, while Pint stays
   configured this way.
5. Every other Safety Net Track node still genuinely missing here (`phpunit`,
   `test-runner-if-missing`, `phpstan-level-0`/`static-code-analyzer`, `psr-4`, `ci-runner`) is still
   proposed normally — this fixture only regression-tests the one judgement call, not a change to
   anything else in scope.

## The bug this regression-tests

Before this change, `refactor-scan` step 4 took `tooling_tree.py`'s `fulfilled: false` for
`php-cs-fixer` at face value and proposed it regardless of Pint's presence — risking a second,
separately-configured style tool that could collide with Pint's own formatting decisions.

## Verified

Not yet manually confirmed live against an opencode model run — see the implementing pull request's
own report for what was attempted and observed.
