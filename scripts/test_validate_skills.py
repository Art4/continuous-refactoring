"""Tests for the Tier 1 static suite validator (scripts/validate-skills.py).

Run: python3 -m unittest discover -s scripts -p 'test_*.py'
"""

import pathlib
import tempfile
import unittest

import validate_skills as vs


def write_tree(root, files):
    for rel, content in files.items():
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content)


class FrontmatterTests(unittest.TestCase):
    def test_valid_frontmatter(self):
        text = "---\nname: refactor-scan\ndescription: Does the scan thing.\n---\n\nbody"
        self.assertEqual(vs.frontmatter_issues(text, "refactor-scan"), [])

    def test_missing_frontmatter(self):
        text = "no frontmatter here"
        issues = vs.frontmatter_issues(text, "x")
        self.assertTrue(any("frontmatter" in i.message for i in issues))

    def test_unclosed_frontmatter(self):
        text = "---\nname: x\ndescription: y\n"
        issues = vs.frontmatter_issues(text, "x")
        self.assertTrue(any(i.level == "error" for i in issues))

    def test_name_mismatch_with_directory(self):
        text = "---\nname: other-skill\ndescription: desc\n---\n"
        issues = vs.frontmatter_issues(text, "refactor-scan")
        self.assertTrue(any("directory" in i.message for i in issues))

    def test_uppercase_name_rejected(self):
        text = "---\nname: Refactor-Scan\ndescription: desc\n---\n"
        issues = vs.frontmatter_issues(text, "refactor-scan")
        self.assertTrue(any("kebab" in i.message.lower() or "lowercase" in i.message.lower() for i in issues))

    def test_double_hyphen_rejected(self):
        text = "---\nname: refactor--scan\ndescription: desc\n---\n"
        self.assertTrue(any(i.level == "error" for i in vs.frontmatter_issues(text, "refactor-scan")))

    def test_leading_hyphen_rejected(self):
        text = "---\nname: -refactor-scan\ndescription: desc\n---\n"
        self.assertTrue(any(i.level == "error" for i in vs.frontmatter_issues(text, "refactor-scan")))

    def test_missing_description(self):
        text = "---\nname: refactor-scan\n---\n"
        issues = vs.frontmatter_issues(text, "refactor-scan")
        self.assertTrue(any("description" in i.message.lower() for i in issues))

    def test_empty_description_rejected(self):
        text = "---\nname: refactor-scan\ndescription: \"\"\n---\n"
        self.assertTrue(any("description" in i.message.lower() for i in vs.frontmatter_issues(text, "refactor-scan")))

    def test_long_description_rejected(self):
        text = f"---\nname: refactor-scan\ndescription: {'x' * 1025}\n---\n"
        self.assertTrue(any("1024" in i.message for i in vs.frontmatter_issues(text, "refactor-scan")))

    def test_unknown_field_rejected(self):
        text = "---\nname: refactor-scan\ndescription: desc\nbogus-field: true\n---\n"
        issues = vs.frontmatter_issues(text, "refactor-scan")
        self.assertTrue(any("bogus-field" in i.message for i in issues))

    def test_opencode_extensions_allowed(self):
        text = "---\nname: refactor-scan\ndescription: desc\ndisable-model-invocation: true\nallowed-tools: Read, Grep\n---\n"
        self.assertEqual(vs.frontmatter_issues(text, "refactor-scan"), [])

    def test_name_too_long(self):
        text = f"---\nname: {'a' * 65}\ndescription: desc\n---\n"
        self.assertTrue(any("64" in i.message for i in vs.frontmatter_issues(text, "a" * 65)))


