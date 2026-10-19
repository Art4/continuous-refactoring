"""Tests for the tooling-tree parser (skills/continuous-refactoring/references/tooling_tree.py)

The model (Roles, Tools and Stages in Packs) and the graph outputs computed from the seed the caller
hands in. Synthetic Packs test the rules; the suite's own Packs are loaded to test the data.
"""

import importlib.util
import json
import pathlib
import shutil
import subprocess
import sys
import tempfile
import unittest
import weakref

_REFERENCES = pathlib.Path(__file__).resolve().parents[1] / "skills" / "continuous-refactoring" / "references"
_spec = importlib.util.spec_from_file_location("tooling_tree", _REFERENCES / "tooling_tree.py")
tp = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(tp)

TRACKER_FILE = "docs/agents/issue-tracker.md"


def make_repo(onboarded=True):
    tmp = tempfile.TemporaryDirectory()
    root = pathlib.Path(tmp.name)
    if onboarded:
        (root / "docs/agents").mkdir(parents=True)
        (root / TRACKER_FILE).write_text("# Issue tracker\n\n## Refactoring operations\n\n- **Search:** `gh issue list`\n")
    return tmp, root


def stage(slug, track="Safety Net", requires=(), after=(), **extra):
    return {"slug": slug, "name": slug.upper(), "track": track, "requires": list(requires), "after": list(after), **extra}


def tool(slug, stages, roles=("alpha",), status="recommended", uses="uses", **extra):
    return {"tool": slug, "name": slug.title(), "uses": uses, "roles": list(roles), "status": status,
            "details": f"{slug}.md", "stages": stages, **extra}


def pack(name, tools, applies_when="Always.", scope=None):
    doc = {"pack": name, "applies_when": applies_when, "tools": tools}
    if scope is not None:
        doc["scope"] = scope
    return doc


ROLES = {"roles": [
    {"slug": slug, "name": slug.title(), "purpose": "p", "signal": None}
    for slug in ("alpha", "beta", "gamma", "delta")
]}


class Model:
    """Synthetic Packs on disk for the lifetime of a test."""

    def __init__(self, packs, roles=None):
        root = pathlib.Path(tempfile.mkdtemp())
        weakref.finalize(self, shutil.rmtree, root, True)
        for doc in packs:
            (root / "packs" / doc["pack"]).mkdir(parents=True)
            (root / "packs" / doc["pack"] / "pack.json").write_text(json.dumps(doc))
        (root / "roles.json").write_text(json.dumps(roles or ROLES))
        self.packs_dir, self.roles_json = root / "packs", root / "roles.json"

    def load(self):
        return tp.load_model(self.packs_dir, self.roles_json)

    def compute(self, seed=None, onboarded=True):
        model = self.load()
        repo_tmp, repo = make_repo(onboarded)
        with repo_tmp:
            full = {"fulfilled": [], "rejected": {}, "packs": None, "not_applicable": [], "runtime": {}}
            full.update(seed or {})
            return tp.compute(repo, model, full)


def chain():
    """alpha: a1 -> a2 (one Tool); beta: b1 requires a2, in Guardrails: g1 requires a1."""
    return Model([pack("main", [
        tool("a", [stage("a1"), stage("a2", requires=["a1"])], roles=["alpha"]),
        tool("b", [stage("b1", requires=["a2"])], roles=["beta"]),
        tool("g", [stage("g1", track="Guardrails", requires=["a1"])], roles=["gamma"]),
    ])])


def languages():
    """A role filled once per scope: Code Style (alpha) in php (two competing Tools) and in twig, and a
    php Stage that requires static analysis (beta), which a twig Tool also plays."""
    return Model([
        pack("php", [
            tool("fixer", [stage("fixer")], roles=["alpha"]),
            tool("pint", [stage("pint")], roles=["alpha"], status="recognized"),
            tool("analyser", [stage("analyser")], roles=["beta"]),
            tool("refactor", [stage("refactor", requires=["beta"])], roles=["gamma"]),
        ], scope="php"),
        pack("twig", [
            tool("twig-fixer", [stage("twig-fixer")], roles=["alpha"]),
            tool("twig-lint", [stage("twig-lint")], roles=["beta"]),
        ], scope="twig"),
    ])


class ScopeTests(unittest.TestCase):
    def test_a_role_is_filled_once_per_scope(self):
        out = languages().compute({"fulfilled": ["fixer"]})
        filled = {(r["role"], r["scope"]): r["filled_by"] for r in out["roles"]}
        self.assertEqual(filled[("alpha", "php")], "fixer")
        self.assertIsNone(filled[("alpha", "twig")])
        self.assertIn("twig-fixer", out["tracks"]["Safety Net"]["backlog"])
        out_tools = {t["tool"] for t in out["tools"] if t["out"]}
        self.assertNotIn("twig-fixer", out_tools)

    def test_tools_of_one_scope_still_compete(self):
        out = languages().compute({"fulfilled": ["pint"]})
        filled = {(r["role"], r["scope"]): r["filled_by"] for r in out["roles"]}
        self.assertEqual(filled[("alpha", "php")], "pint")
        self.assertEqual({t["tool"] for t in out["tools"] if t["out"]}, {"fixer"})
        self.assertIn("twig-fixer", out["tracks"]["Safety Net"]["backlog"])

    def test_both_scopes_can_be_fulfilled_side_by_side(self):
        out = languages().compute({"fulfilled": ["fixer", "twig-fixer"]})
        self.assertEqual({t["tool"] for t in out["tools"] if t["out"]}, {"pint"})  # only php's own alternative

    def test_a_required_role_is_filled_in_the_scope_of_the_stage(self):
        reasons = lambda out: {w["node"]: w["reason"] for w in out["tracks"]["Safety Net"]["withheld"]}
        out = languages().compute({"fulfilled": ["twig-lint"]})
        self.assertEqual(reasons(out)["refactor"], "blocked — no Tool fills the Role beta")
        out = languages().compute({"fulfilled": ["analyser"]})
        self.assertNotIn("refactor", reasons(out))

    def test_a_stage_may_not_require_a_role_nothing_of_its_scope_plays(self):
        with self.assertRaises(tp.PackError) as caught:
            Model([
                pack("php", [tool("a", [stage("a1", requires=["beta"])], roles=["alpha"])], scope="php"),
                pack("twig", [tool("b", [stage("b1")], roles=["beta"])], scope="twig"),
            ]).load()
        self.assertIn("scope php", str(caught.exception))

    def test_rejecting_a_role_closes_its_tools_in_every_scope(self):
        out = languages().compute({"rejected": {"alpha": None}})
        self.assertTrue({"fixer", "twig-fixer"} <= set(out["closed_by_rejection"]))

    def test_a_scope_must_be_a_slug(self):
        with self.assertRaises(tp.PackError):
            Model([pack("php", [tool("a", [stage("a1")])], scope="Not A Slug")]).load()

    def test_the_suites_php_pack_has_the_scope_php(self):
        model = tp.load_model()
        self.assertEqual(model["packs"]["php"]["scope"], "php")
        self.assertIsNone(model["packs"]["generic"]["scope"])


