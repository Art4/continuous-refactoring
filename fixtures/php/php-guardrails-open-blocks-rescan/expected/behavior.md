# Expected behavior — Guardrails Track: `Open` blocks a fresh rescan

Confirms the Guardrails Track's own `## Guardrails` bookkeeping
(`skills/refactor-scan/references/guardrails-track.md`) never rescans the tree while it's still
holding `Open` work, no matter how stale `Last scan` has become — the existing entry is worked through
the ordinary propose → design → implement → learn pipeline first, the same rule
`fixtures/php/php-safety-net-open-blocks-rescan` already exercises for the Safety Net Track.

Not deterministically checkable — pure skill process behavior, not something `tooling_tree.py` asserts
on its own. Run via `fixtures/harness/run.sh guardrails-track php-guardrails-open-blocks-rescan
--opencode`, same non-CI, local-only, advisory posture as `safety-net-track`/`decision-gate-bypass`.

## Seeded state

The Safety Net is fully closed (same shape as `php-guardrails-purpose-recognition`'s own seeded
state — `psr-4`/`ci-runner`/`php-cs-fixer`/`phpunit`/`phpstan-level-5`/the `rector-*`
family/`psalm-taint-analysis` all resolved), so `php-safety-net` resolves and every Guardrails node is
genuinely reachable. `composer-audit`, `coverage-floor`, `php-minimal-version`, `phpstan-level-6`,
`phpstan-deprecation-rules`, and `semgrep` are all still genuinely missing — confirmed directly against
`tooling_tree.py`, every one of them appears in `next`. If the Guardrails Track's own scan actually
re-ran this pass, it would find all six unblocked and propose them.

`docs/refactoring/bookkeeping.md`'s `## Guardrails` section: `Last scan: 2026-01-01` (far past the
default 60-day `Cadence` — deliberately, to make sure staleness alone never forces a rescan while
`Open` holds something), `Open` as a list:
- `phpmd (#5)`

`.scratch/refactor/issues/05-phpmd.md` — already carries `ready-for-agent` and a plan in its own body
(the tooling-tree-node shape, `refactor-scan/SKILL.md` step 2), simulating a pass that filed and
designed this candidate before being interrupted.

## Expected: `refactor-scan` pass

Run `/refactor-scan`. It should:

1. Read `## Guardrails`'s `Open` list, see `phpmd (#5)`, and treat it as resumable.
2. **Not** run a fresh Guardrails Track walk this pass — `composer-audit`, `coverage-floor`,
   `php-minimal-version`, `phpstan-level-6`, `phpstan-deprecation-rules`, `semgrep` (all still
   genuinely missing) must **not** appear as newly proposed candidates this pass.
3. Hand `phpmd` (#5) straight to `refactor-implement` — the issue already carries a plan and
   `ready-for-agent`, so `refactor-prioritize`/`refactor-design` are bypassed.
4. Leave `## Guardrails`'s `Last scan` untouched this pass — only a completed Track scan earns that
   write (`skills/refactor-learn/references/guardrails-write.md`), and this pass's scan didn't run.

## The behavior this regression-tests

Without this rule, a stale `Last scan` could tempt a fresh Track walk mid-candidate, risking a second,
possibly conflicting proposal for a node whose own candidate is already filed and in flight.

## Verified

Confirmed live via `OPENCODE_TIMEOUT=280 fixtures/harness/run.sh guardrails-track
php-guardrails-open-blocks-rescan --opencode` (`opencode/muse-spark-1.2-contributor-free`): the model
resumed `phpmd (#5)` straight to `refactor-implement` without rescanning, self-reporting `RESUMED`.
The harness's own first attempt at this check false-failed on a naive `grep -qi "RESCANNED"` matching
the word "rescanned" inside the model's own (correct) negative reasoning prose elsewhere in the
transcript, not its final self-report line — fixed to a line-anchored `^RESCANNED`/`^RESUMED` match; a
harness robustness fix, not a behavior change. See the implementing pull request's own report for the
full transcript summary.
