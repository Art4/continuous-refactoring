"""Tests for deterministic tooling tree parser (skills/refactor-scan/references/tooling_tree.py)

TDD: verify tree parsing, detection, and 10-step roadmap generation against fixtures.
"""

import importlib.util
import json
import os
import pathlib
import tempfile
import unittest

# importlib, not a dotted import: "refactor-scan"'s hyphen makes
# `skills.refactor_scan...` an invalid package path.
_MODULE_PATH = pathlib.Path(__file__).resolve().parents[1] / "skills" / "refactor-scan" / "references" / "tooling_tree.py"
_spec = importlib.util.spec_from_file_location("tooling_tree", _MODULE_PATH)
tooling_tree = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(tooling_tree)

load_tree = tooling_tree.load_tree
detect_nodes = tooling_tree.detect_nodes
roadmap = tooling_tree.roadmap
next_candidates = tooling_tree.next_candidates
withheld_candidates = tooling_tree.withheld_candidates
php_version_reversal_findings = tooling_tree.php_version_reversal_findings
php_floor_precheck = tooling_tree.php_floor_precheck
_is_baseline_empty = tooling_tree._is_baseline_empty


class LoadTreeTests(unittest.TestCase):
    def test_edges_parsed(self):
        tree = load_tree()
        self.assertGreaterEqual(len(tree["edges"]), 15)
        # generic root (ADR-0008): git -> loop-config, loop-config -> PHP tree roots
        self.assertIn({"from": "git", "to": "loop-config", "type": "required"}, tree["edges"])
        self.assertIn({"from": "loop-config", "to": "composer", "type": "required"}, tree["edges"])
        # check required edge
        self.assertIn({"from": "phpstan-level-0-baseline", "to": "phpstan-level-1", "type": "required"}, tree["edges"])
        # recommended
        self.assertIn({"from": "php-cs-fixer", "to": "rector-dead-code", "type": "recommended"}, tree["edges"])
        # resolved (ADR-0008): PHP-tree leaves gate structural-scan
        self.assertIn({"from": "composer-audit", "to": "structural-scan", "type": "resolved"}, tree["edges"])
        # composer-audit's MR scope now includes wiring into CI (absorbs
        # former ticket 10), so it needs ci-runner too, not just composer.
        self.assertIn({"from": "ci-runner", "to": "composer-audit", "type": "required"}, tree["edges"])
        # ticket 01: `.editorconfig` node — required from loop-config (its own
        # prerequisite, mirroring composer/ci-runner), recommended into
        # php-cs-fixer (settle basic formatting before style-tool adoption).
        self.assertIn({"from": "loop-config", "to": "editorconfig", "type": "required"}, tree["edges"])
        self.assertIn({"from": "editorconfig", "to": "php-cs-fixer", "type": "recommended"}, tree["edges"])
        # ticket 41: editorconfig also resolves into structural-scan —
        # declared in tooling-tree.md's own edge table (both endpoints are
        # generic-root nodes), not php-tooling-tree.md's.
        self.assertIn({"from": "editorconfig", "to": "structural-scan", "type": "resolved"}, tree["edges"])

    def test_order_contains_nodes(self):
        tree = load_tree()
        for n in ["git", "loop-config", "composer", "phpstan-level-0-baseline", "phpstan-level-1", "rector-dead-code", "structural-scan"]:
            self.assertIn(n, tree["order"])

    def test_resolved_parents_of_structural_scan(self):
        tree = load_tree()
        leaves = set(tree["resolved_parents"]["structural-scan"])
        self.assertEqual(
            leaves,
            {
                "composer-audit",
                "phpunit",
                "test-runner-if-missing",
                "php-cs-fixer",
                "phpstan-level-3",
                "rector-dead-code",
                "rector-type-coverage",
                # ticket 41: editorconfig, an 8th resolved leaf, declared in
                # tooling-tree.md's own edge table (generic-to-generic).
                "editorconfig",
            },
        )


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
            self.assertFalse(d["loop-config"]["fulfilled"])
            self.assertFalse(d["composer"]["fulfilled"])
            self.assertFalse(d["phpstan-level-0-baseline"]["fulfilled"])
            self.assertFalse(d["structural-scan"]["fulfilled"])
        finally:
            tmp.cleanup()

    def test_loop_config_fulfilled_when_config_md_present(self):
        tmp, root = self._make_repo({
            "docs/refactoring/config.md": "# Refactoring Loop Config\n\n**Cadence:** weekly\n",
        })
        try:
            d = detect_nodes(root)
            self.assertTrue(d["loop-config"]["fulfilled"])
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