class LoadModelTests(unittest.TestCase):
    def test_the_suites_own_packs_load(self):
        model = tp.load_model()
        self.assertIn("composer", model["stages"])
        self.assertEqual(list(model["packs"])[0], "generic")

    def test_no_stage_is_recognition_only_or_an_aggregation_node(self):
        model = tp.load_model()
        for gone in ("structural-scan", "php-safety-net", "is-php-project", "static-code-analyzer", "has-real-dependency",
                     "phpstan-not-psalm", "phpstan-baseline-empty", "test-runner-if-missing"):
            self.assertNotIn(gone, model["stages"])

    def test_every_stage_belongs_to_a_tool_that_plays_a_role(self):
        model = tp.load_model()
        for slug, s in model["stages"].items():
            self.assertTrue(model["tools"][s["tool"]]["roles"], slug)

    def test_a_tool_may_share_its_slug_with_its_only_stage(self):
        model = chain().load()
        self.assertEqual(set(model["tools"]), {"a", "b", "g"})
        m = Model([pack("main", [tool("b1", [stage("b1")])])]).load()
        self.assertIn("b1", m["stages"])

    def test_a_tool_may_not_share_its_slug_with_one_of_several_stages(self):
        with self.assertRaises(tp.PackError):
            Model([pack("main", [tool("a1", [stage("a1"), stage("a2")])])]).load()

    def test_generic_comes_first(self):
        model = Model([pack("zeta", [tool("z", [stage("z1")])]), pack("generic", [tool("g", [stage("g1")])])]).load()
        self.assertEqual(list(model["packs"]), ["generic", "zeta"])
        self.assertEqual(model["stage_order"], ["g1", "z1"])

    def test_broken_models_are_refused(self):
        cases = {
            "unknown role": [pack("m", [tool("a", [stage("a1")], roles=["nope"])])],
            "no role": [pack("m", [tool("a", [stage("a1")], roles=[])])],
            "bad track": [pack("m", [tool("a", [stage("a1", track="Elsewhere")])])],
            "duplicate stage": [pack("m", [tool("a", [stage("a1")]), tool("b", [stage("a1")])])],
            "duplicate tool": [pack("m", [tool("a", [stage("a1")]), tool("a", [stage("a2")])])],
            "tool with a role's slug": [pack("m", [tool("alpha", [stage("alpha")])])],
            "stage with a role's slug": [pack("m", [tool("a", [stage("alpha")])])],
            "requires unknown": [pack("m", [tool("a", [stage("a1", requires=["zz"])])])],
            "after unknown": [pack("m", [tool("a", [stage("a1", after=["zz"])])])],
            "any-of with a role": [pack("m", [tool("a", [stage("a1", requires=[["alpha", "a2"]]), stage("a2")])])],
            "any-of of one": [pack("m", [tool("a", [stage("a1", requires=[["a2"]]), stage("a2")])])],
            "bad status": [pack("m", [tool("a", [stage("a1")], status="maybe")])],
            "no applies_when": [{"pack": "m", "tools": [tool("a", [stage("a1")])]}],
            "bad min_runtime": [pack("m", [tool("a", [stage("a1")], min_runtime={"php": 7})])],
            "cycle": [pack("m", [tool("a", [stage("a1", requires=["a2"]), stage("a2", requires=["a1"])])])],
            "after cycle": [pack("m", [tool("a", [stage("a1", after=["a2"]), stage("a2", after=["a1"])])])],
        }
        for label, packs in cases.items():
            with self.subTest(label), self.assertRaises(tp.PackError):
                Model(packs).load()

    def test_a_stage_may_not_require_a_stage_of_a_later_track(self):
        packs = [pack("m", [tool("a", [stage("a1", requires=["g1"])]), tool("g", [stage("g1", track="Guardrails")], roles=["gamma"])])]
        with self.assertRaises(tp.PackError):
            Model(packs).load()
        ok = [pack("m", [tool("a", [stage("a1", track="Guardrails", requires=["s1"])]), tool("s", [stage("s1")], roles=["gamma"])])]
        Model(ok).load()

    def test_a_role_requirement_follows_the_same_track_rule(self):
        packs = [pack("m", [tool("a", [stage("a1", requires=["gamma"])]), tool("g", [stage("g1", track="Guardrails")], roles=["gamma"])])]
        with self.assertRaises(tp.PackError):
            Model(packs).load()

    def test_unreadable_files_are_refused(self):
        m = Model([pack("m", [tool("a", [stage("a1")])])])
        (m.packs_dir / "m" / "pack.json").write_text("{not json")
        with self.assertRaises(tp.PackError):
            m.load()
        with tempfile.TemporaryDirectory() as empty, self.assertRaises(tp.PackError):
            tp.load_model(pathlib.Path(empty))


