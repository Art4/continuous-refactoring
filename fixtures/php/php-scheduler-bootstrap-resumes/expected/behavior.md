# Expected behavior — Track scheduler, one-time exception retired, ordinary scheduling resumes

The orchestrator's own Track-selection step (`skills/continuous-refactoring/SKILL.md` step 0b, algorithm
in `skills/continuous-refactoring/references/track-scheduler.md`) picking **Guardrails** via genuine
`overdue_ratio` comparison, *not* the one-time exception — confirming the exception is permanently done
once all three of Investigation/Guardrails/Housekeeping have each had their own turn, even on a pass
where Investigation is (as always) technically due and eligible "by elimination."

Not deterministically checkable via `tooling_tree.py` — the parser has no notion of Tracks, scheduling,
or the one-time exception at all; this is a behavioral property of `continuous-refactoring/SKILL.md` and
`track-scheduler.md`, checked the same non-CI, local-only, advisory way the other `php-scheduler-*`
fixtures already are. Run via `fixtures/harness/run.sh scheduler php-scheduler-bootstrap-resumes
--opencode`.

## Seeded state

Same deterministic node inventory as the other `php-scheduler-bootstrap-*` fixtures — Safety Net and
Guardrails both fully resolved at the filesystem level.

`docs/refactoring/bookkeeping.md` — all four sections present, each having already run at least once (the
one-time exception's own three turns are all long finished):

- `## Safety Net` — `Cadence: 90`, `Last scan: 2026-09-01` (18 days before this fixture's reference date
  of 2026-09-19 → `overdue_ratio ≈ 0.2`), `Open: none`. **Not due.**
- `## Guardrails` — `Cadence: 60`, `Last scan: 2026-07-01` (80 days before → `overdue_ratio ≈ 1.33`),
  `Open: none`. **Due.** (Same numbers as `php-scheduler-housekeeping-competes`'s own Guardrails section —
  reused deliberately, so this fixture's ratio math is easy to cross-check.)
- `## Housekeeping` — `Cadence: 7`, `Last scan: 2026-09-15` (4 days before → `overdue_ratio ≈ 0.57`). **Not
  due.**
- `## Investigation` — `Cadence: continuous`, `Last scan: 2026-08-20`. Always due, always eligible — but,
  per the fixed tie-break order (Safety Net > Guardrails > Housekeeping > Investigation), never wins
  against a Track with a genuine `overdue_ratio >= 1` due this same pass.
- Top-level `Pending candidates: none`.

Every one of the one-time exception's three conditions (`track-scheduler.md`'s own "One-time exception"
section) is false here: `## Investigation` is present with no in-flight `Pending candidates`, `##
Guardrails` is present, `## Housekeeping` is present — condition 4 (the exception is permanently done)
applies, and ordinary Eligibility/Selection runs unmodified.

## Expected: `continuous-refactoring` pass, Track-selection step

Run the orchestrator's Track-selection step (step 0b) — check the one-time exception first, confirm it
does **not** apply, then run ordinary ratio/tie-break selection. It should:

1. Read `## Safety Net`; its `Open` is empty, so check the exception's three conditions — all false (see
   above). The exception does not fire.
2. Compute every wired Track's `overdue_ratio`: Safety Net `≈0.2` (not due), Guardrails `≈1.33` (due),
   Housekeeping `≈0.57` (not due), Investigation always due/eligible but no numeric ratio.
3. **Select Guardrails** — the only Track with a genuine `overdue_ratio >= 1` this pass. Investigation
   must **not** be selected here, even though it's technically due-and-eligible "by elimination" the way
   it would be if Guardrails weren't due — Guardrails' real ratio outranks it (the fixed tie-break order
   only ever resolves a tie or a "no ratio to compare" case, never a genuine staleness difference,
   `track-scheduler.md`'s own Selection section).
4. Neither `## Safety Net`, `## Housekeeping`, nor `## Investigation` is touched this pass.

## The bug this regression-tests

A one-time-exception implementation that keys off something too broad (e.g. "Safety Net's `Open` is
currently empty," full stop, with no per-Track "already had its turn" tracking) would keep re-firing on
every later pass where Safety Net's `Open` happens to be empty — including this steady-state one — and
could easily mis-force Investigation again since it's always eligible. This fixture is the regression
test that the exception is truly permanently retired once each of the three turns is verifiably done, and
that ordinary staleness-ratio scheduling (ticket 04's own mechanism) governs every pass after that, the
same way it would for a target that never went through the exception's sequence at all.

## Verified

Confirmed live via `OPENCODE_TIMEOUT=280 fixtures/harness/run.sh scheduler
php-scheduler-bootstrap-resumes --opencode` — see the implementing pull request's own report for the
transcript summary.
