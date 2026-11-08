# Reference: the design point

Ends with an **implementable plan** on the selected ticket: what changes, where, in which order, and the
check that shows the work is done — enough for someone who has only the ticket. Handed in: the ticket, its
Track, the run's mode, the call's restriction, and for a tooling ticket the Stage's slug and its Tool's `details` file.
Every plan keeps `foundational-refactoring-rules.md` and weighs `principles.md`; every text for the ticket follows
`forge-facing-writing.md`.

Decision points here are laid out as `../SKILL.md`, *Decision points*, says.

## 1. Read the ticket

Read its text and all its comments, oldest first. The first row that applies:

| The ticket | Then |
| --- | --- |
| arrived with its merge request and the review's comments | the plan it carries stands → the implement point |
| is waiting on an open question (*Open questions*, below) | interactive: put the question to the human here, and treat the reply as *An answer arrived*. Autonomous, or unanswered: the run ends with the question named |
| has an answer after its open question (*Open questions*) | *Open questions*, *An answer arrived* |
| is a baseline ticket | `planning-a-baseline-ticket.md` decides whether its newest plan still stands |
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

- **Autonomous** → the suite plans by itself. Say so in one sentence; this is no decision point.
- **Interactive** → a decision point, every time. Findings: each fitting skill with its description in a
  few words, the `AGENTS.md` sentence, or that neither exists. Options: each of them; the suite's own
  planning; **the human plans in a session of their own**. Recommendation: what `AGENTS.md` names; else
  the fitting skill installed in the target itself; else the fitting skill that comes from elsewhere;
  else the suite's own planning.
- **The human plans** → the run ends. The closing report names the ticket, what a plan on it has to state
  (step 1, *carries a plan*), and that a later run takes the ticket up from there. This is also the way
  to a skill only the human can call: the conversation does not list it, so the suite cannot run it.

The answer holds for this ticket in this run and is written nowhere: the next run looks again.

*Done when* it is said who plans.

## 3. Plan

- **The target's skill** → run it with this brief: the ticket; for a tooling ticket the Role's Purpose,
  the Stage's Fulfilment check and MR scope from its Tool's `details` file; `foundational-refactoring-rules.md`; and the
  outcome wanted — the plan on the ticket. In an autonomous run the suite answers the skill's questions
  with its own recommendation; one that meets the bar of step 4 goes there instead.
- **The suite's own** → the section below that names the ticket: *Planning a tooling ticket*,
  `planning-a-baseline-ticket.md`, or *Planning any other ticket*.

*Done when* a plan exists, in this conversation or already on the ticket, or step 4 took over.

## 4. Two findings that change the ending

Check both as soon as planning is over, whoever planned.

**The work cannot be done without changing behaviour.** A refactoring keeps what the target observably
does; this ticket would change it. Lay it out as a decision point — findings: what would change for whom,
and why no behaviour-keeping way exists. Options:

- **Leave the decision to a human** — the recommendation: post the finding as an open question (*Open
  questions*) asking whether the ticket is declined as refactoring or becomes feature work, with the
  `Opener:` lines the plan would have carried (step 5, *Decisions*). The ticket waits until someone replies. An autonomous run takes this option, so a rejection is always a human's.
- **Record a rejection** with that finding as the reason (`rejection.md`): the ticket's subject is
  declined as refactoring; the reason says it is feature work.

A branch that already holds work for the ticket is named in the record or the comment, and stays until
that is written. Act on the answer; the run ends with the finding named. No plan is written.

**A decision meets the ADR bar** while the work stays behaviour-keeping: it is hard to reverse, surprising
without its context, and a real trade-off between alternatives. A ticket whose plan carries such a
decision unanswered is a **flagged candidate**.

- **Interactive** → a decision point: the question, the alternatives, the one recommended. The answer goes
  into the plan under `Decisions`.
- **Autonomous** → the plan takes a default, named as such under `Decisions`, and the question is left on
  the ticket (*Open questions*). The run ends at step 5 with the question named.

*Done when* both were checked, and each one found is decided or left as an open question.

## 5. Put the plan on the ticket

A plan the target's skill already wrote onto the ticket stands as it is. Otherwise the plan is this
step's decision point — findings: the plan in full. Options: post it and go on to the implementation (the
recommendation); post it and end the run, because the human implements it in a session of their own;
change it; end the run. Where the human implements, the closing report names the ticket, the plan's
comment and the branch name the implement point would use (`implement-point.md`, step 2), so that a later
run finds the branch or its merge request and continues there. Post it as one comment that opens with the line `Plan`, holding:

- **What changes and where** — files, modules, configuration, in the target's own names.
- **Slices**, in the order they are built, each small enough for one commit or a few.
- **Done when** — the commands that must pass.
- **Decisions** — every question of this design that met the ADR bar, with its answer: the ticket's
  **decision trail**; it also names each principle (`principles.md`) that changed a decision. For each Tool on request that is not
  in place, has no ticket and is not rejected (the parser's `tools`), whose Opener in its `details` file this
  plan meets, one more line: `Opener: <tool> — <why>`, with the Tool's key from its Pack. Where the target keeps ADRs or a glossary (`implement-point.md`, *Slices every
  kind of ticket can have*), each decision that belongs there is also a slice.
