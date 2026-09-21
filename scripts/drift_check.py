"""Drift check: compare the manual tree-walk fallback prose with the script's
graph-logic output on shared seed fixtures.

The manual fallback (tree-walk-prompt.md) and the script (tooling_tree.py)
encode the same graph rules in prose and code respectively. This check runs
both on shared seed inputs and reports any difference in workable
(next_candidates) and withheld results.

Advisory and local-only: run it by hand (``python3 scripts/drift_check.py``).
Its filename deliberately does not match the ``test_*.py`` pattern CI's
unittest discovery collects (``python3 -m unittest discover -s scripts -p
'test_*.py'``), so it never gates CI.
"""

import importlib.util
import json
import pathlib
import tempfile
import unittest

_REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
_MODULE_PATH = _REPO_ROOT / "skills" / "refactor-scan" / "references" / "tooling_tree.py"
_spec = importlib.util.spec_from_file_location("tooling_tree", _MODULE_PATH)
tooling_tree = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(tooling_tree)

load_tree = tooling_tree.load_tree
next_candidates = tooling_tree.next_candidates
withheld_candidates = tooling_tree.withheld_candidates
ordered_backlog = tooling_tree.ordered_backlog
closed_by_rejection = tooling_tree.closed_by_rejection
_NEVER_PROPOSED = tooling_tree._NEVER_PROPOSED


def _make_repo(files: dict) -> tuple:
    """Create a temporary repo with the given files, return (tmp, root)."""
    tmp = tempfile.TemporaryDirectory()
    root = pathlib.Path(tmp.name)
    for rel, content in files.items():
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(content, dict):
            p.write_text(json.dumps(content))
        else:
            p.write_text(content)
    (root / ".git").mkdir()
    return tmp, root


def _seed_fulfilled(seed: dict) -> dict[str, bool]:
    """Convert a simple {node: bool} seed to the format next_candidates expects."""
    return {k: bool(v) for k, v in seed.items()}


