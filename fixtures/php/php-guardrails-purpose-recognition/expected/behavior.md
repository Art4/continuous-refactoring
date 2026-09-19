# Expected behavior — Guardrails Track purpose-based recognition

The Guardrails Track's own regression case for the same mechanism ADR-0055 established for the Safety
Net (`docs/adr/0055-purpose-based-fulfilment-and-scheduled-tracks.md`,
`fixtures/php/php-safety-net-purpose-recognition`): a target whose CI genuinely gates on `composer
audit` — just invoked indirectly, through a `composer.json` script — should never be proposed
`composer-audit` just because `tooling_tree.py`'s literal CI-text match doesn't follow the
indirection.

Not deterministically checkable via `tooling_tree.py` — that parser still reports `composer-audit`
`fulfilled: false` here (no literal `composer audit` substring in any CI workflow file), on purpose:
the fix under test is that `refactor-scan`'s own Guardrails Track step no longer takes that raw value
at face value for a node in its scope
(`skills/refactor-scan/references/guardrails-track.md`). Run via `fixtures/harness/run.sh
guardrails-track php-guardrails-purpose-recognition --opencode`, same non-CI, local-only, advisory
posture as `safety-net-track`/`decision-gate-bypass`/`judge`/`lift`.

## Seeded state

The Safety Net is fully closed: `composer`, `psr-4` (`src/Greeter.php` under the mapped `App\`
namespace), `ci-runner` (`.github/workflows/ci.yml`), `php-cs-fixer`, `phpunit` (CI-gated),
`phpstan-level-5` (`phpstan.neon`'s declared level 5, empty baseline — this also leaves levels 0–5 all
fulfilled), the `rector-*` family (`rector.php` applies every relevant set), `psalm-taint-analysis`
(rejected under `out-of-scope/`, no Psalm anywhere) — `php-safety-net` resolves, making every
Guardrails node reachable.

`composer.json` declares a `scripts.security-check` entry whose command is literally `composer audit`,
and `.github/workflows/ci.yml` invokes it as `composer run security-check` — the literal substring
`composer audit` never appears in any CI workflow file, only inside `composer.json`, which
`tooling_tree.py`'s own CI-gate check never reads. `composer.json`'s `require` also names a real
dependency (`monolog/monolog`), satisfying `composer-audit`'s own "at least one real dependency" stop
condition.

Every other Guardrails node is genuinely still missing here: no `phpmd/phpmd` dependency or ruleset
config (`phpmd`), no `.coverage-floor` file (`coverage-floor`), `composer.json`'s declared PHP floor
(`^8.1`) is below what `rector-php-set` has actually applied (`UP_TO_PHP_82`, `php-minimal-version`),
`phpstan.neon`'s declared level (5) hasn't reached 6 (`phpstan-level-6`), no
`phpstan/phpstan-deprecation-rules` dependency (`phpstan-deprecation-rules`), and no CI step invokes
`semgrep` (`semgrep`) — this fixture only regression-tests the one judgement call, not a change to
anything else in scope.

## Expected: `refactor-scan` pass

Run `/refactor-scan`. It should:

1. Run `tooling_tree.py` (or the manual tree-walk fallback) and note `composer-audit` comes back
   `fulfilled: false`.
2. Per the Guardrails Track's own judgement step, read `composer-audit`'s Purpose line ("dependency
   vulnerability visibility, enforced as a CI gate") and judge the actual repo against it — not the
   raw CI-text match alone.
3. Recognize that CI genuinely gates on `composer audit`, just invoked via `composer run
   security-check` rather than the literal command — the same real, working check, one level of
   indirection away.
4. **Never propose `composer-audit`** as a candidate this pass, or any future pass, while the script
   stays wired this way.
5. Every other Guardrails node genuinely missing here (`phpmd`, `coverage-floor`,
   `php-minimal-version`, `phpstan-level-6`, `phpstan-deprecation-rules`, `semgrep`) is still proposed
   normally.

## The bug this regression-tests

Before this change, `refactor-scan` step 4 took `tooling_tree.py`'s `fulfilled: false` for
`composer-audit` at face value and proposed it regardless of the already-working, indirectly-invoked
CI gate — risking a second, redundant `composer audit` invocation wired directly into CI on top of the
one already running through the composer script.

## Verified

Confirmed live via `OPENCODE_TIMEOUT=280 fixtures/harness/run.sh guardrails-track
php-guardrails-purpose-recognition --opencode` (`opencode/muse-spark-1.2-contributor-free`): the model
read `guardrails-track.md`'s own working example, recognized the `composer.json` script indirection,
and self-reported `FULFILLED` — `composer-audit` never proposed, every other genuinely-missing
Guardrails node still proposed by Name. See the implementing pull request's own report for the full
transcript summary.
