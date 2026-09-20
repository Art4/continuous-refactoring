# Expected behavior — Track scheduler, Safety Net blockade with nothing workable

The orchestrator's own Track-selection step (`skills/continuous-refactoring/SKILL.md` step 0b, algorithm
in `skills/continuous-refactoring/references/track-scheduler.md`) selecting **Safety Net** even though
none of its `Open` entries are currently workable — the Safety Net blockade is unconditional: while Safety
Net `Open` is non-empty, it is selected and nothing else runs, even if no node is currently workable;
what it waits on is reported.

Not deterministically checkable via `tooling_tree.py` — the parser has no notion of Tracks, scheduling,
or the blockade at all; this is a behavioral property of `continuous-refactoring/SKILL.md` and
`track-scheduler.md`, checked the same non-CI, local-only, advisory way the other `php-scheduler-*`
fixtures already are. Run via `fixtures/harness/run.sh scheduler
php-scheduler-safety-net-blockade --opencode`.

## Seeded state

Same deterministic node inventory as `php-clean`/`php-scheduler-housekeeping-competes` — Safety Net
**and** Guardrails both fully resolved at the filesystem level (`php-safety-net: true`, `next` holds
nothing but `structural-scan`) — confirmed via a direct `tooling_tree.py` run before trusting this file.

`docs/refactoring/bookkeeping.md`:

- `## Safety Net` — `Cadence: 90`, `Last scan: 2026-09-18` (1 day before this fixture's reference date
  of 2026-09-19 → `overdue_ratio ≈ 0.01`), **`Open` (as a list):**
  - `phpstan-level-6 (#20)`
  - `coverage-floor (#21)`

  Both entries are non-workable: `phpstan-level-6` is blocked by `phpstan-level-5` (required parent not
  fulfilled in the bookkeeping sense — the node's issue exists but its prerequisite hasn't been worked
  yet), and `coverage-floor` is flagged `needs-info` on its issue. **The blockade is active — Safety Net
  is selected regardless of ratio or workability.**
- `## Guardrails` — `Cadence: 60`, `Last scan: 2026-07-01` (80 days before → `overdue_ratio ≈ 1.33`),
  `Open` list `- none`. **Due, but blocked by the Safety Net blockade.**
- `## Housekeeping` — `Cadence: 7`, `Last scan: 2026-09-15` (4 days before → `overdue_ratio ≈ 0.57`).
  **Not due, and also blocked by the Safety Net blockade.**
- `## Investigation` — `Cadence: continuous`, `Last scan: 2026-09-10`. Always due, always eligible —
  but blocked by the Safety Net blockade.
- Top-level `Pending candidates: none`.

## Expected: `continuous-refactoring` pass, Track-selection step

Run the orchestrator's Track-selection step (step 0b) — it should:

1. Read `## Safety Net`; recognize its `Open` is **non-empty** — the Safety Net blockade fires
   (`track-scheduler.md`'s own "Safety Net blockade" section). This is stronger than the ordinary
   eligibility rule: Safety Net's `Open` acts as a system-wide blockade, not just a self-exclusion.
2. **Select Safety Net**, this pass, without computing or comparing an `overdue_ratio` for any Track,
   and without applying the fixed tie-break order at all — the blockade overrides everything.
3. Hand the Safety Net Track to `refactor-scan` as an explicit input; `refactor-scan` walks the Track's
   `Open` list top to bottom (`skills/refactor-scan/references/track-open-processing.md`):
   - `phpstan-level-6 (#20)` — not workable (blocked by `phpstan-level-5`); collected with reason.
   - `coverage-floor (#21)` — not workable (`needs-info` flagged); collected with reason.
4. No node is worked this pass (none was workable). The pass report must list both skipped nodes with
   their reasons.
5. `refactor-learn`'s closing call does **not** change `## Safety Net`'s `Open` (no node was removed)
   and does **not** touch `Last scan` either — no scan ran this pass (the walk skipped both entries
   and worked nothing), and `Last scan` is written only after a completed scan
   (`skills/refactor-learn/references/safety-net-write.md`).
6. `## Guardrails`, `## Housekeeping`, and `## Investigation` are **not** touched this pass — the
   blockade prevented them from being selected.

## The bug this regression-tests

A scheduler that only checks "is this Track due and eligible?" without the unconditional Safety Net
blockade would see Safety Net's `Open` non-empty and skip it (the ordinary eligibility rule: non-empty
`Open` makes a Track ineligible for ratio comparison), then fall through to Guardrails (due at ratio
1.33) or Investigation (always due). This fixture is the regression test that the blockade is stronger
than the ordinary eligibility rule: Safety Net is selected *because* its `Open` is non-empty, not
*despite* it, and nothing else runs until it empties.

## Verified

Not yet verified — created by ticket 08.
