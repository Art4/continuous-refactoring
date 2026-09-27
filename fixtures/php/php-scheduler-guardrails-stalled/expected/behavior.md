# Expected behavior — Track scheduler, Guardrails stalled (nothing workable yields)

The orchestrator's own Track-selection step (`skills/continuous-refactoring/SKILL.md` step 1, algorithm
in `skills/continuous-refactoring/references/track-scheduler.md`) handling a Guardrails Track whose
`Open` is non-empty but nothing in it is currently workable — Guardrails yields, its `Open` stays as it
is, and the pass report lists every stalled node with its reason. The ordinary ratio and tie-break rules
then pick among the other Tracks.

Not deterministically checkable via `tooling_tree.py` — the parser has no notion of Tracks, scheduling,
or the yield behavior at all; this is a behavioral property of `continuous-refactoring/SKILL.md` and
`track-scheduler.md`, checked the same non-CI, local-only, advisory way the other `php-scheduler-*`
fixtures already are. Run via `fixtures/harness/run.sh scheduler
php-scheduler-guardrails-stalled --opencode`.

## Seeded state

Same deterministic node inventory as `php-clean`/`php-scheduler-housekeeping-competes` — Safety Net
**and** Guardrails both fully resolved at the filesystem level (`php-safety-net: true`, `next` holds
nothing but `structural-scan`) — confirmed via a direct `tooling_tree.py` run before trusting this file.

`.scratch/refactor/bookkeeping.md`:

- `## Safety Net` — `Cadence: 90`, `Last scan: 2026-09-01` (18 days before this fixture's reference
  date of 2026-09-19 → `overdue_ratio ≈ 0.2`), `Open` list `- none`. **Not due.**
- `## Guardrails` — `Cadence: 60`, `Last scan: 2026-07-01` (80 days before → `overdue_ratio ≈ 1.33`),
  **`Open` (as a list):**
  - `phpstan-level-6 (#30)`
  - `coverage-floor (#31)`

  Both entries are non-workable:
  `phpstan-level-6` is blocked by `phpstan-level-5` (required parent not yet fulfilled in the
  bookkeeping sense), and `coverage-floor` is flagged `needs-info` on its issue. The Track is
  non-empty but stalled — nothing can be worked.
- `## Housekeeping` — `Cadence: 7`, `Last scan: 2026-08-20` (30 days before → `overdue_ratio ≈ 4.29`).
  **Due at a materially higher ratio.**
- `## Investigation` — `Cadence: continuous`, `Last scan: 2026-09-10`. Always due, always eligible.
- Top-level `Pending candidates: none`.

## Expected: `continuous-refactoring` pass, Track-selection step

Run the orchestrator's Track-selection step (step 1) — it should:

1. Read `## Safety Net`; its `Open` is empty — the Safety Net blockade does not fire.
2. Check the one-time exception: all four sections present, Investigation has no in-flight `Pending
   candidates` → the exception is permanently done.
3. Compute every wired Track's `overdue_ratio`: Safety Net ≈0.2 (not due), Guardrails ≈1.33 (due),
   Housekeeping ≈4.29 (due), Investigation always due/eligible but no numeric ratio.
4. Check Guardrails' eligibility: `Open` is non-empty, and the walk finds nothing workable (both
   entries are blocked or flagged). Per the Eligibility rule, Guardrails with `Open` non-empty but
   nothing workable **yields** — it drops out of ratio comparison entirely. Its `Open` stays as it is
   (no node removed, no node worked).
5. Among the remaining due-and-eligible Tracks (Housekeeping at ≈4.29, Investigation as fallback),
   **select Housekeeping** — the highest `overdue_ratio` among the remaining Tracks.
6. Run `housekeeping-track.md`'s own process directly (not handed to `refactor-scan`).
7. The pass report must list every stalled Guardrails node with its reason (e.g. "Guardrails stalled:
   phpstan-level-6 blocked by phpstan-level-5, coverage-floor needs-info").
8. `## Guardrails`'s `Open` is **not** modified this pass — no node was removed.

## The bug this regression-tests

A scheduler that sees Guardrails' `Open` non-empty and either (a) force-selects Guardrails anyway
(ignoring that nothing is workable) or (b) treats the non-empty `Open` as making Guardrails
permanently ineligible (never considering it again until `Open` empties) would either waste a pass on
nothing or skip Guardrails entirely even when a future pass could make progress. This fixture is the
regression test that the yield behavior works: Guardrails is skipped *this pass* because nothing is
workable, but its `Open` stays intact so future passes can re-evaluate it — the scheduler falls
through to Housekeeping (or Investigation, if Housekeeping weren't due) instead.

## Verified

Not yet verified — created by ticket 08.
