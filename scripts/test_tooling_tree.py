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
directly_unblocked_children = tooling_tree.directly_unblocked_children
php_version_reversal_findings = tooling_tree.php_version_reversal_findings
php_floor_precheck = tooling_tree.php_floor_precheck
_is_baseline_empty = tooling_tree._is_baseline_empty
_resolve_refactoring_notes_dir = tooling_tree._resolve_refactoring_notes_dir
_rejected_nodes = tooling_tree._rejected_nodes


class LoadTreeTests(unittest.TestCase):
    def test_edges_parsed(self):
        tree = load_tree()
        self.assertGreaterEqual(len(tree["edges"]), 15)
        # generic root (ADR-0008): git -> loop-config, loop-config -> is-php-project
        # (the PHP specialization's recognition gate, ADR-0022) -> the PHP tree roots.
        self.assertIn({"from": "git", "to": "loop-config", "type": "required"}, tree["edges"])
        self.assertIn({"from": "loop-config", "to": "is-php-project", "type": "required"}, tree["edges"])
        self.assertIn({"from": "is-php-project", "to": "composer", "type": "required"}, tree["edges"])
        # check required edge
        self.assertIn({"from": "phpstan-level-0", "to": "phpstan-level-1", "type": "required"}, tree["edges"])
        # recommended
        self.assertIn({"from": "php-cs-fixer", "to": "rector-dead-code", "type": "recommended"}, tree["edges"])
        # resolved (ADR-0008, ticket 42): PHP-tree leaves gate their own
        # aggregation node, php-structural-scan, which itself gates
        # structural-scan via one resolved edge.
        self.assertIn({"from": "composer-audit", "to": "php-structural-scan", "type": "resolved"}, tree["edges"])
        self.assertIn({"from": "php-structural-scan", "to": "structural-scan", "type": "resolved"}, tree["edges"])
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
        # signals ticket 2: php-cs-fixer's route to php-structural-scan
        # simplified — new recommended edge into rector-php-set replaces its
        # own direct resolved edge (still transitively decided before
        # rector-dead-code/rector-code-quality, both still direct leaves,
        # can resolve).
        self.assertIn({"from": "php-cs-fixer", "to": "rector-php-set", "type": "recommended"}, tree["edges"])
        self.assertNotIn({"from": "php-cs-fixer", "to": "php-structural-scan", "type": "resolved"}, tree["edges"])
        # signals ticket 2: test-runner-if-missing dropped from the leaf set,
        # no replacement.
        self.assertNotIn({"from": "test-runner-if-missing", "to": "php-structural-scan", "type": "resolved"}, tree["edges"])
        # signals ticket 2: the level-chain leaf moves from level 10 to level
        # 5 — the chain's only existing structural fork point.
        self.assertIn({"from": "phpstan-level-5", "to": "php-structural-scan", "type": "resolved"}, tree["edges"])
        self.assertNotIn({"from": "phpstan-level-10", "to": "php-structural-scan", "type": "resolved"}, tree["edges"])
        # signals ticket 2: phpmd and secret-detection are Signal-producing
        # nodes, proposed and ranked normally but never gating structural
        # work — no resolved edge into either gate.
        self.assertIn({"from": "composer", "to": "phpmd", "type": "required"}, tree["edges"])
        self.assertNotIn({"from": "phpmd", "to": "php-structural-scan", "type": "resolved"}, tree["edges"])
        self.assertIn({"from": "loop-config", "to": "secret-detection", "type": "required"}, tree["edges"])
        self.assertNotIn({"from": "secret-detection", "to": "structural-scan", "type": "resolved"}, tree["edges"])

    def test_order_contains_nodes(self):
        tree = load_tree()
        for n in ["git", "loop-config", "composer", "phpstan-level-0", "phpstan-level-1", "rector-dead-code", "structural-scan"]:
            self.assertIn(n, tree["order"])

    def test_resolved_parents_of_structural_scan(self):
        # ticket 42: structural-scan's direct resolved parents are now just
        # editorconfig (generic-root leaf) and php-structural-scan (the PHP
        # tree's own aggregation node) — not the seven PHP leaves directly.
        # ADR-0022 (follow-up): ci-runner joined as a third generic-root
        # resolved-parent — deterministic tooling settling first includes
        # having somewhere for quality jobs to run at all.
        tree = load_tree()
        self.assertEqual(
            set(tree["resolved_parents"]["structural-scan"]),
            {"editorconfig", "ci-runner", "php-structural-scan"},
        )

    def test_resolved_parents_of_php_structural_scan(self):
        # ticket 43: phpstan-level-10 replaced phpstan-level-3 as the level
        # chain's leaf, and 5 new leaves joined (phpstan-deprecation-rules,
        # rector-php-set, rector-code-quality, rector-phpunit-set,
        # rector-early-return) — twelve total, up from seven. Ticket 44's
        # follow-up adds `psalm-taint-analysis` as a thirteenth leaf — a
        # deterministic security-scan tool exactly like `composer-audit`
        # (also one of these thirteen), so it gates the same way. `psalm`
        # itself is deliberately NOT one of these — ticket 37 originally gave
        # it its own leaf, found redundant on review and dropped: the actual
        # bug (a Psalm-only target never resolving the level chain's leaf) is
        # already fixed by that node's own mutual-exclusion rejection
        # housekeeping, without needing `psalm` to be a leaf too. Ticket 48
        # later dropped `rector-early-return` itself (its rule set shipped
        # permanently empty upstream, folded into `rector-code-quality`) —
        # back down to twelve. Ticket 50 added `psr-4` as a new thirteenth
        # leaf — gating on a different basis than every other leaf here (a
        # code-organization convention, not a checking tool). `signals`
        # ticket 2 dropped `test-runner-if-missing` (no replacement) and
        # `php-cs-fixer` (rerouted through a new recommended edge into
        # `rector-php-set` instead — still transitively decided before this
        # node resolves, just not a direct edge any more) and lowered the
        # level-chain leaf from `phpstan-level-10` to `phpstan-level-5` — down
        # to eleven.
        tree = load_tree()
        self.assertEqual(
            set(tree["resolved_parents"]["php-structural-scan"]),
            {
                "psr-4",
                "composer-audit",
                "phpunit",
                "phpstan-level-5",
                "phpstan-deprecation-rules",
                "rector-dead-code",
                "rector-type-coverage",
                "rector-php-set",
                "rector-code-quality",
                "rector-phpunit-set",
                "psalm-taint-analysis",
            },
        )
        self.assertNotIn("psalm", tree["resolved_parents"]["php-structural-scan"])
        self.assertNotIn("rector-early-return", tree["resolved_parents"]["php-structural-scan"])
        self.assertNotIn("test-runner-if-missing", tree["resolved_parents"]["php-structural-scan"])
        self.assertNotIn("php-cs-fixer", tree["resolved_parents"]["php-structural-scan"])
        self.assertNotIn("phpstan-level-10", tree["resolved_parents"]["php-structural-scan"])

    def test_required_any_parents_of_psalm_taint_analysis(self):
        # ticket 37: a new OR-required-parent edge type — psalm-taint-analysis
        # is unblocked once *either* phpstan-level-4 or psalm is fulfilled,
        # not both.
        tree = load_tree()
        self.assertEqual(
            set(tree["required_any_parents"]["psalm-taint-analysis"]),
            {"phpstan-level-4", "psalm"},
        )

    def test_required_any_parents_of_rector_php_set(self):
        # ticket 37/44 follow-up: rector-php-set reads the static-analyzer
        # gate directly via required-any(phpstan-level-0, psalm)
        # instead of relying on it being implicit inside
        # phpstan-level-0's own Psalm-equivalence fulfilment check.
        # rector-dead-code/rector-code-quality no longer
        # carry their own direct required edge on phpstan-level-0 —
        # they read this transitively via their existing required parent on
        # rector-php-set. rector-type-coverage/rector-phpunit-set are no
        # longer tied to this gate at all (later restructuring moved them
        # onto sibling Rector nodes instead, via recommended edges — see
        # test_rector_type_coverage_and_phpunit_set_gate_via_siblings_now).
        # Ticket 48 dropped the sixth Rector node, rector-early-return
        # (folded into rector-code-quality) — two direct children remain.
        tree = load_tree()
        self.assertEqual(
            set(tree["required_any_parents"]["rector-php-set"]),
            {"phpstan-level-0", "psalm"},
        )
        self.assertEqual(tree["required_parents"]["rector-dead-code"], ["rector-php-set"])
        self.assertEqual(tree["required_parents"]["rector-code-quality"], ["rector-php-set"])
        self.assertNotIn("rector-early-return", tree["required_parents"])
        self.assertEqual(tree["required_parents"]["rector-type-coverage"], [])
        self.assertEqual(tree["required_parents"]["rector-phpunit-set"], ["phpunit"])
        # Exactly these two nodes use required-any today.
        self.assertEqual(
            {n for n, parents in tree["required_any_parents"].items() if parents},
            {"psalm-taint-analysis", "rector-php-set"},
        )

    def test_rector_type_coverage_and_phpunit_set_gate_via_siblings_now(self):
        # Follow-up restructuring: rector-type-coverage/rector-phpunit-set
        # lost their direct required: rector-php-set edge, gated instead via
        # recommended edges from sibling Rector nodes (dead-code/
        # code-quality for type-coverage; code-quality for phpunit-set).
        # Ticket 48: rector-type-coverage's second recommended parent used to
        # be rector-early-return (control-flow flattening); once that node
        # was dropped, rector-code-quality — which absorbed its rules — took
        # over the gate slot instead of the slot disappearing.
        tree = load_tree()
        self.assertEqual(
            set(tree["recommended_parents"]["rector-type-coverage"]),
            {"rector-dead-code", "rector-code-quality", "php-cs-fixer", "phpstan-level-3"},
        )
        self.assertEqual(
            set(tree["recommended_parents"]["rector-phpunit-set"]),
            {"rector-code-quality", "php-cs-fixer"},
        )

    def test_php_structural_scan_aggregated_away_not_exposed(self):
        # ticket 42: php-structural-scan feeds structural-scan's own
        # resolved gate, so it must never be exposed as a proposable
        # candidate itself — only structural-scan is.
        tree = load_tree()
        self.assertEqual(tree["exposed_resolved_gate_nodes"], {"structural-scan"})

    def test_php_minimal_version_edges(self):
        # ticket 57: php-minimal-version's only required parent is now
        # rector-php-set (reversed direction from ticket 35's original
        # design, where php-minimal-version was rector-php-set's own
        # recommended parent instead) -- is-php-project/ci-runner dropped as
        # direct required parents, both still reachable transitively.
        tree = load_tree()
        self.assertEqual(
            set(tree["required_parents"]["php-minimal-version"]),
            {"rector-php-set"},
        )
        self.assertNotIn("php-minimal-version", tree["recommended_parents"].get("rector-php-set", []))
        self.assertNotIn("rector-php-set", tree["recommended_parents"].get("php-minimal-version", []))
        # Deliberately NOT one of php-structural-scan's resolved-parent
        # leaves — never decided as one, ticket 35's original grilling
        # session included, still not one after ticket 57.
        self.assertNotIn("php-minimal-version", tree["resolved_parents"]["php-structural-scan"])


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
            self.assertFalse(d["phpstan-level-0"]["fulfilled"])
            self.assertFalse(d["structural-scan"]["fulfilled"])
        finally:
            tmp.cleanup()

    def test_loop_config_fulfilled_when_config_md_present(self):
        tmp, root = self._make_repo({
            "docs/refactoring/bookkeeping.md": "# Refactoring Loop Config\n\n**Cadence:** weekly\n",
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
            self.assertTrue(d["phpstan-level-0"]["fulfilled"])
            self.assertIn("psalm", d["phpstan-level-0"]["reason"].lower())
            # p1 not applicable
            self.assertFalse(d["phpstan-level-1"]["fulfilled"])
        finally:
            tmp.cleanup()

    def test_p0_psalm_equivalence_still_unblocks_rector_family(self):
        # Ticket 37 regression guard: mutual exclusion must NOT touch
        # phpstan-level-0's own fulfilled state. If the
        # Psalm-equivalence branch were ever replaced by rejecting
        # phpstan-level-0 itself (ticket 37's literal wording,
        # deliberately not implemented that way — see php-tooling-tree.md's
        # `phpstan` equivalents section), the Rector family would become
        # permanently unreachable for every Psalm-only target on that path
        # alone (a required-parent rejection closes every node beneath it).
        # Ticket 37/44's follow-up made this doubly robust: rector-php-set's
        # gate is now required-any(phpstan-level-0, psalm) — psalm
        # unblocks it directly, independent of phpstan-level-0's own
        # fulfilled state entirely. rector-dead-code/rector-type-coverage are
        # not checked directly here — they only require rector-php-set
        # fulfilled (an ordinary, unrelated adoption fact), so this one check
        # on rector-php-set's own unblocked-ness is the meaningful regression
        # guard for the whole family.
        tmp, root = self._make_repo({
            "composer.json": json.dumps({"require": {"vimeo/psalm": "^5.0"}}),
            "composer.lock": "{}",
            "psalm.xml": "<psalm></psalm>",
        })
        try:
            d = detect_nodes(root)
            self.assertTrue(d["phpstan-level-0"]["fulfilled"])
            self.assertTrue(d["psalm"]["fulfilled"])
            ok, why = tooling_tree._is_unblocked("rector-php-set", load_tree(), d)
            self.assertTrue(ok, why)
        finally:
            tmp.cleanup()

    def test_rector_php_set_reachable_via_psalm_alone_even_if_p0_were_false(self):
        # Direct proof of the "doubly robust" claim above: rector-php-set's
        # required-any(phpstan-level-0, psalm) unblocks it via psalm
        # alone, with no dependency on phpstan-level-0's own
        # fulfilled state — unlike before ticket 37/44's follow-up, where the
        # only path was through phpstan-level-0's fulfilled flag
        # (itself driven by the equivalence).
        fulfilled = {"phpstan-level-0": {"fulfilled": False}, "psalm": {"fulfilled": True}}
        ok, why = tooling_tree._is_unblocked("rector-php-set", load_tree(), fulfilled)
        self.assertTrue(ok, why)

    def test_p0_phpstan_level0_empty(self):
        tmp, root = self._make_repo({
            "composer.json": json.dumps({"require-dev": {"phpstan/phpstan": "^1.0"}}),
            "composer.lock": "{}",
            "phpstan.neon": "parameters:\n    level: 0\n    paths: [src]\nincludes:\n    - phpstan-baseline.neon\n",
            "phpstan-baseline.neon": "parameters:\n    ignoreErrors: []\n",
        })
        try:
            d = detect_nodes(root)
            self.assertTrue(d["phpstan-level-0"]["fulfilled"])
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
            self.assertTrue(d["phpstan-level-0"]["fulfilled"])
            self.assertFalse(d["phpstan-level-1"]["fulfilled"])
            # roadmap should not propose p1 when baseline non-empty
            r = roadmap(root, steps=5)
            nodes = [x["node"] for x in r]
            self.assertNotIn("phpstan-level-1", nodes[:2])  # at least not immediate
        finally:
            tmp.cleanup()


class RefactoringNotesResolutionTests(unittest.TestCase):
    """`_resolve_refactoring_notes_dir` — the Refactoring Notes' path,
    default docs/refactoring/, overridable via a `Refactoring Notes:
    `<path>`` line in AGENTS.md/CLAUDE.md (skills/continuous-refactoring/
    references/refactoring-bookkeeping.md's resolution rule)."""

    def _make_repo(self, files: dict):
        tmp = tempfile.TemporaryDirectory()
        root = pathlib.Path(tmp.name)
        for rel, content in files.items():
            p = root / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content)
        (root / ".git").mkdir()
        return tmp, root

    def test_default_with_neither_file_present(self):
        tmp, root = self._make_repo({})
        try:
            self.assertEqual(_resolve_refactoring_notes_dir(root), root / "docs" / "refactoring")
        finally:
            tmp.cleanup()

    def test_default_when_agents_md_present_without_the_line(self):
        tmp, root = self._make_repo({"AGENTS.md": "# Agents\n\nSome other instructions.\n"})
        try:
            self.assertEqual(_resolve_refactoring_notes_dir(root), root / "docs" / "refactoring")
        finally:
            tmp.cleanup()

    def test_custom_path_from_agents_md(self):
        tmp, root = self._make_repo({
            "AGENTS.md": "## Continuous-refactoring suite\n\nRefactoring Notes: `custom/path/` — notes.\n",
            "custom/path/bookkeeping.md": "# Refactoring Loop Config\n",
        })
        try:
            self.assertEqual(_resolve_refactoring_notes_dir(root), root / "custom" / "path")
            d = detect_nodes(root)
            self.assertTrue(d["loop-config"]["fulfilled"])
        finally:
            tmp.cleanup()

    def test_custom_path_from_claude_md_when_no_agents_md(self):
        tmp, root = self._make_repo({
            "CLAUDE.md": "Refactoring Notes: `notes/refactor/`\n",
            "notes/refactor/bookkeeping.md": "# Refactoring Loop Config\n",
        })
        try:
            self.assertEqual(_resolve_refactoring_notes_dir(root), root / "notes" / "refactor")
            d = detect_nodes(root)
            self.assertTrue(d["loop-config"]["fulfilled"])
        finally:
            tmp.cleanup()

    def test_agents_md_without_line_falls_through_to_claude_md(self):
        tmp, root = self._make_repo({
            "AGENTS.md": "# Agents\n\nNo suite section here.\n",
            "CLAUDE.md": "Refactoring Notes: `alt/notes/`\n",
        })
        try:
            self.assertEqual(_resolve_refactoring_notes_dir(root), root / "alt" / "notes")
        finally:
            tmp.cleanup()

    def test_out_of_scope_honors_custom_path(self):
        tmp, root = self._make_repo({
            "AGENTS.md": "Refactoring Notes: `custom/path/`\n",
            "custom/path/out-of-scope/psalm.md": "# psalm\n\nRejected.\n",
        })
        try:
            self.assertIn("psalm", _rejected_nodes(root))
            # the default location has nothing, so it must not be found there
            self.assertFalse((root / "docs" / "refactoring" / "out-of-scope" / "psalm.md").exists())
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
                    "phpstan/phpstan-deprecation-rules": "^1.0",
                    "phpunit/phpunit": "^10.0",
                    "friendsofphp/php-cs-fixer": "^3.0",
                },
                # ticket 50: psr-4 is a 13th php-structural-scan leaf — a
                # "fully tooled" fixture needs a real, verified mapping
                # (declaration alone isn't enough, see PsrFourGateTests),
                # not just a rejection.
                "autoload": {"psr-4": {"App\\": "src/"}},
            }),
            "composer.lock": "{}",
            "src/Example.php": "<?php\n\nnamespace App;\n\nclass Example\n{\n}\n",
            ".php-cs-fixer.php": "<?php return [];",
            # signals ticket 2: the level-chain leaf is phpstan-level-5 now
            # (was phpstan-level-10, ticket 43's own level-3 before that) —
            # a "fully tooled" fixture must reach the current leaf to resolve
            # php-structural-scan by fulfilment alone.
            "phpstan.neon": "parameters:\n    level: 5\n",
            "phpstan-baseline.neon": "parameters:\n    ignoreErrors: []\n",
            # ticket 43: also fulfils rector-php-set/-code-quality/-phpunit-set
            # (substring-detected, same style as DeadCode/Type).
            "rector.php": "<?php // DeadCode Type LevelSetList CodeQuality PHPUnitSetList",
            # ticket 41: editorconfig is now an 8th structural-scan leaf —
            # this "fully tooled" fixture needs it decided (fulfilled) too.
            ".editorconfig": "root = true\n\n[*]\ncharset = utf-8\n",
            # ci-runner + composer-audit's own CI-gate fulfilment (no `require`
            # dep here, so composer-audit only resolves via the "every other
            # leaf resolved" fallback — see ComposerAuditGateTests). Also
            # gates phpunit's/phpstan-level-0's own CI-gating check
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
            # ticket 44: `psalm-taint-analysis` is a 13th php-structural-scan
            # leaf. This fixture never adopted vimeo/psalm at all (PHPStan
            # path, no taint scanning either), so a "fully tooled" scenario
            # needs its own rejection written too — otherwise it sits neither
            # fulfilled nor rejected and this helper stops being "fully
            # resolved". `psalm` itself is not a leaf (ticket 37, dropped as
            # redundant) so it needs no rejection here.
            "docs/refactoring/out-of-scope/psalm-taint-analysis.md": "rejected: no taint analysis adopted\n",
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
            (root / "docs" / "refactoring" / "out-of-scope").mkdir(parents=True, exist_ok=True)
            (root / "docs" / "refactoring" / "out-of-scope" / "editorconfig.md").write_text("rejected\n")
            d = detect_nodes(root)
            self.assertTrue(d["structural-scan"]["fulfilled"], d["structural-scan"])
        finally:
            tmp.cleanup()

    def test_unfulfilled_when_leaves_missing(self):
        # ticket 42: structural-scan's own `unresolved` now names its direct
        # resolved-parents (editorconfig, php-structural-scan — plus
        # ci-runner per ADR-0022's follow-up), not the individual PHP
        # leaves — those live one hop down, on php-structural-scan's own
        # `unresolved` (see PhpStructuralScanAggregationTests).
        tmp, root = self._make_repo({})
        try:
            d = detect_nodes(root)
            self.assertFalse(d["structural-scan"]["fulfilled"])
            self.assertEqual(set(d["structural-scan"]["details"]["unresolved"]), {"editorconfig", "ci-runner", "php-structural-scan"})
            self.assertIn("composer-audit", d["php-structural-scan"]["details"]["unresolved"])
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
        # Drop only the "Type"/"type" markers (rector-type-coverage) — keep
        # every other ticket-43 rector marker so only this one leaf is
        # unfulfilled-and-rejected, not incidentally several more.
        files["rector.php"] = "<?php // DeadCode LevelSetList CodeQuality PHPUnitSetList"
        tmp, root = self._make_repo(files)
        try:
            (root / "docs" / "refactoring" / "out-of-scope").mkdir(parents=True, exist_ok=True)
            (root / "docs" / "refactoring" / "out-of-scope" / "rector-type-coverage.md").write_text("rejected: declined\n")
            d = detect_nodes(root)
            self.assertTrue(d["composer-audit"]["fulfilled"], d["composer-audit"])  # genuinely fulfilled, not rejected
            self.assertFalse(d["rector-type-coverage"]["fulfilled"])
            self.assertTrue(d["structural-scan"]["fulfilled"], d["structural-scan"])
        finally:
            tmp.cleanup()


