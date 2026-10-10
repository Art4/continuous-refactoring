# Playbook: A Run

The playbook for humans. The skills do the work; this document explains how you steer a run — what you can say in the call, what you decide along the way, and how a run ends.

## What a run is

One call of `/continuous-refactoring` is one **run**. It leads from your project's open refactoring tickets to one opened merge request:

```
reconcile → choose a Track → scan (only when needed) → file tickets → select a ticket → design → implement → merge request
```

A run ends when the merge request is open. More work is another call, not a longer run — so a weekly rhythm and a spontaneous call both work, and they run the same chain.

The suite keeps nothing between runs. Each one searches your tracker and your forge afresh: what is open, what is in review, what was merged, what you declined. If you closed a ticket by hand, merged something outside the suite or set a tool up yourself, the next run simply finds it that way.

On a project the suite has not seen, the run begins with a short **onboarding**: where your tickets live and how a few operations work there. The answer is written as one section into `docs/agents/issue-tracker.md`; commit that file. The suite then offers to go on with the run in the same call.

## The call

Say what you want in your own words after the command. The suite says back in one sentence what it understood.

| You say | What it does |
|---|---|
| nothing | an interactive run over everything |
| "do it yourself", "without asking" | an **autonomous** run: every decision takes the suite's own recommendation |
| a Track — "work on Guardrails" | that Track, whatever the suite would have recommended; the run ends when that Track has nothing to work on |
| a ticket — "ticket 42" | exactly that ticket; the run ends if it turns out not to need work |
| a restriction — "only the Rector tools" | scan, filing and selection stay within it |
| "scan again" | the Track is scanned although it was scanned before |

These combine: "do Guardrails yourself, only the security tools".

## Decision points

At each link of the chain the suite lays out three things: what it **found**, the **options**, and the one it **recommends**, with the reason in a few words. Nothing is written to your tracker, your forge or your repository that did not follow from one.

- In an **interactive** run you answer. "Yes" takes the recommendation.
- Say "carry on yourself from here" at any point and the run is autonomous from the next decision on. That is the way to attend only the decisions you care about.
- In an **autonomous** run the suite still writes down what it found at each decision, then names the recommendation it took. Nothing is asked, but the conversation reads the same as an interactive run — so you can see afterwards why it went the way it did.
- If a run was started without the autonomous hint and nobody answers, it ends at that decision point. What you find afterwards is the report — findings, options, recommendation — and nothing was written. An unattended call is therefore safe by default; say "do it yourself" in the call to let it work.

One change always waits for you, in an autonomous run too: an edit to your project's `AGENTS.md`.

## What you decide in a run

| Decision point | What is laid out | Recommended |
|---|---|---|
| Onboarding (only when the tracker section is missing or incomplete) | the tracker, where merge requests live, each operation and where its answer came from | write the section |
| Reconcile | merge requests of open tickets that were merged or closed, and declined work whose blocker is now met | close the ticket of a merged one; record a rejection where the comments say the change is not wanted; keep the ticket where they name a defect; ask you where a merge request was closed without a reason |
| Track choice | per Track how many tickets are workable, in review, blocked, waiting | the first Track in the fixed order with something to work on ([Track playbook](tracks.md)) |
| File tickets (after a scan) | one proposal per tool that is neither in place nor declined, blocked ones included, each with existing tickets on the subject | file them all; you may file some, none, or decline a tool for good |
| Select | tickets whose tool turned out to be in place already, tickets that cannot be worked and why, the rest in order | close the first group with a note, work the first of the rest |
| Who plans, who implements | the skills your project offers for it | your project's own; the suite's procedure only as a fallback |
| The plan | the plan in full: what changes, the slices, the commands that show it is done | post it on the ticket |
| The merge request | branch, commits, the checks that ran, title and description | push and open it |

A decision point with nothing to decide is one sentence instead of a question.

## Tickets that wait for you

Two findings at the design point stop a run instead of guessing:

- **A decision that is hard to reverse and a real trade-off.** In an interactive run you are asked. An autonomous run plans with a default, leaves the question on the ticket as a comment that opens with `Open question`, and ends.
- **The work cannot be done without changing behaviour.** A refactoring keeps what the application does. The suite leaves that finding on the ticket as an open question: decline it as refactoring, or turn it into feature work. An autonomous run never declines a ticket by its own judgement.

A ticket waits while that comment is its newest one. **Answer by commenting on the ticket** — any newer comment ends the wait, and the next run reads it: it lets the plan stand, plans again with the way you named, or asks once more. There is no label to set or remove.

## How a run ends

- **A merge request is open** — review and merge it.
- **A branch was handed to you** — there is no forge, or you chose to push yourself. Its name is in a comment on the ticket.
- **An open question** is on the ticket — answer there.
- **Nothing is workable** — every open ticket is in review, blocked or waiting.
- **"Safety Net is waiting for merges"** — an autonomous run found nothing workable in Safety Net while Safety Net is unfinished. The report lists what is in review. Merge, or name another Track.
- **Nobody answered** a decision point of an interactive run.

Every run closes with two lines. **Status** says what happened and where it ended; **Next** says what you can do now. Where a claim could not be confirmed — CI still running, checks unreadable — the report says so.

## Running it regularly

The suite schedules nothing. Point your own scheduler (a cron job, `/schedule`, `/loop`) at `/continuous-refactoring do it yourself` and at `/continuous-housekeeping do it yourself`, as often as fits.

Nothing limits how many merge requests are open at once. Called repeatedly, Safety Net ends at "every workable tool has a ticket and an open merge request" — from there the next step is yours: review and merge. Merge requests opened side by side may conflict with each other; resolving that is yours too.

## Steering what gets worked on

- **A priority mark.** Where your tracker section says how a ticket is marked as priority, a ticket so marked comes first within its Track.
- **Your own tickets.** A ticket you wrote is worked when your tracker section says how refactoring tickets are marked and it carries that mark, or when you name it in the call.
- **Focus areas and refactoring goal.** Two lines in your `AGENTS.md` — `Focus areas: order intake, billing` and `Refactoring goal: convert legacy procedural code to OOP` — say where an exploration looks first and which shape the code should move towards.
- **Declining.** Decline a tool at filing or selection and it is recorded with your reason, in the place your project names, and not proposed again. The tickets that depended on it are a decision point of their own.

## Common mistakes

- **Waiting for the suite to do more in one call.** A run ends at one merge request. Call again.
- **Starting an unattended run without saying so.** It ends at the first decision point, by design.
- **Answering an open question in the conversation of a later run.** Answer on the ticket; that is where the next run looks.
- **Expecting a scan on every run.** A Track is scanned once; after that its tickets are the record. Ask for a scan, or let Housekeeping's re-check find what changed.
- **Merging reviews into one score.** The suite's own review keeps two axes apart — does the change do what the plan says, and does it follow the project's standards — so a failure on one stays visible when the other is fine.
