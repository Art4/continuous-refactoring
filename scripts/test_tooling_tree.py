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
next_candidates = tooling_tree.next_candidates
withheld_candidates = tooling_tree.withheld_candidates
directly_unblocked_children = tooling_tree.directly_unblocked_children
php_version_reversal_findings = tooling_tree.php_version_reversal_findings
php_floor_precheck = tooling_tree.php_floor_precheck
_resolve_refactoring_notes_dir = tooling_tree._resolve_refactoring_notes_dir
_rejected_nodes = tooling_tree._rejected_nodes
closed_by_rejection = tooling_tree.closed_by_rejection
withheld_with_reasons = tooling_tree.withheld_with_reasons
ordered_backlog = tooling_tree.ordered_backlog
_load_fulfilled_seed = tooling_tree._load_fulfilled_seed
_derive_fulfilled_from_bookkeeping = tooling_tree._derive_fulfilled_from_bookkeeping


class LoadTreeTests(unittest.TestCase):
    def test_edges_parsed(self):
        tree = load_tree()
        self.assertGreaterEqual(len(tree["edges"]), 15)
        # generic root (ADR-0008): git -> onboarding-setup, onboarding-setup -> is-php-project
        # (the PHP specialization's recognition gate, ADR-0022) -> the PHP tree roots.
        self.assertIn({"from": "git", "to": "onboarding-setup", "type": "required"}, tree["edges"])
        self.assertIn({"from": "onboarding-setup", "to": "is-php-project", "type": "required"}, tree["edges"])
        self.assertIn({"from": "is-php-project", "to": "composer", "type": "required"}, tree["edges"])
        # check required edge
        self.assertIn({"from": "phpstan-level-0", "to": "phpstan-level-1", "type": "required"}, tree["edges"])
        # recommended
        self.assertIn({"from": "php-cs-fixer", "to": "rector-dead-code", "type": "recommended"}, tree["edges"])
        # resolved (ADR-0008, ticket 42): PHP-tree leaves gate their own
        # aggregation node, php-safety-net (renamed from php-structural-scan,
        # ticket 63), which itself gates structural-scan via one resolved
        # edge.
        self.assertIn({"from": "php-safety-net", "to": "structural-scan", "type": "resolved"}, tree["edges"])
        # ticket 63: composer-audit moved out of the Safety Net (Signal wave
        # instead) — no longer a resolved leaf, gains php-safety-net as an
        # *additional* required parent alongside its existing ones, and
        # ci-runner is downgraded from required to recommended (the
        # Housekeeping-line fulfilment fallback covers the no-CI case).
        self.assertNotIn({"from": "composer-audit", "to": "php-safety-net", "type": "resolved"}, tree["edges"])
        self.assertIn({"from": "php-safety-net", "to": "composer-audit", "type": "required"}, tree["edges"])
        self.assertIn({"from": "composer", "to": "composer-audit", "type": "required"}, tree["edges"])
        self.assertIn({"from": "ci-runner", "to": "composer-audit", "type": "recommended"}, tree["edges"])
        self.assertNotIn({"from": "ci-runner", "to": "composer-audit", "type": "required"}, tree["edges"])
        # ticket 01: `.editorconfig` node — required from onboarding-setup (its own
        # prerequisite, mirroring composer/ci-runner), recommended into
        # php-cs-fixer (settle basic formatting before style-tool adoption).
        self.assertIn({"from": "onboarding-setup", "to": "editorconfig", "type": "required"}, tree["edges"])
        self.assertIn({"from": "editorconfig", "to": "php-cs-fixer", "type": "recommended"}, tree["edges"])
        # ticket 41: editorconfig also resolves into structural-scan —
        # declared in tooling-tree.md's own edge table (both endpoints are
        # generic-root nodes), not php-tooling-tree.md's.
        self.assertIn({"from": "editorconfig", "to": "structural-scan", "type": "resolved"}, tree["edges"])
        # signals ticket 2: php-cs-fixer's route to php-safety-net
        # simplified — new recommended edge into rector-php-set replaces its
        # own direct resolved edge (still transitively decided before
        # rector-dead-code/rector-code-quality, both still direct leaves,
        # can resolve).
        self.assertIn({"from": "php-cs-fixer", "to": "rector-php-set", "type": "recommended"}, tree["edges"])
        self.assertNotIn({"from": "php-cs-fixer", "to": "php-safety-net", "type": "resolved"}, tree["edges"])
        # signals ticket 2: test-runner-if-missing dropped from the leaf set,
        # no replacement.
        self.assertNotIn({"from": "test-runner-if-missing", "to": "php-safety-net", "type": "resolved"}, tree["edges"])
        # signals ticket 2: the level-chain leaf moves from level 10 to level
        # 5 — the chain's only existing structural fork point.
        self.assertIn({"from": "phpstan-level-5", "to": "php-safety-net", "type": "resolved"}, tree["edges"])
        self.assertNotIn({"from": "phpstan-level-10", "to": "php-safety-net", "type": "resolved"}, tree["edges"])
        # signals ticket 2: phpmd is a Signal-producing node, proposed and
        # ranked normally but never gating structural work directly — no
        # resolved edge into either gate. Ticket 63: phpmd additionally
        # requires php-safety-net now (a Signal *wave* node too — proposed
        # only once the Safety Net closes, orthogonal to the Signal axis).
        self.assertIn({"from": "composer", "to": "phpmd", "type": "required"}, tree["edges"])
        self.assertIn({"from": "php-safety-net", "to": "phpmd", "type": "required"}, tree["edges"])
        self.assertNotIn({"from": "phpmd", "to": "php-safety-net", "type": "resolved"}, tree["edges"])
        # ticket 63: secret-detection's required parent is repointed from
        # onboarding-setup to structural-scan itself — a Signal wave node,
        # proposed only once the (language-neutral) Safety Net has closed,
        # not from the very first wave. Still no resolved edge either way
        # (language-neutral, not part of any Safety Net).
        self.assertNotIn({"from": "onboarding-setup", "to": "secret-detection", "type": "required"}, tree["edges"])
        self.assertIn({"from": "structural-scan", "to": "secret-detection", "type": "required"}, tree["edges"])
        self.assertNotIn({"from": "secret-detection", "to": "structural-scan", "type": "resolved"}, tree["edges"])

    def test_order_contains_nodes(self):
        tree = load_tree()
        for n in ["git", "onboarding-setup", "composer", "phpstan-level-0", "phpstan-level-1", "rector-dead-code", "structural-scan"]:
            self.assertIn(n, tree["order"])

    def test_resolved_parents_of_structural_scan(self):
        # ticket 42: structural-scan's direct resolved parents are now just
        # editorconfig (generic-root leaf) and php-safety-net (the PHP
        # tree's own aggregation node, renamed from php-structural-scan,
        # ticket 63) — not the seven PHP leaves directly. ADR-0022
        # (follow-up): ci-runner joined as a third generic-root
        # resolved-parent — deterministic tooling settling first includes
        # having somewhere for quality jobs to run at all.
        tree = load_tree()
        self.assertEqual(
            set(tree["resolved_parents"]["structural-scan"]),
            {"editorconfig", "ci-runner", "php-safety-net"},
        )

    def test_resolved_parents_of_php_safety_net(self):
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
        # to eleven. Ticket 63 (this node renamed php-structural-scan ->
        # php-safety-net) drops `composer-audit` and
        # `phpstan-deprecation-rules` too — both moved to the Signal wave
        # instead, since their findings (third-party CVEs; deprecated-API
        # calls) don't collide with agent-driven structural work the way the
        # remaining nine leaves' findings do — down to nine.
        tree = load_tree()
        self.assertEqual(
            set(tree["resolved_parents"]["php-safety-net"]),
            {
                "psr-4",
                "phpunit",
                "phpstan-level-5",
                "rector-dead-code",
                "rector-type-coverage",
                "rector-php-set",
                "rector-code-quality",
                "rector-phpunit-set",
                "psalm-taint-analysis",
            },
        )
        self.assertNotIn("psalm", tree["resolved_parents"]["php-safety-net"])
        self.assertNotIn("rector-early-return", tree["resolved_parents"]["php-safety-net"])
        self.assertNotIn("test-runner-if-missing", tree["resolved_parents"]["php-safety-net"])
        self.assertNotIn("php-cs-fixer", tree["resolved_parents"]["php-safety-net"])
        self.assertNotIn("phpstan-level-10", tree["resolved_parents"]["php-safety-net"])
        self.assertNotIn("composer-audit", tree["resolved_parents"]["php-safety-net"])
        self.assertNotIn("phpstan-deprecation-rules", tree["resolved_parents"]["php-safety-net"])

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
        # No tie to rector-php-set specifically (still true) -- but it does
        # carry a bare `composer` required parent since ticket 62, the
        # tree-wide floor every other node in this family already had.
        self.assertEqual(tree["required_parents"]["rector-type-coverage"], ["composer"])
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

    def test_php_safety_net_aggregated_away_not_exposed(self):
        # ticket 42: php-safety-net (renamed from php-structural-scan,
        # ticket 63) feeds structural-scan's own resolved gate, so it must
        # never be exposed as a proposable candidate itself — only
        # structural-scan is.
        tree = load_tree()
        self.assertEqual(tree["exposed_resolved_gate_nodes"], {"structural-scan"})

    def test_php_minimal_version_edges(self):
        # ticket 57: php-minimal-version's only required parent used to be
        # rector-php-set alone (reversed direction from ticket 35's original
        # design, where php-minimal-version was rector-php-set's own
        # recommended parent instead) -- is-php-project/ci-runner dropped as
        # direct required parents, both still reachable transitively.
        # Ticket 63: php-safety-net joins as an *additional* required
        # parent — a Signal wave node now, kept alongside rector-php-set
        # (not replacing it) since a rejected rector-php-set must still
        # permanently close this node.
        tree = load_tree()
        self.assertEqual(
            set(tree["required_parents"]["php-minimal-version"]),
            {"rector-php-set", "php-safety-net"},
        )
        self.assertNotIn("php-minimal-version", tree["recommended_parents"].get("rector-php-set", []))
        self.assertNotIn("rector-php-set", tree["recommended_parents"].get("php-minimal-version", []))
        # Deliberately NOT one of php-safety-net's resolved-parent
        # leaves — never decided as one, ticket 35's original grilling
        # session included, still not one after ticket 57 or ticket 63.
        self.assertNotIn("php-minimal-version", tree["resolved_parents"]["php-safety-net"])

    def test_ticket_63_additive_signal_wave_edges(self):
        # ticket 63: coverage-floor and phpstan-level-6 both gain
        # php-safety-net as an *additional* required parent, keeping their
        # existing one — the same additive shape as phpmd/php-minimal-version
        # above, and composer-audit's own edges tested elsewhere. A rejected
        # phpunit/phpstan-level-5 must still permanently close the
        # dependent, which a bare php-safety-net edge alone wouldn't do.
        tree = load_tree()
        self.assertEqual(
            set(tree["required_parents"]["coverage-floor"]),
            {"phpunit", "php-safety-net"},
        )
        self.assertEqual(
            set(tree["required_parents"]["phpstan-level-6"]),
            {"phpstan-level-5", "php-safety-net", "phpstan-baseline-empty"},
        )
        # Levels 7-10 need no edge of their own -- they inherit the wait
        # transitively through level 6's own required-parent chain.
        # They do carry phpstan-baseline-empty as a direct required parent
        # (the baseline gate applies to every level independently).
        self.assertEqual(
            set(tree["required_parents"]["phpstan-level-7"]),
            {"phpstan-level-6", "phpstan-baseline-empty"},
        )
        self.assertNotIn("php-safety-net", tree["required_parents"]["phpstan-level-7"])

    def test_ticket_63_phpstan_deprecation_rules_additive_signal_wave(self):
        # ticket 63: phpstan-deprecation-rules moves from Safety Net leaf to
        # Signal wave — drops its resolved edge (tested in
        # test_resolved_parents_of_php_safety_net above), gains
        # php-safety-net as an additional required parent alongside its
        # existing phpstan-level-5 one.
        tree = load_tree()
        self.assertEqual(
            set(tree["required_parents"]["phpstan-deprecation-rules"]),
            {"phpstan-level-5", "php-safety-net"},
        )

    def test_ticket_63_semgrep_fully_repointed(self):
        # ticket 63: semgrep is the one clean full-replacement case — its
        # required parent becomes php-safety-net alone (composer dropped
        # entirely, not kept alongside), and its old recommended parent
        # (psalm-taint-analysis) is dropped too, redundant now that
        # psalm-taint-analysis is one of php-safety-net's own nine leaves.
        # ci-runner joins as a new recommended parent instead — the same
        # audit-style shape composer-audit now has.
        tree = load_tree()
        self.assertEqual(tree["required_parents"]["semgrep"], ["php-safety-net"])
        self.assertNotIn("composer", tree["required_parents"]["semgrep"])
        self.assertEqual(tree["recommended_parents"]["semgrep"], ["ci-runner"])
        self.assertNotIn("psalm-taint-analysis", tree["recommended_parents"]["semgrep"])


