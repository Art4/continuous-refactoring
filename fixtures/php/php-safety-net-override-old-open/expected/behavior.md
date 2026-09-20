# Expected behavior — Safety Net Track: manual override corrects an old-meaning `Open`

Confirms that a `## Safety Net` section still written under the **old** `Open` meaning (only nodes
that had a filed issue, with issue numbers) neither errors nor gets migrated, and that a pass which
**names the Track explicitly** (the manual Track override) runs an immediate scan that rewrites `Open`
as the complete backlog — every unresolved scope node in the script's order, blocked ones included —
and records `Last scan`. Spec case 10 of `agent-judged-fulfilment` (the "forced rescan via override"
half; the old-schema pass-through half is covered by `php-safety-net-old-schema` and
`php-guardrails-old-schema`), and the last item of ticket 06
(`skills/continuous-refactoring/references/refactoring-bookkeeping.md`, `docs/adr/0056-agent-judged-fulfilment.md`).

Not deterministically checkable end to end — the fulfilment judgement and the bookkeeping write are
agent behavior. The ordered list below *is* deterministic given the seed and was computed with
`tooling_tree.py`. Run via `fixtures/harness/run.sh safety-net-track php-safety-net-override-old-open
--opencode`, same non-CI, local-only, advisory posture as `safety-net-track`.

## Seeded state

The project matches `php-guardrails-old-schema`'s except PHPStan runs at **level 0** (empty baseline),
so `phpstan-level-1` through `-5` are unresolved; `psalm-taint-analysis` is already rejected under
`out-of-scope/`. Composer, PSR-4, PHP CS Fixer, PHPUnit, CI and the `rector-*` family are in place.

`docs/refactoring/bookkeeping.md` is written under the old meaning:

- `## Safety Net` — `Cadence: 90`, `Last scan: 2026-09-10` (`overdue_ratio ≈ 0.1`, not due),
  **`Open: phpstan-level-1 (#7)`** — the one node an earlier pass filed an issue for, the old meaning of
  `Open`; the other unresolved nodes are not listed. `Out-of-scope: psalm-taint-analysis —
  out-of-scope/psalm-taint-analysis.md`.
- Old-schema residue: `Focus areas: none` and a `Fulfilled nodes` list (`loop-config`, `composer`,
  `ci-runner`, `psr-4`, `php-cs-fixer`, `phpunit`, `phpstan-level-0`, the `rector-*` family) — ignored.
- No `## Guardrails`/`## Housekeeping`/`## Investigation` sections.

Seed the scan is expected to hand the script (every node fulfilled except `phpstan-level-1..10`,
`phpstan-deprecation-rules`, `composer-audit`, `phpmd`, `coverage-floor`, `php-minimal-version`,
`semgrep`, `structural-scan`, `psalm-taint-analysis` and the gate `php-safety-net`), and the script's
output for it (`python3 skills/refactor-scan/references/tooling_tree.py --seed <seed>
<fixture-project>`): `next` is `phpstan-level-1` alone; `phpstan-level-2` through `-5` are withheld,
each blocked by its predecessor in the chain. The Safety Net scope's part of the raw `backlog` (the
rest — Guardrails nodes, `structural-scan`, the plumbing node `php-safety-net` — belongs to other
Tracks): `phpstan-level-1`, `phpstan-level-2`, `phpstan-level-3`, `phpstan-level-4`, `phpstan-level-5`.

## Expected: a pass invoked as "run the Safety Net Track"

1. The old-shape fields (`Focus areas`, `Fulfilled nodes`, the old-meaning `Open`) cause **no error**
   and no migration step; `Fulfilled nodes` is simply not consulted.
2. The Track is named explicitly, so it runs this pass unconditionally, bypassing ordinary selection.
   Because the named Track is scanned immediately, `Last scan`'s recency (not due) does not hold it
   back, and the incomplete old-meaning `Open` is not resumed as if it were the whole backlog.
3. `refactor-scan` judges every Safety Net scope node against its Purpose and hands the seed to the
   script.
4. `refactor-learn`'s closing call rewrites `## Safety Net`:
   - `Open` = `phpstan-level-1`, `phpstan-level-2`, `phpstan-level-3`, `phpstan-level-4`,
     `phpstan-level-5`, in that order — the four blocked levels present, not omitted. The old `(#7)`
     number stays only if the node is actually being worked this pass; otherwise it is dropped.
   - `Last scan` set to today's date; `Out-of-scope` unchanged.
   - `Fulfilled nodes` and `Focus areas` left exactly as they were (never migrated or removed).

## Note on the scheduler docs

`skills/continuous-refactoring/references/track-scheduler.md`'s *Manual override* section and
`skills/refactor-scan/references/safety-net-track.md`'s *Is the Track due this pass?* currently say a
manually named Track with a non-empty `Open` still works that `Open` entry and is never rescanned,
whereas `refactoring-bookkeeping.md`, ADR-0056 and ticket 06 say an old-meaning `Open` is corrected by
"an immediate scan via the Track override". This fixture pins the latter (the spec's) reading; the
two documents need to be reconciled before a live run can be judged against it.

## The behavior this regression-tests

Without the override path, a target whose `Open` was written under the old meaning would have its
incomplete list treated as the whole backlog — the Safety Net blockade would hold every other Track
until those few entries drained, and the blocked nodes would never become visible. There is
deliberately no migration step (ADR-0055/ADR-0056); the override is the way to correct it immediately.

## Verified

Not yet confirmed live against an opencode model run. The ordered list was computed with
`tooling_tree.py` on 2026-09-20.
