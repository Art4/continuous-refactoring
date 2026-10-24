"""Tests for the ADR index and the banner relations (scripts/adr_index.py)."""

import pathlib
import tempfile
import unittest

import adr_index as ai
import validate_skills as vs

REPO = pathlib.Path(__file__).resolve().parents[1]


def repo_with(adrs):
    """A scratch repository whose docs/adr holds the given {filename: text}, index generated."""
    tmp = tempfile.TemporaryDirectory()
    root = pathlib.Path(tmp.name)
    (root / ai.ADR_DIR).mkdir(parents=True)
    for name, text in adrs.items():
        (root / ai.ADR_DIR / name).write_text(text)
    ai.write(root)
    return tmp, root


OLD = "0001-old.md"
NEW = "0002-new.md"


class RealRepositoryTests(unittest.TestCase):
    def test_the_suites_own_adrs_are_consistent_and_the_index_current(self):
        self.assertEqual(ai.check(REPO), [])


class RelationTests(unittest.TestCase):
    def test_a_clause_names_the_adrs_up_to_its_colon(self):
        text = "# T\n\n> Superseded in part by [ADR-0073](a.md) and\n> [ADR-0074](b.md): see ADR-0075.\n\nBody ADR-0099.\n"
        self.assertEqual(ai.relations(text), [("superseded in part by", "0073"), ("superseded in part by", "0074")])

    def test_several_clauses_in_one_sentence(self):
        text = "# T\n\n> Amended by [ADR-0053](a.md), superseded in part by [ADR-0077](b.md): why.\n"
        self.assertEqual(ai.relations(text), [("amended by", "0053"), ("superseded in part by", "0077")])

    def test_a_description_of_another_adr_is_no_clause(self):
        text = "# T\n\n> Interacted with ADR-0015 at the time; ADR-0015 was later superseded by ADR-0049.\n"
        self.assertEqual(ai.relations(text), [])

    def test_the_banner_ends_at_the_first_unquoted_line(self):
        text = "# T\n\nThis supersedes ADR-0005.\n"
        self.assertEqual(ai.relations(text), [])

    def test_status_is_the_strongest_change(self):
        adr = ai.Adr("0001", OLD, "Old", newer={"0002": "amended", "0003": "superseded in part"})
        self.assertEqual(adr.status, "superseded in part")
        self.assertEqual(ai.Adr("0004", "0004-x.md", "X").status, "in force")

    def test_a_change_without_an_adr_sets_the_status(self):
        text = "# T\n\n> Superseded without an ADR: the outlook was dropped when the texts were written anew.\n"
        self.assertEqual(ai.unrecorded(text), {"superseded"})
        self.assertEqual(ai.relations(text), [])


class CheckTests(unittest.TestCase):
    def test_both_sides_named_is_clean(self):
        tmp, root = repo_with({
            OLD: "# Old\n\n> Superseded by [ADR-0002](0002-new.md): gone.\n\nText.\n",
            NEW: "# New\n\n> Supersedes [ADR-0001](0001-old.md).\n\nText.\n",
        })
        with tmp:
            self.assertEqual(ai.check(root), [])

    def test_a_relation_named_on_one_side_only(self):
        tmp, root = repo_with({
            OLD: "# Old\n\nText.\n",
            NEW: "# New\n\n> Amends [ADR-0001](0001-old.md): a detail.\n\nText.\n",
        })
        with tmp:
            self.assertEqual(ai.check(root), [(
                "docs/adr/0002-new.md",
                "banner names ADR-0001 as changed by it, but the banner of ADR-0001 does not name ADR-0002",
            )])

    def test_a_relation_to_an_adr_that_does_not_exist(self):
        tmp, root = repo_with({OLD: "# Old\n\n> Amended by ADR-0009.\n"})
        with tmp:
            self.assertEqual(ai.check(root), [("docs/adr/0001-old.md", "banner names ADR-0009, which does not exist")])

    def test_an_index_out_of_date(self):
        tmp, root = repo_with({OLD: "# Old\n\nText.\n"})
        with tmp:
            (root / ai.ADR_DIR / NEW).write_text("# New\n\nText.\n")
            self.assertEqual(ai.check(root), [("docs/adr/README.md", f"is out of date — run `{ai.COMMAND}`")])
            self.assertTrue(ai.write(root))
            self.assertEqual(ai.check(root), [])
            self.assertFalse(ai.write(root))

    def test_a_repository_without_adrs_is_not_checked(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(ai.check(pathlib.Path(tmp)), [])


class IndexTests(unittest.TestCase):
    def test_the_index_lists_status_and_both_directions(self):
        tmp, root = repo_with({
            OLD: "# Old | choice\n\n> Superseded in part by [ADR-0002](0002-new.md): some of it.\n",
            NEW: "# New\n\n> Supersedes in part [ADR-0001](0001-old.md).\n",
        })
        with tmp:
            index = (root / ai.INDEX).read_text()
        self.assertIn("| [0001](0001-old.md) | Old \\| choice | superseded in part | [0002](0002-new.md) |  |", index)
        self.assertIn("| [0002](0002-new.md) | New | in force |  | [0001](0001-old.md) |", index)
        self.assertIn("Superseded: 0 · Superseded in part: 1 · Amended: 0 · In force: 1", index)


class ValidatorTests(unittest.TestCase):
    def test_the_validator_reports_what_the_check_reports(self):
        tmp, root = repo_with({OLD: "# Old\n\n> Amended by ADR-0002.\n", NEW: "# New\n\nText.\n"})
        with tmp:
            issues = vs.adr_banner_issues(root)
        self.assertEqual([i.skill for i in issues], ["docs/adr/0001-old.md"])


if __name__ == "__main__":
    unittest.main()
