"""Tests for scripts/check_changelog_fragment.py.

Run: python3 -m unittest discover -s scripts -p 'test_*.py'
"""

import unittest

import check_changelog_fragment as ccf


class RequiresFragmentTests(unittest.TestCase):
    def test_skills_path_requires_fragment(self):
        self.assertTrue(ccf.requires_fragment(["skills/refactor-scan/SKILL.md"]))

    def test_docs_path_requires_fragment(self):
        self.assertTrue(ccf.requires_fragment(["docs/FAQ.md"]))

    def test_docs_adr_path_is_exempt(self):
        self.assertFalse(
            ccf.requires_fragment(["docs/adr/0038-some-decision.md"])
        )

    def test_readme_requires_fragment(self):
        self.assertTrue(ccf.requires_fragment(["README.md"]))

    def test_contributing_requires_fragment(self):
        self.assertTrue(ccf.requires_fragment(["CONTRIBUTING.md"]))

    def test_agents_md_does_not_require_fragment(self):
        # Settled design: AGENTS.md itself was not put on the trigger list.
        self.assertFalse(ccf.requires_fragment(["AGENTS.md"]))

    def test_unrelated_paths_do_not_require_fragment(self):
        self.assertFalse(
            ccf.requires_fragment(
                [
                    ".scratch/docs/issues/02-x.md",
                    "scripts/validate_skills.py",
                    "fixtures/php/php-p0-nonempty/expected/x.md",
                    ".github/workflows/skills-validation.yml",
                ]
            )
        )

    def test_one_trigger_path_among_many_is_enough(self):
        self.assertTrue(
            ccf.requires_fragment(
                ["docs/adr/0038-some-decision.md", "docs/FAQ.md", ".scratch/x.md"]
            )
        )

    def test_no_changed_files(self):
        self.assertFalse(ccf.requires_fragment([]))


class HasFragmentTests(unittest.TestCase):
    def test_detects_fragment_file(self):
        self.assertTrue(ccf.has_fragment([".changelog.d/60-changelog-mechanism.md"]))

    def test_false_when_absent(self):
        self.assertFalse(ccf.has_fragment(["docs/FAQ.md", "README.md"]))

    def test_ignores_non_markdown_in_fragment_dir(self):
        self.assertFalse(ccf.has_fragment([".changelog.d/.gitkeep"]))


class CheckTests(unittest.TestCase):
    def test_passes_when_no_trigger_path_touched(self):
        self.assertIsNone(ccf.check([".scratch/x.md"], labels=[]))

    def test_passes_when_fragment_present(self):
        self.assertIsNone(
            ccf.check(
                ["docs/FAQ.md", ".changelog.d/59-faq-section.md"], labels=[]
            )
        )

    def test_fails_when_fragment_missing(self):
        message = ccf.check(["docs/FAQ.md"], labels=[])
        self.assertIsNotNone(message)
        self.assertIn("changelog", message.lower())

    def test_passes_with_no_changelog_label(self):
        self.assertIsNone(
            ccf.check(["docs/FAQ.md"], labels=["no-changelog"])
        )

    def test_unrelated_label_does_not_excuse_missing_fragment(self):
        self.assertIsNotNone(
            ccf.check(["docs/FAQ.md"], labels=["needs-triage"])
        )


if __name__ == "__main__":
    unittest.main()
