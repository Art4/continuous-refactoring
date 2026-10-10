# 09: Decide the tests, accept, open the pull request

**What to build:** The rebuilt suite is accepted on a real target and goes to `main` as one pull request
with a pipeline that is green for stated reasons.

Spec: `../spec.md` (section *Testing Decisions*).

**Blocked by:** 08

**Status:** ready-for-human

- [ ] The human decides, with the list of red checks from ticket 08 in view, what happens to the
      validator's checks, the trigger-control tests and the fixture harness: deleted, adapted or rewritten
- [ ] That decision is carried out and the pipeline is green
- [ ] Acceptance from the `suite-rebuild` checkout in the target whose tracker and forge are different
      systems: onboarding again, one interactive run, one autonomous run, one Housekeeping run; what was
      observed is noted here
- [ ] The pull request from `suite-rebuild` to `main` is open

## Comments

### Red after ticket 10 (parser computes the gates, lists only ticketable nodes)

Ticket 03's comments list what was red before. On top of that:

- `scripts/drift_check.py` (not run in CI) — three more failures, all expecting a node the parser no
  longer lists: `DriftCheckTests.test_empty_repo_workable_starts_with_onboarding_setup`
  (`onboarding-setup` in `next`), `DriftCheckTests.test_php_safety_net_resolved_gate` and
  `SeedFixtureConsistencyTests.test_fully_resolved_seed_only_structural_scan_workable` (`structural-scan`
  in `next`). `SeedFixtureConsistencyTests.test_fully_resolved_seed_empty_backlog`, red since ticket 03,
  passes again. Now 7 failures and 1 error.
- `python3 scripts/validate_skills.py .` — still exits 1 for the old reasons; one new warning, a
  duplication advisory on `skills/refactor-scan/references/php-tooling-tree/psalm.md` (a Purpose sentence
  of `psalm-taint-analysis` now reads the same in the node file and in `php-tooling-tree.md`).
- `changelog-fragment.yml` — `skills/**` changed again without a `.changelog.d/` fragment.

Unchanged: `scripts/test_trigger_controls.py` and `scripts/test_validate_skills.py` fail exactly as
before (one test each). Not run here: the `fixtures/harness/run.sh` tiers; a fixture seed that hands in
`structural-scan` or `php-safety-net` is now ignored for those two nodes.

Not red, but now untrue (skill texts ticket 10 was told not to touch): everything that has
`structural-scan` proposed out of the parser's `next` once its gate opens, or has the caller judge the
two aggregation nodes — `skills/refactor-scan/SKILL.md` (step 4), `references/investigation-track.md`,
`references/tree-walk-prompt.md`, the MR scope in `references/tooling-tree/structural-scan.md`, and the
"`refactor-scan` must never surface this node" wording in `references/php-tooling-tree/php-safety-net.md`
(the parser now guarantees it). `CONTEXT.md` has no entry for "aggregation node", and its
"Recognition-only gate node" entry still gives `structural-scan` as an agent-judged example.

### Red after ticket 04 (the run, through Safety Net and Guardrails)

Unit tests (`python3 -m unittest discover -s scripts -p 'test_*.py'`): unchanged, the same two fail
(`test_trigger_controls…test_next_holds_only_structural_scan`,
`test_validate_skills…test_real_repo_passes`); 239 of 241 green. `scripts/drift_check.py`: unchanged,
7 failures and 1 error.

`python3 scripts/validate_skills.py .` — still exits 1. New errors:

- **Contract of the entry skill** — `continuous-refactoring: missing required '## Completion criterion'
  section` and `orchestrator skill must have a '## The pass' section`. The new `SKILL.md` has "The run"
  and a completion criterion per step.
- **References that do not exist yet** — `references/design-point.md`, `references/implement-point.md`
  (ticket 05) and `references/investigation-track.md` (ticket 06), cited by the new `SKILL.md`.
- **`track-scheduler.md` deleted** — 12 "local reference does not exist" errors in the old skills that
  still cite it: `continuous-safety-net`, `continuous-guardrails`, `continuous-investigation`,
  `continuous-housekeeping` (skill, `housekeeping-track.md`, `housekeeping-cadence-interview.md`),
  `refactor-scan` (skill three times, `safety-net-track.md`, `guardrails-track.md`,
  `investigation-track.md`). They go away with tickets 07 and 08.
- **Glossary** — `domain term 'not fulfilled' / 'proposal' / 'workable' used in 2 skills but missing
  from glossary` (the words are in `CONTEXT.md` inside other entries, not as entries of their own).
- **Ticket numbers in prose** — `reporting-progress.md: skill prose references 'pull request #'`: an
  example sentence to the human ("pull request #34 was merged"), not a maintainer reference.

