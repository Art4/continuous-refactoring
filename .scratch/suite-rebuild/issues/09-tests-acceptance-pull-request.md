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
