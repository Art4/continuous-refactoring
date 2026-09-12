# Abolish suite MR stacking; every suite branch always branches off the default branch

> Supersedes [ADR-0015](0015-suite-merge-requests-always-stack.md) outright — its own decision (stack
> a second suite branch on whatever's currently open, never parallel off the default branch) is fully
> reversed, not narrowed or amended. ADR-0015 itself superseded an even older conditional rule
> (ADR-0006: stack only when the new candidate is a tooling-tree child of what's in flight or the
> design depends on it, otherwise branch parallel) — this ADR does not revive that conditional
> middle ground; it goes further, abolishing stacking in every case, not just some.
>
> Does not affect [ADR-0028](0028-native-tracker-in-flight-bookkeeping-rides-the-candidate-branch.md):
> that ADR's own mechanism — a closing-call commit riding the *same*, already-checked-out candidate
> branch — was never a second branch basing on a first, so nothing about it depends on whether suite
> branches stack.
>
> [ADR-0023](0023-never-delete-a-branch-as-a-candidates-only-close.md)'s own rule (never delete a
> branch carrying an unmerged bookkeeping write without landing the record first) stays in force
> unchanged — see that ADR's own updated note. This decision only removes the one scenario that made
> its original motivating incident possible (a bookkeeping branch stacked *on* a candidate branch);
> the simpler case that rule still protects (a single candidate branch with its own unmerged write)
> is unaffected by whether stacking exists at all.

## Context

ADR-0015 traded a real, observed problem (two suite branches independently writing
`docs/refactoring/bookkeeping.md` in parallel, causing repeated merge conflicts) for a different,
recurring cost that has now surfaced twice, live, on the same watched target (`Art4/legacy-todo`),
caught by the human reviewer rather than the loop itself:

- PR #244, stacked on #243 — GitHub auto-closed #244 the moment #243 merged and its branch was
  deleted, with no warning. Re-opened by hand as #245.
- PR #264, stacked on #261 — the identical failure, weeks later, despite the first incident already
  being known and a reviewer-side mitigation ("check for a stacked child before deleting a branch")
  already having been identified as the fix. Re-opened by hand as #265.

Investigated before this decision (no code changes, a standalone analysis session): the two
incidents have different structural causes. #243→#244 was the *same* candidate (#240) across two
sequential steps — a bookkeeping early-call branch, then that candidate's own implementation branch
riding on it — with no real concurrency risk at all, since nothing else was ever going to touch
`bookkeeping.md` in that same narrow window. #261→#264 was two *genuinely independent* candidates
(#259 and #262), the second correctly stacking on the first per ADR-0015's own rule — exactly the
scenario that rule existed to protect. In neither case did the damage come from an actual
`bookkeeping.md` merge conflict — that risk never materialized either time. Both incidents' damage
came entirely from the forge's own auto-close-on-base-deletion behavior, a cost ADR-0015 introduced
that has now been paid twice for a benefit that has never once been needed in practice.

## Considered Options

- **Keep stacking, harden the reviewer's own branch-deletion procedure instead** (the mitigation
  identified after the first incident, #244). Rejected as the *sole* fix — it demonstrably failed:
  the same reviewer, aware of the exact risk, made the identical mistake again on #264. A safety net
  that depends entirely on a human (or an agent) remembering a special precaution, indefinitely,
  isn't a structural fix. (Its own value as an independent, cheap backstop is not rejected — see
  Decision below, and `docs/playbooks/reviewer-loop.md`.)
- **Keep the ADR-0015 always-stack rule, but abolish only the specific case that actually caused both
  incidents** (a candidate stacking on a bookkeeping-only early-call branch from the same pass, since
  that case never carries real concurrency risk — the genuinely-independent-candidates case would
  keep stacking). Rejected — this reintroduces exactly the case-by-case judgement ADR-0015 itself
  criticized in the conditional rule it replaced (ADR-0006): an agent (or reviewer) has to correctly
  classify which case applies, every time, itself a new failure surface. #261→#264 shows the
  "genuinely needs to stack" case doesn't actually need to stack either — the conflict it protects
  against never materialized there, only the auto-close risk did.
- **A granular `bookkeeping.md` structure that tolerates concurrent writes** (one file per field or
  per entry), removing the conflict risk without needing any branching-policy change at all. Rejected
  for the same reason ADR-0015 itself rejected it: disproportionate — it would ripple through every
  field (`Fulfilled nodes`, `Pending candidates`) for a conflict that, two real incidents later, still
  has never actually happened; the cheaper fix (accept an occasional conflict, resolve it by rebase)
  costs nothing until the rare day it's needed.
- **Abolish stacking outright, accept an occasional ordinary git merge conflict on `bookkeeping.md`
  as the cost.** Accepted. The "fewer than two suite MRs open" cap (`refactor-prioritize` step 1,
  unrelated to and unaffected by this decision) already limits how much is ever concurrently in
  flight; a real conflict, if one ever occurs, is visible and cheap to resolve by rebasing — nothing
  like the silent, surprising auto-close this decision removes.

## Decision

Every suite branch — a candidate's own, a dedicated bookkeeping branch, `loop-config`'s — always
branches directly off the default branch, unconditionally, regardless of whether another suite
branch is currently open, and regardless of whether the two would touch the same candidate, related
candidates, or entirely unrelated ones. `skills/continuous-refactoring/references/opening-a-merge-request.md`'s
"Basing" rule states this as the one, unconditional case — no exceptions, no "unless it's the same
candidate's own earlier step" carve-out (deliberately: see the second Considered Option above).

No replacement mechanism protects against two suite branches independently changing
`bookkeeping.md` at once. If it happens, the second one to merge conflicts, ordinarily, and a human
resolves it by rebasing — the same way any other git merge conflict gets resolved anywhere else in
this suite's own history.

Independent of this decision, `docs/playbooks/reviewer-loop.md` — the human/AI reviewer's own
procedure, not part of the continuous-refactoring suite's own skills — gains a standing rule: before
deleting any merged branch, check whether an open PR bases on it; retarget that PR (or leave the
merged branch undeleted) before deleting. This guards the same failure class regardless of this
ADR's own outcome — a manually-stacked branch, or any future reintroduction of stacking, still needs
it.

## Consequences

- `skills/continuous-refactoring/references/opening-a-merge-request.md`'s "Basing/stacking" rule
  (introduced by ADR-0015) is replaced by a plain "Basing" rule with no stacking case at all.
- ADR-0015 marked superseded, pointing here.
- ADR-0023 and ADR-0028 both updated with a note distinguishing what they said *at the time* (when
  stacking existed) from what still holds now — neither ADR's own core mechanism required stacking to
  exist, so neither needed a substantive reversal, only a wording correction.
- A future pass, human, or reviewer must not stack a second suite branch on a first for any reason,
  including "it's the same candidate's own next step" — that specific case was tempting to carve out
  as an exception and was explicitly considered and rejected above.
- The throughput cost ADR-0015 itself accepted (no two genuinely unrelated candidates in parallel) is
  lifted — two independent candidates may now both be in flight against the default branch at once,
  up to the existing two-MR cap, each merging independently without waiting on the other's merge
  order.
