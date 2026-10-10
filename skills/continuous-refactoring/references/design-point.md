# Reference: the design point

Ends with an **implementable plan** on the selected ticket: what changes, where, in which order, and the
check that shows the work is done — enough for someone who has only the ticket. Handed in: the ticket, its
Track, the run's mode, the call's restriction, and for a tooling ticket the node's slug and tree-doc file.
Every plan keeps `foundational-refactoring-rules.md`; every text for the ticket follows
`forge-facing-writing.md`.

## 1. Read the ticket

Read its text and all its comments, oldest first. The first row that applies:

| The ticket | Then |
| --- | --- |
| arrived with its merge request and the review's comments | the plan it carries stands → the implement point |
| is waiting on an open question (*Open questions*, below) | interactive: put the question to the human here, and treat the reply as *An answer arrived*. Autonomous, or unanswered: the run ends with the question named |
| has comments newer than its open question, none of them a plan | *Open questions*, *An answer arrived* |
| is a baseline ticket | *Planning a baseline ticket* decides whether its newest plan still stands |
| carries a plan, and no newer comment asks for a change to it | the plan stands → the implement point |
| anything else | step 2 |

A ticket **carries a plan** when its text or a comment states what changes, where, and how the result is
checked. A plan the suite wrote is a comment that opens with the word `Plan` on a line of its own; where a
ticket has several, the newest counts.

*Done when* one row is taken.

## 2. Who plans

Look at two places: the skills on offer in this conversation apart from the suite's own two, and what
the target's `AGENTS.md` says about how work is planned. A skill fits here when its description says it
turns a piece of work into a plan or a specified ticket.

- **A skill fits, or `AGENTS.md` names a way** → a decision point. Findings: each fitting skill with its
  description in a few words, and the `AGENTS.md` sentence. Options: each of them, and the suite's own
  planning. Recommendation: what `AGENTS.md` names; else the fitting skill installed in the target
  itself; else the fitting skill that comes from elsewhere.
- **Neither** → say in one sentence that the suite plans by itself; this is no decision point.

The answer holds for this ticket in this run and is written nowhere: the next run looks again.

*Done when* it is said who plans.

## 3. Plan

- **The target's skill** → run it with this brief: the ticket; for a tooling ticket the node's Purpose,
  Fulfilment check and MR scope from its tree-doc file; `foundational-refactoring-rules.md`; and the
  outcome wanted — the plan on the ticket. In an autonomous run the suite answers the skill's questions
  with its own recommendation; one that meets the bar of step 4 goes there instead.
- **The suite's own** → the section below that names the ticket: *Planning a tooling ticket*, *Planning a
  baseline ticket*, or *Planning any other ticket*.

*Done when* a plan exists, in this conversation or already on the ticket, or step 4 took over.

## 4. Two findings that change the ending

Check both as soon as planning is over, whoever planned.

**The work cannot be done without changing behaviour.** A refactoring keeps what the target observably
does; this ticket would change it. Lay it out as a decision point — findings: what would change for whom,
and why no behaviour-keeping way exists. Options:

- **Record a rejection** with that finding as the reason (`rejection.md`) — the recommendation. The
  ticket's subject is declined as refactoring; the reason says it is feature work.
- **Leave the decision to a human**: post the finding as an open question (*Open questions*) asking
  whether the ticket becomes feature work. The ticket waits until someone replies.

A branch that already holds work for the ticket is named in the record or the comment, and stays until
that is written. Act on the answer; the run ends with the finding named. No plan is written.

**A decision meets the ADR bar** while the work stays behaviour-keeping: it is hard to reverse, surprising
without its context, and a real trade-off between alternatives.

- **Interactive** → a decision point: the question, the alternatives, the one recommended. The answer goes
  into the plan under `Decisions`.
- **Autonomous** → the plan takes a default, named as such under `Decisions`, and the question is left on
  the ticket (*Open questions*). The run ends at step 5 with the question named.

*Done when* both were checked, and each one found is decided or left as an open question.

## 5. Put the plan on the ticket

A plan the target's skill already wrote onto the ticket stands as it is. Otherwise the plan is this
step's decision point — findings: the plan in full. Options: post it (the recommendation), change it, end
the run. Post it as one comment that opens with the line `Plan`, holding:

