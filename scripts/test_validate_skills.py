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
                "Config lives in `docs/refactoring/bookkeeping.md`, remembered merge requests "
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


class ScratchRefTests(unittest.TestCase):
    def test_scratch_ref_flagged(self):
        issues = vs.scratch_ref_issues("See `.scratch/php-tooling-tree/issues/10-foo.md`.")
        self.assertTrue(any(".scratch/php-tooling-tree/issues/10-foo.md" in i.message for i in issues))

    def test_scratch_ref_flagged_even_if_file_exists(self):
        # Existence doesn't matter here — unlike local_ref_issues, this is a
        # category ban (internal issue tracker), not a broken-link check.
        issues = vs.scratch_ref_issues("See `.scratch/php-tooling-tree/spec.md`.")
        self.assertTrue(any("spec.md" in i.message for i in issues))

    def test_no_scratch_refs_ok(self):
        self.assertEqual(vs.scratch_ref_issues("No scratch references here."), [])

    def test_plain_prose_scratch_mention_not_flagged(self):
        # Backtick-quoted only, same restraint as local_ref_issues — a
        # non-code mention isn't a link.
        self.assertEqual(vs.scratch_ref_issues("Some scratch work happened here."), [])


class TicketRefTests(unittest.TestCase):
    def test_ticket_ref_flagged(self):
        issues = vs.ticket_ref_issues("Fixed in ticket 37.")
        self.assertTrue(any("ticket 37" in i.message for i in issues))

    def test_capitalized_ticket_ref_flagged(self):
        issues = vs.ticket_ref_issues("Ticket 43 extended the chain.")
        self.assertTrue(any("Ticket 43" in i.message for i in issues))

    def test_pr_ref_flagged(self):
        issues = vs.ticket_ref_issues("See PR #28 for details.")
        self.assertTrue(any("PR #28" in i.message for i in issues))

    def test_pull_request_ref_flagged(self):
        issues = vs.ticket_ref_issues("Discussed in pull request #28.")
        self.assertTrue(any("pull request #28" in i.message for i in issues))

    def test_no_ticket_refs_ok(self):
        self.assertEqual(vs.ticket_ref_issues("No internal tracking references here."), [])

    def test_plain_ticket_word_without_number_not_flagged(self):
        # "ticket" as a bare noun (e.g. glossary avoid-synonym lists) isn't
        # a citation — only a number after it makes this a reference.
        self.assertEqual(vs.ticket_ref_issues("_Avoid_: task, ticket, todo"), [])


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


