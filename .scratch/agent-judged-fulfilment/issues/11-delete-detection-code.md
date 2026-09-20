# 11: Delete the detection code

Spec: `agent-judged-fulfilment`.

**What to build:** The contract step of the expand–contract sequence. With no caller left, the parser's detection functions and their helper predicates, the default that ran detection when no seed was given, and the tests that exercised them are removed. What remains is the graph logic, the PHP-floor precheck and version-reversal findings, and the outlook view. Documentation that still describes the parser as a detector is corrected, and the earlier decision that shipped the parser with detection is marked as replaced by the new ADR.

**Blocked by:** 10 (Drift check and a detection-free test suite).

**Status:** implemented — PR #113, open items listed in Comments

- [x] Every detection function and helper predicate is removed, along with the tests that only exercised them; shared helpers used by the PHP-floor logic stay.
- [x] The script no longer runs detection when no seed is given: scan passes require the seed, other passes derive state from the bookkeeping.
- [ ] No skill, reference, harness script or documentation still refers to a removed function, output field or detection behavior.
- [ ] The earlier decision record is marked as replaced by the new ADR and the new ADR reads consistently with the final state.
- [x] The full deterministic test suite and the static validation tiers pass in CI.

## Comments

**PR:** [#113](https://github.com/Art4/continuous-refactoring/pull/113)

- Item 1: `detect_nodes()` and every `_has_*`/CI-needle/`_detected_secret_scanner` helper are gone
  (`54105f5`); the PHP-floor helpers (`_read_composer`, `_parse_min_version`, `_current_php_floor`,
  `_out_of_scope_blocked_by_php`, `_resolve_refactoring_notes_dir`) remain. Item 2: `_resolve_fulfilled`
  returns `{}` when there is neither seed nor Track-section state (no detection fallback). Left over in the
  script, not blocking: the entry point is still named `detect_and_roadmap` with an unused `steps`
  parameter, and the JSON still has a `detected` map whose `reason`/`details` are always empty.
- Item 5: `python3 -m unittest discover -s scripts -p 'test_*.py'` (220 tests), `validate_skills.py` and
  `bash -n fixtures/harness/run.sh` pass locally; on PR #113 Tier 1, Tier 2, Tier 4, `validate` and `check`
  all pass.
- Item 3 not met, live text still describes parser detection or points at removed output:
  - `skills/refactor-scan/references/safety-net-track.md` and `guardrails-track.md`, "Judging fulfilment":
    "Run `tooling_tree.py` once ... its `detected` map is a first signal", "The parser's own signal still
    counts", "the parser reports `fulfilled: false`", the Pint and `composer-audit` examples.
  - `skills/refactor-scan/SKILL.md` step 4: "**Not** `roadmap`"; steps 4b/4c read the `detected` map.
  - `php-tooling-tree/psalm.md` and `php-tooling-tree/php-safety-net.md`: `next_candidates()`/`roadmap()`;
    `php-tooling-tree/phpstan.md`: "the parser treats them as blocked by equivalence";
    `tree-walk-prompt.md`: "rather than trusting a parser's raw dependency-name match".
  - `fixtures/harness/run.sh` comment above `run_safety_net_track` (parser's dependency-name match),
    `scripts/test_tooling_tree.py` and `scripts/test_trigger_controls.py` docstrings, the `--seed` help text
    ("instead of detection").
- Item 4 not met: ADR-0014 (`0014-tooling-tree-parser-ships-under-refactor-scan.md`), the decision that
  shipped the parser with its docs under `refactor-scan`, carries no note that ADR-0056 replaces it. ADR-0056
  calls it "the earlier, unnumbered decision" and links nothing. ADR-0047 and ADR-0055 do carry reciprocal
  "Amended by ADR-0056" notes. Apart from that, ADR-0056 reads consistently with the final state.
