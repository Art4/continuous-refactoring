# Reference: merging a merge request

The Driver's verdict is mergeable and its Merge setting is `merge`.

1. **CI.** Wait for it to go green. Red is a request for changes (`../SKILL.md`, step 4). A project with no CI relies
   on the checks the review ran.
2. **Merge** with the method the repository uses, read from its settings or its history. Note the branch's tip and the
   files it touched first, since a forge may delete the branch on merge. The branch stays for now.
3. **A stacked child.** Search the forge for an open merge request whose base is this branch: a forge closes one
   silently when its base is deleted. One found → retarget it onto the default branch, with a comment on it saying
   why, or keep the branch where it cannot be retargeted. The check runs at every merge, since a human can stack one
   by hand.
4. **Landed.** A merge reported as done proves nothing: a conflict can resolve to the wrong side with no error. Fetch,
   and compare the files the branch touched on the default branch with the branch's tip:
   `git diff <tip> origin/<default> -- <files>` is empty, or holds only what another merge request merged since.
   Anything else → comment on the merge request what differs, and stop (`../SKILL.md`, *Stops*). The correction is the
   human's call, as a normal merge request, a revert or a fix; history stays as it is, with no force-push.
5. **Tidy.** Delete the branch unless step 3 kept it, pull the default branch, delete the merged local branch.

*Done when* the merge landed and the default branch is checked out and up to date, or the Driver has stopped.