class StructuralScanGateTests(unittest.TestCase):
    """ADR-0008: structural-scan's `resolved` edges — a rejected leaf still
    unblocks the node, unlike a standard required edge."""

    def _make_repo(self, files: dict):
        tmp = tempfile.TemporaryDirectory()
        root = pathlib.Path(tmp.name)
        for rel, content in files.items():
            p = root / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content)
        (root / ".git").mkdir()
        return tmp, root

    def _fully_tooled_files(self):
        return {
            "composer.json": json.dumps({
                "require-dev": {
                    "phpstan/phpstan": "^1.0",
                    "phpunit/phpunit": "^10.0",
                    "friendsofphp/php-cs-fixer": "^3.0",
                },
            }),
            "composer.lock": "{}",
            ".php-cs-fixer.php": "<?php return [];",
            "phpstan.neon": "parameters:\n    level: 3\n",
            "phpstan-baseline.neon": "parameters:\n    ignoreErrors: []\n",
            "rector.php": "<?php // DeadCode Type",
            # ticket 41: editorconfig is now an 8th structural-scan leaf —
            # this "fully tooled" fixture needs it decided (fulfilled) too.
            ".editorconfig": "root = true\n\n[*]\ncharset = utf-8\n",
            # ci-runner + composer-audit's own CI-gate fulfilment (no `require`
            # dep here, so composer-audit only resolves via the "every other
            # leaf resolved" fallback — see ComposerAuditGateTests). Also
            # gates phpunit's/phpstan-level-0-baseline's own CI-gating check
            # (ticket 34) — omitting either invocation here would make this
            # "fully tooled" fixture stop being fully tooled.
            ".github/workflows/ci.yml": (
                "jobs:\n"
                "  audit:\n"
                "    steps:\n"
                "      - run: composer audit\n"
                "      - run: vendor/bin/phpunit\n"
                "      - run: vendor/bin/phpstan analyse\n"
            ),
        }

    def test_unresolved_when_only_editorconfig_missing(self):
        # Every other leaf fulfilled, editorconfig absent and undecided —
        # structural-scan must stay closed on editorconfig alone (ticket 41).
        files = self._fully_tooled_files()
        del files[".editorconfig"]
        tmp, root = self._make_repo(files)
        try:
            d = detect_nodes(root)
            self.assertFalse(d["structural-scan"]["fulfilled"])
            self.assertEqual(d["structural-scan"]["details"]["unresolved"], ["editorconfig"])
        finally:
            tmp.cleanup()

    def test_resolves_via_editorconfig_rejection(self):
        # A rejected editorconfig still unblocks structural-scan, same as
        # every other resolved leaf (ADR-0008's design intent).
        files = self._fully_tooled_files()
        del files[".editorconfig"]
        tmp, root = self._make_repo(files)
        try:
            (root / "docs" / "refactoring" / "out-of-scope").mkdir(parents=True)
            (root / "docs" / "refactoring" / "out-of-scope" / "editorconfig.md").write_text("rejected\n")
            d = detect_nodes(root)
            self.assertTrue(d["structural-scan"]["fulfilled"], d["structural-scan"])
        finally:
            tmp.cleanup()

    def test_unfulfilled_when_leaves_missing(self):
        tmp, root = self._make_repo({})
        try:
            d = detect_nodes(root)
            self.assertFalse(d["structural-scan"]["fulfilled"])
            self.assertIn("composer-audit", d["structural-scan"]["details"]["unresolved"])
        finally:
            tmp.cleanup()

    def test_fulfilled_when_every_leaf_fulfilled(self):
        tmp, root = self._make_repo(self._fully_tooled_files())
        try:
            # composer-audit is genuinely fulfilled here (the fixture's CI job
            # runs `composer audit`) — every leaf fulfilled by file inspection,
            # no rejection needed.
            d = detect_nodes(root)
            self.assertTrue(d["composer-audit"]["fulfilled"], d["composer-audit"])
            self.assertTrue(d["structural-scan"]["fulfilled"], d["structural-scan"])
        finally:
            tmp.cleanup()

    def test_rejected_leaf_still_resolves_unlike_required_edge(self):
        # Every leaf fulfilled except rector-type-coverage, which is rejected
        # (not fulfilled) — structural-scan must still open, unlike a normal
        # required edge which would close permanently on a rejection.
        files = self._fully_tooled_files()
        files["rector.php"] = "<?php // DeadCode rules only"
        tmp, root = self._make_repo(files)
        try:
            (root / "docs" / "refactoring" / "out-of-scope").mkdir(parents=True)
            (root / "docs" / "refactoring" / "out-of-scope" / "rector-type-coverage.md").write_text("rejected: declined\n")
            d = detect_nodes(root)
            self.assertTrue(d["composer-audit"]["fulfilled"], d["composer-audit"])  # genuinely fulfilled, not rejected
            self.assertFalse(d["rector-type-coverage"]["fulfilled"])
            self.assertTrue(d["structural-scan"]["fulfilled"], d["structural-scan"])
        finally:
            tmp.cleanup()


