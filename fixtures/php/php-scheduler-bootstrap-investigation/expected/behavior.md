# Expected behavior — Track scheduler, one-time exception (turn 1: Investigation)

The orchestrator's own Track-selection step (`skills/continuous-refactoring/SKILL.md` step 1, algorithm
in `skills/continuous-refactoring/references/track-scheduler.md`) picking **Investigation** the pass
right after Safety Net's `Open` first empties — this ticket's own core case: the one-time exception
(`track-scheduler.md`'s own "One-time exception" section) must override ordinary ratio/tie-break
selection, which — left unmodified — would instead pick **Guardrails** here (a never-run Track always
wins its own ratio comparison, and Guardrails outranks Investigation in the fixed tie-break order too).
Selecting Investigation despite that is the whole point of this fixture.

Not deterministically checkable via `tooling_tree.py` — the parser has no notion of Tracks, scheduling,
or the one-time exception at all; this is a behavioral property of `continuous-refactoring/SKILL.md` and
`track-scheduler.md`, checked the same non-CI, local-only, advisory way the other `php-scheduler-*`
fixtures already are. Run via `fixtures/harness/run.sh scheduler php-scheduler-bootstrap-investigation
--opencode`.

## Seeded state

Same deterministic node inventory as `php-clean`/`php-scheduler-housekeeping-competes` — Safety Net
**and** Guardrails both fully resolved at the filesystem level (`php-safety-net: true`, `next` holds
nothing but `structural-scan`) — confirmed via a direct `tooling_tree.py` run before trusting this file.

`docs/refactoring/bookkeeping.md`:

- `## Safety Net` — `Cadence: 90`, `Last scan: 2026-09-18` (1 day before this fixture's reference date of
  2026-09-19 → `overdue_ratio ≈ 0.01`), `Open` list `- none`. **Just closed — this is the pass right after `Open`
  emptied.**
- No `## Guardrails`, `## Housekeeping`, or `## Investigation` section at all — none of the three has
  ever run for this target. Under *ordinary* Eligibility/Selection alone (i.e. if the one-time exception
  didn't exist), every one of the three would be "never run" and thus maximally overdue, tied with each
  other; the fixed tie-break order (Safety Net > Guardrails > Housekeeping > Investigation) would then
  pick **Guardrails** — not Investigation. This is the fixture's deliberate adversarial setup: a
  more-overdue-by-the-ordinary-rules Track (Guardrails, tied for "never run" but ranked higher) must
  still lose to Investigation once the one-time exception applies.
- Top-level `Pending candidates: none`.

## Expected: `continuous-refactoring` pass, Track-selection step

Run the orchestrator's Track-selection step (step 1) — check the one-time exception *first*, before any
ratio/tie-break computation — then hand off to `refactor-scan` for that Track only; stop there, don't
continue through design/implement. It should:

1. Read `## Safety Net`; recognize it exists and its `Open` is currently empty — the one-time exception's
   entire precondition.
2. Check the exception's three ordered conditions: `## Investigation` section absent → **its condition
   matches first** — select **Investigation**, this pass, without ever computing or comparing an
   `overdue_ratio` for any Track, and without applying the fixed tie-break order at all.
3. Hand the Investigation Track to `refactor-scan` as an explicit input; `refactor-scan` runs
   `investigation-track.md`'s own process and proposes `structural-scan` — already unblocked (every
   resolved-edge parent resolved).
4. Neither `## Safety Net`, a fresh `## Guardrails`, nor a fresh `## Housekeeping` section should be
   written this pass — only `## Investigation`'s own `Last scan` (and, once the underlying candidate is
   fully delivered in a later pass, nothing further on this section's own account).

## The bug this regression-tests

Before this ticket, no one-time exception existed at all: the pass right after Safety Net's `Open` first
emptied went straight to ordinary ratio/tie-break selection, which — as this fixture's seeded state
shows — would hand the very first post-Safety-Net pass to Guardrails (tooling adoption) instead of
Investigation (one real piece of delivered refactoring work), the opposite of the UX the spec's user
story 5 and ADR-0055 describe. This fixture is the first regression test of the exception actually firing
ahead of a genuinely more-overdue-by-the-ordinary-rules Track.

## Verified

Confirmed live via `OPENCODE_TIMEOUT=280 fixtures/harness/run.sh scheduler
php-scheduler-bootstrap-investigation --opencode` — see the implementing pull request's own report for
the transcript summary.
