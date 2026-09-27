# Bookkeeping state lives in an issue or a local file, never in a suite-managed commit; per-person config is its own file

> Supersedes [ADR-0011](0011-bookkeeping-goes-through-its-own-merge-request.md),
> [ADR-0028](0028-native-tracker-in-flight-bookkeeping-rides-the-candidate-branch.md) and
> [ADR-0031](0031-draft-candidate-mrs-until-fold-in-lands.md): the suite no longer commits its own
> state, so there is no bookkeeping branch, no fold-in and no draft-until-fold-in.
>
> Amends [ADR-0012](0012-remembered-merge-requests-follow-the-tracker.md) and
> [ADR-0029](0029-native-tracker-design-skips-the-pending-candidate-write.md): the reasoning (reuse the
> tracker instead of a committed file) is extended to all suite state, and the special-casing per tracker
> kind is no longer needed.
>
> Amends [ADR-0024](0024-loop-config-interview-decides-tracker-create-mode-storage.md),
> [ADR-0025](0025-agents-md-gets-a-create-mode-pointer-not-the-value.md),
> [ADR-0058](0058-onboarding-is-a-dispatcher-step.md) and
> [ADR-0063](0063-loop-creates-tickets-and-ticket-create-mode.md): where the create-modes live, what
> `AGENTS.md`/`CLAUDE.md` carries, what "onboarded" means, and what an absent `Ticket-create-mode` reads as.

Today the loop's state — `bookkeeping.md`, `merge-requests.md`, `out-of-scope/`, `housekeeping-template.md` —
lives in the target repo's Refactoring Notes folder, and a good part of the suite exists to get it to the
other people and machines: a dedicated bookkeeping branch, a fold-in into the candidate's own merge request,
draft merge requests until the fold-in lands, a path-resolution rule in `AGENTS.md`. The goal was that
everybody reads the same state. What is actually wanted is narrower: usually one machine runs the suite, and
the state must not be tied to that machine — it has to be picked up from another. That does not need a commit
at all.

The create-modes are a second, separate finding. `MR-create-mode` and `Ticket-create-mode` describe how a
particular person wants to be asked, so they can differ per person and machine; they were never project state.

## Decision

**Two artifacts, separable.**
- The **config file** `.scratch/refactor/config.md`, at a fixed path by convention (so it needs no pointer
  of its own): the **Bookkeeping pointer** (below), `Ticket-create-mode` and `MR-create-mode`. Per person or
  machine, written by the onboarding interview, hand-editable.
- The **bookkeeping document**: `Open`, `Out-of-scope`, `Last scan`, `Pending candidates`,
  `Secret history scan`, and each Track's `Cadence` (Housekeeping's included). It holds state only.

**`Focus areas` and `Refactoring goal` move to `AGENTS.md`/`CLAUDE.md`,** as lines like the others the suite
already reads there. Only humans write them, so no write path needs to exist; they describe the project,
belong under review, and stay the same on every machine. The onboarding interview still asks for them.

**The Bookkeeping pointer** is a URL or a path, in the config file; a `Bookkeeping: …` line in
`AGENTS.md`/`CLAUDE.md` is the shared fallback for a team that wants one common document. The config file
wins. **No pointer anywhere means the target is not onboarded** (replacing "no `bookkeeping.md`" in
ADR-0058); onboarding then asks whether to create a new document or adopt an existing one.

**Issue mode** — the pointer is a URL.
- The state is the issue body. Each `out-of-scope` reasoning and each merge-request ledger entry is a comment
  on that issue; the body points to them.
- The issue carries no dedicated label. Whoever edits the body last wins — the suite does not reload and
  merge.
- An issue that can't be read (deleted, no access, forge error) stops the pass with a clear message; the
  suite never creates a replacement on its own. A closed but readable issue is worked normally and the closing
  report says so. Only onboarding creates the issue, with a human present.

**File mode** — the pointer is a path, and always when the tracker is the local Markdown one. The default is
`.scratch/refactor/`, beside the local tracker's own `issues/` folder. The suite writes the files and does
nothing else: no branch, no commit, no ignore rule. Getting them to another machine, and whether they go into
Git at all, is the developer's job. This mode is documented as for one person.