class SectionTests(unittest.TestCase):
    ORCH = vs.ORCHESTRATOR

    def test_standard_skill_ok(self):
        text = "## Process\n...\n## Fallback\n...\n## Completion criterion\n..."
        self.assertEqual(vs.section_issues(text, "refactor-scan", requires_fallback=True), [])

    def test_missing_completion_criterion(self):
        text = "## Process\n..."
        issues = vs.section_issues(text, "refactor-scan", requires_fallback=False)
        self.assertTrue(any("Completion criterion" in i.message for i in issues))

    def test_missing_process(self):
        text = "## Other\n## Completion criterion\n"
        issues = vs.section_issues(text, "refactor-scan", requires_fallback=False)
        self.assertTrue(any("Process" in i.message for i in issues))

    def test_orchestrator_uses_the_pass(self):
        text = "## The pass\n## Completion criterion\n"
        self.assertEqual(vs.section_issues(text, self.ORCH, requires_fallback=False), [])

    def test_orchestrator_missing_the_pass(self):
        text = "## Process\n## Completion criterion\n"
        issues = vs.section_issues(text, self.ORCH, requires_fallback=False)
        self.assertTrue(any("The pass" in i.message for i in issues))

    def test_fallback_required(self):
        text = "## Process\n## Completion criterion\n"
        issues = vs.section_issues(text, "refactor-scan", requires_fallback=True)
        self.assertTrue(any("Fallback" in i.message for i in issues))

    def test_fallback_not_required_ok_without(self):
        text = "## Process\n## Completion criterion\n"
        self.assertEqual(vs.section_issues(text, "refactor-baseline", requires_fallback=False), [])


class LedgerTests(unittest.TestCase):
    def test_parse_ledger(self):
        ledger = vs.parse_ledger(
            "| Skill | Global ref | Role | Fallback type | Self-contained in |\n"
            "|---|---|---|---|---|\n"
            "| `refactor-scan` | `/codebase-design` (Z.31) | enrichment | crash-safe | 01 \u2713 shipped |\n"
            "| `refactor-review` | `/code-review` (Z.23) | core | self-sufficient | 04 (planned) |\n"
        )
        self.assertEqual(
            ledger["refactor-scan"], [("codebase-design", True)]
        )
        self.assertEqual(
            ledger["refactor-review"], [("code-review", False)]
        )

    def test_parse_ledger_ignores_header(self):
        ledger = vs.parse_ledger("| Skill | Global ref | Role | Fallback type | Self-contained in |\n|---|---|---|---|---|\n")
        self.assertEqual(ledger, {})


class GlobalRefTests(unittest.TestCase):
    SUITE = {"refactor-scan", "refactor-baseline", "refactor-prioritize"}

    def test_dangling_ref_not_in_ledger(self):
        text = "See `/grilling` for details."
        issues = vs.global_ref_issues(text, "refactor-scan", self.SUITE, {"refactor-scan": []})
        self.assertTrue(any("grilling" in i.message and "ledger" in i.message for i in issues))

    def test_stale_ledger_row(self):
        text = "No global refs here."
        issues = vs.global_ref_issues(text, "refactor-scan", self.SUITE, {"refactor-scan": [("grilling", True)]})
        self.assertTrue(any("stale" in i.message or "ledger" in i.message for i in issues))

    def test_suite_internal_refs_exempt(self):
        text = "Run `/refactor-scan` then `/refactor-prioritize`."
        issues = vs.global_ref_issues(text, "refactor-baseline", self.SUITE, {"refactor-baseline": []})
        self.assertEqual(issues, [])

    def test_matching_refs_ok(self):
        text = "Use `/codebase-design` vocabulary."
        issues = vs.global_ref_issues(text, "refactor-scan", self.SUITE, {"refactor-scan": [("codebase-design", True)]})
        self.assertEqual(issues, [])

    def test_shipped_row_requires_fallback_covered_by_sections(self):
        text = "Use `/tdd` when installed."
        issues = vs.global_ref_issues(text, "refactor-implement", self.SUITE, {"refactor-implement": [("tdd", True)]})
        self.assertEqual(issues, [])