class PhpStructuralScanAggregationTests(unittest.TestCase):
    """Ticket 42: `php-structural-scan` aggregates the PHP tree's seven
    `resolved` leaves behind one node, itself resolving into
    `structural-scan` via a single `resolved` edge. Same `resolved`-edge
    semantics as `structural-scan`'s own gate, one hop down — and, unlike
    `structural-scan`, never itself a proposable candidate."""

    def _make_repo(self, files: dict):
        tmp = tempfile.TemporaryDirectory()
        root = pathlib.Path(tmp.name)
        for rel, content in files.items():
            p = root / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content)
        (root / ".git").mkdir()
        return tmp, root

    def _fully_tooled_php_leaves(self):
        # Every one of php-structural-scan's thirteen leaves (ticket 43: was
        # seven; ticket 50 added psr-4 as the thirteenth) fulfilled —
        # deliberately omits .editorconfig, which is not one of its
        # siblings (it gates structural-scan directly instead).
        return {
            "composer.json": json.dumps({
                "require-dev": {
                    "phpstan/phpstan": "^1.0",
                    "phpstan/phpstan-deprecation-rules": "^1.0",
                    "phpunit/phpunit": "^10.0",
                    "friendsofphp/php-cs-fixer": "^3.0",
                },
                "autoload": {"psr-4": {"App\\": "src/"}},
            }),
            "composer.lock": "{}",
            "src/Example.php": "<?php\n\nnamespace App;\n\nclass Example\n{\n}\n",
            ".php-cs-fixer.php": "<?php return [];",
            # signals ticket 2: the level-chain leaf is phpstan-level-5 now (was phpstan-level-10, ticket 43's own level-3 before that).
            "phpstan.neon": "parameters:\n    level: 5\n",
            "phpstan-baseline.neon": "parameters:\n    ignoreErrors: []\n",
            "rector.php": "<?php // DeadCode Type LevelSetList CodeQuality PHPUnitSetList",
            ".github/workflows/ci.yml": (
                "jobs:\n"
                "  audit:\n"
                "    steps:\n"
                "      - run: composer audit\n"
                "      - run: vendor/bin/phpunit\n"
                "      - run: vendor/bin/phpstan analyse\n"
            ),
            # ticket 44: `psalm-taint-analysis` is one of the thirteen leaves
            # (ticket 50: psr-4 is now fulfilled instead, above) — this
            # fixture never adopted vimeo/psalm at all (PHPStan path, no
            # taint scanning either), so it needs its own rejection written
            # too (same reasoning as StructuralScanGateTests'
            # `_fully_tooled_files` above). `psalm` itself is not a leaf
            # (ticket 37, dropped as redundant) so it needs no rejection.
            "docs/refactoring/out-of-scope/psalm-taint-analysis.md": "rejected: no taint analysis adopted\n",
        }

    def test_unresolved_when_leaves_missing(self):
        tmp, root = self._make_repo({})
        try:
            d = detect_nodes(root)
            self.assertFalse(d["php-structural-scan"]["fulfilled"])
        finally:
            tmp.cleanup()

    def test_resolved_when_every_leaf_fulfilled(self):
        tmp, root = self._make_repo(self._fully_tooled_php_leaves())
        try:
            d = detect_nodes(root)
            self.assertTrue(d["php-structural-scan"]["fulfilled"], d["php-structural-scan"])
        finally:
            tmp.cleanup()

    def test_rejected_leaf_still_resolves_php_structural_scan(self):
        # Mirrors StructuralScanGateTests' equivalent case, one hop down: a
        # rejected leaf still counts as resolved, unlike a required parent.
        files = self._fully_tooled_php_leaves()
        # Drop only the "Type"/"type" markers (rector-type-coverage).
        files["rector.php"] = "<?php // DeadCode LevelSetList CodeQuality PHPUnitSetList"
        tmp, root = self._make_repo(files)
        try:
            (root / "docs" / "refactoring" / "out-of-scope").mkdir(parents=True, exist_ok=True)
            (root / "docs" / "refactoring" / "out-of-scope" / "rector-type-coverage.md").write_text("rejected: declined\n")
            d = detect_nodes(root)
            self.assertFalse(d["rector-type-coverage"]["fulfilled"])
            self.assertTrue(d["php-structural-scan"]["fulfilled"], d["php-structural-scan"])
        finally:
            tmp.cleanup()

    def test_ancestor_rejected_leaf_still_resolves_php_structural_scan(self):
        # Ticket 53 (signals ticket 2 lowered the leaf from phpstan-level-10
        # to phpstan-level-5, same mechanism either way): phpstan-level-5
        # (the actual leaf) isn't itself rejected, but phpstan-level-2 -- a
        # required ancestor two hops up its own chain -- is. Per the
        # maintainer's own decision, only the directly-rejected node gets an
        # out-of-scope entry; the chain above it (3-5) must still count as
        # resolved via _is_effectively_rejected, not stay stuck in
        # `unresolved` forever waiting for an entry nobody is going to write.
        files = self._fully_tooled_php_leaves()
        files["phpstan.neon"] = "parameters:\n    level: 1\n"  # below the rejected level-2
        tmp, root = self._make_repo(files)
        try:
            (root / "docs" / "refactoring" / "out-of-scope").mkdir(parents=True, exist_ok=True)
            (root / "docs" / "refactoring" / "out-of-scope" / "phpstan-level-2.md").write_text("rejected: declined\n")
            d = detect_nodes(root)
            self.assertFalse(d["phpstan-level-5"]["fulfilled"], d["phpstan-level-5"])
            self.assertTrue(d["php-structural-scan"]["fulfilled"], d["php-structural-scan"])
        finally:
            tmp.cleanup()

    def test_structural_scan_resolves_only_once_php_structural_scan_resolves(self):
        # Two-hop regression: structural-scan must read php-structural-scan's
        # already-computed status regardless of tree["order"] position.
        files = self._fully_tooled_php_leaves()
        files[".editorconfig"] = "root = true\n\n[*]\ncharset = utf-8\n"
        tmp, root = self._make_repo(files)
        try:
            d = detect_nodes(root)
            self.assertTrue(d["php-structural-scan"]["fulfilled"], d["php-structural-scan"])
            self.assertTrue(d["structural-scan"]["fulfilled"], d["structural-scan"])
        finally:
            tmp.cleanup()
        # Now drop one leaf: php-structural-scan (and so structural-scan)
        # must close again.
        files2 = dict(files)
        del files2["rector.php"]
        tmp2, root2 = self._make_repo(files2)
        try:
            d2 = detect_nodes(root2)
            self.assertFalse(d2["php-structural-scan"]["fulfilled"])
            self.assertFalse(d2["structural-scan"]["fulfilled"])
        finally:
            tmp2.cleanup()

    def test_never_in_next_candidates(self):
        files = self._fully_tooled_php_leaves()
        tmp, root = self._make_repo(files)
        try:
            # php-structural-scan resolved, but editorconfig undecided —
            # structural-scan itself stays closed either way.
            nodes = [c["node"] for c in next_candidates(root, limit=20)]
            self.assertNotIn("php-structural-scan", nodes)
            self.assertNotIn("structural-scan", nodes)
        finally:
            tmp.cleanup()
        files[".editorconfig"] = "root = true\n\n[*]\ncharset = utf-8\n"
        tmp2, root2 = self._make_repo(files)
        try:
            nodes = [c["node"] for c in next_candidates(root2, limit=20)]
            self.assertNotIn("php-structural-scan", nodes)
            self.assertIn("structural-scan", nodes)
        finally:
            tmp2.cleanup()

    def test_never_in_roadmap(self):
        files = self._fully_tooled_php_leaves()
        files[".editorconfig"] = "root = true\n\n[*]\ncharset = utf-8\n"
        tmp, root = self._make_repo(files)
        try:
            r = roadmap(root, steps=10)
            self.assertNotIn("php-structural-scan", [x["node"] for x in r])
        finally:
            tmp.cleanup()

    def test_never_in_withheld_candidates(self):
        tmp, root = self._make_repo({})
        try:
            w = withheld_candidates(root)
            self.assertNotIn("php-structural-scan", [x["node"] for x in w])
        finally:
            tmp.cleanup()


