# Reference: the tooling model

How the tools a target can adopt are described and what the parser (`tooling_packs.py`, beside this file)
computes from them: **Roles** filled by **Tools** that have **Stages**, delivered in **Packs**. Vocabulary
the rest of the suite shares: `CONTEXT.md`.

## The terms

| Term | Means | Examples |
| --- | --- | --- |
| **Role** | what a tool is for; a Tool plays one or more Roles, a Role can be empty | Static Analysis, Code Style, Testing, Secret Scanning |
| **Tool** | the concrete tool, or a convention that needs none | PHPStan, Psalm, PHP CS Fixer, PSR-4 Autoloading |
| **Stage** | one degree of a Tool, and the unit a ticket is filed for | PHPStan Level 0 … 10, Rector: Dead Code Set |
| **Track** | the phase of work a Stage belongs to: Safety Net or Guardrails | PHPStan Level 5 is Safety Net, Level 6 Guardrails |
| **Pack** | Tools with a condition under which they apply | generic, PHP, a target's own |
| **Ratchet** | the way a Stage is raised: no new violations, the old ones shrink, one direction only; a property of a Tool | the PHPStan baseline, a coverage floor |

A Track says when and for what a Stage is worked, not which topic it is about: Safety Net settles the
deterministic tooling before structural work starts, Guardrails keeps quality after it. Topics are
**Signals** (`signals.md`); a Role carries the Signal its tool output feeds. A new Track exists only for a
new kind of work.

## Where it lives

```
roles.json              Roles: slug, name, purpose, signal
roles.schema.json
pack.schema.json
packs/<pack>/pack.json  one Pack: applies_when and its Tools with their Stages
tooling_packs.py        the parser
```

A Tool's `details` file holds what is prose: the Fulfilment check and MR scope of each Stage, the Ratchet,
the Housekeeping line. The JSON holds only what the parser computes with.

The JSON files are written in one fixed form: two-space indent, objects expanded one key per line, lists
of plain values on one line, Stages in the order of the Pack, keys in the order of the schema.

The suite's prerequisites, `git` and `onboarding-setup`, are in no Pack: `git` always holds,
`onboarding-setup` holds exactly when the target's tracker file carries the `## Refactoring operations`
section (`onboarding-setup-interview.md`), and no Stage is workable before it does.

## A Pack

`applies_when` is one sentence the agent judges against the target, once per run; the parser is handed the
Packs that apply. The generic Pack always applies. A Stage may carry an `applies_when` of its own (Composer
Audit: the repository requires a real package), judged the same way.

Every Tool has:

- `status` — **recommended**: proposed when its Role is empty. **recognized**: counted when it is there,
  never proposed. One recommended Tool per Role and Pack.
- `roles` — at least one; `uses` — what it runs, or null for a convention; `details` — its prose file;
  `min_runtime` — the oldest runtime any version of the Tool ever ran on, per runtime
  (`{"php": "7.2"}`).

Every Stage has a slug and a Name (the words in ticket titles, merge requests and reports), a `track`,
`requires` and `after`. Slugs of Stages and Tools are unique across all Packs, and so are slugs of
Roles; a Tool may share its slug with its Stage only when that is its only one.

**`requires`** lists what must be fulfilled first: a Stage; a Role (filled once the first Stage of one of
its Tools is fulfilled); or a list of Stages of which one is enough. A rejected required Stage closes this
one. A Stage requires only Stages of its own Track or an earlier one, and the model has no cycles — the
parser refuses a Pack that breaks either.

**`after`** lists Stages that must be *decided* first — fulfilled, closed by a rejection, or never going to
be fulfilled — and a rejection of one releases this Stage instead of closing it.

## What the parser computes

From the Packs and a seed (`tooling_packs.py` documents what the seed holds): which Packs and Stages apply, which Stages are fulfilled,
which subjects are rejected, and the runtime the target allows.

- **A Role is filled** by the first Tool whose first Stage is fulfilled; recommended Tools come before
  recognized ones, so with both present the recommended Tool is the one in use.
- **A Tool is out** when a Role of it is filled by another Tool and its own first Stage is not fulfilled.
  Its Stages are not proposed, do not count towards the Track, and hold nobody's `after`. A target on Psalm
  has the Role Static Analysis filled, and PHPStan is out.
- **A Stage is closed** when a rejection reaches it: its own, its Tool's or a Role of its Tool; a required
  Stage is closed; every member of an any-of group is closed or can never be fulfilled and at least one is
  closed; or a required Role cannot be filled any more because every Tool of it is closed or can never be
  fulfilled (and one is closed).
- **A Stage that can never be fulfilled** is one of a recognized Tool that is not there, or of a Tool that
  is out.
- **A rejection** names a Role, a Tool or a Stage and may carry a blocker, `{"php": "8.1"}`: the runtime
  whose arrival lifts it. Rejecting a Role closes the Tools that play it; rejecting a Tool closes its
  Stages and leaves the Role for another Tool.
- **A Stage is ticketable** when it applies, its Tool is recommended and not out. Per Track, its **backlog**
  is the ticketable Stages not fulfilled and not closed, in the order of the Packs. Its **withheld** list
  names those that cannot be worked now, and why — the target is not onboarded, the runtime is too old, a
  required parent or Role is open, the Safety Net is not fulfilled, an `after` is undecided — and those
  closed by a rejection, with what they hang on.
- **The Safety Net is fulfilled** when its backlog is empty: every Safety Net Stage is fulfilled or
  closed by a rejection. Guardrails Stages wait for it. A run that stops because it is not fulfilled is
  described in `track-choice.md`.
- **The runtime floor** blocks a Tool's first Stage while the runtime the target allows is below the Tool's
  `min_runtime`. Versions are compared as numbers (`8.10` is above `8.9`), best effort: a value the
  parser cannot read blocks nothing, and a blocked Stage's reason names both values so a wrong
  comparison is visible. A rejection with a blocker the runtime now meets is reported for reversal.

## Working it out by hand

Without `python3`, take the same steps in this order, over the Packs that apply:

1. Mark each Stage fulfilled, rejected or neither, from what was judged.
2. Fill the Roles; mark the Tools that are out.
3. Close what a rejection reaches, from the rejected Stages down through `requires`; then Roles that
   nothing can fill; then what requires them; repeat until nothing changes.
4. List the backlog per Track in the order of the Packs; the Safety Net is fulfilled when its backlog is empty.
5. For each backlog Stage, name what holds it back, in this order: the target is not onboarded; the
   runtime is below a minimum; a required Stage is not fulfilled or a required Role is not filled; the
   Safety Net is open (Guardrails only); an `after` Stage is undecided.
