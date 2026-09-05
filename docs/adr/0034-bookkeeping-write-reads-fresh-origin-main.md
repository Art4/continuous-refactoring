# `refactor-learn`'s closing bookkeeping write reads fresh `origin/main`, not the candidate branch's own stale view

A real gap observed live while reviewer-loop-watching `Art4/legacy-todo` (ticket 52): the closing
call's `Fulfilled nodes`/`Skip streak` write (`skills/refactor-learn/references/fulfilled-nodes-write.md`)
computed both fields against whatever the candidate branch's own local checkout happened to have, with
no instruction to check whether `origin/main` had moved on since that branch was created. Confirmed
twice in the same run: a maintainer rejected `phpstan-level-6` (a new `out-of-scope/phpstan-level-6.md`
on `main`); two candidate branches created *before* that merge each wrote a growing
`Skip streak: phpstan-level-6: N` entry for a node that was, by the time their MRs were reviewed,
already permanently closed — compounding with every subsequent pass built on the same stale
lineage. The same staleness class of bug is worse for `Fulfilled nodes`: its own "overwrite the whole
field with the parser's complete fulfilled-set" rule would silently drop a different node's entry that
only exists on `origin/main` because an unrelated sibling PR landed it after the branch forked — a
correctness bug, not just cosmetic drift, just not yet observed in the wild the way the skip-streak
one was. Settled via a `/grill-me` session (ticket 52).

## Considered Options

- **Narrow fix**: only add "never skip-streak a rejected node," without addressing why the parser run
  saw it as proposable in the first place. Rejected during grilling — treats the symptom, leaves the
  more serious `Fulfilled nodes` silent-drop risk (a real correctness bug, not just noise) completely
  unaddressed.
- **Merge `origin/main` into the candidate branch before writing.** Rejected — adds a merge commit to
  what should stay a small, mechanical fold-in diff, and entangles this reference file with git-history
  mechanics the write itself doesn't need to care about.
- **Rebase the candidate branch onto `origin/main` before writing.** Rejected — rewrites history on a
  branch that may already have an open, reviewed MR; conflicts with this suite's own standing "reverts
  and corrections always go through the normal MR workflow, never a rewrite" convention, even though
  strictly speaking this branch is the pass's own not-yet-merged work.

## Decision

**Read fresh, touch nothing else.** Before computing either field: `git fetch origin`, then
`git checkout origin/main -- docs/refactoring/out-of-scope/ docs/refactoring/bookkeeping.md` — syncs
only those two comparison inputs into the working tree from `origin/main`, skipping a path that
doesn't exist there yet. The candidate branch's own already-landed changes (whatever this pass
delivered) are untouched; no merge, no rebase, no commit added purely for this sync — it's a
working-tree read, and the closing call's own commit (as already happens today) is what actually
lands the corrected `Fulfilled nodes`/`Skip streak` values.

**Belt-and-suspenders rule added on top, not instead of the sync**: a node with an
`out-of-scope/<node>.md` entry (now correctly fresh) never gets a `Skip streak` entry, regardless of
what the parser's raw unblocked-check says. Guards the rare case something else still surfaces a
rejected node as unblocked, without being a substitute for fixing the actual staleness root cause.

## Consequences

Both the observed `Skip streak` drift and the not-yet-observed but real `Fulfilled nodes` silent-drop
risk are closed by the same fix. No `tooling_tree.py`/Python change — this lives entirely in
`fulfilled-nodes-write.md`'s prose, since the parser itself was already correct when run against
current state; the gap was purely about which state the write step chose to run it against.
`refactor-learn/SKILL.md` needs no change — its existing one-line pointer to this reference file
already covers "the algorithm," which now includes the fresh-sync step.
