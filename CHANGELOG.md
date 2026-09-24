# Changelog

All notable changes to this project are documented here. Format inspired by
[Keep a Changelog](https://keepachangelog.com/), kept flat (no `Added`/`Changed`/`Fixed`
subcategories) — see `CONTRIBUTING.md`'s "Changelog" section for how entries are produced.

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

[0.5.0]: https://github.com/Art4/continuous-refactoring/compare/0.4.0...0.5.0
[0.4.0]: https://github.com/Art4/continuous-refactoring/compare/0.3.0...0.4.0
[0.3.0]: https://github.com/Art4/continuous-refactoring/compare/0.2.0...0.3.0
[0.2.0]: https://github.com/Art4/continuous-refactoring/compare/0.1.0...0.2.0
[0.1.0]: https://github.com/Art4/continuous-refactoring/releases/tag/0.1.0
