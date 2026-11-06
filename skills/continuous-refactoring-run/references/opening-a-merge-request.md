# Reference: opening the merge request

The last link of a run: the branch with green checks becomes an open merge request, or is handed to the
human where there is no forge. Used by the run and by the Housekeeping Track. Handed in: the ticket (a branch
of `own-pack.md` has none), the branch, its commits, the checks that ran, whether the branch delivers the whole ticket or a part, and where there is one the fact the change is safe
because of with how far it was proved, and the review's notes.
Commands come from the tool the target's **Merge requests** operation names; the description follows
`forge-facing-writing.md`. Towards the human, say the forge's own word (pull request on GitHub).

Every decision point here is laid out as `../SKILL.md`, *Decision points*, says: the findings go into the
conversation as a message of their own, then the question — in an autonomous run, then the recommendation
taken.

## 1. Is there one already?

Search the forge's merge requests for one from this branch — the implementing skill may have opened it,
or the ticket came in review.

- **An open one** → the decision point is only about pushing the new commits. One that is not a draft — opened
  by the implementing skill, or ready from an earlier verdict — is made a draft first, new commits or not, with
  its comment (*Draft and ready*); then step 4.
- **None** → step 2.
- **No forge** — **Merge requests** says `none`, or the remote cannot be reached → step 5.

*Done when* one of the three is taken.

## 2. The decision point

- **Findings:** the branch, its commits in one line each, the checks that ran, the title and the
  description as they would be posted.
- **Options:** push and open it as a draft (the recommendation); change title or description; leave the branch
  unpushed for the human.
- **Left for the human** → step 5.

*Done when* the answer is taken.

## 3. Push and open

Push the branch and open the merge request against the default branch as a draft: `gh pr create --draft`,
`glab mr create --draft`, or the forge's own way (*Draft and ready*).

**Title** — what the change does for the project, in the target's own convention for titles.

**Description**, in this order:

1. One or two sentences for a reader who knows the project and has never heard of the skill suite: what
   the project gains.
2. The ticket. A branch that delivers the **whole** ticket refers to it the way **Linked merge request**
   says, so that merging closes it; without that operation the ticket is named in plain words. A branch
   that delivers a **part** — a baseline ticket with entries left, or a tooling ticket whose plan was cut —
   names the ticket with the word "part"
   and uses no closing reference, and says what stays. A branch with no ticket leaves this point out.
3. What changed, which checks ran and passed — and a gate that could not run locally, left to CI — and for
   code changes which tests cover it. For a structural
   ticket: the pin, and that it passed before the change (for an equivalence script: on how many inputs old
   and new gave the same output, or that no usable input was found and another pin was used), and in plain words where the code became
   easier to follow. The review's notes, each in a sentence: what was seen and why it was left.
4. Where the implement point named one: why the change is safe, in plain words — the one fact, and how
   far it was proved (read in the source, shown that the bad case cannot occur, run, reproduced), or that
   it is not proved and what a reviewer should check.
5. Decisions of the plan, each in a sentence, with the ADR's path where one was committed.
6. A recurring task this branch added to the Housekeeping template, in one line; where the branch created
   the template, say that too.

*Done when* the merge request is open, the forge shows it as a draft (`gh pr view <n> --json isDraft`,
`glab mr view <n> -F json`, field `draft`), and it is reported with its link. Opened ready all the same → make it a
draft now.

## 4. The forge's checks

Where the target runs CI on merge requests, read its result from the forge.

| CI | Then |
| --- | --- |
| green | done; a run alone marks it ready |
| red | a finding for the implement point: fix on the branch, push, read again |
| no pipeline for the push, where earlier merge requests had one | the target's CI skips drafts: mark it ready so CI runs, say so in a comment and the closing report, and read again |
| still running when everything else is done | the closing report says so; the merge request stays open, and a run alone marks it ready |
| cannot be read | the closing report says so and names the checks that ran locally; a run alone marks it ready |

A **run alone** is one the Driver did not call: the call does not say `under the Driver`. Its own review ran before
the merge request opened. Under the Driver the merge request stays a draft until the Driver's verdict.

A claim in the closing report that something is open, fixed or green is read from the forge in this step,
after the last push.

*Done when* one row holds for the last push.

## Draft and ready

A merge request of the suite is a **draft** while the suite does not think it can merge, and **ready** once it
does. A forge without drafts, or **Merge requests** `none`, skips all of this.

| | GitHub | GitLab |
| --- | --- | --- |
| open as a draft | `gh pr create --draft` | `glab mr create --draft` |
| mark it ready | `gh pr ready <n>` | `glab mr update <n> --ready` |
| make it a draft again | `gh pr ready <n> --undo` | `glab mr update <n> --draft` |

**Making a ready one a draft** always comes with a comment on the merge request that says why: the request for
changes, the question, the work that is going on. A base update leaves draft or ready as it found it.

**Whose draft.** A draft is the suite's when it opened the merge request as a draft and it was never ready since, or
when the newest change to draft came with a comment of the suite saying why. Any other draft is the human's
**hold**: the suite leaves that merge request alone — no review, no rework, no base update — until the human marks
it ready or comments on it. The forge's timeline shows the changes (GitHub
`gh api repos/{owner}/{repo}/issues/<n>/timeline`, entries `convert_to_draft` and `ready_for_review`; GitLab the
system notes "marked this merge request as draft" and "as ready"). The account is no help here: the suite often
works under the human's own.

## 5. No forge, or left for the human

The branch stays local as prepared; nothing takes the place of the merge request. Post one comment on the
ticket naming the branch and what it holds — coming from step 1, this comment is the decision point:
post it (the recommendation), or leave the ticket untouched. In a target without a forge, later runs read the branch name
there and treat the ticket as in review until the branch is merged (`worklist.md`, *A ticket's merge
request*); elsewhere the next run finds the branch and continues with it. The closing report names
the branch and the human's two ways on: merge it into the default branch themselves, or push it and open
the merge request once a forge is there. A branch with no ticket posts nothing: the closing report is its record.

*Done when* the closing report can name the branch and both ways.

Opening the merge request is done when it is open with its checks read, or the branch is handed over.
