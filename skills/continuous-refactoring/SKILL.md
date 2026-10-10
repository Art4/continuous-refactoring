---
name: continuous-refactoring
description: One run of the skill suite — from the open refactoring tickets to an opened merge request. Asks you at every decision, or decides by itself when you say so in the call.
disable-model-invocation: true
---

# Continuous Refactoring

One **run**: a chain of **decision points** that leads from the target's open tickets to one opened merge
request. The suite keeps no state of its own. Tickets, merge requests and rejections are found by searching
the target's tracker and forge on every run, through the **Refactoring operations** in the target's
`docs/agents/issue-tracker.md` (`references/refactoring-operations.md`).

## The call

The call's free text may state any of these; read it before step 1 and say back in one sentence what was
understood.

| The call states | Effect |
| --- | --- |
| the **autonomous** mode ("do it yourself", "without asking") | every decision point takes its recommendation |
| a **Track** | the Track choice is answered; the run stays in that Track and ends when it has nothing workable |
| a **ticket** | Track and ticket are chosen: the run works that ticket, and ends if it turns out not to need work |
| a **restriction** ("only the Rector nodes") | the worklist, the scan, the filing and the selection hold only what it covers |

Nothing stated → the run is **interactive** and unrestricted.

## Decision points

A decision point lays out three things, in this order: the **findings**, the **options**, and **one
recommendation** with its reason in a few words. Every write to the target's tracker, forge or files
follows from one; everything before the run's first decision point is read-only.

- **Interactive** → first post the findings as a message in this conversation: a question dialog shows
  the human only its own fields, so what is not in a message was not shown. Then ask and wait — the
  options, the recommendation first, in one `AskUserQuestion` call where that tool exists, as numbered
  prose otherwise. The question refers only to what the message before it shows.
- **Autonomous** → take the recommendation, and say in one sentence that it was taken.
- **Switching** → the human saying mid-run that the suite should carry on by itself makes the run
  autonomous from the next decision point on.
- **Nobody answers** — the run is interactive and the question cannot be put to a human or comes back
  unanswered → the run ends here. Its report is the decision point itself: findings, options,
  recommendation. Nothing is written.
- **A change to the target's `AGENTS.md`** is asked of a human in an autonomous run too; unanswered, it
  stays undone and the report says so.

What the call already states is the human's answer to the choice it addresses. A write that choice did
not cover — closing a named ticket found fulfilled — is still laid out.

Decision points happen in this conversation. A step that only reads and judges may run in a subagent,
handed its reference and returning its result; the subagent asks nothing and writes nothing.

## A clean working tree

A run works on a working tree that `git status --porcelain` shows as clean. Check it twice: after the
onboarding interview wrote, and before the implement point checks out its branch. Files the target
ignores do not show there and need nothing.

Anything shown → a decision point. Findings: the files, and for each whether this run wrote it. Options:

- **Deliver them first** (the recommendation, where this run wrote every one of them): commit them on a
  branch of their own, open its merge request per `references/opening-a-merge-request.md`, and go on.
- **The human tidies up**, and says when the run may go on.
- **End the run.**

A file this run did not write is the human's work in progress: the suite commits none of it, the
recommendation is that the human tidies up, and an autonomous run ends here naming the files.

## The run

Read `references/reporting-progress.md` before the first sentence to the human.

1. **Ready.** No Git repository → the run ends with that message. Read `docs/agents/issue-tracker.md`:
   the `## Refactoring operations` section is missing, or lacks **Search**, **Done** or **Merge
   requests** → run `references/onboarding-setup-interview.md` inline. Its summary is this run's first
   decision point. The interview wrote the section and verified **Search** → check the working tree (*A
   clean working tree*, above), then one more decision point: go on with the run now (recommended), or
   end here. Anything else → the run ends with the interview's
   report.
   *Done when* the section carries the three required operations.

2. **Worklist.** Build the worklist per `references/worklist.md`.
   *Done when* every open ticket found has a Track and a state.

3. **Reconcile.** Follow `references/reconcile.md`.
   *Done when* every finding is acted on or left as decided, or there was none.

4. **Track choice.** Follow `references/track-choice.md`. It ends the run, or names one Track:
   - **Safety Net** or **Guardrails** → step 5.
   - **Housekeeping** → the run continues in `../continuous-housekeeping/references/housekeeping-track.md`
     and ends where that reference ends, unless it comes back here with Housekeeping marked as tried.
   - **Investigation** → the run continues in `references/investigation-track.md`, which hands a selected
     ticket to step 8.

   *Done when* a Track is named or the run has ended.

5. **Scan** — only when the Track has no trace yet (`references/worklist.md`, *A Track's trace*), or the
   call asked for a scan. Follow
   `references/track-scan.md`.
   *Done when* that reference's last step is.

6. **File tickets** — only when step 5 left proposals. Follow `references/filing-a-ticket.md`.
   *Done when* that reference's last step is.

7. **Select.** Follow `references/selection.md`.
   *Done when* one ticket that still needs its work is handed on, or the run is back at step 4 with the
   Track marked as tried.

8. **Design.** Hand the selected ticket to `references/design-point.md`.
   *Done when* the ticket carries an implementable plan, or the run has ended with the open question or
   the finding named.

9. **Implement.** Hand the planned ticket to `references/implement-point.md`.
   *Done when* a branch holds the change and its checks are green.

10. **Merge request.** Follow `references/opening-a-merge-request.md`.
    *Done when* the merge request is open, or the prepared branch is handed to the human.

## The end of a run

A run ends when its merge request is open or its branch is handed to the human, when the design cannot
proceed without a human answer or finds that the ticket is no refactoring, when nothing is workable, or
at a decision point nobody answered.

Close with two lines, each claim confirmed during this run:

- **Status:** what the run did and where it ended.
- **Next:** what the human can do now — review and merge, answer the open question, or call again.