class RefactoringNotesResolutionTests(unittest.TestCase):
    """`_resolve_refactoring_notes_dir` — the Refactoring Notes' path,
    default docs/refactoring/, overridable via a `Refactoring Notes:
    `<path>`` line in AGENTS.md/CLAUDE.md (skills/continuous-refactoring/
    references/refactoring-bookkeeping.md's resolution rule)."""

    def _make_repo(self, files: dict, fulfilled: dict | None = None):
        tmp = tempfile.TemporaryDirectory()
        root = pathlib.Path(tmp.name)
        for rel, content in files.items():
            p = root / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content)
        (root / ".git").mkdir()
        if fulfilled is not None:
            seed_dir = root / "docs" / "refactoring"
            seed_dir.mkdir(parents=True, exist_ok=True)
            (seed_dir / "fulfilled-set.json").write_text(
                json.dumps(fulfilled) + "\n"
            )
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

    def _make_repo(self, files: dict, fulfilled: dict | None = None):
        tmp = tempfile.TemporaryDirectory()
        root = pathlib.Path(tmp.name)
        for rel, content in files.items():
            p = root / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content)
        (root / ".git").mkdir()
        if fulfilled is not None:
            seed_dir = root / "docs" / "refactoring"
            seed_dir.mkdir(parents=True, exist_ok=True)
            (seed_dir / "fulfilled-set.json").write_text(
                json.dumps(fulfilled) + "\n"
            )
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
                # ticket 50: psr-4 is a 13th php-safety-net leaf — a
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
            # php-safety-net by fulfilment alone.
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
            # ticket 44: `psalm-taint-analysis` is a 13th php-safety-net
            # leaf. This fixture never adopted vimeo/psalm at all (PHPStan
            # path, no taint scanning either), so a "fully tooled" scenario
            # needs its own rejection written too — otherwise it sits neither
            # fulfilled nor rejected and this helper stops being "fully
            # resolved". `psalm` itself is not a leaf (ticket 37, dropped as
            # redundant) so it needs no rejection here.
            "docs/refactoring/out-of-scope/psalm-taint-analysis.md": "rejected: no taint analysis adopted\n",
        }