class SeedFileTests(unittest.TestCase):
    def setUp(self):
        self.model = chain().load()
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def seed(self, data):
        path = pathlib.Path(self.tmp.name) / "seed.json"
        path.write_text(data if isinstance(data, str) else json.dumps(data))
        return tp.load_seed(path, self.model)

    def test_a_full_seed(self):
        seed = self.seed({"fulfilled": ["a1"], "rejected": {"b1": None, "g": {"php": "7.1"}},
                          "packs": ["main"], "not_applicable": ["g1"], "runtime": {"php": "7.4"}})
        self.assertEqual(seed["fulfilled"], ["a1"])
        self.assertEqual(seed["rejected"], {"b1": None, "g": {"php": "7.1"}})
        self.assertEqual(seed["packs"], ["main"])

    def test_defaults(self):
        seed = self.seed({})
        self.assertEqual(seed, {"fulfilled": [], "rejected": {}, "packs": None, "not_applicable": [], "runtime": {}})

    def test_rejected_may_be_a_plain_list_and_a_role_a_tool_or_a_stage(self):
        self.assertEqual(self.seed({"rejected": ["alpha", "b", "g1"]})["rejected"], {"alpha": None, "b": None, "g1": None})

    def test_the_prerequisites_may_be_named_and_are_ignored(self):
        seed = self.seed({"fulfilled": ["git", "onboarding-setup", "a1"], "rejected": {"git": None}})
        self.assertEqual(seed["fulfilled"], ["a1"])
        self.assertEqual(seed["rejected"], {})

    def test_what_cannot_be_used_raises(self):
        bad = [
            "not json", "[]", {"surprise": 1},
            {"fulfilled": "a1"}, {"fulfilled": ["nope"]}, {"fulfilled": ["alpha"]}, {"fulfilled": ["a"]},
            {"rejected": ["nope"]}, {"rejected": 3}, {"rejected": {"b1": "later"}}, {"rejected": {"b1": {"php": "x"}}},
            {"rejected": {"b1": {"php": "7", "node": "8"}}},
            {"fulfilled": ["a1"], "rejected": ["a1"]},
            {"packs": ["nope"]}, {"packs": "main"}, {"not_applicable": ["nope"]},
            {"runtime": {"php": 7}}, {"runtime": []},
        ]
        for data in bad:
            with self.subTest(data), self.assertRaises(tp.SeedError):
                self.seed(data)

    def test_cli_exits_with_2_on_a_broken_seed_or_pack(self):
        m = chain()
        repo_tmp, repo = make_repo()
        with repo_tmp, tempfile.TemporaryDirectory() as d:
            seed = pathlib.Path(d) / "seed.json"
            seed.write_text('{"fulfilled": ["nope"]}')
            script = str(_REFERENCES / "tooling_tree.py")
            run = lambda *a: subprocess.run([sys.executable, script, *a], capture_output=True, text=True)  # noqa: E731
            self.assertEqual(run("--packs", str(m.packs_dir), "--seed", str(seed), str(repo)).returncode, 2)
            (m.packs_dir / "main" / "pack.json").write_text("{")
            self.assertEqual(run("--packs", str(m.packs_dir), str(repo)).returncode, 2)

    def test_cli_prints_the_outputs(self):
        repo_tmp, repo = make_repo()
        with repo_tmp, tempfile.TemporaryDirectory() as d:
            seed = pathlib.Path(d) / "seed.json"
            seed.write_text('{"packs": ["generic"], "fulfilled": ["ci-runner"]}')
            out = subprocess.run([sys.executable, str(_REFERENCES / "tooling_tree.py"), "--seed", str(seed), str(repo)],
                                 capture_output=True, text=True)
            self.assertEqual(out.returncode, 0, out.stderr)
            data = json.loads(out.stdout)
            self.assertEqual(data["packs"], ["generic"])
            self.assertEqual(data["tracks"]["Safety Net"]["backlog"], ["editorconfig"])