class EffectivelyRejectedRequiredAnyTests(unittest.TestCase):
    """Ticket 53: `_is_effectively_rejected` must treat a `required-any`
    parent group the same way `_is_permanently_gated` already treats it for
    its own, unrelated gate condition -- closed only once *every* option in
    the group is (recursively) effectively rejected, never on a single
    option alone, since any of the others fulfilling it still would. Unit
    tests directly against the function (same precedent as `_is_unblocked`
    being called directly elsewhere in this file) -- `rector-php-set`'s real
    `required-any(phpstan-level-0, psalm)` gate is the concrete case."""

    def test_single_required_any_option_rejected_does_not_close(self):
        tree = load_tree()
        rejected = {"phpstan-level-0"}
        self.assertFalse(tooling_tree._is_effectively_rejected("rector-php-set", tree, rejected))

    def test_all_required_any_options_rejected_does_close(self):
        tree = load_tree()
        rejected = {"phpstan-level-0", "psalm"}
        self.assertTrue(tooling_tree._is_effectively_rejected("rector-php-set", tree, rejected))

    def test_shared_ancestor_diamond_rejection_still_closes(self):
        """Ticket 60: `phpstan-level-0` and `psalm` (rector-php-set's
        required-any options) don't carry the rejection themselves here --
        both instead require `static-code-analyzer`, which requires the
        rejected `composer`. This is a diamond (two siblings re-converging
        on a shared ancestor), not a cycle -- a shared, mutable `_seen` set
        across the required-any siblings previously made the second
        sibling's honest revisit of `static-code-analyzer` look like a
        cycle, short-circuiting to `False` and leaving `rector-php-set` (and
        everything beneath it) stuck as neither fulfilled nor rejected."""
        tree = load_tree()
        rejected = {"composer"}
        self.assertTrue(tooling_tree._is_effectively_rejected("rector-php-set", tree, rejected))
        self.assertTrue(tooling_tree._is_effectively_rejected("rector-dead-code", tree, rejected))
        self.assertTrue(tooling_tree._is_effectively_rejected("psalm-taint-analysis", tree, rejected))

    def test_shared_ancestor_diamond_does_not_pollute_caller_seen(self):
        """A caller re-using one `_seen` set across sibling top-level calls
        (as `_resolved_gate_status` and `_composer_audit_extra_gate` do, one
        leaf at a time -- not the bug itself, but worth pinning down) must
        get the same answer for each sibling regardless of call order, since
        each call now receives its own copy rather than sharing the caller's
        set across recursion."""
        tree = load_tree()
        rejected = {"composer"}
        seen = set()
        first = tooling_tree._is_effectively_rejected("phpstan-level-0", tree, rejected, seen)
        second = tooling_tree._is_effectively_rejected("psalm", tree, rejected, seen)
        self.assertTrue(first)
        self.assertTrue(second)


class PermanentlyGatedDiamondTests(unittest.TestCase):
    """Ticket 60: `_is_permanently_gated` shares `_is_effectively_rejected`'s
    exact `_seen`-threading pattern and is exposed to the identical bug --
    on the real php-tooling-tree it happens not to manifest today only
    because both nodes on the diamond's shared path (`static-code-analyzer`,
    `psalm`) are themselves `_NEVER_PROPOSED` and self-gate before the
    polluted `_seen` would ever matter. A synthetic tree forces the real
    traversal, independent of that coincidence."""

    def test_shared_ancestor_diamond_still_gates(self):
        original_never_proposed = tooling_tree._NEVER_PROPOSED
        tooling_tree._NEVER_PROPOSED = original_never_proposed | {"gate-root"}
        try:
            tree = {
                "required_parents": {"left-mid": ["gate-root"], "right-mid": ["gate-root"]},
                "recommended_parents": {},
                "resolved_parents": {},
                "required_any_parents": {"child": ["left-mid", "right-mid"]},
            }
            self.assertTrue(tooling_tree._is_permanently_gated("child", tree, {}))
        finally:
            tooling_tree._NEVER_PROPOSED = original_never_proposed


class PsalmMutualExclusionTests(unittest.TestCase):
    """Ticket 37: phpstan-level-5 (was phpstan-level-10 before signals ticket
    2 lowered the level-chain leaf) is the php-structural-scan leaf a
    target's static-analyzer choice must resolve — the actual bug this
    ticket fixes (a Psalm-only target previously left the level-chain leaf
    neither fulfilled nor rejected, permanently blocking
    php-structural-scan). `psalm` itself is deliberately not a leaf (found
    redundant on review, see test_resolved_parents_of_php_structural_scan) —
    only the level-chain leaf's own resolution matters here."""

    def _make_repo(self, files: dict):
        tmp = tempfile.TemporaryDirectory()
        root = pathlib.Path(tmp.name)
        for rel, content in files.items():
            p = root / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content)
        (root / ".git").mkdir()
        return tmp, root

    def _psalm_only_files(self):
        return {
            "composer.json": json.dumps({"require": {"vimeo/psalm": "^5.0"}}),
            "composer.lock": "{}",
            "psalm.xml": "<psalm></psalm>",
        }

    def test_psalm_leaf_fulfilled_but_phpstan_level_5_leaf_unresolved_without_housekeeping(self):
        # Reproduces the bug this ticket fixes: without the mutual-exclusion
        # out-of-scope write, phpstan-level-5 sits neither fulfilled (Psalm
        # path) nor rejected (nobody wrote the file) — php-structural-scan
        # stays blocked on it forever.
        tmp, root = self._make_repo(self._psalm_only_files())
        try:
            d = detect_nodes(root)
            self.assertTrue(d["psalm"]["fulfilled"])
            self.assertFalse(d["phpstan-level-5"]["fulfilled"])
            self.assertIn("phpstan-level-5", d["php-structural-scan"]["details"]["unresolved"])
        finally:
            tmp.cleanup()

    def test_phpstan_level_5_rejection_closes_the_gap(self):
        # The fix: the recognition-pass housekeeping described on the `psalm`
        # node's own entry (php-tooling-tree.md) writes
        # out-of-scope/phpstan-level-5.md — phpstan-level-5 then resolves
        # (rejected), and it's no longer in php-structural-scan's unresolved
        # list, exactly mirroring the real php-psalm fixture (ticket 37).
        files = self._psalm_only_files()
        files["docs/refactoring/out-of-scope/phpstan-level-5.md"] = "rejected: mutual exclusion (ticket 37) — psalm path chosen\n"
        tmp, root = self._make_repo(files)
        try:
            d = detect_nodes(root)
            self.assertNotIn("phpstan-level-5", d["php-structural-scan"]["details"]["unresolved"])
        finally:
            tmp.cleanup()

    def test_co_presence_phpstan_authoritative_over_psalm(self):
        # Co-presence rule (phpstan.md, psalm.md): when both analysers are
        # genuinely adopted, PHPStan stays authoritative for the level
        # chain -- Psalm's own equivalence must not blanket every
        # phpstan-level-N as "not applicable". Reproduces a real gap found
        # live on Art4/legacy-todo: adopting psalm-taint-analysis on top of
        # an existing, already-fulfilled phpstan-level-1..5 setup made the
        # scanner read every one of those genuinely-fulfilled levels as
        # "not applicable: psalm fulfils p0" -- corrupting `refactor-learn`'s
        # `Fulfilled nodes` overwrite the next time a pass had parser access.
        tmp, root = self._make_repo({
            "composer.json": json.dumps({
                "require-dev": {
                    "phpstan/phpstan": "^1.0",
                    "vimeo/psalm": "^5.0",
                },
            }),
            "composer.lock": "{}",
            "phpstan.neon": "parameters:\n    level: 5\n",
            "phpstan-baseline.neon": "parameters:\n    ignoreErrors: []\n",
            "psalm.xml": "<psalm></psalm>",
        })
        try:
            d = detect_nodes(root)
            self.assertTrue(d["psalm"]["fulfilled"])
            self.assertTrue(d["phpstan-level-5"]["fulfilled"], d["phpstan-level-5"])
            self.assertFalse(d["phpstan-level-6"]["fulfilled"], d["phpstan-level-6"])
            self.assertNotEqual(d["phpstan-level-5"]["reason"], "not applicable: psalm fulfils p0")
            self.assertFalse(d["phpstan-level-5"]["details"].get("psalm_equivalent"))
        finally:
            tmp.cleanup()

    def test_psalm_only_still_gets_equivalence_with_phpstan_dep_but_no_level_configured(self):
        # Adopting phpstan/phpstan as a composer dep alone, with no
        # phpstan.neon/level configured, must not count as "genuinely
        # adopted" -- the Psalm-equivalence path stays available, same as a
        # target that never touched PHPStan at all.
        tmp, root = self._make_repo({
            "composer.json": json.dumps({
                "require-dev": {
                    "phpstan/phpstan": "^1.0",
                    "vimeo/psalm": "^5.0",
                },
            }),
            "composer.lock": "{}",
            "psalm.xml": "<psalm></psalm>",
        })
        try:
            d = detect_nodes(root)
            self.assertTrue(d["phpstan-level-0"]["fulfilled"], d["phpstan-level-0"])
            self.assertFalse(d["phpstan-level-1"]["fulfilled"], d["phpstan-level-1"])
            self.assertTrue(d["phpstan-level-1"]["details"].get("psalm_equivalent"))
        finally:
            tmp.cleanup()

    def test_phpstan_path_needs_no_psalm_rejection(self):
        # On the PHPStan path, php-structural-scan resolves without any
        # psalm-related out-of-scope entry at all — psalm isn't a leaf, so
        # there's nothing to reject (unlike the earlier design this ticket
        # tried and dropped, which needed docs/refactoring/out-of-scope/
        # psalm.md just to satisfy a leaf that didn't need to exist).
        tmp, root = self._make_repo({
            "composer.json": json.dumps({"require-dev": {"phpstan/phpstan": "^1.0"}}),
            "composer.lock": "{}",
            "phpstan.neon": "parameters:\n    level: 5\n",
            "phpstan-baseline.neon": "parameters:\n    ignoreErrors: []\n",
        })
        try:
            d = detect_nodes(root)
            self.assertFalse(d["psalm"]["fulfilled"])
            self.assertTrue(d["phpstan-level-5"]["fulfilled"])
            self.assertNotIn("phpstan-level-5", d["php-structural-scan"]["details"]["unresolved"])
        finally:
            tmp.cleanup()


