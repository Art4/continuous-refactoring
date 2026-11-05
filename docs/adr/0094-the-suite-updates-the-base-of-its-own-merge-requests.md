# The suite updates the base of its own merge requests

> Amends [ADR-0073](0073-a-run-is-a-chain-of-decision-points.md): parallel merge requests that conflict are no
> longer the developer's to resolve; the suite brings a blocked merge request onto the default branch itself, and
> hands over only a conflict that needs a decision.

Every merge request of the suite starts from the default branch, and nothing limits how many are open. Once one
merges, another may conflict. Nothing noticed: the Driver's *Ready* picked up an open merge request only when the
human had answered on it, its review read checks but not the forge's merge state, and a run saw the ticket as in
review and passed it by. The human had to point it out, and the docs said resolving it was theirs.

pstack's `babysit` playbook was looked at for this. It reports a conflict and leaves the rebase to the branch's owner,
and its watcher is GitHub-only; the suite is that owner. What it gave: conflicts come before review threads and
those before CI; the forge's merge verdict counts, not a list of green checks; CI red in code the diff does not touch
points to a stale base; an update without a textual conflict still needs its checks, since the default branch may
have grown callers of what the branch moves; force-push only one's own branch, with a lease.

## Decision

- **Blocked** is the forge's verdict: a conflict, a branch behind that the forge refuses to merge (a rule that
  branches be up to date, a fast-forward merge method), or CI red from a stale base. A branch merely behind is left
  alone: every update starts CI again.
- **A run** gives a ticket whose merge request is blocked the state *needs base update*. It comes before every Track
  choice, an interactive run asks first, and the run ends with that merge request.
- **The Driver** has every blocked merge request updated in a run of its own before each round, and before it stops
  done, paused or ended. A handed-over merge request is updated too.
- **Rebase or merge** follows the target's history; rebase only a branch of the suite's own commits, pushed with
  `--force-with-lease`. Unclear → merge, which rewrites nothing.
- **Resolving** is graded. A conflict in a tool's output: run the tool again, then the checks. No textual conflict:
  the checks. By hand: the checks and a new review, the Driver's under the Driver.
- **A conflict that needs a decision** — the same logic changed on both sides, or opposite intents — pushes nothing;
  a comment asks the human what to keep, and the merge request is not taken up again until something changes on it.
- **A base update is neither a rework nor a round, and has no limit.** A conflict says nothing about the merge
  request, and a new one needs a new merge first, so it cannot loop.

## Considered Options

- **Adopt `babysit`.** Rejected: it never rebases, depends on `poteto-mode`, Bugbot and a GitHub-only watcher, and
  opens every pull request ready, never as a draft.
- **Only report the conflict.** Rejected: the human already sees it on the forge; the gap was the suite not acting.
- **Update whenever the branch is behind.** Rejected: CI and review start again with every move of the default
  branch, for a merge request that would merge cleanly.
- **Count a base update as a rework.** Rejected: a good merge request would go to the human only because the default
  branch moved.
- **Always rebase / always merge.** Rejected: a target's history has its own convention, and rebasing a branch with
  someone else's commits rewrites their work.

## Consequences

- A new reference, `updating-the-base.md`, holds the blocked check and the procedure; the worklist, Track choice,
  the implement point, the Housekeeping Track and the Driver point to it.
- Forges other than GitHub and GitLab are checked only for conflicts Git itself finds; without a forge, a local
  branch is checked only when a run works on it.
- A rebased branch is force-pushed. The lease and the own-commits rule keep that to the suite's own work.
