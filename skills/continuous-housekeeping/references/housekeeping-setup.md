# Reference: setting Housekeeping up

Reached from `housekeeping-track.md`, step 1, when the mechanism is missing. It proposes the three parts
of the mechanism — the **Housekeeping template**, the **Housekeeping** operation, the first **Housekeeping
ticket** — and with them the line in the target's instruction file, and writes what a decision point
agreed to. A file named without a path lives in `../../continuous-refactoring/references/`.

## 1. Is a setup already on its way?

Run **Search** over the open tickets with the word `Housekeeping`, and look at each hit's merge request
or branch (`worklist.md`, *A ticket's merge request*):

- **It is open and adds a Housekeeping template** → the mechanism waits for that merge: name the ticket
  and its merge request; there is nothing to work (`housekeeping-track.md`).
- **It was closed without a merge, or the ticket has none** → that ticket is the first ticket of step 4.

*Done when* the search is read: a setup waits, a first ticket exists, or neither.

## 2. Read the target

- **A template that exists** — a file of the target that already lists recurring maintenance tasks. It is
  proposed as the template, its tasks kept, the parts of *The template* it lacks added.
- **The rhythm to recommend** — count the commits the default branch gained in the last 90 days: more
  than 300 → `daily`; 30 to 300 → `weekly`; fewer → `monthly`.
- **The Housekeeping lines** of the fulfilled tooling-tree nodes, as `housekeeping-track.md`, step 4,
  finds and words them.
- **The instruction file** — `AGENTS.md`; where the target has only `CLAUDE.md`, that file.
- **How a ticket is created and listed**, from the tracker file.

*Done when* all five are known.

## 3. The decision point

- **Findings:** the template as it would be written, with its path, rhythm and tasks; the
  **Housekeeping** bullet; the first ticket, due from today; the line for the instruction file.
- **Options:** set it up as laid out (the recommendation); change the path, a task, or the rhythm —
  `daily`, `weekly`, `monthly`, or the human's own words (`every 3 days`, `monthly on the 1st`) —, then
  this decision point again; set it up without the line in the instruction file; not now.
- **The line in the instruction file** changes `AGENTS.md`, so a human is asked in every mode.
  Unanswered or declined, it is left out and the closing report says so.
- **Not now** → nothing is written, and there is nothing to work (`housekeeping-track.md`).

*Done when* the answer is taken.

## 4. Write

1. Create the first ticket as the agreed bullet says, due from today, unless step 1 found it. Report it,
   and assign it per **Claim**, where the target has that operation.
2. Check out its branch per `implement-point.md`, step 2.
3. Commit the template together with the **Housekeeping** bullet in the tracker file's
   `## Refactoring operations` section.
4. Where a human agreed to it, commit the line in the instruction file by itself.

Then go on at `housekeeping-track.md`, step 4, with this ticket: its first cycle runs in this run, and
its merge request carries the setup.

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
- <one task per tool: what its Housekeeping line asks, in the template reader's words>
- Create the next Housekeeping ticket from this file, due one rhythm from today.
```

## The Housekeeping bullet

```markdown
- **Housekeeping**: the template is `<path>`. The next ticket is made with `<the tracker's command to create a ticket>`: the title `Housekeeping, due from <YYYY-MM-DD>`, the text a line `Due from: <YYYY-MM-DD>`, a line `Template: <path>`, and the template's tasks as a checklist. The open ones are listed with `<Search for "Housekeeping" in the title, narrowed to the open tickets>`.
```

## The line in the instruction file

```markdown
**Refactoring ideas.** When you notice a possible refactoring while doing other work, ask the human whether to note it. Once they agree, post it as a comment on the open Housekeeping ticket (`docs/agents/issue-tracker.md`, **Housekeeping**): where it is, what would change, and why. When two Housekeeping tickets are open, ask the human which one, and recommend the younger.
```

A call that asks for the line after the setup gets it in that call's cycle: laid out among the findings
of `housekeeping-track.md`, step 4, and committed by itself.

## A template without an open ticket

One decision point: create the ticket from that template, due from today (the recommendation), or leave
the template without one. Created → report it.

## A further template

A human who asks for a second rhythm ("a monthly one beside the weekly") gets steps 2 to 4 for it:

- **The template** — a path of its own, its rhythm, the tasks the human names, and the last task. The
  secret scan, the re-check and the tools' Housekeeping lines stay in the first template alone.
- **The bullet** — extended: it names each template's path, the first one first, and each title carries
  its template's rhythm: `Housekeeping (monthly), due from <YYYY-MM-DD>`.
- **The line in the instruction file** stays as it is.
