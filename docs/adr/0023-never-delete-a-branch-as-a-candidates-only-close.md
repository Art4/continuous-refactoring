# Never delete a branch as the only record that a candidate was closed

> Amends [ADR-0011](0011-bookkeeping-goes-through-its-own-merge-request.md): the dedicated bookkeeping
> branch/MR discipline decided there stays exactly as decided — this ADR adds a rule for what must happen
> *before* any branch carrying an unmerged bookkeeping write gets deleted or abandoned.
>
> Interacts with [ADR-0015](0015-suite-merge-requests-always-stack.md): the always-stack rule is what let a
> bookkeeping branch end up stacked *on* a candidate branch in the first place — the incident below happened
> because deleting the candidate branch took its stacked bookkeeping child down with it.

A real run against `continuous-refactoring.de` (no `gh`/`glab`/API token configured, so merge requests can be
pushed for real but never formally closed via the API) surfaced a genuine data-loss incident. A candidate
(CI Runner) had its merge request opened for real on the forge (`!6`), with a `refactor-learn` early call's
ledger row for it stacked on a bookkeeping branch that had not yet merged to the default branch. Mid-pass,
the human decided against the candidate. Lacking any way to formally close `!6` on the forge, the acting
agent deleted the candidate branch and its stacked bookkeeping branch as "the practical equivalent" of
closing it — reasoning explicitly recorded in the pass's own transcript. That deletion destroyed the only
copy of the ledger row recording `!6` ever existed, before it had ever reached the default branch. The next
pass's `refactor-scan` reconciliation step had nothing to detect (the row was never on the branch it reads),
so it re-proposed CI Runner from scratch and rejected it fresh — the real, now-orphaned merge request `!6`
left dangling on the forge, unreferenced by anything in the repository going forward.

## Decision

Before deleting or abandoning any branch that carries a bookkeeping write not yet on the default branch —
the candidate's own branch, or a bookkeeping branch stacked on it per ADR-0015's always-stack rule — land
the record of the abandonment first, through an ordinary bookkeeping branch/MR opened off the default
branch, **never one stacked on the branch about to be deleted**. At minimum: a
`docs/refactoring/out-of-scope/<node>.md` entry for a tooling-tree candidate, or a closing note on the issue
for a structural one, stating what was abandoned and why. If a bookkeeping write already sits stacked on the
doomed branch, cherry-pick that commit onto the fresh branch before deleting anything beneath it. Only
delete the branch(es) once that record has merged. No time to complete the merge right now? Leave the branch
undeleted — a stale unmerged branch costs nothing; a silently vanished merge request does. Stated inline in
`refactor-learn`'s `SKILL.md`, not cited by number there (per this suite's own "no unresolvable internal ADR
citation" convention, same as ADR-0011).

## Considered Options

- **Delete the branch, treat it as sufficient (status quo).** Rejected — this is the incident itself: a real
  merge request's only record destroyed before it ever reached the default branch, with no formal-close
  fallback for a target with no forge API access.
- **Never delete an abandoned branch at all, once rejected.** Rejected: once the abandonment's record has
  actually landed on the default branch, the branch itself carries no further information a human needs —
  keeping it around indefinitely is unnecessary clutter with no compensating benefit.
- **Extend `refactor-scan`'s reconciliation to notice a deleted branch and reconstruct what happened.**
  Rejected: by the time a branch is gone, whatever bookkeeping write it carried is unrecoverable — there is
  nothing left to reconstruct from. Prevention (this ADR) is the only point where the fact still exists to
  be saved.

## Consequences

`refactor-learn`'s intro paragraph states the rule directly, next to the bookkeeping-branch-discovery
addition it sits beside. No code or fixture changes — this is a process rule for the agent following the
skill, not a change to `tooling_tree.py`'s graph or detection logic. The concrete failure mode it closes: a
rejected candidate's real merge request becomes permanently unobservable by the suite because the only
record of its existence lived on a branch that got deleted before merging — after this rule, the
out-of-scope entry (or closing note) always lands first, so a later pass's reconciliation (or a human
reading the repository's history) can still see what was decided and why, even though the forge-side merge
request itself stays formally open and unreferenced (a target with no API access has no way to close it
remotely either way — this rule only prevents losing the *local* record of the decision, not the dangling
forge-side state, which is a separate, unaddressed gap).