class PhpSafetyNetAggregationTests(unittest.TestCase):
    """Ticket 42: `php-safety-net` (renamed from `php-structural-scan`,
    ticket 63) aggregates the PHP tree's nine `resolved` leaves behind
    one node, itself resolving into
    `structural-scan` via a single `resolved` edge. Same `resolved`-edge
    semantics as `structural-scan`'s own gate, one hop down — and, unlike
    `structural-scan`, never itself a proposable candidate."""

    def _make_repo(self, files: dict, fulfilled: dict | None = None):
        tmp = tempfile.TemporaryDirectory()
        root = pathlib.Path(tmp.name)
        for rel, content in files.items():
            p = root / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content)
        (root / ".git").mkdir()
        if fulfilled is not None:
            seed_dir = root / "docs" / "refactoring"
            seed_dir.mkdir(parents=True, exist_ok=True)
            (seed_dir / "fulfilled-set.json").write_text(
                json.dumps(fulfilled) + "\n"
            )
        return tmp, root

    def _fully_tooled_php_leaves(self):
        # Every one of php-safety-net's nine leaves (ticket 43: was
        # seven; ticket 50 added psr-4 as a thirteenth, ticket 63 later
        # dropped composer-audit/phpstan-deprecation-rules back down to
        # nine) fulfilled —
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
            # ticket 44: `psalm-taint-analysis` is one of the nine leaves
            # (ticket 50: psr-4 is now fulfilled instead, above) — this
            # fixture never adopted vimeo/psalm at all (PHPStan path, no
            # taint scanning either), so it needs its own rejection written
            # too (same reasoning as StructuralScanGateTests'
            # `_fully_tooled_files` above). `psalm` itself is not a leaf
            # (ticket 37, dropped as redundant) so it needs no rejection.
            "docs/refactoring/out-of-scope/psalm-taint-analysis.md": "rejected: no taint analysis adopted\n",
        }
    def test_never_in_next_candidates(self):
        files = self._fully_tooled_php_leaves()
        p0_fulfilled = {
            "git": True, "onboarding-setup": True, "is-php-project": True,
            "composer": True, "static-code-analyzer": True,
            "phpstan-level-0": True, "rector-php-set": True,
            "phpunit": True, "php-cs-fixer": True, "phpstan-level-5": True,
            "rector-dead-code": True, "rector-type-coverage": True,
            "rector-code-quality": True, "rector-phpunit-set": True,
            "coverage-floor": True, "psr-4": True,
            "phpstan-not-psalm": True, "phpstan-baseline-empty": True,
        }
        tmp, root = self._make_repo(files, fulfilled=p0_fulfilled)
        try:
            nodes = [c["node"] for c in next_candidates(root, limit=20)]
            self.assertNotIn("php-safety-net", nodes)
            self.assertNotIn("structural-scan", nodes)
        finally:
            tmp.cleanup()
        files[".editorconfig"] = "root = true\n\n[*]\ncharset = utf-8\n"
        p0_fulfilled_with_editor = {**p0_fulfilled, "editorconfig": True, "ci-runner": True, "php-safety-net": True, "structural-scan": True}
        tmp2, root2 = self._make_repo(files, fulfilled=p0_fulfilled_with_editor)
        try:
            nodes = [c["node"] for c in next_candidates(root2, limit=20)]
            self.assertNotIn("php-safety-net", nodes)
            self.assertIn("structural-scan", nodes)
        finally:
            tmp2.cleanup()

    def test_never_in_withheld_candidates(self):
        tmp, root = self._make_repo({})
        try:
            w = withheld_candidates(root)
            self.assertNotIn("php-safety-net", [x["node"] for x in w])
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
        (as `_resolved_gate_status` does, one leaf at a time -- not the bug
        itself, but worth pinning down; `_composer_audit_extra_gate`, ticket
        63, no longer exists) must
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


class RequiredChainReachesComposerInvariantTests(unittest.TestCase):
    """Ticket 62: every PHP-tree node gated by at least one `required`/
    `required-any`/`recommended` edge inside `php-tooling-tree.md` must have
    a `required`/`required-any` chain of its own that transitively reaches
    `composer` -- otherwise `_is_effectively_rejected()` (ticket 60) can
    never automatically recognize it as closed once `composer` is rejected,
    since that function only cascades through `required`/`required-any`
    edges, never `recommended` ones. A node failing this invariant can only
    ever resolve via being fulfilled or via its own, manually-written
    `out-of-scope/` entry -- exactly the live churn observed on
    `continuous-refactoring.de` (issue #4, MR !19) for `rector-type-coverage`,
    the one such node that also happens to be a `php-safety-net` leaf.

    Resolved-gated aggregation nodes (`php-safety-net`, `structural-
    scan`) are never themselves in the checked set -- they carry no
    non-`resolved` incoming edge at all inside this file -- but ticket 63's
    `semgrep` is required-gated on `php-safety-net` alone (its old, direct
    `composer` required parent dropped), so this helper must still be able
    to trace a path through such an aggregation node: it reaches `composer`
    once every one of its own resolved-parent leaves does, via their
    ordinary required chains -- exactly `_resolved_gate_status()`'s own
    per-leaf mechanism, generalized here rather than a hardcoded exemption
    for `php-safety-net` specifically."""

    def _reaches_composer(self, node, tree, _seen=None):
        if _seen is None:
            _seen = set()
        if node in _seen:
            return False
        _seen.add(node)
        if node == "composer":
            return True
        # An aggregation node (php-safety-net) has no required/required-any
        # parent of its own -- a rejected composer still resolves it for
        # real once every one of its resolved-parent leaves individually
        # reaches composer via their own required chain (ticket 63's
        # semgrep relies on exactly this).
        resolved_leaves = tree["resolved_parents"].get(node, [])
        if resolved_leaves:
            return all(self._reaches_composer(leaf, tree, set(_seen)) for leaf in resolved_leaves)
        parents = tree["required_parents"].get(node, []) + tree["required_any_parents"].get(node, [])
        return any(self._reaches_composer(p, tree, set(_seen)) for p in parents)

    def test_every_gated_php_tree_node_reaches_composer(self):
        php_tree = load_tree(tooling_tree.TREE_MD)
        full_tree = load_tree()
        gated_nodes = {e["to"] for e in php_tree["edges"] if e["type"] != "resolved"}

        offenders = sorted(n for n in gated_nodes if not self._reaches_composer(n, full_tree))

        self.assertEqual(
            [],
            offenders,
            "these php-tooling-tree.md nodes have no required/required-any chain back "
            "to composer, so a rejected composer can never automatically close them: "
            f"{offenders}",
        )


class ComposerTieBackClosesOrphanedNodesTests(unittest.TestCase):
    """Ticket 62: `rector-type-coverage` (and, at the time, `semgrep`) gained
    a bare `composer` required parent (added alongside their existing
    recommended parent(s), not replacing them) so a rejected `composer`
    auto-closes them with no manual out-of-scope entry needed (the live
    `continuous-refactoring.de` incident this ticket fixes), while a
    genuinely adopted `composer` with individually-rejected Rector siblings
    still leaves `rector-type-coverage` reachable exactly as ADR-0019's own
    deliberate loosening intended -- the new edge must not re-tighten that.
    Ticket 63 later repointed `semgrep`'s required parent from `composer` to
    `php-safety-net` alone (see SemgrepNodeTests/PhpSafetyNetGateOpensSignalWaveTests
    below for its own, different closure guarantee) -- `rector-type-coverage`
    is unaffected and keeps the bare `composer` edge tested here."""

    def test_rejected_composer_closes_rector_type_coverage(self):
        tree = load_tree()
        rejected = {"composer"}
        self.assertTrue(tooling_tree._is_effectively_rejected("rector-type-coverage", tree, rejected))

    def test_fulfilled_composer_with_rejected_rector_siblings_still_releases_type_coverage(self):
        tree = load_tree()
        # composer itself is NOT rejected -- only its two Rector siblings are,
        # the exact scenario ADR-0019 confirmed should stay open regardless
        # of rector-php-set's own fulfilment.
        rejected = {"rector-dead-code", "rector-code-quality"}
        self.assertFalse(tooling_tree._is_effectively_rejected("rector-type-coverage", tree, rejected))
        detected = {
            "rector-dead-code": {"fulfilled": False},
            "rector-code-quality": {"fulfilled": False},
            "php-cs-fixer": {"fulfilled": True},
            "phpstan-level-3": {"fulfilled": True},
        }
        self.assertEqual(
            tooling_tree._undecided_recommended_parents("rector-type-coverage", tree, detected, rejected),
            [],
        )