class OutputTests(unittest.TestCase):
    def test_tracks_list_nodes_in_pack_order_with_name_tool_and_search(self):
        out = chain().compute()
        self.assertEqual([n["node"] for n in out["tracks"]["Safety Net"]["nodes"]], ["a1", "a2", "b1"])
        self.assertEqual(out["tracks"]["Guardrails"]["nodes"][0],
                         {"node": "g1", "name": "G1", "tool": "uses", "search": ["G1", "uses"]})

    def test_search_holds_the_tool_once_and_none_for_a_convention(self):
        m = Model([pack("m", [tool("a", [stage("a1")], uses="A1"), tool("b", [stage("b1")], uses=None, roles=["beta"])])])
        nodes = {n["node"]: n for n in m.compute()["tracks"]["Safety Net"]["nodes"]}
        self.assertEqual(nodes["a1"]["search"], ["A1"])
        self.assertEqual(nodes["b1"]["tool"], None)
        self.assertEqual(nodes["b1"]["search"], ["B1"])

    def test_nothing_decided_means_everything_is_in_the_backlog(self):
        out = chain().compute()
        self.assertEqual(out["tracks"]["Safety Net"]["backlog"], ["a1", "a2", "b1"])
        self.assertEqual(out["tracks"]["Guardrails"]["backlog"], ["g1"])
        self.assertFalse(out["safety_net_fulfilled"])

    def test_the_tools_are_listed_with_their_names_and_whether_they_are_out(self):
        m = Model([pack("m", [
            tool("p", [stage("p1")], roles=["alpha"]),
            tool("q", [stage("q1")], roles=["alpha"], status="recognized"),
        ])])
        tools = {t["tool"]: t for t in m.compute({"fulfilled": ["q1"]})["tools"]}
        self.assertEqual(tools["q"], {"tool": "q", "name": "Q", "roles": ["alpha"], "status": "recognized", "pack": "m", "out": False})
        self.assertTrue(tools["p"]["out"])

    def test_workable_is_the_backlog_without_what_waits(self):
        out = chain().compute({"fulfilled": ["a1"]})
        self.assertEqual(out["tracks"]["Safety Net"]["workable"], ["a2"])
        self.assertEqual(out["tracks"]["Guardrails"]["workable"], [])
        self.assertEqual(chain().compute(onboarded=False)["tracks"]["Safety Net"]["workable"], [])

    def test_the_tree_lists_every_stage_with_its_edges(self):
        stages = {s["stage"]: s for s in chain().compute()["tree"]["stages"]}
        self.assertEqual(stages["a2"]["requires"], ["a1"])
        self.assertEqual(stages["g1"]["track"], "Guardrails")
        self.assertEqual(stages["b1"]["roles"], ["beta"])

    def test_without_the_operations_section_nothing_can_be_worked(self):
        out = chain().compute(onboarded=False)
        self.assertFalse(out["prerequisites"]["onboarding-setup"])
        self.assertTrue(all("onboarding-setup" in w["reason"] for w in out["tracks"]["Safety Net"]["withheld"]))
        self.assertEqual({w["node"] for w in out["tracks"]["Safety Net"]["withheld"]}, {"a1", "a2", "b1"})

    def test_the_prerequisites_are_never_in_a_track(self):
        out = chain().compute()
        listed = {n["node"] for t in out["tracks"].values() for n in t["nodes"]}
        self.assertFalse(listed & {"git", "onboarding-setup"})


class RequiresTests(unittest.TestCase):
    def test_a_stage_waits_for_its_required_parent(self):
        out = chain().compute()
        reasons = {w["node"]: w["reason"] for w in out["tracks"]["Safety Net"]["withheld"]}
        self.assertNotIn("a1", reasons)
        self.assertEqual(reasons["a2"], "blocked by required parent a1")
        out = chain().compute({"fulfilled": ["a1"]})
        self.assertEqual(out["tracks"]["Safety Net"]["backlog"], ["a2", "b1"])
        self.assertEqual([w["node"] for w in out["tracks"]["Safety Net"]["withheld"]], ["b1"])

    def test_a_rejected_parent_closes_the_child_and_everything_below(self):
        out = chain().compute({"rejected": {"a1": None}})
        self.assertEqual(out["closed_by_rejection"], ["a2", "b1", "g1"])
        self.assertEqual(out["tracks"]["Safety Net"]["backlog"], [])
        reasons = {w["node"]: w["reason"] for w in out["tracks"]["Safety Net"]["withheld"]}
        self.assertEqual(reasons["a2"], "closed — a1 was declined")
        self.assertEqual(reasons["b1"], "closed — a1 was declined")
        self.assertTrue(out["safety_net_fulfilled"])

    def test_a_rejected_stage_is_neither_in_the_backlog_nor_withheld_nor_closed(self):
        out = chain().compute({"rejected": {"b1": None}})
        self.assertNotIn("b1", out["tracks"]["Safety Net"]["backlog"])
        self.assertNotIn("b1", [w["node"] for w in out["tracks"]["Safety Net"]["withheld"]])
        self.assertNotIn("b1", out["closed_by_rejection"])

    def test_an_any_of_group_needs_one_member_and_closes_when_all_are_gone(self):
        m = Model([pack("m", [
            tool("a", [stage("a1")], roles=["alpha"]),
            tool("b", [stage("b1")], roles=["beta"]),
            tool("c", [stage("c1", requires=[["a1", "b1"]])], roles=["gamma"]),
        ])])
        waiting = {w["node"]: w["reason"] for w in m.compute()["tracks"]["Safety Net"]["withheld"]}
        self.assertIn("none of the alternatives fulfilled: a1, b1", waiting["c1"])
        self.assertNotIn("c1", [w["node"] for w in m.compute({"fulfilled": ["b1"]})["tracks"]["Safety Net"]["withheld"]])
        self.assertNotIn("c1", m.compute({"rejected": {"a1": None}})["closed_by_rejection"])
        self.assertIn("c1", m.compute({"rejected": {"a1": None, "b1": None}})["closed_by_rejection"])

    def test_an_any_of_group_with_a_recognized_member_closes_once_the_other_is_rejected(self):
        m = Model([pack("m", [
            tool("a", [stage("a1")], roles=["alpha"]),
            tool("r", [stage("r1")], roles=["beta"], status="recognized"),
            tool("c", [stage("c1", requires=[["a1", "r1"]])], roles=["gamma"]),
        ])])
        self.assertIn("c1", m.compute({"rejected": {"a1": None}})["closed_by_rejection"])
        self.assertNotIn("c1", m.compute({"rejected": {"a1": None}, "fulfilled": ["r1"]})["closed_by_rejection"])
        self.assertNotIn("c1", m.compute()["closed_by_rejection"])

    def test_a_diamond_closes_once(self):
        m = Model([pack("m", [
            tool("a", [stage("a1")], roles=["alpha"]),
            tool("b", [stage("b1", requires=["a1"])], roles=["beta"]),
            tool("c", [stage("c1", requires=["a1"])], roles=["gamma"]),
            tool("d", [stage("d1", requires=["b1", "c1"])], roles=["delta"]),
        ])])
        self.assertEqual(m.compute({"rejected": {"a1": None}})["closed_by_rejection"], ["b1", "c1", "d1"])

    def test_a_parent_in_a_pack_that_does_not_apply_closes_the_child(self):
        m = Model([
            pack("generic", [tool("g", [stage("g1")], roles=["alpha"])]),
            pack("extra", [tool("x", [stage("x1", requires=["g1"])], roles=["beta"])]),
            pack("later", [tool("y", [stage("y1", requires=["x1"])], roles=["gamma"])]),
        ])
        out = m.compute({"packs": ["generic", "later"]})
        self.assertEqual(out["closed_by_rejection"], ["y1"])


