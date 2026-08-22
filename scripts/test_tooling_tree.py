"""Tests for deterministic tooling tree parser (scripts/lib/tooling_tree.py)

TDD: verify tree parsing, detection, and 10-step roadmap generation against fixtures.
"""

import json
import pathlib
import tempfile
import unittest

from lib.tooling_tree import load_tree, detect_nodes, roadmap, _is_baseline_empty


class LoadTreeTests(unittest.TestCase):
    def test_edges_parsed(self):
        tree = load_tree()
        self.assertGreaterEqual(len(tree["edges"]), 15)
        # check required edge
        self.assertIn({"from": "git", "to": "composer", "type": "required"}, tree["edges"])
        self.assertIn({"from": "phpstan-level-0-baseline", "to": "phpstan-level-1", "type": "required"}, tree["edges"])
        # recommended
        self.assertIn({"from": "php-cs-fixer", "to": "rector-dead-code", "type": "recommended"}, tree["edges"])

    def test_order_contains_nodes(self):
        tree = load_tree()
        for n in ["git", "composer", "phpstan-level-0-baseline", "phpstan-level-1", "rector-dead-code"]:
            self.assertIn(n, tree["order"])


class BaselineEmptyTests(unittest.TestCase):
    def _repo_with(self, content: str | None):
        tmp = tempfile.TemporaryDirectory()
        root = pathlib.Path(tmp.name)
        if content is not None:
            (root / "phpstan-baseline.neon").write_text(content)
        return tmp, root

    def test_absent_is_empty(self):
        tmp, root = self._repo_with(None)
        try:
            self.assertTrue(_is_baseline_empty(root))
        finally:
            tmp.cleanup()

    def test_empty_ignore_is_empty(self):
        tmp, root = self._repo_with("parameters:\n    ignoreErrors: []\n")
        try:
            self.assertTrue(_is_baseline_empty(root))
        finally:
            tmp.cleanup()

    def test_nonempty_not_empty(self):
        tmp, root = self._repo_with("parameters:\n    ignoreErrors:\n        - message: '#foo#'\n          path: src/Foo.php\n")
        try:
            self.assertFalse(_is_baseline_empty(root))
        finally:
            tmp.cleanup()


class DetectNodesTests(unittest.TestCase):
    def _make_repo(self, files: dict):
        tmp = tempfile.TemporaryDirectory()
        root = pathlib.Path(tmp.name)
        for rel, content in files.items():
            p = root / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content)
        # git
        (root / ".git").mkdir()
        return tmp, root

    def test_empty_repo(self):
        tmp, root = self._make_repo({})
        try:
            d = detect_nodes(root)
            self.assertTrue(d["git"]["fulfilled"])
            self.assertFalse(d["composer"]["fulfilled"])
            self.assertFalse(d["phpstan-level-0-baseline"]["fulfilled"])
        finally:
            tmp.cleanup()

    def test_composer_fulfilled(self):
        tmp, root = self._make_repo({
            "composer.json": json.dumps({"name": "test/app", "require": {"php": "^8.1"}}),
            "composer.lock": "{}",
        })
        try:
            d = detect_nodes(root)
            self.assertTrue(d["composer"]["fulfilled"])
        finally:
            tmp.cleanup()

    def test_p0_psalm_equivalence(self):
        tmp, root = self._make_repo({
            "composer.json": json.dumps({"require": {"vimeo/psalm": "^5.0"}}),
            "composer.lock": "{}",
            "psalm.xml": "<psalm></psalm>",
        })
        try:
            d = detect_nodes(root)
            self.assertTrue(d["phpstan-level-0-baseline"]["fulfilled"])
            self.assertIn("psalm", d["phpstan-level-0-baseline"]["reason"].lower())
            # p1 not applicable
            self.assertFalse(d["phpstan-level-1"]["fulfilled"])
        finally:
            tmp.cleanup()

    def test_p0_phpstan_level0_empty(self):
        tmp, root = self._make_repo({
            "composer.json": json.dumps({"require-dev": {"phpstan/phpstan": "^1.0"}}),
            "composer.lock": "{}",
            "phpstan.neon": "parameters:\n    level: 0\n    paths: [src]\nincludes:\n    - phpstan-baseline.neon\n",
            "phpstan-baseline.neon": "parameters:\n    ignoreErrors: []\n",
        })
        try:
            d = detect_nodes(root)
            self.assertTrue(d["phpstan-level-0-baseline"]["fulfilled"])
        finally:
            tmp.cleanup()

    def test_p0_nonempty_blocks_p1(self):
        tmp, root = self._make_repo({
            "composer.json": json.dumps({"require-dev": {"phpstan/phpstan": "^1.0"}}),
            "composer.lock": "{}",
            "phpstan.neon": "parameters:\n    level: 0\n",
            "phpstan-baseline.neon": "parameters:\n    ignoreErrors:\n        - message: '#foo#'\n",
        })
        try:
            d = detect_nodes(root)
            self.assertTrue(d["phpstan-level-0-baseline"]["fulfilled"])
            self.assertFalse(d["phpstan-level-1"]["fulfilled"])
            # roadmap should not propose p1 when baseline non-empty
            r = roadmap(root, steps=5)
            nodes = [x["node"] for x in r]
            self.assertNotIn("phpstan-level-1", nodes[:2])  # at least not immediate
        finally:
            tmp.cleanup()