class RejectionRespectedTests(unittest.TestCase):
    """A node with an out-of-scope entry stays out of next_candidates()
    even once its required parents are fulfilled -- until the
    entry is removed."""

    def _make_repo(self, files: dict, fulfilled: dict | None = None):
        tmp = tempfile.TemporaryDirectory()
        root = pathlib.Path(tmp.name)
        for rel, content in files.items():
            p = root / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content)
        (root / ".git").mkdir()
        if fulfilled is not None:
            seed_dir = root / "docs" / "refactoring"
            seed_dir.mkdir(parents=True, exist_ok=True)
            (seed_dir / "fulfilled-set.json").write_text(
                json.dumps(fulfilled) + "\n"
            )
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

    def test_rejected_ordinary_node_not_in_next_candidates_even_with_fulfilled_parents(self):
        tmp, root = self._make_repo({
            "composer.json": json.dumps({"require": {"php": ">=7.2"}}),
            "composer.lock": "{}",
            "docs/refactoring/out-of-scope/phpunit.md": "rejected\n",
        })
        try:
            nodes = [c["node"] for c in next_candidates(root, limit=10)]
            self.assertNotIn("phpunit", nodes)
        finally:
            tmp.cleanup()

    def test_unrejected_sibling_still_proposed(self):
        tmp, root = self._make_repo({
            "composer.json": json.dumps({"require": {"php": ">=7.2"}}),
            "composer.lock": "{}",
            "docs/refactoring/out-of-scope/php-cs-fixer.md": "rejected\n",
        }, fulfilled={
            "git": True, "onboarding-setup": True, "is-php-project": True,
            "composer": True, "static-code-analyzer": True,
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

    def _make_repo(self, files: dict, fulfilled: dict | None = None):
        tmp = tempfile.TemporaryDirectory()
        root = pathlib.Path(tmp.name)
        for rel, content in files.items():
            p = root / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content)
        (root / ".git").mkdir()
        if fulfilled is not None:
            seed_dir = root / "docs" / "refactoring"
            seed_dir.mkdir(parents=True, exist_ok=True)
            (seed_dir / "fulfilled-set.json").write_text(
                json.dumps(fulfilled) + "\n"
            )
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

    def _p0_fulfilled_dict(self):
        return {
            "git": True, "onboarding-setup": True, "is-php-project": True,
            "composer": True, "static-code-analyzer": True,
            "phpstan-level-0": True, "rector-php-set": True, "editorconfig": True,
            "phpstan-not-psalm": True, "phpstan-baseline-empty": True,
        }

    def test_child_withheld_while_recommended_parent_undecided(self):
        tmp, root = self._make_repo(self._p0_fulfilled_files(), fulfilled=self._p0_fulfilled_dict())
        try:
            nodes = [c["node"] for c in next_candidates(root)]
            self.assertIn("php-cs-fixer", nodes)  # the undecided parent itself is still proposable
            self.assertNotIn("rector-dead-code", nodes)
        finally:
            tmp.cleanup()

    def test_child_released_once_recommended_parent_rejected(self):
        tmp, root = self._make_repo(self._p0_fulfilled_files(), fulfilled=self._p0_fulfilled_dict())
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
        fulfilled = {**self._p0_fulfilled_dict(), "php-cs-fixer": True}
        tmp, root = self._make_repo(files, fulfilled=fulfilled)
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
        fulfilled = {**self._p0_fulfilled_dict(), "php-cs-fixer": True}
        tmp, root = self._make_repo(files, fulfilled=fulfilled)
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
        fulfilled = {**self._p0_fulfilled_dict(), "php-cs-fixer": True}
        tmp, root = self._make_repo(files, fulfilled=fulfilled)
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
        tmp, root = self._make_repo(self._p0_fulfilled_files(), fulfilled=self._p0_fulfilled_dict())
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
        # change: onboarding-setup, php-cs-fixer, phpunit, test-runner-if-missing,
        # composer-audit, phpstan-level-1).
        files = self._p0_fulfilled_files()
        files["composer.json"] = json.dumps({
            "require": {"vendor/pkg": "^1.0"},
            "require-dev": {"phpstan/phpstan": "^1.0"},
        })
        files[".github/workflows/ci.yml"] = "jobs:\n  build:\n    steps:\n      - run: echo hi\n"
        fulfilled = self._p0_fulfilled_dict()
        tmp, root = self._make_repo(files, fulfilled=fulfilled)
        try:
            nodes = [c["node"] for c in next_candidates(root)]
            self.assertGreater(len(nodes), 5)
            # limit is still honored when a caller explicitly wants one
            self.assertLessEqual(len(next_candidates(root, limit=3)), 3)
        finally:
            tmp.cleanup()


class GateNodeContractTests(unittest.TestCase):
    """The three recognition-gate nodes (`_NEVER_PROPOSED` — never proposed
    themselves) must keep their gated nodes out of ``next_candidates()``
    while seeded False, and release them once seeded True — the contract
    php-tooling-tree.md's `grd`/`pnp`/`pbe` gate rows exist for."""

    def _make_repo(self, files: dict, fulfilled: dict | None = None):
        tmp = tempfile.TemporaryDirectory()
        root = pathlib.Path(tmp.name)
        for rel, content in files.items():
            p = root / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content)
        (root / ".git").mkdir()
        if fulfilled is not None:
            seed_dir = root / "docs" / "refactoring"
            seed_dir.mkdir(parents=True, exist_ok=True)
            (seed_dir / "fulfilled-set.json").write_text(
                json.dumps(fulfilled) + "\n"
            )
        return tmp, root

    def test_baseline_empty_gate_false_keeps_phpstan_level_1_out(self):
        # phpstan-level-1's required parents: phpstan-level-0,
        # phpstan-not-psalm, phpstan-baseline-empty. The other two
        # fulfilled, the baseline gate seeded False is the sole thing
        # holding the node back; seeded True, it appears.
        seed = {
            "phpstan-level-0": True, "phpstan-not-psalm": True,
            "phpstan-baseline-empty": False,
        }
        tmp, root = self._make_repo({})
        try:
            nodes = [c["node"] for c in next_candidates(root, fulfilled=seed)]
            self.assertNotIn("phpstan-level-1", nodes)
            nodes = [c["node"] for c in next_candidates(root, fulfilled={**seed, "phpstan-baseline-empty": True})]
            self.assertIn("phpstan-level-1", nodes)
        finally:
            tmp.cleanup()

    def test_not_psalm_gate_false_keeps_phpstan_level_1_out(self):
        # Symmetric: with the level-0 and baseline gates fulfilled, the
        # Psalm-mutual-exclusion gate seeded False is the sole blocker.
        seed = {
            "phpstan-level-0": True, "phpstan-baseline-empty": True,
            "phpstan-not-psalm": False,
        }
        tmp, root = self._make_repo({})
        try:
            nodes = [c["node"] for c in next_candidates(root, fulfilled=seed)]
            self.assertNotIn("phpstan-level-1", nodes)
            nodes = [c["node"] for c in next_candidates(root, fulfilled={**seed, "phpstan-not-psalm": True})]
            self.assertIn("phpstan-level-1", nodes)
        finally:
            tmp.cleanup()

    def test_has_real_dependency_gate_false_keeps_composer_audit_out(self):
        # composer-audit's required parents: composer, php-safety-net,
        # has-real-dependency (ci-runner is its recommended parent, seeded
        # decided so it isn't the thing under test). With the first two
        # fulfilled, the dependency gate seeded False is the sole blocker.
        seed = {
            "composer": True, "php-safety-net": True, "ci-runner": True,
            "has-real-dependency": False,
        }
        tmp, root = self._make_repo({})
        try:
            nodes = [c["node"] for c in next_candidates(root, fulfilled=seed)]
            self.assertNotIn("composer-audit", nodes)
            nodes = [c["node"] for c in next_candidates(root, fulfilled={**seed, "has-real-dependency": True})]
            self.assertIn("composer-audit", nodes)
        finally:
            tmp.cleanup()


