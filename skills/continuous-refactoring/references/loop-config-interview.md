# Reference: the `loop-config` interview

Backs `refactor-design`'s step 1 exception for the `loop-config` node
(`skills/refactor-design/SKILL.md`) — the one tooling-tree node whose plan
isn't already fully specified by `skills/refactor-scan/references/tooling-tree.md`
alone. Everywhere else, a tooling-tree node's Tool/Purpose/Fulfilment
check/MR scope are fixed text a human already wrote once, for every target
alike. `loop-config` is different on purpose: which tracker to use, how
merge requests get opened, and where the suite's own notes live are facts
about *this* target and *this* human's preference — not something a tree
doc can get right for every target by guessing. Run this once, the first
time `loop-config` is chosen; it never runs again for a target whose
Refactoring Notes (see `## Explore`) already hold a `bookkeeping.md`.

Four parts, in order: **Explore**, **Ask**, **Summarize**, **Record**.

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
- **`AGENTS.md` / `CLAUDE.md`.** Read whichever exists. Note whether either
  already names a merge-request mode (`autonomous`, `ask-each-time`,
  `human-opens`, or an unambiguous paraphrase) — as a **finding**, never an
  auto-decision; suite state is never inferred silently from these files,
  only offered as a recommendation the human still confirms. Both exist and
  disagree → note the conflict explicitly.
- **`CONTEXT.md`.** Note whether it exists — informational only.
- **Refactoring Notes / `bookkeeping.md`.** Check whether `AGENTS.md`, then
  `CLAUDE.md`, already names a `Refactoring Notes:` line (`## Record`
  below) — if one does, that's where to look for `bookkeeping.md`; if neither
  does, check the default `docs/refactoring/`. Note whether the folder
  exists, and separately whether `bookkeeping.md` already exists inside it.
  Should be rare to impossible on a genuinely fresh target — `loop-config`'s
  own Fulfilment check already gates on `bookkeeping.md` *not* existing wherever
  it resolves to. If it's there anyway (a resumed pass, an out-of-band
  write): **don't re-run the interview.** Read what's already recorded —
  `bookkeeping.md`'s `Create-mode` if set, `docs/agents/issue-tracker.md` if it
  exists (its title names which tracker — see `## Record`) — and skip
  asking whatever's already answered. If all three questions below are
  already answered this way, skip straight to `## Summarize` with a recap
  of what's on record; nothing new to write.
- **Existing tracker hints.** Note whether `docs/agents/issue-tracker.md`
  or `docs/agents/triage-labels.md` already exist — neither should on a
  genuinely fresh target, but an existing convention is a strong signal for
  Q1 below, never something to silently overwrite.

## Ask

Before asking anything, summarize `## Explore`'s findings in plain prose —
what's already known (a matched remote or none; an `AGENTS.md`/`CLAUDE.md`
create-mode finding, or none; any existing tracker hints) and, explicitly,
which of Q1–Q3 below are still open (skip naming one `## Explore`'s resume
case already answered). This comes first so the human isn't asked to
re-derive context already gathered.

Then ask one question at a time — never batch. Each question uses the
numbered shape `/grilling`'s fallback already uses
(`skills/refactor-design/references/grilling-fallback.md`):
`❓ **Q1** - **<title>**: <body>`, 2–4 concrete options, one recommended
(`➡️ <recommendation>`) derived from `## Explore`. Ask Q1 — a
single-question `AskUserQuestion` call when available (not all three
questions in one call's `questions` array, even though the tool supports
that), or the same numbered-prose shape otherwise — wait for the reply,
then ask Q2, wait, then Q3, wait. Skip any question `## Explore`'s resume
case already answered.

**Q1 — where do issues and merge requests live?**

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
available" as a surprise. A remote exists → whatever `AGENTS.md`/`CLAUDE.md`
already named, said explicitly ("AGENTS.md already says autonomous"); both
files disagree → name the conflict in the question body, recommend
`ask-each-time` as the safer tie-break (resolving the underlying
disagreement is the target repo's problem, not this interview's); neither
names one → recommend **Autonomous**, the suite's existing default bias.

**Q3 — where should the suite keep its own metadata?**

A folder is needed to store the loop's own state: `bookkeeping.md` (this
interview's own decisions), `merge-requests.md` (in-flight merge-request
bookkeeping, only when the tracker has no native labels), and
`out-of-scope/` (learned rejections) — together, the **Refactoring
Notes**. Recommended — and the only mode this suite supports today — to
commit this folder to git, same as any other project file: that's what
lets config/rejections survive across passes and stay visible to the whole
team, not a private or gitignored scratch space.

- **Yes, default location (`docs/refactoring/`)** — recommended.
- **Yes, a different location** — name the path.
- **No** — stop here (see below).

