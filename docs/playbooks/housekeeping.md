# Playbook: The Housekeeping Track

The playbook for humans. The skill does the work; this document explains how you steer Housekeeping — the template, the standing ticket, the rhythm, and the ideas you leave on it.

## What it is

Recurring maintenance: dependency currency, tooling-deprecation cleanup, a secret scan over the Git history, a re-check of the project's quality tooling — plus the small refactoring ideas that come up during other work.

It is built from two things in your project:

- **The Housekeeping template** — a file in your repository listing the recurring tasks and the rhythm. It is shared and reviewed like code.
- **The Housekeeping ticket** — one open ticket, made from the template, that states from when it is due. Its last task is "create the next Housekeeping ticket", so the cycle carries itself: there is always one open, and the open ticket is the whole state.

One worked ticket is one cycle. It ends with a merge request holding what changed — or, where nothing needed changing, with the ticket closed and a comment saying so.

## Two ways in

- **`/continuous-housekeeping`** runs Housekeeping and nothing else. It needs no Track choice, so it is the one to put on a schedule. It follows the same two modes as any run: it asks at each decision, or decides by itself when you say so in the call.
- **`/continuous-refactoring`** recommends Housekeeping at Track choice when its ticket is due, or when it is not set up yet.

## Setting it up

The first call that finds no Housekeeping mechanism proposes one, as a single decision point:

- **the template**, with a recommended path and the tasks: the secret scan, the re-check of the tooling, and one task for each tool already in place that needs recurring attention;
- **the rhythm** — `daily`, `weekly`, `monthly`, or your own words (`every 3 days`, `monthly on the 1st`). The recommendation is drawn from how busy the repository was in the last 90 days;
- **the first ticket**, due today;
- **one line for your `AGENTS.md`** (below). This one is asked of you in every mode; an autonomous run that gets no answer leaves it out and says so.

What you agree to is committed on the first ticket's branch, the first cycle runs in the same call, and its merge request carries the setup. Until you merge it the mechanism is not on your default branch yet; a call in between tells you that the setup waits for that merge.

An existing file that already lists recurring maintenance tasks is proposed as the template, its tasks kept.

## Rhythm and due date

Each ticket states its date as a line `Due from: YYYY-MM-DD`. A call before that date finds nothing to work and ends, naming the date — so a daily scheduled call on a weekly rhythm is harmless. To work a ticket early, say "now" in the call or name the ticket.

The next ticket is due one rhythm after the day the cycle was worked, not after the old due date. Change the rhythm by editing the line in the template; the next ticket made from it follows.

**Several templates** with different rhythms may exist side by side — say, a weekly and a monthly one — each with its own open ticket. Ask for a further one in the call ("a monthly one beside the weekly"). The secret scan, the tooling re-check and the tools' own tasks stay in the first template; a further one holds the tasks you name.

## What a cycle works

1. **The recurring tasks** of the ticket, in order. Each is ticked on the ticket with its result in a line, so the ticket is the record of the cycle and an interrupted cycle continues where it stopped.
2. **Tasks the ticket lacks**: one the template gained since, or one for a tool that is in place while the template has no task for it — the way a tool you set up by hand gets its recurring check.
3. **The ideas** left on the ticket as comments.

Before any of it is done, the cycle is laid out as one decision point: the tasks, the new ones, and each idea with what the suite makes of it.

### Ideas left as comments

Anyone — you, or an agent in the middle of feature work — can leave a refactoring idea as a comment on the open Housekeeping ticket. The cycle sorts each one:

| The idea | What happens |
|---|---|
| changes structure and keeps behaviour, needs no choice between designs, touches code that tests or a tool cover, and reads as a few commits | **carried out** in this cycle, in one or more commits of its own, so you can review and revert it by itself |
| is a refactoring, but bigger than that | **proposed as a ticket of its own**, where it gets a plan and its own review |
| changes what the application does, or asks for something other than a change of structure — a command to run, a dependency, CI, credentials | **left alone**, with the reason said |

One comment at the end of the cycle says what became of every idea.

### The line in `AGENTS.md`

> **Refactoring ideas.** When you notice a possible refactoring while doing other work, ask the human whether to note it. Once they agree, post it as a comment on the open Housekeeping ticket: where it is, what would change, and why. When two Housekeeping tickets are open, ask the human which one, and recommend the younger.

It turns the Housekeeping ticket into the place where ideas from feature work land instead of getting lost. An agent asks you before commenting, because a comment on your tracker is a write you did not ask for.

### The secret scan

The first cycle scans the whole Git history; each later one scans the commits added since the scan before. It uses the secret scanner your project already runs, with that scanner's own list of known findings. Without one, the task is ticked as not run. A finding is reported by place only — the secret's value is written nowhere. Where people outside the project can read the tracker, the recommendation is to file no ticket for a finding and to tell you in the conversation.

### The re-check of the tooling

A scan of Safety Net and Guardrails, tools with an open ticket included: is every tool set up so far still in place, and is there a further one to set up? Gaps go through the same decision point as any scan's proposals.

## Reading the result

Review the cycle's merge request like any other: one commit per task that changed something, one or more per idea. A task with no clean way through — a security advisory without a patched version, an update that cannot be made green — is not forced: the branch keeps only what is green, the task is ticked with what was found, and the rest is proposed as an ordinary ticket for you to decide about.

Housekeeping keeps current what the project already has. A tool the project lacks is a ticket of the tooling Tracks, never something a cycle installs.

## Housekeeping mentions on ordinary merge requests

A merge request that sets up a tool — say `composer audit` — may also add one recurring task to the Housekeeping template. Its description says so in a line. That is the tool's own contribution to future cycles, not a second decision to make.

## Common mistakes

- **Leaving the setup's merge request unmerged.** Until it is merged there is no template on the default branch, and later calls wait for it.
- **Editing the due date to skip a cycle.** Change the rhythm in the template instead; the date is written when the next ticket is made.
- **Putting a big refactoring into a comment and expecting it done in the cycle.** It becomes a ticket of its own.
- **Treating a finding with no clean fix as something to force through.** It is handed to you as a ticket on purpose.