- **What changes and where** — files, modules, configuration, in the target's own names.
- **Slices**, in the order they are built, each small enough for one commit or a few.
- **Done when** — the commands that must pass.
- **Decisions** — every question of this design that met the ADR bar, with its answer: the ticket's
  **decision trail**. Where the target keeps ADRs or a glossary (`implement-point.md`, *Slices every
  kind of ticket can have*), each decision that belongs there is also a slice.
- **This merge request** — only when the plan covers a part of the ticket: which part, and what stays.

An open question is posted after the plan, so that it is the ticket's newest comment.

*Done when* the ticket carries the plan and goes to the implement point, or the run has ended with the
open question or the finding named.

## Open questions

An **open question** is a comment that opens with the words `Open question` on a line of its own, then:
the question, the default the plan took and why, and one sentence saying that a reply as a comment on
this ticket answers it.

**Waiting.** A ticket is waiting while its newest comment is an open question. Any newer comment ends the
wait; nothing else is set or removed.

**An answer arrived.** Read every comment newer than the question:

| The answer | Then |
| --- | --- |
| confirms the default | the plan stands → the implement point |
| names another way, concretely enough to plan with | plan again with it (steps 2 to 5) and post the new plan |
| leaves the question open, or raises a further one | interactive: put it to the human here. Autonomous: post it as a new open question; the run ends with it named |

## Planning a tooling ticket

The node's tree-doc file is the specification: **MR scope** says what the merge request holds, the
**Fulfilment check** when it is done. Read both, then the target, and write the plan for this target: the
real paths, the existing CI file, the package manager's commands, the tool's current version. A node with
a **Housekeeping** field gets one more slice for it (`implement-point.md`, *Slices every kind of ticket
can have*).

*Done when* every part of the MR scope is a slice and `Done when` repeats the Fulfilment check as
commands.

## Planning a baseline ticket

"PHPStan Level N: shrink the baseline" stays open until the baseline is empty, and takes one merge
request after another. Each run plans the next **part**.

1. Read `phpstan-baseline.neon` and group its entries by root cause: the same message pattern and
   identifier, across files. `$db might not be defined` in nine files is one group.
2. The ticket's newest plan names a group that still has all its entries → that plan stands, and no new
   one is written.
3. Otherwise pick this merge request's part, and give it a name of two or three words: the group that touches input from outside the application
   first; else the group one fix removes the most entries of. A group too large to review in one merge
   request is cut by file, and the plan names the files of this part.
4. Read every file of the part and plan the fix that removes the finding at its cause. Entries are
   removed by fixing code; an `ignoreErrors` entry moved elsewhere or an inline ignore is no fix.
5. `Done when`: the baseline, regenerated, no longer holds the part's entries and holds no new one, and
   the test suite is green. `This merge request` names the part and counts the entries that stay.

A group that only a behaviour change could remove is skipped and named in the plan under `Decisions`.
When only such groups are left, the first of the *Two findings* applies: the baseline cannot become
empty, so the level above cannot be raised. The rejection recorded is that of the next level's node,
with this as its reason (`rejection.md` then deals with the levels above it), and the baseline ticket is
closed with a note pointing to it.

## Planning any other ticket

A structural candidate or a ticket a human wrote. Its plan names five things: the **deepened module**
(what it becomes, its one job, what disappears behind it), the **seam** (the public edge its tests
observe through), the **interface** (what it exposes — smaller than what it hides), **locality** (what
moves together and what must stay put), and the **tests that survive** (which stay, which are rewritten,
which are new at the seam).

1. **Ground.** Read the code the ticket names, the target's glossary and the ADRs of that area, and the
   `Refactoring goal` line in the target's `AGENTS.md` where it has one. *Done when* you can say in two
   sentences why this spot causes friction.
2. **Settle the five, in rounds.** Open are the questions whose prerequisites are settled. Find facts in
   the code yourself; put each decision with its alternatives and one recommendation — interactive: all
   open ones of a round to the human in one message, numbered; autonomous: take the recommendation,
   unless the question meets the ADR bar (*Two findings*). An answer may open further questions: next round.
3. **Check against the goal.** With a `Refactoring goal`: the design moves the code towards it, or the
   plan says why it does not.

*Done when* all five are named, no question is open, and the slices follow the moves of
`foundational-refactoring-rules.md`.