class PhpVersionReversalTests(unittest.TestCase):
    """php-tooling-tree.md's mechanical reversal: a rejected node's
    `Blocked by: PHP >= X.Y` condition satisfied by the target's current
    floor surfaces as a finding (refactor-scan detects, refactor-learn
    removes the out-of-scope entry -- never the other way round)."""

    def _make_repo(self, files: dict, fulfilled: dict | None = None):
        tmp = tempfile.TemporaryDirectory()
        root = pathlib.Path(tmp.name)
        for rel, content in files.items():
            p = root / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content)
        (root / ".git").mkdir()
        if fulfilled is not None:
            seed_dir = root / "docs" / "refactoring"
            seed_dir.mkdir(parents=True, exist_ok=True)
            (seed_dir / "fulfilled-set.json").write_text(
                json.dumps(fulfilled) + "\n"
            )
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

    def _make_repo(self, files: dict, fulfilled: dict | None = None):
        tmp = tempfile.TemporaryDirectory()
        root = pathlib.Path(tmp.name)
        for rel, content in files.items():
            p = root / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content)
        (root / ".git").mkdir()
        if fulfilled is not None:
            seed_dir = root / "docs" / "refactoring"
            seed_dir.mkdir(parents=True, exist_ok=True)
            (seed_dir / "fulfilled-set.json").write_text(
                json.dumps(fulfilled) + "\n"
            )
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
            "docs/refactoring/bookkeeping.md": "# Refactoring Bookkeeping\n",
            ".github/workflows/ci.yml": "jobs:\n  lint:\n    steps:\n      - run: php -l\n",
            # ticket 01: decided (fulfilled), so php-cs-fixer's own recommended
            # gate doesn't interfere with what this test actually exercises.
            ".editorconfig": "root = true\n\n[*]\ncharset = utf-8\n",
        }, fulfilled={
            "git": True, "onboarding-setup": True, "is-php-project": True,
            "composer": True, "static-code-analyzer": True,
            "editorconfig": True,
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

    def test_next_candidates_never_proposes_blocked_leaves(self):
        tmp, root = self._make_repo({
            "composer.json": json.dumps({"require": {"php": ">=5.6"}}),
            "composer.lock": "{}",
            "docs/refactoring/bookkeeping.md": "# Refactoring Bookkeeping\n",
            ".github/workflows/ci.yml": "jobs:\n  lint:\n    steps:\n      - run: php -l\n",
        })
        try:
            nodes = [c["node"] for c in next_candidates(root)]
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
class OrderedBacklogTests(unittest.TestCase):
    """Ticket 05: ordered_backlog() returns the complete ordered list of
    unresolved scope nodes in tree order (blocked nodes included) — the
    list a scan records into ``Open``."""

    def _make_repo(self, files: dict, fulfilled: dict | None = None):
        tmp = tempfile.TemporaryDirectory()
        root = pathlib.Path(tmp.name)
        for rel, content in files.items():
            p = root / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content)
        (root / ".git").mkdir()
        if fulfilled is not None:
            seed_dir = root / "docs" / "refactoring"
            seed_dir.mkdir(parents=True, exist_ok=True)
            (seed_dir / "fulfilled-set.json").write_text(
                json.dumps(fulfilled) + "\n"
            )
        return tmp, root

    def test_empty_repo_backlog_starts_with_onboarding_setup(self):
        tmp, root = self._make_repo({})
        try:
            backlog = ordered_backlog(root)
            self.assertIn("onboarding-setup", backlog)
            self.assertNotIn("git", backlog)
        finally:
            tmp.cleanup()

    def test_backlog_excludes_fulfilled_nodes(self):
        tmp, root = self._make_repo({
            "docs/refactoring/bookkeeping.md": "# Refactoring Bookkeeping\n",
            "composer.json": json.dumps({"require": {"php": "^8.1"}}),
            "composer.lock": "{}",
        }, fulfilled={"onboarding-setup": True, "is-php-project": True, "composer": True})
        try:
            backlog = ordered_backlog(root)
            self.assertNotIn("onboarding-setup", backlog)
            self.assertNotIn("composer", backlog)
        finally:
            tmp.cleanup()

    def test_backlog_excludes_rejected_nodes(self):
        tmp, root = self._make_repo({
            "docs/refactoring/bookkeeping.md": "# Refactoring Bookkeeping\n",
            "docs/refactoring/out-of-scope/phpunit.md": "rejected\n",
        })
        try:
            backlog = ordered_backlog(root)
            self.assertNotIn("phpunit", backlog)
        finally:
            tmp.cleanup()

    def test_backlog_includes_blocked_nodes(self):
        tmp, root = self._make_repo({})
        try:
            backlog = ordered_backlog(root)
            self.assertIn("composer", backlog)
        finally:
            tmp.cleanup()


class WithheldWithReasonsTests(unittest.TestCase):
    """Ticket 05: withheld_with_reasons() returns nodes with reasons."""

    def _make_repo(self, files: dict, fulfilled: dict | None = None):
        tmp = tempfile.TemporaryDirectory()
        root = pathlib.Path(tmp.name)
        for rel, content in files.items():
            p = root / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content)
        (root / ".git").mkdir()
        if fulfilled is not None:
            seed_dir = root / "docs" / "refactoring"
            seed_dir.mkdir(parents=True, exist_ok=True)
            (seed_dir / "fulfilled-set.json").write_text(
                json.dumps(fulfilled) + "\n"
            )
        return tmp, root

    def test_withheld_with_undecided_recommended_parent(self):
        tmp, root = self._make_repo({
            "docs/refactoring/bookkeeping.md": "# Refactoring Bookkeeping\n",
            "composer.json": json.dumps({"require-dev": {"phpstan/phpstan": "^1.0"}}),
            "composer.lock": "{}",
            "phpstan.neon": "parameters:\n    level: 0\n",
            "phpstan-baseline.neon": "parameters:\n    ignoreErrors: []\n",
        }, fulfilled={
            "git": True, "onboarding-setup": True, "is-php-project": True,
            "composer": True, "static-code-analyzer": True,
            "phpstan-level-0": True, "rector-php-set": True,
            "phpstan-not-psalm": True, "phpstan-baseline-empty": True,
        })
        try:
            withheld = withheld_with_reasons(root)
            withheld_nodes = {w["node"]: w["reason"] for w in withheld}
            self.assertIn("rector-dead-code", withheld_nodes)
            self.assertIn("php-cs-fixer", withheld_nodes)
        finally:
            tmp.cleanup()

    def test_withheld_empty_when_all_decided(self):
        tmp, root = self._make_repo({
            "docs/refactoring/bookkeeping.md": "# Refactoring Bookkeeping\n",
            "composer.json": json.dumps({"require": {"php": ">=8.1"}}),
            "composer.lock": "{}",
            "docs/refactoring/out-of-scope/phpunit.md": "rejected\n",
            "docs/refactoring/out-of-scope/php-cs-fixer.md": "rejected\n",
            "docs/refactoring/out-of-scope/rector-dead-code.md": "rejected\n",
            "docs/refactoring/out-of-scope/rector-type-coverage.md": "rejected\n",
            "docs/refactoring/out-of-scope/rector-php-set.md": "rejected\n",
            "docs/refactoring/out-of-scope/rector-code-quality.md": "rejected\n",
            "docs/refactoring/out-of-scope/rector-phpunit-set.md": "rejected\n",
            "docs/refactoring/out-of-scope/psr-4.md": "rejected\n",
            "docs/refactoring/out-of-scope/phpstan-level-0.md": "rejected\n",
            "docs/refactoring/out-of-scope/phpstan-level-1.md": "rejected\n",
            "docs/refactoring/out-of-scope/phpstan-level-2.md": "rejected\n",
            "docs/refactoring/out-of-scope/phpstan-level-3.md": "rejected\n",
            "docs/refactoring/out-of-scope/phpstan-level-4.md": "rejected\n",
            "docs/refactoring/out-of-scope/phpstan-level-5.md": "rejected\n",
            "docs/refactoring/out-of-scope/psalm-taint-analysis.md": "rejected\n",
            "docs/refactoring/out-of-scope/coverage-floor.md": "rejected\n",
            "docs/refactoring/out-of-scope/composer-audit.md": "rejected\n",
            "docs/refactoring/out-of-scope/semgrep.md": "rejected\n",
            "docs/refactoring/out-of-scope/phpmd.md": "rejected\n",
            "docs/refactoring/out-of-scope/phpstan-deprecation-rules.md": "rejected\n",
            "docs/refactoring/out-of-scope/php-minimal-version.md": "rejected\n",
        })
        try:
            withheld = withheld_with_reasons(root)
            withheld_nodes = {w["node"] for w in withheld}
            self.assertNotIn("rector-dead-code", withheld_nodes)
        finally:
            tmp.cleanup()


class ClosedByRejectionTests(unittest.TestCase):
    """Ticket 05: closed_by_rejection() returns nodes whose required
    ancestor is rejected."""

    def test_rejected_composer_closes_php_tree(self):
        tree = load_tree()
        rejected = {"composer"}
        closed = closed_by_rejection(tree, rejected)
        self.assertIn("php-cs-fixer", closed)
        self.assertIn("phpunit", closed)
        self.assertIn("rector-dead-code", closed)

    def test_no_rejection_means_no_closure(self):
        tree = load_tree()
        closed = closed_by_rejection(tree, set())
        self.assertEqual(closed, [])


