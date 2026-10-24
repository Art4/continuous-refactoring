# Reference: setting Housekeeping up

Reached from `housekeeping-track.md`, step 1, when the mechanism is missing. It proposes the three parts
of the mechanism — the **Housekeeping template**, the **Housekeeping** operation, the first **Housekeeping
ticket** — and with them the line in the target's instruction file, and writes what a decision point
agreed to. A file named without a path lives in `../../continuous-refactoring/references/`.

Every decision point here is laid out as `../../continuous-refactoring/SKILL.md`, *Decision points*, says: the findings go into the
conversation as a message of their own, then the question — in an autonomous run, then the recommendation
taken.

## 1. Is a setup already on its way?

Run **Search** over the open tickets with the word `Housekeeping`, and look at each hit's merge request
or branch (`worklist.md`, *A ticket's merge request*):

- **It is open and adds a Housekeeping template** → the mechanism waits for that merge: name the ticket
  and its merge request; there is nothing to work (`housekeeping-track.md`).
- **It was closed without a merge, or the ticket has none, and the ticket lists recurring tasks to work**
  → that ticket is the first ticket of step 4.
- **The hit is something else** — a ticket about introducing Housekeeping, say → it is no first ticket.
  Name it among the findings of step 3 with a proposal for it: close it with a note pointing to this
  setup (the recommendation where the setup covers what it asks for), or leave it as it is.

*Done when* the search is read: a setup waits, a first ticket exists, or neither.

## 2. Read the target

- **A template that exists** — a file of the target that already lists recurring maintenance tasks. It is
  proposed as the template, its tasks kept, the parts of *The template* it lacks added.
- **The rhythm to recommend** — count the commits the default branch gained in the last 90 days: more
  than 300 → `daily`; 30 to 300 → `weekly`; fewer → `monthly`.
- **The Housekeeping lines** of the fulfilled tooling-tree Tools, as `housekeeping-track.md`, step 4,
  finds and words them.
- **The instruction file** — `AGENTS.md`; where the target has only `CLAUDE.md`, that file.
- **How a ticket is created and listed**, from the tracker file.

*Done when* all five are known.

## 3. The decision point

- **Findings:** the template in full, word for word as it will be written, with its path; the
  **Housekeeping** bullet; the first ticket, due today; the line for the instruction file; a ticket
  step 1 found that is no first ticket, with the proposal for it. Shortened, the human would agree to a
  text they have not read.
- **Options:** set it up as laid out and work the first cycle in this run (the recommendation); set it
  up and deliver the setup alone, the first cycle left for a later run; change the path, a task, or the rhythm —
  `daily`, `weekly`, `monthly`, or the human's own words (`every 3 days`, `monthly on the 1st`) —, then
  this decision point again; set it up without the line in the instruction file; not now.
- **The line in the instruction file** changes `AGENTS.md`, so a human is asked in every mode.
  Unanswered or declined, it is left out and the closing report says so.
- **Not now** → nothing is written, and there is nothing to work (`housekeeping-track.md`).

*Done when* the answer is taken.

## 4. Write

1. Create the first ticket as the agreed bullet says, due today, unless step 1 found it. Report it,
   and assign it per **Claim**, where the target has that operation.
2. Check out its branch per `implement-point.md`, step 2.
3. Commit the template together with the **Housekeeping** bullet in the tracker file's
   `## Refactoring operations` section.
4. Where a human agreed to it, commit the line in the instruction file by itself.

Then, as decided in step 3:

- **With the first cycle** → go on at `housekeeping-track.md`, step 4, with this ticket: its cycle runs in
  this run, and its merge request carries the setup.
- **The setup alone** → follow `opening-a-merge-request.md`, handing in this ticket, the branch and that
  it delivers a **part**: the merge request names the ticket without a closing reference and says that
  the first cycle is still to be worked. The run ends there; the ticket stays open, and a later run
  works its cycle once the setup is merged.

*Done when* the ticket exists and the branch holds the agreed commits.

## The template

Recommended path: `docs/refactoring/housekeeping-template.md`. Its tasks are copied into tickets, so each
is worded as `forge-facing-writing.md` asks.

```markdown
# Housekeeping

Rhythm: <daily | weekly | monthly | the human's own words>

Recurring maintenance for this project. One Housekeeping ticket is always open, made from the tasks
below. Ideas for a refactoring are left on it as comments. A new task goes above the last one.

## Tasks

- Scan the Git history for committed secrets: the whole history the first time, afterwards the commits
  added since the previous Housekeeping ticket's scan. Note the commit scanned up to.
- Re-check the project's quality tooling: is every tool set up so far still in place and running, and is
  there a further one to set up? File a ticket for each gap.
- Audit the third-party dependencies for known vulnerabilities with the package manager's own audit
  (`composer audit`, `npm audit`, …) and update each one with an advisory to a patched version.
- <one task per tool: what its Housekeeping line asks, in the template reader's words>
- Create the next Housekeeping ticket from this file, due one rhythm from today.
```

## The Housekeeping bullet

```markdown
- **Housekeeping**: the template is `<path>`. The next ticket is made with `<the tracker's command to create a ticket>`: a title that names Housekeeping and the date the ticket is due from, a line in the text with that date, a line naming the template `<path>`, and the template's tasks as a checklist. The open ones are listed with `<Search for the title's Housekeeping term, narrowed to the open tickets>`.
```

## The line in the instruction file

```markdown
**Refactoring ideas.** When you notice a possible refactoring while doing other work, ask the human whether to note it. Once they agree, post it as a comment on the open Housekeeping ticket (`docs/agents/issue-tracker.md`, **Housekeeping**): where it is, what would change, and why. When two Housekeeping tickets are open, ask the human which one, and recommend the younger.
```

A call that asks for the line after the setup gets it in that call's cycle: laid out among the findings
of `housekeeping-track.md`, step 4, and committed by itself.

## A template without an open ticket

One decision point: create the ticket from that template, due today (the recommendation), or leave
the template without one. Created → report it.

## A further template

A human who asks for a second rhythm ("a monthly one beside the weekly") gets steps 2 to 4 for it:

- **The template** — a path of its own, its rhythm, the tasks the human names, and the last task. The
  secret scan, the re-check, the dependency audit and the tools' Housekeeping lines stay in the first
  template alone.
- **The bullet** — extended: it names each template's path, the first one first, and each title carries
  its template's rhythm, as in the title of a monthly one: Housekeeping, monthly, the date.
- **The line in the instruction file** stays as it is.