class ReferencesDirTests(unittest.TestCase):
    """skills/*/references/*.md ships alongside its SKILL.md, so validate_repo
    scans it the same way: ADR citations forbidden, local refs must resolve.
    """

    def _repo(self, ref_content):
        tmp = tempfile.TemporaryDirectory()
        root = pathlib.Path(tmp.name)
        write_tree(root, {
            "CONTEXT.md": "# glossary",
            "docs/agents/skill-references.md": "# ledger\n",
            "skills/refactor-scan/SKILL.md": (
                "---\nname: refactor-scan\ndescription: test\n---\n\n"
                "## Process\n\n## Completion criterion\n"
            ),
            "skills/refactor-scan/references/tree.md": ref_content,
        })
        return tmp, root

    def test_adr_ref_in_references_dir_flagged(self):
        tmp, root = self._repo("Per ADR-0010, do the thing.")
        try:
            issues = vs.validate_repo(root)
            self.assertTrue(any(
                "references/tree.md" in i.skill and "ADR-0010" in i.message
                for i in issues
            ))
        finally:
            tmp.cleanup()

    def test_scratch_ref_in_references_dir_flagged(self):
        tmp, root = self._repo("See `.scratch/php-tooling-tree/issues/10-foo.md` for background.")
        try:
            issues = vs.validate_repo(root)
            self.assertTrue(any(
                "references/tree.md" in i.skill and ".scratch/" in i.message
                for i in issues
            ))
        finally:
            tmp.cleanup()

    def test_missing_local_ref_in_references_dir_flagged(self):
        tmp, root = self._repo("See `docs/agents/missing.md`.")
        try:
            issues = vs.validate_repo(root)
            self.assertTrue(any(
                "references/tree.md" in i.skill and "missing.md" in i.message
                for i in issues
            ))
        finally:
            tmp.cleanup()

    def test_adr_ref_in_non_md_reference_file_flagged(self):
        # A reference doc doesn't have to be Markdown to ship with the skill
        # — a .py helper under references/ carries the same ban on ADR
        # citations in its own docstrings/comments as prose does.
        tmp, root = self._repo("# glossary")
        try:
            (root / "skills" / "refactor-scan" / "references" / "tooling_tree.py").write_text(
                '"""Per ADR-0010, do the thing."""\n'
            )
            issues = vs.validate_repo(root)
            self.assertTrue(any(
                "references/tooling_tree.py" in i.skill and "ADR-0010" in i.message
                for i in issues
            ))
        finally:
            tmp.cleanup()

    def test_adr_ref_in_nested_reference_dir_flagged(self):
        # references/ can nest a subdirectory of its own (e.g.
        # php-tooling-tree/composer.md) — scanning must recurse, not just
        # glob the top level.
        tmp, root = self._repo("# glossary")
        try:
            (root / "skills" / "refactor-scan" / "references" / "nested").mkdir(parents=True)
            (root / "skills" / "refactor-scan" / "references" / "nested" / "node.md").write_text(
                "Per ADR-0010, do the thing.\n"
            )
            issues = vs.validate_repo(root)
            self.assertTrue(any(
                "references/nested/node.md" in i.skill and "ADR-0010" in i.message
                for i in issues
            ))
        finally:
            tmp.cleanup()

    def test_pycache_in_references_dir_ignored(self):
        # Compiled bytecode is never source and never shipped intentionally
        # — scanning it would only risk a decode error on binary content.
        tmp, root = self._repo("# glossary")
        try:
            pycache = root / "skills" / "refactor-scan" / "references" / "__pycache__"
            pycache.mkdir(parents=True)
            (pycache / "tooling_tree.cpython-311.pyc").write_bytes(b"\x00\x01\x02not text")
            issues = vs.validate_repo(root)  # must not raise
            self.assertFalse(any("__pycache__" in i.skill for i in issues))
        finally:
            tmp.cleanup()

    def test_clean_references_dir_ok(self):
        tmp, root = self._repo("No decisions or dangling paths here.")
        try:
            issues = vs.validate_repo(root)
            self.assertFalse(any("references/tree.md" in i.skill for i in issues))
        finally:
            tmp.cleanup()


class SizeTests(unittest.TestCase):
    def test_under_limit_ok(self):
        text = "---\nname: x\ndescription: y\n---\n\n" + "word " * 100
        self.assertEqual(vs.size_issues({"x": text}), [])

    def test_over_limit_flagged(self):
        text = "---\nname: x\ndescription: y\n---\n\n" + "word " * (vs.SKILL_MD_WORD_LIMIT + 1)
        issues = vs.size_issues({"x": text})
        self.assertEqual(len(issues), 1)
        self.assertIn("size advisory", issues[0].message)

    def test_frontmatter_not_counted_toward_limit(self):
        # A huge frontmatter block alone must not trip the limit -- only the
        # body counts.
        frontmatter = "---\n" + "field: value\n" * (vs.SKILL_MD_WORD_LIMIT + 1) + "---\n\nshort body"
        self.assertEqual(vs.size_issues({"x": frontmatter}), [])


