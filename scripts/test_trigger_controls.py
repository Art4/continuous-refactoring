"""Deterministic negative controls for the tooling-tree parser.

Each case is a target the suite must not propose tooling for, checked at the
signal the run reads: the parser's `workable` per Track. Whether a run then
stops, asks or moves on is the skill texts' matter and is observed in a real
target, not here.
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

LANGUAGE_NEUTRAL = {"ci-runner", "editorconfig"}


def make_target(*, onboarded: bool) -> tuple[tempfile.TemporaryDirectory, pathlib.Path]:
    tmp = tempfile.TemporaryDirectory()
    root = pathlib.Path(tmp.name)
    (root / ".git").mkdir()
    if onboarded:
        tracker = root / "docs" / "agents" / "issue-tracker.md"
        tracker.parent.mkdir(parents=True)
        tracker.write_text("# Issue tracker\n\n## Refactoring operations\n")
    return tmp, root


def workable(root: pathlib.Path, seed: dict | None = None) -> set[str]:
    full = {"fulfilled": [], "rejected": {}, "packs": None, "not_applicable": [], "runtime": {}}
    full.update(seed or {})
    out = tooling_tree.compute(root, tooling_tree.load_model(), full)
    return {s for track in out["tracks"].values() for s in track["workable"]}


class NotOnboardedTests(unittest.TestCase):
    """A target whose tracker file lacks the `## Refactoring operations`
    section gets no ticket at all: everything waits behind
    `onboarding-setup`, which the parser settles itself."""

    def test_nothing_is_proposed(self):
        tmp, root = make_target(onboarded=False)
        self.addCleanup(tmp.cleanup)
        self.assertEqual(workable(root), set())
        self.assertEqual(workable(root, {"packs": ["generic"]}), set())


class PacksThatDoNotApplyTests(unittest.TestCase):
    """The agent judges which Packs apply. A target judged not to be a PHP
    project is offered the language-neutral Stages and nothing of the PHP Pack."""

    def test_target_judged_not_to_be_a_php_project(self):
        tmp, root = make_target(onboarded=True)
        self.addCleanup(tmp.cleanup)
        self.assertEqual(workable(root, {"packs": ["generic"]}), LANGUAGE_NEUTRAL)

    def test_a_php_project_is_offered_composer_besides(self):
        tmp, root = make_target(onboarded=True)
        self.addCleanup(tmp.cleanup)
        self.assertEqual(workable(root, {"packs": ["generic", "php"]}), LANGUAGE_NEUTRAL | {"composer"})

    def test_without_a_judgement_every_pack_applies(self):
        tmp, root = make_target(onboarded=True)
        self.addCleanup(tmp.cleanup)
        self.assertEqual(workable(root), LANGUAGE_NEUTRAL | {"composer"})


class NothingBelowTheSafetyNetTests(unittest.TestCase):
    """Guardrails Stages are not workable while the Safety Net is open."""

    def test_secret_detection_waits(self):
        tmp, root = make_target(onboarded=True)
        self.addCleanup(tmp.cleanup)
        self.assertNotIn("secret-detection", workable(root, {"packs": ["generic"]}))
        self.assertIn(
            "secret-detection",
            workable(root, {"packs": ["generic"], "fulfilled": ["ci-runner", "editorconfig"]}),
        )


if __name__ == "__main__":
    unittest.main()