class SeedInputTests(unittest.TestCase):
    """Ticket 05: seed input contract."""

    def _make_repo(self, files: dict, fulfilled: dict | None = None):
        tmp = tempfile.TemporaryDirectory()
        root = pathlib.Path(tmp.name)
        for rel, content in files.items():
            p = root / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content)
        (root / ".git").mkdir()
        if fulfilled is not None:
            seed_dir = root / "docs" / "refactoring"
            seed_dir.mkdir(parents=True, exist_ok=True)
            (seed_dir / "fulfilled-set.json").write_text(
                json.dumps(fulfilled) + "\n"
            )
        return tmp, root

    def test_seed_drives_next_candidates(self):
        tmp, root = self._make_repo({})
        try:
            seed = {
                "git": True, "onboarding-setup": True, "is-php-project": True,
                "composer": True, "editorconfig": True,
            }
            nodes = [c["node"] for c in next_candidates(root, fulfilled=seed)]
            # composer fulfilled -> phpunit, psr-4 should be proposable
            self.assertIn("phpunit", nodes)
            self.assertIn("psr-4", nodes)
            # onboarding-setup fulfilled -> not in candidates
            self.assertNotIn("onboarding-setup", nodes)
        finally:
            tmp.cleanup()

    def test_seed_takes_priority_over_detection(self):
        tmp, root = self._make_repo({})
        try:
            seed = {
                "git": True, "onboarding-setup": True, "is-php-project": True,
                "composer": True, "editorconfig": True,
            }
            nodes = [c["node"] for c in next_candidates(root, fulfilled=seed)]
            # Detection would say onboarding-setup is not fulfilled
            # Seed says it is — seed wins
            self.assertNotIn("onboarding-setup", nodes)
        finally:
            tmp.cleanup()

    def test_seed_file_loading(self):
        tmp = tempfile.TemporaryDirectory()
        root = pathlib.Path(tmp.name)
        seed_path = root / "fulfilled-set.json"
        seed_path.write_text(json.dumps({"git": True, "composer": False, "onboarding-setup": True}))
        try:
            loaded = _load_fulfilled_seed(seed_path)
            self.assertEqual(loaded, {"git": True, "composer": False, "onboarding-setup": True})
        finally:
            tmp.cleanup()

    def test_seed_missing_nodes_treated_as_not_fulfilled(self):
        tmp = tempfile.TemporaryDirectory()
        root = pathlib.Path(tmp.name)
        seed_path = root / "fulfilled-set.json"
        seed_path.write_text(json.dumps({"git": True}))
        try:
            loaded = _load_fulfilled_seed(seed_path)
            self.assertTrue(loaded["git"])
            self.assertFalse(loaded.get("composer", False))
        finally:
            tmp.cleanup()

    def test_bookkeeping_derivation(self):
        tmp, root = self._make_repo({
            "docs/refactoring/bookkeeping.md": (
                "# Bookkeeping\n\n"
                "## Safety Net\n\n"
                "**Last scan:** 2026-09-14\n\n"
                "**Open:**\n"
                "- `phpunit`\n"
                "- `php-cs-fixer`\n\n"
                "**Out-of-scope:**\n"
                "- `psalm`\n"
            ),
        })
        try:
            tree = load_tree()
            derived = _derive_fulfilled_from_bookkeeping(root, tree)
            self.assertIsNotNone(derived)
            self.assertTrue(derived["git"])
            self.assertTrue(derived["composer"])
            self.assertFalse(derived["phpunit"])
            self.assertFalse(derived["php-cs-fixer"])
            self.assertFalse(derived["psalm"])
        finally:
            tmp.cleanup()

    def test_bookkeeping_derivation_guardrails_section_and_pointers(self):
        # The documented shape's other half: a `## Guardrails` section,
        # whose Out-of-scope bullets carry the `— out-of-scope/<slug>.md`
        # pointer (only the slug itself counts), and `#82` issue refs on
        # Open bullets (first token is the slug).
        tmp, root = self._make_repo({
            "docs/refactoring/bookkeeping.md": (
                "# Bookkeeping\n\n"
                "## Safety Net\n\n"
                "**Open:**\n"
                "- none\n\n"
                "**Out-of-scope:**\n"
                "- none\n\n"
                "## Guardrails\n\n"
                "**Open:**\n"
                "- composer-audit (#90)\n\n"
                "**Out-of-scope:**\n"
                "- phpmd — out-of-scope/phpmd.md\n"
            ),
        })
        try:
            tree = load_tree()
            derived = _derive_fulfilled_from_bookkeeping(root, tree)
            self.assertIsNotNone(derived)
            self.assertFalse(derived["composer-audit"])
            self.assertFalse(derived["phpmd"])
            # `- none` markers are empty lists, not slugs; a Safety Net
            # section whose Open/Out-of-scope are both empty leaves every
            # other node fulfilled.
            self.assertTrue(derived["phpunit"])
            self.assertTrue(derived["composer"])
        finally:
            tmp.cleanup()

    def test_bookkeeping_derivation_against_real_fixture(self):
        # Regression: the parser must read the schema as refactor-learn
        # actually writes it (skills/refactor-learn/references/
        # safety-net-write.md) — the synthetic inputs above once drifted
        # from it and the parser returned None on every real file.
        fixture_bookkeeping = (
            pathlib.Path(__file__).resolve().parents[1]
            / "fixtures" / "php" / "php-safety-net-open-blocks-rescan"
            / "project" / "docs" / "refactoring" / "bookkeeping.md"
        )
        tmp, root = self._make_repo({
            "docs/refactoring/bookkeeping.md": fixture_bookkeeping.read_text(encoding="utf-8"),
        })
        try:
            tree = load_tree()
            derived = _derive_fulfilled_from_bookkeeping(root, tree)
            self.assertIsNotNone(derived)
            # The fixture's `## Safety Net` Open holds php-cs-fixer (#5);
            # its Out-of-scope is `- none`, its `**Fulfilled nodes:**`
            # field (old schema, retained) is ignored.
            self.assertFalse(derived["php-cs-fixer"])
            self.assertTrue(derived["composer"])
            self.assertTrue(derived["phpunit"])
        finally:
            tmp.cleanup()

    def test_detect_and_roadmap_returns_backlog(self):
        tmp, root = self._make_repo({})
        try:
            data = tooling_tree.detect_and_roadmap(root)
            self.assertIn("backlog", data)
            self.assertIn("closed_by_rejection", data)
            self.assertIn("withheld_with_reasons", data)
            self.assertNotIn("roadmap", data)
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
        self.assertIn({"from": "git", "to": "onboarding-setup", "type": "required"}, tree["edges"])

    def test_tree_docs_are_siblings_of_the_module(self):
        module_dir = pathlib.Path(tooling_tree.__file__).resolve().parent
        self.assertTrue((module_dir / "tooling-tree.md").exists())
        self.assertTrue((module_dir / "php-tooling-tree.md").exists())


