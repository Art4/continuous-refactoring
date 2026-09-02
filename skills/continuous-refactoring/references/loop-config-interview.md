# Reference: the `loop-config` interview

Backs `refactor-design`'s step 1 exception for the `loop-config` node
(`skills/refactor-design/SKILL.md`) — the one tooling-tree node whose plan
isn't already fully specified by `skills/refactor-scan/references/tooling-tree.md`
alone. Everywhere else, a tooling-tree node's Tool/Purpose/Fulfilment
check/MR scope are fixed text a human already wrote once, for every target
alike. `loop-config` is different on purpose: which tracker to use, how
merge requests get opened, and confirming where suite state lives are facts
about *this* target and *this* human's preference — not something a tree
doc can get right for every target by guessing. Run this once, the first
time `loop-config` is chosen; it never runs again for a target that already
has `docs/refactoring/config.md`.

Four parts, in order: **Explore**, **Ask**, **Summarize**, **Record**.

## Explore

Read-only. No writes, no questions yet.

- **Git remote.** `git remote -v` on `origin`. Host is `github.com` → GitHub
  match; `gitlab.com` → GitLab match; a different host, or no `origin` at
  all → no match (a `.gitlab-ci.yml` at the root is a weak self-hosted-GitLab
  signal, not something to guess a match from — let the human name it).
  When matched, try one reachability check before asking (`gh repo view` /
  `glab repo view`) — success strengthens the recommendation below, failure
  doesn't rule the option out, only softens the recommendation's wording.
- **`AGENTS.md` / `CLAUDE.md`.** Read whichever exists. Note whether either
  already names a merge-request mode (`autonomous`, `ask-each-time`,
  `human-opens`, or an unambiguous paraphrase) — as a **finding**, never an
  auto-decision; suite state is never inferred silently from these files,
  only offered as a recommendation the human still confirms. Both exist and
  disagree → note the conflict explicitly.
- **`CONTEXT.md`.** Note whether it exists — informational only.
- **`docs/refactoring/` and `config.md`.** Note whether the folder exists,
  and separately whether `config.md` already exists inside it. Should be
  rare to impossible — `loop-config`'s own Fulfilment check already gates
  on `config.md` *not* existing. If it's there anyway (a resumed pass, an
  out-of-band write): **don't re-run the interview.** Read what's already
  recorded — `config.md`'s `Create-mode` if set, `docs/agents/issue-tracker.md`
  if it exists (its title names which tracker — see `## Record`) — and
  skip asking whatever's already answered. If all three questions below
  are already answered this way, skip straight to `## Summarize` with a
  recap of what's on record; nothing new to write.
- **Existing tracker hints.** Note whether `docs/agents/issue-tracker.md`
  or `docs/agents/triage-labels.md` already exist — neither should on a
  genuinely fresh target, but an existing convention is a strong signal for
  Q1 below, never something to silently overwrite.

## Ask

Ask the whole set in one round — the shape `/grilling`'s fallback already
uses (`skills/refactor-design/references/grilling-fallback.md`): number
each question (`❓ **Q1** - **<title>**: <body>`), 2–4 concrete options,
one recommended (`➡️ <recommendation>`) derived from `## Explore`, then
wait. Use `AskUserQuestion` if available; otherwise the same numbered-prose
shape. Skip any question `## Explore`'s resume case already answered.

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

- **Autonomous** — open automatically, right after filing the issue.
  (`Create-mode: autonomous`)
- **Ask each time** — check with you before opening each one.
  (`Create-mode: ask-each-time`)
- **You open them** — the suite prepares branch + change, you push/open it.
  (`Create-mode: human-opens`)

Recommendation: whatever `AGENTS.md`/`CLAUDE.md` already named, said
explicitly ("AGENTS.md already says autonomous"); both files disagree →
name the conflict in the question body, recommend `ask-each-time` as the
safer tie-break (resolving the underlying disagreement is the target
repo's problem, not this interview's); neither names one → recommend
**Autonomous**, the suite's existing default bias.

**Q3 — is `docs/refactoring/` OK as the storage location?**

Confirmation only, not a real fork — the path is already hardcoded
throughout every skill in this suite; there's no alternative to plumb
through today.

- **Yes** — proceed.
- **No** — stop here (see below).

Recommendation: always **Yes**. On **No**: don't invent or wire up an
alternative — out of this interview's scope. Stop here (skip
`## Summarize`/`## Record` for whatever's still open); `refactor-design`
reports the `loop-config` candidate as not filed this pass, reason "human
objected to `docs/refactoring/` as the storage location; the suite has no
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
> Storage: `docs/refactoring/` confirmed.

(When `## Explore`'s resume case skipped questions, name those as "already
recorded" rather than "just decided" — same three lines, sourced from
existing files instead of fresh answers.)

## Record

What `refactor-design` files as this candidate's plan
(`skills/refactor-design/SKILL.md` step 5's `loop-config` exception);
`refactor-implement` performs the actual writes later, from that plan
(`skills/refactor-implement/SKILL.md` step 1's `loop-config` exception):

- **Create-mode** → `docs/refactoring/config.md`'s `Create-mode` field.
- **Tracker choice** → `docs/agents/issue-tracker.md`, created fresh:
  - **GitHub or GitLab:** title names which (`# Issue tracker: GitHub` /
    `GitLab`) — the one signal every lifecycle skill now reads instead of
    re-probing `gh`/`glab` independently. Below the title: which remote,
    that labels are native (`refactor:candidate`, `refactor:delivered`,
    and the triage roles from `docs/agents/triage-labels.md` apply
    directly, no local mirror), and the two operations every skill needs
    ("file an issue": `gh`/`glab issue create` or the forge UI on
    `origin`; "check the external tracker": query the forge directly).
  - **Local Markdown:** write
    `skills/continuous-refactoring/references/local-issue-tracker-template.md`'s
    content verbatim — don't restate it here, avoid two drifting copies.
  - **Something else:** same shape as the two cases above, from what the
    human described; no description given → fall through to Local
    Markdown.
- **Storage-location confirmation** → nothing written; only gates whether
  the interview (and the candidate) proceeds at all.

## If no human is present to ask

Two distinct cases:

- **`AskUserQuestion` unavailable, but a human is present** — crash-safe
  fallback: ask the same three questions as plain numbered prose instead
  (`❓ **Q1**`/options/`➡️ recommendation`, per `## Ask`), wait for the
  reply in conversation. Only the mechanism changes.
- **No human present at all** (an unattended run — e.g. a scripted dry
  run with only a log file as output). Don't guess and proceed as if
  confirmed — that's exactly what this redesign exists to stop. Take every
  recommended answer from `## Ask` as *proposed, not decided*, record it
  exactly as `## Record` describes, but flag every one in the candidate
  issue and this pass's closing report as "recommended, not confirmed by a
  human — first thing to double-check." A later pass or the human reading
  the issue can correct any of the three by hand at any time.
