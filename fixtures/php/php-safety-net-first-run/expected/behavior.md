# Expected behavior — Safety Net Track: first-ever run recording

Confirms a Track with no `## Safety Net` section yet is treated as "never run," not "nothing found" —
and that its very first scan writes `Last scan` even when it turns up nothing missing
(`skills/refactor-learn/references/safety-net-write.md`), so a fully-compliant target still gets its
`Cadence` honored afterward instead of being rescanned every pass.

Not deterministically checkable — the write itself is a skill process behavior, not something
`tooling_tree.py` asserts on its own (the parser never reads or writes `bookkeeping.md`). Run via
`fixtures/harness/run.sh safety-net-track php-safety-net-first-run --opencode`, same non-CI,
local-only, advisory posture as `decision-gate-bypass`.

## Seeded state

Every node in the Safety Net Track's own scope is already resolved: `composer`, `psr-4` (a real
`autoload.psr-4` mapping, `src/Greeter.php` under the mapped `App\` namespace, no entry point so
criterion 2 is vacuous), `ci-runner` (`.github/workflows/ci.yml`), `php-cs-fixer`, `phpunit`
(CI-gated), `phpstan-level-0` (empty baseline — this target's declared ceiling; levels 1–5 explicitly
rejected under `docs/refactoring/out-of-scope/`, which is what actually resolves `php-safety-net`'s own
`phpstan-level-5` leaf), the `rector-*` family (`rector.php` applies all the relevant sets),
`psalm-taint-analysis` (rejected under `out-of-scope/`, no Psalm anywhere). `docs/refactoring/
bookkeeping.md` carries no `## Safety Net` heading at all — this Track has never run on this target.

## Expected: `refactor-scan` pass

Run `/refactor-scan`. It should:

1. Read `bookkeeping.md`, find no `## Safety Net` section, and treat the Track as due (absence means
   "never run," the same as a `Last scan` older than `Cadence`).
2. Walk every node in the Track's scope, judging each against its own Purpose statement (the same
   process `php-safety-net-purpose-recognition` exercises) — find every one already resolved, nothing
   left to propose.
3. Report the Safety Net Track has nothing to propose this pass.

## Expected: `refactor-learn` closing call

1. Create the `## Safety Net` section for the first time: `Cadence: 90`, `Last scan: <today's date>`,
   `Open` and `Out-of-scope` both `- none` — the section is written **even though nothing was found
   missing**, purely to record that the scan ran.
2. Nothing is written to `Fulfilled nodes` or `Pending candidates` on account of this Track's own
   nodes — those fields stay untouched by this write (`skills/refactor-learn/references/
   safety-net-write.md`).

## The behavior this regression-tests

Without an explicit "record even a clean result" rule, a fully-compliant target's Safety Net Track
would look identical before and after its first scan (no section either way, since nothing changed) and
would be rescanned in full every single pass forever, instead of only every `Cadence` days.

## Verified

Not yet manually confirmed live against an opencode model run — see the implementing pull request's
own report for what was attempted and observed.
