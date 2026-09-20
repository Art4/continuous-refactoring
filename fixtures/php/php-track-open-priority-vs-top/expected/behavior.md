# Expected behavior — Track Open: priority-labeled issue vs. the top of Open

Confirms that a `refactor:priority`-labeled issue does not bypass the Safety Net blockade and never
preempts a Track's `Open` walk — the `Open` walk still processes the Track's top workable node, and
the priority issue waits until the blockade lifts (the label narrows the Rank pool and is otherwise
only a tie-breaker between equally ranked candidates, and Track nodes are not in that pool).

Not deterministically checkable via `tooling_tree.py` — checked the same non-CI, local-only,
advisory way `safety-net-track`/`guardrails-track` already are. Run via
`fixtures/harness/run.sh safety-net-track php-track-open-priority-vs-top --opencode`.

## Seeded state

`composer.json` — only `php` itself required, no dev dependencies:
`composer`/`psr-4` read fulfilled, but `phpunit`, `php-cs-fixer`, `phpstan-level-0` are all
genuinely missing.

`docs/refactoring/bookkeeping.md`'s `## Safety Net` section: `Last scan: 2026-01-01`, `Open:`
- `phpunit (#6)` — workable (no required parent blocking it)

`.scratch/refactor/issues/01-shallow-user-service.md` — carries `refactor:priority` and
`ready-for-agent`, a structural candidate (not a Track node). This is a human-prioritized
backlog item that would win the Rank pool if Rank mode ran — but Rank mode doesn't run
when Safety Net has a non-empty `Open` (the blockade is active), and the label never preempts the
`Open` walk.

`.scratch/refactor/issues/06-phpunit.md` — already filed with a plan and `ready-for-agent`,
simulating a previous pass that designed this candidate.

## Expected: `continuous-refactoring` pass

Run the orchestrator with Safety Net selected (blockade active — `Open` non-empty). It should:

1. Safety Net is selected because its `Open` is non-empty (the blockade).
2. `refactor-scan`'s `Open` walk processes `phpunit (#6)` — workable, not fulfilled → hand it forward (its
   issue is already filed; the walk itself files nothing), work it via
   `refactor-design`/`refactor-implement`.
3. The priority-labeled issue (`01-shallow-user-service.md`) is **not** worked this pass — the
   Safety Net blockade means the Track's `Open` walk runs, not Rank mode. The priority issue
   waits until the blockade lifts (Safety Net `Open` empties).
4. Rank mode is not invoked at all this pass — Track nodes bypass it entirely.
5. The closing report's **Status** line mentions `phpunit` was worked; the priority issue is
   not mentioned (it's not a Track node and wasn't processed).

## The behavior this regression-tests

Without the "priority never preempts the `Open` walk / the Safety Net blockade" rule (the label is only a tie-breaker between equally ranked candidates), a human-prioritized issue
could steal a pass from the Track's own `Open` work, delaying the Safety Net's completion. The
blockade ensures Track `Open` work finishes before any other prioritized work runs.

## Verified

Not yet manually confirmed live against an opencode model run — see the implementing pull request's
own report for what was attempted and observed.
