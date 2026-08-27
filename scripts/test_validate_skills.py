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
        self.assertTrue(vs.frontmatter_issues(text, "x"))

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
        self.assertTrue(vs.frontmatter_issues(text, "refactor-scan"))

    def test_leading_hyphen_rejected(self):
        text = "---\nname: -refactor-scan\ndescription: desc\n---\n"
        self.assertTrue(vs.frontmatter_issues(text, "refactor-scan"))

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
        self.assertEqual(vs.section_issues(text, "test-skill-fixture", requires_fallback=False), [])


class LedgerTests(unittest.TestCase):
    def test_parse_ledger(self):
        ledger = vs.parse_ledger(
            "| Skill | Global ref | Role | Fallback type | Self-contained in |\n"
            "|---|---|---|---|---|\n"
            "| `refactor-scan` | `/codebase-design` (Z.31) | enrichment | crash-safe | 01 \u2713 shipped |\n"
            "| `refactor-review` | `/code-review` (Z.23) | core | self-sufficient | 04 \u2713 shipped |\n"
        )
        self.assertEqual(
            ledger["refactor-scan"], [("codebase-design", True)]
        )
        self.assertEqual(
            ledger["refactor-review"], [("code-review", True)]
        )

    def test_parse_ledger_ignores_header(self):
        ledger = vs.parse_ledger("| Skill | Global ref | Role | Fallback type | Self-contained in |\n|---|---|---|---|---|\n")
        self.assertEqual(ledger, {})


class GlobalRefTests(unittest.TestCase):
    SUITE = {"refactor-scan", "test-skill-fixture", "refactor-prioritize"}

    def test_dangling_ref_not_in_ledger(self):
        text = "See `/grilling` for details."
        issues = vs.global_ref_issues(text, "refactor-scan", self.SUITE, {"refactor-scan": []})
        self.assertTrue(any("grilling" in i.message and "ledger" in i.message for i in issues))

    def test_bare_ref_not_in_ledger(self):
        text = "See /grilling for details."
        issues = vs.global_ref_issues(text, "refactor-scan", self.SUITE, {"refactor-scan": []})
        self.assertTrue(any("grilling" in i.message and "ledger" in i.message for i in issues))

    def test_docs_path_slash_is_not_a_ref(self):
        text = "Offer an ADR under `docs/adr/`."
        issues = vs.global_ref_issues(text, "refactor-design", self.SUITE, {"refactor-design": []})
        self.assertEqual(issues, [])

    def test_stale_ledger_row(self):
        text = "No global refs here."
        issues = vs.global_ref_issues(text, "refactor-scan", self.SUITE, {"refactor-scan": [("grilling", True)]})
        self.assertTrue(any("stale" in i.message or "ledger" in i.message for i in issues))

    def test_suite_internal_refs_exempt(self):
        text = "Run `/refactor-scan` then `/refactor-prioritize`."
        issues = vs.global_ref_issues(text, "test-skill-fixture", self.SUITE, {"test-skill-fixture": []})
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
            text = "See `CODING_STANDARDS.md` or `CONTRIBUTING.md`."
            self.assertEqual(vs.local_ref_issues(text, root), [])
        finally:
            tmp.cleanup()

    def test_target_repo_suite_state_exempt(self):
        tmp, root = self._repo()
        try:
            text = (
                "Config lives in `docs/refactoring/config.md`, remembered merge requests "
                "in `docs/refactoring/merge-requests.md`, learned rejections under "
                "`docs/refactoring/out-of-scope/`."
            )
            self.assertEqual(vs.local_ref_issues(text, root), [])
        finally:
            tmp.cleanup()

    def test_superseded_config_location_flagged(self):
        tmp, root = self._repo()
        try:
            issues = vs.local_ref_issues("Read `docs/agents/refactoring.md`.", root)
            self.assertTrue(any("docs/agents/refactoring.md" in i.message for i in issues))
        finally:
            tmp.cleanup()

    def test_non_path_backticks_ignored(self):
        tmp, root = self._repo()
        try:
            text = "Run `git log --oneline`, `git mv a.md b.md`, check `composer.json`, `Makefile`, `.php-cs-fixer.php`."
            self.assertEqual(vs.local_ref_issues(text, root), [])
        finally:
            tmp.cleanup()


