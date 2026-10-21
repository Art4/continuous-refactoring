# Changelog

All notable changes to this project are documented here. Format inspired by
[Keep a Changelog](https://keepachangelog.com/), kept flat (no `Added`/`Changed`/`Fixed`
subcategories) — see `CONTRIBUTING.md`'s "Changelog" section for how entries are produced.

## [0.9.0] - 2026-10-21

- The tooling tree is now Roles, Tools and Stages delivered in Packs: a project on Psalm is no longer offered PHPStan, a project that is not PHP can have a fulfilled Safety Net from the language-neutral tools, a rejection can name a whole tool or role, and a tool the suite learns about later is picked up on the next run.
- The tools the suite knows are now drawn for humans: `docs/tooling/` lists the Roles and, per Pack, the Tools and Stages with a diagram of what requires what. The pages are generated from the Packs, and the validator now fails on a Pack that breaks its schema, is not in the fixed form, has two recommended tools for one Role, names a missing details file, or whose page is out of date.
- The prose for a tool now sits beside its Pack: the generic Pack's tools, the suite's two prerequisites and the smaller PHP tools moved to `packs/<pack>/<tool>.md`, without the history of how they used to be wired. The PHP Pack also knows Laravel Pint and Easy Coding Standard now: a project on either has its code style settled, and PHP CS Fixer is not proposed to it.
- The last tool files (PHPStan, Psalm, Rector) moved into the PHP Pack and lost the description of how the tools used to be wired; the two tooling-tree documents are gone. Every tool now has one file beside its Pack, and the Pack pages under `docs/tooling/` link to it.
- A project can keep a Pack of its own for tools the suite does not know: a `pack.json` and a file per tool, named in a new optional **Tooling Pack** operation of its tracker file. Its steps are proposed like the suite's own; it can add tools, steps and roles, never redefine the suite's, and a clash ends the run's tooling step with an error that names both places. A Pack now names a scope (PHP, Twig, …): tools take each other's place only within a scope, so a code-style tool for Twig no longer competes with one for PHP. See the new playbook on adding a tool of your own.
- A new Pack for Twig in PHP projects: it applies when the PHP project requires `twig/twig` (the file extension of the templates does not decide) and brings Twig-CS-Fixer for the Code Style of the templates and TwigStan for their Static Analysis. Both stand beside the PHP Tools and do not take their place.
- PHP_CodeSniffer is now a recognized Tool for the Role Code Style: a target that runs `phpcs`/`phpcbf` has the Role filled, so PHP CS Fixer is no longer proposed on top of it.
- The PHP Pack Stage "PHP Minimum Version" is now called "PHP Version Floor", matching its Role Runtime Floor and the terms Floor correction and Floor raise; its slug `php-minimal-version` is unchanged.
- Psalm Taint Analysis is now a Guardrails Stage instead of a Safety Net one: its findings can need a restructuring to fix, and that restructuring waits for the Safety Net, so the Stage no longer holds the Safety Net back and no longer has to be skipped to pass it.
- Twig-CS-Fixer is now a Guardrails Stage instead of a Safety Net one: a style pass over Twig templates no longer holds the Safety Net, and with it every PHP Guardrails Stage, back. TwigStan still waits for it.
- In the PHP Pack diagram, the Static Analysis Role now sits inside the Safety Net group instead of outside it.
- PHP CS Fixer now comes in two Stages, so a project with thousands of files gets its code style in merge requests a person can review. The adoption (`php-cs-fixer-adoption`, renamed from `php-cs-fixer`) pins a PER Coding Style version, proposes a list of extra rules you may decline, checks the project's lowest PHP version, and takes in as many rules as one merge request can carry; it alone releases Rector. The new Guardrails Stage `php-cs-fixer-rollout` takes in the rules left `Not yet:` one at a time, path by path, through a second config file, as the ticket "PHP CS Fixer: take in the remaining rules". A Housekeeping line looks for a newer PER Coding Style version.
- PHPMD no longer starts with a baseline: the limits of its metric rules are set to the worst value the code has today, with a comment, and fall whenever a refactoring removes that worst value. Deliberate exceptions are suppressed at the code with a reason, the five rule sets (now with `design`) are the default, and a project that already has a PHPMD baseline gets one merge request that replaces it.
- PHPMD now comes in two Stages, like PHP CS Fixer. The adoption (`phpmd-adoption`, renamed from `phpmd`) installs the tool, sets the limits, takes in the rules one merge request can carry and adds the CI job; rules left `Not yet:` no longer keep it unfulfilled. The new Guardrails Stage `phpmd-rollout` takes in those rules one at a time, as the ticket "PHPMD: take in the remaining rules". A rule too large for one merge request is taken in directory by directory through a second ruleset, `phpmd.rollout.xml`, which CI runs over the directories already done, so they cannot slip back before the rule is in everywhere.
- A Stage's `after` may now name a Role as well as a Stage. The Rector Stages wait for the Role Code Style instead of PHP CS Fixer's adoption, so the tooling diagram shows PHP CS Fixer, Laravel Pint, Easy Coding Standard and PHP_CodeSniffer feeding one Code Style node that Rector waits on. When Rector is released does not change: a Role counts as decided once it is filled, or once every Tool that could fill it is decided. A target's own Pack can use the same form.
- The suite no longer names one agent's question tool: it asks for the environment's multiple-choice question tool (Claude Code, Cursor and OpenCode each have one under a different name) and falls back to numbered options in chat when there is none, so questions are shown in Cursor and OpenCode too. A tool reply that no human gave counts as unanswered.
- A new optional operation, **Ready after plan**, lets a target mark a ticket ready for implementation (for example a label or a board column) right after the suite posts a plan on it. Without the bullet nothing changes.

## [0.8.0] - 2026-10-17

