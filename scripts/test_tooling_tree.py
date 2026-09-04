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
        # bug (a Psalm-only target never resolving `phpstan-level-10`) is
        # already fixed by that node's own mutual-exclusion rejection
        # housekeeping, without needing `psalm` to be a leaf too. Ticket 48
        # later dropped `rector-early-return` itself (its rule set shipped
        # permanently empty upstream, folded into `rector-code-quality`) —
        # back down to twelve. Ticket 50 added `psr-4` as a new thirteenth
        # leaf — gating on a different basis than every other leaf here (a
        # code-organization convention, not a checking tool).
        tree = load_tree()
        self.assertEqual(
            set(tree["resolved_parents"]["php-structural-scan"]),
            {
                "psr-4",
                "composer-audit",
                "phpunit",
                "test-runner-if-missing",
                "php-cs-fixer",
                "phpstan-level-10",
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
        # ticket 35: php-minimal-version — two required parents (same shape
        # as composer-audit's ci-runner + composer), and a recommended
        # parent of rector-php-set (its PHP-version-targeted rule set
        # otherwise has no dependency on the runtime floor it rewrites to).
        # `loop-config` -> `is-php-project` (ADR-0022) replaced the direct
        # `loop-config` parent once the PHP tree's recognition gate landed.
        tree = load_tree()
        self.assertEqual(
            set(tree["required_parents"]["php-minimal-version"]),
            {"is-php-project", "ci-runner"},
        )
        self.assertIn("php-minimal-version", tree["recommended_parents"]["rector-php-set"])
        # Deliberately NOT one of php-structural-scan's resolved-parent
        # leaves — not decided during ticket 35's grilling session, so not
        # added here.
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
            # ticket 43: level chain now reaches phpstan-level-10 (was 3) —
            # a "fully tooled" fixture must reach the new top to resolve
            # php-structural-scan by fulfilment alone.
            "phpstan.neon": "parameters:\n    level: 10\n",
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
            # ticket 43: level chain now reaches phpstan-level-10 (was 3).
            "phpstan.neon": "parameters:\n    level: 10\n",
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


class PsalmMutualExclusionTests(unittest.TestCase):
    """Ticket 37: phpstan-level-10 is the php-structural-scan leaf a target's
    static-analyzer choice must resolve — the actual bug this ticket fixes (a
    Psalm-only target previously left phpstan-level-10 neither fulfilled nor
    rejected, permanently blocking php-structural-scan). `psalm` itself is
    deliberately not a leaf (found redundant on review, see
    test_resolved_parents_of_php_structural_scan) — only phpstan-level-10's
    own resolution matters here."""

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

    def test_psalm_leaf_fulfilled_but_phpstan_level_10_leaf_unresolved_without_housekeeping(self):
        # Reproduces the bug this ticket fixes: without the mutual-exclusion
        # out-of-scope write, phpstan-level-10 sits neither fulfilled (Psalm
        # path) nor rejected (nobody wrote the file) — php-structural-scan
        # stays blocked on it forever.
        tmp, root = self._make_repo(self._psalm_only_files())
        try:
            d = detect_nodes(root)
            self.assertTrue(d["psalm"]["fulfilled"])
            self.assertFalse(d["phpstan-level-10"]["fulfilled"])
            self.assertIn("phpstan-level-10", d["php-structural-scan"]["details"]["unresolved"])
        finally:
            tmp.cleanup()

    def test_phpstan_level_10_rejection_closes_the_gap(self):
        # The fix: the recognition-pass housekeeping described on the `psalm`
        # node's own entry (php-tooling-tree.md) writes
        # out-of-scope/phpstan-level-10.md — phpstan-level-10 then resolves
        # (rejected), and it's no longer in php-structural-scan's unresolved
        # list, exactly mirroring the real php-psalm fixture (ticket 37).
        files = self._psalm_only_files()
        files["docs/refactoring/out-of-scope/phpstan-level-10.md"] = "rejected: mutual exclusion (ticket 37) — psalm path chosen\n"
        tmp, root = self._make_repo(files)
        try:
            d = detect_nodes(root)
            self.assertNotIn("phpstan-level-10", d["php-structural-scan"]["details"]["unresolved"])
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
            "phpstan.neon": "parameters:\n    level: 10\n",
            "phpstan-baseline.neon": "parameters:\n    ignoreErrors: []\n",
        })
        try:
            d = detect_nodes(root)
            self.assertFalse(d["psalm"]["fulfilled"])
            self.assertTrue(d["phpstan-level-10"]["fulfilled"])
            self.assertNotIn("phpstan-level-10", d["php-structural-scan"]["details"]["unresolved"])
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
            # ticket 43: level chain now reaches phpstan-level-10 (was 3).
            "phpstan.neon": "parameters:\n    level: 10\n",
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
    of `composer`/`php-minimal-version` in `php-tooling-tree.md`. `_NEVER_PROPOSED`
    (like `git`), so it never appears in `next`/`roadmap`/`withheld` itself —
    only its gating effect on `composer`/`php-minimal-version` is visible
    there."""

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
    """Ticket 35: `php-minimal-version` recommends raising composer.json's
    declared PHP floor once it no longer covers what the tree actually
    needs — the minimum of any leaf `php_floor_precheck()` currently blocks,
    or the highest PHP version a quality-tooling CI job (phpstan/psalm/
    rector/php-cs-fixer) tests. Two required parents (loop-config,
    ci-runner); a recommended parent of rector-php-set."""

    def _make_repo(self, files: dict):
        tmp = tempfile.TemporaryDirectory()
        root = pathlib.Path(tmp.name)
        for rel, content in files.items():
            p = root / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content)
        (root / ".git").mkdir()
        return tmp, root

    _CI_YML_PHPSTAN_83 = (
        "jobs:\n"
        "  quality:\n"
        "    strategy:\n"
        "      matrix:\n"
        "        php-version: ['8.3']\n"
        "    steps:\n"
        "      - run: vendor/bin/phpstan analyse\n"
    )
    # A job testing multiple PHP versions, but only running phpunit — a
    # legitimate compatibility matrix, not evidence the runtime floor itself
    # needs to move (signal (b) must not fire on this).
    _CI_YML_COMPAT_MATRIX_PHPUNIT = (
        "jobs:\n"
        "  compat:\n"
        "    strategy:\n"
        "      matrix:\n"
        "        php-version: ['7.4', '8.0', '8.3']\n"
        "    steps:\n"
        "      - run: vendor/bin/phpunit\n"
    )

    def test_fulfilled_when_no_composer_json(self):
        # Undeterminable floor -- same convention php_floor_precheck() uses:
        # unknown floor never blocks/recommends anything.
        tmp, root = self._make_repo({})
        try:
            d = detect_nodes(root)
            self.assertTrue(d["php-minimal-version"]["fulfilled"], d["php-minimal-version"])
        finally:
            tmp.cleanup()

    def test_fulfilled_when_floor_already_covers_every_signal(self):
        tmp, root = self._make_repo({
            "composer.json": json.dumps({"require": {"php": ">=8.1"}}),
            "composer.lock": "{}",
        })
        try:
            d = detect_nodes(root)
            self.assertTrue(d["php-minimal-version"]["fulfilled"], d["php-minimal-version"])
        finally:
            tmp.cleanup()

    def test_not_fulfilled_when_floor_blocks_a_leaf(self):
        # Signal (a): php_floor_precheck() blocks composer-audit (PHP >=7.2)
        # and phpstan-level-0 (PHP >=7.0) at this floor -- gap is
        # the higher of the two, 7.2.
        tmp, root = self._make_repo({
            "composer.json": json.dumps({"require": {"php": ">=5.6"}}),
            "composer.lock": "{}",
        })
        try:
            d = detect_nodes(root)
            self.assertFalse(d["php-minimal-version"]["fulfilled"], d["php-minimal-version"])
            self.assertEqual(d["php-minimal-version"]["details"]["gap"], [7, 2])
        finally:
            tmp.cleanup()

    def test_quality_tooling_ci_job_php_version_creates_gap(self):
        # Signal (b): a quality-tooling job (phpstan) tests PHP 8.3, above
        # the declared floor -- gap fires even though no leaf is
        # floor-blocked at 7.4.
        tmp, root = self._make_repo({
            "composer.json": json.dumps({"require": {"php": ">=7.4"}}),
            "composer.lock": "{}",
            ".github/workflows/ci.yml": self._CI_YML_PHPSTAN_83,
        })
        try:
            d = detect_nodes(root)
            self.assertFalse(d["php-minimal-version"]["fulfilled"], d["php-minimal-version"])
            self.assertEqual(d["php-minimal-version"]["details"]["gap"], [8, 3])
        finally:
            tmp.cleanup()

    def test_compat_matrix_job_without_quality_tool_does_not_create_gap(self):
        # A job testing multiple PHP versions but only running phpunit (not
        # a quality tool) must not trigger the recommendation -- exactly the
        # distinction the grilling session drew.
        tmp, root = self._make_repo({
            "composer.json": json.dumps({"require": {"php": ">=7.4"}}),
            "composer.lock": "{}",
            ".github/workflows/ci.yml": self._CI_YML_COMPAT_MATRIX_PHPUNIT,
        })
        try:
            d = detect_nodes(root)
            self.assertTrue(d["php-minimal-version"]["fulfilled"], d["php-minimal-version"])
        finally:
            tmp.cleanup()

    def test_not_proposable_without_ci_runner_even_with_a_gap(self):
        # ci-runner is a required parent -- a real gap alone isn't enough.
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

    def test_proposable_once_loop_config_and_ci_runner_fulfilled(self):
        tmp, root = self._make_repo({
            "composer.json": json.dumps({"require": {"php": ">=5.6"}}),
            "composer.lock": "{}",
            "docs/refactoring/bookkeeping.md": "# Refactoring Loop Config\n",
            ".github/workflows/ci.yml": "jobs:\n  lint:\n    steps:\n      - run: php -l\n",
        })
        try:
            nodes = [c["node"] for c in next_candidates(root)]
            self.assertIn("php-minimal-version", nodes)
        finally:
            tmp.cleanup()

    def test_rector_php_set_withheld_while_undecided_then_released_on_rejection(self):
        # Same decided-gate shape as every other recommended edge
        # (RecommendedGateTests) -- php-minimal-version undecided (a real
        # gap, not yet rejected) withholds rector-php-set; rejecting
        # php-minimal-version releases it.
        files = {
            "composer.json": json.dumps({"require": {"php": ">=5.6"}, "require-dev": {"phpstan/phpstan": "^1.0"}}),
            "composer.lock": "{}",
            "docs/refactoring/bookkeeping.md": "# Refactoring Loop Config\n",
            # Invokes phpstan too, so phpstan-level-0 is genuinely
            # fulfilled (ticket 34's CI self-wiring) despite CI existing —
            # rector-php-set's required-any parent needs this, independent
            # of php-minimal-version's own gate under test here.
            ".github/workflows/ci.yml": "jobs:\n  analyse:\n    steps:\n      - run: vendor/bin/phpstan analyse\n",
            "phpstan.neon": "parameters:\n    level: 0\n",
            "phpstan-baseline.neon": "parameters:\n    ignoreErrors: []\n",
            # No rector.php -- rector-php-set itself stays unfulfilled, so it
            # can actually appear as a candidate once its gates release.
        }
        tmp, root = self._make_repo(files)
        try:
            nodes = [c["node"] for c in next_candidates(root)]
            self.assertNotIn("rector-php-set", nodes)
            (root / "docs" / "refactoring" / "out-of-scope").mkdir(parents=True, exist_ok=True)
            (root / "docs" / "refactoring" / "out-of-scope" / "php-minimal-version.md").write_text("rejected\n")
            nodes = [c["node"] for c in next_candidates(root)]
            self.assertIn("rector-php-set", nodes)
        finally:
            tmp.cleanup()

    def test_can_flip_back_to_unfulfilled_as_the_moving_target_changes(self):
        # Re-triggering property: no persisted state, no special mechanism —
        # detect_nodes() is re-derived fresh each call. A floor that
        # satisfied yesterday's requirement stops satisfying it once a new
        # quality-tooling CI job tests a higher version.
        base_files = {
            "composer.json": json.dumps({"require": {"php": ">=8.1"}}),
            "composer.lock": "{}",
        }
        tmp, root = self._make_repo(base_files)
        try:
            self.assertTrue(detect_nodes(root)["php-minimal-version"]["fulfilled"])
            (root / ".github" / "workflows").mkdir(parents=True, exist_ok=True)
            (root / ".github" / "workflows" / "ci.yml").write_text(self._CI_YML_PHPSTAN_83)
            # 8.1 still >= 8.3? No -- now stale: a later tool raised the bar.
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
            r = roadmap(root, steps=6)
            self.assertEqual(r[0]["node"], "loop-config")
            # ADR-0022: is-php-project sits between loop-config and
            # ci-runner/editorconfig in tree["order"] but is never proposed
            # (_NEVER_PROPOSED) — it never appears in roadmap output itself.
            self.assertNotIn("is-php-project", [step["node"] for step in r])
            # ci-runner now sorts ahead of editorconfig — both trivial
            # generic-root nodes, tooling-tree.md's edge table lists
            # ci-runner's row first.
            self.assertEqual(r[1]["node"], "ci-runner")
            self.assertEqual(r[2]["node"], "editorconfig")
            self.assertEqual(r[3]["node"], "composer")
            self.assertIn(r[4]["node"], ["composer-audit", "php-cs-fixer", "phpunit", "psr-4"])
        finally:
            tmp.cleanup()

    def test_roadmap_with_loop_config_starts_with_composer(self):
        # With docs/refactoring/bookkeeping.md already present, loop-config is
        # fulfilled and the roadmap picks up where it used to before ADR-0008
        # — plus ci-runner/editorconfig (ticket 01), ordered ahead of
        # composer for the same reason as above. Needs a PHP signal too,
        # same as above (ADR-0022).
        tmp, root = self._make_repo({
            "docs/refactoring/bookkeeping.md": "# Refactoring Loop Config\n\n**Cadence:** weekly\n",
            "index.php": "<?php\n",
        })
        try:
            r = roadmap(root, steps=5)
            self.assertNotIn("is-php-project", [step["node"] for step in r])
            self.assertEqual(r[0]["node"], "ci-runner")
            self.assertEqual(r[1]["node"], "editorconfig")
            self.assertEqual(r[2]["node"], "composer")
            self.assertIn(r[3]["node"], ["composer-audit", "php-cs-fixer", "phpunit", "psr-4"])
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
            "phpstan.neon": "parameters:\n    level: 10\n",
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
        # composer alone (no phpunit/cs-fixer/CI configured yet) unblocks
        # four siblings at once: phpunit, test-runner-if-missing, and
        # psr-4 directly, phpstan-level-0 through the static-code-analyzer
        # walk-through (a pure organizational node, never itself reported).
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
        # phpstan-level-0, psalm)) -- must be reported.
        tmp, root = self._make_repo({
            "composer.json": json.dumps({"require": {"php": ">=8.1", "vimeo/psalm": "^5.0"}}),
            "composer.lock": "{}",
            "psalm.xml": "<psalm></psalm>",
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
        # phpunit is the last of php-structural-scan's thirteen leaves to
        # resolve (the other twelve rejected via out-of-scope, same for
        # structural-scan's other two resolved-parents, editorconfig and
        # ci-runner) -- landing it must report structural-scan itself, not
        # the never-exposed php-structural-scan aggregation node in between.
        other_leaves = [
            "psr-4", "composer-audit", "test-runner-if-missing", "php-cs-fixer", "phpstan-level-10",
            "phpstan-deprecation-rules", "rector-dead-code", "rector-type-coverage",
            "rector-php-set", "rector-code-quality", "rector-phpunit-set",
            "psalm-taint-analysis", "editorconfig", "ci-runner",
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


if __name__ == "__main__":
    unittest.main()
