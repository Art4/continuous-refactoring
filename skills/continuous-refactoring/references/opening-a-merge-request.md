# Reference: opening the merge request

The last link of a run: the branch with green checks becomes an open merge request, or is handed to the
human where there is no forge. Used by the run and by the Housekeeping Track. Handed in: the ticket, the
branch, its commits, the checks that ran, and whether the branch delivers the whole ticket or a part.
Commands come from the tool the target's **Merge requests** operation names; the description follows
`forge-facing-writing.md`. Towards the human, say the forge's own word (pull request on GitHub).

## 1. Is there one already?

Search the forge's merge requests for one from this branch — the implementing skill may have opened it,
or the ticket came in review.

- **An open one** → the decision point is only about pushing the new commits; then step 4.
- **None** → step 2.
- **No forge** — **Merge requests** says `none`, or the remote cannot be reached → step 5.

*Done when* one of the three is taken.

## 2. The decision point

- **Findings:** the branch, its commits in one line each, the checks that ran, the title and the
  description as they would be posted.
- **Options:** push and open it (the recommendation); change title or description; leave the branch
  unpushed for the human.
- **Left for the human** → step 5.

*Done when* the answer is taken.

## 3. Push and open

Push the branch and open the merge request against the default branch.

**Title** — what the change does for the project, in the target's own convention for titles.

**Description**, in this order:

1. One or two sentences for a reader who knows the project and has never heard of the skill suite: what
   the project gains.
2. The ticket. A branch that delivers the **whole** ticket refers to it the way **Linked merge request**
   says, so that merging closes it; without that operation the ticket is named in plain words. A branch
   that delivers a **part** — a baseline ticket with entries left — names the ticket with the word "part"
   and uses no closing reference, and says what stays.
3. What changed, which checks ran and passed, and for code changes which tests cover it.
4. Decisions of the plan, each in a sentence, with the ADR's path where one was committed.
5. A recurring task this branch added to the Housekeeping template, in one line; where the branch created
   the template, say that too.

*Done when* the merge request is open and reported with its link.

## 4. The forge's checks

Where the target runs CI on merge requests, read its result from the forge.

| CI | Then |
| --- | --- |
| green | done |
| red | a finding for the implement point: fix on the branch, push, read again |
| still running when everything else is done | the closing report says so; the merge request stays open |
| cannot be read | the closing report says so and names the checks that ran locally |

A claim in the closing report that something is open, fixed or green is read from the forge in this step,
after the last push.

*Done when* one row holds for the last push.

## 5. No forge, or left for the human

The branch stays local as prepared; nothing takes the place of the merge request. Post one comment on the
ticket naming the branch and what it holds — coming from step 1, this comment is the decision point:
post it (the recommendation), or leave the ticket untouched. In a target without a forge, later runs read the branch name
there and treat the ticket as in review until the branch is merged (`worklist.md`, *A ticket's merge
request*); elsewhere the next run finds the branch and continues with it. The closing report names
the branch and the human's two ways on: merge it into the default branch themselves, or push it and open
the merge request once a forge is there.

*Done when* the closing report can name the branch and both ways.

Opening the merge request is done when it is open with its checks read, or the branch is handed over.
