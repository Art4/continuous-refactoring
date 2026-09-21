# 01: Onboarding as its own dispatcher step (and rename `loop-config` → `onboarding-setup`)

**What to build:** Running `/continuous-refactoring` on a target with no Refactoring Notes' `bookkeeping.md` currently
selects Safety Net, announces "Starting a fresh scan in a subagent" and only reaches the config interview after scan →
prioritise → design. The human sees no hint that this is onboarding and aborts. Make onboarding its own **step 0 of the
dispatcher**: it asks the interview questions, writes the files, tells the human what was done, suggests committing them,
and ends the invocation — the next invocation starts the Safety Net scan. No issue, no merge request, no scan / prioritise /
design / implement / learn. Rename the tooling-tree node `loop-config` to `onboarding-setup` (Name "Onboarding Setup").

**Status:** done — PR pending

## Decided behaviour (grilled with the maintainer)

- **Gate.** Step 0 of `continuous-refactoring` fires whenever the Refactoring Notes' `bookkeeping.md` is missing — every
  invocation, including one that names a Track. It announces onboarding, runs the interview inline (no subagent), then
  **ends the invocation**: no Track selection, no dispatch, no chaining into a scan. The closing text tells the human to run
  `/continuous-refactoring` again (optionally naming a Track).
- **Internal skills.** `refactor-loop` (input validation, next to the Track check) and `continuous-housekeeping` (does not go
  through `refactor-loop`) abort when there is no `bookkeeping.md`, pointing at `/continuous-refactoring`. `refactor-scan`'s
  "no `bookkeeping.md` → propose `loop-config`" precondition is removed without replacement.
- **Interview flow.** Explore (also reads `docs/agents/issue-tracker.md`, `docs/agents/triage-labels.md`, queries the forge
  for existing labels) → **only when the engineering-skills setup is incomplete**, one up-front question: abort (nothing
  written, hint to run `setup-matt-pocock-skills`) or continue without it → Q1 tracker (skipped when `issue-tracker.md`
  exists), Q2 create-mode, Q3 Refactoring Notes location → informational summary (no approval gate) → write with one status
  line per write → closing.
- **Setup detection.** Both `docs/agents/triage-labels.md` and `docs/agents/issue-tracker.md` exist → set up; otherwise not.
- **Write order / resume.** `bookkeeping.md` is written **last** — it is the "onboarding complete" marker. Partial state
  (e.g. the pointer or `issue-tracker.md` already there) is recognised, not re-asked, confirmed in the summary, and only the
  missing parts are added. Nothing is overwritten silently.
