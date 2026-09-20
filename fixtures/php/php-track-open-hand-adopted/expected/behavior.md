# Expected behavior — Track Open: pick-up re-check on a hand-adopted node

Confirms `refactor-scan`'s own `Open` walk
(`skills/refactor-scan/references/track-open-processing.md`) re-runs the Fulfilment check
before creating a node's issue, and reports a node that has become fulfilled since the scan (for
example adopted by hand) as a "fulfilled at pick-up" finding for `refactor-learn`'s early call to
remove from `Open` — no merge request.

Not deterministically checkable via `tooling_tree.py` — the parser has no notion of Tracks or the
`Open` walk; this is a behavioral property of `refactor-scan`'s Track `Open` handling (dispatched
from `refactor-loop/SKILL.md` step 1), checked the same non-CI, local-only, advisory way
`safety-net-track`/`guardrails-track` already are. Run via `fixtures/harness/run.sh safety-net-track
php-track-open-hand-adopted --opencode`.

## Seeded state

`composer.json` — `friendsofphp/php-cs-fixer` as a dev dependency, `.php-cs-fixer.php` config
committed, `vendor/bin/php-cs-fixer fix --dry-run` clean (zero diffs). `composer` and `psr-4` are
also fulfilled (namespaced `src/Greeter.php` under `App\`).

`docs/refactoring/bookkeeping.md`'s `## Safety Net` section: `Last scan: 2026-01-01` (far past the
default 90-day `Cadence`), `Open` as a list:
- `php-cs-fixer (#5)`
- `phpunit (#6)`
- `phpstan-level-0 (#7)`

`.scratch/refactor/issues/05-php-cs-fixer.md` — already carries `ready-for-agent` and a plan,
simulating a pass that filed this candidate before the human adopted php-cs-fixer by hand.

## Expected: `refactor-scan` pass

Run `/refactor-scan` with the Safety Net Track selected. It should:

1. Read `## Safety Net`'s `Open` list — three entries: `php-cs-fixer (#5)`, `phpunit (#6)`,
   `phpstan-level-0 (#7)`.
2. Walk the list top to bottom per `skills/refactor-scan/references/track-open-processing.md`:
   - **php-cs-fixer (#5)** — workable (unblocked, no `needs-info`, no PHP floor issue). Re-run its
     Fulfilment check: `friendsofphp/php-cs-fixer` is installed, `.php-cs-fixer.php` config is
     committed, the tool runs clean. **Fulfilment check now passes** → report a "fulfilled at
     pick-up" finding and hand it to `refactor-learn`'s early call, which removes `php-cs-fixer`
     from `Open` — no merge request, no issue created, and scan itself writes nothing. Move to the
     next entry.
   - **phpunit (#6)** — workable. Re-run its Fulfilment check: `phpunit/phpunit` is not in
     `composer.json` dev dependencies, no CI workflow references it. **Not fulfilled** → this is the
     one node worked this pass. The walk files no issue itself — hand `phpunit` forward to
     `refactor-design`, which files its issue when it works the node.
3. `phpstan-level-0 (#7)` is **not** reached this pass — exactly one node is worked per pass.
4. `php-cs-fixer` must **not** have a merge request opened for it — it left `Open` via
   `refactor-learn`'s early call, acting on scan's "fulfilled at pick-up" finding, not via any
   write scan performed.
5. The closing report's **Status** line should not mention `php-cs-fixer` as skipped (it was
   fulfilled, not skipped) — only the worked node (`phpunit`) appears.

## The behavior this regression-tests

Without the re-check, a node adopted by hand between the scan and the pass would still get a merge
request opened for it, delivering a tool the target already has. The re-check catches this and
reports it — `refactor-learn`'s early call removes the node from `Open`, keeping the write out of
`refactor-scan`'s hands entirely.

## Verified

Not yet manually confirmed live against an opencode model run — see the implementing pull request's
own report for what was attempted and observed.