class ComposerAuditGateTests(unittest.TestCase):
    """php-tooling-tree.md's composer-audit stop conditions: proposable once
    ci-runner + composer are fulfilled, and (a real `require` dependency
    exists, or every other structural-scan leaf is already resolved)."""

    # CI exists (fulfils ci-runner) but doesn't run `composer audit` yet —
    # for eligibility tests, which must stay independent of composer-audit's
    # own fulfilment check (otherwise it'd be skipped as already-done, not
    # exercised as blocked/eligible for the right reason).
    _CI_YML_NO_AUDIT = "jobs:\n  lint:\n    steps:\n      - run: php -l\n"
    _CI_YML_WITH_AUDIT = "jobs:\n  audit:\n    steps:\n      - run: composer audit\n"

    def _make_repo(self, files: dict):
        tmp = tempfile.TemporaryDirectory()
        root = pathlib.Path(tmp.name)
        for rel, content in files.items():
            p = root / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content)
        (root / ".git").mkdir()
        return tmp, root

    def test_blocked_without_ci_runner_even_with_real_dep(self):
        tmp, root = self._make_repo({
            "composer.json": json.dumps({"require": {"acme/widgets": "^1.0"}}),
            "composer.lock": "{}",
        })
        try:
            nodes = [c["node"] for c in next_candidates(root, limit=10)]
            self.assertNotIn("composer-audit", nodes)
        finally:
            tmp.cleanup()

    def test_blocked_with_ci_but_only_platform_dependency(self):
        tmp, root = self._make_repo({
            "composer.json": json.dumps({"require": {"php": ">=8.1", "ext-json": "*"}}),
            "composer.lock": "{}",
            ".github/workflows/ci.yml": self._CI_YML_NO_AUDIT,
        })
        try:
            nodes = [c["node"] for c in next_candidates(root, limit=10)]
            self.assertNotIn("composer-audit", nodes)
        finally:
            tmp.cleanup()

    def test_eligible_with_real_dependency_and_ci(self):
        tmp, root = self._make_repo({
            "composer.json": json.dumps({"require": {"php": ">=8.1", "acme/widgets": "^1.0"}}),
            "composer.lock": "{}",
            ".github/workflows/ci.yml": self._CI_YML_NO_AUDIT,
        })
        try:
            nodes = [c["node"] for c in next_candidates(root, limit=10)]
            self.assertIn("composer-audit", nodes)
        finally:
            tmp.cleanup()

    def test_eligible_via_fallback_when_every_other_leaf_resolved(self):
        # No real dependency at all, but every other structural-scan leaf is
        # fulfilled — composer-audit must still eventually become proposable,
        # or structural-scan would never open on a dependency-free target.
        tmp, root = self._make_repo({
            "composer.json": json.dumps({
                "require-dev": {
                    "phpstan/phpstan": "^1.0",
                    "phpunit/phpunit": "^10.0",
                    "friendsofphp/php-cs-fixer": "^3.0",
                },
            }),
            "composer.lock": "{}",
            ".php-cs-fixer.php": "<?php return [];",
            "phpstan.neon": "parameters:\n    level: 3\n",
            "phpstan-baseline.neon": "parameters:\n    ignoreErrors: []\n",
            "rector.php": "<?php // DeadCode Type",
            # ticket 41: editorconfig is now among "every other leaf" too.
            ".editorconfig": "root = true\n\n[*]\ncharset = utf-8\n",
            # No `composer audit` here — deliberate (see docstring). Does
            # invoke phpunit/phpstan though, so phpunit/phpstan-level-3
            # genuinely resolve too (ticket 34's self-wiring); otherwise this
            # fixture would no longer have "every other leaf resolved".
            ".github/workflows/ci.yml": (
                "jobs:\n"
                "  build:\n"
                "    steps:\n"
                "      - run: vendor/bin/phpunit\n"
                "      - run: vendor/bin/phpstan analyse\n"
            ),
        })
        try:
            nodes = [c["node"] for c in next_candidates(root, limit=10)]
            self.assertIn("composer-audit", nodes)
        finally:
            tmp.cleanup()

    def test_fulfilled_once_ci_job_present(self):
        tmp, root = self._make_repo({
            "composer.json": json.dumps({"require": {"acme/widgets": "^1.0"}}),
            "composer.lock": "{}",
            ".github/workflows/ci.yml": self._CI_YML_WITH_AUDIT,
        })
        try:
            d = detect_nodes(root)
            self.assertTrue(d["composer-audit"]["fulfilled"])
        finally:
            tmp.cleanup()

    def test_not_fulfilled_without_ci_job(self):
        tmp, root = self._make_repo({
            "composer.json": json.dumps({"require": {"acme/widgets": "^1.0"}}),
            "composer.lock": "{}",
        })
        try:
            d = detect_nodes(root)
            self.assertFalse(d["composer-audit"]["fulfilled"])
        finally:
            tmp.cleanup()


