# Expected behavior — Guardrails Track first-ever run recording

Confirms a Track with no `## Guardrails` section yet is treated as "never run," not "nothing found" —
and that its very first scan writes `Last scan` even when it turns up nothing missing
(`skills/refactor-learn/references/guardrails-write.md`), so a fully-compliant target still gets its
`Cadence` honored afterward instead of being rescanned every pass. The Guardrails Track's own
counterpart to `fixtures/php/php-safety-net-first-run`.

Not deterministically checkable — the write itself is a skill process behavior, not something
`tooling_tree.py` asserts on its own (the parser never reads or writes `bookkeeping.md`). Run via
`fixtures/harness/run.sh guardrails-track php-guardrails-first-run --opencode`, same non-CI,
local-only, advisory posture as `safety-net-track`/`decision-gate-bypass`.

## Seeded state

Every node in the Guardrails Track's own scope is already resolved. The Safety Net is fully closed
(`## Safety Net` already present and empty — `psr-4`, `ci-runner`, `php-cs-fixer`, `phpunit`,
`test-runner-if-missing`, `phpstan-level-0`, the `rector-*` family all fulfilled; PHPStan levels 1–10
and `psalm-taint-analysis` rejected under `out-of-scope/`, the same "declared ceiling level 0"
resolution `php-clean` already uses). Of the seven Guardrails nodes: `composer-audit` (CI gate
literally invokes `composer audit`), `phpmd` (dependency + `phpmd.xml`), `coverage-floor` (`<coverage>`
section, `.coverage-floor` committed, CI-gated), `php-minimal-version` (declared floor `^8.2` already
matches what `rector-php-set` applied), and `semgrep` (CI step with the OWASP Top 10 ruleset) are all
genuinely fulfilled; `phpstan-level-6` and `phpstan-deprecation-rules` are effectively rejected —
closed the same cascading way `phpstan-level-1`'s own explicit rejection closes every level above it,
confirmed directly against `tooling_tree.py`: both come back outside `next` even though their own raw
`fulfilled` flag reads `false`. `docs/refactoring/bookkeeping.md` carries `## Safety Net` but no `##
Guardrails` heading at all — this Track has never run on this target.

## Expected: `refactor-scan` pass

Run `/refactor-scan`. It should:

1. Read `bookkeeping.md`, find no `## Guardrails` section, and treat the Track as due (absence means
   "never run," the same as a `Last scan` older than `Cadence`).
2. Walk every node in the Track's scope, judging each against its own Purpose statement — find every
   one already resolved (fulfilled or effectively rejected), nothing left to propose.
3. Report the Guardrails Track has nothing to propose this pass.

## Expected: `refactor-learn` closing call

1. Create the `## Guardrails` section for the first time: `Cadence: 60`, `Last scan: <today's date>`,
   `Open` and `Out-of-scope` both `- none` — written **even though nothing was found missing**, purely
   to record that the scan ran.
2. Nothing is written to `Pending candidates` on account of this Track's own
   nodes — those fields, and `## Safety Net`'s own section, stay untouched by this write
   (`skills/refactor-learn/references/guardrails-write.md`).

## The behavior this regression-tests

Without an explicit "record even a clean result" rule, a fully-compliant target's Guardrails Track
would look identical before and after its first scan (no section either way, since nothing changed)
and would be rescanned in full every single pass forever, instead of only every `Cadence` days.

## Verified

Confirmed live via `OPENCODE_TIMEOUT=280 fixtures/harness/run.sh guardrails-track
php-guardrails-first-run --opencode` (`opencode/muse-spark-1.2-contributor-free`), after one real fix
this run surfaced: `refactor-learn/SKILL.md`'s own closing-call precondition (pre-existing, shared with
the Safety Net Track, `skills/refactor-learn/SKILL.md`) only listed "a freshly opened MR" or "a
design-time breaking-change finding" as precondition-satisfying events, with no clause covering "a
Track's scan ran and found nothing to propose" — so a strictly literal reading stopped the closing call
before it ever reached `guardrails-write.md`'s own "`Last scan` regardless" write, contradicting
ADR-0055's own stated rule. Fixed by adding a third precondition clause naming a Safety Net/Guardrails
Track's own scan having run this pass as itself a genuine, sufficient event — narrowly scoped to
authorize only that one write, nothing else. After the fix, the model wrote
`## Guardrails` with `Cadence: 60`, `Last scan: <today>`, `Open`/`Out-of-scope` both `- none`. See the
implementing pull request's own report for the full transcript summary and the judgement call on why
this fix was made in this PR rather than deferred.
