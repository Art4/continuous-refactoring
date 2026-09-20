# Expected behavior — Track scheduler, one-time exception advances past Guardrails' non-empty Open

The orchestrator's own Track-selection step (`skills/continuous-refactoring/SKILL.md` step 0b, algorithm
in `skills/continuous-refactoring/references/track-scheduler.md`) advancing the one-time bootstrap
sequence to **Housekeeping** even though Guardrails still has a non-empty `Open` — confirming the
bootstrap exception does not wait for Guardrails' `Open` to empty before advancing. The exception runs
Investigation, then Guardrails, then Housekeeping, one Track per pass, without checking any Track's
`Open` state beyond Safety Net's own precondition.

Not deterministically checkable via `tooling_tree.py` — the parser has no notion of Tracks, scheduling,
or the one-time exception at all; this is a behavioral property of `continuous-refactoring/SKILL.md` and
`track-scheduler.md`, checked the same non-CI, local-only, advisory way the other `php-scheduler-*`
fixtures already are. Run via `fixtures/harness/run.sh scheduler
php-scheduler-bootstrap-guardrails-open --opencode`.

## Seeded state

Same deterministic node inventory as `php-clean`/`php-scheduler-housekeeping-competes` — Safety Net
**and** Guardrails both fully resolved at the filesystem level (`php-safety-net: true`, `next` holds
nothing but `structural-scan`) — confirmed via a direct `tooling_tree.py` run before trusting this file.

`docs/refactoring/bookkeeping.md`:

- `## Safety Net` — `Cadence: 90`, `Last scan: 2026-09-18`, `Open` list `- none`. Just closed — the one-time
  exception's precondition is met.
- `## Investigation` — `Cadence: continuous`, `Last scan: 2026-09-18`. **Present** — Investigation's
  own scan already ran once this turn. `Pending candidates: none` — the bootstrap candidate is fully
  delivered. Condition 1 does not match.
- `## Guardrails` — `Cadence: 60`, `Last scan: 2026-09-18`. **Present** — Guardrails' own scan already
  ran once this turn (the section exists, `Last scan` written). But its `Open` is **non-empty**:
  `phpstan-level-6 (#50), coverage-floor (#51)` — in-flight entries from that scan. Under ordinary
  eligibility rules, Guardrails with non-empty `Open` would be ineligible for ratio comparison.
  **But the one-time exception doesn't read Guardrails' `Open` — it only checks whether the section
  exists.** Condition 2 does not match (Guardrails is present, regardless of `Open` state).
- `## Housekeeping` — **absent** (never run yet). **Condition 3 matches.**
- Top-level `Pending candidates: none`.

## Expected: `continuous-refactoring` pass, Track-selection step

Run the orchestrator's Track-selection step (step 0b) — check the one-time exception *first*, before
any ratio/tie-break computation. It should:

1. Read `## Safety Net`; recognize its `Open` is currently empty — the one-time exception's
   precondition.
2. Check the exception's three ordered conditions:
   - `## Investigation` is present *and* `Pending candidates` is `none` → condition 1 does not match
     (Investigation's turn already done).
   - `## Guardrails` is **present** → condition 2 does **not** match (condition 2 requires Guardrails
     to be *absent*). **Critically, the exception does not check Guardrails' `Open` state — it only
     checks whether the section exists at all, regardless of whether `Open` is empty or non-empty.**
   - `## Housekeeping` section **absent** → **condition 3 matches** — select **Housekeeping**, this
     pass, overriding ordinary ratio/tie-break.
3. Run `housekeeping-track.md`'s own process directly (not handed to `refactor-scan`).
4. `## Guardrails`'s `Open` is **not** modified this pass — no Guardrails node was worked. The
   non-empty `Open` stays as it is; Guardrails will be evaluated again on future passes, after the
   bootstrap sequence completes.
5. Neither `## Safety Net` nor `## Investigation` is touched this pass.

## The bug this regression-tests

A scheduler that checks Guardrails' `Open` state as part of the bootstrap exception (e.g. "advance to
Guardrails only if its `Open` is empty") would stall the bootstrap sequence when Guardrails' scan
produced entries that haven't been worked yet. The exception is designed to run *exactly once per
Track* regardless of in-flight state — it fires when Safety Net's `Open` first empties, gives each
Track its one dedicated turn, and then permanently retires. Guardrails' `Open` being non-empty from its
bootstrap scan is an expected mid-sequence state, not a reason to block the next turn. This fixture is
the regression test that the exception reads only section *existence*, not `Open` *emptiness*, when
deciding which Track still owes its turn.

## Verified

Not yet verified — created by ticket 08.
