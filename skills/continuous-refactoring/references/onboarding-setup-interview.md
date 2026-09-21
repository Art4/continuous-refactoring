# Reference: the onboarding interview

Backs step 0 of `continuous-refactoring` (`skills/continuous-refactoring/SKILL.md`),
which fulfils the `onboarding-setup` node of the tooling tree
(`skills/refactor-scan/references/tooling-tree/onboarding-setup.md`) before any
Track runs. Everywhere else, a tooling-tree node's plan is fixed text a human
wrote once, for every target alike. Onboarding is different on purpose: which
tracker to use, how merge requests get opened, and where the suite's own notes
live are facts about *this* target and *this* human's preference — not
something a tree doc can get right for every target by guessing.

It runs inline in the dispatcher (never in a subagent), once per target, and
**ends the invocation** — no Track selection, no scan, no issue, no merge
request, no branch, nothing created on the forge. It never runs again for a
target whose Refactoring Notes already hold a `bookkeeping.md`.

Parts, in order: **Explore**, **Setup gap** (only when the engineering-skills
setup is incomplete), **Ask**, **Summarize**, **Record**, **Closing**.

**The instruction file.** Wherever this reference says "the instruction file"
it means `AGENTS.md` if it exists, otherwise `CLAUDE.md` — the same order the
suite uses to resolve the Refactoring Notes
(`skills/continuous-refactoring/references/refactoring-bookkeeping.md`, *Where the
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
- **The instruction file.** Read it. Note whether it already names a
  merge-request mode (`autonomous`, `ask-each-time`, `human-opens`, or an
  unambiguous paraphrase) — as a **finding**, never an auto-decision; suite
  state is never inferred silently from it, only offered as a recommendation
  the human still confirms. Note whether it already carries the suite's
  `## Continuous-refactoring suite` section and what that names (see
  `## Record`).
- **Engineering-skills setup.** Read `docs/agents/issue-tracker.md` and
  `docs/agents/triage-labels.md` if they exist. **Both exist → set up**;
  anything less → not set up (a repo-based test — which skills are installed
  on this machine is never consulted). An existing `issue-tracker.md` also
  answers Q1 below: its title names the tracker (`# Issue tracker: GitHub` /
  `GitLab` / `Local Markdown`, or a freeform description for anything else).
  Note the tracker's native-label status from it and whether
  `triage-labels.md` has a `done` row.
- **Refactoring Notes.** The instruction file's `Refactoring Notes:` line
  says where they live; none → the default `docs/refactoring/`.
  `bookkeeping.md` is missing — that's why onboarding is running at all.
- **Partial state — resume.** An earlier onboarding may have been interrupted
  between writes. `## Record`'s order makes that recognisable: the suite's own
  `## Continuous-refactoring suite` section is written **first** (it exists
  only once an earlier onboarding got past its questions, including the
  setup-gap question), `bookkeeping.md` **last** (the only file whose absence
  means "not finished"). So the section already being in the instruction file
  means: **skip the setup-gap question** whatever files exist or are missing,
  treat what the files record — the tracker in `issue-tracker.md`, the
  `Refactoring Notes:` line — as **on record** (don't re-ask it, confirm it in
  `## Summarize` as "already recorded"), and write only what is missing. A
  missing `issue-tracker.md` or `triage-labels.md` is then simply the next
  write, in the not-set-up form. `Create-mode` is the one answer an
  interruption can lose: its only home is `bookkeeping.md` (the instruction
  file holds a pointer, never the value), so Q2 is asked again (the earlier
  answer is at most an instruction-file finding, a recommendation only).
  Nothing is overwritten silently.
- **Was the setup missing?** Needed for `## Closing`. Not set up (above), or —
  on a resume — `triage-labels.md` lacks the `needs-triage` and
  `ready-for-human` rows (the minimal table this onboarding writes, as against
  the engineering skills' full one,
  `skills/continuous-refactoring/references/triage-labels-template.md`).

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
what's already known (a matched remote or none; an instruction-file
create-mode finding, or none; whether the engineering-skills setup is
present; anything already on record) and, explicitly, which of Q1–Q3 below
are still open. This comes first so the human isn't asked to re-derive
context already gathered.

Then ask one question at a time — never batch. Each question uses the
numbered shape `/grilling`'s fallback already uses
(`skills/refactor-design/references/grilling-fallback.md`):
`❓ **Q1** - **<title>**: <body>`, 2–4 concrete options, one recommended
(`➡️ <recommendation>`) derived from `## Explore`. Ask Q1 — a
single-question `AskUserQuestion` call when available (not all three
questions in one call's `questions` array, even though the tool supports
that), or the same numbered-prose shape otherwise — wait for the reply,
then ask Q2, wait, then Q3, wait. Skip any question `## Explore` found
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

**Q2 — merge requests: open automatically, or check with you first?**

Whichever mode is chosen, review still happens at the merge request, not
the issue — the issue only states the plan; the merge request shows the
actual diff, so you see exactly what changed before it lands, regardless
of mode.

- **Autonomous** — open automatically, right after filing the issue.
  (`Create-mode: autonomous`)
- **Ask each time** — check with you before opening each one.
  (`Create-mode: ask-each-time`)