class CiSelfWiringTests(unittest.TestCase):
    """Ticket 34: phpunit's and phpstan-level-0-baseline's own fulfilment
    checks self-wire a CI-gating requirement once ci-runner is fulfilled,
    instead of a separate phpunit-ci-job/phpstan-ci-job node."""

    def _make_repo(self, files: dict):
        tmp = tempfile.TemporaryDirectory()
        root = pathlib.Path(tmp.name)
        for rel, content in files.items():
            p = root / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content)
        (root / ".git").mkdir()
        return tmp, root

    _CI_YML_NO_TOOLS = "jobs:\n  lint:\n    steps:\n      - run: php -l\n"
    _CI_YML_PHPUNIT = "jobs:\n  test:\n    steps:\n      - run: vendor/bin/phpunit\n"
    _CI_YML_PEST = "jobs:\n  test:\n    steps:\n      - run: vendor/bin/pest\n"
    _CI_YML_PHPSTAN = "jobs:\n  analyse:\n    steps:\n      - run: vendor/bin/phpstan analyse\n"

    def test_phpunit_fulfilled_on_adoption_alone_without_ci(self):
        tmp, root = self._make_repo({
            "composer.json": json.dumps({"require-dev": {"phpunit/phpunit": "^10.0"}}),
            "composer.lock": "{}",
        })
        try:
            d = detect_nodes(root)
            self.assertTrue(d["phpunit"]["fulfilled"], d["phpunit"])
        finally:
            tmp.cleanup()

    def test_phpunit_not_fulfilled_when_ci_exists_but_doesnt_gate(self):
        tmp, root = self._make_repo({
            "composer.json": json.dumps({"require-dev": {"phpunit/phpunit": "^10.0"}}),
            "composer.lock": "{}",
            ".github/workflows/ci.yml": self._CI_YML_NO_TOOLS,
        })
        try:
            d = detect_nodes(root)
            self.assertFalse(d["phpunit"]["fulfilled"], d["phpunit"])
            self.assertIn("not gated in CI", d["phpunit"]["reason"])
        finally:
            tmp.cleanup()

    def test_phpunit_fulfilled_when_ci_gates_on_it(self):
        tmp, root = self._make_repo({
            "composer.json": json.dumps({"require-dev": {"phpunit/phpunit": "^10.0"}}),
            "composer.lock": "{}",
            ".github/workflows/ci.yml": self._CI_YML_PHPUNIT,
        })
        try:
            d = detect_nodes(root)
            self.assertTrue(d["phpunit"]["fulfilled"], d["phpunit"])
        finally:
            tmp.cleanup()

    def test_pest_requires_pest_invocation_not_phpunit(self):
        tmp, root = self._make_repo({
            "composer.json": json.dumps({"require-dev": {"pestphp/pest": "^2.0"}}),
            "composer.lock": "{}",
            ".github/workflows/ci.yml": self._CI_YML_PHPUNIT,  # gates phpunit, not pest
        })
        try:
            d = detect_nodes(root)
            self.assertFalse(d["phpunit"]["fulfilled"], d["phpunit"])
        finally:
            tmp.cleanup()

    def test_test_runner_if_missing_independent_of_ci_gating(self):
        # A runner is adopted (satisfies test-runner-if-missing) but not yet
        # CI-gated (phpunit stays unfulfilled) — the two nodes must diverge,
        # not track each other as they did before ticket 34.
        tmp, root = self._make_repo({
            "composer.json": json.dumps({"require-dev": {"phpunit/phpunit": "^10.0"}}),
            "composer.lock": "{}",
            ".github/workflows/ci.yml": self._CI_YML_NO_TOOLS,
        })
        try:
            d = detect_nodes(root)
            self.assertFalse(d["phpunit"]["fulfilled"], d["phpunit"])
            self.assertTrue(d["test-runner-if-missing"]["fulfilled"], d["test-runner-if-missing"])
        finally:
            tmp.cleanup()

    def test_roadmap_still_proposes_phpunit_for_ci_wiring(self):
        # Regression guard for the stale roadmap() skip this ticket removes:
        # test-runner-if-missing already fulfilled must not hide phpunit's
        # own still-open CI-gating candidate.
        tmp, root = self._make_repo({
            "composer.json": json.dumps({"require-dev": {"phpunit/phpunit": "^10.0"}}),
            "composer.lock": "{}",
            ".github/workflows/ci.yml": self._CI_YML_NO_TOOLS,
        })
        try:
            nodes = [c["node"] for c in next_candidates(root, limit=10)]
            self.assertIn("phpunit", nodes)
        finally:
            tmp.cleanup()

    def test_phpstan_p0_fulfilled_on_adoption_alone_without_ci(self):
        tmp, root = self._make_repo({
            "composer.json": json.dumps({"require-dev": {"phpstan/phpstan": "^1.0"}}),
            "composer.lock": "{}",
            "phpstan.neon": "parameters:\n    level: 0\n",
            "phpstan-baseline.neon": "parameters:\n    ignoreErrors: []\n",
        })
        try:
            d = detect_nodes(root)
            self.assertTrue(d["phpstan-level-0-baseline"]["fulfilled"], d["phpstan-level-0-baseline"])
        finally:
            tmp.cleanup()

    def test_phpstan_p0_not_fulfilled_when_ci_exists_but_doesnt_gate(self):
        tmp, root = self._make_repo({
            "composer.json": json.dumps({"require-dev": {"phpstan/phpstan": "^1.0"}}),
            "composer.lock": "{}",
            "phpstan.neon": "parameters:\n    level: 0\n",
            "phpstan-baseline.neon": "parameters:\n    ignoreErrors: []\n",
            ".github/workflows/ci.yml": self._CI_YML_NO_TOOLS,
        })
        try:
            d = detect_nodes(root)
            self.assertFalse(d["phpstan-level-0-baseline"]["fulfilled"], d["phpstan-level-0-baseline"])
            self.assertIn("not gated in CI", d["phpstan-level-0-baseline"]["reason"])
            # the level chain stays blocked too, via the normal required-edge check
            self.assertFalse(d["phpstan-level-1"]["fulfilled"])
        finally:
            tmp.cleanup()

    def test_phpstan_p0_fulfilled_when_ci_gates_on_it(self):
        tmp, root = self._make_repo({
            "composer.json": json.dumps({"require-dev": {"phpstan/phpstan": "^1.0"}}),
            "composer.lock": "{}",
            "phpstan.neon": "parameters:\n    level: 0\n",
            "phpstan-baseline.neon": "parameters:\n    ignoreErrors: []\n",
            ".github/workflows/ci.yml": self._CI_YML_PHPSTAN,
        })
        try:
            d = detect_nodes(root)
            self.assertTrue(d["phpstan-level-0-baseline"]["fulfilled"], d["phpstan-level-0-baseline"])
        finally:
            tmp.cleanup()

    def test_psalm_equivalence_not_ci_gated(self):
        # Deliberately out of scope for this ticket (see php-tooling-tree.md)
        # — Psalm gets its own node, and its own CI check, in a follow-up.
        tmp, root = self._make_repo({
            "composer.json": json.dumps({"require": {"vimeo/psalm": "^5.0"}}),
            "composer.lock": "{}",
            "psalm.xml": "<psalm></psalm>",
            ".github/workflows/ci.yml": self._CI_YML_NO_TOOLS,
        })
        try:
            d = detect_nodes(root)
            self.assertTrue(d["phpstan-level-0-baseline"]["fulfilled"], d["phpstan-level-0-baseline"])
        finally:
            tmp.cleanup()