class PsalmTaintAnalysisTests(unittest.TestCase):
    """Ticket 37: psalm-taint-analysis is unlocked via a required-any edge
    (phpstan-level-4 OR psalm), independent of the mutual exclusion above."""

    def _make_repo(self, files: dict):
        tmp = tempfile.TemporaryDirectory()
        root = pathlib.Path(tmp.name)
        for rel, content in files.items():
            p = root / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content)
        (root / ".git").mkdir()
        return tmp, root

    def test_fulfilled_via_psalm_dep_and_config(self):
        tmp, root = self._make_repo({
            "composer.json": json.dumps({"require": {"vimeo/psalm": "^5.0"}}),
            "composer.lock": "{}",
            "psalm.xml": "<psalm></psalm>",
        })
        try:
            d = detect_nodes(root)
            self.assertTrue(d["psalm-taint-analysis"]["fulfilled"], d["psalm-taint-analysis"])
        finally:
            tmp.cleanup()

    def test_is_a_php_structural_scan_resolved_leaf(self):
        # Follow-up correction: psalm-taint-analysis is a deterministic
        # security-scan tool exactly like composer-audit (also a
        # php-structural-scan leaf) — fulfilling it resolves its own leaf,
        # same as any other leaf in the set.
        tree = load_tree()
        self.assertIn("psalm-taint-analysis", tree["resolved_parents"]["php-structural-scan"])
        tmp, root = self._make_repo({
            "composer.json": json.dumps({"require": {"vimeo/psalm": "^5.0"}}),
            "composer.lock": "{}",
            "psalm.xml": "<psalm></psalm>",
        })
        try:
            d = detect_nodes(root)
            self.assertTrue(d["psalm-taint-analysis"]["fulfilled"])
            self.assertNotIn("psalm-taint-analysis", d["php-structural-scan"]["details"]["unresolved"])
        finally:
            tmp.cleanup()

    def test_unfulfilled_without_psalm(self):
        tmp, root = self._make_repo({
            "composer.json": json.dumps({"require-dev": {"phpstan/phpstan": "^1.0"}}),
            "composer.lock": "{}",
        })
        try:
            d = detect_nodes(root)
            self.assertFalse(d["psalm-taint-analysis"]["fulfilled"])
        finally:
            tmp.cleanup()

    def test_ci_present_but_not_gated_on_taint_flag_stays_unfulfilled(self):
        # Same ticket-34 CI-self-wiring shape as phpstan-level-0: once
        # ci-runner exists, a plain `vendor/bin/psalm` invocation (no
        # --taint-analysis) is not enough.
        tmp, root = self._make_repo({
            "composer.json": json.dumps({"require": {"vimeo/psalm": "^5.0"}}),
            "composer.lock": "{}",
            "psalm.xml": "<psalm></psalm>",
            ".github/workflows/ci.yml": "jobs:\n  analyse:\n    steps:\n      - run: vendor/bin/psalm\n",
        })
        try:
            d = detect_nodes(root)
            self.assertFalse(d["psalm-taint-analysis"]["fulfilled"], d["psalm-taint-analysis"])
        finally:
            tmp.cleanup()

    def test_ci_gated_on_taint_flag_fulfils(self):
        tmp, root = self._make_repo({
            "composer.json": json.dumps({"require": {"vimeo/psalm": "^5.0"}}),
            "composer.lock": "{}",
            "psalm.xml": "<psalm></psalm>",
            ".github/workflows/ci.yml": "jobs:\n  analyse:\n    steps:\n      - run: vendor/bin/psalm --taint-analysis\n",
        })
        try:
            d = detect_nodes(root)
            self.assertTrue(d["psalm-taint-analysis"]["fulfilled"], d["psalm-taint-analysis"])
        finally:
            tmp.cleanup()

    def test_not_proposable_when_neither_required_any_parent_fulfilled(self):
        # phpstan at level 0 only (not level 4), no psalm at all.
        tmp, root = self._make_repo({
            "composer.json": json.dumps({"require-dev": {"phpstan/phpstan": "^1.0"}}),
            "composer.lock": "{}",
            "phpstan.neon": "parameters:\n    level: 0\n",
            "phpstan-baseline.neon": "parameters:\n    ignoreErrors: []\n",
        })
        try:
            nodes = [c["node"] for c in next_candidates(root, limit=20)]
            self.assertNotIn("psalm-taint-analysis", nodes)
        finally:
            tmp.cleanup()

    def test_proposable_once_phpstan_level_4_fulfilled(self):
        tmp, root = self._make_repo({
            "composer.json": json.dumps({"require-dev": {"phpstan/phpstan": "^1.0"}}),
            "composer.lock": "{}",
            "phpstan.neon": "parameters:\n    level: 4\n",
            "phpstan-baseline.neon": "parameters:\n    ignoreErrors: []\n",
        })
        try:
            nodes = [c["node"] for c in next_candidates(root, limit=20)]
            self.assertIn("psalm-taint-analysis", nodes)
        finally:
            tmp.cleanup()


class PsrFourGateTests(unittest.TestCase):
    """Ticket 50: `psr-4` — declared AND verifiably in use, not declaration
    alone (php-tooling-tree/psr-4.md's Fulfilment check)."""

    def _make_repo(self, files: dict):
        tmp = tempfile.TemporaryDirectory()
        root = pathlib.Path(tmp.name)
        for rel, content in files.items():
            p = root / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content)
        (root / ".git").mkdir()
        return tmp, root

    def test_required_parent_is_composer(self):
        tree = load_tree()
        self.assertEqual(tree["required_parents"]["psr-4"], ["composer"])

    def test_unfulfilled_when_no_autoload_declared(self):
        tmp, root = self._make_repo({
            "composer.json": json.dumps({"require-dev": {}}),
            "composer.lock": "{}",
        })
        try:
            d = detect_nodes(root)
            self.assertFalse(d["psr-4"]["fulfilled"])
            self.assertFalse(d["psr-4"]["details"]["declared"])
        finally:
            tmp.cleanup()

    def test_unfulfilled_when_declared_but_unused(self):
        # A declaration nothing yet uses is a claim, not evidence — the
        # exact pattern ticket 48 flagged as a problem for a different node.
        tmp, root = self._make_repo({
            "composer.json": json.dumps({"autoload": {"psr-4": {"App\\": "src/"}}}),
            "composer.lock": "{}",
        })
        try:
            d = detect_nodes(root)
            self.assertFalse(d["psr-4"]["fulfilled"])
            self.assertTrue(d["psr-4"]["details"]["declared"])
            self.assertIn("declared but no file", d["psr-4"]["reason"])
        finally:
            tmp.cleanup()

    def test_fulfilled_when_declared_and_a_real_file_uses_it(self):
        tmp, root = self._make_repo({
            "composer.json": json.dumps({"autoload": {"psr-4": {"App\\": "src/"}}}),
            "composer.lock": "{}",
            "src/Example.php": "<?php\n\nnamespace App;\n\nclass Example\n{\n}\n",
        })
        try:
            d = detect_nodes(root)
            self.assertTrue(d["psr-4"]["fulfilled"], d["psr-4"])
        finally:
            tmp.cleanup()

    def test_unfulfilled_when_file_under_mapped_dir_uses_a_different_namespace(self):
        # A file exists under the mapped directory, but doesn't actually
        # declare the mapped namespace — not proof the mapping is in use.
        tmp, root = self._make_repo({
            "composer.json": json.dumps({"autoload": {"psr-4": {"App\\": "src/"}}}),
            "composer.lock": "{}",
            "src/Example.php": "<?php\n\nnamespace SomethingElse;\n\nclass Example\n{\n}\n",
        })
        try:
            d = detect_nodes(root)
            self.assertFalse(d["psr-4"]["fulfilled"])
        finally:
            tmp.cleanup()

    def test_fulfilled_with_array_of_directories(self):
        # Composer's own schema allows a psr-4 prefix to map to a list of
        # directories, not just one — must not assume a bare string.
        tmp, root = self._make_repo({
            "composer.json": json.dumps({"autoload": {"psr-4": {"App\\": ["src/", "lib/"]}}}),
            "composer.lock": "{}",
            "lib/Example.php": "<?php\n\nnamespace App;\n\nclass Example\n{\n}\n",
        })
        try:
            d = detect_nodes(root)
            self.assertTrue(d["psr-4"]["fulfilled"], d["psr-4"])
        finally:
            tmp.cleanup()

    def test_resolved_parent_of_php_structural_scan(self):
        tree = load_tree()
        self.assertIn("psr-4", tree["resolved_parents"]["php-structural-scan"])


class Psr4AutoloaderWiringTests(unittest.TestCase):
    """Ticket 58: psr-4's fulfilment gains a second criterion on top of the
    mapping-mechanism bar above (PsrFourGateTests) -- the autoloader is
    actually wired into the target's own Composition root, or every Entry
    point when there's no single root (CONTEXT.md, php-tooling-tree/
    psr-4.md's own Fulfilment check)."""

    def _make_repo(self, files: dict):
        tmp = tempfile.TemporaryDirectory()
        root = pathlib.Path(tmp.name)
        for rel, content in files.items():
            p = root / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content)
        (root / ".git").mkdir()
        return tmp, root

    _COMPOSER_MAPPED = json.dumps({"autoload": {"psr-4": {"App\\": "src/"}}})

    def test_unfulfilled_when_entry_point_exists_but_autoloader_not_wired(self):
        tmp, root = self._make_repo({
            "composer.json": self._COMPOSER_MAPPED,
            "composer.lock": "{}",
            "src/Example.php": "<?php\n\nnamespace App;\n\nclass Example\n{\n}\n",
            "public/index.php": "<?php\necho 'hi';\n",
        })
        try:
            d = detect_nodes(root)
            self.assertFalse(d["psr-4"]["fulfilled"], d["psr-4"])
            self.assertTrue(d["psr-4"]["details"]["mechanism_verified"])
            self.assertFalse(d["psr-4"]["details"]["autoloader_wired"])
            self.assertIn("autoloader isn't wired", d["psr-4"]["reason"])
            self.assertEqual(d["psr-4"]["details"]["unwired_entry_points"], ["public/index.php"])
        finally:
            tmp.cleanup()

    def test_fulfilled_reports_empty_unwired_list(self):
        tmp, root = self._make_repo({
            "composer.json": self._COMPOSER_MAPPED,
            "composer.lock": "{}",
            "src/Example.php": "<?php\n\nnamespace App;\n\nclass Example\n{\n}\n",
            "public/index.php": "<?php\nrequire_once __DIR__ . '/../vendor/autoload.php';\necho 'hi';\n",
        })
        try:
            d = detect_nodes(root)
            self.assertTrue(d["psr-4"]["fulfilled"], d["psr-4"])
            self.assertEqual(d["psr-4"]["details"]["unwired_entry_points"], [])
        finally:
            tmp.cleanup()

    def test_generated_ci_helper_script_is_still_reported_as_unwired(self):
        # Real false positive caught live on Art4/legacy-todo (PR #229): a
        # tooling-tree node's own generated CI-helper script (coverage-
        # floor's scripts/check-coverage-floor.php) is a real, unrequired
        # .php file that structurally never needs the app's own classes.
        # Deliberately NOT special-cased away here (see ADR-0046's revised
        # decision) -- the deterministic layer stays a simple, honest
        # "does this candidate's text contain the autoload.php require"
        # check and reports it plainly; sorting a genuine application entry
        # point from a script like this one is an agentic judgement call
        # documented in php-tooling-tree/psr-4.md's own Fulfilment check,
        # not something this parser tries to guess at.
        tmp, root = self._make_repo({
            "composer.json": self._COMPOSER_MAPPED,
            "composer.lock": "{}",
            "src/Example.php": "<?php\n\nnamespace App;\n\nclass Example\n{\n}\n",
            "public/index.php": "<?php\nrequire_once __DIR__ . '/../vendor/autoload.php';\necho 'hi';\n",
            "scripts/check-coverage-floor.php": (
                "#!/usr/bin/env php\n<?php\n$xml = simplexml_load_file($argv[1]);\necho 'ok';\n"
            ),
        })
        try:
            d = detect_nodes(root)
            self.assertFalse(d["psr-4"]["fulfilled"], d["psr-4"])
            self.assertEqual(
                d["psr-4"]["details"]["unwired_entry_points"],
                ["scripts/check-coverage-floor.php"],
            )
        finally:
            tmp.cleanup()

    def test_fulfilled_when_the_single_entry_point_requires_autoload_directly(self):
        tmp, root = self._make_repo({
            "composer.json": self._COMPOSER_MAPPED,
            "composer.lock": "{}",
            "src/Example.php": "<?php\n\nnamespace App;\n\nclass Example\n{\n}\n",
            "public/index.php": "<?php\nrequire_once __DIR__ . '/../vendor/autoload.php';\necho 'hi';\n",
        })
        try:
            d = detect_nodes(root)
            self.assertTrue(d["psr-4"]["fulfilled"], d["psr-4"])
        finally:
            tmp.cleanup()

    def test_fulfilled_via_composition_root_wiring_alone(self):
        # Two entry points both delegate to bootstrap.php -- wiring the
        # autoloader there alone is enough, no entry point needs its own.
        tmp, root = self._make_repo({
            "composer.json": self._COMPOSER_MAPPED,
            "composer.lock": "{}",
            "src/Example.php": "<?php\n\nnamespace App;\n\nclass Example\n{\n}\n",
            "src/Bootstrap.php": "<?php\nrequire_once __DIR__ . '/../vendor/autoload.php';\n",
            "public/a.php": "<?php\nrequire_once __DIR__ . '/../src/Bootstrap.php';\n",
            "public/b.php": "<?php\nrequire_once __DIR__ . '/../src/Bootstrap.php';\n",
        })
        try:
            d = detect_nodes(root)
            self.assertTrue(d["psr-4"]["fulfilled"], d["psr-4"])
        finally:
            tmp.cleanup()

    def test_composition_root_recognized_with_a_straggler_needing_its_own_wiring(self):
        # a.php and b.php converge on bootstrap.php (a real majority: 2 of
        # 3) -- c.php doesn't. bootstrap.php is recognized as the
        # composition root regardless, but c.php still needs its own direct
        # wiring -- fulfilled only once both are satisfied.
        base_files = {
            "composer.json": self._COMPOSER_MAPPED,
            "composer.lock": "{}",
            "src/Example.php": "<?php\n\nnamespace App;\n\nclass Example\n{\n}\n",
            "src/Bootstrap.php": "<?php\nrequire_once __DIR__ . '/../vendor/autoload.php';\n",
            "public/a.php": "<?php\nrequire_once __DIR__ . '/../src/Bootstrap.php';\n",
            "public/b.php": "<?php\nrequire_once __DIR__ . '/../src/Bootstrap.php';\n",
            "public/c.php": "<?php\necho 'legacy standalone page';\n",
        }
        tmp, root = self._make_repo(base_files)
        try:
            d = detect_nodes(root)
            self.assertFalse(d["psr-4"]["fulfilled"], d["psr-4"])
            (root / "public" / "c.php").write_text(
                "<?php\nrequire_once __DIR__ . '/../vendor/autoload.php';\necho 'legacy standalone page';\n"
            )
            d = detect_nodes(root)
            self.assertTrue(d["psr-4"]["fulfilled"], d["psr-4"])
        finally:
            tmp.cleanup()

    def test_exact_tie_recognizes_no_composition_root(self):
        # 2 of 4 entry points converge on bootstrap.php -- exactly half, not
        # a real majority (best_count * 2 > len(entry_points) must be a
        # strict inequality). No composition root is recognized, so wiring
        # bootstrap.php alone is not enough -- every entry point needs its
        # own direct require, even a.php/b.php which do converge.
        tmp, root = self._make_repo({
            "composer.json": self._COMPOSER_MAPPED,
            "composer.lock": "{}",
            "src/Example.php": "<?php\n\nnamespace App;\n\nclass Example\n{\n}\n",
            "src/Bootstrap.php": "<?php\nrequire_once __DIR__ . '/../vendor/autoload.php';\n",
            "public/a.php": "<?php\nrequire_once __DIR__ . '/../src/Bootstrap.php';\n",
            "public/b.php": "<?php\nrequire_once __DIR__ . '/../src/Bootstrap.php';\n",
            "public/c.php": "<?php\necho 'standalone c';\n",
            "public/d.php": "<?php\necho 'standalone d';\n",
        })
        try:
            d = detect_nodes(root)
            self.assertFalse(d["psr-4"]["fulfilled"], d["psr-4"])
            # Confirm it's genuinely "no composition root", not just "c/d
            # unwired" -- even a.php, which does converge on bootstrap.php,
            # is unfulfilled on its own until it requires autoload.php
            # itself, since bootstrap.php's own wiring isn't credited to it.
            _, composition_root, wiring_targets = tooling_tree._detect_entry_points(root, ["src/"])
            self.assertIsNone(composition_root)
            self.assertEqual(len(wiring_targets), 4)
        finally:
            tmp.cleanup()

    def test_vacuously_fulfilled_with_no_entry_points_at_all(self):
        # Every .php file sits under the mapped namespace directory itself
        # -- nothing to wire, same "nothing to recommend" convention this
        # tree already uses for an undeterminable PHP floor.
        tmp, root = self._make_repo({
            "composer.json": self._COMPOSER_MAPPED,
            "composer.lock": "{}",
            "src/Example.php": "<?php\n\nnamespace App;\n\nclass Example\n{\n}\n",
        })
        try:
            d = detect_nodes(root)
            self.assertTrue(d["psr-4"]["fulfilled"], d["psr-4"])
            self.assertTrue(d["psr-4"]["details"]["autoloader_wired"])
        finally:
            tmp.cleanup()

    def test_tooling_config_php_files_are_never_treated_as_entry_points(self):
        # rector.php/.php-cs-fixer.php are real, unrequired, top-level .php
        # files -- without the exclusion they'd wrongly need autoload.php
        # wiring too, since nothing in the source tree requires them either.
        tmp, root = self._make_repo({
            "composer.json": self._COMPOSER_MAPPED,
            "composer.lock": "{}",
            "src/Example.php": "<?php\n\nnamespace App;\n\nclass Example\n{\n}\n",
            "rector.php": "<?php // DeadCode\n",
            ".php-cs-fixer.php": "<?php return [];\n",
        })
        try:
            d = detect_nodes(root)
            self.assertTrue(d["psr-4"]["fulfilled"], d["psr-4"])
        finally:
            tmp.cleanup()

    def test_entry_point_inside_tests_directory_excluded(self):
        tmp, root = self._make_repo({
            "composer.json": self._COMPOSER_MAPPED,
            "composer.lock": "{}",
            "src/Example.php": "<?php\n\nnamespace App;\n\nclass Example\n{\n}\n",
            "tests/SomeScript.php": "<?php\necho 'not an app entry point';\n",
        })
        try:
            d = detect_nodes(root)
            self.assertTrue(d["psr-4"]["fulfilled"], d["psr-4"])
        finally:
            tmp.cleanup()