class DirectlyUnblockedChildrenTests(unittest.TestCase):
    """The outlook comment's fan-out diagram data (refactor-implement/references/outlook-comment.md,
    ticket 47/ADR-0027): every node landed_node's fulfilment newly makes
    proposable, not next_candidates()'s full current set."""

    def _make_repo(self, files: dict, fulfilled: dict | None = None):
        tmp = tempfile.TemporaryDirectory()
        root = pathlib.Path(tmp.name)
        for rel, content in files.items():
            p = root / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content)
        (root / ".git").mkdir()
        if fulfilled is not None:
            seed_dir = root / "docs" / "refactoring"
            seed_dir.mkdir(parents=True, exist_ok=True)
            (seed_dir / "fulfilled-set.json").write_text(
                json.dumps(fulfilled) + "\n"
            )
        return tmp, root

    def test_multi_child_fan_out_from_composer(self):
        # composer alone (no phpunit/cs-fixer/CI configured yet) unblocks
        # four siblings at once: phpunit, test-runner-if-missing, and psr-4
        # directly, phpstan-level-0 through the static-code-analyzer
        # walk-through (a pure organizational node, never itself reported).
        # ticket 63: phpmd no longer shows up here -- it additionally
        # requires php-safety-net now (unfulfilled in this bare fixture), so
        # composer alone is no longer sufficient to unblock it.
        tmp, root = self._make_repo({
            "composer.json": json.dumps({"require": {"php": ">=8.1"}}),
            "composer.lock": "{}",
        })
        try:
            fulfilled = {"git": True, "onboarding-setup": True, "composer": True, "static-code-analyzer": True}
            got = {(c["node"], c["type"]) for c in directly_unblocked_children(root, "composer", fulfilled=fulfilled)}
            self.assertEqual(
                got,
                {
                    ("phpunit", "required"),
                    ("test-runner-if-missing", "required"),
                    ("phpstan-level-0", "required"),
                    ("psr-4", "required"),
                },
            )
            self.assertNotIn("phpmd", {c["node"] for c in directly_unblocked_children(root, "composer", fulfilled=fulfilled)})
            self.assertNotIn("static-code-analyzer", {c["node"] for c in directly_unblocked_children(root, "composer", fulfilled=fulfilled)})
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
            fulfilled = {"composer": True, "psalm": True, "phpstan-level-4": True}
            got = {c["node"] for c in directly_unblocked_children(root, "phpstan-level-4", fulfilled=fulfilled)}
            self.assertNotIn("psalm-taint-analysis", got)
        finally:
            tmp.cleanup()

    def test_resolved_gate_walk_through_to_structural_scan(self):
        # phpunit is the last of php-safety-net's leaves to resolve —
        # landing it makes structural-scan newly proposable in the
        # fulfilled-state the caller provides.
        other_leaves = [
            "psr-4", "composer-audit", "phpstan-level-5",
            "phpstan-deprecation-rules", "rector-dead-code", "rector-type-coverage",
            "rector-php-set", "rector-code-quality", "rector-phpunit-set",
            "psalm-taint-analysis", "editorconfig", "ci-runner",
            "coverage-floor",
        ]
        files = {
            "composer.json": json.dumps({"require-dev": {"phpunit/phpunit": "^10.0"}}),
            "composer.lock": "{}",
        }
        for leaf in other_leaves:
            files[f"docs/refactoring/out-of-scope/{leaf}.md"] = "rejected\n"
        fulfilled = {
            "git": True, "onboarding-setup": True, "is-php-project": True,
            "composer": True, "static-code-analyzer": True,
            "phpstan-level-0": True, "phpstan-level-5": True,
            "phpstan-not-psalm": True, "phpstan-baseline-empty": True,
            "php-cs-fixer": True, "rector-php-set": True, "editorconfig": True,
            "ci-runner": True, "phpunit": True,
            "php-safety-net": True, "structural-scan": True,
        }
        tmp, root = self._make_repo(files, fulfilled=fulfilled)
        try:
            nodes = [c["node"] for c in next_candidates(root, fulfilled=fulfilled)]
            self.assertIn("structural-scan", nodes)
        finally:
            tmp.cleanup()

    def test_unknown_landed_node_returns_empty(self):
        tmp, root = self._make_repo({})
        try:
            self.assertEqual(directly_unblocked_children(root, "not-a-real-node"), [])
        finally:
            tmp.cleanup()

    def test_no_children_when_nothing_new(self):
        # Empty repo: onboarding-setup isn't fulfilled, so forcing it "unfulfilled"
        # in the counterfactual changes nothing real -- no children to report.
        tmp, root = self._make_repo({})
        try:
            self.assertEqual(directly_unblocked_children(root, "onboarding-setup"), [])
        finally:
            tmp.cleanup()
class TrackOpenFillingTests(unittest.TestCase):
    """Ticket 06: Advisory agent fixtures for filling ``Open`` with the
    complete ordered backlog — blocked nodes included, in script order."""

    def _make_repo(self, files: dict, fulfilled: dict | None = None):
        tmp = tempfile.TemporaryDirectory()
        root = pathlib.Path(tmp.name)
        for rel, content in files.items():
            p = root / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content)
        (root / ".git").mkdir()
        if fulfilled is not None:
            seed_dir = root / "docs" / "refactoring"
            seed_dir.mkdir(parents=True, exist_ok=True)
            (seed_dir / "fulfilled-set.json").write_text(
                json.dumps(fulfilled) + "\n"
            )
        return tmp, root

    def test_open_includes_blocked_nodes_in_order(self):
        """Every unresolved scope node, including blocked ones, appears in
        ``ordered_backlog()`` in script order — the complete backlog a scan
        records into ``Open``."""
        tmp, root = self._make_repo({
            "docs/refactoring/bookkeeping.md": "# Refactoring Bookkeeping\n\n**Cadence:** weekly\n",
            "composer.json": json.dumps({"require": {"php": "^8.1"}}),
            "composer.lock": "{}",
        }, fulfilled={
            "git": True, "onboarding-setup": True, "is-php-project": True,
            "composer": True, "static-code-analyzer": True,
        })
        try:
            backlog = ordered_backlog(root)
            # onboarding-setup fulfilled, composer fulfilled — phpunit, psr-4,
            # phpstan-level-0, test-runner-if-missing should all appear,
            # even though some are blocked by each other or by
            # recommended-gating.
            self.assertNotIn("onboarding-setup", backlog)
            self.assertNotIn("composer", backlog)
            self.assertIn("phpunit", backlog)
            self.assertIn("psr-4", backlog)
            # Verify order: phpunit comes before rector-dead-code in
            # the tree's edge order (composer → phpunit before
            # rector-php-set → rector-dead-code).
            idx_phpunit = backlog.index("phpunit")
            if "rector-dead-code" in backlog:
                self.assertLess(idx_phpunit, backlog.index("rector-dead-code"))
        finally:
            tmp.cleanup()

    def test_seed_drives_backlog_order(self):
        """A fulfilled seed file (the agent's judgement handed to the script)
        drives the backlog computation — nodes fulfilled by judgement are
        excluded, the rest appear in script order."""
        tmp, root = self._make_repo({})
        try:
            seed = {
                "git": True, "onboarding-setup": True, "is-php-project": True,
                "composer": True, "editorconfig": True,
                "phpunit": True, "psr-4": True, "phpstan-level-0": True,
                "phpstan-level-1": True, "phpstan-level-2": True,
                "phpstan-level-3": True, "phpstan-level-4": True,
                "phpstan-level-5": True,
            }
            backlog = ordered_backlog(root, fulfilled=seed)
            self.assertNotIn("phpunit", backlog)
            self.assertNotIn("phpstan-level-0", backlog)
            self.assertNotIn("phpstan-level-5", backlog)
            # These should still appear — not fulfilled by seed
            self.assertIn("rector-dead-code", backlog)
        finally:
            tmp.cleanup()

    def test_empty_backlog_when_everything_resolved(self):
        """A scan that finds every scope node resolved writes ``Last scan``
        and an empty ``Open`` — ``ordered_backlog()`` returns []."""
        tmp, root = self._make_repo({})
        try:
            # Fully resolved via seed — every non-NEVER_PROPOSED node
            tree = load_tree()
            seed = {n: True for n in tree["nodes"] if n not in tooling_tree._NEVER_PROPOSED}
            seed["git"] = True
            backlog = ordered_backlog(root, fulfilled=seed)
            self.assertEqual(backlog, [])
        finally:
            tmp.cleanup()