- **No forge action.** Nothing is created on GitHub/GitLab. Labels are only recorded in files and shown in the summary:
  - Set up: `refactor:candidate` / `refactor:priority` recorded only in the `AGENTS.md`/`CLAUDE.md` section ("Backlog
    labels: …"). Local Markdown tracker and `triage-labels.md` lacks a `done` row → append it.
  - Not set up, continued: onboarding writes `triage-labels.md` (`needs-info`, `ready-for-agent`, `wontfix`; `done` only for
    a Local Markdown tracker; forge labels that exist under a different spelling become overrides in the right-hand column)
    plus `issue-tracker.md`. No `domain.md`.
  - `done` is not a label on GitHub/GitLab (closed = done). Verify no forge path of the suite applies `done` as a label.
  - GitHub closing text lists ready-to-copy `gh label create …` commands for the two `refactor:*` labels (GitLab: nothing
    needed — to be verified against the docs). The matt-pocock skills don't handle missing labels at all.
- **Closing text.** What was created; commit/merge the files to the default branch (candidate branches base on it; no active
  check); rerun `/continuous-refactoring`; when the setup was missing: it can be run later and updates the files.
- **No human present.** Recommended answers are recorded as *proposed, not decided* and flagged in the closing text; the
  "setup missing" question defaults to continue.
- **Tree node stays.** `onboarding-setup` remains the tooling-tree root prerequisite (Fulfilment check: `bookkeeping.md`
  exists locally); it is just never proposed any more because the dispatcher fulfils it first. `tooling_tree.py` logic and
  tests are untouched apart from slugs.
- **`php-minimal-version` exception.** The first Safety Net bookkeeping write (`refactor-learn`) contributes the
  `Housekeeping` line when the node is already fulfilled on first evaluation; if that doesn't fit cleanly, the exception is
  dropped with a note in `docs/known-limitations.md`.
- **Old candidates.** Targets with an open old-style `loop-config` candidate are not migrated (changelog note only).

## Tasks

- [x] **A. Rename** (first commit, purely mechanical): `git mv` `tooling-tree/loop-config.md` → `onboarding-setup.md` and
      `loop-config-interview.md` → `onboarding-setup-interview.md`; replace the slug everywhere except `docs/adr/00*.md`,
      `.scratch/**`, `CHANGELOG.md`, existing `.changelog.d/*`; display name "Refactoring Config" → "Onboarding Setup";
      slug seeds in `scripts/drift_check.py`, `test_tooling_tree.py`, `test_trigger_controls.py`; fixtures
      (`fulfilled-set.json`, ignored "Fulfilled nodes" lists), `fixtures/harness/run.sh`, `fixtures/README.md`.
- [x] **B. Dispatcher:** step 0 in `skills/continuous-refactoring/SKILL.md`; adapt intro, description, completion criterion.
- [x] **C. Interview reference:** owner = dispatcher; extended Explore; setup-gap question; Summarize (files + recorded labels,
      no issue/MR, no gate); Record executed directly, `bookkeeping.md` last, no `Pending candidates`; new Closing; "no human"
      case; `triage-labels.md` template reference compatible with the matt-pocock one.
- [x] **D. Clean up the loop:** aborts in `refactor-loop` / `continuous-housekeeping`; drop `refactor-scan` precondition;
      remove or rewrite the exceptions in `refactor-design`, `refactor-implement`, `refactor-learn`, `refactor-prioritize`,
      `opening-a-merge-request.md`, `local-issue-tracker-template.md`, `refactoring-bookkeeping.md`, `safety-net-track.md`,
      `tooling-tree.md`; rewrite `tooling-tree/onboarding-setup.md`; re-home the `php-minimal-version` line.
- [x] **E. Docs** (own words, no ADR/ticket numbers): README callout on the optional matt-pocock setup before "Quick start" +
      quick-start step 1; `docs/FAQ.md` ("Do I need the matt-pocock skills?", "Why two invocations?");
      `docs/known-limitations.md`; `docs/architecture.md`; `docs/playbooks/loop.md`, `tracks.md`; `CONTEXT.md`
      (**Onboarding**, **Tooling tree**); new ADR recording the decision, the rename and the rejected alternatives; changelog
      fragment `.changelog.d/onboarding-as-dispatcher-step.md`.
- [x] **F. Fixtures/harness:** `fixtures/harness/run.sh` interview references; fixtures without `bookkeeping.md` expect the
      onboarding stop instead of a `loop-config` proposal.
- [ ] Before every push: `python3 -m unittest discover -s scripts -p 'test_*.py'` and
      `python3 scripts/validate_skills.py .` green; fixture/parser changes also need the relevant
      `scripts/run-test.sh` / `fixtures/harness/run.sh` tier.

## Verification

1. Unit tests + validator green.
2. Dry run in an empty repo: first output is the onboarding announcement, no scan subagent; questions one at a time;
   files exist afterwards, no issue/MR/branch; closing text with commit + rerun hint. Variants: set up, not set up +
   continue, not set up + abort (nothing written), interrupted mid-write (resume without re-asking).
3. Second invocation selects Safety Net and starts the scan subagent normally.
4. Direct `/continuous-safety-net` and `/continuous-housekeeping` without notes abort with a pointer.

## Comments

### 2026-09-21 — Spec (`/to-spec`, synthesised from the grilling session; `Status: ready-for-agent`)

#### Problem Statement

A maintainer runs `/continuous-refactoring` in a project that has never used the suite. The pass detects that there is no
Refactoring Notes' `bookkeeping.md`, picks the Safety Net **Track**, and announces "Starting a fresh scan in a subagent".
Nothing tells the maintainer this is **Onboarding**; the config interview only happens after a scan subagent and a
prioritise step that can conclude nothing but "`loop-config` is the only proposal". The maintainer expects onboarding to
start first, and aborts. On top of that, onboarding pushes a config change through the whole scan → prioritise → design →
implement → learn pipeline, files an issue and opens a merge request for what is really one-time setup, and never tells
the maintainer that the engineering-skills setup (issue-tracker config, triage labels) it silently relies on may be missing.

#### Solution

Onboarding becomes its own first step of the dispatcher. When the Refactoring Notes' `bookkeeping.md` is missing, the
dispatcher says so, runs a short interview (tracker, merge-request create-mode, Refactoring Notes location — plus a
one-time "setup incomplete: abort or continue?" question when the engineering-skills setup is missing), shows a summary,
writes the files, tells the maintainer what it did, recommends committing them, and ends. The next `/continuous-refactoring`
(optionally naming a Track) starts the first Safety Net scan. Nothing is created on the forge, no issue is filed, no merge
request is opened. The tooling-tree node formerly called `loop-config` is renamed `onboarding-setup` ("Onboarding Setup")
and stays as the tree's root prerequisite, fulfilled by the dispatcher before any scan.

#### User Stories

1. As a maintainer running the suite for the first time, I want the very first output to say that onboarding is starting, so
   that I understand what is happening instead of watching a scan subagent spin up.
2. As a maintainer, I want no subagent, scan, prioritise or design step to run before the interview, so that onboarding
   starts immediately.
3. As a maintainer, I want to be asked the tracker, merge-request mode and notes-location questions one at a time, each with
   a recommended answer derived from what the repo already shows, so that I can accept sensible defaults in a word.
4. As a maintainer whose repo already has an issue-tracker file, I want the tracker question skipped, so that I am not asked
   something the repo already answers.
5. As a maintainer, I want a plain-prose summary of what will be written (files, recorded labels) before anything is
   written, so that nothing surprises me.
6. As a maintainer, I want one short status line per file written, so that I can follow what the onboarding does.
7. As a maintainer, I want the onboarding to end after writing — no issue, no merge request, no branch — so that one-time
   setup does not masquerade as refactoring work.
8. As a maintainer, I want the closing text to recommend committing or merging the new files to the default branch, so that
   later candidate branches contain the Refactoring Notes.
9. As a maintainer, I want the closing text to tell me to run `/continuous-refactoring` again (optionally naming a Track),
   so that I know what starts the first scan.
10. As a maintainer who names a Track on a repo that was never onboarded, I want onboarding to run first anyway, so that no
    Track runs without Refactoring Notes.
11. As a maintainer whose repo has the engineering-skills setup (both `triage-labels.md` and `issue-tracker.md`), I want the
    onboarding to reuse it and only add what the suite itself needs, so that nothing I already configured is overwritten.
12. As a maintainer whose repo lacks that setup, I want to be offered the choice to abort and install it first, so that I can
    use the recommended tooling.
13. As a maintainer who aborts at that point, I want nothing written and the next invocation to start the onboarding from
    scratch, so that no half-configured state remains.
14. As a maintainer who continues without the setup, I want the onboarding to write minimal equivalents (issue-tracker file,
    triage-label table) itself, so that the suite works without extra tools.
15. As a maintainer who later installs the engineering-skills setup, I want its run to update those files in place, so that
    nothing is lost.
16. As a maintainer on GitHub or GitLab, I want no label created on the forge by the onboarding, so that setup never acts
    outside my repo without me.
17. As a maintainer on GitHub, I want the closing text to give me copy-pasteable commands for the two `refactor:*` labels, so
    that the first pass does not fail on a missing label.
18. As a maintainer on GitLab, I want no label instructions I don't need, so that the closing text stays short.
19. As a maintainer with labels that already exist under a different spelling, I want them recorded as overrides in the label
    table, so that the suite uses my vocabulary instead of duplicating labels.
20. As a maintainer using a Local Markdown tracker, I want a `done` row in the label table, and as a maintainer on a forge I
    want none, because a closed issue there is done.
21. As a maintainer, I want the `refactor:candidate` / `refactor:priority` labels recorded in the suite's own section of my
    `AGENTS.md`/`CLAUDE.md`, so that the backlog vocabulary is written down once.
22. As a maintainer whose onboarding was interrupted mid-write, I want the next run to recognise the partial state, not re-ask
    what is on record, and add only what is missing, so that I am not interviewed twice.
23. As a maintainer, I want `bookkeeping.md` written last, so that its existence reliably means "onboarding completed".
24. As a maintainer, I want no file overwritten silently, so that my own edits survive.
25. As a maintainer running unattended (no human to ask), I want every recommended answer recorded as "proposed, not decided"
    and flagged in the closing text, so that I can double-check it later.
26. As a maintainer who invokes `/continuous-safety-net` or `/continuous-housekeeping` directly on an un-onboarded repo, I want
    a clear abort that points at `/continuous-refactoring`, so that I am not left with a confusing failure.
27. As a maintainer, I want the second `/continuous-refactoring` on the same repo to select a Track and start the scan
    subagent normally, so that onboarding never slows down later passes.
28. As a maintainer of an already-onboarded repo, I want nothing to change for me, so that the upgrade is invisible.
29. As a skill author reading the tooling tree, I want the root node named for what it is (Onboarding Setup), so that the name
    matches the dispatcher step that fulfils it.
30. As a reader of the README, I want the optional engineering-skills setup called out before "Quick start", so that I know
    what it gives me and that the suite works without it.
31. As a reader of the docs, I want the FAQ to answer "Do I need the matt-pocock skills?" and "Why two invocations?", so that
    I don't have to read skill text.
32. As a PHP-project maintainer, I want the `Housekeeping` line for an already-satisfied PHP minimum version still recorded,
    so that the target does not permanently miss it just because the floor was sufficient from day one.

#### Implementation Decisions

- **Dispatcher gains a step 0, Onboarding, ahead of Track selection.** It fires on every invocation whose Refactoring Notes
  have no `bookkeeping.md` — including manual Track overrides — announces itself in one sentence, runs the interview inline
  (never in a subagent), and ends the invocation. The dispatcher's stated purpose widens from "decides only which Track" to
  "first onboards an un-onboarded target, otherwise decides which Track".
- **The interview reference is retained and reworked**, its owner changing from the design step to the dispatcher. Parts:
  Explore, an optional setup-gap question, Ask (Q1 tracker, Q2 create-mode, Q3 notes location), Summarize, Record, Closing.
  The summary is informational only; there is no approval gate. The only abort point is the setup-gap question.
- **Setup detection is repo-based:** both the triage-label table and the issue-tracker file exist → set up. Partial → not set
  up. Machine-level skill installation is not consulted.
- **Explore additionally reads** the issue-tracker file, the triage-label table, and the forge's existing labels (via the
  forge CLI when reachable; failure only softens the summary, it never blocks).