- **This merge request** — only when the plan covers a part of the ticket: which part, and what stays.

An open question is posted after the plan, so that it is the ticket's newest comment.

Where the target has **Ready after plan**, run it once the `Plan` comment is posted, whichever way the run
goes on (the implementation, or the human implementing in a session of their own). Run it only for a plan
this step posted, and not while an open question follows the plan: the answer's new plan runs it. If it
fails, the run goes on and the closing report names the command.

*Done when* the ticket carries the plan and goes to the implement point, or the run has ended with the
open question or the finding named.

## Open questions

An **open question** is a comment that opens with the words `Open question` on a line of its own, then:
the question, the default the plan took and why — on a ticket filed with its question
(`filing-a-ticket.md`), the default the suite recommends —, and one sentence saying that a reply as a
comment on this ticket answers it.

An **answer** is a comment newer than the open question that opens with neither `Plan` nor `Open
question`, the two forms the suite posts while a ticket waits. The content decides, never the account
that wrote it: an agent often posts with the human's own account.

**Waiting.** A ticket is waiting while its newest open question has no answer after it. The first answer
ends the wait; nothing else is set or removed.

**An answer arrived.** Read every answer:

| The answer | Then |
| --- | --- |
| confirms the default | the plan stands → the implement point; a ticket without a plan yet → step 2, the default taken |
| declines the ticket's subject | record the rejection with the answer as its reason (`rejection.md`); the run ends with it named |
| names another way, concretely enough to plan with | plan again with it (steps 2 to 5) and post the new plan |
| leaves the question open, or raises a further one | interactive: put it to the human here. Autonomous: post it as a new open question; the run ends with it named |

## Planning a tooling ticket

The Stage's entry in its Tool's `details` file is the specification: **MR scope** says what the merge request holds, the
**Fulfilment check** when it is done. Read both, then the target, and write the plan for this target: the
real paths, the existing CI file, the package manager's commands, the tool's current version. A Tool with
a **Housekeeping** field gets one more slice for it (`implement-point.md`, *Slices every kind of ticket
can have*).

Before the slices, estimate the size of what the scope holds — the tool's dry run on the target, or a
count of the files — and weigh it against `principles.md`, *A merge request a person can review*. Where
one merge request is too much, the plan is cut into parts, listed in order, and *This merge request* names
the first; a later run works the first part whose commits are not yet on the default branch.

*Done when* every part of the MR scope is a slice (or belongs to a listed part), the size and the cut or
its absence are stated in a sentence, and `Done when` repeats the Fulfilment check as commands.

## Planning any other ticket

A structural candidate or a ticket a human wrote. Its plan names six things: the **deepened module**
(what it becomes, its one job, what disappears behind it), the **seam** (the public edge its tests
observe through), the **interface** (what it exposes — smaller than what it hides), **locality** (what
moves together and what must stay put), the **tests that survive** (which stay, which are rewritten,
which are new at the seam), and the **pin** (the Pinning Test that holds today's behaviour at the seam
before structure moves: its kind — a characterization test, a snapshot or an equivalence script — and
what it holds; a type check or a linter is none. Where the area already has tests that reach the code the
slices touch, the pin is those tests, named; otherwise it is new and is the plan's first slice). Where
the seam gives an output that can be compared — text, a file, data — and the reshape reaches over several
slices behind it, the pin is an equivalence script that runs the old and the new side on the target's own
sample inputs (fixtures, example files, inputs of its tests; never production data) and compares the
outputs; the plan says in one sentence why it chose it or why not. No threshold decides this, the agent
judges it. Where the target has no usable input, the pin is of another kind.

1. **Ground.** Read the code the ticket names, the target's glossary and the ADRs of that area, and the
   target's `Refactoring goal` line where it has one (`structural-candidate-search.md`, step 1). *Done
   when* you can say in two sentences why this spot causes friction; the review later measures reader load
   against those sentences.
2. **Settle the six, in rounds.** Open are the questions whose prerequisites are settled. Find facts in
   the code yourself, and a fact that shows only when something runs — behaviour, output, timing — by
   running something that changes nothing in the target (its tests, a command, a throwaway script outside
   the tree), not by asking; put each decision with its alternatives and one recommendation — interactive: all
   open ones of a round to the human in one message, numbered; autonomous: take the recommendation,
   unless the question meets the ADR bar (*Two findings*). An answer may open further questions: next round.
3. **A pin that costs too much.** Where the behaviour cannot be held at the seam at a reasonable cost, no
   plan is written for it: the pin's kind and the reason go under `Decisions`, and the question is an
   open question (*Open questions*) — put to the human in an interactive run, left on the ticket in an
   autonomous one. The agent judges the cost; there is no fixed threshold.
4. **Check against the goal.** With a `Refactoring goal`: the design moves the code towards it, or the
   plan says why it does not.
5. **A Ratchet.** Where the target's tooling holds a Ratchet that records where its worst value sits (the
   PHPMD limits' `Current peak` comments) and a file the slices touch is named there, the plan lists the
   Ratchet slice (`implement-point.md`, *Slices every kind of ticket can have*) and its `Done when` says
   which limit is expected to fall.

*Done when* all six are named, no question is open, and the slices follow the moves of
`principles.md`, *Technique vocabulary*.
