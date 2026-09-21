# Architecture

How the suite is put together, for someone who wants to understand or extend it. For steering a run as a user, see the [loop playbook](playbooks/loop.md); for the vocabulary, [CONTEXT.md](../CONTEXT.md).

## Skill hierarchy

```
/continuous-refactoring            ← the only user entry point; onboards a new project, otherwise picks a Track
   ├── /continuous-safety-net      ┐
   ├── /continuous-guardrails      ├─ each names its Track and delegates to ↓
   ├── /continuous-investigation   ┘
   │        └── refactor-loop      ← one track-agnostic pass
   │               ├── refactor-scan
   │               ├── refactor-prioritize
   │               ├── refactor-design
   │               ├── refactor-implement
   │               └── refactor-learn
   └── /continuous-housekeeping    ← owns Housekeeping's own process; never calls refactor-loop
```

- **`continuous-refactoring`** is a thin dispatcher. Step 0 is **onboarding**: when the target has no `bookkeeping.md` it runs a short interview inline, writes the setup files and ends the invocation (see [Loop state](#loop-state)). Otherwise it selects a [Track](playbooks/tracks.md), announces the choice in one sentence and invokes that Track's skill. It never runs the pass itself.
- **`continuous-safety-net` / `-guardrails` / `-investigation`** are internal. Each does nothing but name its Track and call `refactor-loop`.
- **`continuous-housekeeping`** runs the Housekeeping Track's own reconcile → checklist → quality gate → deliver process, then records its `Last scan` through `refactor-learn`. It aborts, pointing at `/continuous-refactoring`, on a target with no `bookkeeping.md`.
- **`refactor-loop`** requires a Track and an onboarded target (a `bookkeeping.md`) and aborts without either; it never guesses a Track from repo state and never branches on a Track's name itself.

Only `continuous-refactoring` is meant to be typed by a human; the others are implementation detail, though invoking a `continuous-<track>` skill directly is a valid manual override.

## One pass, step by step

`refactor-loop` is a **thin data pipe**: it calls each lifecycle skill in order and carries that skill's output to the next skill's input. It decides nothing a lifecycle skill could decide, and no skill re-derives context from shared state (except `refactor-scan`'s own detection).

| Step | Skill | Job | Writes? |
|---|---|---|---|
| 1 | `refactor-scan` | Check preconditions (git, backlog size), resume pending work, walk the Track's `Open` list or scan the tooling tree, detect merged/closed merge requests | never |
| 2 | `refactor-learn` (early call) | Record what scan found — only if it found something — so ranking sees a current ledger | yes |
| 3 | `refactor-prioritize` | Rank the proposals; for a gate-shaped winner (structural work, PHPStan baseline shrink), select and minimally file the concrete candidate | files the candidate issue |
| 4 | `refactor-design` | Ground and grill the candidate into a plan; file or update the issue, add the plan as a comment | files/updates the issue |
| 5 | `refactor-implement` | Branch, execute the plan test-first, review the diff (standards and spec, separately), open the merge request | branch, commits, merge request |
| 6 | `refactor-learn` (closing call) | Record the outcome — always, even when nothing past step 3 ran | yes |

Early exits are normal: no git repository ends the pass; a full backlog, a resumable candidate or a candidate still waiting for an answer skip ahead. Whenever a step stops the pass early, the human is told why immediately, and the closing report is always two lines (**Status**, **Next**).

### Only `refactor-learn` writes bookkeeping

`refactor-learn` is the suite's only dedicated writer: the ledger, `bookkeeping.md` Track sections, ADRs/`CONTEXT.md` in the target, issue status. The few other writes are the ones a step itself produces (an issue filed, a branch pushed) and the dispatcher's one-time onboarding files. This keeps "what changed the state" answerable by looking at one skill.

### Subagents and hand-back

`refactor-loop` runs the scan step and the implement step in fresh subagents, so their reasoning stays in their own context and only their stated output comes back. A subagent can't ask you a question or reliably reach the forge, so it hands back instead of stalling: it reports the branch and commits plus whatever it couldn't do (seams awaiting your confirmation, a create-mode that asks you, a failed push or merge request, an unreadable CI status). The loop then finishes that part in its own context. Without a subagent mechanism, the steps run inline.

### The two-merge-request cap

Before implement would open a *new* merge request, the loop counts the suite's open ones. Two or more → the candidate keeps its plan, stays pending, and the pass ends with a note naming the waiting merge requests. Continuing an already-open merge request is never gated. Merge requests always branch off the default branch — never off each other.

## The tooling tree

Safety Net and Guardrails work through the **tooling tree**: a directed graph of adoption steps a target climbs — a language-neutral root ([tooling-tree.md](../skills/refactor-scan/references/tooling-tree.md)) with a specialization attached beneath (PHP: [php-tooling-tree.md](../skills/refactor-scan/references/php-tooling-tree.md)). Edges are *required* (gates the child until the parent is fulfilled or rejected) or *recommended* (advises only).

- **Fulfilment is judged, not detected.** Each node has a Purpose and a Fulfilment check; an agent judges whether the target already satisfies it — so a tool adopted by hand, or a differently named equivalent, counts. There is no hardcoded list of dependency names.
- **The parser only does graph logic.** `tooling_tree.py` takes a fulfilment state and computes the ordered `Open` backlog, workable and withheld nodes with reasons, rejection cascades and the merge-request outlook. It never inspects the target.
- **Rejections are remembered.** A node you decline is recorded under `out-of-scope/` and counts as resolved, so it isn't proposed again.
- **A tooling-tree merge request is small and factual:** one node, its own fulfilment check as acceptance criterion, and a comment on the issue about what it unlocks next.

## Loop state

State lives in the target repo, never in the conversation; every lifecycle skill reads it directly.

| What | Where |
|---|---|
| Config, `Create-mode`, focus areas, `Pending candidates`, each Track's `Cadence` / `Last scan` / `Open` / `Out-of-scope` | Refactoring Notes' `bookkeeping.md` (default folder `docs/refactoring/`, overridable) — [full reference](../skills/continuous-refactoring/references/refactoring-bookkeeping.md) |
| Remembered merge requests | open `refactor:candidate` issues with a linked pull request (native-label trackers); `merge-requests.md` otherwise |
| Backlog | `refactor:*` issues on the tracker named in `docs/agents/issue-tracker.md` |
| Learned rejections | `out-of-scope/` |
| Housekeeping checklist | `housekeeping-template.md` |
| Domain language, decisions | the target's `CONTEXT.md` and ADRs |

`bookkeeping.md` doesn't exist on a fresh target. The dispatcher's onboarding step creates it: a short human interview (tracker, merge request create-mode, Refactoring Notes location — plus a one-time abort-or-continue question when the engineering skills' issue-tracker and label files are missing) whose answers are decided once. Onboarding writes `bookkeeping.md` last, so its existence means "onboarding complete", suggests committing the new files and ends the invocation — no issue, merge request, branch or scan, and nothing is created on GitHub or GitLab. The next invocation selects a Track and scans. The tooling tree keeps a root node for this (`onboarding-setup`, "Onboarding Setup"); the onboarding step fulfils it before any scan, so it is never proposed as a candidate.

## Fallbacks and self-containment

The suite must keep working in a target with none of the engineering skills installed. Every reference from a suite skill to a global skill (`/tdd`, `/grilling`, `/domain-modeling`, …) carries a fallback — either *crash-safe* (skip with a note; the step's core is already inline) or *self-sufficient* (the fallback inlines the part it needs). Likewise, no forge or remote is not an error: the branch is prepared and handed to you.

## Where things live in this repo

- `skills/<skill>/SKILL.md` — the skill itself, kept short; detail lives in `skills/<skill>/references/`.
- Anything a skill needs at runtime lives under its own `references/`. `docs/` (playbooks, this file) is for humans and never ships with the skills.
- `fixtures/` and `scripts/` — the test harness for the tooling-tree parser and the skill-validation checks ([fixtures/README.md](../fixtures/README.md), [CONTRIBUTING.md](../CONTRIBUTING.md)).