- **Record writes directly** (no plan handed to the implement step): the Refactoring Notes' `bookkeeping.md` (create-mode,
  optional focus areas, no pending candidate), the issue-tracker file when absent, the label table when the setup is missing
  (or a `done` row appended for a Local Markdown tracker when it is missing), and the suite's pointer section in the
  existing `AGENTS.md`/`CLAUDE.md` (create `AGENTS.md` only when neither exists), now including both backlog labels.
  `bookkeeping.md` is written last as the completion marker; partial state is detected, confirmed in the summary, and
  completed without re-asking.
- **No forge action, no approval gate for labels.** Labels are recorded in files and shown in the summary. GitHub closing text
  lists the two label-creation commands; GitLab needs none (to be verified against the CLI/API documentation before the text
  is written). The suite must not apply a `done` label on a forge tracker.
- **Files written to a target repo cite no suite-internal skill paths** (forge-facing / target-facing text stays
  self-contained).
- **Internal skills abort on missing notes:** the loop-running skill validates it next to the Track input; the Housekeeping
  skill, which does not use the loop, does the same. The scan step's cold-start precondition is removed; a second abort there
  would be unreachable.
- **Tree node renamed** `loop-config` → `onboarding-setup` (Name "Onboarding Setup"), remaining the root prerequisite with the
  same required edges; its Fulfilment check is unchanged (`bookkeeping.md` exists locally); its scope text now says the
  dispatcher's onboarding step fulfils it and it is never proposed as a candidate. Historical ADRs, tickets and changelog
  entries keep the old name; a new ADR records the rename and the decision. Existing targets need no migration (the slug
  only ever appears in the ignored, retired "Fulfilled nodes" list).
