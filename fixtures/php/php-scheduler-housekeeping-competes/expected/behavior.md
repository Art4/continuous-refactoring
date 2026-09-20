# Expected behavior — Track scheduler, Housekeeping's real Cadence competing in ratio comparison

The orchestrator's own Track-selection step (`skills/continuous-refactoring/SKILL.md` step 0b, algorithm
in `skills/continuous-refactoring/references/track-scheduler.md`) picking **Housekeeping**
(`CONTEXT.md`) — this ticket's own core case: unlike Investigation's permanent `continuous` Cadence,
Housekeeping's `## Housekeeping` section carries a real day-count `Cadence` that has to actually win the
numeric `overdue_ratio` comparison, not just fall out of the fixed tie-break order. This fixture
deliberately sets Housekeeping's ratio *above* Guardrails' even though the fixed tie-break order (Safety
Net > Guardrails > Housekeeping > Investigation) ranks Guardrails higher — proving selection follows the
genuine ratio, not the tie-break order, the same point `php-scheduler-staleness-selection` (ticket 04)
already established for Guardrails outranking Safety Net.

Not deterministically checkable via `tooling_tree.py` — the parser has no notion of Tracks or scheduling
at all; this is a behavioral property of `continuous-refactoring/SKILL.md` and `track-scheduler.md`,
checked the same non-CI, local-only, advisory way the other `php-scheduler-*` fixtures already are. Run
via `fixtures/harness/run.sh scheduler php-scheduler-housekeeping-competes --opencode`.

## Seeded state

Same deterministic node inventory as `php-scheduler-investigation-fallback`/`php-clean` — Safety Net
**and** Guardrails both fully resolved (`php-safety-net: true`, `next` holds nothing but
`structural-scan`) — confirmed via a direct `tooling_tree.py` run before trusting this file.

`docs/refactoring/bookkeeping.md`:

- `## Safety Net` — `Cadence: 90`, `Last scan: 2026-09-01` (18 days before this fixture's reference date
  of 2026-09-19 → `overdue_ratio ≈ 0.2`), `Open` list `- none`. **Not due.**
- `## Guardrails` — `Cadence: 60`, `Last scan: 2026-07-01` (80 days before → `overdue_ratio ≈ 1.33`),
  `Open` list `- none`. **Due, but modestly.**
- `## Housekeeping` — `Cadence: 7`, `Last scan: 2026-08-20` (30 days before → `overdue_ratio ≈ 4.29`). No
  `Open`/`Out-of-scope` field at all (this section never carries either, per
  `skills/continuous-refactoring/references/refactoring-bookkeeping.md`'s own `## Housekeeping` section)
  — always eligible the moment it's due. **Very due — the highest ratio of any Track this pass.**
- `## Investigation` — `Cadence: continuous`, `Last scan: 2026-09-10`. Always due (no day-count to
  divide by) and always eligible, but the scheduler's own lowest tie-break priority — irrelevant here
  since two other Tracks carry a genuine ratio `>= 1`.

`docs/refactoring/housekeeping-template.md` carries one contributed line (`Confirm composer.json's
description field still accurately describes this project; update if stale`), so a fresh Housekeeping
cycle has something real to check — not the "nothing registered" all-clear case.

## Expected: `continuous-refactoring` pass, Track-selection step

Run the orchestrator's Track-selection step (step 0b), then the Housekeeping Track's own process (step
0c, `skills/continuous-housekeeping/references/housekeeping-track.md`) — stop once that process reaches
its own *Deliver* step's "no forge/remote available" branch (this sandbox has no git remote), don't
continue into a real push. It should:

1. Read `## Safety Net`, `## Guardrails`, `## Housekeeping`, and `## Investigation`; compute each
   `overdue_ratio` (or, for Investigation, note the absence of one).
2. Recognize Safety Net (`≈0.2`) is **not due**.
3. Recognize Guardrails (`≈1.33`) **is due**, and Housekeeping (`≈4.29`) **is due, at a materially
   higher ratio** — not a tie, a genuine difference.
4. **Select Housekeeping** — the highest `overdue_ratio` this pass, despite Guardrails outranking it in
   the fixed tie-break order; the tie-break order only ever applies to a tie or to Tracks with no ratio
   to compare, never to override a real staleness difference (`track-scheduler.md`'s own Selection
   section).
5. Run `skills/continuous-housekeeping/references/housekeeping-track.md`'s own process directly (not
   handed to `refactor-scan` — Housekeeping isn't a tooling-tree scan): find no in-progress
   `Housekeeping — <date>` issue (a fresh cycle), reconcile, read `housekeeping-template.md`'s one
   contributed line, open an issue titled `Housekeeping — <date>` with that line plus the standing
   AGENTS.md/skills/house-rules check, and work the checklist.
6. Neither `## Safety Net` nor `## Guardrails` is touched this pass (both still due-check-eligible for a
   future pass, just not the one selected this time) — no write to either section should happen.

## The bug this regression-tests

Before this ticket, `## Housekeeping` didn't exist as a bookkeeping section at all — Housekeeping
structurally couldn't enter Track-selection's ratio comparison (ticket 04's own PR report explicitly
named this gap), and the standalone `continuous-housekeeping` skill computed its own due-ness from
tracker history alone, with no way to ever lose a competition it wasn't in. This fixture is the first
regression test of Housekeeping actually competing on a real, hand-editable `Cadence` — and of it
winning *on ratio*, not merely by sitting above Investigation in the fixed tie-break order the way
`php-scheduler-investigation-fallback` already exercises.

## Verified

Confirmed live via `OPENCODE_TIMEOUT=280 fixtures/harness/run.sh scheduler
php-scheduler-housekeeping-competes --opencode` — see the implementing pull request's own report for the
transcript summary.
