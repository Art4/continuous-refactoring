---
name: continuous-refactoring
description: One run of the continuous-refactoring skill suite — from the project's open refactoring tickets to an opened merge request. Asks at every decision, or decides by itself when the call says so. Use when asked to run continuous refactoring or the skill suite on this project, or to work one of its Tracks or tickets, or to build a Pack of the project's own for a tool the suite does not know.
---

# Continuous Refactoring

One **run**: a chain of **decision points** that leads from the target's open tickets to one opened merge
request. The suite keeps no state of its own. Tickets, merge requests and rejections are found by searching
the target's tracker and forge on every run, through the **Refactoring operations** in the target's tracker
file (`references/refactoring-operations.md`).

## The call

The call's free text may state any of these; read it before step 1 and say back in one sentence what was
understood.

| The call states | Effect |
| --- | --- |
| the **autonomous** mode ("do it yourself", "without asking") | every decision point takes its recommendation |
| a **Track** | the Track choice is answered; the run stays in that Track and ends when it has nothing workable |
| a **ticket** | Track and ticket are chosen: the worklist and reconcile hold that ticket alone, the run works it, and ends if it turns out not to need work |
| a **restriction** ("only the Rector Stages") | the worklist, the scan, the filing and the selection hold only what it covers |
| a **Pack** of the target's own, or a tool the suite does not know | after step 1 the run continues in `references/own-pack.md` instead of step 2, and ends where that reference ends |

Nothing stated → the run is **interactive** and unrestricted.

## Decision points

A decision point lays out three things, in this order: the **findings**, the **options**, and **one
recommendation** with its reason in a few words. Every write to the target's tracker, forge or files
follows from one; everything before the run's first decision point is read-only.

- **Interactive** → first post the findings as a message in this conversation: a question dialog shows
  the human only its own fields, so what is not in a message was not shown. Then ask and wait — the
  options, the recommendation first, in one call of the environment's multiple-choice question tool
  (Claude Code: `AskUserQuestion`, Cursor: `AskQuestion`, OpenCode: `question`) where the agent has
  one, as numbered prose in the last message otherwise. The question refers only to what the message
  before it shows. A tool reply that no human gave (skipped, declined, or auto-answered because nobody
  is there) is no answer: ask again as numbered prose, and if that goes unanswered, **Nobody answers**
  applies.
- **Autonomous** → post the same findings message a human would get, then one sentence naming the
  recommendation taken, and only then act on it. Nobody answers, so the message is the record: a reader
  who comes later learns from it what was found and why the run went the way it did.
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

A run works on a working tree that `git status --porcelain` shows as clean. Check it before the implement
point checks out its branch. Files the target ignores do not show there and need nothing.

Anything shown → a decision point. Findings: the files, and for each whether this run wrote it. Options:

- **Deliver them first** (the recommendation, where this run wrote every one of them): commit them on a
  branch of their own, open its merge request per `references/opening-a-merge-request.md`, and go on.
- **The human tidies up**, and says when the run may go on.
- **End the run.**

A file this run did not write is the human's work in progress: the suite commits none of it, the
recommendation is that the human tidies up, and an autonomous run ends here naming the files.

## The run

Read `references/reporting-progress.md` before the first sentence to the human.

1. **Ready.** No Git repository → the run ends with that message. Find the tracker file: read `AGENTS.md`
   and `CLAUDE.md` for it (`references/refactoring-operations.md`, *The tracker file*). A name that leaves
   the repository → the run ends, naming it. The two name different files → a finding, and the run goes on.
   Every call of the parser hands it this path (`references/tooling-parser.md`). Read the tracker file:
   the `## Refactoring operations` section is missing, or lacks **Search**, **Done** or **Merge
   requests** → run `references/onboarding-setup-interview.md` inline. Its summary is this run's first
   decision point. The run ends after the interview whatever its outcome — it does not go on to the
   worklist, and it does not ask who commits what. The final report says the onboarding is complete (or
   what ended it), names the files the interview wrote and any other change in the working tree, and
   recommends committing them and then calling the skill again; a call for a Pack adds that the Pack is still
   to come. The section is complete but has no
   **BC promise** bullet → `references/onboarding-setup-interview.md`, *The BC promise alone*, then go on.
   *Done when* the section carries the three required operations, and the BC promise was asked about.

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

A run ends when its merge request is open or its branch is handed to the human, when the review leaves no slice
that makes the code easier to follow, when a fix does not hold after two attempts, when the design cannot
proceed without a human answer or finds that the ticket is no refactoring, when nothing is workable, or
at a decision point nobody answered.

Close with two lines, each claim confirmed during this run:

- **Status:** opens with how many things wait for the human, or that none does; then what the run did and
  where it ended. A run that reviewed a branch also names what the review dismissed, each with its reason.
- **Next:** what the human can do now — review and merge, answer the open question, or call again. Each
  thing that waits gets its recommendation and what happens if nobody answers.
