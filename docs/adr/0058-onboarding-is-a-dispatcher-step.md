# Onboarding is step 0 of the dispatcher, and the `loop-config` node becomes `onboarding-setup`

> Amended by [ADR-0064](0064-bookkeeping-state-lives-in-an-issue-or-a-local-file.md): onboarding is triggered by a missing Bookkeeping pointer rather than a missing `bookkeeping.md`.

> Supersedes in part [ADR-0024](0024-loop-config-interview-decides-tracker-create-mode-storage.md) and
> [ADR-0057](0057-refactor-loop-and-per-track-skills.md): the interview ADR-0024 introduced stays, but is
> now the dispatcher's own step 0 rather than the design step of a `loop-config` candidate; the dispatcher
> ADR-0057 shrank to "Track selection and dispatch only" now also onboards. Amends
> [ADR-0025](0025-agents-md-gets-a-create-mode-pointer-not-the-value.md): the pointer section in
> `AGENTS.md`/`CLAUDE.md` now also records the backlog labels. The `loop-config`-specific exceptions and
> preconditions in ADR-0011, -0028, -0029 and -0047 no longer exist (onboarding has no candidate branch), but
> the decisions of those ADRs otherwise still hold.
> [ADR-0054](0054-onboarding-safety-net-and-signal-wave.md)'s **Onboarding** phase stands; this ADR only
> changes how its first step is carried out.

A maintainer running `/continuous-refactoring` in a project that had never used the suite saw the Safety Net
Track selected and "Starting a fresh scan in a subagent" — with nothing to say this was onboarding. The
config interview only happened after a scan subagent and a prioritise step whose entire conclusion was
"`loop-config` is the only proposal". The maintainer expected onboarding to start first, and aborted. On top
of that, one-time setup went through the whole scan → prioritise → design → implement → learn pipeline, filed
an issue and opened a merge request, and never told the maintainer that the engineering-skills setup
(issue-tracker file, triage-label table) it silently relies on could be missing.

## Considered Options

- **Only reword the announcement** ("Starting onboarding…"). Rejected — it leaves the pointless scan
  subagent and prioritise step in front of the interview, and still files an issue and a merge request for
  one-time setup.
- **A skip-scan path inside `refactor-loop`** (detect the missing `bookkeeping.md`, jump straight to design).
  Rejected — still a full pass for one-time setup: a candidate issue, a plan, an implement branch, a merge
  request, and a Track-agnostic skill that would need to branch on "onboarding or not".
- **A separate internal onboarding skill** dispatched by `continuous-refactoring`. Rejected — a new skill
  surface (trigger controls, validator entries, a description to keep honest) for what is one short,
  interactive step the dispatcher can own; the interview reference already exists and simply changes owner.
- **Creating the two backlog labels on GitHub/GitLab during onboarding.** Rejected — setup should never act
  outside the repo without the human; the engineering skills don't create labels on the forge either (they
  record the role-to-string mapping and apply labels with bare CLI calls). Labels are recorded in files and
  shown in the summary instead.
- **Requiring the engineering-skills setup before onboarding.** Rejected — the suite has to keep working
  without it. A one-time abort-or-continue question replaces the requirement.

## Decision

- **Step 0 of `continuous-refactoring`, before Track selection.** Fires on every invocation whose Refactoring
  Notes have no `bookkeeping.md`, including one that names a Track. It announces onboarding, runs the
  interview **inline** (never in a subagent), writes the files and **ends the invocation**: no Track
  selection, no dispatch, no scan, no issue, no merge request, no branch, no forge action. The closing text
  tells the human to commit the files to the default branch (candidate branches base on it) and to run
  `/continuous-refactoring` again, optionally naming a Track.
- **Interview flow.** Explore (also the issue-tracker file, the triage-label table and the forge's existing
  labels) → only when the engineering-skills setup is incomplete, one up-front question (abort with nothing
  written, or continue) → tracker (skipped when the issue-tracker file exists), create-mode, Refactoring
  Notes location → an informational summary with no approval gate → the writes, one status line each →
  the closing text. **Setup is detected from the repo**: both `docs/agents/triage-labels.md` and
  `docs/agents/issue-tracker.md` exist, or it counts as incomplete. The setup-gap question is the only
  choice that can end onboarding without writing; the Refactoring Notes folder is a requirement, so the
  location question has no "don't store them" option.
- **Write order and resume.** The suite's section in `AGENTS.md`/`CLAUDE.md` is written first — the
  "onboarding started" marker, whose presence on a later run skips the setup-gap question — and
  `bookkeeping.md` last, the "onboarding complete" marker. Partial state from an interrupted run is
  recognised, confirmed in the summary and completed without re-asking what is on record; nothing is
  overwritten silently. (`Create-mode`, whose only home is
  `bookkeeping.md`, is the one answer an interruption can lose.)
- **Labels.** Recorded only in files. With the setup present: `refactor:candidate`/`refactor:priority` in the
  `AGENTS.md`/`CLAUDE.md` section, plus a `done` row appended to the label table on a Local Markdown tracker.
  Without it: onboarding writes a minimal label table (compatible with the engineering skills', so their
  setup updates it in place) and the issue-tracker file. `done` is a label only on a Local Markdown tracker —
  on GitHub/GitLab a closed issue is done, and no path of the suite applies a `done` label there.
- **Missing labels on the forge.** GitLab's API creates a project label when an issue is filed with one that
  doesn't exist; GitHub does not — `gh issue create --label` fails for a missing label — so the GitHub
  closing text always lists both ready-to-copy `gh label create` commands. GitLab needs no instruction
  (verified against the API documentation only, not the `glab` client).
- **Internal skills abort without notes.** `refactor-loop` (next to its Track check) and
  `continuous-housekeeping` (which doesn't go through the loop) stop and point at `/continuous-refactoring`
  when there is no `bookkeeping.md`. The scan's cold-start precondition is removed — a second abort there
  would be unreachable.
- **No human present.** Recommended answers are recorded as proposed, not decided, and flagged in the closing
  text; the setup-gap question defaults to continue.
- **Rename.** The tooling-tree node `loop-config` (Name "Refactoring Config") becomes `onboarding-setup`
  (Name "Onboarding Setup"), the interview reference `onboarding-setup-interview.md`. The node stays the tree's
  root prerequisite with the same required edges and the same Fulfilment check (`bookkeeping.md` exists); it
  is simply never proposed any more, because the dispatcher fulfils it first. The parser is untouched apart
  from slugs. Historical ADRs, tickets and changelog entries keep the old name; the slug only ever appeared
  in the ignored, retired "Fulfilled nodes" list of existing targets, so no migration is needed. A target
  with an open old-style `loop-config` candidate is not migrated.
- **PHP minimum-version line.** The exception that had the onboarding merge request contribute the
  `php-minimal-version` Housekeeping line moves nowhere: that node belongs to the Guardrails scope (the first
  Safety Net write never evaluates it), and the Housekeeping Track's own reconciliation already adds the line
  of any fulfilled node without a delivering merge request. The exception is dropped; such a target's line
  arrives with its first Housekeeping cycle.

## Consequences

- The first thing a new maintainer sees is that onboarding is starting; no scan subagent runs first.
- One-time setup no longer produces an issue, a branch or a merge request, and the `loop-config`-in-flight
  branch exceptions in design, implement, learn and the bookkeeping/merge-request references are gone.
- Onboarding is two invocations: the second one, after the files are committed, is the first ordinary pass.
  Nothing checks that the files were committed; forgetting it means candidate branches start without them.
- Onboarded repos are unaffected.