class RejectionRespectedTests(unittest.TestCase):
    """A node with an out-of-scope entry stays out of next_candidates()/
    roadmap() even once its required parents are fulfilled -- until the
    entry is removed (the composer-audit/phpunit reversal gap: rejected
    ordinary nodes were never checked, only structural-scan's own gate)."""

    def _make_repo(self, files: dict):
        tmp = tempfile.TemporaryDirectory()
        root = pathlib.Path(tmp.name)
        for rel, content in files.items():
            p = root / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content)
        (root / ".git").mkdir()
        return tmp, root

    def test_rejected_ordinary_node_not_in_next_candidates(self):
        tmp, root = self._make_repo({
            "composer.json": json.dumps({"require": {"php": ">=7.2"}}),
            "composer.lock": "{}",
            "docs/refactoring/out-of-scope/php-cs-fixer.md": "rejected\n",
        })
        try:
            nodes = [c["node"] for c in next_candidates(root, limit=10)]
            self.assertNotIn("php-cs-fixer", nodes)
        finally:
            tmp.cleanup()

    def test_rejected_ordinary_node_not_in_roadmap(self):
        tmp, root = self._make_repo({
            "composer.json": json.dumps({"require": {"php": ">=7.2"}}),
            "composer.lock": "{}",
            "docs/refactoring/out-of-scope/phpunit.md": "rejected\n",
        })
        try:
            nodes = [x["node"] for x in roadmap(root, steps=10)]
            self.assertNotIn("phpunit", nodes)
        finally:
            tmp.cleanup()

    def test_unrejected_sibling_still_proposed(self):
        tmp, root = self._make_repo({
            "composer.json": json.dumps({"require": {"php": ">=7.2"}}),
            "composer.lock": "{}",
            "docs/refactoring/out-of-scope/php-cs-fixer.md": "rejected\n",
        })
        try:
            nodes = [c["node"] for c in next_candidates(root, limit=10)]
            self.assertIn("phpunit", nodes)
        finally:
            tmp.cleanup()


class RecommendedGateTests(unittest.TestCase):
    """ADR-0016: a `recommended` edge now withholds its child from
    next_candidates() until every recommended parent is decided — fulfilled
    or rejected, released either way. Unlike a `required` edge, which only
    ever releases the child on fulfilment and instead cascades a rejection,
    a decided-rejected recommended parent still releases the child."""

    def _make_repo(self, files: dict):
        tmp = tempfile.TemporaryDirectory()
        root = pathlib.Path(tmp.name)
        for rel, content in files.items():
            p = root / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content)
        (root / ".git").mkdir()
        return tmp, root

    def _p0_fulfilled_files(self):
        # phpstan-level-0-baseline fulfilled (rector-dead-code's/
        # rector-type-coverage's required parent); php-cs-fixer and
        # phpstan-level-3 both stay undecided (neither fulfilled nor
        # rejected). `.editorconfig` present (ticket 01: php-cs-fixer's own
        # recommended parent) so php-cs-fixer itself stays proposable here —
        # its undecided status under test is about rector-dead-code's gate,
        # not php-cs-fixer's own.
        return {
            "composer.json": json.dumps({"require-dev": {"phpstan/phpstan": "^1.0"}}),
            "composer.lock": "{}",
            "phpstan.neon": "parameters:\n    level: 0\n",
            "phpstan-baseline.neon": "parameters:\n    ignoreErrors: []\n",
            ".editorconfig": "root = true\n\n[*]\ncharset = utf-8\n",
        }

    def test_child_withheld_while_recommended_parent_undecided(self):
        tmp, root = self._make_repo(self._p0_fulfilled_files())
        try:
            nodes = [c["node"] for c in next_candidates(root)]
            self.assertIn("php-cs-fixer", nodes)  # the undecided parent itself is still proposable
            self.assertNotIn("rector-dead-code", nodes)
        finally:
            tmp.cleanup()

    def test_child_released_once_recommended_parent_rejected(self):
        tmp, root = self._make_repo(self._p0_fulfilled_files())
        try:
            (root / "docs" / "refactoring" / "out-of-scope").mkdir(parents=True)
            (root / "docs" / "refactoring" / "out-of-scope" / "php-cs-fixer.md").write_text("rejected\n")
            nodes = [c["node"] for c in next_candidates(root)]
            self.assertIn("rector-dead-code", nodes)
        finally:
            tmp.cleanup()

    def test_child_released_once_recommended_parent_fulfilled(self):
        files = self._p0_fulfilled_files()
        files["composer.json"] = json.dumps({"require-dev": {
            "phpstan/phpstan": "^1.0",
            "friendsofphp/php-cs-fixer": "^3.0",
        }})
        files[".php-cs-fixer.php"] = "<?php return [];"
        tmp, root = self._make_repo(files)
        try:
            nodes = [c["node"] for c in next_candidates(root)]
            self.assertIn("rector-dead-code", nodes)
        finally:
            tmp.cleanup()

    def test_gate_waits_on_every_recommended_parent_not_just_one(self):
        # php-cs-fixer decided (fulfilled) but phpstan-level-3 not even
        # reached yet (level still 0) -> rector-type-coverage stays
        # withheld: it has two recommended parents, both must be decided.
        files = self._p0_fulfilled_files()
        files["composer.json"] = json.dumps({"require-dev": {
            "phpstan/phpstan": "^1.0",
            "friendsofphp/php-cs-fixer": "^3.0",
        }})
        files[".php-cs-fixer.php"] = "<?php return [];"
        tmp, root = self._make_repo(files)
        try:
            nodes = [c["node"] for c in next_candidates(root)]
            self.assertNotIn("rector-type-coverage", nodes)
        finally:
            tmp.cleanup()

    def test_cascade_rejection_of_required_ancestor_decides_recommended_parent(self):
        # phpstan-level-1 rejected -> phpstan-level-2/-3 permanently closed
        # via the required chain -> counts as phpstan-level-3 "decided" for
        # rector-type-coverage's recommended edge (php-cs-fixer is decided
        # here too, via fulfilment, so it isn't the thing under test).
        files = self._p0_fulfilled_files()
        files["composer.json"] = json.dumps({"require-dev": {
            "phpstan/phpstan": "^1.0",
            "friendsofphp/php-cs-fixer": "^3.0",
        }})
        files[".php-cs-fixer.php"] = "<?php return [];"
        tmp, root = self._make_repo(files)
        try:
            (root / "docs" / "refactoring" / "out-of-scope").mkdir(parents=True)
            (root / "docs" / "refactoring" / "out-of-scope" / "phpstan-level-1.md").write_text("rejected\n")
            nodes = [c["node"] for c in next_candidates(root)]
            self.assertIn("rector-type-coverage", nodes)
        finally:
            tmp.cleanup()

    def test_withheld_candidates_names_the_waiting_on_parents(self):
        tmp, root = self._make_repo(self._p0_fulfilled_files())
        try:
            withheld = {w["node"]: set(w["waiting_on"]) for w in withheld_candidates(root)}
            self.assertEqual(withheld["rector-dead-code"], {"php-cs-fixer"})
            self.assertEqual(withheld["rector-type-coverage"], {"php-cs-fixer", "phpstan-level-3"})
        finally:
            tmp.cleanup()

    def test_next_candidates_uncapped_by_default(self):
        # Six nodes genuinely unblocked at once — past the old five-node cap
        # ADR-0016 lifts (real even without this ticket's recommended-gate
        # change: loop-config, php-cs-fixer, phpunit, test-runner-if-missing,
        # composer-audit, phpstan-level-1).
        files = self._p0_fulfilled_files()
        files["composer.json"] = json.dumps({
            "require": {"vendor/pkg": "^1.0"},
            "require-dev": {"phpstan/phpstan": "^1.0"},
        })
        files[".github/workflows/ci.yml"] = "jobs:\n  build:\n    steps:\n      - run: echo hi\n"
        tmp, root = self._make_repo(files)
        try:
            nodes = [c["node"] for c in next_candidates(root)]
            self.assertGreater(len(nodes), 5)
            # limit is still honored when a caller explicitly wants one
            self.assertLessEqual(len(next_candidates(root, limit=3)), 3)
        finally:
            tmp.cleanup()


