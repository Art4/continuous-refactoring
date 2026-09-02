# `loop-config` runs a human interview instead of guessing tracker, create-mode, and storage

> Amends [ADR-0006](0006-loop-delivers-remembered-merge-requests.md): its "read `AGENTS.md` / `CLAUDE.md`
> first; if neither says, propose `autonomous` and remember" mechanism (line 27) is replaced by a one-time,
> human-confirmed interview, run when `loop-config` itself is filed rather than inferred fresh per merge
> request. The side-constraint ADR-0006 already established stands unchanged: create-mode is suite state
> under `docs/refactoring/`, never written into `AGENTS.md` / `CLAUDE.md` themselves.
>
> Cross-references [ADR-0012](0012-remembered-merge-requests-follow-the-tracker.md): its
> tracker-representability split stands exactly as decided — `config.md`'s fields (`Create-mode`,
> `Focus areas`, `Pending candidates`, `Fulfilled nodes`) stay tracker-agnostic, "none of that data is
> tracker-representable." The interview below adds no new `config.md` field for tracker type; the tracker
> decision is recorded in `docs/agents/issue-tracker.md`, exactly where ADR-0012 already locates that fact.

Run against a real target (`continuous-refactoring.de`), `loop-config` surfaced two problems with guessing
instead of asking. First, create-mode: ADR-0006's fallback ("if neither `AGENTS.md` nor `CLAUDE.md` says,
propose `autonomous`") means a human who never wrote either file gets an autonomous merge-request loop
silently, discovering the choice only after merge requests are already open. Second, tracker discovery: no
skill ever records "does this target's issue tracker support native labels" as a fact anywhere — five-plus
call sites (`refactor-scan`, `refactor-prioritize`, `refactor-learn`, more than once each) each independently
re-derive it, and `docs/agents/issue-tracker.md`, the one file the orchestrator already points at
(`skills/continuous-refactoring/SKILL.md`, "see docs/agents/issue-tracker.md"), is never actually created by
any skill — only the test harness fakes its existence for dry runs.

The user's framing: stop trying to deterministically detect or guess at the `loop-config` node, and ask the
human instead — explore the target for signals first (git remote, `AGENTS.md`/`CLAUDE.md`, `CONTEXT.md`,
`docs/refactoring/`), then present findings and ask, with recommended answers, rather than silently deciding.

## Decision

`loop-config`'s MR scope becomes a **procedure**, not fixed text: the interview in
`skills/continuous-refactoring/references/loop-config-interview.md`, run once, the first time `loop-config`
is chosen as a candidate (never again once `docs/refactoring/config.md` exists). It has four parts — Explore
(read-only: git remote, `AGENTS.md`/`CLAUDE.md`, `CONTEXT.md`, `docs/refactoring/`, existing tracker hints),
Ask (one round, three questions, each with 2–4 options and a recommendation derived from Explore —
`AskUserQuestion` when available, the same numbered-prose shape `/grilling`'s fallback already uses
otherwise), Summarize (a plain-prose recap before anything is written), Record (where each decision lands).

Three questions, each decided by the human, never inferred silently:

1. **Where do issues and merge requests live?** GitHub/GitLab offered only when Explore found a matching
   remote; Local Markdown always offered; "something else" lets the human name an unsupported convention,
   falling back to the Local Markdown template for mechanics. Recorded in a freshly created
   `docs/agents/issue-tracker.md` — title names the tracker, the one fact every lifecycle skill now reads
   instead of re-probing `gh`/`glab` independently.
2. **Merge requests: autonomous, ask each time, or human opens?** Recommendation drawn from
   `AGENTS.md`/`CLAUDE.md` when either already names a mode (conflict between the two → name it, recommend
   the safer `ask-each-time` tie-break); otherwise recommend `autonomous`, the suite's existing default bias.
   Recorded in `config.md`'s `Create-mode` field, written once by `refactor-implement` when it creates the
   file — not left for `refactor-learn` to fill in on first bookkeeping, as ADR-0006 had it.
3. **Is `docs/refactoring/` OK as the storage location?** Confirmation only, not a real fork — the path is
   hardcoded throughout the suite; no alternative exists to plumb through today. A "no" stops the pass
   without writing anything; `loop-config` is proposed again from scratch next pass.

The five-plus call sites that previously re-derived "does the tracker support native labels" (in
`refactor-scan`, `refactor-prioritize`, `refactor-learn`) now read `docs/agents/issue-tracker.md` instead.

## Considered Options

- **Keep guessing per ADR-0006, only tighten the fallback wording.** Rejected: guessing is exactly what the
  user asked to stop — a human who never wrote `AGENTS.md`/`CLAUDE.md` still deserves to be asked once,
  explicitly, before an autonomous loop starts opening merge requests unsupervised.
- **Add a new tracker-type field to `config.md`.** Rejected: breaks ADR-0012's tracker-representability
  split — that data already has a home (`docs/agents/issue-tracker.md`), a second copy in `config.md` would
  drift.
- **Make `docs/refactoring/` a real configurable path.** Rejected: far larger surface (every skill's
  hardcoded path), not needed to solve the guessing problem — a confirmation question is enough for now.
- **Fold `Focus areas` into the same interview round.** Rejected: no filesystem signal exists to recommend
  an answer from, and a fourth unanchored question risks the human rubber-stamping the whole round instead
  of engaging with the three that do have grounded recommendations. Stays hand-editable any time, unchanged.
- **Three separate interview rounds instead of one.** Rejected: `/grilling`'s existing fallback precedent
  (`skills/refactor-design/references/grilling-fallback.md`) already asks a whole frontier of questions in
  one round; no reason for this interview to be less efficient with the human's attention.

## Consequences

`loop-config` becomes the one tooling-tree node whose MR scope is a procedure rather than the tree doc's
usual fixed Purpose/Fulfilment-check/MR-scope text (`skills/refactor-scan/references/tooling-tree.md`,
`skills/refactor-design/SKILL.md` step 1's new exception). `refactor-implement` sets `Create-mode` (and,
when the interview chose a local tracker, creates `docs/agents/issue-tracker.md`) in the same merge request
that creates `config.md` — `refactor-learn`'s own `Create-mode`-writing bullet narrows to a fallback for a
`config.md` that predates this convention, rather than the primary path ADR-0006 described.

An unattended run (no human to answer `AskUserQuestion` or its prose fallback — e.g. a scripted dry run)
still proceeds: every recommended answer is taken as *proposed, not decided*, recorded the same way, but
flagged in the candidate issue and the pass's closing report as unconfirmed, first thing to double-check.

Known loose end, not resolved here: an independent, unmerged branch
(`fix/subagent-reference-and-tracker-discovery`) already added similar but differently-worded text ("check
`docs/agents/issue-tracker.md` first, if it exists") to some of the same call sites this decision touches.
That branch assumed the file only *might* exist; this decision makes it exist reliably after `loop-config`'s
first pass. The two branches need manual reconciliation (merge order or rebase) whenever both land — not
addressed by this ADR.

As with ADR-0011/ADR-0012, this is maintainer-facing paper trail only — no skill cites it by number; the
rule is stated inline, in plain prose, in the affected skills.