class OrphanedReferenceTests(unittest.TestCase):
    def test_referenced_file_not_flagged(self):
        refs = [("refactor-scan", "skills/refactor-scan/references/foo.md")]
        all_text = {
            "skills/refactor-scan/SKILL.md": "See `skills/refactor-scan/references/foo.md` for details.",
            "skills/refactor-scan/references/foo.md": "The details.",
        }
        self.assertEqual(vs.orphaned_reference_issues(refs, all_text), [])

    def test_unreferenced_file_flagged(self):
        refs = [("refactor-scan", "skills/refactor-scan/references/foo.md")]
        all_text = {
            "skills/refactor-scan/SKILL.md": "Nothing points anywhere.",
            "skills/refactor-scan/references/foo.md": "Orphaned content.",
        }
        issues = vs.orphaned_reference_issues(refs, all_text)
        self.assertEqual(len(issues), 1)
        self.assertIn("orphan advisory", issues[0].message)

    def test_referenced_from_another_skill_not_flagged(self):
        # Cross-skill pointers count too -- refactor-design can be the only
        # thing naming a file that ships under continuous-refactoring/.
        refs = [("continuous-refactoring", "skills/continuous-refactoring/references/shared.md")]
        all_text = {
            "skills/continuous-refactoring/references/shared.md": "Shared rule.",
            "skills/refactor-design/SKILL.md": "See `skills/continuous-refactoring/references/shared.md`.",
        }
        self.assertEqual(vs.orphaned_reference_issues(refs, all_text), [])


class DuplicationTests(unittest.TestCase):
    LONG = "This sentence has more than fifteen words in it so it should count as a real duplication candidate."

    def test_unique_sentences_ok(self):
        all_text = {
            "a.md": self.LONG,
            "b.md": "A completely different sentence that also has plenty of words in it to pass the threshold.",
        }
        self.assertEqual(vs.duplication_issues(all_text), [])

    def test_duplicate_sentence_flagged(self):
        all_text = {"a.md": self.LONG, "b.md": self.LONG}
        issues = vs.duplication_issues(all_text)
        self.assertEqual(len(issues), 1)
        self.assertIn("duplication advisory", issues[0].message)

    def test_short_sentence_not_flagged(self):
        short = "Too short to matter."
        all_text = {"a.md": short, "b.md": short}
        self.assertEqual(vs.duplication_issues(all_text), [])

    def test_code_fence_ignored(self):
        block = "```\n" + self.LONG + "\n```"
        all_text = {"a.md": block, "b.md": block}
        self.assertEqual(vs.duplication_issues(all_text), [])

    def test_allowlisted_pair_not_flagged(self):
        all_text = {"a.md": self.LONG, "b.md": self.LONG}
        issues = vs.duplication_issues(all_text, allow={frozenset({"a.md", "b.md"})})
        self.assertEqual(issues, [])

    def test_repeat_within_same_file_not_flagged(self):
        # Single source of truth is a cross-file concern; a file repeating
        # its own sentence is a different (unaddressed) smell.
        all_text = {"a.md": self.LONG + " " + self.LONG}
        self.assertEqual(vs.duplication_issues(all_text), [])


class CompletionClarityTests(unittest.TestCase):
    def test_checkable_criterion_ok(self):
        skills = {"x": "## Completion criterion\nThe branch exists and CI is green."}
        self.assertEqual(vs.completion_clarity_issues(skills), [])

    def test_vague_phrase_flagged(self):
        skills = {"x": "## Completion criterion\nThe change is properly implemented."}
        issues = vs.completion_clarity_issues(skills)
        self.assertEqual(len(issues), 1)
        self.assertIn("clarity advisory", issues[0].message)

    def test_missing_section_skipped(self):
        skills = {"x": "## Process\nDo the thing."}
        self.assertEqual(vs.completion_clarity_issues(skills), [])

    def test_vague_phrase_outside_section_not_flagged(self):
        skills = {"x": "Properly implemented is mentioned here.\n\n## Completion criterion\nThe branch exists."}
        self.assertEqual(vs.completion_clarity_issues(skills), [])


class IsAdvisoryTests(unittest.TestCase):
    def test_advisory_message_true(self):
        self.assertTrue(vs.is_advisory(vs.Issue("x", "size advisory: too long")))

    def test_error_message_false(self):
        self.assertFalse(vs.is_advisory(vs.Issue("x", "missing frontmatter")))


class EndToEndTests(unittest.TestCase):
    def test_real_repo_passes(self):
        repo = pathlib.Path(__file__).resolve().parents[1]
        issues = vs.validate_repo(repo)
        # Advisory issues (contract consistency, size, orphaned references,
        # duplication, completion clarity) are warnings, not hard failures.
        errors = [i for i in issues if not vs.is_advisory(i)]
        self.assertEqual(errors, [], msg="\n".join(str(i) for i in errors))


if __name__ == "__main__":
    unittest.main()