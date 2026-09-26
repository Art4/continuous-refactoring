# Expected behavior — Track scheduler, one-time exception (turn 3: Housekeeping)

The orchestrator's own Track-selection step (`skills/continuous-refactoring/SKILL.md` step 1, algorithm
in `skills/continuous-refactoring/references/track-scheduler.md`) picking **Housekeeping** the pass right
after both Investigation's and Guardrails' own one-time-exception turns already completed — the third and
final turn of the sequence.

Not deterministically checkable via `tooling_tree.py` — the parser has no notion of Tracks, scheduling,
or the one-time exception at all; this is a behavioral property of `continuous-refactoring/SKILL.md` and
`track-scheduler.md`, checked the same non-CI, local-only, advisory way the other `php-scheduler-*`
fixtures already are. Run via `fixtures/harness/run.sh scheduler php-scheduler-bootstrap-housekeeping
--opencode`.

## Seeded state

Same deterministic node inventory as the other `php-scheduler-bootstrap-*` fixtures — Safety Net and
Guardrails both fully resolved at the filesystem level.

`.scratch/refactor/bookkeeping.md`:

- `## Safety Net` — `Cadence: 90`, `Last scan: 2026-09-18`, `Open` list `- none`. Still the same "just closed"
  state the whole sequence started from.
- `## Guardrails` — `Cadence: 60`, `Last scan: 2026-09-18`, `Open` list `- none`. **Present** — Guardrails' own
  turn (from `php-scheduler-bootstrap-guardrails`) already ran and found nothing new to propose (this
  fixture's underlying project already fulfils every Guardrails node).
- `## Investigation` — `Cadence: continuous`, `Last scan: 2026-09-18`. Present, top-level `Pending
  candidates: none` — Investigation's own turn (from `php-scheduler-bootstrap-investigation`) is fully
  delivered.
- No `## Housekeeping` section at all — the only one of the four still never run.

## Expected: `continuous-refactoring` pass, Track-selection step

Run the orchestrator's Track-selection step (step 1) — check the one-time exception first. It should:

1. Read `## Safety Net`; `Open` is empty — precondition met.
2. Check condition 1 (`## Investigation` absent or `Pending candidates` naming an issue) — false, both
   present and clear. Check condition 2 (`## Guardrails` absent) — false, present. Check condition 3
   (`## Housekeeping` absent) — **true** — select **Housekeeping**, this pass, overriding ratio/
   tie-break, without ever computing an `overdue_ratio` for any Track.
3. Continue at `SKILL.md` step 2: run `housekeeping-track.md`'s own process directly (not handed to
   `refactor-scan`) — reconcile, open this cycle's issue, work the checklist, quality gate, reach Deliver.
   This sandbox has no git remote, so stop once `opening-a-merge-request.md`'s own "no forge/remote
   available" branch is reached — don't attempt a real push.
4. Neither `## Safety Net`, `## Guardrails`, nor `## Investigation` is touched this pass — only `##
   Housekeeping`'s own `Last scan` gets written, by `refactor-learn`'s closing call.

## The bug this regression-tests

Confirms the sequence's third and final turn actually fires — a one-time-exception implementation that
correctly handles turns 1 and 2 but miscounts "how many turns are left" (e.g. treating Guardrails'
presence as also covering Housekeeping, or stopping the sequence after two turns instead of three) would
either skip straight to ordinary ratio selection here or loop back to an earlier Track. This fixture is
the direct regression test that Housekeeping still gets its own dedicated turn.

## Verified

Confirmed live via `OPENCODE_TIMEOUT=280 fixtures/harness/run.sh scheduler
php-scheduler-bootstrap-housekeeping --opencode` — see the implementing pull request's own report for the
transcript summary.
