# Expected behavior — Track scheduler, never-run tie-break once Safety Net closes

The orchestrator's own Track-selection step (`skills/continuous-refactoring/SKILL.md` step 1, algorithm
in `skills/continuous-refactoring/references/track-scheduler.md`) picking **Guardrails** on the pass
right after Safety Net's `Open` first empties. No Track gets a special turn at that point: Guardrails
and Housekeeping are both never run, tie, and the fixed order decides; Investigation is the fallback
and only runs once nothing above it matches.

Not deterministically checkable via `tooling_tree.py` — the parser has no notion of Tracks or
scheduling; this is a behavioral property of `continuous-refactoring/SKILL.md` and `track-scheduler.md`,
checked the same non-CI, local-only, advisory way the other `php-scheduler-*` fixtures already are. Run
via `fixtures/harness/run.sh scheduler php-scheduler-never-run-tie-break --opencode`.

## Seeded state

Same deterministic node inventory as `php-clean`/`php-scheduler-housekeeping-competes` — Safety Net
**and** Guardrails both fully resolved at the filesystem level (`php-safety-net: true`, `next` holds
nothing but `structural-scan`).

`.scratch/refactor/bookkeeping.md`:

- `## Safety Net` — `Cadence: 90`, `Last scan: 2026-09-18` (1 day before this fixture's reference date of
  2026-09-19 → `overdue_ratio ≈ 0.01`), `Open` list `- none`. **Not due, no blockade.**
- No `## Guardrails`, `## Housekeeping`, or `## Investigation` section at all — none of the three has
  ever run for this target.

## Expected: `continuous-refactoring` pass, Track-selection step

Run the orchestrator's Track-selection step (step 1), then hand off to `refactor-scan` for that Track
only; stop there, don't continue through design/implement. It should:

1. Read `## Safety Net`; its `Open` is empty, so the blockade doesn't apply, and it isn't due.
2. Find Guardrails and Housekeeping both never run — due, eligible, tied — and pick **Guardrails** by
   the fixed order Safety Net > Guardrails > Housekeeping > Investigation.
3. Hand the Guardrails Track to `refactor-scan`, which runs `guardrails-track.md`'s own scan.
4. Not select Investigation: `structural-scan` being unblocked doesn't matter, Investigation only gets
   the pass when no other Track is due and Guardrails has no workable `Open` node.

## The bug this regression-tests

An earlier scheduler gave Investigation, then Guardrails, then Housekeeping one forced turn each right
after Safety Net closed, overriding the ordinary order. That exception is gone; this fixture's seeded
state is exactly the one where it used to fire, and selecting Investigation here means it is still
being applied.

## Verified

Not yet run live against the rewritten scheduler.