- **You open them** — the suite prepares branch + change, you push/open it
  (forge access exists), or commit it yourself directly (it doesn't).
  (`Create-mode: human-opens`)

Recommendation: `## Explore` found no git remote at all → recommend
**You open them** — `autonomous`/`ask-each-time` both mean "push and open a
merge request," which has nowhere to go yet; naming this now avoids every
future pass hitting `opening-a-merge-request.md`'s "No forge/remote
available" as a surprise. A remote exists → whatever the instruction file
already named, said explicitly ("AGENTS.md already says autonomous");
neither names one → recommend **Autonomous**, the suite's existing default
bias.

**Q3 — where should the suite keep its own metadata?**

The suite needs a folder for the loop's own state: `bookkeeping.md` (this
interview's own decisions), `merge-requests.md` (in-flight merge-request
bookkeeping, only when the tracker has no native labels), and
`out-of-scope/` (learned rejections) — together, the **Refactoring
Notes**. It is committed to git, same as any other project file — that's what
lets config/rejections survive across passes and stay visible to the whole
team, and the only mode this suite supports. So the question is only *where*:

- **Default location (`docs/refactoring/`)** — recommended.
- **A different location** — name the path.

Recommendation: always the default location. If the human refuses to store
the Refactoring Notes at all, don't invent or wire up an alternative: say the
suite can't run without them, write nothing, and end the invocation — the
next `/continuous-refactoring` starts onboarding from scratch.

**Not asked here: `Focus areas` or `Refactoring goal`.** Both free-form, no
filesystem signal to recommend from, and piling on unanchored questions
risks rubber-stamping the whole round. Both stay hand-editable any time,
same as `Create-mode` — natural additions for a later, focused pass, not
folded in here.

## Summarize

Before recording anything, recap in plain prose. This is **informational —
there is no approval gate**; the setup-gap question is the only choice that
can end onboarding without writing.

> Tracker: <GitHub | GitLab | Local Markdown | other, as named>.
> Create-mode: <autonomous | ask-each-time | human-opens>.
> Refactoring Notes: `<path>`, to be recorded in the instruction file.
> Files: <the files `## Record` will write — the instruction file's section,
> `docs/agents/triage-labels.md` and `docs/agents/issue-tracker.md` when
> missing, `<path>/bookkeeping.md`>.
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
`## Explore`'s resume check reads) and `bookkeeping.md` **last** (the
"onboarding complete" marker every other skill reads). A file that already
exists is never overwritten; add only what's missing (a missing section, a
missing table row) and say so.

1. **Refactoring Notes path and backlog labels** → written into the
   instruction file, creating `AGENTS.md` only when neither file exists.
   Appended under a new `## Continuous-refactoring suite` heading if not
   already present; when the heading exists, add only the lines it lacks.
   `<path>` is Q3's answer (default `docs/refactoring/`):

   ```markdown
   ## Continuous-refactoring suite

   Refactoring Notes: `<path>` — the continuous-refactoring
   suite's own config, in-flight merge-request bookkeeping, and
   rejected-tooling records live here.

   Create-mode: see the Refactoring Notes' `bookkeeping.md` — that file is
   the sole authoritative value, this is a pointer, not a copy.

   Backlog labels: `refactor:candidate` (proposed work) and
   `refactor:priority` (jumps the queue) — see `docs/agents/issue-tracker.md`.
   ```

   The text written here (like every file this interview writes) is
   self-contained: it never cites the suite's own skill files. Every other
   skill in the suite refers to this folder by name — "the Refactoring
   Notes" — never by restating the concrete path.
2. **Triage labels** → `docs/agents/triage-labels.md`:
   - **File exists** → leave it. Local Markdown tracker and it has no `done`
     row → append that one row. Otherwise nothing.
   - Absent → write
     `skills/continuous-refactoring/references/triage-labels-template.md`'s
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
     `skills/continuous-refactoring/references/local-issue-tracker-template.md`'s
     content verbatim — don't restate it here, avoid two drifting copies.
   - **Something else:** same shape as the two cases above, from what the
     human described; no description given → fall through to Local
     Markdown.
4. **Create-mode** → the Refactoring Notes' `bookkeeping.md` — **last**,
   creating the folder if needed. It is the sole write-authority for
   `Create-mode`; the instruction file (step 1) holds only a pointer to it.
   The shape is `refactoring-bookkeeping.md`'s `## Structure`, reduced to
   the title line and `Create-mode`: no `Pending candidates` (nothing is
   pending), no Track sections (each appears when its Track first runs).
   `Focus areas` only if the human named one unprompted.

No issue is filed, no branch or merge request is opened, no label is created
on the forge, and nothing is committed — the human commits the files.

## Closing

Ends the invocation. Tell the human, in plain prose:

- **What was created** — each file, one line each (and what was already
  there and left alone).
- **Commit them.** The new files should reach the default branch (commit and
  merge them): candidate branches are based on it, so they only contain the
  Refactoring Notes once it does. Not checked here — a reminder, not a gate.
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
  defaults to **Continue**, Q3 stays the default location; never invent a
  custom path with nobody to name one — record it exactly as `## Record`
  describes, but flag every one in the closing text as "recommended, not
  confirmed by a human — first thing to double-check." The human reading
  the closing text can correct any of them by hand at any time.
