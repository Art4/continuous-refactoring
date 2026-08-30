"""Tier 4 — deterministic negative controls (ticket 27).

These are the slice of Tier 4's "trigger tests incl. negative controls" that
can be verified without an LLM: the ground-truth *signal* each negative
control ultimately depends on. Two of the three controls in ticket 27's plan
are themselves prose-level judgment calls a skill makes, not something the
deterministic parser decides:

- "orchestrator without git must not run" — `refactor-scan`'s own step 1
  precondition (`skills/refactor-scan/SKILL.md`); `next_candidates()`
  deliberately hardcodes ``git`` as fulfilled for downstream gating (see its
  own comment) since it assumes the precondition already passed. What *is*
  real and testable here is the detection primitive the precondition reads:
  a missing ``.git`` must be reported accurately.
- "non-PHP project gets no PHP baseline" — ADR-0008 explicitly keeps
  language recognition "an informal heuristic, not part of this ADR;
  formalizing it is premature before a second language specialization
  exists." So this module does not invent a language detector; it only
  checks the ground-truth signal (no `composer.json`, no PHP-specific
  files) an informal judgment would read.

Both of those, plus "explicit + implicit invocation per skill", are exercised
end-to-end via `fixtures/harness/run.sh tier4` (opencode-based, local/
advisory — see fixtures/README.md's "Tier 4" section, same non-CI posture as
`roadmap --opencode` and `agent-loop`).

The third control, "scan on clean repo reports clean", *is* fully
deterministic: `fixtures/php/php-clean/` is a target where every deterministic
PHP-tooling-tree leaf is fulfilled or explicitly rejected, so `next()` must
hold nothing but the perpetual `structural-scan` invitation and `withheld()`
must be empty. That is a genuine, real assertion below, not a proxy.
"""

import importlib.util
import pathlib
import tempfile
import unittest

_REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
_MODULE_PATH = _REPO_ROOT / "skills" / "refactor-scan" / "references" / "tooling_tree.py"
_spec = importlib.util.spec_from_file_location("tooling_tree", _MODULE_PATH)
tooling_tree = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(tooling_tree)

detect_nodes = tooling_tree.detect_nodes
next_candidates = tooling_tree.next_candidates
withheld_candidates = tooling_tree.withheld_candidates

PHP_CLEAN_FIXTURE = _REPO_ROOT / "fixtures" / "php" / "php-clean" / "project"


class CleanRepoReportsCleanTests(unittest.TestCase):
    """Negative control: a repo with every deterministic PHP-tooling-tree leaf
    resolved must propose nothing but `structural-scan` — no phantom tooling
    leftovers, nothing withheld."""

    def test_next_holds_only_structural_scan(self):
        self.assertEqual(
            [c["node"] for c in next_candidates(PHP_CLEAN_FIXTURE)],
            ["structural-scan"],
        )

    def test_nothing_withheld(self):
        self.assertEqual(withheld_candidates(PHP_CLEAN_FIXTURE), [])

    def test_structural_scan_gate_open_for_the_resolved_reason(self):
        detected = detect_nodes(PHP_CLEAN_FIXTURE)
        self.assertTrue(detected["structural-scan"]["fulfilled"])
        self.assertEqual(detected["structural-scan"]["details"]["unresolved"], [])
        # The three phpstan levels above this target's declared ceiling are
        # rejected (docs/refactoring/out-of-scope/), not fulfilled — a
        # `resolved` parent counts either way (ADR-0008).
        self.assertEqual(
            sorted(detected["structural-scan"]["details"]["rejected"]),
            ["phpstan-level-1", "phpstan-level-2", "phpstan-level-3"],
        )


class GitPreconditionSignalTests(unittest.TestCase):
    """`refactor-scan` step 1 stops the pass on a missing `.git` before it
    ever calls into this parser (`skills/refactor-scan/SKILL.md`). This only
    checks that the signal that precondition reads is accurate — the
    behavioral half (does the skill actually stop) is exercised by
    `fixtures/harness/run.sh tier4`, not here."""

    def test_missing_git_is_reported_unfulfilled(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            (root / "composer.json").write_text("{}")
            detected = detect_nodes(root)
            self.assertFalse(detected["git"]["fulfilled"])
            self.assertEqual(detected["git"]["reason"], "no .git")

    def test_present_git_is_reported_fulfilled(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            (root / ".git").mkdir()
            detected = detect_nodes(root)
            self.assertTrue(detected["git"]["fulfilled"])


class NonPhpProjectSignalTests(unittest.TestCase):
    """ADR-0008 keeps "is this even a PHP project" an informal, skill-level
    judgment on purpose — this only checks the ground-truth signal that
    judgment would read: a repo with no `composer.json` and no PHP-specific
    marker files reports every PHP-tree leaf below `composer` unfulfilled, so
    nothing past the generic root is deterministically proposable."""

    def test_no_composer_json_leaves_php_tree_unfulfilled(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            (root / ".git").mkdir()
            (root / "package.json").write_text('{"name": "not-php"}')
            detected = detect_nodes(root)
            self.assertFalse(detected["composer"]["fulfilled"])
            for node in ("php-cs-fixer", "phpunit", "phpstan-level-0-baseline"):
                self.assertFalse(detected[node]["fulfilled"])

    def test_next_never_proposes_a_php_leaf_before_composer(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            (root / ".git").mkdir()
            (root / "package.json").write_text('{"name": "not-php"}')
            proposed = {c["node"] for c in next_candidates(root)}
            # Only the generic-root nodes composer/ci-runner (both required
            # parent: loop-config) can be proposed with zero PHP signal —
            # every PHP-specific leaf is required-parent-blocked on composer.
            self.assertTrue(proposed.issubset({"loop-config", "composer", "ci-runner"}))


if __name__ == "__main__":
    unittest.main()