Recommendation: always **Yes, default location**. On **No**: don't invent
or wire up an alternative — out of this interview's scope. Stop here (skip
`## Summarize`/`## Record` for whatever's still open); `refactor-design`
reports the `loop-config` candidate as not filed this pass, reason "human
objected to storing the Refactoring Notes at all; the suite has no
alternative today" — the pass ends the same way it ends when nothing
survives prioritising. Next pass, `refactor-scan` proposes `loop-config`
again from scratch and this interview runs again, since nothing was
recorded.

**Not asked here: `Focus areas`.** Free-form, no filesystem signal to
recommend from, and a fourth unanchored question risks rubber-stamping the
whole round. Stays hand-editable any time, same as `Create-mode` — a
natural addition for a later, focused pass, not folded in here.

## Summarize

Before recording anything, recap in plain prose:

> Tracker: <GitHub | GitLab | Local Markdown | other, as named>.
> Create-mode: <autonomous | ask-each-time | human-opens>.
> Refactoring Notes: `<path>`, to be recorded in `AGENTS.md`/`CLAUDE.md`.

(When `## Explore`'s resume case skipped questions, name those as "already
recorded" rather than "just decided" — same three lines, sourced from
existing files instead of fresh answers.)

## Record

What `refactor-design` files as this candidate's plan
(`skills/refactor-design/SKILL.md` step 5's `loop-config` exception);
`refactor-implement` performs the actual writes later, from that plan
(`skills/refactor-implement/SKILL.md` step 1's `loop-config` exception):

- **Create-mode** → the Refactoring Notes' `bookkeeping.md`'s `Create-mode`
  field — the sole write-authority (`docs/adr/0025-agents-md-gets-a-create-mode-pointer-not-the-value.md`).
  `AGENTS.md`/`CLAUDE.md` (below) gets only a read-only pointer to it, never
  the value itself.
- **Tracker choice** → `docs/agents/issue-tracker.md`, created fresh:
  - **GitHub or GitLab:** title names which (`# Issue tracker: GitHub` /
    `GitLab`) — the one signal every lifecycle skill now reads instead of
    re-probing `gh`/`glab` independently. Below the title: which remote,
    that labels are native (`refactor:candidate`, and the triage roles
    from `docs/agents/triage-labels.md` apply directly, no local mirror —
    no `refactor:delivered` or other in-flight label; a candidate's
    linked pull request, native to the tracker, is what's in flight —
    `docs/adr/0026-drop-delivered-label-use-native-pr-linkage.md`), and
    the two operations every skill needs ("file an issue": `gh`/`glab
    issue create` or the forge UI on `origin`; "check the external
    tracker": query the forge directly).
  - **Local Markdown:** write
    `skills/continuous-refactoring/references/local-issue-tracker-template.md`'s
    content verbatim — don't restate it here, avoid two drifting copies.
  - **Something else:** same shape as the two cases above, from what the
    human described; no description given → fall through to Local
    Markdown.
- **Refactoring Notes path** → written, labeled `Refactoring Notes:`, into
  whichever of the target's `AGENTS.md`/`CLAUDE.md` already exists — never
  create the other one instead; only when neither exists, create
  `AGENTS.md`. Appended under a new `## Continuous-refactoring suite`
  heading if not already present:

  ```markdown
  ## Continuous-refactoring suite

  Refactoring Notes: `docs/refactoring/` — the continuous-refactoring
  suite's own config, in-flight merge-request bookkeeping, and
  rejected-tooling records live here.

  Create-mode: see the Refactoring Notes' `bookkeeping.md` — that file is
  the sole authoritative value, this is a pointer, not a copy.

  Backlog label: `refactor:candidate` (native tracker only — see
  `docs/agents/issue-tracker.md`).
  ```

  Every other skill in the suite refers to this folder by name — "the
  Refactoring Notes" — never by restating the concrete path (see
  `skills/continuous-refactoring/references/refactoring-bookkeeping.md` for the
  resolution rule every skill, and the deterministic parser, follow). Also
  gates whether the interview (and the candidate) proceeds at all — see
  Q3's **No** case above.

## If no human is present to ask

Two distinct cases:

- **`AskUserQuestion` unavailable, but a human is present** — crash-safe
  fallback: ask the same three questions as plain numbered prose instead
  (`❓ **Q1**`/options/`➡️ recommendation`, per `## Ask`), one at a time,
  waiting for each reply in conversation before the next. Only the
  mechanism changes.
- **No human present at all** (an unattended run — e.g. a scripted dry
  run with only a log file as output). Don't guess and proceed as if
  confirmed — that's exactly what this redesign exists to stop. Take every
  recommended answer from `## Ask` as *proposed, not decided* — Q3's stays
  the default location; never invent a custom path with nobody to name one
  — record it exactly as `## Record` describes, but flag every one in the
  candidate issue and this pass's closing report as "recommended, not
  confirmed by a human — first thing to double-check." A later pass or the
  human reading the issue can correct any of the three by hand at any
  time.
