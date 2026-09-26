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
**ends the invocation** — no Track selection, no scan, no issue, no merge
request, no branch, nothing created on the forge. It never runs again for a
target whose Bookkeeping pointer already resolves to an existing `bookkeeping.md`.

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
  on this machine is never consulted). An existing `issue-tracker.md` also
  answers Q1 below: its title names the tracker (`# Issue tracker: GitHub` /
  `GitLab` / `Local Markdown`, or a freeform description for anything else).
  Note the tracker's native-label status from it and whether
  `triage-labels.md` has a `done` row.
- **Refactoring Notes.** The Bookkeeping pointer (`refactoring-bookkeeping.md`,
  *Where the Refactoring Notes live*) says where they live; none → the default
  `.scratch/refactor/`. `bookkeeping.md` is missing — that's why onboarding is
  running at all.
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
  missing `issue-tracker.md` or `triage-labels.md` is then simply the next
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
files.`

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
present; anything already on record) and, explicitly, which of Q1–Q4 below
are still open. This comes first so the human isn't asked to re-derive
context already gathered.

Then ask one question at a time — never batch. Each question uses the
numbered shape `/grilling`'s fallback already uses
(`../../refactor-design/references/grilling-fallback.md`):
`❓ **Q1** - **<title>**: <body>`, 2–4 concrete options, one recommended
(`➡️ <recommendation>`) derived from `## Explore`. Ask Q1 — a
single-question `AskUserQuestion` call when available (not all four
questions in one call's `questions` array, even though the tool supports
that), or the same numbered-prose shape otherwise — wait for the reply,
then ask Q2, wait, then Q3, wait, then Q4, wait. Skip any question `## Explore` found
already on record.

**Q1 — where do issues and merge requests live?** Skipped when
`docs/agents/issue-tracker.md` exists — its title already answers it.

- **GitHub** — only offered when Explore found a `github.com` match.
- **GitLab** — only offered when Explore found a `gitlab.com` match.
- **Local Markdown** — always offered, regardless of what else was found:
  issues and merge requests tracked as files inside this repo, no forge
  involved.
- **Something else** — the human names a different tracker. Note what they
  named; fall through to the Local Markdown template for the actual
  mechanics unless they describe a different concrete convention — this
  suite ships native handling for GitHub and GitLab only.

Recommendation: the matched GitHub/GitLab option (worded with the
reachability finding) when one exists; **Local Markdown** when no match was
found, or when a match was a different/unrecognized host ("no built-in
native handling for this host yet — Local Markdown works everywhere; pick
'something else' if you'd rather describe a different convention").

**Q2 — tickets: create automatically, or check with you first?** Skipped when
`config.md` already states `Ticket-create-mode`.

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
Skipped when `config.md` already states `MR-create-mode`.

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

The suite needs a folder for the loop's own state: `bookkeeping.md` (each
Track's cadence, last scan and open items), `merge-requests.md` (in-flight
merge-request bookkeeping, only when the tracker has no native labels), and
`out-of-scope/` (learned rejections) — together, the **Refactoring
Notes**. The suite writes these files and never commits them; whether they go
into Git, and how they reach another machine, is the developer's job — this is
for one person. So the question is only *where*:

- **Default location (`.scratch/refactor/`)** — recommended.
- **A different location** — name the path of the `bookkeeping.md`.

Recommendation: always the default location. If the human refuses to store
the Refactoring Notes at all, don't invent or wire up an alternative: say the
suite can't run without them, write nothing, and end the invocation — the
next `/continuous-refactoring` starts onboarding from scratch.

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
> Ticket-create-mode: <autonomous | ask-each-time>.
> MR-create-mode: <autonomous | ask-each-time | human-opens>.
> Bookkeeping: `<path>`, to be recorded in `.scratch/refactor/config.md`.
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
   - **File exists** → leave it. Local Markdown tracker and it has no `done`
     row → append that one row. Otherwise nothing.
   - Absent → write
     `triage-labels-template.md`'s
     content (its `## Variants` say when the `done` row is dropped and how
     forge overrides apply) — don't restate it here.
3. **Tracker choice** → `docs/agents/issue-tracker.md`, only when absent:
   - **GitHub or GitLab:** title names which (`# Issue tracker: GitHub` /
     `GitLab`) — the one signal every lifecycle skill reads instead of
     re-probing `gh`/`glab` independently. Below the title: which remote,
     that labels are native (`refactor:candidate`, `refactor:priority`, and
     the triage roles from `docs/agents/triage-labels.md` apply directly, no
     local mirror — no `refactor:delivered` or other in-flight label; a
     candidate's linked pull request, native to the tracker, is what's in
     flight; a closed issue is a done one, no `done` label), and the two
     operations every skill needs ("file an issue": `gh`/`glab issue create`
     or the forge UI on `origin`; "check the external tracker": query the
     forge directly).
   - **Local Markdown:** write
     `local-issue-tracker-template.md`'s
     content verbatim — don't restate it here, avoid two drifting copies.
   - **Something else:** same shape as the two cases above, from what the
     human described; no description given → fall through to Local
     Markdown.
4. **Bookkeeping pointer and the two create-modes** → `.scratch/refactor/config.md`,
   creating the folder if needed. The shape is `refactoring-bookkeeping.md`'s
   *The config file*: the title line, `**Bookkeeping:**` (Q4's path, default
   `.scratch/refactor/bookkeeping.md`), `**Ticket-create-mode:**` and
   `**MR-create-mode:**`. A file that already exists keeps the values it has;
   only missing fields are added.
5. **The bookkeeping document** → `<path>/bookkeeping.md` — **last**, creating
   the folder if needed. The shape is `refactoring-bookkeeping.md`'s
   `## Structure`, reduced to the title line (`# Refactoring Bookkeeping`):
   no `Pending candidates` (nothing is pending), no Track sections (each
   appears when its Track first runs).

No issue is filed, no branch or merge request is opened, no label is created
on the forge, and nothing is committed.

## Closing

Ends the invocation. Tell the human, in plain prose:

- **What was created** — each file, one line each (and what was already
  there and left alone).
- **Commit what belongs in Git** — only when this run wrote something that
  does: the instruction file's section, `docs/agents/triage-labels.md`,
  `docs/agents/issue-tracker.md`. Everything under `.scratch/refactor/` is the
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
  yet creates that project label. Local Markdown needs nothing.
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
  defaults to **Continue**, Q4 stays the default location; never invent a
  custom path with nobody to name one — record it exactly as `## Record`
  describes, but flag every one in the closing text as "recommended, not
  confirmed by a human — first thing to double-check." The human reading
  the closing text can correct any of them by hand at any time.