class GuardrailsTests(unittest.TestCase):
    def test_guardrails_wait_for_the_safety_net(self):
        out = chain().compute({"fulfilled": ["a1"]})
        self.assertEqual(out["tracks"]["Guardrails"]["withheld"], [{"node": "g1", "reason": "waiting on the Safety Net"}])
        self.assertFalse(out["safety_net_fulfilled"])

    def test_the_safety_net_is_fulfilled_once_every_stage_is_decided(self):
        out = chain().compute({"fulfilled": ["a1", "a2"], "rejected": {"b1": None}})
        self.assertTrue(out["safety_net_fulfilled"])
        self.assertTrue(out["tracks"]["Safety Net"]["fulfilled"])
        self.assertEqual(out["tracks"]["Guardrails"]["withheld"], [])

    def test_a_stage_closed_by_a_rejection_counts_as_decided(self):
        self.assertTrue(chain().compute({"rejected": {"a1": None}})["safety_net_fulfilled"])

    def test_a_state_handed_in_for_the_computed_state_does_not_exist(self):
        with self.assertRaises(tp.SeedError), tempfile.TemporaryDirectory() as d:
            path = pathlib.Path(d) / "s.json"
            path.write_text('{"fulfilled": ["structural-scan"]}')
            tp.load_seed(path, chain().load())


class AfterTests(unittest.TestCase):
    def model(self):
        return Model([pack("m", [
            tool("a", [stage("a1")], roles=["alpha"]),
            tool("b", [stage("b1", after=["a1"])], roles=["beta"]),
        ])])

    def test_a_stage_waits_until_its_predecessor_is_decided(self):
        out = self.model().compute()
        self.assertEqual(out["tracks"]["Safety Net"]["withheld"], [{"node": "b1", "reason": "waiting on: a1"}])

    def test_fulfilled_releases_it(self):
        self.assertEqual(self.model().compute({"fulfilled": ["a1"]})["tracks"]["Safety Net"]["withheld"], [])

    def test_rejected_releases_it(self):
        out = self.model().compute({"rejected": {"a1": None}})
        self.assertEqual(out["tracks"]["Safety Net"]["withheld"], [])
        self.assertEqual(out["tracks"]["Safety Net"]["backlog"], ["b1"])

    def test_a_predecessor_closed_by_a_rejection_releases_it(self):
        m = Model([pack("m", [
            tool("p", [stage("p1")], roles=["alpha"]),
            tool("a", [stage("a1", requires=["p1"])], roles=["beta"]),
            tool("b", [stage("b1", after=["a1"])], roles=["gamma"]),
        ])])
        self.assertEqual([w["node"] for w in m.compute({"rejected": {"p1": None}})["tracks"]["Safety Net"]["withheld"]], ["a1"])
        self.assertNotIn("b1", [w["node"] for w in m.compute({"rejected": {"p1": None}})["tracks"]["Safety Net"]["withheld"]])

    def test_it_waits_on_every_predecessor(self):
        m = Model([pack("m", [
            tool("a", [stage("a1")], roles=["alpha"]),
            tool("b", [stage("b1")], roles=["beta"]),
            tool("c", [stage("c1", after=["a1", "b1"])], roles=["gamma"]),
        ])])
        out = m.compute({"fulfilled": ["a1"]})
        self.assertEqual([w for w in out["tracks"]["Safety Net"]["withheld"] if w["node"] == "c1"][0]["reason"], "waiting on: b1")


