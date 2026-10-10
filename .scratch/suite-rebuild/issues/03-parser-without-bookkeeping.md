# 03: Parser without bookkeeping

**What to build:** Whoever calls the tooling-tree parser hands in which nodes are fulfilled and which are
rejected, and gets back, per Track, the nodes with their name and tool, the ordered backlog with blocked
nodes included, and the reason a node is withheld. The parser reads the tree and the target repository,
and no file the suite used to keep.

Spec: `../spec.md` (sections *The parser*, *Testing Decisions*). This is the one ticket built test-first.

**Blocked by:** None (can start immediately)

**Status:** done

- [x] The parser takes the node state (fulfilled, rejected) as input; called without it, it treats every
      node as undecided rather than looking for a file
- [x] The parser emits, per Track, each node's slug, name and tool; Track membership is derived from the
      edges as before
- [x] No code path reads a bookkeeping document, a config file, a bookkeeping pointer or the old
      out-of-scope folder; the code deriving state from them is deleted
- [x] A rejection's machine-readable blocker (minimum PHP version) is handed in with the rejected state,
      and the reversal finding is still reported when the target meets it
- [x] The `onboarding-setup` node counts as fulfilled when the target's tracker file has a
      `## Refactoring operations` section
- [x] Parser tests cover the handed-in state and the per-Track list at the parser's existing interface;
      tests of the removed derivation are deleted; the parser's own test file is green

## Comments

### Done — what the parser's interface looks like now

- **Functions** (`next_candidates`, `withheld_candidates`, `withheld_with_reasons`, `ordered_backlog`,
  `directly_unblocked_children`, `detect_and_roadmap`) take `fulfilled` (`{slug: bool}`) and `rejected` (a
  collection of slugs, or `{slug: blocker}` with blocker `None` or `{"php": "X.Y"}`).
  `php_version_reversal_findings(repo, rejected)` reads the blockers from the same mapping.
- **Command line:** `--seed <file>` with
  `{"fulfilled": [slug, ...], "rejected": {slug: null | {"php": "X.Y"}}}` (`rejected` may be a plain list).
  The old `{slug: true/false}` shape, an unknown slug, a slug in both lists and an unusable blocker exit
  with code 2. Without `--seed` every node is undecided.
- **Output:** new key `tracks`: `{"Safety Net": {...}, "Guardrails": {...}}`, each with `nodes`
  (`{node, name, tool}` in tree order), `backlog` and `withheld` (`{node, reason}`). The flat keys
  (`next`, `backlog`, `withheld`, `withheld_with_reasons`, `reversals`, `php_floor_blocked`,
  `closed_by_rejection`, `detected`, `tree`) stay.
- **`git` and `onboarding-setup` are the parser's own:** whatever is handed in for them is ignored.
  `onboarding-setup` is fulfilled exactly when `docs/agents/issue-tracker.md` has a
  `## Refactoring operations` heading.
- A node below its PHP floor now carries that reason in `withheld_with_reasons` (it was in the backlog
  with no reason before).

### Left as it was, for ticket 04 to decide

- The backlog still contains the two aggregation nodes `structural-scan` and `php-safety-net` while they
  are not handed in as fulfilled, and the caller still has to hand in their state itself (the parser does
  not compute a resolved gate from its leaves). A scan that offers a ticket per backlog node would offer
  one for each of them. Both behaviours predate this ticket.
- `tracks[...]["nodes"]` lists every node of the Track, gate and recognition nodes included (`git`,
  `is-php-project`, `php-safety-net`, ...). Names come back as written, so `php-safety-net` is
  "PHP Safety Net (internal — never proposed; ...)" and `editorconfig` is "`.editorconfig`" with backticks.

### Red afterwards, for ticket 09

Newly red through this ticket:

- `scripts/test_trigger_controls.py` — `CleanRepoReportsCleanTests.test_next_holds_only_structural_scan`:
  relied on the parser picking up `fixtures/php/php-clean/project/.scratch/refactor/fulfilled-set.json` by
  itself. CI: `skills-validation.yml` (unittest discover) and `test-harness.yml` (trigger controls).
- `scripts/drift_check.py` (not run in CI) — two more failures on top of the four it already had:
  `DriftCheckTests.test_onboarding_setup_fulfilled_unblocks_editorconfig` and
  `SeedFixtureConsistencyTests.test_fully_resolved_seed_empty_backlog` (both hand in `onboarding-setup` as
  fulfilled without a tracker file).
- `changelog-fragment.yml` — `skills/**` changed without a `.changelog.d/` fragment.

Red before this ticket, unchanged:

- `scripts/test_validate_skills.py` — `EndToEndTests.test_real_repo_passes`, and
  `python3 scripts/validate_skills.py .` itself (glossary avoid-terms in the old skill texts).
- `scripts/drift_check.py` — `DriftCheckTests.test_backlog_excludes_rejected_nodes`,
  `test_recommended_parent_rejected_releases_child`, `test_rejected_node_excluded_from_workable`,
  `SeedFixtureConsistencyTests.test_rejected_node_excluded_from_backlog_and_workable` (all four write
  rejections as `docs/refactoring/out-of-scope/*.md` files).

Not run here (needs Docker and an agent): `fixtures/harness/run.sh` tiers. Every fixture's
`.scratch/refactor/` (bookkeeping, config, `out-of-scope/`, `fulfilled-set.json`) is no longer read by
the parser, so any tier that expects parser output from them will differ.

Not red, but now untrue (texts this ticket was told not to touch): the old seed shape and the
auto-discovered seed in `skills/refactor-scan/SKILL.md`, `references/tree-walk-prompt.md`,
`references/safety-net-track.md`, `references/guardrails-track.md`,
`skills/refactor-implement/references/outlook-comment.md` and `fixtures/README.md`; the Fulfilment check
in `references/tooling-tree/onboarding-setup.md` (still the bookkeeping pointer); the `out-of-scope/`
wording in `references/php-tooling-tree.md`.
