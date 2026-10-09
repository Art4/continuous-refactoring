# Reference: the onboarding interview

Backs step 0 of `continuous-refactoring` (`../SKILL.md`),
which fulfils the `onboarding-setup` node of the tooling tree
(`../../refactor-scan/references/tooling-tree/onboarding-setup.md`) before any
Track runs. Everywhere else, a tooling-tree node's plan is fixed text a human
wrote once, for every target alike. Onboarding is different on purpose: which
tracker to use, whether tickets and merge requests get created on their own or only after asking, and where the suite's own state
lives are facts about *this* target and *this* human's preference — not
something a tree doc can get right for every target by guessing.

It runs inline in the dispatcher (never in a subagent), once per target, and
**ends the invocation** — no Track selection, no scan, no candidate issue, no
merge request, no branch, nothing created on the forge — except the one
place for remote bookkeeping, when the human chose that (Q4).

Parts, in order: **Explore**, **Setup gap** (only when the engineering-skills
setup is incomplete), **Ask**, **Summarize**, **Record**, **Closing**.

**The instruction file.** Wherever this reference says "the instruction file"
it means `AGENTS.md` if it exists, otherwise `CLAUDE.md` — the same order the
suite uses to resolve the Bookkeeping pointer's shared fallback
(`refactoring-bookkeeping.md`, *Where the
Refactoring Notes live*). Neither exists → onboarding creates `AGENTS.md`
(`## Record`), and never creates the other one when one exists.

## Explore

Read-only. No writes, no questions yet.

- **Git remote.** `git remote -v` on `origin`. Host is `github.com` → GitHub
  match; `gitlab.com` → GitLab match; a different host, or no `origin` at
  all → no match (a `.gitlab-ci.yml` at the root is a weak self-hosted-GitLab
  signal, not something to guess a match from — let the human name it).
  When matched, try one reachability check before asking (`gh repo view` /
  `glab repo view`) — success strengthens the recommendation below, failure
  doesn't rule the option out, only softens the recommendation's wording —
  never install `gh`/`glab` if either is missing; a missing CLI is scored
  the same as a failed reachability check, not something to fix first.
- **Existing forge labels.** Reachable → list the repo's labels (`gh label
  list` / `glab label list`) and note which existing labels plainly play one
  of the triage roles under a different spelling (e.g. `wont-fix` for
  `wontfix`). Unreachable → note that; it only softens the summary, never
  blocks.
- **The instruction file.** Read it. Note whether it already carries the suite's
  `## Continuous-refactoring suite` section and what that names (see
  `## Record`), and whether it already names a `Bookkeeping:` line (a team's
  shared document — then Q4 is answered).
- **The config file.** Read `.scratch/refactor/config.md` if it exists: a
  `Bookkeeping:` pointer, `Ticket-create-mode` and `MR-create-mode` it already
  states are **on record**.
- **Engineering-skills setup.** Read `docs/agents/issue-tracker.md` and
  `docs/agents/triage-labels.md` if they exist. **Both exist → set up**;
  anything less → not set up (a repo-based test — which skills are installed
  on this machine is never consulted). Note whether `triage-labels.md` has a
  `done` row.
- **The tracker.** What `issue-tracker.md` says decides Q1 below
  (`refactoring-operations.md` names the operations and holds the templates):
  - It carries `## Refactoring operations` → the tracker is **on record**.
  - No such section, title `# Issue tracker: GitHub` / `GitLab` /
    `Local Markdown` → on record too; the section is the next write, from
    that template.
  - No such section, and the file describes another tracker → **described**:
    note its name, and which operations the file and the repo's own docs
    (`CONTRIBUTING.md`, the instruction file) already answer.
  - No file → note any sign that a tracker other than the forge is in use
    (the instruction file or `CONTRIBUTING.md` names one, ticket numbers in
    commit messages that match no forge issue).
