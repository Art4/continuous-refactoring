# Expected behavior — Safety Net Track: `Open` blocks a fresh rescan

Confirms the Safety Net Track's own `## Safety Net` bookkeeping (`skills/refactor-scan/references/
safety-net-track.md`) never rescans the tree while it's still holding `Open` work, no matter how stale
`Last scan` has become — the existing entry is worked through the ordinary propose → design → implement
→ learn pipeline first, same as `Pending candidates` already does for the global case.

Not deterministically checkable — pure skill process behavior, not something `tooling_tree.py` asserts
on its own. Run via `fixtures/harness/run.sh safety-net-track php-safety-net-open-blocks-rescan
--opencode`, same non-CI, local-only, advisory posture as `decision-gate-bypass`.

## Seeded state

`composer.json`/`composer.lock` — only `php` itself required, no dev dependencies at all:
`composer`/`psr-4`/`static-code-analyzer` read fulfilled via the deterministic parser (an ordinary
small namespaced project, same as `php-safety-net-purpose-recognition`), but `php-cs-fixer`, `phpunit`,
`test-runner-if-missing`, `phpstan-level-0`, and `ci-runner` are all still genuinely missing. If the
Track's own scan actually re-ran this pass, it would find several of these unblocked and propose them.

`docs/refactoring/bookkeeping.md`'s `## Safety Net` section: `Last scan: 2026-01-01` (far past the
default 90-day `Cadence` — deliberately, to make sure staleness alone never forces a rescan while `Open`
holds something), `Open` as a list:
- `php-cs-fixer (#5)`

`.scratch/refactor/issues/05-php-cs-fixer.md` — already carries `ready-for-agent` and a plan in its own
body (the tooling-tree-node shape, `refactor-scan/SKILL.md` step 2), simulating a pass that filed and
designed this candidate before being interrupted.

## Expected: `refactor-scan` pass

Run `/refactor-scan`. It should:

1. Read `## Safety Net`'s `Open` list, see `php-cs-fixer (#5)`, and treat it as resumable — same
   resume-before-propose discipline `Pending candidates` already gets, scoped to this Track.
2. **Not** run a fresh Safety Net Track walk this pass — `phpunit`, `test-runner-if-missing`,
   `phpstan-level-0`, `ci-runner` (all still genuinely missing) must **not** appear as newly proposed
   candidates this pass.
3. Hand `php-cs-fixer` (#5) straight to `refactor-implement` — the issue already carries a plan and
   `ready-for-agent`, so `refactor-prioritize`/`refactor-design` are bypassed the same way an ordinary
   resumable `Pending candidates` entry already bypasses them.
4. Leave `## Safety Net`'s `Last scan` untouched this pass — only a completed Track scan earns that
   write (`skills/refactor-learn/references/safety-net-write.md`), and this pass's scan didn't run.

## The behavior this regression-tests

Without this rule, a stale `Last scan` could tempt a fresh Track walk mid-candidate, risking a second,
possibly conflicting proposal for a node whose own candidate is already filed and in flight.

## Verified

Not yet manually confirmed live against an opencode model run — see the implementing pull request's
own report for what was attempted and observed.
