# Expected behavior — Track scheduler, staleness-ratio selection

The orchestrator's own new Track-selection step (`skills/continuous-refactoring/SKILL.md` step 0b,
algorithm in `skills/continuous-refactoring/references/track-scheduler.md`) computing real competition
between two wired Tracks, spec Testing Decision #2 ("Track selection under simple staleness"): a
`bookkeeping.md` with Safety Net and Guardrails at different staleness ratios, neither holding `Open`
work — expect the most-overdue eligible Track selected, not simply the fixed-tie-break winner.

Not deterministically checkable via `tooling_tree.py` — the parser has no notion of Tracks or
scheduling at all; this is a behavioral property of `continuous-refactoring/SKILL.md` and
`track-scheduler.md`, checked the same non-CI, local-only, advisory way `safety-net-track`/
`guardrails-track` already are. Run via `fixtures/harness/run.sh scheduler
php-scheduler-staleness-selection --opencode`.

## Seeded state

The Safety Net is fully closed: `composer`, `psr-4` (`src/Greeter.php` under the mapped `App\`
namespace), `ci-runner` (`.github/workflows/ci.yml`), `php-cs-fixer`, `phpunit` (CI-gated),
`phpstan-level-5` (`phpstan.neon`'s declared level 5, empty baseline), the `rector-*` family
(`rector.php` applies every relevant set), `psalm-taint-analysis` (rejected under `out-of-scope/`) —
`php-safety-net` resolves, making every Guardrails node reachable. No Guardrails node is adopted:
`composer-audit`, `phpmd`, `coverage-floor`, `php-minimal-version`, `phpstan-level-6`,
`phpstan-deprecation-rules`, `semgrep` are all genuinely missing.

`docs/refactoring/bookkeeping.md`:

- `## Safety Net` — `Cadence: 90`, `Last scan: 2026-06-16` (95 days before this fixture's reference
  date of 2026-09-19 → `overdue_ratio ≈ 1.056`, just past due), `Open` list `- none`.
- `## Guardrails` — `Cadence: 60`, `Last scan: 2026-04-22` (150 days before 2026-09-19 →
  `overdue_ratio = 2.5`, far more overdue), `Open` list `- none`.

Both Tracks are due (`overdue_ratio >= 1`) and eligible (`Open` empty for both) — a genuine competition,
not a tie: Guardrails' ratio (2.5) is more than double Safety Net's (≈1.056). The fixed tie-break order
(Safety Net > Guardrails > Housekeeping > Investigation) only applies to a tie or to un-comparable
"never run" Tracks — it must **not** override a real staleness difference like this one.

## Expected: `continuous-refactoring` pass, Track-selection step

Run the orchestrator's Track-selection step (step 0b), then hand off to `refactor-scan` for that Track
only — stop there, don't continue through design/implement. It should:

1. Read both `## Safety Net` and `## Guardrails`, compute each `overdue_ratio`.
2. Recognize both are due and eligible (`Open` empty for both).
3. **Select Guardrails** — its ratio (2.5) is higher than Safety Net's (≈1.056), even though Safety Net
   outranks Guardrails in the fixed tie-break order. This is the core assertion: ratio wins over fixed
   order whenever it's a genuine, non-tied comparison.
4. Hand the Guardrails Track to `refactor-scan` as an explicit input; `refactor-scan` runs
   `guardrails-track.md`'s own process and proposes the genuinely-missing Guardrails nodes (at least
   one of `composer-audit`, `phpmd`, `coverage-floor`, `php-minimal-version`, `phpstan-level-6`,
   `phpstan-deprecation-rules`, `semgrep`).
5. Safety Net's own section is left untouched this pass (still due, just not selected) — no write to
   `## Safety Net` should happen.

## The bug this regression-tests

Before ticket 04, `refactor-scan` decided Safety-Net-due-ness for itself, with no cross-Track
comparison at all (tickets 01/02's own "temporary" per-Track due-check) — there was no mechanism that
could ever pick Guardrails over Safety Net on staleness grounds, or indeed compare the two at all. This
fixture is the first regression test of the actual competition ticket 04 adds.

## Verified

Confirmed live via `OPENCODE_TIMEOUT=280 fixtures/harness/run.sh scheduler
php-scheduler-staleness-selection --opencode` (`opencode/muse-spark-1.2-contributor-free`) — see the
implementing pull request's own report for the transcript summary.
