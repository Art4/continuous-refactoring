# Never let deleting a branch be the only record that something happened

Rejecting a candidate mid-flight with no forge API access to formally close its merge request is not a license to delete the branch as "the practical equivalent" of closing it. Whatever is left of the candidate exists only on that branch and in the merge request, and deleting the branch destroys the only record that a real merge request ever existed.

Before deleting or abandoning any such branch — ordinarily the candidate's own — record the abandonment first, in the Refactoring Notes, which the suite writes in place and never commits: at minimum an `out-of-scope/<node>.md` entry stating what was abandoned and why (structural candidate: a closing note on the issue instead), written for the target repo's own reader (`../../continuous-refactoring/references/forge-facing-writing.md`).

Only delete the branch after that record is written. No time to complete it right now? Leave the branch undeleted — a stale unmerged branch costs nothing; a silently vanished merge request does.