class EditorconfigNodeTests(unittest.TestCase):
    """Ticket 01: `.editorconfig` as its own generic-tree node. Two edges
    exercised here: `loop-config -> editorconfig` (required — its own
    prerequisite) and `editorconfig -> php-cs-fixer` (recommended — settle
    basic formatting before php-cs-fixer's style rules, ADR-0016's
    decided-gate)."""

    def _make_repo(self, files: dict):
        tmp = tempfile.TemporaryDirectory()
        root = pathlib.Path(tmp.name)
        for rel, content in files.items():
            p = root / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content)
        (root / ".git").mkdir()
        return tmp, root

    def _loop_config_and_composer_files(self):
        return {
            "docs/refactoring/config.md": "# Refactoring Loop Config\n\n**Cadence:** weekly\n",
            "composer.json": json.dumps({"name": "test/app", "require": {"php": "^8.1"}}),
            "composer.lock": "{}",
        }

    def test_absent_not_fulfilled(self):
        tmp, root = self._make_repo(self._loop_config_and_composer_files())
        try:
            d = detect_nodes(root)
            self.assertFalse(d["editorconfig"]["fulfilled"])
        finally:
            tmp.cleanup()

    def test_present_fulfilled(self):
        files = self._loop_config_and_composer_files()
        files[".editorconfig"] = "root = true\n\n[*]\ncharset = utf-8\n"
        tmp, root = self._make_repo(files)
        try:
            d = detect_nodes(root)
            self.assertTrue(d["editorconfig"]["fulfilled"])
        finally:
            tmp.cleanup()

    def test_blocked_until_loop_config_fulfilled(self):
        tmp, root = self._make_repo({})  # no docs/refactoring/config.md
        try:
            nodes = [c["node"] for c in next_candidates(root)]
            self.assertNotIn("editorconfig", nodes)
            self.assertIn("loop-config", nodes)
        finally:
            tmp.cleanup()

    def test_proposable_once_loop_config_fulfilled(self):
        tmp, root = self._make_repo({"docs/refactoring/config.md": "# Refactoring Loop Config\n"})
        try:
            nodes = [c["node"] for c in next_candidates(root)]
            self.assertIn("editorconfig", nodes)
        finally:
            tmp.cleanup()

    def test_php_cs_fixer_withheld_while_editorconfig_undecided(self):
        tmp, root = self._make_repo(self._loop_config_and_composer_files())
        try:
            nodes = [c["node"] for c in next_candidates(root)]
            self.assertIn("editorconfig", nodes)  # the undecided parent itself is still proposable
            self.assertNotIn("php-cs-fixer", nodes)
        finally:
            tmp.cleanup()

    def test_php_cs_fixer_released_once_editorconfig_fulfilled(self):
        files = self._loop_config_and_composer_files()
        files[".editorconfig"] = "root = true\n\n[*]\ncharset = utf-8\n"
        tmp, root = self._make_repo(files)
        try:
            nodes = [c["node"] for c in next_candidates(root)]
            self.assertIn("php-cs-fixer", nodes)
        finally:
            tmp.cleanup()

    def test_php_cs_fixer_released_once_editorconfig_rejected(self):
        tmp, root = self._make_repo(self._loop_config_and_composer_files())
        try:
            (root / "docs" / "refactoring" / "out-of-scope").mkdir(parents=True)
            (root / "docs" / "refactoring" / "out-of-scope" / "editorconfig.md").write_text("rejected\n")
            nodes = [c["node"] for c in next_candidates(root)]
            self.assertIn("php-cs-fixer", nodes)
        finally:
            tmp.cleanup()

    def test_withheld_candidates_names_editorconfig(self):
        tmp, root = self._make_repo(self._loop_config_and_composer_files())
        try:
            withheld = {w["node"]: set(w["waiting_on"]) for w in withheld_candidates(root)}
            self.assertEqual(withheld["php-cs-fixer"], {"editorconfig"})
        finally:
            tmp.cleanup()


