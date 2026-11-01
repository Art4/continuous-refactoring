# Reference: the tooling model

How the tools a target can adopt are described and what the parser (`tooling_tree.py`, beside this file)
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
| **Ratchet** | the way a Stage is raised: no new violations, the old ones shrink, one direction only; a property of a Tool | the PHPStan baseline, a coverage floor, PHPMD's limits |

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
packs/<pack>/<tool>.md  one file per Tool: the prose of its Stages
packs/<pack>/README.md  prose for the Pack as a whole, where it has some (the PHP Pack's runtime floor)
prerequisites/          git and onboarding-setup, in no Pack
tooling_tree.py         the parser
```

A Tool's `details` file holds what is prose: for each Stage its Purpose where it goes beyond the Role's, the
Fulfilment check and MR scope, the Ratchet, the Housekeeping line, and a sentence on why the Tool comes
after what it comes after. The JSON holds only what the parser computes with and the generated pages show.

The JSON files are written in one fixed form: two-space indent, objects expanded one key per line, lists
of plain values on one line, Stages in the order of the Pack, keys in the order of the schema.

The suite's prerequisites, `git` and `onboarding-setup` (`prerequisites/git.md`,
`prerequisites/onboarding-setup.md`), are in no Pack: `git` always holds,
`onboarding-setup` holds exactly when the target's tracker file carries the `## Refactoring operations`
section (`onboarding-setup-interview.md`), and no Stage is workable before it does.

## A Pack

`applies_when` is one sentence the agent judges against the target, once per run; the parser is handed the
Packs that apply. The generic Pack always applies. A Stage may carry an `applies_when` of its own (Composer
Audit: the repository requires a real package), judged the same way.

A Pack may name a `scope`, the language or area its Tools work on (`php`, `twig-php`, `js`); the generic Pack has
none. Tools compete for a Role only with Tools of their own scope, so a Pack for Twig and a Pack for PHP can
each have a Code Style Tool and neither takes the other's place. A target's own Pack for PHP names the scope
`php` to stand among the PHP Tools.

Every Tool has:

- `status` — **recommended**: proposed when its Role is empty. **on-request**: counted when it is there,
  proposed only when a human asks for it — worth having on some targets and noise on others (Semgrep finds
  little in code written under guardrails). **recognized**: counted when it is there, never proposed. One
  recommended Tool per Role and Pack.
- `roles` — at least one; `uses` — what it runs, or null for a convention; `details` — its prose file, named relative to the Pack's directory;
  `min_runtime` — the oldest runtime any version of the Tool ever ran on, per runtime
  (`{"php": "7.2"}`).

Every Stage has a slug and a Name (the words in ticket titles, merge requests and reports), a `track`,
`requires` and `waits_for`. Slugs of Stages and Tools are unique across all Packs, and so are slugs of
Roles; a Tool may share its slug with its Stage only when that is its only one. A Tool that gains a second
Stage gets a slug of its own and its Stages keep theirs: tickets and rejections on record name the Stage.

**`requires`** lists what must be fulfilled first: a Stage; a Role (filled once the first Stage of one of
its Tools is fulfilled); or a list of Stages of which one is enough. A rejected required Stage closes this
one. A Stage requires only Stages of its own Track or an earlier one, and the model has no cycles — the
parser refuses a Pack that breaks either.

**`waits_for`** lists Stages or Roles this Stage waits for until they are *decided*, and a rejection of one
releases this Stage instead of closing it. A Stage is decided when it is fulfilled, closed by a rejection, or never going to be
fulfilled; a Role, when it is filled in the Stage's scope or the first Stage of every Tool that could fill it
there is decided. A Role stands for whichever Tool fills it: the Rector Stages wait for Code Style, so a
target on Pint releases them as well as one on PHP CS Fixer.

## A target's own Pack

A target may keep a Pack of its own for the tools it uses and the suite does not know: a directory with a
`pack.json` in the form above and, where it adds Roles, a `roles.json` in the form of the suite's.
`## Refactoring operations` names the directory (**Tooling Pack**, `refactoring-operations.md`). Its
`details` files are named relative to that directory, and its `"$schema"` points at the schema in the
target's installed skills, so an editor checks it.

- **It adds, never redefines.** Tools, Stages and Roles of its own, and Tools that play a Role of the suite.
  Its Stages may require and wait for Stages and Roles of the suite; nothing of the suite requires one of
  its own. A slug already taken by the suite, a Pack name or a Role is not reusable: the parser ends in exit
  code 2 and names both places. A suite Tool the target does not want is rejected (`rejection.md`).
- **It stands among the suite's Tools through its scope.** A Pack for PHP names the scope `php`; its Tool for
  Static Analysis then competes with PHPStan and Psalm, and a target that prefers it rejects the PHPStan Tool.
- **It comes last** in the order of the Packs, so the suite's Stages are proposed first.
- **Its *Applies when* is judged** like the suite's Packs'; the Pack of a project is usually "Always."

## What the parser computes

From the Packs and a seed (`tooling-parser.md`): which Packs and Stages apply, which Stages are fulfilled,
which subjects are rejected, and the runtime the target allows.

- **A Role is filled, per scope,** by the first Tool of that scope whose first Stage is fulfilled; recommended
  Tools come before on-request ones and both before recognized ones, so with several present the
  recommended Tool is the one in use. A Stage
  that requires a Role needs it filled in its own Pack's scope (a Stage of a Pack without a scope, in any).
- **A Tool is out** when a Role of it is filled, in its scope, by another Tool and its own first Stage is not fulfilled.
  Its Stages are not proposed, do not count towards the Track, and hold nobody's `waits_for`. A target on Psalm
  has the Role Static Analysis filled, and PHPStan is out. A Tool of another scope is not touched.
- **A Stage is closed** when a rejection reaches it: its own, its Tool's or a Role of its Tool; a required
  Stage is closed; every member of an any-of group is closed or can never be fulfilled and at least one is
  closed; or a required Role cannot be filled any more because every Tool of it is closed or can never be
  fulfilled (and one is closed).
- **A Stage that can never be fulfilled** is one of a recognized Tool that is not there, of an on-request
  Tool nobody asked for, or of a Tool that is out.
- **An on-request Tool is asked for** once a Stage of it is in the seed's `requested`: a ticket of it
  exists, or the call names it. Its Stages are then ordinary Stages.
- **A rejection** names a Role, a Tool or a Stage and may carry a blocker, `{"php": "8.1"}`: the runtime
  whose arrival lifts it. Rejecting a Role closes the Tools that play it; rejecting a Tool closes its
  Stages and leaves the Role for another Tool.
- **A Stage is ticketable** when it applies, its Tool is not out, and the Tool is recommended or an
  on-request Tool that was asked for. Per Track, its **backlog**
  is the ticketable Stages not fulfilled and not closed, in the order of the Packs. Its **withheld** list
  names those that cannot be worked now, and why — the target is not onboarded, the runtime is too old, a
  required parent or Role is open, the Safety Net is not fulfilled, a `waits_for` is undecided — and those
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
   Safety Net is open (Guardrails only); a `waits_for` Stage or Role is undecided.
