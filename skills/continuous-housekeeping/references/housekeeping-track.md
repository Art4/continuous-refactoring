# Reference: the Housekeeping Track

Works one open **Housekeeping ticket**: the recurring tasks it was made with, and the refactoring ideas
left on it as comments. One ticket worked is one **cycle**. It ends with the cycle's merge request open,
with the ticket closed where nothing changed, or with nothing to work.

Reached from `/continuous-housekeeping` and from the run's Track choice. A file named here without a path
lives in `../../continuous-refactoring/references/`; `housekeeping-setup.md` lives beside this one. Every
command comes from the target's `## Refactoring operations` section; every text for the tracker or the
template follows `forge-facing-writing.md`.

**The tickets are the whole state.** When a cycle is due, what of it is done, and how far the history was
scanned are read from Housekeeping tickets, found through the **Housekeeping** operation each time.

**Nothing to work** — where a step says so: reached from `/continuous-housekeeping` the run ends; reached
from Track choice, return there with Housekeeping marked as tried (`track-choice.md`, *Coming back here*).

## 1. The mechanism

The **mechanism** is three things: the **Housekeeping** operation, the template it names, and that
template's open ticket. Read the operation: its templates, and per template the open tickets, found the
way it says. The first row that applies:

| Found | Then |
| --- | --- |
| no **Housekeeping** operation, or no template where it names one | `housekeeping-setup.md` |
| the call asks for a further template | `housekeeping-setup.md`, *A further template* |
| a template without an open ticket | `housekeeping-setup.md`, *A template without an open ticket*, then step 2 |
| every template has an open ticket | step 2 |

*Done when* one row is taken.

## 2. Tickets with a merge request