- **Refactoring Notes.** The Bookkeeping pointer (`refactoring-bookkeeping.md`,
  *Where the Refactoring Notes live*) says where they live; none → the default
  `.scratch/refactor/`. `bookkeeping.md` is missing — that's why onboarding is
  running at all.
- **Earlier state.** A target that ran a version of the suite which kept its
  state in a committed folder has that folder: `docs/refactoring/`, or the
  path an old `Refactoring Notes: <path>` line in the instruction file names,
  holding a `bookkeeping.md`. Read it: the values of `Ticket-create-mode`,
  `MR-create-mode` (or its older name `Create-mode`), `Focus areas` and
  `Refactoring goal` in it are **on record** (Q2 and Q3 are skipped for the
  modes it states), and Q5 offers to move the rest.
- **Partial state — resume.** An earlier onboarding may have been interrupted
  between writes. `## Record`'s order makes that recognisable: the suite's own
  `## Continuous-refactoring suite` section is written **first** (it exists
  only once an earlier onboarding got past its questions, including the
  setup-gap question), then `config.md`, then `bookkeeping.md` **last** (the only
  file whose absence means "not finished"). So the section already being in the instruction file
  means: **skip the setup-gap question** whatever files exist or are missing,
  treat what the files record — the tracker in `issue-tracker.md`, the
  `Bookkeeping:` pointer in `config.md` — as **on record** (don't re-ask it, confirm it in
  `## Summarize` as "already recorded"), and write only what is missing. A
  missing `issue-tracker.md` or `triage-labels.md`, or an `issue-tracker.md`
  without its `## Refactoring operations` section, is then simply the next
  write, in the not-set-up form. `Ticket-create-mode` and `MR-create-mode`
  are on record only if `config.md` already states them; an interruption before
  that write loses them, so Q2 and Q3 are then asked again.
  Nothing is overwritten silently.
- **Was the setup missing?** Needed for `## Closing`. Not set up (above), or —
  on a resume — `triage-labels.md` lacks the `needs-triage` and
  `ready-for-human` rows (the minimal table this onboarding writes, as against
  the engineering skills' full one,
  `triage-labels-template.md`).

## Setup gap

Only when `## Explore` found the engineering-skills setup incomplete and
this is not a resume. One up-front question, before Q1 — asked first because
the answer decides whether the rest is worth asking at all:

`❓ **Q0** - **Engineering-skills setup is incomplete**: <which of the two
files is missing>. The engineering skills (issue-tracker config, triage
labels) set the repo's issue-tracking vocabulary; this suite reads the same
files.` When `## Explore` found signs of another tracker and no
`issue-tracker.md`, add that the setup can describe that tracker, and that
continuing means describing it here (Q1).

- **Abort** — nothing is written. Point the human at the
  `setup-matt-pocock-skills` setup skill, to run first; the next
  `/continuous-refactoring` starts onboarding from scratch. Ends the
  invocation here. This is the only question that can end onboarding without
  writing.
- **Continue without it** — onboarding writes the minimal equivalents itself
  (`## Record`). The setup skill can still be run later; it updates those
  files in place.

Recommendation: **Continue** — the suite works without the setup, and a human
who wants it can add it any time.

## Ask

Before asking anything, summarize `## Explore`'s findings in plain prose —
what's already known (a matched remote or none; whether the engineering-skills setup is
present; anything already on record) and, explicitly, which of Q1–Q5 below
are still open. This comes first so the human isn't asked to re-derive
context already gathered.

Then ask one question at a time — never batch. Each question uses the
numbered shape `/grilling`'s fallback already uses
(`../../refactor-design/references/grilling-fallback.md`):
`❓ **Q1** - **<title>**: <body>`, 2–4 concrete options, one recommended
(`➡️ <recommendation>`) derived from `## Explore`. Ask Q1 — a
single-question `AskUserQuestion` call when available (not all the
questions in one call's `questions` array, even though the tool supports
that), or the same numbered-prose shape otherwise — wait for the reply,
then ask Q2, wait, then Q3, wait, then Q4, wait, then Q5 if it applies, wait. Skip any question `## Explore` found
already on record.