Gone: the two "loop pass" errors of the entry skill and "glossary term 'Worklist' is defined but never
used".

New warnings: `contract advisory: orchestrator 'scan' / 'design' / 'implement' step does not mention
completion-criterion terms` for `refactor-scan`, `refactor-design`, `refactor-implement` — the validator
compares the entry skill's steps with the old skills of the same name.

Not run here: the `fixtures/harness/run.sh` tiers. Red by reading: every `php-scheduler-*` fixture, the
`_scheduler_scan_prompt` and `_guardrails_scan_prompt` prompts in `fixtures/harness/run.sh`, and
`fixtures/README.md` describe Track selection by `track-scheduler.md` (cadence, `overdue_ratio`, the
blockade); `php-safety-net-old-meaning-open` cites its *Manual override* section.
`changelog-fragment.yml` — `skills/**` and `CONTEXT.md` changed without a `.changelog.d/` fragment
(ticket 08's).

Not red, but now untrue: `AGENTS.md` line 44 still names `references/track-scheduler.md` (ticket 08).

### Red after ticket 11 (parser closes a node whose whole required-any group is out of reach)

Nothing is newly red. Unit tests (`python3 -m unittest discover -s scripts -p 'test_*.py'`): the same two
fail (`test_trigger_controls…test_next_holds_only_structural_scan`,
`test_validate_skills…test_real_repo_passes`); 248 of 250 green, the parser's own file 106 of 106.
`scripts/drift_check.py`: unchanged, 7 failures and 1 error. `python3 scripts/validate_skills.py .`:
output identical to before the ticket, still exit 1.

Not run here: the `fixtures/harness/run.sh` tiers. `changelog-fragment.yml` — `skills/**` changed again
without a `.changelog.d/` fragment.

Not red, but now untrue (texts ticket 11 was told not to touch) — each still describes the closure as
"a required or required-any ancestor is rejected", without the recognition-only member that is not
fulfilled:

- `CONTEXT.md`, entry **Aggregation node**: "fulfilled, rejected, or closed by a rejected required
  parent". The entry **Recognition-only gate node** uses "out of reach" for the node waiting behind an
  unfulfilled recognition-only node; the parser now closes such a node when a rejection takes the rest of
  its group.
- `skills/refactor-scan/references/tree-walk-prompt.md` (the `Open` paragraph),
  `skills/refactor-learn/references/safety-net-write.md` and
  `skills/refactor-learn/references/guardrails-write.md` (old skills, going with ticket 08).
- `fixtures/README.md` and `fixtures/php/php-safety-net-rejection-cascade/expected/behavior.md` name
  `closed_by_rejection` with the old meaning.

### Red after ticket 05 (design point, implement point, merge request)

Unit tests (`python3 -m unittest discover -s scripts -p 'test_*.py'`): unchanged, the same two fail; 248
of 250 green. `scripts/drift_check.py`: unchanged, 7 failures and 1 error.

`python3 scripts/validate_skills.py .` — still exits 1. New errors, all "domain term used in 2 skills but
missing from glossary", each because a new reference and an old skill share a word:

- `'spec'` and `'standards'` (the two review axes: `reviewing-a-change.md` and `refactor-implement`)
- `'tautological'` (`reviewing-a-change.md` and `refactor-implement`)
- `'tests that survive'` (`design-point.md` and `refactor-design`)

They go away when ticket 08 removes the old skills, unless the validator then still wants the words as
glossary entries.

Gone: the two "local reference does not exist" errors for `references/design-point.md` and
`references/implement-point.md`, and the orphan advisory for `triage-labels-template.md` (file deleted).

Not run here: the `fixtures/harness/run.sh` tiers. `changelog-fragment.yml` — `skills/**` and
`CONTEXT.md` changed again without a `.changelog.d/` fragment.

Not red, but now untrue:

- `fixtures/README.md` (line 88) and a comment in `fixtures/harness/run.sh` (line 372) name the deleted
  `triage-labels-template.md`; `fixtures/README.md` (line 285) describes the old "no forge/remote
  available" branch of `opening-a-merge-request.md`.
- `skills/continuous-housekeeping/references/housekeeping-track.md` (line 128) cites
  `opening-a-merge-request.md` for "MR-create-mode, basing" — rules that file no longer has (ticket 07).
- `docs/FAQ.md`, `docs/known-limitations.md`, `docs/playbooks/loop.md` and `docs/playbooks/tracks.md`
  still describe the `needs-info` / `ready-for-agent` labels of a flagged candidate (ticket 08).
- The PHP tree doc `php-tooling-tree/phpstan.md` (*Stop conditions*) still sends the baseline work to
  `refactor-scan` step 4b and `refactor-design`'s `phpstan-baseline-shrink.md`; node docs with a
  **Housekeeping** field (`composer-audit.md`) still name `docs/refactoring/housekeeping-template.md`
  as the fixed place and create it fresh, where `implement-point.md` now follows the **Housekeeping**
  operation.
- `scripts/validate_skills.py` (line 815) and the parser's `directly_unblocked_children` with its tests
  serve the Outlook comment, which the rebuilt suite no longer posts.

### Red after ticket 06 (Investigation in the run)

Unit tests (`python3 -m unittest discover -s scripts -p 'test_*.py'`): unchanged, the same two fail; 248
of 250 green. `scripts/drift_check.py`: unchanged, 7 failures and 1 error.

`python3 scripts/validate_skills.py .` — still exits 1. New errors, all "domain term used in 2 skills
(continuous-refactoring, refactor-prioritize) but missing from glossary", because the carried-over
`signals.md` and `structural-candidate-search.md` share their bold words with the old copies:

- the signal names: `'blast radius of inaction'`, `'defect density'`, `'low leverage'`, `'missing
  locality'`, `'observability'`, `'security'`, `'tightly-coupled seams'`, `'understandability'`
- the ranking word `'heat'`, and `'generic'`
- the ticket parts `'where'`, `'problem'`

They go away when ticket 08 removes `refactor-prioritize`, unless the validator then still wants the
words as glossary entries.

New warning: a duplication advisory on `skills/refactor-prioritize/references/signals.md` (a sentence of
the catalogue reads the same in the new `continuous-refactoring/references/signals.md`); gone with
ticket 08 as well.

Gone: "local reference 'references/investigation-track.md' does not exist".

Not run here: the `fixtures/harness/run.sh` tiers. `changelog-fragment.yml` — `skills/**` changed again
without a `.changelog.d/` fragment.

Not red, but now untrue: the **Signal** fields in the tree docs (`tooling-tree/secret-detection.md`,
`php-tooling-tree/phpmd.md`, `semgrep.md`, `coverage-floor.md`, and both tree files) point to
`refactor-prioritize/references/signals.md` and name "Select mode"; the catalogue the run reads is now
`continuous-refactoring/references/signals.md` (ticket 08).

### Red after ticket 07 (Housekeeping)

Unit tests (`python3 -m unittest discover -s scripts -p 'test_*.py'`): unchanged, the same two fail; 248
of 250 green. `scripts/drift_check.py`: unchanged, 7 failures and 1 error.

`python3 scripts/validate_skills.py .` — still exits 1, 61 errors before and after. New errors:

- **Contract of the skill** — `continuous-housekeeping: missing required '## Process' section` and
  `missing required '## Completion criterion' section`. The new `SKILL.md` has "The run" and a completion
  criterion per step, like the entry skill.
- **Glossary** — `domain term 'decision points' / 'none' / 'housekeeping line' used in 2 skills
  (continuous-housekeeping, continuous-refactoring) but missing from glossary`, and `'status'`
  (continuous-housekeeping, refactor-loop).
- **A deleted reference still cited by an old skill** —
  `refactor-learn/references/housekeeping-write.md` cites `housekeeping-cadence-interview.md`. Goes with
  ticket 08.

Gone: the four avoid-term errors of the old Housekeeping texts (`ask-each-time`, `bookkeeping`,
`checklist file`, `loop pass`) and their three "local reference `track-scheduler.md` does not exist"
errors.

Not run here: the `fixtures/harness/run.sh` tiers. Red by reading: the `housekeeping-track` tier and its
fixtures `php-housekeeping-hand-adopted-guardrails` and `php-housekeeping-old-schema`, and the two
`php-scheduler-housekeeping-*` fixtures, expect the old process (cadence, `Last scan`, a dated issue per
cycle, the fixed template path). `changelog-fragment.yml` — `skills/**` changed again without a
`.changelog.d/` fragment.

Not red, but now untrue:

- `skills/continuous-refactoring/references/refactoring-bookkeeping.md` (old, going with ticket 08)
  cites the deleted `housekeeping-cadence-interview.md` and sections of the old `housekeeping-track.md`.
- `scripts/validate_skills.py` (line 86) and `scripts/test_validate_skills.py` (line 217) name
  `docs/refactoring/housekeeping-template.md` as a fixed shared path; it is now only the path the setup
  recommends.
- `docs/playbooks/housekeeping.md`, `docs/architecture.md`, `docs/known-limitations.md` and `README.md`
  describe the old Housekeeping (ticket 08).
- For acceptance: the Housekeeping run should cover the setup with the first cycle in one run, and a
  second call before that merge request is merged (it should report that the setup waits).

### Red after ticket 08 (remove the old, bring the docs in line) — the full list

This list replaces the ones above: it is the state of `suite-rebuild` after the last build ticket.

**Unit tests** — `python3 -m unittest discover -s scripts -p 'test_*.py'`: 141 tests run, 1 failure,
2 errors.

- `scripts/test_tooling_tree.py` — error at import: it loads the parser from
  `skills/refactor-scan/references/tooling_tree.py`, and the parser now lives in
  `skills/continuous-refactoring/references/`. In a scratch copy with only that path changed, all 106
  tests pass.
- `scripts/test_trigger_controls.py` — error at import, for the same path. With the path changed, 4 of
  5 pass and `CleanRepoReportsCleanTests.test_next_holds_only_structural_scan` fails: it expects the
  parser to pick up `fulfilled-set.json` from the fixture's old scratch folder by itself and to offer
  `structural-scan` as a candidate.
- `scripts/test_validate_skills.py` — `EndToEndTests.test_real_repo_passes` fails because the validator
  reports errors on the real repository (next item). Its other tests pass; they build their own
  miniature suites out of the old skill names.
- `scripts/test_check_changelog_fragment.py` — green.

**Validator** — `python3 scripts/validate_skills.py .`: exit 1, 21 errors, 3 warnings.

- 5 × `ADR-0004: rule keyword … not found in refactor-design or refactor-implement` — the validator
  looks for the foundational rules in two skills that no longer exist; the rules are in
  `continuous-refactoring/references/foundational-refactoring-rules.md`.
- `continuous-refactoring: missing required '## Completion criterion' section` and `orchestrator skill
  must have a '## The pass' section` — the skill has "The run" and a completion criterion per step.
- `continuous-housekeeping: missing required '## Process' section` and `'## Completion criterion'
  section` — the same shape as the entry skill.
- 3 × `domain term … used in 2 skills but missing from glossary` (`decision points`, `housekeeping
  line`, `none`) — bold words both skills use that are no glossary entries of their own.
- `glossary term 'Flagged candidate' is defined but never used in the suite` — the design point
  describes the case without the term.
- 7 × `glossary avoid-term … used`: `task` (four times: the Housekeeping tasks of a template, where
  the glossary lists the word as avoided for **Candidate**), `todo` (twice: the package name
  `art4/legacy-todo` in the tree docs, whose exemption is keyed to the removed `refactor-scan`),
  `bookkeeping` (once: the interview names the old **Bookkeeping** bullet it removes).
- `reporting-progress.md: skill prose references 'pull request #34'` — an example sentence to the human,
  not a maintainer reference.
- Warnings: three duplication advisories between a node file and its tree doc (`psalm.md`,
  `ci-runner.md`, `is-php-project.md`); the tree doc repeats Name, Tool and Purpose by design.
- Beyond what it reports: its contract table (`scan` → `refactor-scan`, …), its exemption table and the
  two tree-doc paths in it (lines 96–125, 447–451) name removed skills and the old location.

**`scripts/drift_check.py`** (not run in CI) — does not start: it loads the parser from the old path.
With only the path changed, 31 tests run with 7 failures and 1 error, the same eight as before this
ticket:

- `test_backlog_excludes_rejected_nodes`, `test_recommended_parent_rejected_releases_child`,
  `test_rejected_node_excluded_from_workable`,
  `SeedFixtureConsistencyTests.test_rejected_node_excluded_from_backlog_and_workable` — they write
  rejections as files in the old out-of-scope folder, which the parser no longer reads.
- `test_onboarding_setup_fulfilled_unblocks_editorconfig` — hands `onboarding-setup` in as fulfilled
  without a tracker file; the parser settles that node itself.
- `test_empty_repo_workable_starts_with_onboarding_setup` (error), `test_php_safety_net_resolved_gate`,
  `SeedFixtureConsistencyTests.test_fully_resolved_seed_only_structural_scan_workable` — they expect
  `onboarding-setup` or `structural-scan` among the candidates; neither is listed any more.

**Changelog check** — `changelog-fragment.yml` / `scripts/check_changelog_fragment.py`: green.
`.changelog.d/suite-rebuild.md` exists (run here over the files changed against `main`).

**CI workflows as they stand**

- `skills-validation.yml` — red at both steps (unit tests, validator).
- `test-harness.yml` — tier 1 red (the validator); tier 4 red (`scripts.test_trigger_controls` fails
  at import); tier 2 depends on tier 1 and does not run.
- `changelog-fragment.yml` — green.

**Fixture harness** — `fixtures/harness/run.sh`, not run here (it needs Docker and an agent); by
reading:

- `tier2` (the one CI runs, on `php-project-with-candidates`) — would pass, but what it asserts is the
  old suite: the fixture's own `expected/` holds `config.md` and `bookkeeping.md`, and issues with the
  label `refactor:candidate`.
- `tier3` — counts ticket files under the old scratch folder against planted candidates; it compares
  numbers only and stays as it is, but nothing files tickets there by a fixed convention any more.
- `tier4` (local part) — asks an agent to run `/refactor-scan` and checks that the five removed
  lifecycle skills are discoverable; none exists.
- `agent-loop` — its prompt sends the agent from `continuous-refactoring/SKILL.md` to the five removed
  lifecycle skills and to a "no human is present" section the skill no longer has; a comment names the
  deleted `triage-labels-template.md`.
- `judge` — `rubric.md` grades against `refactor-implement`, `refactor-prioritize` and the consistency
  of `bookkeeping.md` and `merge-requests.md`.
- `decision-gate-bypass` — runs `/refactor-design` and `/refactor-scan` and expects the `needs-info` /
  `ready-for-agent` labels; the design point uses neither.
- `safety-net-track`, `guardrails-track` — every prompt runs `/refactor-scan` and `/refactor-learn` with
  `safety-net-track.md`, `guardrails-track.md`, `safety-net-write.md`, `guardrails-write.md`, and checks
  the `Open` list in `bookkeeping.md`; all of it is removed.
- `housekeeping-track` — expects the old process: cadence, `Last scan`, one dated issue per cycle, the
  fixed template path.
- `scheduler` — every prompt follows `track-scheduler.md` (cadence, overdue ratio, the blockade), which
  is deleted.
- `lift` — independent of the suite's shape; unaffected.
- Fixtures: every `php-*` fixture carries the old scratch folder (`bookkeeping.md`, `config.md`,
  `out-of-scope/`, `fulfilled-set.json`) and an `expected/behavior.md` in the old words; the
  `php-onboarding-*`, `php-issue-mode-unreadable` and `php-ticket-create-mode-ask` fixtures describe
  the old interview, `php-scheduler-*` the old Track selection, `php-*-old-schema` and
  `php-safety-net-old-meaning-open` a migration that no longer exists. `fixtures/README.md` describes
  all of this the old way.

**Not red, but worth knowing for the decision**

- `scripts/validate_skills.py` line 86 and `scripts/test_validate_skills.py` line 217 name
  `docs/refactoring/housekeeping-template.md` as a fixed shared path; it is now the path the setup
  recommends.
- The parser's `directly_unblocked_children` / `--unblocked-by` and their tests serve the Outlook
  comment, which the suite no longer posts.
- `docs/agents/skill-references.md`, the ledger the validator reads, now states that no suite skill
  names a global skill.

**For the acceptance run**

- A target that is not a PHP project: a scan leaves Safety Net unfulfilled, the seed from the trace
  counts it as fulfilled once the two language-neutral tickets are closed (tried against the parser;
  ticket 08's comments). Then a Guardrails scan judges the PHP Safety Net nodes for real, so the one
  language-neutral Guardrails proposal, the secret scanner, would be filed as blocked by PHP tools that
  have no ticket. Read from the texts, not tried in a run.
- A Psalm-only target: the PHPStan levels above 0 are out of reach in a scan; no rejection of
  `phpstan-level-5` is written any more.

### Decision about the tests (2026-10-10)

Taken with the full list above in view. Carried out after the acceptance run, because fixes from that run
would touch the validator again.

1. **Parser tests and trigger-control tests: adapted.** The parser's new path; the one trigger test that
   expects the old behaviour (a seed picked up from the fixture, `structural-scan` as a candidate) is
   rewritten to what the parser does now, or deleted where nothing is left to assert.
2. **Validator: kept and cut to the two skills.** Its general checks stay — references that do not
   exist, glossary use, avoid-terms, duplication, ticket numbers in prose. The checks of the old skill
   shape go: the required sections, the contract and exemption tables, the foundational-rules check
   against two removed skills. What it reports rightly is fixed in the texts or the glossary.
3. **`scripts/drift_check.py`: deleted.** Not run in CI; the parser's tests cover it.
4. **Fixture harness: the agent tiers and the fixtures' old state are removed; the PHP sample projects
   stay.** A harness for the rebuilt suite is work of its own after 0.7.0, once the acceptance run has
   shown what is worth asserting.

Order: acceptance first, then the four points, then the pull request.