class ComposerAuditGateTests(unittest.TestCase):
    """php-tooling-tree.md's composer-audit stop conditions: proposable once
    ci-runner + composer are fulfilled, and (a real `require` dependency
    exists, or every other leaf feeding php-structural-scan is already
    resolved)."""

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
        # No real dependency at all, but every other leaf feeding
        # php-structural-scan is fulfilled — composer-audit must still
        # eventually become proposable, or php-structural-scan (and so
        # structural-scan) would never open on a dependency-free target.
        tmp, root = self._make_repo({
            "composer.json": json.dumps({
                "require-dev": {
                    "phpstan/phpstan": "^1.0",
                    "phpstan/phpstan-deprecation-rules": "^1.0",
                    "phpunit/phpunit": "^10.0",
                    "friendsofphp/php-cs-fixer": "^3.0",
                },
            }),
            "composer.lock": "{}",
            ".php-cs-fixer.php": "<?php return [];",
            # signals ticket 2: the level-chain leaf is phpstan-level-5 now.
            "phpstan.neon": "parameters:\n    level: 5\n",
            "phpstan-baseline.neon": "parameters:\n    ignoreErrors: []\n",
            "rector.php": "<?php // DeadCode Type LevelSetList CodeQuality PHPUnitSetList",
            # ticket 42: editorconfig is no longer one of composer-audit's
            # siblings (it gates structural-scan directly, not
            # php-structural-scan) — kept here anyway, harmless, so this
            # fixture also happens to be "fully tooled" overall.
            ".editorconfig": "root = true\n\n[*]\ncharset = utf-8\n",
            # No `composer audit` here — deliberate (see docstring). Does
            # invoke phpunit/phpstan though, so phpunit/phpstan-level-10
            # genuinely resolve too (ticket 34's self-wiring); otherwise this
            # fixture would no longer have "every other leaf resolved".
            ".github/workflows/ci.yml": (
                "jobs:\n"
                "  build:\n"
                "    steps:\n"
                "      - run: vendor/bin/phpunit\n"
                "      - run: vendor/bin/phpstan analyse\n"
            ),
            # ticket 44: `psalm-taint-analysis` is one of the "every other
            # leaf" — written rejected here, same PHPStan-path reasoning as
            # the other "fully tooled" fixtures above. `psalm` itself is not
            # a leaf (ticket 37, dropped as redundant) so it needs none.
            "docs/refactoring/out-of-scope/psalm-taint-analysis.md": "rejected: no taint analysis adopted\n",
            # ticket 50: `psr-4` joined the same "every other leaf" set —
            # rejected here rather than adopted, simplest way to keep this
            # fixture focused on composer-audit's own fallback logic.
            "docs/refactoring/out-of-scope/psr-4.md": "rejected: not adopting namespacing yet\n",
        })
        try:
            nodes = [c["node"] for c in next_candidates(root, limit=10)]
            self.assertIn("composer-audit", nodes)
        finally:
            tmp.cleanup()

    def test_eligible_via_fallback_when_leaf_effectively_rejected_through_ancestor(self):
        # Ticket 55 (signals ticket 2 lowered the leaf to phpstan-level-5):
        # phpstan-level-5 (the actual php-structural-scan leaf) isn't itself
        # rejected and isn't fulfilled either -- only phpstan-level-2, a
        # required ancestor up its own chain, is (per ticket 53's own
        # decision, only the directly-rejected node gets an out-of-scope
        # entry). _composer_audit_extra_gate's "every other leaf resolved"
        # fallback must count phpstan-level-5 as resolved via
        # _is_effectively_rejected the same way _resolved_gate_status
        # already does (ticket 53/ADR-0035) -- before ticket 55's fix it
        # used a raw `leaf in rejected` check and stayed stuck forever,
        # exactly the live gap found on Art4/legacy-todo.
        tmp, root = self._make_repo({
            "composer.json": json.dumps({
                "require-dev": {
                    "phpstan/phpstan": "^1.0",
                    "phpstan/phpstan-deprecation-rules": "^1.0",
                    "phpunit/phpunit": "^10.0",
                    "friendsofphp/php-cs-fixer": "^3.0",
                },
            }),
            "composer.lock": "{}",
            ".php-cs-fixer.php": "<?php return [];",
            "phpstan.neon": "parameters:\n    level: 1\n",
            "phpstan-baseline.neon": "parameters:\n    ignoreErrors: []\n",
            "rector.php": "<?php // DeadCode Type LevelSetList CodeQuality PHPUnitSetList",
            # No `composer audit` here -- deliberate, so composer-audit's own
            # fallback path (not direct CI-job fulfilment) is what's under
            # test. Does invoke phpunit/phpstan, so those leaves genuinely
            # resolve too (ticket 34's self-wiring).
            ".github/workflows/ci.yml": (
                "jobs:\n"
                "  build:\n"
                "    steps:\n"
                "      - run: vendor/bin/phpunit\n"
                "      - run: vendor/bin/phpstan analyse\n"
            ),
            "docs/refactoring/out-of-scope/psalm-taint-analysis.md": "rejected: no taint analysis adopted\n",
            "docs/refactoring/out-of-scope/psr-4.md": "rejected: not adopting namespacing yet\n",
            # The rejection that matters: phpstan-level-2 only, never
            # phpstan-level-5 itself.
            "docs/refactoring/out-of-scope/phpstan-level-2.md": "rejected: declined\n",
        })
        try:
            d = detect_nodes(root)
            self.assertFalse(d["phpstan-level-5"]["fulfilled"], d["phpstan-level-5"])
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
    """Ticket 34: phpunit's and phpstan-level-0's own fulfilment
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
    _CI_YML_PHPSTAN_EPHEMERAL = (
        "jobs:\n  analyse:\n    steps:\n      - run: |\n"
        "          composer require --dev phpstan/phpstan\n"
        "          vendor/bin/phpstan analyse\n"
    )
    _CI_YML_PHPSTAN_MENTIONED_ONLY = (
        "jobs:\n  lint:\n    steps:\n"
        "      - run: echo 'consider adding phpstan/phpstan later'\n"
    )
    _CI_YML_PHPSTAN_INSTALLED_NOT_RUN = (
        "jobs:\n  install:\n    steps:\n      - run: composer require --dev phpstan/phpstan\n"
    )

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
            self.assertTrue(d["phpstan-level-0"]["fulfilled"], d["phpstan-level-0"])
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
            self.assertFalse(d["phpstan-level-0"]["fulfilled"], d["phpstan-level-0"])
            self.assertIn("not gated in CI", d["phpstan-level-0"]["reason"])
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
            self.assertTrue(d["phpstan-level-0"]["fulfilled"], d["phpstan-level-0"])
        finally:
            tmp.cleanup()

    def test_phpstan_p0_fulfilled_via_ephemeral_ci_install(self):
        # phpstan/phpstan absent from composer.json entirely (a target may
        # deliberately keep its own manifest free of pure-analysis tooling)
        # -- but a CI job installs it at runtime and invokes it. Same
        # fulfilment as a committed dependency.
        tmp, root = self._make_repo({
            "composer.json": json.dumps({}),
            "composer.lock": "{}",
            "phpstan.neon": "parameters:\n    level: 0\n",
            "phpstan-baseline.neon": "parameters:\n    ignoreErrors: []\n",
            ".github/workflows/ci.yml": self._CI_YML_PHPSTAN_EPHEMERAL,
        })
        try:
            d = detect_nodes(root)
            self.assertTrue(d["phpstan-level-0"]["fulfilled"], d["phpstan-level-0"])
            self.assertTrue(d["phpstan-level-0"]["details"]["ephemeral_ci_dep"])
        finally:
            tmp.cleanup()

    def test_phpstan_p0_not_fulfilled_on_mention_alone(self):
        # "phpstan" appearing in CI text with neither a real `composer
        # require` nor an invocation must not false-positive.
        tmp, root = self._make_repo({
            "composer.json": json.dumps({}),
            "composer.lock": "{}",
            "phpstan.neon": "parameters:\n    level: 0\n",
            "phpstan-baseline.neon": "parameters:\n    ignoreErrors: []\n",
            ".github/workflows/ci.yml": self._CI_YML_PHPSTAN_MENTIONED_ONLY,
        })
        try:
            d = detect_nodes(root)
            self.assertFalse(d["phpstan-level-0"]["fulfilled"], d["phpstan-level-0"])
        finally:
            tmp.cleanup()

    def test_phpstan_p0_not_fulfilled_when_ephemeral_install_never_run(self):
        # Installed at CI runtime but never actually invoked -- not gated,
        # same "not gated in CI" outcome as a committed-but-unwired dep.
        tmp, root = self._make_repo({
            "composer.json": json.dumps({}),
            "composer.lock": "{}",
            "phpstan.neon": "parameters:\n    level: 0\n",
            "phpstan-baseline.neon": "parameters:\n    ignoreErrors: []\n",
            ".github/workflows/ci.yml": self._CI_YML_PHPSTAN_INSTALLED_NOT_RUN,
        })
        try:
            d = detect_nodes(root)
            self.assertFalse(d["phpstan-level-0"]["fulfilled"], d["phpstan-level-0"])
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
            self.assertTrue(d["phpstan-level-0"]["fulfilled"], d["phpstan-level-0"])
        finally:
            tmp.cleanup()

    def test_phpstan_p0_stays_fulfilled_once_advanced_past_level_zero(self):
        # Regression guard: phpstan-level-0's own fulfilment check must not
        # require the config to still literally say `level: 0` once the
        # project has moved on to a higher level — every level-0 check
        # (dep present, baseline committed, CI gated) is still satisfied by
        # a project at level 1+, and phpstan-level-1's own required-parent
        # check depends on phpstan-level-0 staying reported as fulfilled.
        tmp, root = self._make_repo({
            "composer.json": json.dumps({"require-dev": {"phpstan/phpstan": "^1.0"}}),
            "composer.lock": "{}",
            "phpstan.neon": "parameters:\n    level: 1\n",
            "phpstan-baseline.neon": "parameters:\n    ignoreErrors: []\n",
            ".github/workflows/ci.yml": self._CI_YML_PHPSTAN,
        })
        try:
            d = detect_nodes(root)
            self.assertTrue(d["phpstan-level-0"]["fulfilled"], d["phpstan-level-0"])
            self.assertTrue(d["phpstan-level-1"]["fulfilled"], d["phpstan-level-1"])
        finally:
            tmp.cleanup()

    def test_fulfilled_level_exposes_non_empty_baseline_in_details(self):
        # Regression guard for ticket 51's baseline-shrink mechanism:
        # refactor-scan step 4b reads detect_nodes()'s own output to find
        # the highest fulfilled phpstan-level-N and check its baseline —
        # no separate detection path exists, so `fulfilled` staying True
        # alongside `details.baseline_empty` staying False (real, unshrunk
        # findings) is the exact signal that mechanism depends on.
        tmp, root = self._make_repo({
            "composer.json": json.dumps({"require-dev": {"phpstan/phpstan": "^1.0"}}),
            "composer.lock": "{}",
            "phpstan.neon": "parameters:\n    level: 1\n",
            "phpstan-baseline.neon": (
                "parameters:\n    ignoreErrors:\n"
                "        -\n"
                "            message: '#^Variable \\$db might not be defined\\.$#'\n"
                "            count: 1\n"
                "            path: db.php\n"
            ),
            ".github/workflows/ci.yml": self._CI_YML_PHPSTAN,
        })
        try:
            d = detect_nodes(root)
            self.assertTrue(d["phpstan-level-1"]["fulfilled"], d["phpstan-level-1"])
            self.assertFalse(d["phpstan-level-1"]["details"]["baseline_empty"], d["phpstan-level-1"])
        finally:
            tmp.cleanup()


class RectorSetListUnderscoreCasingTests(unittest.TestCase):
    """Rector's current SetList API names sets as ALL_CAPS-with-underscore
    class constants (e.g. `SetList::DEAD_CODE`, `SetList::CODE_QUALITY`),
    not the older PascalCase-ish prose the substring detection originally
    matched. Lowercasing alone doesn't bridge the two: "DEAD_CODE" lowers to
    "dead_code", not "dead-code" -- detection must tolerate both forms."""

    def _make_repo(self, files: dict):
        tmp = tempfile.TemporaryDirectory()
        root = pathlib.Path(tmp.name)
        for rel, content in files.items():
            p = root / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content)
        (root / ".git").mkdir()
        return tmp, root

    def test_dead_code_and_code_quality_detected_via_underscore_constants(self):
        tmp, root = self._make_repo({
            "rector.php": (
                "<?php\nreturn RectorConfig::configure()->withSets(["
                "SetList::DEAD_CODE, SetList::CODE_QUALITY, LevelSetList::UP_TO_PHP_82,"
                "]);\n"
            ),
        })
        try:
            d = detect_nodes(root)
            self.assertTrue(d["rector-dead-code"]["fulfilled"], d["rector-dead-code"])
            self.assertTrue(d["rector-code-quality"]["fulfilled"], d["rector-code-quality"])
            self.assertTrue(d["rector-php-set"]["fulfilled"], d["rector-php-set"])
        finally:
            tmp.cleanup()

    def test_dead_code_and_code_quality_still_detected_via_old_pascalcase_prose(self):
        # Not a regression against the original (still-valid) detection style.
        tmp, root = self._make_repo({
            "rector.php": "<?php // DeadCode CodeQuality LevelSetList",
        })
        try:
            d = detect_nodes(root)
            self.assertTrue(d["rector-dead-code"]["fulfilled"], d["rector-dead-code"])
            self.assertTrue(d["rector-code-quality"]["fulfilled"], d["rector-code-quality"])
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
        # phpstan-level-0 fulfilled (unblocks rector-php-set via its
        # required-any gate); php-cs-fixer and phpstan-level-3 both stay
        # undecided (neither fulfilled nor rejected). `.editorconfig` present
        # (ticket 01: php-cs-fixer's own recommended parent) so php-cs-fixer
        # itself stays proposable here — its undecided status under test is
        # about rector-dead-code's gate, not php-cs-fixer's own. `rector.php`
        # fulfils rector-php-set only (ticket 43) — no DeadCode/Type/
        # CodeQuality markers, so rector-dead-code/rector-type-coverage/
        # rector-code-quality all stay unfulfilled, exactly what each test
        # below is probing. rector-type-coverage no longer has rector-php-set
        # as a required parent at all (follow-up restructuring) — it's gated
        # by rector-dead-code/rector-code-quality as recommended parents
        # instead, alongside php-cs-fixer/phpstan-level-3 (ticket 48:
        # rector-code-quality replaced the now-dropped rector-early-return
        # in this gate).
        return {
            "composer.json": json.dumps({"require-dev": {"phpstan/phpstan": "^1.0"}}),
            "composer.lock": "{}",
            "phpstan.neon": "parameters:\n    level: 0\n",
            "phpstan-baseline.neon": "parameters:\n    ignoreErrors: []\n",
            ".editorconfig": "root = true\n\n[*]\ncharset = utf-8\n",
            "rector.php": "<?php // LevelSetList",
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
            (root / "docs" / "refactoring" / "out-of-scope").mkdir(parents=True, exist_ok=True)
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
        # rector-type-coverage also gained rector-dead-code/rector-code-quality
        # as recommended parents (follow-up restructuring; ticket 48 swapped
        # in rector-code-quality where rector-early-return used to be) —
        # decided here via rejection, since this fixture's rector.php doesn't
        # fulfil either.
        files = self._p0_fulfilled_files()
        files["composer.json"] = json.dumps({"require-dev": {
            "phpstan/phpstan": "^1.0",
            "friendsofphp/php-cs-fixer": "^3.0",
        }})
        files[".php-cs-fixer.php"] = "<?php return [];"
        tmp, root = self._make_repo(files)
        try:
            (root / "docs" / "refactoring" / "out-of-scope").mkdir(parents=True, exist_ok=True)
            (root / "docs" / "refactoring" / "out-of-scope" / "phpstan-level-1.md").write_text("rejected\n")
            (root / "docs" / "refactoring" / "out-of-scope" / "rector-dead-code.md").write_text("rejected\n")
            (root / "docs" / "refactoring" / "out-of-scope" / "rector-code-quality.md").write_text("rejected\n")
            nodes = [c["node"] for c in next_candidates(root)]
            self.assertIn("rector-type-coverage", nodes)
        finally:
            tmp.cleanup()

    def test_withheld_candidates_names_the_waiting_on_parents(self):
        tmp, root = self._make_repo(self._p0_fulfilled_files())
        try:
            withheld = {w["node"]: set(w["waiting_on"]) for w in withheld_candidates(root)}
            self.assertEqual(withheld["rector-dead-code"], {"php-cs-fixer"})
            self.assertEqual(
                withheld["rector-type-coverage"],
                {"rector-dead-code", "rector-code-quality", "php-cs-fixer", "phpstan-level-3"},
            )
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
            "docs/refactoring/bookkeeping.md": "# Refactoring Loop Config\n\n**Cadence:** weekly\n",
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
        tmp, root = self._make_repo({})  # no docs/refactoring/bookkeeping.md
        try:
            nodes = [c["node"] for c in next_candidates(root)]
            self.assertNotIn("editorconfig", nodes)
            self.assertIn("loop-config", nodes)
        finally:
            tmp.cleanup()

    def test_proposable_once_loop_config_fulfilled(self):
        tmp, root = self._make_repo({"docs/refactoring/bookkeeping.md": "# Refactoring Loop Config\n"})
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
            (root / "docs" / "refactoring" / "out-of-scope").mkdir(parents=True, exist_ok=True)
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


class IsPhpProjectTests(unittest.TestCase):
    """ADR-0022: `is-php-project` — the PHP specialization's recognition
    gate, declared in `tooling-tree.md` (the generic root), required parent
    of `composer` in `php-tooling-tree.md`. `_NEVER_PROPOSED`
    (like `git`), so it never appears in `next`/`roadmap`/`withheld` itself —
    only its gating effect on `composer` (and, transitively through the
    tree, `php-minimal-version` -- ticket 57 dropped its own direct
    required parent on this node) is visible there."""

    def _make_repo(self, files: dict):
        tmp = tempfile.TemporaryDirectory()
        root = pathlib.Path(tmp.name)
        for rel, content in files.items():
            p = root / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content)
        (root / ".git").mkdir()
        return tmp, root

    def _loop_config_only(self):
        return {"docs/refactoring/bookkeeping.md": "# Refactoring Loop Config\n\n**Cadence:** weekly\n"}

    def test_unfulfilled_with_no_composer_json_and_no_php_files(self):
        tmp, root = self._make_repo({"index.html": "<html></html>\n", "styles.css": "body{}\n"})
        try:
            d = detect_nodes(root)
            self.assertFalse(d["is-php-project"]["fulfilled"])
        finally:
            tmp.cleanup()

    def test_fulfilled_via_php_file_without_composer_json(self):
        files = self._loop_config_only()
        files["src/Foo.php"] = "<?php\n"
        tmp, root = self._make_repo(files)
        try:
            d = detect_nodes(root)
            self.assertTrue(d["is-php-project"]["fulfilled"])
            self.assertFalse(d["is-php-project"]["details"]["has_composer_json"])
            self.assertTrue(d["is-php-project"]["details"]["has_php_files"])
        finally:
            tmp.cleanup()

    def test_fulfilled_via_composer_json_without_php_files(self):
        files = self._loop_config_only()
        files["composer.json"] = json.dumps({"name": "test/app"})
        tmp, root = self._make_repo(files)
        try:
            d = detect_nodes(root)
            self.assertTrue(d["is-php-project"]["fulfilled"])
        finally:
            tmp.cleanup()

    def test_vendor_php_files_do_not_count(self):
        files = self._loop_config_only()
        files["vendor/some-pkg/src/Bar.php"] = "<?php\n"
        tmp, root = self._make_repo(files)
        try:
            d = detect_nodes(root)
            self.assertFalse(d["is-php-project"]["fulfilled"])
        finally:
            tmp.cleanup()

    def test_composer_and_php_minimal_version_absent_from_next_while_unfulfilled(self):
        tmp, root = self._make_repo(self._loop_config_only())
        try:
            nodes = [c["node"] for c in next_candidates(root)]
            self.assertNotIn("composer", nodes)
            self.assertNotIn("php-minimal-version", nodes)
            # ci-runner/editorconfig stay reachable — language-neutral, not
            # gated by is-php-project.
            self.assertIn("ci-runner", nodes)
            self.assertIn("editorconfig", nodes)
        finally:
            tmp.cleanup()

    def test_composer_released_once_is_php_project_fulfilled(self):
        files = self._loop_config_only()
        files["src/Foo.php"] = "<?php\n"
        tmp, root = self._make_repo(files)
        try:
            nodes = [c["node"] for c in next_candidates(root)]
            self.assertIn("composer", nodes)
        finally:
            tmp.cleanup()

    def test_never_in_next_roadmap_or_withheld(self):
        tmp, root = self._make_repo(self._loop_config_only())
        try:
            self.assertNotIn("is-php-project", [c["node"] for c in next_candidates(root)])
            self.assertNotIn("is-php-project", [r["node"] for r in roadmap(root, steps=10)])
            self.assertNotIn("is-php-project", [w["node"] for w in withheld_candidates(root)])
        finally:
            tmp.cleanup()

    def test_retroactively_activates_once_php_appears(self):
        # The user's own requirement: a target that starts non-PHP and only
        # later becomes one opens the tree automatically, no separate
        # mechanism needed — detect_nodes() re-derives from scratch every
        # call, nothing caches the earlier "no PHP" state.
        tmp, root = self._make_repo(self._loop_config_only())
        try:
            self.assertNotIn("composer", [c["node"] for c in next_candidates(root)])
            (root / "src").mkdir(parents=True, exist_ok=True)
            (root / "src" / "Foo.php").write_text("<?php\n")
            self.assertTrue(detect_nodes(root)["is-php-project"]["fulfilled"])
            self.assertIn("composer", [c["node"] for c in next_candidates(root)])
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
        # phpstan-level-0 (phpstan/phpstan has required PHP >=7.1
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
            self.assertEqual(blocked, {"composer-audit", "phpstan-level-0"})
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
                    "phpstan-level-0",
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
            "docs/refactoring/bookkeeping.md": "# Refactoring Loop Config\n",
            ".github/workflows/ci.yml": "jobs:\n  lint:\n    steps:\n      - run: php -l\n",
            # ticket 01: decided (fulfilled), so php-cs-fixer's own recommended
            # gate doesn't interfere with what this test actually exercises.
            ".editorconfig": "root = true\n\n[*]\ncharset = utf-8\n",
        })
        try:
            nodes = [c["node"] for c in next_candidates(root)]
            self.assertNotIn("composer-audit", nodes)
            self.assertNotIn("phpstan-level-0", nodes)
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
            "docs/refactoring/bookkeeping.md": "# Refactoring Loop Config\n",
            ".github/workflows/ci.yml": "jobs:\n  lint:\n    steps:\n      - run: php -l\n",
        })
        try:
            r = roadmap(root, steps=10)
            nodes = [x["node"] for x in r]
            self.assertNotIn("composer-audit", nodes)
            self.assertNotIn("phpstan-level-0", nodes)
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
            self.assertEqual(blocked, {"composer-audit", "phpstan-level-0"})
        finally:
            tmp.cleanup()


class PhpMinimalVersionTests(unittest.TestCase):
    """Ticket 57: `php-minimal-version` proposes only a Floor correction
    (CONTEXT.md) -- composer.json's declared PHP floor brought in line with
    the PHP-version level `rector-php-set` has itself applied, never a Floor
    raise ahead of the code actually needing it. Required parent:
    rector-php-set (reversed from ticket 35's original design, where
    php-minimal-version was rector-php-set's own recommended parent
    instead)."""

    def _make_repo(self, files: dict):
        tmp = tempfile.TemporaryDirectory()
        root = pathlib.Path(tmp.name)
        for rel, content in files.items():
            p = root / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content)
        (root / ".git").mkdir()
        return tmp, root

    _RECTOR_PHP_UP_TO_82 = (
        "<?php\n"
        "use Rector\\Set\\ValueObject\\LevelSetList;\n"
        "return static function ($rectorConfig) {\n"
        "    $rectorConfig->sets([LevelSetList::UP_TO_PHP_82]);\n"
        "};\n"
    )
    _RECTOR_PHP_UP_TO_74 = (
        "<?php\n"
        "use Rector\\Set\\ValueObject\\LevelSetList;\n"
        "return static function ($rectorConfig) {\n"
        "    $rectorConfig->sets([LevelSetList::UP_TO_PHP_74]);\n"
        "};\n"
    )

    def test_fulfilled_when_no_composer_json(self):
        # Undeterminable floor -- same convention php_floor_precheck() uses:
        # unknown floor never blocks/recommends anything.
        tmp, root = self._make_repo({"rector.php": self._RECTOR_PHP_UP_TO_82})
        try:
            d = detect_nodes(root)
            self.assertTrue(d["php-minimal-version"]["fulfilled"], d["php-minimal-version"])
        finally:
            tmp.cleanup()

    def test_fulfilled_when_no_rector_php_set_level_applied_yet(self):
        # Nothing for rector-php-set to have landed -- nothing to correct,
        # vacuously fulfilled, same convention "floor undeterminable" uses.
        tmp, root = self._make_repo({
            "composer.json": json.dumps({"require": {"php": ">=7.4"}}),
            "composer.lock": "{}",
        })
        try:
            d = detect_nodes(root)
            self.assertTrue(d["php-minimal-version"]["fulfilled"], d["php-minimal-version"])
        finally:
            tmp.cleanup()

    def test_fulfilled_when_floor_already_matches_applied_level(self):
        tmp, root = self._make_repo({
            "composer.json": json.dumps({"require": {"php": ">=8.2"}}),
            "composer.lock": "{}",
            "rector.php": self._RECTOR_PHP_UP_TO_82,
        })
        try:
            d = detect_nodes(root)
            self.assertTrue(d["php-minimal-version"]["fulfilled"], d["php-minimal-version"])
            self.assertEqual(d["php-minimal-version"]["details"]["rector_level"], [8, 2])
        finally:
            tmp.cleanup()

    def test_not_fulfilled_when_floor_behind_applied_level(self):
        tmp, root = self._make_repo({
            "composer.json": json.dumps({"require": {"php": ">=7.4"}}),
            "composer.lock": "{}",
            "rector.php": self._RECTOR_PHP_UP_TO_82,
        })
        try:
            d = detect_nodes(root)
            self.assertFalse(d["php-minimal-version"]["fulfilled"], d["php-minimal-version"])
            self.assertEqual(d["php-minimal-version"]["details"]["rector_level"], [8, 2])
            self.assertEqual(d["php-minimal-version"]["details"]["floor"], [7, 4])
        finally:
            tmp.cleanup()

    def test_a_require_dev_tools_own_php_floor_never_creates_a_gap(self):
        # The Composer-semantics finding this redesign is built on: a
        # require-dev tool's own PHP-version requirement (here phpstan,
        # tested under a newer PHP image in CI) is never a legitimate
        # signal for this node -- only rector-php-set's own applied level
        # is, and no rector.php exists in this fixture at all.
        tmp, root = self._make_repo({
            "composer.json": json.dumps({"require": {"php": ">=7.4"}, "require-dev": {"phpstan/phpstan": "^1.10"}}),
            "composer.lock": "{}",
            ".github/workflows/ci.yml": (
                "jobs:\n  quality:\n    steps:\n      - run: vendor/bin/phpstan analyse\n"
            ),
        })
        try:
            d = detect_nodes(root)
            self.assertTrue(d["php-minimal-version"]["fulfilled"], d["php-minimal-version"])
        finally:
            tmp.cleanup()

    def test_not_proposable_while_rector_php_set_unfulfilled(self):
        # rector-php-set is the sole required parent -- no rector.php at
        # all means rector-php-set itself is unfulfilled, so
        # php-minimal-version can't be proposed regardless of any gap.
        tmp, root = self._make_repo({
            "composer.json": json.dumps({"require": {"php": ">=5.6"}}),
            "composer.lock": "{}",
            "docs/refactoring/bookkeeping.md": "# Refactoring Loop Config\n",
        })
        try:
            nodes = [c["node"] for c in next_candidates(root)]
            self.assertNotIn("php-minimal-version", nodes)
        finally:
            tmp.cleanup()

    def test_proposable_once_rector_php_set_fulfilled(self):
        tmp, root = self._make_repo({
            "composer.json": json.dumps({"require": {"php": ">=7.4"}}),
            "composer.lock": "{}",
            "docs/refactoring/bookkeeping.md": "# Refactoring Loop Config\n",
            "rector.php": self._RECTOR_PHP_UP_TO_82,
        })
        try:
            nodes = [c["node"] for c in next_candidates(root)]
            self.assertIn("php-minimal-version", nodes)
        finally:
            tmp.cleanup()

    def test_permanently_unproposable_once_rector_php_set_rejected(self):
        # required-parent rejection closes everything beneath it -- the
        # tree's ordinary convention, no special-casing needed here. A real
        # gap (floor 5.6, far below any plausible rector level) would have
        # made this proposable under the old design; not any more.
        tmp, root = self._make_repo({
            "composer.json": json.dumps({"require": {"php": ">=5.6"}}),
            "composer.lock": "{}",
            "docs/refactoring/bookkeeping.md": "# Refactoring Loop Config\n",
            "docs/refactoring/out-of-scope/rector-php-set.md": "rejected\n",
        })
        try:
            nodes = [c["node"] for c in next_candidates(root)]
            self.assertNotIn("php-minimal-version", nodes)
        finally:
            tmp.cleanup()

    def test_can_flip_back_to_unfulfilled_as_the_moving_target_changes(self):
        # Re-triggering property: no persisted state, no special mechanism —
        # detect_nodes() is re-derived fresh each call. A floor that
        # satisfied yesterday's applied level stops satisfying it once
        # rector-php-set re-levels upward in a later pass (its own MR
        # scope: "adopted in levels, one MR per target PHP version bump").
        tmp, root = self._make_repo({
            "composer.json": json.dumps({"require": {"php": ">=7.4"}}),
            "composer.lock": "{}",
            "rector.php": self._RECTOR_PHP_UP_TO_74,
        })
        try:
            self.assertTrue(detect_nodes(root)["php-minimal-version"]["fulfilled"])
            (root / "rector.php").write_text(self._RECTOR_PHP_UP_TO_82)
            # 7.4 still >= 8.2? No -- now stale: a later pass re-leveled up.
            self.assertFalse(detect_nodes(root)["php-minimal-version"]["fulfilled"])
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
        # ADR-0008: with no docs/refactoring/bookkeeping.md, loop-config is the
        # first proposable node — required parent of ci-runner/editorconfig,
        # and (via is-php-project, ADR-0022) composer.
        # ADR-0022: composer now requires is-php-project as well as
        # loop-config — a bare `.git` repo with no PHP signal never fulfils
        # it, so a minimal `index.php` is added here to keep testing the
        # composer cascade; IsPhpProjectTests covers the genuinely-no-PHP
        # case (composer never reachable at all) separately.
        tmp, root = self._make_repo({"index.php": "<?php\n"})
        try:
            r = roadmap(root, steps=7)
            self.assertEqual(r[0]["node"], "loop-config")
            # ADR-0022: is-php-project sits between loop-config and
            # ci-runner/editorconfig in tree["order"] but is never proposed
            # (_NEVER_PROPOSED) — it never appears in roadmap output itself.
            self.assertNotIn("is-php-project", [step["node"] for step in r])
            # ci-runner now sorts ahead of editorconfig — both trivial
            # generic-root nodes, tooling-tree.md's edge table lists
            # ci-runner's row first. secret-detection (signals ticket 2)
            # sorts after editorconfig, same reason (its own edge table row
            # comes last among loop-config's direct required children).
            self.assertEqual(r[1]["node"], "ci-runner")
            self.assertEqual(r[2]["node"], "editorconfig")
            self.assertEqual(r[3]["node"], "secret-detection")
            self.assertEqual(r[4]["node"], "composer")
            self.assertIn(r[5]["node"], ["composer-audit", "php-cs-fixer", "phpunit", "psr-4"])
        finally:
            tmp.cleanup()

    def test_roadmap_with_loop_config_starts_with_composer(self):
        # With docs/refactoring/bookkeeping.md already present, loop-config is
        # fulfilled and the roadmap picks up where it used to before ADR-0008
        # — plus ci-runner/editorconfig/secret-detection (ticket 01, signals
        # ticket 2), ordered ahead of composer for the same reason as above.
        # Needs a PHP signal too, same as above (ADR-0022).
        tmp, root = self._make_repo({
            "docs/refactoring/bookkeeping.md": "# Refactoring Loop Config\n\n**Cadence:** weekly\n",
            "index.php": "<?php\n",
        })
        try:
            r = roadmap(root, steps=6)
            self.assertNotIn("is-php-project", [step["node"] for step in r])
            self.assertEqual(r[0]["node"], "ci-runner")
            self.assertEqual(r[1]["node"], "editorconfig")
            self.assertEqual(r[2]["node"], "secret-detection")
            self.assertEqual(r[3]["node"], "composer")
            self.assertIn(r[4]["node"], ["composer-audit", "php-cs-fixer", "phpunit", "psr-4"])
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
            self.assertIn("phpstan-level-0", nodes)
            # composer-audit stays blocked here: no ci-runner (required parent)
            # and no real `require` dependency (only the `php` platform
            # pseudo-package) — see ComposerAuditGateTests for its own gating.
            self.assertNotIn("composer-audit", nodes)
            # p0 within 10 (needs composer)
            self.assertIn("phpstan-level-0", nodes)
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
            # ticket 43: the level chain alone (1..10) now spans 10 nodes, so
            # a 10-step lookahead no longer reaches rector-dead-code at all —
            # widen the lookahead rather than shrink what's under test.
            r = roadmap(root, steps=25)
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

    def test_structural_scan_proposed_once_gate_open_ticket_39(self):
        # Ticket 39: once every php-structural-scan leaf is resolved
        # (fulfilled or rejected), roadmap()'s simulation loop used to skip
        # structural-scan forever (its resolved-gate branch sat *after* the
        # generic sim_fulfilled skip, so a node marked "fulfilled" the
        # instant its gate opened was never reached again) and fell through
        # to a meaningless phpstan-level-N "open chain" filler instead, every
        # step, for the whole lookahead. Reusing
        # StructuralScanGateTests._fully_tooled_files's fixture shape (every
        # leaf fulfilled by file inspection, no rejections needed) — same
        # fixture that already proves detect_nodes() marks structural-scan
        # fulfilled; roadmap() must now agree it stays proposable.
        tmp, root = self._make_repo({
            "docs/refactoring/bookkeeping.md": "# Refactoring Loop Config\n\n**Cadence:** weekly\n",
            "composer.json": json.dumps({
                "require-dev": {
                    "phpstan/phpstan": "^1.0",
                    "phpstan/phpstan-deprecation-rules": "^1.0",
                    "phpunit/phpunit": "^10.0",
                    "friendsofphp/php-cs-fixer": "^3.0",
                },
                "require": {
                    "some/real-dep": "^1.0",
                },
                "autoload": {"psr-4": {"App\\": "src/"}},
            }),
            "composer.lock": "{}",
            "src/Example.php": "<?php\n\nnamespace App;\n\nclass Example\n{\n}\n",
            ".php-cs-fixer.php": "<?php return [];",
            "phpstan.neon": "parameters:\n    level: 5\n",
            "phpstan-baseline.neon": "parameters:\n    ignoreErrors: []\n",
            "rector.php": "<?php // DeadCode Type LevelSetList CodeQuality PHPUnitSetList",
            ".editorconfig": "root = true\n\n[*]\ncharset = utf-8\n",
            ".github/workflows/ci.yml": (
                "jobs:\n"
                "  audit:\n"
                "    steps:\n"
                "      - run: composer audit\n"
                "      - run: vendor/bin/phpunit\n"
                "      - run: vendor/bin/phpstan analyse\n"
                "      - run: gitleaks detect\n"
            ),
            "docs/refactoring/out-of-scope/psalm-taint-analysis.md": "rejected: no taint analysis adopted\n",
        })
        try:
            r = roadmap(root, steps=1)
            self.assertEqual(r[0]["node"], "structural-scan")
            # And it stays the answer every step, not just the first —
            # exactly the "ongoing candidate" shape next_candidates() already
            # gives an exposed resolved-gate node.
            r10 = roadmap(root, steps=10)
            self.assertTrue(all(x["node"] == "structural-scan" for x in r10))
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


class DirectlyUnblockedChildrenTests(unittest.TestCase):
    """The MR outlook's fan-out diagram data (opening-a-merge-request.md,
    ticket 47/ADR-0027): every node landed_node's fulfilment newly makes
    proposable, not next_candidates()'s full current set."""

    def _make_repo(self, files: dict):
        tmp = tempfile.TemporaryDirectory()
        root = pathlib.Path(tmp.name)
        for rel, content in files.items():
            p = root / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content)
        (root / ".git").mkdir()
        return tmp, root

    def test_multi_child_fan_out_from_composer(self):
        # composer alone (no phpunit/cs-fixer/phpmd/CI configured yet)
        # unblocks five siblings at once: phpunit, test-runner-if-missing,
        # phpmd, and psr-4 directly, phpstan-level-0 through the
        # static-code-analyzer walk-through (a pure organizational node,
        # never itself reported).
        tmp, root = self._make_repo({
            "composer.json": json.dumps({"require": {"php": ">=8.1"}}),
            "composer.lock": "{}",
        })
        try:
            got = {(c["node"], c["type"]) for c in directly_unblocked_children(root, "composer")}
            self.assertEqual(
                got,
                {
                    ("phpunit", "required"),
                    ("test-runner-if-missing", "required"),
                    ("phpmd", "required"),
                    ("phpstan-level-0", "required"),
                    ("psr-4", "required"),
                },
            )
            self.assertNotIn("static-code-analyzer", {c["node"] for c in directly_unblocked_children(root, "composer")})
        finally:
            tmp.cleanup()

    def test_required_any_child_reported_when_only_path(self):
        # Psalm-only target, no real PHPStan config: landing psalm is the
        # *only* thing that unblocks rector-php-set (required-any(
        # phpstan-level-0, psalm)) -- must be reported. php-cs-fixer (a
        # recommended parent since signals ticket 2) is decided (rejected)
        # here so it isn't also withholding rector-php-set -- this test is
        # about the required-any path specifically, not the recommended one.
        tmp, root = self._make_repo({
            "composer.json": json.dumps({"require": {"php": ">=8.1", "vimeo/psalm": "^5.0"}}),
            "composer.lock": "{}",
            "psalm.xml": "<psalm></psalm>",
            "docs/refactoring/out-of-scope/php-cs-fixer.md": "rejected\n",
        })
        try:
            got = [(c["node"], c["type"]) for c in directly_unblocked_children(root, "psalm")]
            self.assertIn(("rector-php-set", "required-any"), got)
        finally:
            tmp.cleanup()

    def test_required_any_child_excluded_when_already_reachable_via_sibling(self):
        # psalm already fulfilled independently -- landing phpstan-level-4
        # does NOT newly unblock psalm-taint-analysis (required-any(
        # phpstan-level-4, psalm)): psalm already covered it.
        tmp, root = self._make_repo({
            "composer.json": json.dumps({"require": {"php": ">=8.1", "vimeo/psalm": "^5.0"}}),
            "composer.lock": "{}",
            "psalm.xml": "<psalm></psalm>",
        })
        try:
            got = {c["node"] for c in directly_unblocked_children(root, "phpstan-level-4")}
            self.assertNotIn("psalm-taint-analysis", got)
        finally:
            tmp.cleanup()

    def test_resolved_gate_walk_through_to_structural_scan(self):
        # phpunit is the last of php-structural-scan's eleven leaves (signals
        # ticket 2 dropped test-runner-if-missing and php-cs-fixer, lowered
        # the level-chain leaf to phpstan-level-5) to resolve (the other ten
        # rejected via out-of-scope, same for structural-scan's other two
        # resolved-parents, editorconfig and ci-runner) -- landing it must
        # report structural-scan itself, not the never-exposed
        # php-structural-scan aggregation node in between.
        other_leaves = [
            "psr-4", "composer-audit", "phpstan-level-5",
            "phpstan-deprecation-rules", "rector-dead-code", "rector-type-coverage",
            "rector-php-set", "rector-code-quality", "rector-phpunit-set",
            "psalm-taint-analysis", "editorconfig", "ci-runner",
            # coverage-floor (ticket 08): also a direct required child of
            # phpunit now, same as rector-phpunit-set above -- rejected here
            # too so landing phpunit reports only the resolved-gate
            # walk-through this test is actually about, not an unrelated
            # newly-unblocked Signal node.
            "coverage-floor",
        ]
        files = {
            "composer.json": json.dumps({"require-dev": {"phpunit/phpunit": "^10.0"}}),
            "composer.lock": "{}",
        }
        for leaf in other_leaves:
            files[f"docs/refactoring/out-of-scope/{leaf}.md"] = "rejected\n"
        tmp, root = self._make_repo(files)
        try:
            got = [(c["node"], c["type"]) for c in directly_unblocked_children(root, "phpunit")]
            self.assertEqual(got, [("structural-scan", "resolved")])
        finally:
            tmp.cleanup()

    def test_unknown_landed_node_returns_empty(self):
        tmp, root = self._make_repo({})
        try:
            self.assertEqual(directly_unblocked_children(root, "not-a-real-node"), [])
        finally:
            tmp.cleanup()

    def test_no_children_when_nothing_new(self):
        # Empty repo: loop-config isn't fulfilled, so forcing it "unfulfilled"
        # in the counterfactual changes nothing real -- no children to report.
        tmp, root = self._make_repo({})
        try:
            self.assertEqual(directly_unblocked_children(root, "loop-config"), [])
        finally:
            tmp.cleanup()