**Q1 — where do issues live?** Skipped when `## Explore` found the tracker
on record. Merge requests are not part of this question: they live on the
forge, read from the Git remote (`refactoring-operations.md`, **Merge
requests**).

- **GitHub** — only offered when Explore found a `github.com` match.
- **GitLab** — only offered when Explore found a `gitlab.com` match.
- **<Name>, as `docs/agents/issue-tracker.md` describes it** — only offered
  when Explore found a described tracker (e.g. "Redmine, as
  `docs/agents/issue-tracker.md` describes it").
- **Another tracker, described here** — only offered when there is no
  `issue-tracker.md`: the human names the tracker and how an agent reaches it.
- **Local Markdown** — always offered, regardless of what else was found:
  refactoring issues tracked as files inside this repo. An existing
  `issue-tracker.md` stays as it is; only the suite's own issues are local.

Recommendation, first match: the described tracker; another tracker
described here, when Explore found signs of one; the matched GitHub/GitLab
option (worded with the reachability finding); **Local Markdown**.

**Q1 follow-ups — the operations.** Only for a described tracker or one
described here; GitHub, GitLab and Local Markdown take their template. One
question at a time, each with a recommendation drawn from what the file and
the repo's docs already state. An operation those already answer is not
asked — it goes into `## Summarize` as read from there.

- **The basics** — only for a tracker described here: how an agent creates,
  reads, lists, comments on and closes an issue. One question, one paragraph
  or a command each.
- **Marking** — how an issue is marked a refactoring candidate, and how a
  priority one (**Candidate**, **Priority**). Labels where the tracker has
  them; otherwise the human names the mechanism (a custom field, a subject
  prefix, child issues of one collecting issue). When `triage-labels.md` is
  missing, the same question covers the three triage roles `needs-info`,
  `ready-for-agent` and `wontfix`.
- **Done** and **Filed date** — recommended from the file: closing an issue
  finishes it, its creation timestamp is the date.
- **Linked merge request** — whether the repo has a convention for how a
  merge request refers to its issue and how to find one from the other. None
  → the bullet is left out.
- **Comment author and time**, **Claim** — recommended from the file when it
  shows comments carrying author and timestamp, and an assignee field. Not
  available → the bullet is left out.

**Q2 — tickets: create automatically, or check with you first?** Skipped when
`config.md`, or the earlier state's `bookkeeping.md`, already states `Ticket-create-mode`.

A ticket is the issue that states a candidate's plan. Creating one is visible
to everyone who watches the tracker, so you can choose to be asked first.

- **Autonomous** — the loop creates tickets as a pass needs them.
  (`Ticket-create-mode: autonomous`)
- **Ask each time** — the loop asks before creating: once per pass for the
  tickets it would create up front for every proposed node, then for the
  ticket of the candidate it chose. With nobody there to answer, it creates
  nothing and says it is waiting. (`Ticket-create-mode: ask-each-time`)

Recommendation: **Autonomous** — the fewest interruptions. (A config file that
doesn't state the field reads as `ask-each-time`; the answer is written down
either way.)

**Q3 — merge requests: open automatically, or check with you first?**
Skipped when `config.md`, or the earlier state's `bookkeeping.md`, already states `MR-create-mode`.

Whichever mode is chosen, review still happens at the merge request, not
the issue — the issue only states the plan; the merge request shows the
actual diff, so you see exactly what changed before it lands, regardless
of mode.

- **Autonomous** — open automatically, right after filing the issue.
  (`MR-create-mode: autonomous`)
- **Ask each time** — check with you before opening each one.
  (`MR-create-mode: ask-each-time`)
- **You open them** — the suite prepares branch + change, you push/open it
  (forge access exists), or commit it yourself directly (it doesn't).
  (`MR-create-mode: human-opens`)

Recommendation: `## Explore` found no git remote at all → recommend
**You open them** — `autonomous`/`ask-each-time` both mean "push and open a
merge request," which has nowhere to go yet; naming this now avoids every
future pass hitting `opening-a-merge-request.md`'s "No forge/remote
available" as a surprise. A remote exists → recommend **Autonomous**, the
suite's existing bias.

**Q4 — where should the suite keep its own state?** Skipped when the
instruction file already names a `Bookkeeping:` line.

The suite needs somewhere for the loop's own state: each Track's cadence, last
scan and open items, plus the learned rejections and, on a tracker without
a **Linked merge request** operation, the merge-request ledger — together, the **bookkeeping
document** and the **Refactoring Notes**. The suite never commits them; how
they reach another machine depends on where they live:

- **Local files (`.scratch/refactor/`)** — recommended. Nothing else to set
  up; whether they go into Git, and how they reach another machine, is up to
  you, and this is meant for one person.
- **A new issue on the tracker** — only offered when the GitHub or GitLab
  template is the tracker's, and only when Explore found the forge reachable.
  The state lives in the issue, so any machine can pick it up; this interview
  creates the issue (the one thing it creates on the forge).
- **As this project describes it** — remote bookkeeping somewhere the project
  names: a ticket, a wiki page. Offered when `## Refactoring operations`
  already has a **Bookkeeping** bullet, or when the human wants to name a
  place. No bullet yet → propose one from what the target's own files say
  about reaching that place (where it lives, what the pointer's value is, how
  it is fetched and stored); the human confirms or changes it, and `## Record`
  writes it. The bullet says how the place is created → this interview
  creates it; otherwise the human names one that exists.
- **One that already exists** — name the file's path, or the pointer value of
  remote bookkeeping, e.g. to continue on a second machine.

Recommendation: **Local files**, unless the human said they work from more
than one machine, then remote bookkeeping. If the human refuses to store the state at
all, don't invent or wire up an alternative: say the suite can't run without
it, write nothing, and end the invocation — the next `/continuous-refactoring`
starts onboarding from scratch.

**Q5 — move the earlier state?** Only when `## Explore` found earlier state.
The folder's `bookkeeping.md`, `merge-requests.md` and `out-of-scope/` would
move to where Q4 says; its create-modes go to the config file, its `Focus
areas` and `Refactoring goal` (when not `none`) to the instruction file.

- **Move it and remove the old files** — recommended. The old files are only
  removed once the new state is written.
- **Move it, keep the old files.**
- **Don't move it** — start fresh; the old files stay untouched.

**Not asked here: `Focus areas` or `Refactoring goal`.** Both free-form, no
filesystem signal to recommend from, and piling on unanchored questions
risks rubber-stamping the whole round. Both are lines in the instruction
file that humans add any time — natural additions for a later, focused pass,
not folded in here.

## Summarize

Before recording anything, recap in plain prose. This is **informational —
there is no approval gate**; the setup-gap question is the only choice that
can end onboarding without writing.

> Tracker: <GitHub | GitLab | Local Markdown | other, as named>.
> Merge requests: <the forge and its tool | none — you land the prepared branch>.
> Operations: <each `## Refactoring operations` bullet, one line; "read from
> `<file>`" for one that wasn't asked> (only for a tracker without a template).
> Ticket-create-mode: <autonomous | ask-each-time>.
> MR-create-mode: <autonomous | ask-each-time | human-opens>.
> Bookkeeping: `<path or pointer value>`, to be recorded in `.scratch/refactor/config.md` (a place is created for it — only when Q4 chose a new one).
> Bookkeeping bullet: <how it is fetched and stored, one line> (only when Q4 wrote one).
> Earlier state: <moved and removed | moved, kept | not moved | none found>.
> Files: <the files `## Record` will write — the instruction file's section,
> `docs/agents/triage-labels.md` and `docs/agents/issue-tracker.md` when
> missing, `.scratch/refactor/config.md`, `<path>`>.
> Labels: `refactor:candidate` and `refactor:priority` are recorded in the
> instruction file only — nothing is created on <the forge>[; label
> overrides recorded (only when the label table is written now): <role →
> existing label>].

Anything the partial-state check found already on record is named as
"already recorded" rather than "just decided" — same lines, sourced from
existing files instead of fresh answers.

## Record

Executed directly by the dispatcher — no plan is handed to another skill.
Each write gets **one short status line** as it happens (e.g. "Wrote
`docs/agents/issue-tracker.md`."), never running silently. **Order matters**:
the instruction file's section goes first (the "onboarding started" marker
`## Explore`'s resume check reads), `config.md` next to last and
`bookkeeping.md` **last** (the
"onboarding complete" marker every other skill reads). A file that already
exists is never overwritten; add only what's missing (a missing section, a
missing table row) and say so.

1. **Backlog labels** → written into the instruction file, creating
   `AGENTS.md` only when neither file exists. Appended under a new
   `## Continuous-refactoring suite` heading if not already present; when the
   heading exists, add only the lines it lacks. A `Bookkeeping:` line goes
   here only when the human named one as a team's shared document (Q4); the
   ordinary pointer is in `config.md` (step 4):

   ```markdown
   ## Continuous-refactoring suite

   Backlog labels: `refactor:candidate` (proposed work) and
   `refactor:priority` (jumps the queue) — see `docs/agents/issue-tracker.md`.
   ```

   The text written here (like every file this interview writes) is
   self-contained: it never cites the suite's own skill files. Every other
   skill in the suite refers to that folder by name — "the Refactoring
   Notes" — never by restating the concrete path.
2. **Triage labels** → `docs/agents/triage-labels.md`:
   - **File exists** → leave it. The tracker's **Done** names a `done`
     marker (the Local Markdown template does) and the table has no `done`
     row → append that one row. Otherwise nothing.
   - Absent → write
     `triage-labels-template.md`'s
     content (its `## Variants` say when the `done` row is dropped and how
     forge overrides apply) — don't restate it here.
3. **Tracker choice** → `docs/agents/issue-tracker.md`. The part every
   tracker gets is the `## Refactoring operations` section, appended when the
   file lacks it; nothing else in an existing file changes. Its content is
   `refactoring-operations.md`'s — don't restate it here.
   - **GitHub or GitLab:** file absent → write the title
     (`# Issue tracker: GitHub` / `GitLab`), one sentence naming the remote,
     and that template's section. File present → append the section.
   - **Local Markdown:** file absent → write
     `local-issue-tracker-template.md`'s content. File present (it describes
     another tracker) → append the Local Markdown section only.
   - **A described tracker:** append the section, built from the Q1
     follow-ups.
   - **A tracker described here:** write the title (`# Issue tracker:
     <Name>`), a `## Conventions` list from the basics the human gave, and
     the section.

   In every case the **Merge requests** bullet states the forge Explore read
   from the Git remote.
4. **Remote bookkeeping** — only when Q4 chose it. A **Bookkeeping** bullet
   the human confirmed in Q4 is added to `## Refactoring operations` first. A
   new place is created the way the bullet says; what names it becomes the
   Bookkeeping pointer. An existing place → the value the human gave.
5. **Earlier state, moved** — only when Q5 chose to move it. The old
   `bookkeeping.md` minus the fields that go elsewhere becomes the new
   document; `out-of-scope/` and `merge-requests.md` come across as they are
   (with remote bookkeeping they are stored with it, `remote-bookkeeping.md`); a
   `housekeeping-template.md` inside a custom old folder moves to
   `docs/refactoring/housekeeping-template.md`. `Focus areas` and `Refactoring
   goal` (when not `none`) are added as lines to the instruction file's
   section; the old `Refactoring Notes:` line and the pointer paragraph that
   named the create-modes are removed from it.
6. **Bookkeeping pointer and the two create-modes** → `.scratch/refactor/config.md`,
   creating the folder if needed. The shape is `refactoring-bookkeeping.md`'s
   *The config file*: the title line, `**Bookkeeping:**` (Q4's path or pointer value,
   default `.scratch/refactor/bookkeeping.md`), `**Ticket-create-mode:**` and
   `**MR-create-mode:**` (Q2/Q3, or the values moved from earlier state). A
   file that already exists keeps the values it has; only missing fields are
   added.
7. **The bookkeeping document** → `<path>/bookkeeping.md` (with remote bookkeeping, the
   working copy under `.scratch/refactor/`, which is then stored as
   `remote-bookkeeping.md` says) — **last**, creating the folder if needed. The shape is
   `refactoring-bookkeeping.md`'s `## Structure`, reduced to the title line
   (`# Refactoring Bookkeeping`) — or, after a move, what the old document
   carried: no Track sections
   (each appears when its Track first runs).
8. **Old files removed** — only when Q5 chose to remove them, and only after
   steps 5–7 are done: the old `bookkeeping.md`, `merge-requests.md`,
   `out-of-scope/`, `fulfilled-set.json` (with local bookkeeping it moves with the
   folder instead) and then the old folder, if empty. They stay in Git
   history if they were ever committed.

No candidate issue is filed, no branch or merge request is opened, no label is
created on the forge, and nothing is committed. The place for remote bookkeeping (step 4)
is not a ticket: `Ticket-create-mode` doesn't govern it.

## Closing

Ends the invocation. Tell the human, in plain prose:

- **What was created** — each file, one line each, and the place for remote bookkeeping
  with its link (and what was already there and left alone). After a move:
  what was moved and what was removed.
- **Commit what belongs in Git** — only when this run wrote something that
  does: the instruction file's section, `docs/agents/triage-labels.md`,
  `docs/agents/issue-tracker.md`, and — after a move — the removal of the old
  folder's files. Everything under `.scratch/refactor/` is the
  developer's own: the suite doesn't commit or ignore it, and whether it goes
  into Git is their call. Nothing committable written → don't mention
  committing at all. A reminder, not a gate.
- **Run `/continuous-refactoring` again** to start the first scan —
  optionally naming a Track (e.g. `/continuous-refactoring guardrails`).
- **The setup was missing** (`## Explore`'s "Was the setup missing?") → the
  engineering skills' setup can still be run later; it updates the files
  written here in place.
- **GitHub only — the two backlog labels.** GitHub doesn't create a label
  when an issue is filed with one that doesn't exist yet (`gh issue create
  --label` fails with a "label not found" error), so always list both
  commands, ready to copy — `--force` makes them safe to run when the label
  already exists:

  ```
  gh label create "refactor:candidate" --description "Proposed refactoring work" --force
  gh label create "refactor:priority" --description "Refactoring work that jumps the queue" --force
  ```

  GitLab needs nothing: creating an issue with a label that doesn't exist
  yet creates that project label. Every other tracker needs nothing.
- **Proposed, not decided** — when no human was present (below), name each
  answer that was taken as a recommendation.

## If no human is present to ask

Two distinct cases:

- **`AskUserQuestion` unavailable, but a human is present** — crash-safe
  fallback: ask the same questions as plain numbered prose instead
  (`❓ **Q1**`/options/`➡️ recommendation`, per `## Ask`), one at a time,
  waiting for each reply in conversation before the next. Only the
  mechanism changes.
- **No human present at all** (an unattended run — e.g. a scripted dry
  run with only a log file as output). Don't guess and proceed as if
  confirmed — that's exactly what this design exists to stop. Take every
  recommended answer as *proposed, not decided* — the setup-gap question
  defaults to **Continue**, a Q1 follow-up nobody can answer makes Q1
  **Local Markdown**, Q4 stays local files at the default location and Q5 becomes *don't move it* — no place for remote
  bookkeeping is created and nothing is removed with nobody there to confirm; never invent a
  custom path with nobody to name one — record it exactly as `## Record`
  describes, but flag every one in the closing text as "recommended, not
  confirmed by a human — first thing to double-check." The human reading
  the closing text can correct any of them by hand at any time.