class PhpVersionReversalTests(unittest.TestCase):
    """php-tooling-tree.md's mechanical reversal: a rejected node's
    `Blocked by: PHP >= X.Y` condition satisfied by the target's current
    floor surfaces as a finding (refactor-scan detects, refactor-learn
    removes the out-of-scope entry -- never the other way round)."""

    def _make_repo(self, files: dict):
        tmp = tempfile.TemporaryDirectory()
        root = pathlib.Path(tmp.name)
        for rel, content in files.items():
            p = root / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content)
        (root / ".git").mkdir()
        return tmp, root

    def test_reversal_found_when_php_floor_satisfies_blocked_by(self):
        tmp, root = self._make_repo({
            "composer.json": json.dumps({"require": {"php": ">=7.2"}}),
            "composer.lock": "{}",
            "docs/refactoring/out-of-scope/phpunit.md": "**Blocked by:** PHP >= 7.0\n",
        })
        try:
            nodes = [f["node"] for f in php_version_reversal_findings(root)]
            self.assertIn("phpunit", nodes)
        finally:
            tmp.cleanup()

    def test_no_reversal_when_php_floor_still_below_blocked_by(self):
        tmp, root = self._make_repo({
            "composer.json": json.dumps({"require": {"php": ">=5.6"}}),
            "composer.lock": "{}",
            "docs/refactoring/out-of-scope/phpunit.md": "**Blocked by:** PHP >= 7.0\n",
        })
        try:
            self.assertEqual(php_version_reversal_findings(root), [])
        finally:
            tmp.cleanup()

    def test_no_reversal_without_blocked_by_field(self):
        tmp, root = self._make_repo({
            "composer.json": json.dumps({"require": {"php": ">=8.1"}}),
            "composer.lock": "{}",
            "docs/refactoring/out-of-scope/some-stylistic-rejection.md": "Not worth it here.\n",
        })
        try:
            self.assertEqual(php_version_reversal_findings(root), [])
        finally:
            tmp.cleanup()

    def test_uses_platform_pin_over_require_when_present(self):
        tmp, root = self._make_repo({
            "composer.json": json.dumps({
                "require": {"php": ">=7.2"},
                "config": {"platform": {"php": "7.2.34"}},
            }),
            "composer.lock": "{}",
            "docs/refactoring/out-of-scope/phpunit.md": "**Blocked by:** PHP >= 7.0\n",
        })
        try:
            nodes = [f["node"] for f in php_version_reversal_findings(root)]
            self.assertEqual(nodes, ["phpunit"])
        finally:
            tmp.cleanup()


