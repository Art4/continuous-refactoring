# Architecture

How the suite is put together, for someone who wants to understand or extend it. For steering a run as a user, see the [run playbook](playbooks/run.md); for the vocabulary, [CONTEXT.md](../CONTEXT.md).

## Two skills, everything else a reference

```
/continuous-refactoring            ← one run: from the open tickets to an opened merge request
   └── references/
         ├── onboarding, the operations and their templates
         ├── worklist, reconcile, Track choice
         ├── scanning a tooling Track, filing tickets, selection, rejections
         ├── the Investigation Track, the signals, the search for structural candidates
         ├── design point, implement point, review, opening the merge request
         └── the tooling tree: its parser, the tree docs, one file per node

/continuous-housekeeping           ← the Housekeeping Track alone, no Track choice
   └── references/
         ├── the Housekeeping Track
         └── setting Housekeeping up
```

- **`continuous-refactoring`** holds the run: how the call is read, the rules of a decision point, the ten steps, and how a run ends. Each step points to the reference that carries its detail, so a run loads only what it reaches.
- **`continuous-housekeeping`** is a second entry point for one Track. It needs no Track choice, which is what makes it fit for a schedule. A run of `continuous-refactoring` that chooses Housekeeping reads the same Housekeeping reference, so there is one description of the process.

Both are typed by a human; neither is picked by the agent on its own. A step that only reads and judges — the fulfilment judgements of a scan, the exploration for structural candidates, a review — may be handed to a subagent together with its reference, so its reasoning stays out of the main conversation. A subagent asks nothing and writes nothing; every decision point stays in the conversation with you.

## One run, step by step

| Step | What happens | Ends when |
|---|---|---|
| 1 Ready | No Git repository ends the run. A tracker file without the suite's section, or with a required operation missing, leads into the onboarding interview | the section carries the three required operations |
| 2 Worklist | The open tickets are searched, each sorted into a Track and given a state: workable, in review, blocked, waiting | every ticket found has both |
| 3 Reconcile | Merge requests that were merged or closed since, and declined work whose stated blocker is now met, are laid out with what follows | every finding is acted on or left as decided |
| 4 Track choice | One Track is recommended in the fixed order; the run may end here | a Track is named |
| 5 Scan | Only for a tooling Track that was never scanned, or when the call asks: each tool is judged against the project, the tree is ordered | every tool is fulfilled, declined, proposed, or named as out of reach |
| 6 File tickets | The scan's proposals become tickets, after a search for existing ones | each proposal has a ticket or was left by decision |
| 7 Select | The first workable ticket in the Track's order; its tool is judged once more | one ticket that still needs its work is handed on |
| 8 Design | A plan is written onto the ticket | the ticket carries an implementable plan |
| 9 Implement | The plan is built on a branch of its own | the branch's checks are green |
| 10 Merge request | The branch is pushed and the merge request opened | it is open, or the branch is handed to you |

Housekeeping and Investigation replace steps 5 to 7 with their own way to a ticket; from the design point on Investigation rejoins the chain, and Housekeeping delivers through the same merge-request step.

### Decision points and the two modes

Every write to your tracker, your forge or your files follows from a **decision point**: findings, options, one recommendation. Everything before the first one is read-only.

- **Interactive**, the default: the suite asks and waits.
- **Autonomous**, said in the call or mid-run: the suite takes its recommendation and says so in a sentence.

Autonomous is the same chain with the recommendation taken, so there is one path to maintain and nothing to configure. The mode is never stored. An interactive run that nobody answers ends at that decision point; its report is the decision point itself, and nothing was written. One write waits for a human in every mode: a change to the project's `AGENTS.md`.

### The project's own skills first

At the design point and at the implement point the suite looks at the skills on offer in the conversation and at what the project's `AGENTS.md` says about planning and implementing. It recommends what `AGENTS.md` names, else a fitting skill of the project, else a fitting skill from elsewhere, and only then its own procedure. The choice is a decision point and is made again on every run, so installing a skill tomorrow changes the recommendation tomorrow.

The suite expects two things back: from planning, a ticket that carries an implementable plan; from implementing, a branch whose checks are green. It opens the merge request itself unless one is already open, so a run ends the same way whoever built the change. A decision worth recording becomes an ADR on the same branch — only where the project's domain docs say where ADRs are kept.

