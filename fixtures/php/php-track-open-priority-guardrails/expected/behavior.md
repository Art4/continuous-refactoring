# Expected behavior — Track Open: priority-labeled issue vs. a Guardrails `Open` walk

Confirms that a `refactor:priority`-labeled issue never preempts a Guardrails Track's `Open` walk —
Guardrails is selected because it has a workable `Open` node, the walk still works that node this
pass, and the priority issue waits until Guardrails' `Open` has no workable node left (Guardrails
yields). The label narrows the Rank pool only, and Track nodes are not in that pool.

Guardrails counterpart of `php-track-open-priority-vs-top` (which pins the same rule under the Safety
Net blockade). Not deterministically checkable via `tooling_tree.py` — checked the same non-CI,
local-only, advisory way `safety-net-track`/`guardrails-track` already are. Run via
`fixtures/harness/run.sh guardrails-track php-track-open-priority-guardrails --opencode`.

## Seeded state

The Safety Net is fully closed (same shape as `php-guardrails-open-blocks-rescan`'s own seeded state —
`psr-4`/`ci-runner`/`php-cs-fixer`/`phpunit`/`phpstan-level-5`/the `rector-*` family resolved,
`psalm-taint-analysis` rejected), so `php-safety-net` resolves and every Guardrails node is genuinely
reachable. `phpmd` is still genuinely missing.

`docs/refactoring/bookkeeping.md`:

- `## Safety Net` — `Cadence: 90`, `Last scan: 2026-09-01` (18 days before this fixture's reference
  date of 2026-09-19 → `overdue_ratio ≈ 0.2`), `Open: none`. Not due; no blockade.
- `## Guardrails` — `Cadence: 60`, `Last scan: 2026-07-01` (80 days before → `overdue_ratio ≈ 1.33`),
  `Open: phpmd (#5)` — workable (unblocked, not flagged `needs-info`, no PHP floor issue). Due and
  has a workable `Open` node.
- `## Housekeeping` — `Cadence: 7`, `Last scan: 2026-09-15` (`overdue_ratio ≈ 0.57`). Not due, so it
  does not preempt Guardrails.
- `## Investigation` — `Cadence: continuous`. Always due, always eligible, lowest tie-break.
- Top-level `Pending candidates: none`.

`.scratch/refactor/issues/01-shallow-user-service.md` — carries `refactor:priority` and
`ready-for-agent`, a structural candidate (not a Track node). A human-prioritized backlog item that
would win the Rank pool if Rank mode ran — but Rank mode doesn't run while a Track with a workable
`Open` node is selected, and the label never preempts the `Open` walk.

`.scratch/refactor/issues/05-phpmd.md` — already filed with a plan and `ready-for-agent`, simulating
a previous pass that designed this candidate.

## Expected: `continuous-refactoring` pass

Run the orchestrator through Track selection and the scan step. It should:

1. Select **Guardrails** — the one-time exception is done (all four sections present), Guardrails is
   the due-and-eligible Track with a workable `Open` node, ahead of Investigation; Housekeeping is
   not due.
2. `refactor-scan`'s `Open` walk processes `phpmd (#5)` — workable, not fulfilled → hand it forward
   (its issue is already filed; the walk itself files nothing), work it via
   `refactor-design`/`refactor-implement`.
3. The priority-labeled issue (`01-shallow-user-service.md`) is **not** worked this pass — the `Open`
   walk runs, not Rank mode. The priority issue waits until Guardrails' `Open` has no workable node
   left (Guardrails yields).
4. Rank mode is not invoked at all this pass — Track nodes bypass it entirely, and a labeled
   structural issue is never compared against the head of `Open`.
5. The closing report's **Status** line mentions `phpmd` was worked; the priority issue is not
   mentioned (it's not a Track node and wasn't processed).

## The behavior this regression-tests

Without the "priority never preempts the `Open` walk" rule, a human-prioritized issue could steal a
pass from a selected Guardrails Track that still has workable work, contradicting ADR-0056 (Track
nodes left the Rank pool; the label narrows the Rank pool only).

## Verified

Not yet manually confirmed live against an opencode model run.