class CoverageFloorNodeTests(unittest.TestCase):
    """Ticket 08: `coverage-floor`, a PHPUnit child, Signal-producing node
    (no `resolved` edge anywhere). Driver-agnostic by design (PCOV vs.
    Xdebug is a review-time MR-scope choice, never checked here) -- only
    "coverage configured, floor committed, CI-gated once CI exists"
    matters."""

    def _make_repo(self, files: dict):
        tmp = tempfile.TemporaryDirectory()
        root = pathlib.Path(tmp.name)
        for rel, content in files.items():
            p = root / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content)
        (root / ".git").mkdir()
        return tmp, root

    def _base_files(self):
        return {
            "docs/refactoring/bookkeeping.md": "# Refactoring Loop Config\n\n**Cadence:** weekly\n",
            "composer.json": json.dumps({"require-dev": {"phpunit/phpunit": "^10.0"}}),
            "composer.lock": "{}",
        }

    def test_edge_is_required_from_phpunit(self):
        tree = load_tree()
        self.assertIn({"from": "phpunit", "to": "coverage-floor", "type": "required"}, tree["edges"])

    def test_no_resolved_edge_anywhere(self):
        tree = load_tree()
        self.assertNotIn(
            {"from": "coverage-floor", "to": "php-structural-scan", "type": "resolved"},
            tree["edges"],
        )
        self.assertFalse(any(e["from"] == "coverage-floor" and e["type"] == "resolved" for e in tree["edges"]))

    def test_neither_coverage_config_nor_floor_unfulfilled(self):
        tmp, root = self._make_repo(self._base_files())
        try:
            d = detect_nodes(root)
            self.assertFalse(d["coverage-floor"]["fulfilled"])
            self.assertFalse(d["coverage-floor"]["details"]["has_coverage_config"])
            self.assertIsNone(d["coverage-floor"]["details"]["floor"])
        finally:
            tmp.cleanup()

    def test_coverage_config_without_floor_file_unfulfilled(self):
        files = self._base_files()
        files["phpunit.xml.dist"] = "<phpunit><coverage><report><clover outputFile=\"c.xml\"/></report></coverage></phpunit>"
        tmp, root = self._make_repo(files)
        try:
            d = detect_nodes(root)
            self.assertFalse(d["coverage-floor"]["fulfilled"])
            self.assertTrue(d["coverage-floor"]["details"]["has_coverage_config"])
            self.assertIsNone(d["coverage-floor"]["details"]["floor"])
        finally:
            tmp.cleanup()

    def test_floor_file_without_coverage_config_unfulfilled(self):
        files = self._base_files()
        files[".coverage-floor"] = "62.5\n"
        tmp, root = self._make_repo(files)
        try:
            d = detect_nodes(root)
            self.assertFalse(d["coverage-floor"]["fulfilled"])
            self.assertFalse(d["coverage-floor"]["details"]["has_coverage_config"])
            self.assertEqual(d["coverage-floor"]["details"]["floor"], 62.5)
        finally:
            tmp.cleanup()

    def test_both_present_no_ci_fulfilled(self):
        # No CI yet still fulfils the node on local adoption alone -- same
        # convention every other self-wired CI-gate node already uses.
        files = self._base_files()
        files["phpunit.xml.dist"] = "<phpunit><coverage><report><clover outputFile=\"c.xml\"/></report></coverage></phpunit>"
        files[".coverage-floor"] = "62.5\n"
        tmp, root = self._make_repo(files)
        try:
            d = detect_nodes(root)
            self.assertTrue(d["coverage-floor"]["fulfilled"])
        finally:
            tmp.cleanup()

    def test_ci_exists_but_not_coverage_gated_unfulfilled(self):
        files = self._base_files()
        files["phpunit.xml.dist"] = "<phpunit><coverage><report><clover outputFile=\"c.xml\"/></report></coverage></phpunit>"
        files[".coverage-floor"] = "62.5\n"
        files[".github/workflows/ci.yml"] = "jobs:\n  test:\n    steps:\n      - run: vendor/bin/phpunit\n"
        tmp, root = self._make_repo(files)
        try:
            d = detect_nodes(root)
            self.assertFalse(d["coverage-floor"]["fulfilled"])
            self.assertIn("not gated in CI", d["coverage-floor"]["reason"])
        finally:
            tmp.cleanup()

    def test_ci_coverage_gated_fulfilled(self):
        files = self._base_files()
        files["phpunit.xml.dist"] = "<phpunit><coverage><report><clover outputFile=\"c.xml\"/></report></coverage></phpunit>"
        files[".coverage-floor"] = "62.5\n"
        files[".github/workflows/ci.yml"] = "jobs:\n  test:\n    steps:\n      - run: vendor/bin/phpunit --coverage-text\n"
        tmp, root = self._make_repo(files)
        try:
            d = detect_nodes(root)
            self.assertTrue(d["coverage-floor"]["fulfilled"])
        finally:
            tmp.cleanup()

    def test_unparseable_floor_file_treated_as_absent(self):
        files = self._base_files()
        files["phpunit.xml.dist"] = "<phpunit><coverage><report><clover outputFile=\"c.xml\"/></report></coverage></phpunit>"
        files[".coverage-floor"] = "not-a-number\n"
        tmp, root = self._make_repo(files)
        try:
            d = detect_nodes(root)
            self.assertFalse(d["coverage-floor"]["fulfilled"])
            self.assertIsNone(d["coverage-floor"]["details"]["floor"])
        finally:
            tmp.cleanup()

    def test_driver_agnostic_xdebug_still_fulfils(self):
        # The fulfilment check never inspects which driver actually ran --
        # an Xdebug-based CI invocation fulfils the node exactly the same
        # way a PCOV-based one would (php-tooling-tree/coverage-floor.md's
        # own "PCOV is a default, not a requirement").
        files = self._base_files()
        files["phpunit.xml.dist"] = "<phpunit><coverage><report><clover outputFile=\"c.xml\"/></report></coverage></phpunit>"
        files[".coverage-floor"] = "62.5\n"
        files[".github/workflows/ci.yml"] = (
            "jobs:\n  test:\n    steps:\n      - run: XDEBUG_MODE=coverage vendor/bin/phpunit --coverage-text\n"
        )
        tmp, root = self._make_repo(files)
        try:
            d = detect_nodes(root)
            self.assertTrue(d["coverage-floor"]["fulfilled"])
        finally:
            tmp.cleanup()


