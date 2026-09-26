# Expected behavior — Track scheduler, Housekeeping preempts Guardrails backlog

The orchestrator's own Track-selection step (`skills/continuous-refactoring/SKILL.md` step 1, algorithm
in `skills/continuous-refactoring/references/track-scheduler.md`) selecting **Housekeeping** over
Guardrails when both are due — Housekeeping preempts Guardrails for one pass when due
(`overdue_ratio >= 1`), then Guardrails resumes afterwards. This tests the preemption rule:
Housekeeping is selected over Guardrails for that single pass, even though Guardrails has higher
tie-break priority and has workable `Open` entries.

Not deterministically checkable via `tooling_tree.py` — the parser has no notion of Tracks, scheduling,
or the preemption rule at all; this is a behavioral property of `continuous-refactoring/SKILL.md` and
`track-scheduler.md`, checked the same non-CI, local-only, advisory way the other `php-scheduler-*`
fixtures already are. Run via `fixtures/harness/run.sh scheduler
php-scheduler-housekeeping-preempts-guardrails --opencode`.

## Seeded state

Same deterministic node inventory as `php-clean`/`php-scheduler-housekeeping-competes` — Safety Net
**and** Guardrails both fully resolved at the filesystem level (`php-safety-net: true`, `next` holds
nothing but `structural-scan`) — confirmed via a direct `tooling_tree.py` run before trusting this file.

`.scratch/refactor/bookkeeping.md`:

- `## Safety Net` — `Cadence: 90`, `Last scan: 2026-09-01` (18 days before this fixture's reference
  date of 2026-09-19 → `overdue_ratio ≈ 0.2`), `Open` list `- none`. **Not due.**
- `## Guardrails` — `Cadence: 60`, `Last scan: 2026-07-01` (80 days before → `overdue_ratio ≈ 1.33`),
  `Open` (as a list):
  - `composer-audit (#40)`
  - `phpmd (#41)`

  Both entries are workable (unblocked, not flagged, no PHP floor issue). **Due and has workable Open entries — would win under ordinary selection.**
- `## Housekeeping` — `Cadence: 7`, `Last scan: 2026-08-20` (30 days before → `overdue_ratio ≈ 4.29`).
  **Due at a materially higher ratio — preempts Guardrails.**
- `## Investigation` — `Cadence: continuous`, `Last scan: 2026-09-10`. Always due, always eligible.
- Top-level `Pending candidates: none`.

## Expected: `continuous-refactoring` pass, Track-selection step

Run the orchestrator's Track-selection step (step 1) — it should:

1. Read `## Safety Net`; its `Open` is empty — the Safety Net blockade does not fire.
2. Check the one-time exception: all four sections present, Investigation has no in-flight `Pending
   candidates` → the exception is permanently done.
3. Compute every wired Track's `overdue_ratio`: Safety Net ≈0.2 (not due), Guardrails ≈1.33 (due),
   Housekeeping ≈4.29 (due), Investigation always due/eligible but no numeric ratio.
4. Apply the preemption rule: Housekeeping (`overdue_ratio >= 1`) preempts Guardrails for this single
   pass — Housekeeping is selected over Guardrails even though Guardrails has higher tie-break priority
   and has workable `Open` entries.
5. **Select Housekeeping** — the preemption rule overrides Guardrails' higher tie-break priority.
6. Run `housekeeping-track.md`'s own process directly (not handed to `refactor-scan`).
7. `## Guardrails`'s `Open` is **not** modified this pass — no Guardrails node was worked. Guardrails
   resumes on a future pass when it is selected again.
8. The pass report should note that Housekeeping preempted Guardrails.

## The bug this regression-tests

A scheduler that doesn't implement the preemption rule would select Guardrails over Housekeeping when
both are due, because Guardrails has higher tie-break priority (Safety Net > Guardrails > Housekeeping >
Investigation) and both have genuine `overdue_ratio >= 1`. This fixture is the regression test that
Housekeeping's preemption rule fires: Housekeeping is selected for this one pass despite Guardrails'
higher tie-break rank, and Guardrails resumes afterwards.

## Verified

Not yet verified — created by ticket 08.