class LocalRefTests(unittest.TestCase):
    def _repo(self):
        tmp = tempfile.TemporaryDirectory()
        root = pathlib.Path(tmp.name)
        write_tree(root, {
            "CONTEXT.md": "# glossary",
            "docs/agents/issue-tracker.md": "# tracker",
            "docs/adr/0002-foo.md": "# adr",
        })
        return tmp, root

    def test_existing_refs_ok(self):
        tmp, root = self._repo()
        try:
            text = "See `docs/agents/issue-tracker.md` and `CONTEXT.md` and `docs/adr/`."
            self.assertEqual(vs.local_ref_issues(text, root), [])
        finally:
            tmp.cleanup()

    def test_missing_ref_flagged(self):
        tmp, root = self._repo()
        try:
            text = "See `docs/agents/missing.md`."
            issues = vs.local_ref_issues(text, root)
            self.assertTrue(any("missing.md" in i.message for i in issues))
        finally:
            tmp.cleanup()

    def test_target_repo_artifacts_exempt(self):
        tmp, root = self._repo()
        try:
            text = "Scaffold `docs/agents/refactoring.md`; see `CODING_STANDARDS.md` or `CONTRIBUTING.md`."
            self.assertEqual(vs.local_ref_issues(text, root), [])
        finally:
            tmp.cleanup()

    def test_non_path_backticks_ignored(self):
        tmp, root = self._repo()
        try:
            text = "Run `git log --oneline`, check `composer.json`, `Makefile`, `.php-cs-fixer.php`."
            self.assertEqual(vs.local_ref_issues(text, root), [])
        finally:
            tmp.cleanup()


class AdrTests(unittest.TestCase):
    def _repo(self):
        tmp = tempfile.TemporaryDirectory()
        root = pathlib.Path(tmp.name)
        write_tree(root, {"docs/adr/0002-generic-core-php-first.md": "# 0002"})
        return tmp, root

    def test_resolvable_adr_ok(self):
        tmp, root = self._repo()
        try:
            self.assertEqual(vs.adr_issues("Per ADR-0002.", root), [])
        finally:
            tmp.cleanup()

    def test_missing_adr_flagged(self):
        tmp, root = self._repo()
        try:
            issues = vs.adr_issues("Per ADR-9999.", root)
            self.assertTrue(any("9999" in i.message for i in issues))
        finally:
            tmp.cleanup()

    def test_no_adr_refs_ok(self):
        tmp, root = self._repo()
        try:
            self.assertEqual(vs.adr_issues("No decisions here.", root), [])
        finally:
            tmp.cleanup()


class VocabTests(unittest.TestCase):
    def test_glossary_parsed(self):
        glossary = vs.parse_glossary(
            "# Lang\n"
            "**Candidate**: an opportunity\n"
            "_Avoid_: task, ticket, todo\n"
            "**Seam**: the boundary\n"
            "_Avoid_: boundary, internal hook\n"
            "**Deletion test**: x\n"
            "_Avoid_: (none \u2014 use the term as-is)\n"
        )
        self.assertEqual(glossary.terms, ["Candidate", "Seam", "Deletion test"])
        self.assertEqual(glossary.avoid, ["task", "ticket", "todo", "boundary", "internal hook"])

    def test_terms_in_use(self):
        skills = {"refactor-scan": "A **hot spot**, the **seam**, and the **deletion test**."}
        issues = vs.vocab_issues(["Hot spot", "Seam", "Deletion test"], ["boundary"], skills, set())
        self.assertEqual(issues, [])

    def test_unused_term_flagged(self):
        skills = {"refactor-scan": "no glossary words here"}
        issues = vs.vocab_issues(["Hot spot"], [], skills, set())
        self.assertTrue(any("Hot spot" in i.message for i in issues))

    def test_avoid_term_flagged(self):
        skills = {"refactor-scan": "A classic pain point to check."}
        issues = vs.vocab_issues(["Hot spot"], ["pain point"], skills, set())
        self.assertTrue(any("pain point" in i.message for i in issues))

    def test_allowlisted_use_ok(self):
        skills = {"refactor-scan": "A **hot spot** with a classic pain point to check."}
        issues = vs.vocab_issues(["Hot spot"], ["pain point"], skills, {("refactor-scan", "pain point")})
        self.assertEqual(issues, [])

    def test_plural_of_term_counts_as_use(self):
        skills = {"refactor-scan": "Look for the hot spots."}
        self.assertEqual(vs.vocab_issues(["Hot spot"], [], skills, set()), [])


class EndToEndTests(unittest.TestCase):
    def test_real_repo_passes(self):
        repo = pathlib.Path(__file__).resolve().parents[1]
        issues = vs.validate_repo(repo)
        errors = [i for i in issues if i.level == "error"]
        self.assertEqual(errors, [], msg="\n".join(str(i) for i in errors))


if __name__ == "__main__":
    unittest.main()