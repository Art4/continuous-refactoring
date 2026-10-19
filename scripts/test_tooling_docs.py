"""Tests for the tooling model's generator and checks (scripts/tooling_docs.py)."""

import json
import pathlib
import shutil
import tempfile
import unittest
from unittest import mock

import tooling_docs as td
import validate_skills as vs

REPO = pathlib.Path(__file__).resolve().parents[1]
REFS = td.REFERENCES


def copy_repo(tmp):
    """The suite's own model in a scratch repository, docs generated."""
    root = pathlib.Path(tmp)
    shutil.copytree(REPO / REFS, root / REFS, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    td.write(root)
    return root


def edit_pack(root, pack, change):
    path = root / REFS / "packs" / pack / "pack.json"
    data = json.loads(path.read_text())
    change(data)
    path.write_text(td.canonical_json(data, "pack"))


class RealRepositoryTests(unittest.TestCase):
    def test_the_suites_own_model_is_current(self):
        self.assertEqual(td.check(REPO), [])

    def test_writing_twice_changes_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = copy_repo(tmp)
            self.assertEqual(td.write(root), [])


class FixedFormTests(unittest.TestCase):
    def test_form(self):
        data = {
            "applies_when": "Always.",
            "pack": "x",
            "$schema": "s.json",
            "tools": [{
                "stages": [{"after": [], "requires": ["a", ["b", "c"]], "track": "Safety Net", "name": "N", "slug": "n"}],
                "min_runtime": {"php": "7.2"},
                "tool": "t", "name": "T", "uses": None, "roles": ["r"], "status": "recommended", "details": "d.md",
            }],
        }
        self.assertEqual(
            td.canonical_json(data, "pack"),
            """{
  "$schema": "s.json",
  "pack": "x",
  "applies_when": "Always.",
  "tools": [
    {
      "tool": "t",
      "name": "T",
      "uses": null,
      "roles": ["r"],
      "status": "recommended",
      "details": "d.md",
      "min_runtime": {
        "php": "7.2"
      },
      "stages": [
        {
          "slug": "n",
          "name": "N",
          "track": "Safety Net",
          "requires": ["a", ["b", "c"]],
          "after": []
        }
      ]
    }
  ]
}
""",
        )

    def test_roles_are_expanded(self):
        text = td.canonical_json({"roles": [{"signal": None, "slug": "a", "name": "A", "purpose": "p"}]}, "roles")
        self.assertIn('{\n      "slug": "a",\n      "name": "A",\n      "purpose": "p",\n      "signal": null\n    }', text)

    def test_another_indent_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = copy_repo(tmp)
            path = root / REFS / "packs" / "generic" / "pack.json"
            path.write_text(json.dumps(json.loads(path.read_text()), indent=4) + "\n")
            problems = td.form_problems(root)
            self.assertEqual([p[0] for p in problems], [f"{REFS.as_posix()}/packs/generic/pack.json"])
            self.assertIn("fixed form", problems[0][1])


class OwnPackFixtureTests(unittest.TestCase):
    """The example of a project's own Pack follows the schema and the fixed form, as the suite's do."""

    PACK = REPO / "fixtures/php/php-own-pack/project/docs/agents/tooling-pack"

    def test_the_example_is_valid_and_in_the_fixed_form(self):
        import jsonschema
        for name, kind, schema in (("pack.json", "pack", "pack.schema.json"), ("roles.json", "roles", "roles.schema.json")):
            text = (self.PACK / name).read_text()
            data = json.loads(text)
            jsonschema.Draft202012Validator(json.loads((REPO / REFS / schema).read_text())).validate(data)
            self.assertEqual(text, td.canonical_json(data, kind), name)


class SchemaTests(unittest.TestCase):
    def test_a_track_outside_the_schema(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = copy_repo(tmp)
            edit_pack(root, "generic", lambda d: d["tools"][0]["stages"][0].update(track="Nowhere"))
            problems = td.schema_problems(root)
            self.assertTrue(any("tools/0/stages/0/track" in p[1] for p in problems), problems)

    def test_an_unknown_key(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = copy_repo(tmp)
            edit_pack(root, "generic", lambda d: d["tools"][0].update(color="red"))
            self.assertTrue(td.schema_problems(root))

    def test_a_missing_jsonschema_is_an_error_not_a_skip(self):
        with mock.patch.dict("sys.modules", {"jsonschema": None}):
            problems = td.schema_problems(REPO)
        self.assertEqual(len(problems), 1)
        self.assertIn("pip install jsonschema", problems[0][1])


class ModelTests(unittest.TestCase):
    def test_two_recommended_tools_for_one_role(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = copy_repo(tmp)

            def second(data):
                tools = data["tools"]
                twin = json.loads(json.dumps(tools[0]))
                twin.update(tool="twin", name="Twin")
                twin["stages"] = [{"slug": "twin", "name": "Twin", "track": "Safety Net", "requires": [], "after": []}]
                tools.append(twin)

            edit_pack(root, "generic", second)
            td.write(root)
            problems = [p for p in td.check(root) if p[0] == "pack generic"]
            self.assertEqual(len(problems), 1)
            self.assertIn("two recommended tools for the role continuous-integration", problems[0][1])

    def test_a_recognized_tool_may_share_a_role(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = copy_repo(tmp)
            self.assertEqual([p for p in td.check(root) if p[0].startswith("pack ")], [])

    def test_a_missing_details_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = copy_repo(tmp)
            (root / REFS / "packs" / "generic" / "ci-runner.md").unlink()
            problems = td.check(root)
            self.assertIn(("tool ci-runner", "names the details file ci-runner.md, which does not exist"), problems)

    def test_a_tool_file_no_tool_names_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = copy_repo(tmp)
            (root / REFS / "packs" / "php" / "forgotten.md").write_text("# Forgotten\n")
            (root / REFS / "packs" / "php" / "README.md").write_text("# Pack prose\n")
            problems = td.check(root)
            self.assertEqual(
                [p for p in problems if p[0].startswith("packs/")],
                [("packs/php/forgotten.md", "is the details file of no Tool in its Pack")],
            )

    def test_a_broken_model_is_reported_not_raised(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = copy_repo(tmp)
            edit_pack(root, "generic", lambda d: d["tools"][0]["stages"][0].update(requires=["nothing"]))
            problems = td.check(root)
            self.assertTrue(any(p[0] == "tooling model" and "nothing" in p[1] for p in problems), problems)


class DocsTests(unittest.TestCase):
    def test_changing_a_stage_without_regenerating_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = copy_repo(tmp)
            edit_pack(root, "php", lambda d: d["tools"][0]["stages"][0].update(name="Composer 2"))
            problems = td.check(root)
            self.assertEqual(
                problems,
                [("docs/tooling/packs/php.md", f"is out of date — run `{td.COMMAND}`")],
            )
            td.write(root)
            self.assertEqual(td.check(root), [])

    def test_a_missing_page(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = copy_repo(tmp)
            (root / "docs/tooling/packs/generic.md").unlink()
            self.assertEqual([p[0] for p in td.check(root)], ["docs/tooling/packs/generic.md"])

    def test_a_page_of_no_pack_is_reported_and_removed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = copy_repo(tmp)
            stale = root / "docs/tooling/packs/gone.md"
            stale.write_text("old\n")
            self.assertEqual([p[0] for p in td.check(root)], ["docs/tooling/packs/gone.md"])
            self.assertEqual(td.write(root), ["docs/tooling/packs/gone.md (removed)"])
            self.assertFalse(stale.exists())

    def test_the_pages(self):
        model = td.tooling_tree.load_model()
        docs = td.render_docs(model)
        self.assertEqual(sorted(docs), ["docs/tooling/README.md", "docs/tooling/packs/generic.md", "docs/tooling/packs/php.md"])
        php = docs["docs/tooling/packs/php.md"]
        self.assertIn("```mermaid\nflowchart TD", php)
        self.assertIn("subgraph t_safety_net", php)
        self.assertIn("s_phpstan_level_4 -->|one of| s_psalm_taint_analysis", php)  # an any-of: one labelled edge per member
        self.assertIn("s_psalm -->|one of| s_psalm_taint_analysis", php)
        self.assertIn("s_phpstan_level_5 --> s_phpstan_level_6", php)     # requires: solid
        self.assertIn("s_php_cs_fixer -.-> s_rector_php_set", php)        # after: dashed
        self.assertIn('x_editorconfig[".editorconfig (generic)"]', php)   # another Pack's Stage at the edge
        self.assertIn('r_static_analysis(["Static Analysis"])', php)      # a Role
        self.assertIn("Secret Scanning", docs["docs/tooling/README.md"])
        self.assertLess(php.index("## Diagram"), php.index("## Tools"))     # the picture comes first

    def test_node_ids_of_different_kinds_never_meet(self):
        self.assertNotEqual(td._node("s", "psalm"), td._node("r", "psalm"))

    def test_no_citation_of_decisions_or_tickets(self):
        for rel, text in td.render_docs(td.tooling_tree.load_model()).items():
            self.assertEqual(vs.doc_citation_issues(text, rel), [], rel)


class ValidatorTests(unittest.TestCase):
    def test_the_validator_reports_what_the_check_reports(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = copy_repo(tmp)
            (root / "docs/tooling/README.md").write_text("old\n")
            issues = vs.tooling_model_issues(root)
            self.assertEqual([(i.skill, "out of date" in i.message) for i in issues], [("docs/tooling/README.md", True)])

    def test_a_repository_without_a_model_is_not_checked(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(vs.tooling_model_issues(tmp), [])


if __name__ == "__main__":
    unittest.main()