class SecretHistoryScanDetectionTests(unittest.TestCase):
    """Ticket 13's remaining half: `secret-detection`'s own `details.scanner`
    names which recognized scanner the CI config actually invokes, so
    `refactor-scan/SKILL.md` step 4c's one-time git-history scan can reuse it
    without re-reading the CI config itself."""

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
            "docs/refactoring/bookkeeping.md": "# Refactoring Loop Config\n\n**Cadence:** weekly\n",
            "composer.json": json.dumps({"name": "test/app", "require": {"php": "^8.1"}}),
            "composer.lock": "{}",
        }

    def test_no_ci_job_scanner_is_none(self):
        tmp, root = self._make_repo(self._loop_config_and_composer_files())
        try:
            d = detect_nodes(root)
            self.assertFalse(d["secret-detection"]["fulfilled"])
            self.assertIsNone(d["secret-detection"]["details"]["scanner"])
        finally:
            tmp.cleanup()

    def test_gitleaks_ci_job_names_gitleaks(self):
        files = self._loop_config_and_composer_files()
        files[".github/workflows/ci.yml"] = (
            "jobs:\n  scan:\n    steps:\n      - run: gitleaks detect\n"
        )
        tmp, root = self._make_repo(files)
        try:
            d = detect_nodes(root)
            self.assertTrue(d["secret-detection"]["fulfilled"])
            self.assertEqual(d["secret-detection"]["details"]["scanner"], "gitleaks")
        finally:
            tmp.cleanup()

    def test_detect_secrets_ci_job_names_detect_secrets(self):
        files = self._loop_config_and_composer_files()
        files[".github/workflows/ci.yml"] = (
            "jobs:\n  scan:\n    steps:\n      - run: detect-secrets scan\n"
        )
        tmp, root = self._make_repo(files)
        try:
            d = detect_nodes(root)
            self.assertTrue(d["secret-detection"]["fulfilled"])
            self.assertEqual(d["secret-detection"]["details"]["scanner"], "detect-secrets")
        finally:
            tmp.cleanup()

    def test_trufflehog_ci_job_names_trufflehog(self):
        files = self._loop_config_and_composer_files()
        files[".github/workflows/ci.yml"] = (
            "jobs:\n  scan:\n    steps:\n      - run: trufflehog filesystem .\n"
        )
        tmp, root = self._make_repo(files)
        try:
            d = detect_nodes(root)
            self.assertTrue(d["secret-detection"]["fulfilled"])
            self.assertEqual(d["secret-detection"]["details"]["scanner"], "trufflehog")
        finally:
            tmp.cleanup()

    def test_unrecognized_scanner_not_fulfilled_scanner_none(self):
        # A CI job exists but doesn't invoke any of the three recognized
        # needles -- secret-detection stays unfulfilled, and there's no
        # scanner name to report (nothing for step 4c to reuse).
        files = self._loop_config_and_composer_files()
        files[".github/workflows/ci.yml"] = (
            "jobs:\n  scan:\n    steps:\n      - run: some-other-scanner scan\n"
        )
        tmp, root = self._make_repo(files)
        try:
            d = detect_nodes(root)
            self.assertFalse(d["secret-detection"]["fulfilled"])
            self.assertIsNone(d["secret-detection"]["details"]["scanner"])
        finally:
            tmp.cleanup()