class RolesAndToolsTests(unittest.TestCase):
    def model(self):
        """Role alpha: tool p (recommended, two stages) or tool q (recognized). rr requires the Role."""
        return Model([pack("m", [
            tool("p", [stage("p1"), stage("p2", requires=["p1"])], roles=["alpha"]),
            tool("q", [stage("q1")], roles=["alpha"], status="recognized"),
            tool("r", [stage("rr", requires=["alpha"])], roles=["beta"]),
        ])])

    def test_a_recognized_tool_is_never_proposed(self):
        out = self.model().compute()
        self.assertEqual([n["node"] for n in out["tracks"]["Safety Net"]["nodes"]], ["p1", "p2", "rr"])
        self.assertNotIn("q1", out["tracks"]["Safety Net"]["backlog"])

    def test_a_role_requirement_waits_until_a_tool_fills_the_role(self):
        reasons = {w["node"]: w["reason"] for w in self.model().compute()["tracks"]["Safety Net"]["withheld"]}
        self.assertEqual(reasons["rr"], "blocked — no Tool fills the Role alpha")
        out = self.model().compute({"fulfilled": ["p1"]})
        self.assertIn("rr", out["tracks"]["Safety Net"]["backlog"])
        self.assertNotIn("rr", [w["node"] for w in out["tracks"]["Safety Net"]["withheld"]])

    def test_a_recognized_tool_that_is_there_fills_the_role_and_takes_the_other_tools_place(self):
        out = self.model().compute({"fulfilled": ["q1"]})
        self.assertEqual({r["role"]: r["filled_by"] for r in out["roles"]}["alpha"], "q")
        self.assertEqual([n["node"] for n in out["tracks"]["Safety Net"]["nodes"]], ["rr"])
        self.assertEqual(out["tracks"]["Safety Net"]["backlog"], ["rr"])
        self.assertEqual(out["tracks"]["Safety Net"]["withheld"], [])
        self.assertTrue(self.model().compute({"fulfilled": ["q1", "rr"]})["safety_net_fulfilled"])

    def test_when_both_are_there_the_recommended_tool_stays(self):
        out = self.model().compute({"fulfilled": ["p1", "q1"]})
        self.assertEqual({r["role"]: r["filled_by"] for r in out["roles"]}["alpha"], "p")
        self.assertIn("p2", out["tracks"]["Safety Net"]["backlog"])

    def test_a_tool_that_took_its_place_does_not_hold_the_after_of_others(self):
        m = Model([pack("m", [
            tool("p", [stage("p1")], roles=["alpha"]),
            tool("q", [stage("q1")], roles=["alpha"], status="recognized"),
            tool("s", [stage("s1", after=["p1"])], roles=["beta"]),
        ])])
        self.assertEqual(m.compute({"fulfilled": ["q1"]})["tracks"]["Safety Net"]["withheld"], [])
        self.assertEqual(m.compute()["tracks"]["Safety Net"]["withheld"], [{"node": "s1", "reason": "waiting on: p1"}])

    def test_rejecting_a_tool_closes_its_stages_and_not_the_other_tools_of_the_role(self):
        m = Model([pack("m", [
            tool("p", [stage("p1")], roles=["alpha"]),
            tool("s", [stage("s1")], roles=["alpha"]),
            tool("r", [stage("rr", requires=["alpha"])], roles=["beta"]),
        ])])
        out = m.compute({"rejected": {"p": None}})
        self.assertEqual(out["closed_by_rejection"], ["p1"])
        self.assertNotIn("p1", out["tracks"]["Safety Net"]["backlog"])
        self.assertNotIn("p1", [w["node"] for w in out["tracks"]["Safety Net"]["withheld"]])
        self.assertEqual(out["tracks"]["Safety Net"]["backlog"], ["s1", "rr"])
        self.assertEqual({r["role"]: r["filled_by"] for r in out["roles"]}["alpha"], None)

    def test_rejecting_a_role_closes_its_tools_and_whatever_requires_it(self):
        out = self.model().compute({"rejected": {"alpha": None}})
        self.assertEqual(out["closed_by_rejection"], ["p1", "p2", "q1", "rr"])
        self.assertEqual({w["node"]: w["reason"] for w in out["tracks"]["Safety Net"]["withheld"]}["rr"], "closed — alpha was declined")

    def test_a_role_nothing_can_fill_any_more_closes_what_requires_it(self):
        out = self.model().compute({"rejected": {"p": None}})
        self.assertIn("rr", out["closed_by_rejection"])
        self.assertEqual({w["node"]: w["reason"] for w in out["tracks"]["Safety Net"]["withheld"]}["rr"],
                         "closed — no Tool can fill the Role alpha any more")

    def test_a_role_with_only_a_recognized_tool_that_is_missing_closes_nothing_without_a_rejection(self):
        m = Model([pack("m", [
            tool("q", [stage("q1")], roles=["alpha"], status="recognized"),
            tool("r", [stage("rr", requires=["alpha"])], roles=["beta"]),
        ])])
        self.assertEqual(m.compute()["closed_by_rejection"], [])

    def test_a_single_stage_tool_rejected_by_its_shared_slug_is_one_rejection(self):
        m = Model([pack("m", [tool("b1", [stage("b1")])])])
        self.assertEqual(m.compute({"rejected": {"b1": None}})["tracks"]["Safety Net"]["backlog"], [])


class AppliesWhenTests(unittest.TestCase):
    def model(self):
        return Model([
            pack("generic", [tool("g", [stage("g1")], roles=["alpha"])]),
            pack("extra", [tool("x", [stage("x1"), stage("x2", requires=["x1"], applies_when="Only sometimes.")], roles=["beta"])]),
        ])

    def test_every_pack_applies_without_a_list(self):
        self.assertEqual(self.model().compute()["packs"], ["generic", "extra"])

    def test_a_pack_that_does_not_apply_is_absent_everywhere(self):
        out = self.model().compute({"packs": ["generic"]})
        self.assertEqual(out["packs"], ["generic"])
        self.assertEqual([n["node"] for n in out["tracks"]["Safety Net"]["nodes"]], ["g1"])
        self.assertEqual(out["tracks"]["Safety Net"]["backlog"], ["g1"])
        self.assertTrue(self.model().compute({"packs": ["generic"], "fulfilled": ["g1"]})["safety_net_fulfilled"])

    def test_a_stage_that_does_not_apply_is_absent(self):
        out = self.model().compute({"not_applicable": ["x2"]})
        self.assertEqual(out["tracks"]["Safety Net"]["backlog"], ["g1", "x1"])
        self.assertNotIn("x2", [n["node"] for n in out["tracks"]["Safety Net"]["nodes"]])

    def test_a_stage_with_its_own_condition_is_in_the_model(self):
        self.assertEqual(self.model().load()["stages"]["x2"]["applies_when"], "Only sometimes.")