- **Every place that described the old flow is reworded:** design/implement/learn/prioritize exceptions for the old node,
  bookkeeping reference, merge-request opening reference, local-tracker template reference, Safety Net Track reference,
  tooling-tree references, PHP minimum-version node.
- **PHP minimum-version exception** moves from the retired onboarding merge request to the first Safety Net bookkeeping write;
  if that does not fit cleanly it is dropped and recorded in the known-limitations page.
- **Docs kept true in the same change:** README (callout before "Quick start", quick-start step 1), FAQ, known limitations,
  architecture overview, loop and Track playbooks, `CONTEXT.md` (**Onboarding**, **Tooling tree**), plus a new ADR and a
  changelog fragment. README and `docs/**` cite no ADR numbers, ticket numbers or `.scratch/` paths.
- **Old-style candidates** already open in a target are not migrated.

#### Testing Decisions

- **Seams (proposed — highest existing seams, no new one):**
  1. The **fixture harness** (`fixtures/harness`, per-fixture `expected/behavior.md`) — external behavior of a whole
     invocation: a fixture without `bookkeeping.md` must end after onboarding, must not spawn a scan, must write the files in
     the documented order; set-up and not-set-up variants; an interrupted-write variant; a second invocation that selects a
     Track.
  2. The **tooling-tree parser tests** (`scripts/test_tooling_tree.py`, `drift_check.py`, `test_trigger_controls.py`) — the
     renamed root node keeps the same graph behaviour (unblocking of its children, fulfilment by `bookkeeping.md`).
  3. The **skill validator** (`scripts/validate_skills.py`) — every rewritten reference still resolves, no dangling links to the
     renamed files, frontmatter intact.
  Please confirm these three match your expectations; the implementer should not add seams.
