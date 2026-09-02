# Never let deleting a branch be the only record that something happened

Rejecting a candidate mid-flight with no forge API access to formally close its merge request is not a license to delete the branch as "the practical equivalent" of closing it. A bookkeeping write not yet on the default branch (a ledger row, a `Fulfilled nodes` entry, an out-of-scope entry) that exists only on a branch about to be deleted is destroyed with it — taking the only record that a real merge request ever existed.

Before deleting or abandoning any such branch — the candidate's own, or a bookkeeping branch stacked on it — land the record of the abandonment first, through an ordinary bookkeeping branch/MR **off the default branch, never one stacked on the branch about to be deleted**: at minimum an `out-of-scope/<node>.md` entry in the Refactoring Notes (structural candidate: a closing note on the issue instead) stating what was abandoned and why.

If a bookkeeping write already sits stacked on the doomed candidate branch (this pass's early call, or an interrupted earlier one), cherry-pick that commit onto a fresh branch off the default branch before deleting anything beneath it.

Only delete the branch(es) after that record has merged. No time to complete the merge right now? Leave the branch undeleted — a stale unmerged branch costs nothing; a silently vanished merge request does.