class RejectionCascadeTests(unittest.TestCase):
    """Ticket 06: Rejection cascade and its reversal — every node closed
    by a rejected ancestor leaves ``Open``, with no new files; reversing a
    rejection makes the next scan bring those nodes back."""

    def _make_repo(self, files: dict, fulfilled: dict | None = None):
        tmp = tempfile.TemporaryDirectory()
        root = pathlib.Path(tmp.name)
        for rel, content in files.items():
            p = root / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content)
        (root / ".git").mkdir()
        if fulfilled is not None:
            seed_dir = root / "docs" / "refactoring"
            seed_dir.mkdir(parents=True, exist_ok=True)
            (seed_dir / "fulfilled-set.json").write_text(
                json.dumps(fulfilled) + "\n"
            )
        return tmp, root

    def test_rejected_composer_removes_descendants_from_backlog(self):
        """A rejected composer closes every PHP-tree node via required
        edges — ``closed_by_rejection()`` reports them, and they stay out
        of ``ordered_backlog()``."""
        tree = load_tree()
        rejected = {"composer"}
        closed = closed_by_rejection(tree, rejected)
        self.assertIn("php-cs-fixer", closed)
        self.assertIn("phpunit", closed)
        self.assertIn("rector-dead-code", closed)
        self.assertIn("phpstan-level-0", closed)

        tmp, root = self._make_repo({
            "docs/refactoring/bookkeeping.md": "# Refactoring Bookkeeping\n",
            "docs/refactoring/out-of-scope/composer.md": "rejected\n",
        })
        try:
            backlog = ordered_backlog(root)
            self.assertNotIn("php-cs-fixer", backlog)
            self.assertNotIn("phpunit", backlog)
            self.assertNotIn("rector-dead-code", backlog)
        finally:
            tmp.cleanup()

    def test_reversal_brings_nodes_back(self):
        """Removing an out-of-scope entry (reversing the rejection) makes
        ``ordered_backlog()`` include the formerly-closed nodes again."""
        tree = load_tree()
        rejected = {"composer"}
        closed = closed_by_rejection(tree, rejected)
        self.assertIn("phpunit", closed)

        tmp, root = self._make_repo({
            "docs/refactoring/bookkeeping.md": "# Refactoring Bookkeeping\n",
            "composer.json": json.dumps({"require": {"php": "^8.1"}}),
            "composer.lock": "{}",
            "docs/refactoring/out-of-scope/composer.md": "rejected\n",
        })
        try:
            backlog_before = ordered_backlog(root)
            self.assertNotIn("phpunit", backlog_before)
            # Reverse the rejection
            (root / "docs/refactoring/out-of-scope" / "composer.md").unlink()
            backlog_after = ordered_backlog(root)
            self.assertIn("phpunit", backlog_after)
        finally:
            tmp.cleanup()

    def test_partial_rejection_only_closes_required_descendants(self):
        """Rejecting a non-root node only closes nodes that transitively
        depend on it via required edges — siblings remain in the backlog."""
        tmp, root = self._make_repo({
            "docs/refactoring/bookkeeping.md": "# Refactoring Bookkeeping\n",
            "composer.json": json.dumps({"require-dev": {"phpstan/phpstan": "^1.0"}}),
            "composer.lock": "{}",
            "phpstan.neon": "parameters:\n    level: 5\n",
            "phpstan-baseline.neon": "parameters:\n    ignoreErrors: []\n",
            "docs/refactoring/out-of-scope/phpstan-level-2.md": "rejected\n",
        })
        try:
            backlog = ordered_backlog(root)
            # phpstan-level-2 rejected — levels 3,4,5 are effectively
            # closed (required chain through level-2)
            self.assertNotIn("phpstan-level-2", backlog)
            self.assertNotIn("phpstan-level-3", backlog)
            self.assertNotIn("phpstan-level-4", backlog)
            self.assertNotIn("phpstan-level-5", backlog)
            # But phpunit, psr-4 etc. remain — not dependent on phpstan-level-2
            self.assertIn("phpunit", backlog)
            self.assertIn("psr-4", backlog)
        finally:
            tmp.cleanup()


class OldSchemaPassThroughTests(unittest.TestCase):
    """Ticket 06: Bookkeeping in the old shape or with an old-meaning
    ``Open`` should not be migrated and should not cause an error; a Track
    override forces an immediate scan that corrects it."""

    def _make_repo(self, files: dict, fulfilled: dict | None = None):
        tmp = tempfile.TemporaryDirectory()
        root = pathlib.Path(tmp.name)
        for rel, content in files.items():
            p = root / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content)
        (root / ".git").mkdir()
        if fulfilled is not None:
            seed_dir = root / "docs" / "refactoring"
            seed_dir.mkdir(parents=True, exist_ok=True)
            (seed_dir / "fulfilled-set.json").write_text(
                json.dumps(fulfilled) + "\n"
            )
        return tmp, root

    def test_old_fulfilled_nodes_field_ignored(self):
        """The old ``Fulfilled nodes`` field is retired — the script's
        ``_derive_fulfilled_from_bookkeeping`` doesn't read it. Only the
        ``## Safety Net``/``## Guardrails`` sections' ``**Open:**`` and
        ``**Out-of-scope:**`` fields matter, wherever the retired field
        sits."""
        tmp, root = self._make_repo({
            "docs/refactoring/bookkeeping.md": (
                "# Bookkeeping\n\n"
                "Fulfilled nodes:\n\n"
                "- onboarding-setup\n"
                "- composer\n\n"
                "## Safety Net\n\n"
                "**Last scan:** 2026-09-14\n\n"
                "**Open:**\n"
                "- phpunit\n"
                "- php-cs-fixer\n\n"
                "**Out-of-scope:**\n"
                "- psalm\n\n"
                "**Fulfilled nodes:**\n"
                "- editorconfig\n"
            ),
        })
        try:
            tree = load_tree()
            derived = _derive_fulfilled_from_bookkeeping(root, tree)
            self.assertIsNotNone(derived)
            # phpunit and php-cs-fixer are in Open -> not fulfilled
            self.assertFalse(derived["phpunit"])
            self.assertFalse(derived["php-cs-fixer"])
            # psalm is in Out-of-scope -> not fulfilled
            self.assertFalse(derived["psalm"])
            # onboarding-setup and composer are NOT in Open or Out-of-scope
            # -> treated as fulfilled by derivation
            self.assertTrue(derived["onboarding-setup"])
            self.assertTrue(derived["composer"])
            # the retired field's entries (top-level or inside a Track
            # section) are ignored, not migrated — editorconfig is
            # fulfilled by the absence rule, not by its listing
            self.assertTrue(derived["editorconfig"])
        finally:
            tmp.cleanup()

    def test_old_schema_no_track_sections_still_works(self):
        """A bookkeeping.md with no Track sections at all (old shape) is
        treated as a target whose Tracks have never run — not an error.
        The caller returns {} — no detection fallback."""
        tmp, root = self._make_repo({
            "docs/refactoring/bookkeeping.md": (
                "# Bookkeeping\n\n"
                "Fulfilled nodes:\n\n"
                "- onboarding-setup\n"
                "- composer\n"
            ),
        })
        try:
            tree = load_tree()
            derived = _derive_fulfilled_from_bookkeeping(root, tree)
            # No Track sections -> returns None (caller returns {})
            self.assertIsNone(derived)
        finally:
            tmp.cleanup()

    def test_old_schema_fulfilled_nodes_not_affecting_backlog(self):
        """Old ``Fulfilled nodes`` entries don't interfere with the
        ordered backlog — only Track sections and detection matter."""
        tmp, root = self._make_repo({
            "docs/refactoring/bookkeeping.md": (
                "# Bookkeeping\n\n"
                "Fulfilled nodes:\n\n"
                "- onboarding-setup\n"
                "- composer\n"
                "- phpunit\n"
            ),
            "composer.json": json.dumps({"require-dev": {"phpstan/phpstan": "^1.0"}}),
            "composer.lock": "{}",
            "phpstan.neon": "parameters:\n    level: 0\n",
            "phpstan-baseline.neon": "parameters:\n    ignoreErrors: []\n",
        })
        try:
            backlog = ordered_backlog(root)
            # phpunit is listed in old Fulfilled nodes but NOT fulfilled
            # by detection (no CI gate) — the old field is ignored, so
            # phpunit should still appear in the backlog.
            self.assertIn("phpunit", backlog)
        finally:
            tmp.cleanup()

    def test_track_override_forces_rescan(self):
        """A Track override (manual selection) forces an immediate scan
        that corrects old Open entries — verified by providing a fresh
        seed reflecting actual state."""
        tmp, root = self._make_repo({
            "docs/refactoring/bookkeeping.md": (
                "# Bookkeeping\n\n"
                "Fulfilled nodes:\n\n"
                "- onboarding-setup\n"
                "- composer\n"
            ),
            "composer.json": json.dumps({"require-dev": {"phpunit/phpunit": "^10.0"}}),
            "composer.lock": "{}",
            ".github/workflows/ci.yml": "jobs:\n  test:\n    steps:\n      - run: vendor/bin/phpunit\n",
        })
        try:
            # The scan would provide a fresh seed reflecting actual state.
            # phpunit is genuinely fulfilled (dep + CI gate), so the
            # backlog should NOT include it once the seed is applied.
            seed = {
                "git": True, "onboarding-setup": True, "is-php-project": True,
                "composer": True, "editorconfig": True, "phpunit": True,
            }
            backlog = ordered_backlog(root, fulfilled=seed)
            self.assertNotIn("phpunit", backlog)
        finally:
            tmp.cleanup()


if __name__ == "__main__":
    unittest.main()
