# Expected behavior — decision-gate `ready-for-agent` bypass regression test

This fixture reproduces the bug fixed by [ADR-0053](../../../../docs/adr/0053-decision-gate-actively-manages-both-triage-labels.md)
("Amends [ADR-0050](../../../../docs/adr/0050-pre-implementation-decision-gate.md)"): an
externally-filed candidate issue that already carries `ready-for-agent`, describing a change that
isn't actually fully specified.

Not deterministically checkable — there's no `tooling_tree.py`-parseable output involved, this is
pure issue/label lifecycle behavior. Run via
`fixtures/harness/run.sh decision-gate-bypass php-decision-gate-bypass --opencode`, same non-CI,
local-only, advisory posture as `judge`/`lift`.

## Seeded state

`.scratch/refactor/issues/01-unify-retry-logic.md` — filed with `Labels: refactor:candidate,
ready-for-agent`, claiming "fully specified, go ahead". `src/OrderRetrySender.php` and
`src/PaymentRetryDispatcher.php` implement retry-with-backoff independently, with genuinely
different observable contracts (5 attempts / exponential / 1s / `usleep` vs. 4 attempts / linear /
2s / `sleep`) — unifying them requires a real design decision (parameterize vs. enforce one policy),
meeting the `/domain-modeling` ADR bar.

## Expected: `refactor-design` pass

Run `/refactor-design` against the issue. It should:

1. Not treat the issue as already fully specified — an externally-labeled candidate is never assumed
   complete by its own claim (`refactor-design/SKILL.md` step 1).
2. Ground in the two implementations, grill toward the seam, and find the backoff-policy decision
   meets the ADR bar (`skills/refactor-design/references/decision-gate.md`).
3. Write a plan comment with a proposed default (parameterized policy, preserving both current
   contracts) and an explicit open question.
4. **Remove `ready-for-agent` from the issue's `Labels:` line** (it was pre-existing) and **add
   `needs-info`** — the regression this fixture exists to catch.
5. Explicitly note in the comment that a pre-existing `ready-for-agent` was found and removed.

## Expected: `refactor-scan` pass (after the design pass above)

With `docs/refactoring/bookkeeping.md`'s `Pending candidates` pointing at the issue, run
`/refactor-scan`. It should:

1. Read the issue's `Labels:` line: `needs-info` present, `ready-for-agent` absent.
2. Recognize this as "flagged and still waiting" (`refactor-scan/SKILL.md` step 2) — **not**
   resumable.
3. **Not** route the candidate to `refactor-implement`. On this fixture's Local Markdown (git-only)
   tracker, the pass stops here entirely, reporting the candidate is still waiting on
   `ready-for-agent`.

## The bug this regression-tests

Before ADR-0053, step 4 above never happened — a pre-existing `ready-for-agent` was left untouched,
so `refactor-scan`'s resume check in the second pass read it as already confirmed and routed
straight to `refactor-implement` without a human ever seeing the flagged question.

## Verified

Manually confirmed live against `opencode/muse-spark-1.2-contributor-free` on 2026-09-15 (PR #86,
against a throwaway `/tmp` copy of this same scenario) — both passes behaved exactly as described
above.
