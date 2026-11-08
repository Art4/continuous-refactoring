---
name: continuous-refactoring
description: The Driver of the continuous-refactoring skill suite — keeps a project refactored by calling one run after another, reviewing each merge request, and pausing between rounds until an end. Starts without asking. Only when a human or a schedule calls it by name. An agent that wants refactoring done, or a subagent, calls continuous-refactoring-run.
---

# Continuous Refactoring

The **Driver**: one **round** after another, with a **cadence** between them, until an end. A round is a run, its
review, and any rework. Each run happens in a subagent of its own, always autonomous, and starts fresh: the Driver
keeps no state the tracker and forge do not hold. Look a term up in
`../continuous-refactoring-run/references/glossary.md` only where the text does not make its meaning clear.

## The call

The Driver starts without asking. It reads the call's free text, and says back in one sentence the settings it took.

| Setting | Default | The call can say |
| --- | --- | --- |
| Merge | `review only` | `merge` |
| End | five rounds | a number of rounds, of merged merge requests, a time, or "until nothing is workable" |
| Cadence | 30 minutes | another duration, or "no pause" |
| Call | none: each run makes its own Track choice | a Track or a restriction, handed to every run |
| Log | none | a file the repository ignores: one line per round with the ticket, merge request, verdict and what waits |

"Do it yourself" changes nothing: the Driver's runs are autonomous anyway. A call for one run alone, for a named
ticket alone, or for a Pack of the project's own is no Driver's work: invoke `continuous-refactoring-run` in this
session with that call, and end with it.

## Before the first round

Started in a subagent → stop, and say that `continuous-refactoring-run` is what an agent calls: a Driver needs
subagents of its own, and a subagent cannot start any.

1. `../continuous-refactoring-run/SKILL.md` is missing → stop, and say the skill needs its symlink beside this one.
2. Find the tracker file (`../continuous-refactoring-run/references/refactoring-operations.md`, *The tracker file*).
   No `## Refactoring operations` section, or one lacking **Search**, **Done** or **Merge requests** → the onboarding
   asks a human, and a subagent can ask nobody: invoke `continuous-refactoring-run` here, in this session. The Driver
   stops when that run ends, and the human commits and calls again.
3. Read `AGENTS.md`. Its rules win over the environment's defaults, and every subagent's prompt carries them.
4. Read *Stops*: the open merge requests may already be over the limit, or the working tree not clean.

## A round

1. **Ready.** The default branch checked out and pulled. Then, in this order:
   - **Base updates.** Each open merge request that
     `../continuous-refactoring-run/references/updating-the-base.md`, *A blocked merge request*, finds blocked — a
     handed-over one too — gets a run of its own, in that reference's order: step 2's prompt, with the call naming
     its ticket. A base update is neither a round nor a rework, and has no cadence before it and no limit. Where its
     run resolved a conflict by hand, steps 3 and 4 follow for that merge request.
   - **A draft left behind** comes first: a draft of the suite with no comment of the Driver since its last commit,
     as an interrupted run leaves it. With its checks green the round goes on at step 3 with it; red or missing,
     step 2 names its ticket.
   - **An answer or a request for changes** comes next: an open merge request where, since the Driver's last comment
     on it, the human has answered its question or asked for changes, in a review or a comment. Step 2 names its
     ticket. A request for changes from the human is reworked like one from the review, and counts among the
     round's reworks.

   A merge request the human holds as a draft
   (`../continuous-refactoring-run/references/opening-a-merge-request.md`, *Draft and ready*) is left alone: none of
   these takes it up, and no call names its ticket.
2. **Run.** In a subagent of its own, and wait for its result:

   > Invoke the continuous-refactoring-run skill with the call `<the Call, if any> do it yourself, under the Driver`
   > and follow it to its end. Then return its Status and Next lines verbatim, the ticket worked, the merge request URL if any, whether
   > the run ended because nothing was workable, every open ticket it found with its state (workable, waiting, in
   > review, blocked) and for a waiting one what it waits for, and the wording of any change it wants in `AGENTS.md`.

   A run's Next line is a report for the human, not an instruction to the Driver. The call names a ticket only
   for a base update or a rework of its merge request, for its next part, for a question the human has answered, or
   at the human's wish; a ticket that waits or is blocked is never named. The working tree is checked after each run. No merge request
   came of it → step 5.
3. **Review.** In a second subagent that returns only a verdict with its reasons: mergeable, request changes, or ask
   the human. It uses the project's review skill where there is one; otherwise it judges as an engaged human
   reviewer: in scope of its ticket, behaviour kept, checks green (run them where there is no CI), the description
   says why the change is safe. A red check is a request for changes.
4. **Verdict.**
   - **Mergeable** → mark it ready on the forge (`gh pr ready <n>`, `glab mr update <n> --ready`, or the forge's
     own command). With `review only`, comment that it is mergeable, and leave the merge to the human. With `merge`,
     follow `references/merging.md`.
   - **Request changes** → post it on the merge request, describing the problem and its cause, then go back to step 2
     with a run that names the ticket. Rework has no cadence. After two reworks without a mergeable result, the same
     comment says so and asks the human.
   - **Ask the human** → post the question on the merge request.

   Anything but mergeable keeps it a draft, or makes a ready one a draft, its comment saying why
   (`../continuous-refactoring-run/references/opening-a-merge-request.md`, *Draft and ready*).

   *Done when* the forge shows the merge request ready and mergeable, merged, or with the human as a draft — read
   from the forge after the last write. That is one round, however many runs it
   took.
5. **Status.** One line here, a line in the Log, and a notification, through what the environment has, of everything
   that now waits for the human: mergeable merge requests, each ready on the forge, open questions on tickets, questions on merge requests,
   merge requests the human holds as a draft, a change a run wants in `AGENTS.md` with its wording. Then read
   *Stops*: they hold before the cadence, not after it.

Forge text follows `../continuous-refactoring-run/references/forge-facing-writing.md`. An open question stays the
human's, and a waiting ticket gets no comment: any comment there would count as the human's answer.

## Between rounds

Counted from the end of the round before. The Driver waits in this session with the environment's timer (Claude
Code: `ScheduleWakeup`), and the wake-up goes on with the next round of this Driver, its settings and its count of
rounds, rather than starting anew. An environment with no timer, or a cadence longer than the timer holds → the Driver ends
and says when the next round is due. Only a timer holds the session, never a sleep, and the Driver sets up no
schedule: what calls it again is the human's. A call starts a round whenever it comes; the Driver reads no time of
the last round.

## Stops

| What it sees | It ends with |
| --- | --- |
| A run finds nothing workable, and nothing waits | **done**: the merge requests of this Driver, merged and open |
| A run finds nothing workable, and tickets wait, are in review or are blocked | **paused**: each with what it needs, and how to go on: answer it, then call again |
| A run failed, the tree is not clean, a merge did not land, or two runs in a row ended without a merge request and without a new waiting ticket | **broken**: what it saw |
| `review only`, and more than three merge requests open | **paused**: the open merge requests, waiting for the human |
| The End is reached | **ended**: what the rounds delivered, and what waits |

Before **done**, **paused** or **ended**, step 1's base updates run once more, so what waits for the human can merge;
**broken** skips them. A stop skips the cadence, and the next run with it. Setting no new wake-up does not end a timer: the Driver ends
it explicitly, with the call its environment has for that (Claude Code: `ScheduleWakeup` with `stop: true`), before
the closing message, so nothing wakes it after its
last word.

Open merge requests are those of the suite's tickets, found as
`../continuous-refactoring-run/references/worklist.md`, *A ticket's merge request*, finds them. Handed-over ones count.