- A structural refactoring ticket now starts with a Pinning Test — a test that holds today's behaviour and passes before any restructuring — which the plan names, the review checks, and the merge request reports; where none can be written at a reasonable cost, the run asks instead of restructuring unchecked.
- For a restructuring that reaches over several steps behind one edge, the plan can pin the behaviour with a script that runs the old and the new code on the project's own sample inputs and compares the outputs; the merge request says on how many inputs they agreed.
- A structural refactoring now has to make the code easier to follow: the review takes off any change that lowers the reader's effort nowhere, and the run ends without a merge request when none is left. Judgement aids — reader load, the Strangler Fig, the technique vocabulary — now live in their own principles reference, apart from the few binding rules.
- Plans now tell apart an API someone outside depends on (replaced piece by piece, old and new side by side) from an internal one (all callers moved and the old API deleted in one step), remove dead code before reshaping, and every rename is searched for across strings, docs and configuration.
- When a restructuring renames, moves or deletes something that can be referred to from outside the tested interface, the merge request now states the one fact the change is safe because of and how far it was proved — or that it is not proved.
- A plan for a tooling ticket now estimates how big its merge request would be and, where a person could not review it, is cut into parts at a seam of kind or risk, each worth merging alone.
- The suite's own review now sorts its findings into fix, note and dismiss: what the plan cannot fix is named in the merge request, a dismissal carries its reason in the closing report, and a finding against the plan is never dismissed.
- When a run works a ticket that already has a merge request, it now sorts the review comments instead of fixing all of them: a bot's comment is checked and then fixed, dismissed with a reason, or asked about (security, data and permissions are always asked); a person's comment is fixed or answered, never dismissed; each handled comment gets a short reply, and threads are left for the reviewer to resolve.
- A run now stops when the same failing check or review finding survives two fix attempts: the branch stays local, the ticket gets an open question in plain words, and no check is deleted, loosened or ignored to get green.
- The design now settles a question about behaviour, output or timing by running something harmless instead of asking you, and a run's closing report opens with how many things wait for you and says what is recommended and what happens if you do not answer.
- A PHPStan baseline ticket's merge request may now add a new baseline entry as long as the baseline gets shorter overall, and names it; a finding to ignore for good, or a baseline that would not get shorter, becomes an ignore rule in `phpstan.neon` only after the human allows it.
- Contributors are told to turn a rule that is broken twice into a check, and the validator now checks that README and docs cite no ADR or PR numbers and no scratch files.

## [0.7.0] - 2026-10-14

- **Breaking, for 0.7.0:** the suite is rebuilt around one **run** of decision points, with all state in your tracker and forge. `/continuous-refactoring` now leads from your open refactoring tickets to one opened merge request and, at every step — reconcile, Track choice, scan, filing tickets, selecting, design, implementation, merge request — shows what it found, the options and one recommendation. By default you decide each time; say in the call that it should do the run itself ("do it yourself"), or mid-run "carry on yourself from here", and it takes its own recommendations. The call also takes a Track, a ticket or a restriction ("only the Rector tools") in your own words. The suite keeps no state of its own any more: the config file, the bookkeeping document (local and remote), `Ticket-create-mode`, `MR-create-mode` and the Track cadences are gone, and so are the limits of two open merge requests and five open candidates. Tickets are found by their subject instead of a fixed label or title, a ticket you wrote yourself is picked up through a **Candidate** mark or by naming it, and a Track is scanned once — afterwards its tickets are the record. Where your project has its own skills for planning and implementing, a run recommends those and uses the suite's procedures as a fallback. Housekeeping is now one standing ticket made from a template in your repository, with a rhythm you choose, refactoring ideas left on it as comments, and its own command `/continuous-housekeeping` that can be scheduled and that an agent may start by itself. The suite is two skills, `continuous-refactoring` and `continuous-housekeeping`; the nine others are removed. The operations in `docs/agents/issue-tracker.md` change their cut: **Search** is new and required; **Rejected**, **Blocked by** and **Housekeeping** are new and optional; **Bookkeeping**, **Filed date** and **Comment author and time** are removed.

  **A project onboarded on 0.6.0 needs three steps.** (1) Run the onboarding again: call `/continuous-refactoring`, which adds **Search** to your `## Refactoring operations` section and removes the bullets that no longer exist. (2) Delete the suite's old files under `.scratch/refactor/` — `config.md`, `bookkeeping.md`, `merge-requests.md` and the folder `out-of-scope/`; they are no longer read. Tickets kept as local Markdown files under `.scratch/refactor/issues/` stay. To keep your old rejections where they are instead of deleting them, name that folder under **Rejected** in the section (a rejection that should come back by itself once a PHP version is reached needs a line `Blocker: PHP >= X.Y`). Where the bookkeeping lived in a tracker issue, close that issue. (3) Remove the symlinks of the removed skills from your skills folder: `refactor-loop`, `refactor-scan`, `refactor-prioritize`, `refactor-design`, `refactor-implement`, `refactor-learn`, `continuous-safety-net`, `continuous-guardrails`, `continuous-investigation`. Nothing is migrated; the first scan of each Track rebuilds the worklist as tickets.
- The Housekeeping ticket's date line, template line and title are described by what they hold, not by a fixed wording: the onboarding words the Housekeeping bullet itself, and later runs read the due date and the template from the ticket in whatever words it states them.
- The suite no longer sets or reads the triage labels `needs-info` and `ready-for-agent`. Whether a ticket waits for an answer or is ready to work is read from its comments, so it works in a tracker without them. It stays compatible with other engineering skills, such as those of mattpocock/skills, and needs none of them.
- The onboarding now ends the run. Instead of offering to go on in the same call, `/continuous-refactoring` reports the onboarding as complete, points out the changes it left in the working tree (the tracker file) and recommends committing them and calling the skill again.
- The onboarding now tries its search and merge-request commands before it shows you the summary, not after writing the tracker file. When one fails, for example because your installed `glab` or `gh` is older, the onboarding asks about a working variant at that point, so the summary you confirm already contains commands that work and no second confirmation follows after writing. A run on its own takes a working variant it found itself; without one, it writes nothing and names the open question.

## [0.6.0] - 2026-10-10