**Absent create-modes read as the safe values** — `Ticket-create-mode: ask-each-time`,
`MR-create-mode: human-opens` — and the closing report names it when they apply. This replaces ADR-0063's
"absent means `autonomous`": a fresh machine without a config file must not create tickets or merge requests
on its own.

**Housekeeping.** `housekeeping-template.md` stays a file in the repo at the fixed path
`docs/refactoring/housekeeping-template.md`, outside the Refactoring Notes — shared and reviewed like code; a
tooling-tree node's merge request still adds its own line. Housekeeping's `Cadence` and `Last scan` are in the
bookkeeping document, so two separate documents mean two independent Housekeeping schedules — accepted and
documented.

**Architecture.** The lifecycle skills and the parser keep working on one local file; two operations, `load`
and `save`, move it between that file and the backend (issue body and comments, or the file itself). This
leaves the skills and the deterministic parser unchanged, and puts all mode differences into one place.

**`refactor-learn` commits nothing.** Its state writes go into the working tree in place; the ADR and
`CONTEXT.md` changes it makes are written there too and named in its output for the developer to commit —
never onto the candidate's branch, whose review is about the candidate's own diff.

**`refactor-implement` stages only what it changed itself,** never `git add -A`, so a candidate commit can't
pick up state from `.scratch/`.

**Migration.** Onboarding gains a step for a target that still has `docs/refactoring/`: it reads the old
files, writes the state to the chosen target (issue or `.scratch/refactor/`), and removes the old files as a
confirmed action (`never-delete-without-record.md`). There is no legacy mode that keeps reading the old
folder.

## Considered Options

- **Everything in one document, config included.** Rejected: the create-modes are personal; sharing them in a
  shared issue would make one person's preference everybody's, and anyone who can edit the body could switch
  the loop to `autonomous`.
- **Config in Git, state in an issue.** Rejected: brings back a committed file that differs by person.
- **A user-level config file outside the repo, layered under the repo file.** Rejected: one more place and one
  more precedence rule for little gain; config in `.scratch/` already is per machine.
- **A dedicated label for the bookkeeping issue.** Rejected: the scan's issue detection looks for the backlog
  labels and remembered numbers, and the document has neither; a label would only invite confusion.
- **Reload and merge before every save.** Rejected: only one machine writes at a time, and a human editing
  a field the suite is about to write is rare enough that last-write-wins is acceptable.
- **Derive the merge-request ledger from the forge alone.** Kept only where it loses nothing; comments
  remain the fallback (decided with the rollout).
- **A legacy mode that keeps `docs/refactoring/`.** Rejected: the suite is early enough (0.x) for a clean cut,
  and two paths would stay to be tested for good.
- **Keep the committed folder and only add the issue as a second option.** Rejected: the bookkeeping branch and
  fold-in machinery would stay.

## Consequences

- The bookkeeping branch (`refactor-learn/references/bookkeeping-branch.md`), the fold-in exception and the
  commit instructions in `refactor-learn` go away, and with them the draft-merge-request reconciliation
  finding of ADR-0031.
- `Pending candidates` stays for now, as an ordinary state field. It is no longer written differently per
  tracker kind; dropping it is a separate, later change.
- The `Refactoring Notes: <path>` line in `AGENTS.md` goes away. `AGENTS.md`/`CLAUDE.md` gains `Bookkeeping:`
  (optional), `Focus areas:` and `Refactoring goal:` lines, and the pointer section of ADR-0025 changes.
- The dispatcher's "onboarded" check becomes "the pointer resolves".
- Onboarding ends with "please commit" only when it produced something committable — for instance the
  `AGENTS.md` lines or `housekeeping-template.md` — and says nothing of the kind otherwise.
- A team using one shared issue must keep the pointer in `AGENTS.md`; everyone else keeps it local.
- The fixtures that carry a `bookkeeping.md` and the tests around the parser change with the rollout.

## Rollout

Three merge requests, the last two each carrying their own documentation and changelog fragment: (1) this ADR, (2) the
`load`/`save` layer and file mode, including the fixtures, (3) issue mode, onboarding and migration. The
glossary entries for the new terms (**Bookkeeping document**, **Bookkeeping pointer**, **Config file**,
**Issue mode**/**File mode**) land with (2) and (3), because the suite's validator rejects a glossary term no
skill uses yet. Until then the skills and `refactoring-bookkeeping.md` still describe the folder in the repo.