### What the suite reports

One sentence when a step starts and one with its result; one line per write, as it happens, naming the thing and where it lives. A run closes with two lines: **Status** — what it did and where it ended — and **Next** — what you can do now. A claim that something is open, fixed or green is read from the forge after the last push.

## No state of its own

| What | Where it is found |
|---|---|
| Work to do | open tickets, found by searching the tracker |
| A ticket's Track | the tool or subject its title and text name |
| What blocks a ticket | the tracker's own blocking mechanism, or a `Blocked by:` sentence in the ticket |
| Work in review | the ticket's merge request, found through the tracker's link or by searching the forge |
| A ticket waiting for your answer | its newest comment is an open question |
| Declined work | a closed ticket or a file with the reason, where the project's operations say |
| Housekeeping: when due, what is done, how far the history was scanned | the Housekeeping tickets |
| Focus areas, refactoring goal | two lines in `AGENTS.md`/`CLAUDE.md`, written by you only |
| Domain language, decisions | the project's own glossary and ADRs |

A ticket the suite files names its subject in plain words — the tool's name — in title and text, so that a later search finds it. There is no hidden marker and no fixed title. Before filing, the suite searches for an existing ticket on the subject, open or closed, and continues on yours instead of filing a duplicate.

### Tracker and forge

The suite never asks which tracker a project uses. It reads named operations from the `## Refactoring operations` section of `docs/agents/issue-tracker.md`. Three are required: how tickets are searched, how a finished one is recognised, and where merge requests live. The others are optional — how refactoring tickets and priority ones are marked, how a merge request and its ticket refer to each other, how a ticket is assigned, how declined work is recorded, how a ticket states what blocks it, and where the Housekeeping template lives. A project whose tracker lacks one leaves it out and the suite takes the plainer route; for some of them it proposes an answer at the moment it is first needed and writes it into the section.

The tracker and the **forge** — the system that hosts the repository and its merge requests — are two things. They are the same system on a GitHub or GitLab project, and different ones where tickets live in Redmine and the code on GitLab. Onboarding writes the section: from a template for GitHub, GitLab and local Markdown files, from your answers for anything else.

## The tooling tree

Safety Net and Guardrails work through the **tooling tree**: a directed graph of adoption steps a project climbs — a language-neutral root ([tooling-tree.md](../skills/continuous-refactoring/references/tooling-tree.md)) with a specialization attached beneath (PHP: [php-tooling-tree.md](../skills/continuous-refactoring/references/php-tooling-tree.md)). An edge is *required* (the child waits until the parent is fulfilled), *recommended* (the child waits until the parent is decided — fulfilled or declined), or one of two variants the tree docs explain.

- **Fulfilment is judged, not detected.** Each node has a Purpose and a Fulfilment check; an agent judges whether the project already serves the Purpose — so a tool set up by hand, or an equivalent under another name, counts. There is no list of dependency names.
- **The parser only does graph logic.** `tooling_tree.py` is handed which nodes are fulfilled and which declined, and answers what that means: the nodes per Track, their order, what holds each one back, which nodes a rejection closes, and which declined node can come back because its PHP version is now reached. It reads the tree docs and the project, and keeps no file.
- **Safety Net has a gate.** A handful of nodes aggregate others; their state is computed, never judged. "Is Safety Net fulfilled?" is the state of one of them, and that answer decides whether an autonomous run stops at Safety Net.
- **A tooling merge request is small and factual:** one node, and its own Fulfilment check says when it is done.

The parser and the tree docs ship together inside `continuous-refactoring`, so a copied or symlinked skill is complete.

## Self-containment

The suite works in a project with none of the engineering skills installed: planning, test-first implementation and review each have a procedure of the suite's own, used when the project offers nothing fitting. Likewise, no forge or remote is not an error: the branch is prepared, named in a comment on its ticket, and handed to you.

## Where things live in this repo

- `skills/<skill>/SKILL.md` — the skill itself, kept short; detail lives in `skills/<skill>/references/`.
- Anything a skill needs at runtime lives under its own `references/`. `docs/` (playbooks, this file) is for humans and never ships with the skills.
- `fixtures/` and `scripts/` — the test harness for the tooling-tree parser and the skill-validation checks ([fixtures/README.md](../fixtures/README.md), [CONTRIBUTING.md](../CONTRIBUTING.md)).