class SemgrepNodeTests(unittest.TestCase):
    """Ticket 11: `semgrep`, OWASP Top 10 coverage. Signal-producing (no
    `resolved` edge anywhere), recommended parent `psalm-taint-analysis`
    (not the flat `composer`-level required edge `phpmd` uses) so Psalm's
    own taint baseline settles first."""

    def _make_repo(self, files: dict):
        tmp = tempfile.TemporaryDirectory()
        root = pathlib.Path(tmp.name)
        for rel, content in files.items():
            p = root / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content)
        (root / ".git").mkdir()
        return tmp, root

    def _base_files(self):
        return {
            "docs/refactoring/bookkeeping.md": "# Refactoring Loop Config\n\n**Cadence:** weekly\n",
            "composer.json": json.dumps({"name": "test/app", "require": {"php": "^8.1"}}),
            "composer.lock": "{}",
        }

    def test_edge_is_recommended_from_psalm_taint_analysis(self):
        tree = load_tree()
        self.assertIn(
            {"from": "psalm-taint-analysis", "to": "semgrep", "type": "recommended"},
            tree["edges"],
        )

    def test_no_resolved_edge_anywhere(self):
        tree = load_tree()
        self.assertFalse(any(e["from"] == "semgrep" and e["type"] == "resolved" for e in tree["edges"]))

    def test_no_ci_job_unfulfilled(self):
        tmp, root = self._make_repo(self._base_files())
        try:
            d = detect_nodes(root)
            self.assertFalse(d["semgrep"]["fulfilled"])
        finally:
            tmp.cleanup()

    def test_semgrep_without_owasp_unfulfilled(self):
        files = self._base_files()
        files[".github/workflows/ci.yml"] = "jobs:\n  scan:\n    steps:\n      - run: semgrep --config=auto\n"
        tmp, root = self._make_repo(files)
        try:
            d = detect_nodes(root)
            self.assertFalse(d["semgrep"]["fulfilled"])
        finally:
            tmp.cleanup()

    def test_owasp_mentioned_without_semgrep_unfulfilled(self):
        # An OWASP mention alone (e.g. a comment, a different tool) isn't
        # this node's own evidence -- semgrep itself must actually run.
        files = self._base_files()
        files[".github/workflows/ci.yml"] = "jobs:\n  scan:\n    steps:\n      - run: echo owasp reminder\n"
        tmp, root = self._make_repo(files)
        try:
            d = detect_nodes(root)
            self.assertFalse(d["semgrep"]["fulfilled"])
        finally:
            tmp.cleanup()

    def test_semgrep_with_inline_owasp_config_fulfilled(self):
        files = self._base_files()
        files[".github/workflows/ci.yml"] = (
            "jobs:\n  scan:\n    steps:\n      - run: semgrep --config=p/owasp-top-ten\n"
        )
        tmp, root = self._make_repo(files)
        try:
            d = detect_nodes(root)
            self.assertTrue(d["semgrep"]["fulfilled"])
        finally:
            tmp.cleanup()

    def test_semgrep_ci_plus_owasp_in_committed_config_fulfilled(self):
        files = self._base_files()
        files[".github/workflows/ci.yml"] = "jobs:\n  scan:\n    steps:\n      - run: semgrep ci\n"
        files[".semgrep.yml"] = "rules:\n  - id: owasp-top-ten-imported\n"
        tmp, root = self._make_repo(files)
        try:
            d = detect_nodes(root)
            self.assertTrue(d["semgrep"]["fulfilled"])
        finally:
            tmp.cleanup()


if __name__ == "__main__":
    unittest.main()