- **A good test** asserts only externally observable behavior: what the invocation says and writes, the files that exist
  afterwards, that no issue/branch/merge request/forge call appears, which skill runs next — never the wording of skill
  prose beyond the required announcement and closing content.
- **Existing tests must stay green after a slug-only change**; the rename is verified by them, not by new tests.
- **Prior art:** the existing first-run fixtures (`php-safety-net-first-run`, `php-scheduler-bootstrap-*`) and the harness
  tiers in `fixtures/README.md`; tests are written first (tdd) at those seams where a seam can express the behavior.

#### Out of Scope

- Creating labels on GitHub/GitLab from the onboarding (explicitly rejected), and ensuring labels at filing time.
- An active check that the onboarding files are committed before the next run.
- A migration path or detection for target repos with an old-style onboarding candidate/branch/issue.
- Writing `domain.md`, asking about `Focus areas` or `Refactoring goal`, or any change to the Safety Net / Guardrails /
  Investigation / Housekeeping Track logic beyond the re-homed PHP line.
- Removing the tooling-tree root node, or renaming historical ADRs, tickets or changelog entries.
- Changing how the matt-pocock setup skills work.

#### Further Notes

- Rejected alternatives (for the ADR): only rewording the announcement (leaves the pointless scan subagent); a skip-scan path
  inside the loop skill (still a full pass for one-time setup); a separate internal onboarding skill (new skill surface,
  trigger controls, validator entries for no gain).
