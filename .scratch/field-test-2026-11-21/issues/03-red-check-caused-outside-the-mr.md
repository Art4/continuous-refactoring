# 03 — A red check the merge request did not cause

Type: task
Status: open
Blocked by: —

**What was seen**

The Driver's step 3 says "A red check is a request for changes". Twice in one run the red check came from outside the
merge request's scope, so no rework of that merge request could fix it:

1. A CI matrix extended to PHP 8.4/8.5 failed in PHPStan on an implicit nullable type in code the ticket kept out of
   scope.
2. A new workflow's merge request failed in a coverage upload shared by all matrix jobs (a closed build on the
   coverage service).

Both times the review improvised the same verdict: "ask the human" — should the cause be fixed in a separate merge
request this one is rebased onto? The question was posted on the merge request, as the skill wants. Then, with no
answer on the forge:

- in case 1 a ticket and a merge request for the cause appeared and were merged, and the first merge request was
  updated from the default branch and judged mergeable;
- in case 2 the merge request was updated from the default branch, the upload happened to pass, and it was judged
  mergeable while the cause stayed (later removed by the maintainer).

"An open question stays the human's" was not kept, or the question was answered in the Driver's session; not
known.

**Open**

- A rule for this case: e.g. file a ticket for the cause, keep the merge request a draft, blocked by it; ask only
  where the fix is no refactoring.
- When an open question on a merge request counts as settled: by the human only, or also when its cause is gone.

## Comments