- **Breaking:** the suite's state no longer lives in a committed `docs/refactoring/` folder. Your
  create-modes (`Ticket-create-mode`, `MR-create-mode`) and the pointer to the bookkeeping now sit
  in `.scratch/refactor/config.md`, and by default the bookkeeping itself in
  `.scratch/refactor/bookkeeping.md` — files the suite writes but never commits, branches or opens a
  merge request for (whether they go into Git, and how they reach another machine, is up to you).
  Focus areas and refactoring goal are now two lines you add to `AGENTS.md`. A create-mode the
  config doesn't state reads as the safe value (`ask-each-time`, `human-opens`), and candidate merge
  requests are no longer opened as drafts. An existing project runs the onboarding again: it moves
  the state from `docs/refactoring/` into the new layout and, after you confirm, removes the old
  files. The Housekeeping checklist stays at `docs/refactoring/housekeeping-template.md`.
- The suite now works with any issue tracker that `docs/agents/issue-tracker.md` describes, not only
  GitHub, GitLab and local Markdown files. Skills read a handful of named operations from a new `##
  Refactoring operations` section in that file instead of deciding by the tracker's name, and
  tickets and merge requests may live in different systems (for example Redmine tickets with GitLab
  merge requests). Onboarding offers a tracker the file already describes as its own answer, lets
  you describe another one in the interview, and no longer falls back to local files silently. **A
  project onboarded earlier needs the new section:** `/continuous-refactoring` stops with a message
  until the onboarding has been run again, which adds it. The suite no longer prescribes `Closes
  #<n>` itself — the GitHub and GitLab templates carry it.
- New: **remote bookkeeping**. Instead of local files, the bookkeeping can live in a tracker issue
  or anywhere else your project describes, and any machine with access to it picks the state up
  without a commit. The suite fetches the bookkeeping before a pass and stores it after every write;
  where it lives and how that is done is written in your project, as a **Bookkeeping** entry under
  `## Refactoring operations` in `docs/agents/issue-tracker.md`. The GitHub and GitLab templates
  bring that entry: an issue whose body is the bookkeeping, with learned rejections as comments on
  it. Onboarding offers to create such an issue, to adopt an existing one, or "as this project
  describes it", for which it proposes a description from your project's own files. The last write
  wins; bookkeeping that can't be fetched stops the pass and is never replaced on its own.
- A Safety Net or Guardrails pass no longer picks up structural candidates: an issue labelled
  `refactor:candidate` that isn't a tooling-tree node's is now worked only in an Investigation pass,
  and the closing report says how many are waiting. Candidates you label `refactor:priority` are
  still taken by any pass.
- The bookkeeping document's top-level `Pending candidates` field is gone: every candidate in flight
  is now tracked in its own Track's `Open` list. `## Investigation` gains an `Open` field for that,
  the same shape Safety Net's and Guardrails' already use, holding one entry per in-flight candidate
  of its own (structural, PHPStan baseline-shrink, or externally-labeled) — up to two, as the
  suite-wide two-merge-request cap allows. `refactor-design` appends the entry, `refactor-learn`
  removes only the one for the candidate that resolves, and `refactor-design` writes no bookkeeping
  for a tooling-tree node. `refactor-scan` resumes from the selected Track's `Open` alone, so an
  Investigation candidate is resumed only during an Investigation pass, never mid a Safety Net or
  Guardrails one. An existing document that still carries `Pending candidates` needs no change — the
  line is ignored. One edge changes: on a tracker without native labels, a hand-filed `Tooling tree:
  <Name>` issue interrupted between design and implementation is ranked again on the next pass
  instead of being resumed unconditionally.
- A flagged candidate (`needs-info`) now self-confirms when a human's newest comment on the issue
  plainly agrees with the stated default: the suite swaps the labels itself instead of waiting for
  you to also flip `needs-info`/`ready-for-agent` by hand. A comment proposing something else, or
  raising a further question, still leaves it flagged — the suite nudges once instead of skipping
  silently forever, but never applies an alternative on its own.
- `refactor-prioritize`'s "a proposable tooling-tree node is a strong default recommendation" now
  applies only when every proposal in the pool is itself a tooling-tree node. The moment an
  issue-backed candidate (structural, PHPStan baseline-shrink, or externally-labeled) is ranked
  alongside a gate like `structural-scan`, no default applies to either side — both compete purely
  on Heat, Leverage, Tooling pressure, and Risk. Previously the default let a
  permanently-or-long-proposable gate out-rank an already-filed candidate indefinitely, regardless
  of the candidate's real merit.
- The one-time exception in Track selection is gone: once the Safety Net is in place, no Track gets
  a forced turn any more. The scheduler goes straight to its ordinary order — Guardrails' first
  scan, Housekeeping's first cycle, Guardrails' backlog, then Investigation — and the Safety Net
  pass that finishes the foundation tells you that Guardrails, Housekeeping and Investigation can
  now each be run directly by naming the Track (e.g. `/continuous-refactoring investigation`). An
  Investigation candidate already in flight no longer takes passes away from a due Housekeeping or a
  workable Guardrails node.
- A Safety Net or Guardrails scan now hands its own fulfilment judgement to the tooling-tree script
  and records the script's complete ordered list — blocked nodes included — as the Track's `Open`,
  instead of reading a state the script no longer detects. Fixed alongside: a target whose
  `bookkeeping.md` had a `## Safety Net` section but no `## Guardrails` section yet was read as
  having every Guardrails node already in place; a missing Track section now means that Track never
  ran. A seed file the script cannot read now stops it with an error instead of being silently
  replaced by the bookkeeping state.

## [0.5.0] - 2026-09-24

- The PHP tooling tree's three propose-time stop conditions are now recognition-only gate nodes in the
  shipped tree (`skills/refactor-scan/references/php-tooling-tree.md`), modeled on `is-php-project`:
  `has-real-dependency` (the project has a real, non-platform dependency) gates `composer-audit`,
  `phpstan-baseline-empty` (the current PHPStan baseline is empty) gates every PHPStan level above zero,
  and `phpstan-not-psalm` (PHPStan, not Psalm, is the project's analyzer) gates the first level above
  zero. Each is never proposed — only a required parent carrying a Purpose and an agent-judged
  Fulfilment check in its tree doc — and the graph logic carries no special-case flag for these
  situations any more; what gets proposed on any target is unchanged.
- `continuous-refactoring` is now a thin dispatcher: it only selects a Track (`references/track-scheduler.md`,
  unchanged) and invokes that Track's own skill. The pass itself (scan → prioritise → design → implement →
  learn) moved into a new track-agnostic `refactor-loop` skill that requires a Track and aborts without one;
  `continuous-safety-net`, `continuous-guardrails` and `continuous-investigation` delegate to it, and
  `continuous-housekeeping` owns Housekeeping's own process with its three reference files. Only
  `continuous-refactoring` is a user entry point (`/continuous-refactoring`, with or without a Track name,
  behaves as before); the new skills are internal. See ADR-0057.