- The matt-pocock skills never create labels on the forge either: they only record the role → string mapping and apply labels
  with bare CLI calls. The suite's behavior is therefore not worse than that convention, and the closing text is better.
- Work on branch `feat/onboarding-setup-dispatcher-step`; the rename is its own first commit. Before every push run the
  unit tests and the validator; fixture/parser changes also need the relevant harness tier. Deliver through a pull request,
  never a direct commit to `main`.

### 2026-09-21 — Implementation notes (branch `feat/onboarding-setup-dispatcher-step`, PR pending)

**Open items, as resolved**

1. **Missing labels on the forge.** GitLab: the official REST API docs for creating an issue say "If a label does
   not already exist, this creates a new project label and assigns it to the issue" — verified for the API only,
   not for the `glab` client. GitHub: the official `gh issue create` manual only says `--label` "Add labels by
   name" and is silent on missing labels; the failure ("could not add label: … not found") is documented only in
   community sources (community discussion #35377, cli/cli #3284). So the GitHub closing text always lists both
   `gh label create "<name>" --description "…" --force` commands (`--force` is in the official `gh label create`
   manual); GitLab and Local Markdown get no instruction.
2. **`done` label.** No forge path of the suite applies a `done` label. The one ambiguity was `refactor-learn`'s
   "mark `done`", now worded as: on GitHub/GitLab closing the issue is done, never a `done` label; `done` is a label
   only on a Local Markdown tracker.
3. **`php-minimal-version` Housekeeping line.** Dropped. The node is Guardrails-scoped, so the first Safety Net
   bookkeeping write never evaluates it, and the Housekeeping Track's own reconciliation already adds the line of
   any fulfilled node with no delivering merge request — it arrives with the first Housekeeping cycle. Recorded in
   the new ADR only (not in `docs/known-limitations.md`: internal behaviour, not something a user hits).

**Process.** `/implement` could not be invoked from the implementing subagent (the skill is user-invocation
only), so the tasks were implemented directly. Two `/code-review` rounds (Standards and Spec axes) ran against the
first implementation; the findings were fixed in follow-up commits: resume no longer re-asks the setup-gap question
(the suite's own `AGENTS.md`/`CLAUDE.md` section is written first as the "onboarding started" marker,
`bookkeeping.md` last); the setup gap is the only abort point (the Refactoring Notes are a requirement, Q3 only asks
where); the backlog-labels line dropped its "native tracker only" qualifier; label overrides are only recorded in
the not-set-up path; both `gh label create` commands are always listed; the missing fixtures were added (abort,
direct Track invocation, second invocation, one-file partial state); the triage-label table has one source
(`triage-labels-template.md`); the "not onboarded yet" abort text is defined once in `refactoring-bookkeeping.md`;
CONTEXT.md, the node doc and the ADR banners were tightened (superseded-in-part banners only on ADR-0024, -0025 and
-0057).

**Outstanding.** A live dry run of the onboarding (Verification 2–4) has not been done — every `php-onboarding-*`
fixture's `expected/behavior.md` is marked "not yet manually confirmed live". Unit tests, `drift_check`, the skill
validator and harness tier 2 are green.
