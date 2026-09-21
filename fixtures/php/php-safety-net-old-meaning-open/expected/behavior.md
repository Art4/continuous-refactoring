# Expected behavior — Safety Net Track: an old-meaning `Open` is worked, not force-rescanned

Confirms that a `## Safety Net` section still written under the **old** `Open` meaning (only nodes
that had a filed issue, with issue numbers) neither errors nor gets migrated, and is handled by the
one rule that decides when a scan runs: **a selected Track with no `Open` entries is scanned; a
selected Track with a non-empty `Open` works its `Open` walk.** That holds however the Track was
selected — including a pass that names the Track explicitly, which forces no scan. The old-meaning
`Open` is corrected later, by the scan that runs once it is empty
(`skills/continuous-refactoring/references/track-scheduler.md`'s *Manual override*,
`skills/continuous-refactoring/references/refactoring-bookkeeping.md`, ADR-0056). Complements the
old-schema pass-through fixtures (`php-safety-net-old-schema`, `php-guardrails-old-schema`).

Deviates from the spec's case 10 ("forced rescan via override"), by the user's later decision.

Not deterministically checkable — pure skill process behavior. Run via
`fixtures/harness/run.sh safety-net-track php-safety-net-old-meaning-open --opencode`, same non-CI,
local-only, advisory posture as `safety-net-track`.

## Seeded state

The project matches `php-guardrails-old-schema`'s except PHPStan runs at **level 0** (empty baseline),
so `phpstan-level-1` through `-5` are unresolved; `psalm-taint-analysis` is already rejected under
`out-of-scope/`. Composer, PSR-4, PHP CS Fixer, PHPUnit, CI and the `rector-*` family are in place.

`docs/refactoring/bookkeeping.md` is written under the old meaning:

- `## Safety Net` — `Cadence: 90`, `Last scan: 2026-09-10` (`overdue_ratio ≈ 0.1`, not due). `Open`,
  as a list:
  - `phpstan-level-1 (#7)`

  — the one node an earlier pass filed an issue for (the old meaning of `Open`); the other unresolved
  nodes are not listed. `Out-of-scope`, as a list: `psalm-taint-analysis —
  out-of-scope/psalm-taint-analysis.md`.
- Old-schema residue: `Focus areas: none` and a `Fulfilled nodes` list (`onboarding-setup`, `composer`,
  `ci-runner`, `psr-4`, `php-cs-fixer`, `phpunit`, `phpstan-level-0`, the `rector-*` family) — ignored.
- No `## Guardrails`/`## Housekeeping`/`## Investigation` sections.

`.scratch/refactor/issues/07-phpstan-level-1.md` — carries a plan and `ready-for-agent`, simulating a
pass that filed and designed this candidate.

## Expected: a pass invoked as "run the Safety Net Track" (or an ordinary pass — same outcome)

1. The old-shape fields (`Focus areas`, `Fulfilled nodes`, the old-meaning `Open`) cause **no error**
   and no migration step; `Fulfilled nodes` is simply not consulted.
2. Safety Net is selected (its `Open` is non-empty — the blockade — and here also named explicitly).
   `Open` has an entry, so **no scan runs**: `refactor-scan` walks `Open` per
   `skills/refactor-scan/references/track-open-processing.md`.
3. The walk finds `phpstan-level-1` workable and not fulfilled and hands it forward (its issue already
   exists; the walk files nothing) to `refactor-implement`, since it already carries a plan and
   `ready-for-agent`.
4. The incomplete list is **not** rewritten this pass: `Open` is not replaced by the complete backlog
   (`phpstan-level-1` through `-5`), and `Last scan` is left untouched — only a completed scan earns
   that write (`skills/refactor-learn/references/safety-net-write.md`). `Fulfilled nodes` and
   `Focus areas` are left exactly as they were.
5. Once `phpstan-level-1` merges and `Open` empties, the scan that runs next records the complete
   backlog (`phpstan-level-2` through `-5`, in order) — that later scan, not this pass, corrects the
   old-meaning list.

## The behavior this regression-tests

Without one clear rule for when a scan runs, a manually named Track (or a stale-looking `Last scan`)
could trigger a rescan over an `Open` that still holds an in-flight, designed candidate, risking a
second, conflicting proposal for it. There is deliberately no migration step (ADR-0055/ADR-0056): the
old-meaning list is simply worked down, and the next scan fills in the rest.

## Verified

Not yet confirmed live against an opencode model run.