- Safety Net Track: `refactor-scan` now judges a Safety Net Track node's Fulfilment check against its
  own Purpose statement (an agent walking the tree), instead of trusting `tooling_tree.py`'s raw
  dependency-name match alone — a target already running Laravel Pint is recognized as fulfilling
  `php-cs-fixer`'s Purpose and is never proposed a redundant, possibly colliding second style tool.
  `bookkeeping.md` gains a `## Safety Net` section (`Cadence`, `Last scan`, `Open`, `Out-of-scope`),
  replacing the old `Fulfilled nodes`/global `Pending candidates` fields for this Track's own nodes;
  `refactor-learn` writes into it symmetrically — merge removes an entry from `Open`, rejection removes
  it and writes both `out-of-scope/<slug>.md` and an `Out-of-scope` pointer. A repo on the old
  `bookkeeping.md` shape runs a normal pass, unaffected.
- Guardrails Track: `refactor-scan` now judges a Guardrails Track node's Fulfilment check against its
  own Purpose statement, the same mechanism ticket 01 established for the Safety Net, applied to the
  seven nodes required on `structural-scan`/`php-safety-net` themselves (`composer-audit`, `phpmd`,
  `coverage-floor`, `php-minimal-version`, `phpstan-level-6` and above, `phpstan-deprecation-rules`,
  `semgrep`) — proposed only once the Safety Net has closed. `bookkeeping.md` gains a `## Guardrails`
  section (`Cadence: 60`, `Last scan`, `Open`, `Out-of-scope`), independent of `## Safety Net`;
  `refactor-learn` writes into it with the identical merge/rejection symmetry
  `safety-net-write.md` already established. A repo mid-migration — `## Safety Net` already closed, `##
  Guardrails` never run — runs a normal pass, unaffected.
- Dev-repo CI: `tier3` (Ground Truth) and the `roadmap` fixture matrix no longer gate `test-harness.yml`.
  Both asserted against `tooling_tree.py`'s own deterministic, hardcoded-dependency-name matching for
  Safety Net/Guardrails nodes — which tickets 01/02 (ADR-0055) made no longer the operative fulfilment
  path for those nodes — and CI has no model credentials to run the agent-judged check that replaced it.
  Both remain runnable locally via `fixtures/harness/run.sh`'s existing `--opencode` flag, the same
  local-only/advisory posture `tier4`'s non-deterministic parts, `judge`, `lift`, `agent-loop`, and
  `decision-gate-bypass` already use. `tier1`/`tier2` are unaffected and still gate CI.
- Track scheduler: the orchestrator now runs real competition between every currently-wired **Track**
  (Safety Net, Guardrails) instead of each Track deciding on its own whether it's due — a new
  Track-selection step (`skills/continuous-refactoring/SKILL.md` step 0b,
  `skills/continuous-refactoring/references/track-scheduler.md`) computes each due, `Open`-empty Track's
  `overdue_ratio = (today − Last scan) / Cadence` and hands the highest-ratio one to `refactor-scan` as
  an explicit input; a tie (or two Tracks that have never run) falls back to the fixed order Safety Net
  > Guardrails > Housekeeping > Investigation. A Track with non-empty `Open` still always has its
  existing work worked instead of being rescanned, and a human can still name a Track directly to bypass
  selection entirely. Written generically over every Track carrying a bookkeeping section, so
  Housekeeping and Investigation slot into the same mechanism later without another rework. The
  suite-wide open-MR cap (`refactor-prioritize` step 1) was already Track-agnostic and needed no change.
- **Investigation** now has its own `bookkeeping.md` section (`## Investigation`, `Cadence`/`Last scan`
  only — no `Open`/`Out-of-scope`, a structural candidate's own state still lives on the issue tracker /
  `merge-requests.md` as before) and joins the Track scheduler's real competition
  (`skills/continuous-refactoring/references/track-scheduler.md`). Its `Cadence` is always the literal
  `continuous` — no fixed interval, always due, always eligible — which makes it the scheduler's
  permanent fallback: it only wins a pass the moment no other wired Track (Safety Net, Guardrails) is
  both due and eligible, consistent with the fixed tie-break order Safety Net > Guardrails > Housekeeping
  > Investigation. `structural-scan`'s own candidate-search behavior is unchanged — only *when* it gets
  proposed changes: gated behind Investigation Track selection (`skills/refactor-scan/references/
  investigation-track.md`) instead of proposed unconditionally every pass.