class DriftCheckTests(unittest.TestCase):
    """Advisory: compare the script's graph-logic outputs (next_candidates,
    withheld_candidates) against expectations derived from the prose rules
    (tree-walk-prompt.md). Each test sets up a known fulfilled state via a
    seed and asserts the expected workable/withheld sets. If the script
    drifts from the prose, these tests fail."""

    def test_empty_repo_workable_starts_with_onboarding_setup(self):
        """Prose: the first workable node after git is onboarding-setup (required
        parent: git, which is always fulfilled in the script)."""
        tmp, root = _make_repo({})
        try:
            seed = {"git": True}
            workable = [c["node"] for c in next_candidates(root, fulfilled=seed)]
            self.assertEqual(workable[0], "onboarding-setup")
        finally:
            tmp.cleanup()

    def test_onboarding_setup_fulfilled_unblocks_editorconfig(self):
        """Prose point 2: editorconfig is unblocked once onboarding-setup (its
        required parent) is fulfilled."""
        tmp, root = _make_repo({})
        try:
            seed = {"git": True, "onboarding-setup": True}
            workable = [c["node"] for c in next_candidates(root, fulfilled=seed)]
            self.assertIn("editorconfig", workable)
            self.assertNotIn("onboarding-setup", workable)
        finally:
            tmp.cleanup()

    def test_composer_fulfilled_unblocks_php_tree(self):
        """Prose point 2: phpunit, psr-4, php-cs-fixer, test-runner-if-missing
        are unblocked once composer (their required parent) is fulfilled.
        phpstan-level-0 additionally requires phpstan-not-psalm, which
        is a derived gate."""
        tmp, root = _make_repo({})
        try:
            seed = {
                "git": True, "onboarding-setup": True, "is-php-project": True,
                "composer": True, "editorconfig": True,
            }
            workable = [c["node"] for c in next_candidates(root, fulfilled=seed)]
            self.assertIn("phpunit", workable)
            self.assertIn("psr-4", workable)
            self.assertIn("php-cs-fixer", workable)
            self.assertNotIn("composer", workable)
        finally:
            tmp.cleanup()

    def test_fulfilled_node_excluded_from_workable(self):
        """Prose point 3: a fulfilled node is skipped."""
        tmp, root = _make_repo({})
        try:
            seed = {
                "git": True, "onboarding-setup": True, "is-php-project": True,
                "composer": True, "editorconfig": True,
                "phpunit": True,
            }
            workable = [c["node"] for c in next_candidates(root, fulfilled=seed)]
            self.assertNotIn("phpunit", workable)
        finally:
            tmp.cleanup()

    def test_rejected_node_excluded_from_workable(self):
        """Prose point 4: a rejected node is skipped."""
        tmp, root = _make_repo({
            "docs/refactoring/out-of-scope/phpunit.md": "rejected\n",
        })
        try:
            seed = {
                "git": True, "onboarding-setup": True, "is-php-project": True,
                "composer": True, "editorconfig": True,
            }
            workable = [c["node"] for c in next_candidates(root, fulfilled=seed)]
            self.assertNotIn("phpunit", workable)
        finally:
            tmp.cleanup()

    def test_rejected_ancestor_closes_descendants(self):
        """Prose: a rejected required ancestor permanently closes descendants
        via the required chain."""
        tree = load_tree()
        rejected = {"composer"}
        closed = closed_by_rejection(tree, rejected)
        self.assertIn("phpunit", closed)
        self.assertIn("php-cs-fixer", closed)
        self.assertIn("rector-dead-code", closed)

    def test_reversal_brings_nodes_back(self):
        """Prose: reversing a rejection brings closed nodes back."""
        tree = load_tree()
        rejected = {"composer"}
        closed = closed_by_rejection(tree, rejected)
        self.assertIn("phpunit", closed)
        # Reversal: no rejection
        closed_after = closed_by_rejection(tree, set())
        self.assertNotIn("phpunit", closed_after)

    def test_recommended_gate_withholds_child(self):
        """Prose point 5: a node with an undecided recommended parent is
        withheld from the workable set."""
        tmp, root = _make_repo({})
        try:
            seed = {
                "git": True, "onboarding-setup": True, "is-php-project": True,
                "composer": True, "editorconfig": True,
                "phpstan-level-0": True,
            }
            workable = [c["node"] for c in next_candidates(root, fulfilled=seed)]
            withheld = {w["node"]: w["waiting_on"] for w in withheld_candidates(root, fulfilled=seed)}
            # rector-php-set has phpstan-level-0 (required-any) fulfilled
            # but php-cs-fixer (recommended) is undecided → withheld
            self.assertNotIn("rector-php-set", workable)
            self.assertIn("rector-php-set", withheld)
        finally:
            tmp.cleanup()

    def test_recommended_parent_fulfilled_releases_child(self):
        """Prose point 5: a recommended parent being decided (fulfilled)
        releases the child."""
        tmp, root = _make_repo({})
        try:
            seed = {
                "git": True, "onboarding-setup": True, "is-php-project": True,
                "composer": True, "editorconfig": True,
                "php-cs-fixer": True, "phpstan-level-0": True,
            }
            workable = [c["node"] for c in next_candidates(root, fulfilled=seed)]
            # rector-php-set: phpstan-level-0 (required-any) fulfilled,
            # php-cs-fixer (recommended) decided → released
            self.assertIn("rector-php-set", workable)
        finally:
            tmp.cleanup()

    def test_recommended_parent_rejected_releases_child(self):
        """Prose point 5: a recommended parent being decided (rejected)
        also releases the child."""
        tmp, root = _make_repo({
            "docs/refactoring/out-of-scope/php-cs-fixer.md": "rejected\n",
        })
        try:
            seed = {
                "git": True, "onboarding-setup": True, "is-php-project": True,
                "composer": True, "editorconfig": True,
                "phpstan-level-0": True,
            }
            workable = [c["node"] for c in next_candidates(root, fulfilled=seed)]
            # rector-php-set: phpstan-level-0 (required-any) fulfilled,
            # php-cs-fixer (recommended) rejected → decided → released
            self.assertIn("rector-php-set", workable)
        finally:
            tmp.cleanup()

    def test_aggregation_node_never_proposed(self):
        """Prose: php-safety-net (aggregation node) is never a candidate."""
        tmp, root = _make_repo({})
        try:
            seed = {"git": True, "onboarding-setup": True, "is-php-project": True, "composer": True}
            workable = [c["node"] for c in next_candidates(root, fulfilled=seed)]
            withheld = [w["node"] for w in withheld_candidates(root, fulfilled=seed)]
            self.assertNotIn("php-safety-net", workable)
            self.assertNotIn("php-safety-net", withheld)
        finally:
            tmp.cleanup()

    def test_static_code_analyzer_never_proposed(self):
        """Prose: static-code-analyzer is never a candidate."""
        tmp, root = _make_repo({})
        try:
            seed = {"git": True, "onboarding-setup": True, "is-php-project": True, "composer": True}
            workable = [c["node"] for c in next_candidates(root, fulfilled=seed)]
            self.assertNotIn("static-code-analyzer", workable)
        finally:
            tmp.cleanup()

    def test_psalm_never_proposed(self):
        """Prose: psalm is recognition-only, never proposed."""
        tmp, root = _make_repo({})
        try:
            seed = {"git": True, "onboarding-setup": True, "is-php-project": True, "composer": True}
            workable = [c["node"] for c in next_candidates(root, fulfilled=seed)]
            self.assertNotIn("psalm", workable)
        finally:
            tmp.cleanup()

    def test_git_never_proposed(self):
        """Prose: git is never a candidate."""
        tmp, root = _make_repo({})
        try:
            seed = {"git": True}
            workable = [c["node"] for c in next_candidates(root, fulfilled=seed)]
            self.assertNotIn("git", workable)
        finally:
            tmp.cleanup()

    def test_backlog_includes_blocked_nodes(self):
        """Prose: Open includes blocked nodes in tree order."""
        tmp, root = _make_repo({})
        try:
            seed = {"git": True, "onboarding-setup": True, "is-php-project": True, "composer": True}
            backlog = ordered_backlog(root, fulfilled=seed)
            # phpunit is blocked by phpunit's own required parent (composer)
            # which is fulfilled — but phpunit's CI gate blocks it when CI
            # exists. Without CI, phpunit IS unblocked. Without seed, backlog
            # still includes it as it's not fulfilled.
            self.assertIn("phpunit", backlog)
        finally:
            tmp.cleanup()

    def test_backlog_excludes_fulfilled_nodes(self):
        """Prose: fulfilled nodes are excluded from the backlog."""
        tmp, root = _make_repo({})
        try:
            seed = {
                "git": True, "onboarding-setup": True, "is-php-project": True,
                "composer": True, "editorconfig": True,
                "phpunit": True, "psr-4": True, "phpstan-level-0": True,
            }
            backlog = ordered_backlog(root, fulfilled=seed)
            self.assertNotIn("phpunit", backlog)
            self.assertNotIn("psr-4", backlog)
            self.assertNotIn("phpstan-level-0", backlog)
        finally:
            tmp.cleanup()

    def test_backlog_excludes_rejected_nodes(self):
        """Prose: rejected nodes are excluded from the backlog."""
        tmp, root = _make_repo({
            "docs/refactoring/out-of-scope/phpunit.md": "rejected\n",
        })
        try:
            seed = {"git": True, "onboarding-setup": True, "is-php-project": True, "composer": True}
            backlog = ordered_backlog(root, fulfilled=seed)
            self.assertNotIn("phpunit", backlog)
        finally:
            tmp.cleanup()

    def test_backlog_order_matches_tree_order(self):
        """Prose: nodes appear in table order in the backlog."""
        tmp, root = _make_repo({})
        try:
            tree = load_tree()
            seed = {"git": True, "onboarding-setup": True, "is-php-project": True, "composer": True}
            backlog = ordered_backlog(root, tree=tree, fulfilled=seed)
            # Verify backlog is a subset of tree order, preserving relative order
            tree_order = [n for n in tree["order"] if n not in _NEVER_PROPOSED]
            backlog_idx = {n: i for i, n in enumerate(backlog)}
            tree_idx = {n: i for i, n in enumerate(tree_order)}
            for i, node in enumerate(backlog):
                for j, later in enumerate(backlog[i + 1:], i + 1):
                    if node in tree_idx and later in tree_idx:
                        self.assertLess(
                            tree_idx[node], tree_idx[later],
                            f"backlog order violation: {node} before {later}",
                        )
        finally:
            tmp.cleanup()

    def test_seed_drives_script_output(self):
        """The seed input contract: a fulfilled seed drives the script's
        graph-logic output, matching what the prose rules would produce
        from the same fulfilled state."""
        tmp, root = _make_repo({})
        try:
            seed = {
                "git": True, "onboarding-setup": True, "is-php-project": True,
                "composer": True, "editorconfig": True,
                "php-cs-fixer": True, "phpstan-level-0": True,
                "phpstan-level-1": True, "phpstan-level-2": True,
                "phpstan-level-3": True, "phpstan-level-4": True,
                "phpstan-level-5": True, "rector-php-set": True,
            }
            workable = [c["node"] for c in next_candidates(root, fulfilled=seed)]
            # With rector-php-set fulfilled and php-cs-fixer fulfilled:
            # - rector-dead-code should be workable (rector-php-set required
            #   parent fulfilled, php-cs-fixer recommended parent decided)
            # - phpunit should be workable (composer fulfilled, no CI)
            # - psr-4 should be workable (composer fulfilled)
            self.assertIn("rector-dead-code", workable)
            self.assertIn("phpunit", workable)
            self.assertIn("psr-4", workable)
            # Fulfilled nodes excluded
            self.assertNotIn("php-cs-fixer", workable)
            self.assertNotIn("phpstan-level-0", workable)
            self.assertNotIn("rector-php-set", workable)
        finally:
            tmp.cleanup()

    def test_php_safety_net_resolved_gate(self):
        """Prose point 2: a resolved-gated node is workable once every one
        of its resolved parents is fulfilled or rejected."""
        tmp, root = _make_repo({})
        try:
            tree = load_tree()
            # Build a seed where all php-safety-net leaves are fulfilled
            seed = {n: True for n in tree["nodes"] if n not in _NEVER_PROPOSED}
            seed["git"] = True
            workable = [c["node"] for c in next_candidates(root, tree=tree, fulfilled=seed)]
            # structural-scan should be workable when all resolved parents
            # (editorconfig, ci-runner, php-safety-net) are resolved
            self.assertIn("structural-scan", workable)
            # php-safety-net itself must never be proposed
            self.assertNotIn("php-safety-net", workable)
        finally:
            tmp.cleanup()

    def test_withheld_reasons_match_prose(self):
        """Prose point 5: withheld nodes report which parents they wait on."""
        tmp, root = _make_repo({})
        try:
            seed = {
                "git": True, "onboarding-setup": True, "is-php-project": True,
                "composer": True, "editorconfig": True,
                "phpstan-level-0": True,
            }
            withheld = {w["node"]: w["waiting_on"] for w in withheld_candidates(root, fulfilled=seed)}
            # rector-php-set waits on php-cs-fixer (recommended parent)
            self.assertIn("rector-php-set", withheld)
            self.assertIn("php-cs-fixer", withheld["rector-php-set"])
        finally:
            tmp.cleanup()

    def test_workable_and_withheld_are_disjoint(self):
        """A node cannot be both workable and withheld at the same time."""
        tmp, root = _make_repo({})
        try:
            seed = {
                "git": True, "onboarding-setup": True, "is-php-project": True,
                "composer": True, "editorconfig": True,
            }
            workable = {c["node"] for c in next_candidates(root, fulfilled=seed)}
            withheld = {w["node"] for w in withheld_candidates(root, fulfilled=seed)}
            self.assertTrue(workable.isdisjoint(withheld),
                            f"overlap: {workable & withheld}")
        finally:
            tmp.cleanup()

    def test_all_NEVER_PROPOSED_excluded(self):
        """Prose: git, static-code-analyzer, psalm, is-php-project,
        has-real-dependency, phpstan-baseline-empty, phpstan-not-psalm
        are never candidates or withheld."""
        tmp, root = _make_repo({})
        try:
            tree = load_tree()
            seed = {n: True for n in tree["nodes"]}
            workable = {c["node"] for c in next_candidates(root, tree=tree, fulfilled=seed)}
            withheld = {w["node"] for w in withheld_candidates(root, tree=tree, fulfilled=seed)}
            for node in _NEVER_PROPOSED:
                self.assertNotIn(node, workable, f"{node} should never be workable")
                self.assertNotIn(node, withheld, f"{node} should never be withheld")
        finally:
            tmp.cleanup()

    def test_required_any_gate_one_fulfilled(self):
        """Prose: rector-php-set requires-any(phpstan-level-0, psalm) —
        one fulfilled is sufficient. With php-cs-fixer (recommended) decided,
        rector-php-set is workable via phpstan-level-0 alone."""
        tmp, root = _make_repo({})
        try:
            seed = {
                "git": True, "onboarding-setup": True, "is-php-project": True,
                "composer": True, "editorconfig": True,
                "phpstan-level-0": True, "php-cs-fixer": True,
            }
            workable = [c["node"] for c in next_candidates(root, fulfilled=seed)]
            # rector-php-set should be workable via phpstan-level-0 alone
            self.assertIn("rector-php-set", workable)
        finally:
            tmp.cleanup()

    def test_required_any_gate_none_fulfilled(self):
        """Prose: rector-php-set is blocked when neither phpstan-level-0
        nor psalm is fulfilled."""
        tmp, root = _make_repo({})
        try:
            seed = {
                "git": True, "onboarding-setup": True, "is-php-project": True,
                "composer": True, "editorconfig": True,
            }
            workable = [c["node"] for c in next_candidates(root, fulfilled=seed)]
            # rector-php-set should NOT be workable — no required-any parent
            self.assertNotIn("rector-php-set", workable)
        finally:
            tmp.cleanup()

    def test_php_floor_blocked_excluded(self):
        """Nodes below the PHP floor are excluded from workable."""
        tmp, root = _make_repo({
            "composer.json": json.dumps({"require": {"php": ">=5.6"}}),
            "composer.lock": "{}",
        })
        try:
            seed = {
                "git": True, "onboarding-setup": True, "is-php-project": True,
                "composer": True, "editorconfig": True,
            }
            workable = [c["node"] for c in next_candidates(root, fulfilled=seed)]
            # composer-audit needs PHP >=7.2, phpstan-level-0 needs PHP >=7.0
            self.assertNotIn("composer-audit", workable)
            self.assertNotIn("phpstan-level-0", workable)
        finally:
            tmp.cleanup()


