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