- The standalone `continuous-housekeeping` skill is retired. Its process — due-check, reconciliation
  against fulfilled nodes, checklist assembly from `housekeeping-template.md`, quality gate, deliver —
  is unchanged, but now runs as the **Housekeeping Track**'s own content
  (`skills/continuous-refactoring/references/housekeeping-track.md`), triggered by the shared Track
  scheduler (`skills/continuous-refactoring/references/track-scheduler.md`) instead of its own standalone
  due-check. `bookkeeping.md` gains a `## Housekeeping` section (`Cadence`, `Last scan` only — no
  `Open`/`Out-of-scope`; swept content stays in `housekeeping-template.md`, unchanged) — a hybrid of
  Investigation's shape and Safety Net's/Guardrails' own: `Cadence` defaults to `7` (days, unchanged from
  today's default) and is hand-editable, unlike Investigation's permanent `continuous`, but there's no
  in-flight `Open` list, unlike Safety Net/Guardrails. Manual invocation of the Housekeeping Track
  directly stays possible, generalized to the same Track-name-as-argument pattern Safety Net, Guardrails,
  and Investigation already use — one shared invocation surface across all four Tracks now, replacing the
  old skill's own separate `/continuous-housekeeping` entry point. No standalone `continuous-housekeeping`
  skill remains; its `references/` (cadence interview, `housekeeping-template.md`'s own format doc) moved
  under `continuous-refactoring`.
- The Track scheduler gains a one-time exception, checked first, before any `overdue_ratio`/tie-break
  computation: the pass right after Safety Net's own `Open` first empties runs **Investigation** once
  (one candidate, fully delivered), then the following pass runs **Guardrails** once (its own first
  scan-and-clear cycle), then the pass after that runs **Housekeeping** once (its own first cycle) —
  each overriding ordinary selection for exactly that one turn, so a target sees one real piece of
  delivered refactoring value before being asked to adopt more tooling or sit through maintenance.
  Ordinary staleness-ratio scheduling resumes permanently once Housekeeping's turn completes — including
  Safety Net's own later, rarer rescans. Tracked entirely from the existing Track sections'
  `Last scan`/`Open`/`Pending candidates` state — no new stored flag: each of Investigation's/Guardrails'/
  Housekeeping's own "have I ever run" section-presence, plus (for Investigation only, which carries no
  `Open` of its own) whether `Pending candidates` still names its in-flight candidate, is what makes the
  exception fire exactly once per repo (`skills/continuous-refactoring/references/track-scheduler.md`'s
  own "One-time exception" section).