class PhpFloorPrecheckTests(unittest.TestCase):
    """Ticket 31: the target's current PHP floor is checked once against each
    of the five deterministic PHP tooling leaves' known minimum-ever PHP
    version, instead of proposing/rejecting each one individually. Design
    decision (see `php_floor_precheck`'s docstring): skip silently, no
    `docs/refactoring/out-of-scope/` entry written."""

    def _make_repo(self, files: dict):
        tmp = tempfile.TemporaryDirectory()
        root = pathlib.Path(tmp.name)
        for rel, content in files.items():
            p = root / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content)
        (root / ".git").mkdir()
        return tmp, root

    def test_no_composer_json_blocks_nothing(self):
        tmp, root = self._make_repo({})
        try:
            self.assertEqual(php_floor_precheck(root), [])
        finally:
            tmp.cleanup()

    def test_modern_floor_blocks_nothing(self):
        tmp, root = self._make_repo({
            "composer.json": json.dumps({"require": {"php": "^8.1"}}),
            "composer.lock": "{}",
        })
        try:
            self.assertEqual(php_floor_precheck(root), [])
        finally:
            tmp.cleanup()

    def test_php_56_floor_blocks_only_the_two_leaves_that_never_ran_that_low(self):
        # composer-audit (needs Composer >=2.4, itself PHP >=7.2.5) and
        # phpstan-level-0-baseline (phpstan/phpstan has required PHP >=7.1
        # since its first release) never had a version installable on PHP
        # 5.6. php-cs-fixer, phpunit, and test-runner-if-missing all have
        # PHP-5.6-compatible lines (their absolute floor is PHP 5.3), so PHP
        # 5.6 alone doesn't block them.
        tmp, root = self._make_repo({
            "composer.json": json.dumps({"require": {"php": ">=5.6"}}),
            "composer.lock": "{}",
        })
        try:
            blocked = {b["node"] for b in php_floor_precheck(root)}
            self.assertEqual(blocked, {"composer-audit", "phpstan-level-0-baseline"})
        finally:
            tmp.cleanup()

    def test_php_70_unblocks_phpstan_but_not_composer_audit(self):
        # phpstan/phpstan's first published release (0.1) required PHP ~7.0
        # -- its true floor, below PHPStan's own documented "PHP 7.1+"
        # marketing baseline for later versions. composer-audit still needs
        # PHP >=7.2.5 (Composer 2.4's own floor), so it stays blocked here.
        tmp, root = self._make_repo({
            "composer.json": json.dumps({"require": {"php": ">=7.0"}}),
            "composer.lock": "{}",
        })
        try:
            blocked = {b["node"] for b in php_floor_precheck(root)}
            self.assertEqual(blocked, {"composer-audit"})
        finally:
            tmp.cleanup()

    def test_very_old_floor_blocks_all_five_leaves(self):
        tmp, root = self._make_repo({
            "composer.json": json.dumps({"require": {"php": ">=5.2"}}),
            "composer.lock": "{}",
        })
        try:
            blocked = {b["node"] for b in php_floor_precheck(root)}
            self.assertEqual(
                blocked,
                {
                    "php-cs-fixer",
                    "phpunit",
                    "test-runner-if-missing",
                    "composer-audit",
                    "phpstan-level-0-baseline",
                },
            )
        finally:
            tmp.cleanup()

    def test_uses_platform_pin_over_require_when_present(self):
        tmp, root = self._make_repo({
            "composer.json": json.dumps({
                "require": {"php": ">=8.1"},
                "config": {"platform": {"php": "5.6.40"}},
            }),
            "composer.lock": "{}",
        })
        try:
            blocked = {b["node"] for b in php_floor_precheck(root)}
            self.assertIn("composer-audit", blocked)
        finally:
            tmp.cleanup()

    def test_next_candidates_excludes_blocked_leaves(self):
        tmp, root = self._make_repo({
            "composer.json": json.dumps({"require": {"php": ">=5.6"}}),
            "composer.lock": "{}",
            "docs/refactoring/config.md": "# Refactoring Loop Config\n",
            ".github/workflows/ci.yml": "jobs:\n  lint:\n    steps:\n      - run: php -l\n",
            # ticket 01: decided (fulfilled), so php-cs-fixer's own recommended
            # gate doesn't interfere with what this test actually exercises.
            ".editorconfig": "root = true\n\n[*]\ncharset = utf-8\n",
        })
        try:
            nodes = [c["node"] for c in next_candidates(root)]
            self.assertNotIn("composer-audit", nodes)
            self.assertNotIn("phpstan-level-0-baseline", nodes)
            # php-cs-fixer and test-runner-if-missing are PHP-5.6-compatible
            # and unblocked (required parents fulfilled) — still proposed.
            self.assertIn("php-cs-fixer", nodes)
            self.assertIn("test-runner-if-missing", nodes)
        finally:
            tmp.cleanup()

    def test_roadmap_never_proposes_blocked_leaves(self):
        tmp, root = self._make_repo({
            "composer.json": json.dumps({"require": {"php": ">=5.6"}}),
            "composer.lock": "{}",
            "docs/refactoring/config.md": "# Refactoring Loop Config\n",
            ".github/workflows/ci.yml": "jobs:\n  lint:\n    steps:\n      - run: php -l\n",
        })
        try:
            r = roadmap(root, steps=10)
            nodes = [x["node"] for x in r]
            self.assertNotIn("composer-audit", nodes)
            self.assertNotIn("phpstan-level-0-baseline", nodes)
        finally:
            tmp.cleanup()

    def test_detect_and_roadmap_reports_php_floor_blocked(self):
        tmp, root = self._make_repo({
            "composer.json": json.dumps({"require": {"php": ">=5.6"}}),
            "composer.lock": "{}",
        })
        try:
            data = tooling_tree.detect_and_roadmap(root)
            blocked = {b["node"] for b in data["php_floor_blocked"]}
            self.assertEqual(blocked, {"composer-audit", "phpstan-level-0-baseline"})
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

    def test_empty_roadmap_starts_with_loop_config(self):
        # ADR-0008: with no docs/refactoring/config.md, loop-config is the
        # first proposable node — required parent of composer/ci-runner
        # (and, since ticket 01, editorconfig).
        tmp, root = self._make_repo({})
        try:
            r = roadmap(root, steps=5)
            self.assertEqual(r[0]["node"], "loop-config")
            # ticket 01: editorconfig lives in tooling-tree.md, parsed before
            # php-tooling-tree.md, so it sorts ahead of composer/ci-runner in
            # tree["order"] — a trivial generic-root node, same footing as
            # loop-config itself.
            self.assertEqual(r[1]["node"], "editorconfig")
            self.assertEqual(r[2]["node"], "composer")
            self.assertIn(r[3]["node"], ["ci-runner", "composer-audit", "php-cs-fixer", "phpunit"])
        finally:
            tmp.cleanup()

    def test_roadmap_with_loop_config_starts_with_composer(self):
        # With docs/refactoring/config.md already present, loop-config is
        # fulfilled and the roadmap picks up where it used to before ADR-0008
        # — plus editorconfig (ticket 01), ordered ahead of composer for the
        # same reason as above.
        tmp, root = self._make_repo({"docs/refactoring/config.md": "# Refactoring Loop Config\n\n**Cadence:** weekly\n"})
        try:
            r = roadmap(root, steps=4)
            self.assertEqual(r[0]["node"], "editorconfig")
            self.assertEqual(r[1]["node"], "composer")
            self.assertIn(r[2]["node"], ["ci-runner", "composer-audit", "php-cs-fixer", "phpunit"])
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
            self.assertIn("phpstan-level-0-baseline", nodes)
            # composer-audit stays blocked here: no ci-runner (required parent)
            # and no real `require` dependency (only the `php` platform
            # pseudo-package) — see ComposerAuditGateTests for its own gating.
            self.assertNotIn("composer-audit", nodes)
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


class PortabilityTests(unittest.TestCase):
    """Guards the property the skills/refactor-scan/references/ move exists for:
    the module finds its own tree docs as siblings, never via the suite
    checkout's layout — so a shipped copy (skills/refactor-scan/ alone, no
    scripts/ or docs/ around it) still works, under symlink or copy install.
    """

    def test_load_tree_ignores_cwd(self):
        old_cwd = pathlib.Path.cwd()
        with tempfile.TemporaryDirectory() as unrelated:
            os.chdir(unrelated)
            try:
                tree = load_tree()
            finally:
                os.chdir(old_cwd)
        self.assertGreaterEqual(len(tree["edges"]), 15)
        self.assertIn({"from": "git", "to": "loop-config", "type": "required"}, tree["edges"])

    def test_tree_docs_are_siblings_of_the_module(self):
        module_dir = pathlib.Path(tooling_tree.__file__).resolve().parent
        self.assertTrue((module_dir / "tooling-tree.md").exists())
        self.assertTrue((module_dir / "php-tooling-tree.md").exists())


if __name__ == "__main__":
    unittest.main()