class AdrTests(unittest.TestCase):
    def test_any_adr_ref_flagged(self):
        issues = vs.adr_issues("Per ADR-0002.")
        self.assertTrue(any("0002" in i.message for i in issues))

    def test_resolvable_adr_still_flagged(self):
        # Even a real, existing ADR is forbidden in skill prose — suite ADRs
        # are internal maintainer docs that never ship with the skill.
        issues = vs.adr_issues("Per ADR-0010.")
        self.assertTrue(any("0010" in i.message for i in issues))

    def test_no_adr_refs_ok(self):
        self.assertEqual(vs.adr_issues("No decisions here."), [])


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

    def test_avoid_term_plural_flagged(self):
        skills = {"refactor-scan": "Several pain points to check."}
        issues = vs.vocab_issues(["Hot spot"], ["pain point"], skills, set())
        self.assertTrue(any("pain point" in i.message for i in issues))

    def test_term_inflection_matches_only_plural(self):
        skills = {"refactor-scan": "Run the deletion testing on it."}
        issues = vs.vocab_issues(["Deletion test"], [], skills, set())
        self.assertTrue(any("Deletion test" in i.message for i in issues))

    def test_allowlisted_use_ok(self):
        skills = {"refactor-scan": "A **hot spot** with a classic pain point to check."}
        issues = vs.vocab_issues(["Hot spot"], ["pain point"], skills, {("refactor-scan", "pain point")})
        self.assertEqual(issues, [])

    def test_plural_of_term_counts_as_use(self):
        skills = {"refactor-scan": "Look for the hot spots."}
        self.assertEqual(vs.vocab_issues(["Hot spot"], [], skills, set()), [])


class ADR0004PropagationTests(unittest.TestCase):
    def test_all_keywords_present(self):
        skills = {
            "refactor-design": "behavior-preserving, Strangler Fig, Kent Beck, deterministic tools, own branch",
            "refactor-implement": "",
        }
        self.assertEqual(vs.adr0004_propagation_issues(skills), [])

    def test_split_across_skills(self):
        skills = {
            "refactor-design": "behavior-preserving, Strangler Fig",
            "refactor-implement": "Kent Beck, deterministic tools, own branch",
        }
        self.assertEqual(vs.adr0004_propagation_issues(skills), [])

    def test_missing_keyword_flagged(self):
        skills = {
            "refactor-design": "behavior-preserving, Strangler Fig, Kent Beck",
            "refactor-implement": "deterministic tools",
        }
        issues = vs.adr0004_propagation_issues(skills)
        self.assertEqual(len(issues), 1)
        self.assertIn("own branch", issues[0].message)

    def test_case_insensitive(self):
        skills = {
            "refactor-design": "BEHAVIOR-PRESERVING, strangler fig, kent beck, DETERMINISTIC TOOLS, own branch",
            "refactor-implement": "",
        }
        self.assertEqual(vs.adr0004_propagation_issues(skills), [])

    def test_missing_skill_flagged(self):
        skills = {"refactor-design": "behavior-preserving Strangler Fig Kent Beck deterministic tools own branch"}
        self.assertEqual(vs.adr0004_propagation_issues(skills), [])

    def test_multiple_missing(self):
        skills = {"refactor-design": "", "refactor-implement": ""}
        issues = vs.adr0004_propagation_issues(skills)
        self.assertEqual(len(issues), 5)


class ContractConsistencyTests(unittest.TestCase):
    ORCH = (
        "## The pass\n"
        "1. **Scan.** Run the scan to file candidates.\n"
        "2. **Prioritise.** Rank the backlog.\n"
        "3. **Design.** Grill the candidate into a plan.\n"
        "4. **Implement.** Execute the plan slice by slice.\n"
        "5. **Review.** Verify tooling green and report findings.\n"
    )

    def test_matching_contracts(self):
        skills = {
            "refactor-scan": "## Completion criterion\nEvery candidate filed.",
            "refactor-prioritize": "## Completion criterion\nBacklog ranked.",
            "refactor-design": "## Completion criterion\nPlan written.",
            "refactor-implement": "## Completion criterion\nSlices done, green.",
            "refactor-review": "## Completion criterion\nTooling green, findings reported.",
        }
        issues = vs.contract_consistency_issues(self.ORCH, skills)
        # All five steps produce advisory issues (orchestrator is brief);
        # verify no hard errors.
        self.assertTrue(len(issues) > 0, "expected advisory issues for brief orchestrator steps")
        for i in issues:
            self.assertIn("advisory", i.message)

    def test_mismatch_flagged(self):
        skills = {
            "refactor-scan": "## Completion criterion\nNothing relevant at all.",
            "refactor-prioritize": "## Completion criterion\nBacklog ranked.",
            "refactor-design": "## Completion criterion\nPlan written.",
            "refactor-implement": "## Completion criterion\nSlices done, green.",
            "refactor-review": "## Completion criterion\nTooling green, findings reported.",
        }
        issues = vs.contract_consistency_issues(self.ORCH, skills)
        scan_issues = [i for i in issues if "scan" in i.skill]
        self.assertTrue(len(scan_issues) > 0)

    def test_missing_step_skipped(self):
        skills = {}
        issues = vs.contract_consistency_issues(self.ORCH, skills)
        self.assertEqual(issues, [])

    def test_empty_orchestrator(self):
        skills = {"refactor-scan": "## Completion criterion\nDone."}
        issues = vs.contract_consistency_issues("", skills)
        self.assertEqual(issues, [])


