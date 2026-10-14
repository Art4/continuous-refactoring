"""Deterministic negative controls for the tooling-tree parser.

Each case is a target the suite must not propose tooling for, checked at the
signal the run reads: the parser's `next` for a seedless call. Whether a run
then stops, asks or moves on is the skill texts' matter and is observed in a
real target, not here.
"""

import importlib.util
import pathlib
import tempfile
import unittest

_REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
_MODULE_PATH = _REPO_ROOT / "skills" / "continuous-refactoring" / "references" / "tooling_tree.py"
_spec = importlib.util.spec_from_file_location("tooling_tree", _MODULE_PATH)
tooling_tree = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(tooling_tree)

next_candidates = tooling_tree.next_candidates

LANGUAGE_NEUTRAL = {"ci-runner", "editorconfig"}


def make_target(*, composer: bool, onboarded: bool) -> tuple[tempfile.TemporaryDirectory, pathlib.Path]:
    tmp = tempfile.TemporaryDirectory()
    root = pathlib.Path(tmp.name)
    (root / ".git").mkdir()
    if composer:
        (root / "composer.json").write_text("{}")
    else:
        (root / "package.json").write_text('{"name": "not-php"}')
    if onboarded:
        tracker = root / "docs" / "agents" / "issue-tracker.md"
        tracker.parent.mkdir(parents=True)
        tracker.write_text("# Issue tracker\n\n## Refactoring operations\n")
    return tmp, root


class NotOnboardedTests(unittest.TestCase):
    """A target whose tracker file lacks the `## Refactoring operations`
    section gets no candidate at all: everything waits behind
    `onboarding-setup`, which the parser settles itself."""

    def test_nothing_is_proposed(self):
        tmp, root = make_target(composer=True, onboarded=False)
        self.addCleanup(tmp.cleanup)
        self.assertEqual(next_candidates(root), [])


class UndecidedPhpProjectTests(unittest.TestCase):
    """With no node handed in, nothing below the PHP recognition gate is
    proposed — not for a PHP project nobody judged yet, and not for a target
    that is no PHP project."""

    def _proposed(self, *, composer: bool) -> set[str]:
        tmp, root = make_target(composer=composer, onboarded=True)
        self.addCleanup(tmp.cleanup)
        return {c["node"] for c in next_candidates(root)}

    def test_php_project_nobody_judged(self):
        self.assertEqual(self._proposed(composer=True), LANGUAGE_NEUTRAL)

    def test_target_that_is_no_php_project(self):
        self.assertEqual(self._proposed(composer=False), LANGUAGE_NEUTRAL)


if __name__ == "__main__":
    unittest.main()