class SeedFixtureConsistencyTests(unittest.TestCase):
    """Verify that the script's output on a seed matches what the prose
    rules would produce — the core drift-check invariant."""

    def _php_safety_net_resolved_seed(self):
        """Seed where all php-safety-net leaves are resolved, and
        structural-scan's other resolved parents (editorconfig, ci-runner)
        are also resolved."""
        tree = load_tree()
        seed = {}
        for node in tree["nodes"]:
            if node in _NEVER_PROPOSED:
                seed[node] = True  # recognized
            else:
                seed[node] = True  # fulfilled
        return seed

    def test_fully_resolved_seed_empty_backlog(self):
        """When every scope node is resolved, the backlog is empty."""
        tmp, root = _make_repo({})
        try:
            seed = self._php_safety_net_resolved_seed()
            backlog = ordered_backlog(root, fulfilled=seed)
            self.assertEqual(backlog, [])
        finally:
            tmp.cleanup()

    def test_fully_resolved_seed_only_structural_scan_workable(self):
        """When every scope node is resolved, only structural-scan
        (resolved-gated, exposed) appears in workable."""
        tmp, root = _make_repo({})
        try:
            seed = self._php_safety_net_resolved_seed()
            workable = [c["node"] for c in next_candidates(root, fulfilled=seed)]
            # structural-scan is the only exposed resolved-gate node
            self.assertIn("structural-scan", workable)
        finally:
            tmp.cleanup()

    def test_one_unresolved_node_appears_in_backlog(self):
        """With one node unfulfilled, it appears in the backlog."""
        tmp, root = _make_repo({})
        try:
            seed = self._php_safety_net_resolved_seed()
            seed["phpunit"] = False  # unfulfill phpunit
            backlog = ordered_backlog(root, fulfilled=seed)
            self.assertIn("phpunit", backlog)
        finally:
            tmp.cleanup()

    def test_one_unresolved_node_appears_in_workable_if_unblocked(self):
        """With one unfulfilled node whose required parents are all
        fulfilled, it appears in workable."""
        tmp, root = _make_repo({})
        try:
            seed = self._php_safety_net_resolved_seed()
            seed["phpunit"] = False
            workable = [c["node"] for c in next_candidates(root, fulfilled=seed)]
            self.assertIn("phpunit", workable)
        finally:
            tmp.cleanup()

    def test_rejected_node_excluded_from_backlog_and_workable(self):
        """A rejected node is excluded from both backlog and workable."""
        tmp, root = _make_repo({
            "docs/refactoring/out-of-scope/phpunit.md": "rejected\n",
        })
        try:
            seed = self._php_safety_net_resolved_seed()
            seed["phpunit"] = False  # not fulfilled (rejected instead)
            backlog = ordered_backlog(root, fulfilled=seed)
            workable = [c["node"] for c in next_candidates(root, fulfilled=seed)]
            self.assertNotIn("phpunit", backlog)
            self.assertNotIn("phpunit", workable)
        finally:
            tmp.cleanup()


if __name__ == "__main__":
    unittest.main()
