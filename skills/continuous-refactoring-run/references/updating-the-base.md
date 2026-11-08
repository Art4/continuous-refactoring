# Reference: updating the base

A **base update** brings the branch of an open merge request of the suite onto the current default branch, so it
can merge again. Reached from Track choice, when the worklist holds a ticket that needs one (`track-choice.md`, *A
base update first*), and from the implement point, step 2, for a branch it works anyway. Handed in: the ticket, its
merge request or branch, and what blocks it. Commands come from the tool the target's **Merge requests** operation
names; every text for the forge follows `forge-facing-writing.md`.

Decision points here are laid out as `../SKILL.md`, *Decision points*, says.

## A blocked merge request

Read from the forge, after `git fetch`. A merge request is **blocked** when one of these holds:

| Blocker | GitHub (`gh pr view <n> --json mergeable,mergeStateStatus`) | GitLab (`glab mr view <n> -F json`) |
| --- | --- | --- |
| a **conflict** | `mergeable` is `CONFLICTING`, or `mergeStateStatus` is `DIRTY` | `has_conflicts` is true, or `detailed_merge_status` is `conflict` |
| **behind**, and the forge refuses to merge it so | `mergeStateStatus` is `BEHIND` | `detailed_merge_status` is `need_rebase` |
| a **stale base** | CI is red in a file the branch does not touch, and `git merge-base --is-ancestor origin/<default> origin/<branch>` fails | the same |

Another forge: its own merge state where its tool shows one; otherwise a conflict that
`git merge-tree --write-tree origin/<default> origin/<branch>` reports. A branch with no merge request, where
**Merge requests** says `none`: the same command on the local branch.

- **Behind with nothing refusing it** is not blocked: every update starts CI again, so the branch stays as it is.
- **A state the forge is still computing** (GitHub `UNKNOWN`, GitLab `checking` or `unchecked`) → read it again
  after a minute; still computing → not blocked this time, and the closing report says so.
- **The human's hold** — a draft the human set (`opening-a-merge-request.md`, *Draft and ready*) — is not blocked.
- **Handed over by a base update** (step 6) is not blocked again until a commit lands on its branch or a human
  comments after the handover.

Several blocked → the merge request whose ticket another ticket names as its blocker first, then the oldest. After
each update, the others are read again.

## 1. The decision point

Reached from the implement point → no decision point here: the implement point's own covers it; go to step 2.

- **Findings:** the merge request, its blocker, and for a conflict the files `git merge-tree` names.
- **Options:** update it (the recommendation); skip it, and go back to where the run came from — Track choice, or
  the Housekeeping Track — with it counted as in review; end the run.

*Done when* the answer is taken.

## 2. Rebase or merge

Check the branch out, up to date with its remote, and note its remote tip. Rebase onto `origin/<default>` when both
hold:

- the target updates branches that way: the default branch's history is linear, the forge merges by fast-forward or
  rebase, or earlier merge requests were rebased rather than given merge commits of the default branch;
- every commit in `origin/<default>..<branch>` has the author this run commits as.

Otherwise merge `origin/<default>` into the branch, with the message the target's earlier merges of this kind use.
Unclear → merge: it rewrites nothing.

*Done when* the rebase or merge has started.

## 3. Resolve

Each conflicting file, the first row that applies:

| The conflict | Resolved by |
| --- | --- |
| in output of a tool — a commit that is a tool's run, as the implement point builds a tooling or rewrite ticket | taking the default branch's side and running the tool again with the same command; its run replaces that commit |
| any other, where the intent of both sides can be kept | hand: the file does what the default branch changed and what the branch changes |
| both sides changed the same logic so that keeping both needs a decision, or their intents contradict | nothing: abort (`git rebase --abort`, `git merge --abort`), push nothing, and go to step 6 |

**Drift.** With or without a conflict, the default branch may have gained callers of what the branch renames, moves
or deletes. Search its new commits for the old names, as the implement point does after a rename (step 3), and fix
each hit in a commit of its own.

*Done when* every file is resolved and the rebase or merge is complete, or the run is at step 6.

## 4. Checks

Run every check of `implement-point.md`, step 4, on the updated branch; a red check is fixed there as it says. The
same check red after a second attempt → step 6: nothing is pushed.

A conflict resolved by hand → the diff of the resolved files is reviewed per `reviewing-a-change.md`, and a finding
to fix is fixed and checked again. Under the Driver its own review follows, once the run reports it.

*Done when* every check passed after the last commit, and a hand resolution is reviewed.

## 5. Push

- **Rebased** → `git push --force-with-lease=<branch>:<the remote tip from step 2>`.
- **Merged** → a plain push.

Draft or ready stays as it was.
- **Refused**, because someone pushed in between → fetch, and from step 2 again: that commit is not this run's, so it
  is a merge now.

Reached from the implement point → push nothing here: the merge-request step pushes with the rest of the work, and
the comment below is posted after that push.

A conflict that was resolved gets one comment on the merge request: the files, what on the default branch it
collided with (a merge request or a commit), and how it was resolved — the tool run again, or by hand, keeping
what. An update with no conflict gets none: the push shows it. Then read the forge's checks as
`opening-a-merge-request.md`, step 4, says.

*Done when* the push is on the forge and its checks are read.

## 6. Handed to the human

The branch stays as it was on the forge. One comment on the merge request — or, where there is no forge, on the
ticket — names the files, says in plain words what each side changes and why the two cannot both be kept without a
decision, and asks how to go on. Without an answer, nothing changes: the merge request stays open and is not
blocked again (*A blocked merge request*).

*Done when* the comment is posted.

## The end

Reached from Track choice, or handed to the human, the run ends here. Its Status line names the merge request and how
the update ended: with no conflict, the tool run again, resolved by hand, or handed to the human. Otherwise, reached
from the implement point, the run goes on with it.

Updating the base is done when the branch is on the default branch's tip with its checks read, or handed to the
human.