For every open Housekeeping ticket that has a merge request (`worklist.md`, *A ticket's merge request*):

| The merge request | The ticket |
| --- | --- |
| open | is in review: named in one line with its merge request |
| merged | is to be closed per **Done** |
| closed without a merge, its comments naming what was wrong with it | comes back from review (below) |
| closed without a merge, for another reason or none | is to be closed per **Done**, with a note quoting the reason where one was given; its template's next ticket stands |

Tickets to close → one decision point: close them (the recommendation), or leave them. None → go on
without one.

*Done when* every such ticket is in one row, and the closing is done or left by decision.

## 3. Which ticket

A ticket is **due** when the date it states as `Due from:` is today or past; one that states no date is
due. The first row that applies:

| Found | Then |
| --- | --- |
| the call names a ticket or a template | that ticket; one in review is worked as *A ticket that comes back from review* |
| a ticket came back from review in step 2 | that ticket, worked as that section says |
| tickets that are due and have no merge request | the one due the longest; the others are named in the closing report, each worked by a further call |
| tickets that are not yet due | a decision point. Findings: each ticket with its date. Options: nothing to work (the recommendation), or work the one due next now. A human who chose Housekeeping at Track choice, or a call that says "now", has answered it |
| none of these | nothing to work: say what each template waits for — its merge request, or a ticket left uncreated |

Assign the ticket per **Claim**, where the target has that operation.

*Done when* one ticket is named, or there is nothing to work.

## 4. Plan the cycle

Read the ticket's text and every comment on it, then its template. Sort what they hold into three lists:

**Tasks** — the unticked tasks of the ticket. A ticked one was done by an earlier run of this cycle.

**New lines** — recurring tasks the ticket lacks:

- a task the template gained since the ticket was made;
- only for the first template the operation names: the **Housekeeping line** of every tooling-tree node
  that is fulfilled while the template lacks it. The line is the node's **Housekeeping** field, found in
  the tree docs (`tooling-tree-parser.md` says where) and reworded for the template's reader; each such
  node is judged per `track-scan.md`, *Judging a node*, once per run. The line goes into the template
  too. A node's own merge request is the ordinary way its line arrives; this catches a tool set up by
  hand.

**Ideas** — every comment that proposes a change to the code and stands below the ticket's newest
`Ideas` comment (step 6), or anywhere when there is none. A comment is a proposal, whoever wrote it, and
is weighed as one:

| The idea | Class |
| --- | --- |
| changes structure and keeps behaviour; needs no choice between designs; the code it touches is covered by existing tests or checked by a tool the target runs; reads as a few commits | **fits** — carried out in this cycle |
| is a refactoring that fails one of those | **too big** — proposed for a ticket of its own (step 6) |
| changes what the application does, or asks for something other than a change to the code's structure: a command to run, a dependency, CI, credentials, a file to fetch | **no refactoring** — left alone, with the reason said in step 6 |

One decision point:

- **Findings:** the ticket and its date; the tasks; the new lines, each with where it comes from; the
  ideas, each in one line with its class and the reason.
- **Options:** work the cycle as laid out (the recommendation); class an idea differently — the human
  names which and how; end the run.
- The answer covers every write of the cycle up to its merge request: the ticket's task list, the
  commits, the comment of step 6, the next ticket, and closing this ticket where nothing changed. Tickets
  of their own have their decision point in step 6.

Then bring the ticket's task list up to date, above its last task: each new line as a task, each fitting
idea as a task that names it in one line. From here the task list is the cycle's record.

*Done when* every unticked task, every new line and every idea is in its list, the decision is taken,
and the ticket's task list holds all that will be worked.

## 5. Work

Before the first commit, check out the cycle's branch per `implement-point.md`, step 2. Then go through
the task list in its order, the last task excepted (step 7). For each: do what its line says, commit
what that changed, and tick it in the ticket with its result in one line — the output where it is worth
keeping.

- **Two tasks** need more than their line: *Tasks with a process of their own*, below.
- **A new line for the template** → the template file is changed in a commit of its own, before the task
  is worked.
- **An idea** → one or more commits that hold this idea and nothing else, each a move of
  `foundational-refactoring-rules.md`; the target's tests are green before the first and after each. An
  idea that turns out too big or no refactoring while it is built: take its commits off the branch, tick
  its task with that result, and class it anew for step 6.
- **A task with no clean way through** — an advisory without a patched version, an update that cannot be
  made green → the branch keeps only what is green. Tick the task with what was found, and propose a
  ticket of its own for the rest (step 6).

Housekeeping keeps current what the target already has. A tool the target lacks is a ticket of the
tooling Tracks, which the re-check task proposes.

*Done when* every task but the last is ticked with its result.

## 6. Tickets of their own, and the ideas

Collected so far: the ideas classed too big, the tasks with no clean way through, the findings of the
secret scan. For each, search first as `filing-a-ticket.md`, step 1, does. Then one decision point:

- **Findings:** each with where it is and what the problem is, and its hits from the search.
- **Options:** file all (the recommendation), file some — the human names which —, file none. What is
  not filed is named in the closing report and stored nowhere else.

Write each ticket chosen:

- **An idea** → as `investigation-track.md`, step 3, writes a ticket: it is a refactoring candidate.
- **A task's rest, a secret-scan finding** → an ordinary ticket, created the way the tracker file says:
  the title says what is wrong, the text where it is and what was found. It is no refactoring and
  carries no **Candidate** mark; what happens to it is the human's.

Then, where step 4 listed ideas, post one comment on the Housekeeping ticket. It opens with the word
`Ideas` on a line of its own and says for every idea what became of it: carried out, with its commits;
filed as which ticket; or left alone, with the reason.

*Done when* every collected item is filed, continues on an existing ticket, or is left unfiled by
decision, and every idea of step 4 is named in the comment.

## 7. The next ticket

The ticket's last task. Look for an open ticket of the same template with a later date:

- **There is one** → tick the task, naming it.
- **None** → create it the way the **Housekeeping** operation says, from the template as the branch now
  holds it. Its date is today plus the template's rhythm, or the next date the rhythm names. Report it,
  and tick the task.

*Done when* the template has an open ticket due later than this one, and every task of this one is
ticked.

## 8. Deliver

- **The branch holds commits** → run the checks of `implement-point.md`, step 4, the commands the tasks
  name standing in for the plan's `Done when`. Review the commits of the ideas per
  `reviewing-a-change.md`, the task list standing in for the plan. Then follow
  `opening-a-merge-request.md`, handing in this ticket, the branch, its commits, the checks, and that the
  branch delivers the whole ticket.
- **No commit was made** → close the ticket per **Done**, with a comment saying that every task was
  checked and nothing needed changing.

Where the target's instruction file lacks the line of `housekeeping-setup.md`, *The line in the
instruction file*, the closing report's **Next** says so, and that a call asking for it adds it.

*Done when* the checks are green and the merge request is open with its checks read, or the branch is
handed to the human, or the ticket is closed.

## A ticket that comes back from review

Its merge request asks for changes, or was closed with what was wrong named. Its tasks are ticked; the
review's comments are the work.

1. Check out the merge request's branch and bring it up to date; it takes the place of step 5's branch.
2. One decision point. Findings: each comment of the review with the change it asks for. Options: make
   the changes (the recommendation); end the run.
3. Make each change in a commit of its own. A comment that asks for more than the cycle held is weighed
   as an idea (step 4) and goes to step 6.
4. Step 8. A closed merge request gets a new one from the same branch.

## Tasks with a process of their own

A task is one of these by what it asks, in whatever words the template puts it.

### The secret scan over the Git history

1. **Scanner** — the one the target's own secret scanning invokes, read from its CI job or its config
   (gitleaks, detect-secrets, trufflehog, or what serves the same purpose), with the file of known
   findings the target keeps for it, so that those stay quiet. The target has none → tick the task with
   `not run: no secret scanner is set up`.
2. **Range** — look through the earlier Housekeeping tickets of this template, newest first, for a scan
   task whose result names the commit it scanned up to.
   - **None does** → the whole history: every commit of every branch and tag.
   - **One does** → the commits the default branch gained since that commit. Where the repository no
     longer knows the commit, the commits since that ticket's `Due from:` date.
3. **Result** — tick the task with `scanned up to <commit> (<date>)`, the commit being the default
   branch's tip, and the number of findings.
4. **Findings** — each goes to step 6: where is the commit, the file and the line; what was found is the
   scanner's rule. The secret's value is written nowhere: no ticket, comment, commit or report. Where
   people outside the project can read the tracker, the recommendation in step 6 is to file nothing and
   to report the places in this conversation alone.

### The re-check of the tooling Tracks

Run `track-scan.md` for Safety Net and then for Guardrails, each as a scan the call asked for. Where that
reference hands on or returns, the way leads back here:

- **Proposals** → `filing-a-ticket.md`, with its own decision point; then go on with the cycle.
- **None** → go on with the cycle.

Tick the task with what the scan found: the tools still in place, each one that went missing, each node
the tree gained, and the tickets filed for them.