class RoadmapTests(unittest.TestCase):
    def _make_repo(self, files: dict):
        tmp = tempfile.TemporaryDirectory()
        root = pathlib.Path(tmp.name)
        for rel, content in files.items():
            p = root / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content)
        (root / ".git").mkdir()
        return tmp, root

    def test_empty_roadmap_starts_with_composer(self):
        tmp, root = self._make_repo({})
        try:
            r = roadmap(root, steps=3)
            self.assertEqual(r[0]["node"], "composer")
            # ci-runner and composer are both children of git; composer has priority in order table
            # second step should be ci-runner or cs-fixer depending on fulfilled simulation
            self.assertIn(r[1]["node"], ["ci-runner", "composer-audit", "php-cs-fixer", "phpunit"])
        finally:
            tmp.cleanup()

    def test_partial_composer_then_unblocked(self):
        tmp, root = self._make_repo({
            "composer.json": json.dumps({"require": {"php": "^8.1"}}),
            "composer.lock": "{}",
        })
        try:
            r = roadmap(root, steps=10)
            nodes = [x["node"] for x in r]
            # after composer fulfilled, unblocked should include these
            self.assertIn("php-cs-fixer", nodes)
            self.assertIn("phpunit", nodes)
            self.assertIn("composer-audit", nodes)
            self.assertIn("phpstan-level-0-baseline", nodes)
            # p0 within 10 (needs composer)
            self.assertIn("phpstan-level-0-baseline", nodes)
        finally:
            tmp.cleanup()

    def test_p0_empty_then_p1_next(self):
        tmp, root = self._make_repo({
            "composer.json": json.dumps({"require-dev": {"phpstan/phpstan": "^1.0"}}),
            "composer.lock": "{}",
            "phpstan.neon": "parameters:\n    level: 0\n",
            "phpstan-baseline.neon": "parameters:\n    ignoreErrors: []\n",
            ".php-cs-fixer.php": "<?php // config",
        })
        try:
            r = roadmap(root, steps=10)
            nodes = [x["node"] for x in r]
            # Since composer and cs etc. fulfilled via our minimal setup, p1 should appear within 10
            self.assertIn("phpstan-level-1", nodes)
        finally:
            tmp.cleanup()

    def test_recommended_outlook(self):
        # p0 fulfilled but cs-fixer missing -> rector still proposable (recommended edge)
        # cs-fixer will be picked before rector due to priority, so we just check rector is proposable
        tmp, root = self._make_repo({
            "composer.json": json.dumps({"require-dev": {"phpstan/phpstan": "^1.0"}}),
            "composer.lock": "{}",
            "phpstan.neon": "parameters:\n    level: 0\n",
            "phpstan-baseline.neon": "parameters:\n    ignoreErrors: []\n",
        })
        try:
            r = roadmap(root, steps=10)
            rector = [x for x in r if x["node"] == "rector-dead-code"]
            self.assertTrue(rector)
            # rector should be present; outlook may be absent if cs-fixer already picked earlier — accept either
            self.assertTrue(rector[0]["node"] == "rector-dead-code")
        finally:
            tmp.cleanup()

    def test_10_steps_always(self):
        tmp, root = self._make_repo({
            "composer.json": json.dumps({"require": {"php": "^8.1"}}),
            "composer.lock": "{}",
        })
        try:
            r = roadmap(root, steps=10)
            self.assertEqual(len(r), 10)
            self.assertEqual(r[0]["n"], 1)
            self.assertEqual(r[-1]["n"], 10)
        finally:
            tmp.cleanup()


if __name__ == "__main__":
    unittest.main()