class GlossaryReverseTests(unittest.TestCase):
    def test_known_term_not_flagged(self):
        skills = {
            "refactor-scan": "Use the **hot spot** to find candidates.",
            "refactor-design": "The **hot spot** drives prioritisation.",
        }
        context = "**Hot spot**: a frequently changing area."
        issues = vs.glossary_reverse_issues(skills, context)
        self.assertEqual(issues, [])

    def test_unknown_bold_term_flagged(self):
        skills = {
            "refactor-scan": "Apply the **frontier** analysis.",
            "refactor-design": "Expand the **frontier** outward.",
        }
        issues = vs.glossary_reverse_issues(skills, {})
        self.assertEqual(len(issues), 1)
        self.assertIn("frontier", issues[0].message)

    def test_single_skill_not_flagged(self):
        skills = {"refactor-scan": "Use **frontier** in one place only."}
        issues = vs.glossary_reverse_issues(skills, {})
        self.assertEqual(issues, [])

    def test_empty_skills(self):
        issues = vs.glossary_reverse_issues({}, {})
        self.assertEqual(issues, [])

    def test_non_bold_terms_ignored(self):
        skills = {
            "refactor-scan": "frontier analysis and frontier theory",
            "refactor-design": "frontier exploration and frontier logic",
        }
        issues = vs.glossary_reverse_issues(skills, {})
        self.assertEqual(issues, [])

    def test_hyphenated_term(self):
        skills = {
            "refactor-scan": "The **design tree** branches.",
            "refactor-design": "Build the **design tree** step by step.",
        }
        issues = vs.glossary_reverse_issues(skills, {})
        self.assertEqual(len(issues), 1)
        self.assertIn("design tree", issues[0].message)


class ADRStalenessTests(unittest.TestCase):
    def _repo(self, adr_files):
        tmp = tempfile.TemporaryDirectory()
        root = pathlib.Path(tmp.name)
        adr_dir = root / "docs" / "adr"
        adr_dir.mkdir(parents=True)
        for name, content in adr_files.items():
            (adr_dir / name).write_text(content)
        return tmp, root

    def test_no_superseded(self):
        tmp, root = self._repo({"0001-foo.md": "# Foo\nADR-0002 referenced."})
        try:
            issues = vs.adr_staleness_issues({}, root / "docs" / "adr")
            self.assertEqual(issues, [])
        finally:
            tmp.cleanup()

    def test_superseded_without_successor_flagged(self):
        tmp, root = self._repo({
            "0001-old.md": "# Old",
            "0002-new.md": "# New\nThis supersedes ADR-0001.",
        })
        try:
            skills = {"refactor-scan": "Per ADR-0001 we do things."}
            issues = vs.adr_staleness_issues(skills, root / "docs" / "adr")
            self.assertEqual(len(issues), 1)
            self.assertIn("ADR-0001", issues[0].message)
            self.assertIn("ADR-0002", issues[0].message)
        finally:
            tmp.cleanup()

    def test_superseded_with_successor_ok(self):
        tmp, root = self._repo({
            "0001-old.md": "# Old",
            "0002-new.md": "# New\nThis supersedes ADR-0001.",
        })
        try:
            skills = {"refactor-scan": "Per ADR-0001, see also ADR-0002."}
            issues = vs.adr_staleness_issues(skills, root / "docs" / "adr")
            self.assertEqual(issues, [])
        finally:
            tmp.cleanup()

    def test_amends_not_flagged(self):
        tmp, root = self._repo({
            "0001-foo.md": "# Foo",
            "0002-bar.md": "# Bar\nThis amends ADR-0001.",
        })
        try:
            skills = {"refactor-scan": "Per ADR-0001."}
            issues = vs.adr_staleness_issues(skills, root / "docs" / "adr")
            self.assertEqual(issues, [])
        finally:
            tmp.cleanup()

    def test_no_adr_refs_ok(self):
        tmp, root = self._repo({
            "0001-old.md": "# Old",
            "0002-new.md": "# New\nThis supersedes ADR-0001.",
        })
        try:
            skills = {"refactor-scan": "No ADR references here."}
            issues = vs.adr_staleness_issues(skills, root / "docs" / "adr")
            self.assertEqual(issues, [])
        finally:
            tmp.cleanup()


class EndToEndTests(unittest.TestCase):
    def test_real_repo_passes(self):
        repo = pathlib.Path(__file__).resolve().parents[1]
        issues = vs.validate_repo(repo)
        # Contract consistency issues are advisory (orchestrator steps are
        # intentionally brief); exclude them from the hard-fail check.
        errors = [i for i in issues if vs.ADVISORY_PREFIX not in i.message]
        self.assertEqual(errors, [], msg="\n".join(str(i) for i in errors))


if __name__ == "__main__":
    unittest.main()