class RuntimeTests(unittest.TestCase):
    def model(self):
        return Model([pack("m", [
            tool("a", [stage("a1"), stage("a2", requires=["a1"])], roles=["alpha"], min_runtime={"php": "7.2"}),
            tool("b", [stage("b1")], roles=["beta"], min_runtime={"node": "18"}),
        ])])

    def test_a_tool_below_its_minimum_runtime_is_blocked_at_its_first_stage(self):
        out = self.model().compute({"runtime": {"php": "7.0"}})
        self.assertEqual(out["runtime_blocked"], [{"node": "a1", "reason": "php runtime 7.0 is below a1's minimum php >= 7.2"}])
        reasons = {w["node"]: w["reason"] for w in out["tracks"]["Safety Net"]["withheld"]}
        self.assertEqual(reasons["a1"], out["runtime_blocked"][0]["reason"])
        self.assertEqual(reasons["a2"], "blocked by required parent a1")
        self.assertNotIn("b1", reasons)

    def test_the_minimum_itself_and_above_are_not_blocked(self):
        for version in ("7.2", "7.2.0", "8.1", "^8.0", ">=7.4"):
            self.assertEqual(self.model().compute({"runtime": {"php": version}})["runtime_blocked"], [], version)

    def test_versions_are_compared_by_numbers_not_by_text(self):
        m = Model([pack("m", [tool("a", [stage("a1")], min_runtime={"php": "8.10"})])])
        self.assertEqual(len(m.compute({"runtime": {"php": "8.9"}})["runtime_blocked"]), 1)
        self.assertEqual(m.compute({"runtime": {"php": "8.10.1"}})["runtime_blocked"], [])

    def test_a_version_it_cannot_read_blocks_nothing(self):
        for version in ("latest", "", "bookworm"):
            self.assertEqual(self.model().compute({"runtime": {"php": version}})["runtime_blocked"], [], version)

    def test_no_runtime_handed_in_blocks_nothing(self):
        self.assertEqual(self.model().compute()["runtime_blocked"], [])
        self.assertEqual(self.model().compute({"runtime": {"node": "20"}})["runtime_blocked"], [])

    def test_another_runtime_is_compared_on_its_own(self):
        out = self.model().compute({"runtime": {"php": "8.2", "node": "16"}})
        self.assertEqual([b["node"] for b in out["runtime_blocked"]], ["b1"])

    def test_a_blocked_stage_that_was_rejected_is_still_listed(self):
        out = self.model().compute({"runtime": {"php": "7.0"}, "rejected": {"a1": {"php": "8.1"}}})
        self.assertEqual([b["node"] for b in out["runtime_blocked"]], ["a1"])

    def test_a_pack_that_does_not_apply_is_not_checked(self):
        m = Model([
            pack("generic", [tool("g", [stage("g1")], roles=["alpha"])]),
            pack("php", [tool("a", [stage("a1")], roles=["beta"], min_runtime={"php": "7.2"})]),
        ])
        self.assertEqual(m.compute({"packs": ["generic"], "runtime": {"php": "5.6"}})["runtime_blocked"], [])


class ReversalTests(unittest.TestCase):
    def model(self):
        return Model([pack("m", [
            tool("a", [stage("a1")], roles=["alpha"]),
            tool("b", [stage("b1")], roles=["beta"]),
        ])])

    def test_a_rejection_whose_blocker_the_runtime_now_meets_is_reported(self):
        out = self.model().compute({"rejected": {"a1": {"php": "7.4"}, "b1": {"php": "8.1"}}, "runtime": {"php": "8.0"}})
        self.assertEqual([r["node"] for r in out["reversals"]], ["a1"])
        self.assertIn("8.0", out["reversals"][0]["reason"])

    def test_a_rejection_without_a_blocker_is_never_reported(self):
        self.assertEqual(self.model().compute({"rejected": {"a1": None}, "runtime": {"php": "9.0"}})["reversals"], [])

    def test_no_runtime_means_no_reversal(self):
        self.assertEqual(self.model().compute({"rejected": {"a1": {"php": "7.4"}}})["reversals"], [])

    def test_a_blocker_may_name_another_runtime(self):
        out = self.model().compute({"rejected": {"a1": {"node": "20"}}, "runtime": {"node": "22", "php": "5.6"}})
        self.assertEqual([r["node"] for r in out["reversals"]], ["a1"])

    def test_a_rejected_role_or_tool_can_be_reversed_too(self):
        out = self.model().compute({"rejected": {"alpha": {"php": "7.4"}, "b": {"php": "7.4"}}, "runtime": {"php": "8.0"}})
        self.assertEqual([r["node"] for r in out["reversals"]], ["alpha", "b"])