- A selected node-based Track is now worked one `Open` node per pass, top to bottom
  (`skills/refactor-scan/references/track-open-processing.md`): the topmost workable node is picked up,
  its Fulfilment check is re-run right before its issue is created — a node fulfilled by hand since the
  scan leaves `Open` with no merge request and the pass moves on — and non-workable nodes are collected
  with a reason for the pass report. Track nodes are no longer pre-filed as issues at proposal time
  (amending ADR-0047's pre-filing decision for them): the issue is created only when the node is
  actually worked, and Rank mode no longer chooses among Track nodes. Three new advisory agent fixtures
  cover the pick-up re-check (`php-track-open-hand-adopted`), the top-to-bottom order with a blocked
  node in between (`php-track-open-blocked-in-between`), and a priority-labeled issue waiting behind the
  top of `Open` (`php-track-open-priority-vs-top`).
- The Track scheduler implements Safety Net blockade, Guardrails yield, and Housekeeping preemption
  (`skills/continuous-refactoring/references/track-scheduler.md`). While Safety Net `Open` is non-empty,
  Safety Net is selected and nothing else runs — even if no node is currently workable; what it waits on
  is reported. Guardrails with a workable `Open` node is selected ahead of Investigation; Guardrails with
  `Open` non-empty but nothing workable yields, its `Open` stays as it is, and the pass report lists
  every stalled node with its reason. Housekeeping preempts Guardrails for one pass when due
  (`overdue_ratio >= 1`), then Guardrails resumes afterwards. The one-time bootstrap exception advances
  past Guardrails' non-empty `Open` — it reads only whether each section *exists*, not whether its `Open`
  is empty. Four new advisory agent fixtures exercise these rules: `php-scheduler-safety-net-blockade`,
  `php-scheduler-guardrails-stalled`, `php-scheduler-housekeeping-preempts-guardrails`,
  `php-scheduler-bootstrap-guardrails-open`.
- The Housekeeping Track's reconciliation now sweeps via agent judgement
  (`skills/continuous-refactoring/references/housekeeping-track.md`): each cycle it checks only the
  nodes that carry a `Housekeeping` field, judges each one's Fulfilment check against its Purpose, and
  appends any missing checklist line — so a tool adopted by hand, Guardrails tools included, gets its
  line even when no delivering merge request ever existed. The `Fulfilled nodes` bookkeeping field is
  retired: no skill reads or writes it any more, and a `bookkeeping.md` that still carries the old field
  is left untouched and ignored. Covered by two new advisory agent fixtures:
  `php-housekeeping-hand-adopted-guardrails` and `php-housekeeping-old-schema`.
- `skills/refactor-scan/references/tooling_tree.py` no longer detects anything: the hardcoded
  dependency-name detection and the forward-simulating `roadmap` output are deleted, and the script now
  takes a fulfilment seed (`--seed`, or the Refactoring Notes' `fulfilled-set.json`) or derives state
  from `bookkeeping.md`'s Track sections, computing the tree's graph logic only — the ordered `Open`
  backlog, workable and withheld nodes with reasons, rejection cascades, PHP-floor findings, and the
  merge-request outlook (`--unblocked-by`). The harness's `roadmap` tier and the eight
  `expected/roadmap.json` fixtures are removed with it; the drift check comparing the manual tree-walk
  fallback with the script's graph logic continues as `scripts/drift_check.py`, advisory and run
  manually (never collected by CI's `test_*.py` discovery).
- Safety Net and Guardrails Track `Open` entries now record their issue number (`- <slug> (#<issue>)`) as soon as `refactor-design` files it, instead of staying unlinked until a merge request opens or merges — closes a bookkeeping gap that previously forced `refactor-scan` to rediscover already-filed tickets by searching instead of reading the link.
- Cross-skill citations inside `skills/**` (one skill's `SKILL.md`/reference file pointing at another skill's reference doc) are now written relative to the citing file instead of the suite repo's root — the old form never resolved once a skill shipped into a target repo, forcing an agent to search the filesystem for a file it was told to consult. `scripts/validate_skills.py` now checks the new form and flags any reappearance of the old one.

    `safety-net-track.md`/`guardrails-track.md` no longer imply a node's tree-doc file can be derived from its slug alone (`php-tooling-tree/<node>.md`) — a multi-node file like `rector.md`/`psalm.md` broke that assumption and sent an agent searching for a file that doesn't exist under that name. Both now point at `php-tooling-tree.md`'s own per-node *Full definition* pointer instead, which always names the right file.
- `php-structural-scan` renamed `php-safety-net`. `CONTEXT.md` gains **Onboarding** (the bounded
  phase before `structural-scan` opens) and its narrower **Safety Net**, plus a new **Signal wave**:
  `composer-audit`/`phpstan-deprecation-rules` move out of the PHP Safety Net into the Signal wave
  (gated on `php-safety-net` closing, in addition to their existing required parent, so a rejected
  parent still permanently closes them); `phpmd`/`coverage-floor`/`php-minimal-version`/
  `phpstan-level-6` join the Signal wave the same additive way; `semgrep` is fully repointed onto
  `php-safety-net` alone (its old `composer` required parent dropped); the generic root's
  `secret-detection` now waits for `structural-scan` itself to open instead of proposing from the
  very first pass. `composer-audit`/`semgrep` also gain a Housekeeping-line fulfilment fallback (a
  committed `housekeeping-template.md` line naming the node, no CI run required).
- `phpstan-level-0` detection now falls back to `phpstan.neon.dist` when `phpstan.neon` is absent
  (PHPStan's own auto-discovery order, already honored elsewhere in this tree for
  `phpunit.xml.dist`/`psalm.xml.dist`/`phpmd.xml.dist`). `phpstan.neon` still wins when both files
  exist. Fixes a false "no level configured" report on targets that only ever committed the `.dist`
  file.
- A Track's `Cadence` can now be written with a unit — `12 hours`, `7 days`, `2 weeks`, `1 month` — or as a fixed monthly day (`monthly on the 1st`); a bare number from an older `bookkeeping.md` still reads as days, and the loop now writes its defaults as `90 days`, `60 days` and `7 days`.
- Docs refresh: README now explains the four Tracks (Safety Net, Guardrails, Housekeeping, Investigation), the dispatcher/`refactor-loop` split and the two-merge-request cap, and indexes all docs. New `docs/playbooks/tracks.md` (how Tracks are selected, the one-time exception, working open items, overrides) and `docs/architecture.md` (skill hierarchy, one pass step by step, subagent hand-back, tooling tree, loop state). The loop and Housekeeping playbooks, FAQ and known-limitations (now with a "why did the pass end without doing anything?" troubleshooting table) are brought in line with the current skills.
- The loop now says what it is doing while it runs: one sentence before and after each step (scan, ranking, design, implementation, recording), and a separate line for every change it makes in your repository — an issue created, a branch pushed, a merge request opened. Housekeeping reports the same way.
- Onboarding is now its own first step of `/continuous-refactoring`: on a project with no `bookkeeping.md` the very first output says onboarding is starting, a short interview (tracker, merge-request mode, where the Refactoring Notes live — plus a one-time "stop and set up the engineering skills, or continue?" question when their issue-tracker and triage-label files are missing) runs inline, the setup files are written (`bookkeeping.md` last) and the invocation ends with a closing text: commit the files, then run `/continuous-refactoring` again to start the first scan. No scan subagent, issue, merge request, branch or forge action is involved, and no label is created on GitHub/GitLab (the closing text lists `gh label create` commands for GitHub). `continuous-safety-net`, `continuous-guardrails`, `continuous-investigation` and `continuous-housekeeping` now abort with a pointer to `/continuous-refactoring` on a project that was never onboarded. The tooling-tree node `loop-config` ("Refactoring Config") is renamed `onboarding-setup` ("Onboarding Setup"); targets with an old-style `loop-config` candidate already open are not migrated.
- The `bookkeeping.md` the onboarding writes is now titled `# Refactoring Bookkeeping` (was `# Refactoring Loop Config`); existing files keep working unchanged. On an already-onboarded project a pass no longer says anything about onboarding.
- `refactor-scan`'s tooling-tree step now applies `php-tooling-tree/psr-4.md`'s own judgement call
  before treating a non-empty `unwired_entry_points` result as real unaddressed work: files that never
  reference the target's own PSR-4 root namespace and are self-evidently dev/CI/build utilities are
  exempt. Fixes a false "PSR-4 autoloader not wired" report on targets (e.g. Laravel-style repos) whose
  entry-point sweep also picks up framework config/migration files that were never meant to require
  the autoloader themselves.
- The retired `Fulfilled nodes` bookkeeping field is removed from the documented schema and from every fixture and harness check. Nothing changes for a `bookkeeping.md` that still carries it: the block is ignored, and can be deleted by hand at any time.
- New `Ticket-create-mode` setting (`autonomous`, or `ask-each-time` to be asked before a ticket is created), asked in the onboarding interview right after the tracker. Only the loop creates tickets now — the steps that propose candidates hand it drafts — and with `ask-each-time` it asks once for the batch of proposed tickets and once for the candidate it chose; a refused or unanswered ticket ends the pass without writing anything. A missing field means `autonomous`, so existing targets behave as before.
- `Create-mode` is renamed `MR-create-mode` (values unchanged) — it only ever governed how merge requests get opened. An older `bookkeeping.md` with the old name is still read, and renamed on its next bookkeeping write.

## [0.4.0] - 2026-09-15

- `refactor-prioritize` now selects and minimally files a structural or PHPStan-baseline-shrink
  candidate itself (a second, fresh dispatch — "Select mode"), the moment one is chosen — visible
  on the tracker right away instead of only once its full plan is finished. `refactor-design`
  grounds and grills that already-filed candidate afterward, adding the plan as a comment rather
  than filing a second issue. (#63)
- `refactor-prioritize`'s Select mode now files every genuine structural/PHPStan-baseline-shrink
  candidate it finds, not just the strongest — sorted into a `refactor:priority` tier (Security or
  Blast-Radius-of-inaction signals, exempt from `refactor-scan`'s backlog cap) or the ordinary
  capped tier. New `signals.md` catalogues seven additional Signal factors (Security, defect
  density, blast radius of inaction, understandability, observability, domain/business criticality,
  timing) used only in Select mode's own candidate search and ranking. `CONTEXT.md` gains a
  `Signal` glossary entry; `docs/playbooks/loop.md` introduces "Safety Net" as a human-facing
  reading aid for the existing tooling tree. (#64)
- Two new Signal-producing tooling-tree nodes — `phpmd` (PHP tree) and `secret-detection` (generic
  root) — are real, adoptable nodes now, not just `signals.md` documentation; once adopted,
  `refactor-prioritize`'s Select mode reads their real tool output for the
  Understandability/Defect-density and Security factors instead of the generic recognition method.
  Neither carries a `resolved` edge into `structural-scan` — adopting them enriches candidate
  selection, they never gate structural work. Node docs gain an optional `Signal` field (mirroring
  the existing `Housekeeping` field). Three PHP-tree edges simplified: `test-runner-if-missing`
  drops its direct `php-structural-scan` resolved edge (`ci-runner` already gates `structural-scan`
  independently); `php-cs-fixer` drops its own direct resolved edge in favor of a new `recommended`
  edge into `rector-php-set`; the PHPStan level chain's resolved-leaf moves from level 10 to level 5
  (its first structural fork point), leaving levels 6–10 ordinary, non-gating, still-proposable
  nodes. (#65)
- `php-minimal-version` no longer proposes raising `composer.json`'s declared PHP floor beyond what
  the codebase's own code already requires — only a Floor correction (bringing the declared floor
  in line with syntax `rector-php-set` has already landed) is ever auto-proposed now, never a Floor
  raise (committing the application to a newer PHP than its code currently needs, a real breaking
  change). `CONTEXT.md` gains `Floor correction`, `Floor raise`, and `Breaking change` glossary
  entries. (#67)
- `psr-4` now also wires Composer's autoloader (`vendor/autoload.php`) into the target's own
  composition root (or every entry point when there's none), on top of its existing check that the
  mapping mechanism actually works — closing the gap where a target could adopt PSR-4 yet keep
  loading classes by hand indefinitely. `CONTEXT.md` gains `Entry point` and `Composition root`
  glossary entries. (#68)
- `refactor-scan` now runs a one-time full git-history secret scan once `secret-detection` is
  fulfilled, reusing the same scanner already gating CI and its own baseline mechanism to avoid
  re-filing known findings — each new finding becomes a `refactor:priority` candidate issue (the
  secret's value redacted), filed by `refactor-learn`. (#71)
- New `coverage-floor` tooling-tree node (PHPUnit child, Signal-producing — no `structural-scan`
  gating): measures test coverage against a self-tightening ratchet committed to the target repo
  (`.coverage-floor`, only ever rises via a normal reviewed commit, never auto-bumped by CI) instead
  of a fixed percentage. Driver-agnostic — PCOV is the adoption default, Xdebug works too. (#72)
- New `semgrep` tooling-tree node (OWASP Top 10 static analysis, Signal-producing — no
  `structural-scan` gating): complements the existing `psalm-taint-analysis` node rather than
  duplicating it (crypto misuse, misconfiguration, and logging-gap categories taint analysis
  doesn't reach on its own). No separate manual security checklist — the tool's own CI-gated
  findings supersede it. (#73)
- `psr-4`'s autoloader-wiring check now reports exactly which entry points still need
  `vendor/autoload.php` wiring instead of only a boolean — a tooling-tree node's own generated
  CI-helper script can structurally never need it, and telling that apart from genuine unaddressed
  application work is now a documented judgement call, not a guess the parser itself makes. (#74)
- The suite now has an official website, [continuous-refactoring.de](https://continuous-refactoring.de/),
  linked from `README.md` and set as this GitHub repo's homepage URL. (#75)
- Every currently-unblocked tooling-tree node now gets a minimal candidate issue filed as soon as
  it's proposable, not just the one the loop picks to work on next — giving a human a chance to
  comment or reject a proposed tool before any implementation work is spent on it. `loop-config`'s
  own onboarding interview now summarizes the concrete decisions and actions about to happen before
  writing anything; a cold-start pass on a target with no Refactoring Notes yet skips straight to
  proposing `loop-config` instead of walking the whole tooling tree first. (#76)
- `Skip streak` is gone — replaced by two signals `refactor-prioritize`'s Rank mode now reads
  directly off each proposal's own pre-filed issue: its age, and a human-settable
  `refactor:priority` label (a hard override — narrows the candidate pool to only priority-labeled
  proposals when any exist). Local Markdown issue trackers gain a `Filed: YYYY-MM-DD` line so age
  is readable there too. (#77)
- Suite merge requests no longer stack — every branch this suite opens now always branches directly
  off the default branch, unconditionally. Reverses an earlier decision after two real incidents
  where a stacked PR got silently auto-closed by the forge when its base branch was deleted on
  merge. (#78)
- Fixed a bug where a target with a rejected `composer` node (out of scope) could get permanently
  stuck with zero proposable tooling-tree candidates, never reaching `structural-scan`, even though
  the rejection should have cascaded down and resolved everything beneath it — the internal
  gate-closure checks mistook a legitimate diamond-shaped dependency for a cycle and returned a
  false negative. (#79)
- `rector-type-coverage` and `semgrep` now carry a `composer` required parent, alongside their
  existing recommended parent(s) — they were the only two nodes in the whole tooling tree with no
  required/required-any chain back to `composer` at all, so a rejected `composer` could never
  automatically close them, forcing a manual issue-file-and-reject cycle on a target with no PHP
  application code. (#79)
- Clarified `CONTEXT.md`'s `Recommended edge`/`decided` definition: a recommended parent counts as
  decided-rejected not only via its own `out-of-scope/` entry, but also transitively, when one of
  its own required ancestors is rejected — a rule the tooling has always implemented but the
  glossary never stated. (#80)
- `refactor-design` now applies a pre-implementation decision gate while grounding/grilling or
  planning a fix: a design decision that's hard to reverse, surprising without context, or a real
  trade-off — while the candidate itself stays behavior-preserving — gets written as a plan with a
  proposed default plus an explicit open question on the candidate issue, and the existing
  `ready-for-agent` label is deliberately withheld until a human confirms or overrides it. A genuine
  breaking change discovered mid-design is now handled too: `refactor-design` hands it forward as a
  finding, and `refactor-learn`'s closing call applies its existing rejection machinery (`wontfix`,
  a closing note or `out-of-scope/` entry). (#82)
- A new shared reference tells every lifecycle skill how to write text that lands on the target
  repo's own forge (issue comments, closing notes, `out-of-scope/` entries, merge request
  descriptions): the reader has never seen this suite's own repo, so skills no longer cite this
  suite's own file paths or use its controlled-vocabulary labels as justification — they state the
  rule or finding itself in plain words instead. (#83)
- `refactor-learn` now requires a genuine event (a finding, a freshly opened merge request, or a
  design-time breaking-change finding) before it writes anything — a call with nothing to react to
  stops immediately instead of opening a bookkeeping merge request that only refreshed the
  `Fulfilled nodes` cache, and checks only what it was actually handed rather than independently
  investigating to find a reason to act. `refactor-design` now reads existing issue comments, not
  just the body, everywhere it grounds itself in a candidate, and posts a **Decision trail** comment
  recording any grilling question that met the ADR bar, separate from the decision gate. A
  tooling-tree candidate's "what this unlocks next" note moves off the merge request description
  and onto the candidate's own issue. `Secret history scan: done` now carries the date it ran.
  `refactor-scan` also now resolves `tooling_tree.py` relative to wherever the suite's skills are
  actually installed rather than assuming the suite's own repo is the current working directory —
  no more sub-agent dispatch just to locate it when running from a target repo. (#84)
- Fixed a bug that could silently bypass the pre-implementation decision gate: a pre-existing
  `ready-for-agent` label on an externally-filed issue was never cleared when `refactor-design`
  flagged a decision meeting the ADR bar, so `refactor-scan`'s resume checks read it as already
  confirmed and routed straight to `refactor-implement` without a human ever seeing the flagged
  question. `refactor-design` now actively manages both `ready-for-agent` and `needs-info` in both
  directions for every candidate it plans, not only the three decision-gate-eligible types. (#86)

## [0.3.0] - 2026-09-06

- Fixed two tooling-tree parser false negatives (`phpstan-level-0` and Rector's set-name casing)
  that could report an already-adopted node as unfulfilled. (#48)
- `refactor-scan` now proposes PHPStan baseline-shrink candidates: incrementally reducing an
  existing baseline file instead of leaving it frozen forever. (#49)
- Fixed a staleness bug: the bookkeeping write now reads a fresh `origin/main` immediately before
  writing, instead of a snapshot that could be several commits behind. (#50)
- Fixed the resolved-gate cascade to correctly propagate through a rejected required ancestor,
  instead of leaving descendants stuck — including the same fix applied to `composer-audit`'s own
  fallback gate. (#51, #55)
- Added a `Refactoring goal` field that steers which structural candidates the loop searches for
  next. (#53)
- Fixed Psalm-equivalence detection to respect the documented co-presence rule instead of a
  stricter, undocumented one. (#57)
- Added the `continuous-housekeeping` skill: a separate, recurring maintenance sweep (default
  weekly) for dependency currency, tooling-deprecation cleanup, and documentation sync — plus a
  `Housekeeping` field tooling-tree nodes can contribute to. (#58)
- Added `docs/FAQ.md`, answering recurring questions about the suite's own design decisions,
  linked from the README. (#59)
- Added a `CHANGELOG.md` fragment-file mechanism: noteworthy changes drop a `.changelog.d/*.md`
  fragment (enforced by CI via the `no-changelog` label escape hatch), consolidated into
  `CHANGELOG.md` — and the fragments deleted — at release time. (#60)

## [0.2.0] - 2026-09-04

- Folded native-tracker in-flight bookkeeping into the candidate's own branch instead of a shared
  file, removing a recurring source of merge conflicts. (#40)
- On a native-label tracker, `refactor-design` skips the now-redundant Pending-candidates write.
  (#41)
- Dropped the `rector-early-return` tooling-tree node, folding its scope into
  `rector-code-quality`. (#45)
- Candidate merge requests now open as draft until the fold-in bookkeeping lands. (#46)
- Added a `psr-4` tooling-tree node for app-source autoloading. (#47)

## [0.1.0] - 2026-09-03

Initial release.

- The `scan → prioritize → design → implement → learn` orchestrator loop, plus the generic
  (language-neutral) tooling tree and its `structural-scan` gate. (#8, #9)
- PHP tooling-tree specialization: structural-scan leaves (editorconfig, composer, ci-runner), an
  `is-php-project` recognition gate, the PHPStan adoption chain (levels 0–10, baseline shrinking,
  Psalm mutual exclusion), the Rector rule-set family, and a PHP-minimum-version floor precheck.
  (#6, #7, #21, #23, #24, #26, #27, #28, #29, #30, #31)
- Recommended-edge gating and a CI-gating self-wire, so a node only proposes once its
  prerequisites are actually adopted, not merely present. (#19, #20)
- `loop-config` became a one-time human setup interview instead of guessing the tracker/create-mode.
  (#32)
- Human-readable tooling-tree node names, a per-pass closing report, and Learnings entries
  recording what a past attempt got wrong. (#13, #14)
- A round of fixes from the suite's first live dogfooding run against a real target repo:
  composer-audit timing, config caching, PHPUnit layout detection, `.scratch` cleanup,
  refactor-prioritize starvation, and a further batch of reviewer-loop findings. (#12, #15, #16,
  #17, #18, #36)
- Test harness (Tiers 1–5): fixture-driven regression coverage for the tooling-tree parser,
  trigger tests, and its own CI gate. (#1, #2, #3, #10, #22)
- Every skill's `SKILL.md` radically shrunk for token economy, detail moved into `references/`.
  (#33)
- Repo prepared for going public. (#37)

[0.9.0]: https://github.com/Art4/continuous-refactoring/compare/0.8.0...0.9.0
[0.8.0]: https://github.com/Art4/continuous-refactoring/compare/0.7.0...0.8.0
[0.7.0]: https://github.com/Art4/continuous-refactoring/compare/0.6.0...0.7.0
[0.6.0]: https://github.com/Art4/continuous-refactoring/compare/0.5.0...0.6.0
[0.5.0]: https://github.com/Art4/continuous-refactoring/compare/0.4.0...0.5.0
[0.4.0]: https://github.com/Art4/continuous-refactoring/compare/0.3.0...0.4.0
[0.3.0]: https://github.com/Art4/continuous-refactoring/compare/0.2.0...0.3.0
[0.2.0]: https://github.com/Art4/continuous-refactoring/compare/0.1.0...0.2.0
[0.1.0]: https://github.com/Art4/continuous-refactoring/releases/tag/0.1.0
