# Expected behavior — Track scheduler, one-time exception (turn 2: Guardrails, not Investigation again)

The orchestrator's own Track-selection step (`skills/continuous-refactoring/SKILL.md` step 1, algorithm
in `skills/continuous-refactoring/references/track-scheduler.md`) picking **Guardrails** the pass right
after Investigation's own one bootstrap turn already completed — confirming the one-time exception's
sequence actually advances instead of re-selecting Investigation forever (Investigation is otherwise the
scheduler's *permanent* fallback, so a naive implementation could easily keep picking it).

Not deterministically checkable via `tooling_tree.py` — the parser has no notion of Tracks, scheduling,
or the one-time exception at all; this is a behavioral property of `continuous-refactoring/SKILL.md` and
`track-scheduler.md`, checked the same non-CI, local-only, advisory way the other `php-scheduler-*`
fixtures already are. Run via `fixtures/harness/run.sh scheduler php-scheduler-bootstrap-guardrails
--opencode`.

## Seeded state

Same deterministic node inventory as `php-scheduler-bootstrap-investigation` — Safety Net and Guardrails
both fully resolved at the filesystem level (`php-safety-net: true`, `next` holds nothing but
`structural-scan`).

`.scratch/refactor/bookkeeping.md`:

- `## Safety Net` — `Cadence: 90`, `Last scan: 2026-09-18`, `Open` list `- none`. Same as
  `php-scheduler-bootstrap-investigation` — still the same "just closed" state.
- `## Investigation` — `Cadence: continuous`, `Last scan: 2026-09-18`. **Present** (unlike
  `php-scheduler-bootstrap-investigation`, where it was absent) — Investigation's own scan already ran
  once, this turn's first pass. Top-level `Pending candidates: none` — the one bootstrap candidate that
  scan proposed is already fully delivered (design → implement → learn all complete), not just proposed.
  This combination — section present *and* `Pending candidates: none` — is exactly what
  `track-scheduler.md`'s own "One-time exception" section 1 requires to consider Investigation's turn
  finished, distinct from a mid-flight candidate (section present but `Pending candidates` still naming
  an issue), which would keep forcing Investigation selected instead.
- No `## Guardrails` or `## Housekeeping` section at all — neither has run yet.

## Expected: `continuous-refactoring` pass, Track-selection step

Run the orchestrator's Track-selection step (step 1) — check the one-time exception first — then hand
off to `refactor-scan` for that Track only; stop there, don't continue through design/implement. It
should:

1. Read `## Safety Net`; recognize its `Open` is currently empty — the exception's precondition still
   holds.
2. Check the exception's three ordered conditions: `## Investigation` is present *and* `Pending
   candidates` is `none` → **condition 1 does not match** (Investigation's own turn is done). Check
   condition 2: `## Guardrails` section absent → **matches** — select **Guardrails**, this pass,
   overriding ordinary ratio/tie-break, without ever re-selecting Investigation.
3. Hand the Guardrails Track to `refactor-scan` as an explicit input; `refactor-scan` runs
   `guardrails-track.md`'s own process, judging each Guardrails node's Purpose against the repo (this
   fixture's underlying files already fulfil every Guardrails node deterministically, so the scan should
   find nothing new to propose and record `## Guardrails` with `Open` list `- none`, `Last scan` set — the
   "first-run, nothing missing" outcome, same shape `php-guardrails-first-run` already exercises for the
   Guardrails Track alone).
4. Neither `## Safety Net` nor `## Investigation` should be touched this pass.

## The bug this regression-tests

A one-time-exception implementation that only checks "did Safety Net's `Open` just empty" without also
tracking which of the three downstream Tracks already had its turn would either re-select Investigation
forever (it's otherwise the scheduler's permanent, always-due, always-eligible fallback) or reset back to
Investigation on every pass regardless of progress. This fixture is the first regression test of the
sequence actually advancing to Guardrails once Investigation's own turn is verifiably finished.

## Verified

Confirmed live via `OPENCODE_TIMEOUT=280 fixtures/harness/run.sh scheduler
php-scheduler-bootstrap-guardrails --opencode` — see the implementing pull request's own report for the
transcript summary.