class SuiteDataTests(unittest.TestCase):
    """The suite's own Packs, computed with a seed a run would hand in."""

    @classmethod
    def setUpClass(cls):
        cls.model = tp.load_model()

    def compute(self, seed):
        repo_tmp, repo = make_repo()
        with repo_tmp:
            full = {"fulfilled": [], "rejected": {}, "packs": None, "not_applicable": [], "runtime": {}}
            full.update(seed)
            return tp.compute(repo, self.model, full)

    def test_the_tracks_hold_the_stages_a_ticket_is_filed_for(self):
        out = self.compute({})
        self.assertEqual(len(out["tracks"]["Safety Net"]["nodes"]), 18)
        self.assertEqual(len(out["tracks"]["Guardrails"]["nodes"]), 12)
        listed = {n["node"] for t in out["tracks"].values() for n in t["nodes"]}
        self.assertNotIn("psalm", listed)

    def test_names_come_from_the_pack(self):
        nodes = {n["node"]: n for t in self.compute({})["tracks"].values() for n in t["nodes"]}
        self.assertEqual(nodes["phpstan-level-3"]["name"], "PHPStan Level 3")
        self.assertEqual(nodes["editorconfig"]["name"], ".editorconfig")
        self.assertEqual(nodes["psr-4"]["tool"], None)

    def test_a_rejected_composer_closes_the_php_pack(self):
        out = self.compute({"rejected": {"composer": None}})
        for slug in ("psr-4", "php-cs-fixer", "phpunit", "phpstan-level-0", "rector-type-coverage", "composer-audit", "semgrep" if False else "phpmd"):
            self.assertIn(slug, out["closed_by_rejection"], slug)
        self.assertNotIn("ci-runner", out["closed_by_rejection"])

    def test_without_the_php_pack_the_safety_net_needs_only_the_generic_stages(self):
        out = self.compute({"packs": ["generic"], "fulfilled": ["ci-runner", "editorconfig"]})
        self.assertTrue(out["safety_net_fulfilled"])
        self.assertEqual([w["node"] for w in out["tracks"]["Guardrails"]["withheld"]], [])
        self.assertEqual(out["tracks"]["Guardrails"]["backlog"], ["secret-detection"])

    def test_psalm_takes_the_place_of_phpstan(self):
        out = self.compute({"fulfilled": ["composer", "psalm"]})
        filled = {r["role"]: r["filled_by"] for r in out["roles"]}
        self.assertEqual(filled["static-analysis"], "psalm")
        listed = {n["node"] for t in out["tracks"].values() for n in t["nodes"]}
        self.assertFalse({s for s in listed if s.startswith("phpstan-")})
        self.assertIn("rector-php-set", out["tracks"]["Safety Net"]["backlog"])
        reasons = {w["node"]: w["reason"] for w in out["tracks"]["Safety Net"]["withheld"]}
        self.assertEqual(reasons["rector-php-set"], "waiting on: php-cs-fixer")
        self.assertIn("psalm-taint-analysis", out["tracks"]["Safety Net"]["backlog"])

    def test_pint_and_ecs_take_the_place_of_php_cs_fixer(self):
        for tool in ("pint", "ecs"):
            out = self.compute({"fulfilled": ["composer", "phpstan-level-0", tool]})
            filled = {r["role"]: r["filled_by"] for r in out["roles"]}
            self.assertEqual(filled["code-style"], tool)
            safety_net = out["tracks"]["Safety Net"]
            self.assertNotIn("php-cs-fixer", {n["node"] for n in safety_net["nodes"]})
            self.assertNotIn(tool, {n["node"] for n in safety_net["nodes"]})
            self.assertIn("rector-php-set", safety_net["workable"])

    def test_phpstan_is_proposed_when_the_role_is_empty(self):
        out = self.compute({"fulfilled": ["composer"]})
        self.assertIn("phpstan-level-0", out["tracks"]["Safety Net"]["backlog"])
        self.assertEqual({w["node"] for w in out["tracks"]["Safety Net"]["withheld"] if w["node"] == "phpstan-level-0"}, set())

    def test_rector_waits_for_static_analysis_and_for_the_code_style_decision(self):
        reasons = {w["node"]: w["reason"] for w in self.compute({"fulfilled": ["composer"]})["tracks"]["Safety Net"]["withheld"]}
        self.assertEqual(reasons["rector-php-set"], "blocked — no Tool fills the Role static-analysis")
        reasons = {w["node"]: w["reason"] for w in self.compute({"fulfilled": ["composer", "phpstan-level-0"]})["tracks"]["Safety Net"]["withheld"]}
        self.assertEqual(reasons["rector-php-set"], "waiting on: php-cs-fixer")

    def test_the_phpstan_levels_are_a_chain(self):
        stages = self.model["stages"]
        for n in range(1, 11):
            self.assertEqual(stages[f"phpstan-level-{n}"]["requires"], [f"phpstan-level-{n - 1}"])
        self.assertEqual(stages["phpstan-level-5"]["track"], "Safety Net")
        self.assertEqual(stages["phpstan-level-6"]["track"], "Guardrails")

    def test_composer_audit_applies_only_to_a_repository_with_a_real_dependency(self):
        self.assertIn("applies_when", self.model["stages"]["composer-audit"])
        out = self.compute({"not_applicable": ["composer-audit"]})
        self.assertNotIn("composer-audit", out["tracks"]["Guardrails"]["backlog"])

    def test_a_php_floor_below_a_tools_minimum_blocks_its_first_stage(self):
        out = self.compute({"runtime": {"php": "5.6"}})
        self.assertEqual({b["node"] for b in out["runtime_blocked"]}, {"composer-audit", "phpstan-level-0"})
        out = self.compute({"runtime": {"php": "5.2"}})
        self.assertEqual({b["node"] for b in out["runtime_blocked"]}, {"composer-audit", "phpstan-level-0", "php-cs-fixer", "phpunit"})
        self.assertEqual(self.compute({"runtime": {"php": "8.3"}})["runtime_blocked"], [])

    def test_the_tracks_partition_the_ticketable_stages(self):
        out = self.compute({})
        sn, gr = ({n["node"] for n in out["tracks"][t]["nodes"]} for t in ("Safety Net", "Guardrails"))
        self.assertFalse(sn & gr)

    def test_the_tree_output_names_every_stage_once(self):
        slugs = [s["stage"] for s in self.compute({})["tree"]["stages"]]
        self.assertEqual(len(slugs), len(set(slugs)))
        self.assertEqual(slugs, self.model["stage_order"])

    def test_every_details_file_exists(self):
        for slug, t in self.model["tools"].items():
            self.assertTrue((t["dir"] / t["details"]).is_file(), f"{slug}: {t['details']}")


class PortabilityTests(unittest.TestCase):
    def test_the_model_loads_whatever_the_working_directory(self):
        import os
        cwd = os.getcwd()
        with tempfile.TemporaryDirectory() as d:
            try:
                os.chdir(d)
                self.assertIn("composer", tp.load_model()["stages"])
            finally:
                os.chdir(cwd)

    def test_the_packs_are_siblings_of_the_module(self):
        self.assertEqual(tp.PACKS_DIR, _REFERENCES / "packs")
        self.assertEqual(tp.ROLES_JSON, _REFERENCES / "roles.json")


if __name__ == "__main__":
    unittest.main()
