"""Tests for deterministic tooling tree parser (skills/refactor-scan/references/tooling_tree.py)

Verify tree parsing and the graph outputs computed from the node state the caller hands in.
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
closed_by_rejection = tooling_tree.closed_by_rejection
withheld_with_reasons = tooling_tree.withheld_with_reasons
ordered_backlog = tooling_tree.ordered_backlog


TRACKER_FILE = "docs/agents/issue-tracker.md"


def make_repo(files: dict | None = None, onboarded: bool = True):
    """A throwaway target repository holding *files* (relative path ->
    content). Onboarded unless told otherwise: its tracker file carries
    the `## Refactoring operations` section."""
    files = dict(files or {})
    if onboarded:
        files.setdefault(TRACKER_FILE, "# Issue tracker\n\n## Refactoring operations\n\n- **Search:** `gh issue list`\n")
    tmp = tempfile.TemporaryDirectory()
    root = pathlib.Path(tmp.name)
    for rel, content in files.items():
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content)
    (root / ".git").mkdir()
    return tmp, root


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


class AggregationStateTests(unittest.TestCase):
    """An aggregation node — one others reach through `resolved` edges
    (`php-safety-net`, `structural-scan`) — is fulfilled once every leaf
    feeding it is fulfilled or rejected. The parser works that out; what
    the caller hands in for such a node is ignored."""

    PHP_LEAVES = [
        "psr-4", "phpunit", "phpstan-level-5", "rector-dead-code",
        "rector-type-coverage", "rector-php-set", "rector-code-quality",
        "rector-phpunit-set", "psalm-taint-analysis",
    ]
    BASE = {"is-php-project": True, "composer": True}

    def setUp(self):
        tmp, self.root = make_repo()
        self.addCleanup(tmp.cleanup)

    def _fulfilled(self, **state):
        data = tooling_tree.detect_and_roadmap(self.root, **state)
        return {n: d["fulfilled"] for n, d in data["detected"].items()}

    def test_fulfilled_once_every_leaf_is_fulfilled(self):
        leaves = {leaf: True for leaf in self.PHP_LEAVES}
        state = self._fulfilled(fulfilled={**self.BASE, **leaves, "phpunit": False})
        self.assertFalse(state["php-safety-net"])
        state = self._fulfilled(fulfilled={**self.BASE, **leaves})
        self.assertTrue(state["php-safety-net"])
        # structural-scan reads php-safety-net and its own two leaves
        self.assertFalse(state["structural-scan"])
        state = self._fulfilled(fulfilled={**self.BASE, **leaves, "editorconfig": True, "ci-runner": True})
        self.assertTrue(state["structural-scan"])

    def test_handed_in_state_of_an_aggregation_node_is_ignored(self):
        state = self._fulfilled(fulfilled={**self.BASE, "php-safety-net": True, "structural-scan": True})
        self.assertFalse(state["php-safety-net"])
        self.assertFalse(state["structural-scan"])
        leaves = {leaf: True for leaf in self.PHP_LEAVES}
        data = tooling_tree.detect_and_roadmap(
            self.root,
            fulfilled={**self.BASE, **leaves, "php-safety-net": False},
            rejected={"php-safety-net", "structural-scan"},
        )
        self.assertTrue(data["detected"]["php-safety-net"]["fulfilled"])
        # a rejected required parent would have closed semgrep
        self.assertEqual(data["closed_by_rejection"], [])
        self.assertIn("semgrep", data["backlog"])

    def test_a_rejected_leaf_counts_as_decided(self):
        leaves = {leaf: True for leaf in self.PHP_LEAVES if leaf != "psalm-taint-analysis"}
        state = self._fulfilled(fulfilled={**self.BASE, **leaves}, rejected={"psalm-taint-analysis"})
        self.assertTrue(state["php-safety-net"])
        state = self._fulfilled(
            fulfilled={**self.BASE, **leaves, "editorconfig": True},
            rejected={"psalm-taint-analysis", "ci-runner"},
        )
        self.assertTrue(state["structural-scan"])

    def test_a_leaf_closed_by_a_rejected_required_parent_counts_as_decided(self):
        # composer rejected: every PHP leaf sits behind it
        state = self._fulfilled(fulfilled={"is-php-project": True}, rejected={"composer"})
        self.assertTrue(state["php-safety-net"])

    def test_computed_state_opens_the_nodes_behind_the_gate(self):
        leaves = {leaf: True for leaf in self.PHP_LEAVES}
        waiting = {**self.BASE, "ci-runner": True, "phpunit": False, **{leaf: True for leaf in self.PHP_LEAVES if leaf != "phpunit"}}
        nodes = [c["node"] for c in next_candidates(self.root, fulfilled=waiting)]
        self.assertNotIn("semgrep", nodes)
        reasons = {w["node"]: w["reason"] for w in withheld_with_reasons(self.root, fulfilled=waiting)}
        self.assertEqual(reasons["semgrep"], "blocked by required parent php-safety-net")
        nodes = [c["node"] for c in next_candidates(self.root, fulfilled={**self.BASE, "ci-runner": True, **leaves})]
        self.assertIn("semgrep", nodes)


class EffectivelyRejectedRequiredAnyTests(unittest.TestCase):
    """Ticket 53: `_is_effectively_rejected` closes the child of a
    `required-any` parent group only once no option in the group could
    still fulfil it, never on a single rejected option alone while another
    could (`StrandedRequiredAnyTests` has the option that is a
    recognition-only node). Unit
    tests directly against the function (same precedent as `_is_unblocked`
    being called directly elsewhere in this file) -- `rector-php-set`'s real
    `required-any(phpstan-level-0, psalm)` gate is the concrete case."""

    def test_single_required_any_option_rejected_does_not_close(self):
        tree = load_tree()
        # the other option can still fulfil it: psalm is in use (see
        # StrandedRequiredAnyTests for the target without psalm)
        rejected = {"phpstan-level-0"}
        self.assertFalse(tooling_tree._is_effectively_rejected(
            "rector-php-set", tree, rejected, fulfilled_lookup={"psalm": True}.get,
        ))
        self.assertFalse(tooling_tree._is_effectively_rejected("rector-php-set", tree, {"psalm"}))

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
    """A node handed in as rejected stays out of next_candidates() even
    once its required parents are fulfilled -- until the caller stops
    handing it in as rejected."""

    FULFILLED = {
        "git": True, "onboarding-setup": True, "is-php-project": True,
        "composer": True, "static-code-analyzer": True, "editorconfig": True,
    }

    def test_rejected_node_not_in_next_candidates_even_with_fulfilled_parents(self):
        tmp, root = make_repo()
        try:
            self.assertIn("phpunit", [c["node"] for c in next_candidates(root, fulfilled=self.FULFILLED)])
            nodes = [c["node"] for c in next_candidates(root, fulfilled=self.FULFILLED, rejected={"phpunit"})]
            self.assertNotIn("phpunit", nodes)
        finally:
            tmp.cleanup()

    def test_unrejected_sibling_still_proposed(self):
        tmp, root = make_repo()
        try:
            nodes = [c["node"] for c in next_candidates(root, fulfilled=self.FULFILLED, rejected={"php-cs-fixer"})]
            self.assertNotIn("php-cs-fixer", nodes)
            self.assertIn("phpunit", nodes)
        finally:
            tmp.cleanup()


class RecommendedGateTests(unittest.TestCase):
    """ADR-0016: a `recommended` edge now withholds its child from
    next_candidates() until every recommended parent is decided — fulfilled
    or rejected, released either way. Unlike a `required` edge, which only
    ever releases the child on fulfilment and instead cascades a rejection,
    a decided-rejected recommended parent still releases the child."""

    # phpstan-level-0 fulfilled (unblocks rector-php-set via its required-any
    # gate); php-cs-fixer and phpstan-level-3 both stay undecided (neither
    # fulfilled nor rejected). editorconfig fulfilled (php-cs-fixer's own
    # recommended parent) so php-cs-fixer itself stays proposable — its
    # undecided status under test is about rector-dead-code's gate, not
    # php-cs-fixer's own. rector-type-coverage is gated by
    # rector-dead-code/rector-code-quality as recommended parents, alongside
    # php-cs-fixer/phpstan-level-3.
    P0 = {
        "git": True, "onboarding-setup": True, "is-php-project": True,
        "composer": True, "static-code-analyzer": True,
        "phpstan-level-0": True, "rector-php-set": True, "editorconfig": True,
        "phpstan-not-psalm": True, "phpstan-baseline-empty": True,
    }

    def setUp(self):
        tmp, self.root = make_repo()
        self.addCleanup(tmp.cleanup)

    def _next(self, fulfilled, rejected=None):
        return [c["node"] for c in next_candidates(self.root, fulfilled=fulfilled, rejected=rejected)]

    def test_child_withheld_while_recommended_parent_undecided(self):
        nodes = self._next(self.P0)
        self.assertIn("php-cs-fixer", nodes)  # the undecided parent itself is still proposable
        self.assertNotIn("rector-dead-code", nodes)

    def test_child_released_once_recommended_parent_rejected(self):
        self.assertIn("rector-dead-code", self._next(self.P0, rejected={"php-cs-fixer"}))

    def test_child_released_once_recommended_parent_fulfilled(self):
        self.assertIn("rector-dead-code", self._next({**self.P0, "php-cs-fixer": True}))

    def test_gate_waits_on_every_recommended_parent_not_just_one(self):
        # php-cs-fixer decided (fulfilled) but phpstan-level-3 not even
        # reached yet -> rector-type-coverage stays withheld: every one of
        # its recommended parents must be decided.
        self.assertNotIn("rector-type-coverage", self._next({**self.P0, "php-cs-fixer": True}))

    def test_cascade_rejection_of_required_ancestor_decides_recommended_parent(self):
        # phpstan-level-1 rejected -> phpstan-level-2/-3 permanently closed
        # via the required chain -> counts as phpstan-level-3 "decided" for
        # rector-type-coverage's recommended edge (php-cs-fixer is decided
        # here too, via fulfilment, so it isn't the thing under test).
        # rector-dead-code/rector-code-quality, its other recommended
        # parents, are decided here via rejection.
        nodes = self._next(
            {**self.P0, "php-cs-fixer": True},
            rejected={"phpstan-level-1", "rector-dead-code", "rector-code-quality"},
        )
        self.assertIn("rector-type-coverage", nodes)

    def test_withheld_candidates_names_the_waiting_on_parents(self):
        withheld = {w["node"]: set(w["waiting_on"]) for w in withheld_candidates(self.root, fulfilled=self.P0)}
        self.assertEqual(withheld["rector-dead-code"], {"php-cs-fixer"})
        self.assertEqual(
            withheld["rector-type-coverage"],
            {"rector-dead-code", "rector-code-quality", "php-cs-fixer", "phpstan-level-3"},
        )

    def test_next_candidates_uncapped_by_default(self):
        # More than five nodes genuinely unblocked at once — past the old
        # five-node cap ADR-0016 lifts.
        fulfilled = {**self.P0, "has-real-dependency": True}
        self.assertGreater(len(self._next(fulfilled)), 5)
        # limit is still honored when a caller explicitly wants one
        self.assertLessEqual(len(next_candidates(self.root, limit=3, fulfilled=fulfilled)), 3)


class GateNodeContractTests(unittest.TestCase):
    """The three recognition-gate nodes (`_NEVER_PROPOSED` — never proposed
    themselves) must keep their gated nodes out of ``next_candidates()``
    while seeded False, and release them once seeded True — the contract
    php-tooling-tree.md's `grd`/`pnp`/`pbe` gate rows exist for."""

    def test_baseline_empty_gate_false_keeps_phpstan_level_1_out(self):
        # phpstan-level-1's required parents: phpstan-level-0,
        # phpstan-not-psalm, phpstan-baseline-empty. The other two
        # fulfilled, the baseline gate seeded False is the sole thing
        # holding the node back; seeded True, it appears.
        seed = {
            "phpstan-level-0": True, "phpstan-not-psalm": True,
            "phpstan-baseline-empty": False,
        }
        tmp, root = make_repo({})
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
        tmp, root = make_repo({})
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
        # fulfilled — php-safety-net through its leaves — the dependency
        # gate seeded False is the sole blocker.
        seed = {
            "composer": True, "ci-runner": True,
            "has-real-dependency": False,
            **{leaf: True for leaf in AggregationStateTests.PHP_LEAVES},
        }
        tmp, root = make_repo({})
        try:
            nodes = [c["node"] for c in next_candidates(root, fulfilled=seed)]
            self.assertNotIn("composer-audit", nodes)
            nodes = [c["node"] for c in next_candidates(root, fulfilled={**seed, "has-real-dependency": True})]
            self.assertIn("composer-audit", nodes)
        finally:
            tmp.cleanup()


class PhpVersionReversalTests(unittest.TestCase):
    """A rejection handed in with a minimum-PHP-version blocker is reported
    for reversal once the target's PHP floor meets it. The parser only
    reports; the node stays rejected until the caller reverses it."""

    COMPOSER_DONE = {"onboarding-setup": True, "is-php-project": True, "composer": True, "static-code-analyzer": True}

    def test_rejection_blocked_by_a_php_version_the_target_now_meets_is_reported_for_reversal(self):
        tmp, root = make_repo({"composer.json": json.dumps({"require": {"php": ">=7.2"}})})
        try:
            rejected = {
                "phpunit": {"php": "7.0"},      # met by 7.2
                "phpmd": {"php": ">=8.1"},      # not met yet
                "php-cs-fixer": None,           # rejected for a reason no version change lifts
            }
            findings = php_version_reversal_findings(root, rejected)
            self.assertEqual([f["node"] for f in findings], ["phpunit"])
            self.assertIn("7.2", findings[0]["reason"])
            data = tooling_tree.detect_and_roadmap(root, fulfilled=self.COMPOSER_DONE, rejected=rejected)
            self.assertEqual([f["node"] for f in data["reversals"]], ["phpunit"])
            # still rejected until the caller reverses it
            self.assertNotIn("phpunit", data["backlog"])
        finally:
            tmp.cleanup()

    def test_rejections_without_a_blocker_are_never_reported(self):
        tmp, root = make_repo({"composer.json": json.dumps({"require": {"php": ">=8.1"}})})
        try:
            self.assertEqual(php_version_reversal_findings(root, {"phpunit", "phpmd"}), [])
            self.assertEqual(php_version_reversal_findings(root), [])
        finally:
            tmp.cleanup()

    def test_uses_platform_pin_over_require_when_present(self):
        tmp, root = make_repo({
            "composer.json": json.dumps({
                "require": {"php": ">=8.1"},
                "config": {"platform": {"php": "7.2.34"}},
            }),
        })
        try:
            findings = php_version_reversal_findings(root, {"phpunit": {"php": "7.0"}, "phpmd": {"php": "8.0"}})
            self.assertEqual([f["node"] for f in findings], ["phpunit"])
        finally:
            tmp.cleanup()


class PhpFloorPrecheckTests(unittest.TestCase):
    """Ticket 31: the target's current PHP floor is checked once against each
    of the five deterministic PHP tooling leaves' known minimum-ever PHP
    version, instead of proposing/rejecting each one individually. Design
    decision (see `php_floor_precheck`'s docstring): skip silently, the
    leaf is neither fulfilled nor rejected."""

    def test_no_composer_json_blocks_nothing(self):
        tmp, root = make_repo({})
        try:
            self.assertEqual(php_floor_precheck(root), [])
        finally:
            tmp.cleanup()

    def test_modern_floor_blocks_nothing(self):
        tmp, root = make_repo({
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
        tmp, root = make_repo({
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
        tmp, root = make_repo({
            "composer.json": json.dumps({"require": {"php": ">=7.0"}}),
            "composer.lock": "{}",
        })
        try:
            blocked = {b["node"] for b in php_floor_precheck(root)}
            self.assertEqual(blocked, {"composer-audit"})
        finally:
            tmp.cleanup()

    def test_very_old_floor_blocks_all_five_leaves(self):
        tmp, root = make_repo({
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
        tmp, root = make_repo({
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
        tmp, root = make_repo({
            "composer.json": json.dumps({"require": {"php": ">=5.6"}}),
            "composer.lock": "{}",
            ".github/workflows/ci.yml": "jobs:\n  lint:\n    steps:\n      - run: php -l\n",
        })
        fulfilled = {
            "git": True, "onboarding-setup": True, "is-php-project": True,
            "composer": True, "static-code-analyzer": True,
            # decided, so php-cs-fixer's own recommended gate doesn't
            # interfere with what this test actually exercises.
            "editorconfig": True,
        }
        try:
            nodes = [c["node"] for c in next_candidates(root, fulfilled=fulfilled)]
            self.assertNotIn("composer-audit", nodes)
            self.assertNotIn("phpstan-level-0", nodes)
            # php-cs-fixer and test-runner-if-missing are PHP-5.6-compatible
            # and unblocked (required parents fulfilled) — still proposed.
            self.assertIn("php-cs-fixer", nodes)
            self.assertIn("test-runner-if-missing", nodes)
        finally:
            tmp.cleanup()

    def test_next_candidates_never_proposes_blocked_leaves(self):
        tmp, root = make_repo({
            "composer.json": json.dumps({"require": {"php": ">=5.6"}}),
            "composer.lock": "{}",
            ".github/workflows/ci.yml": "jobs:\n  lint:\n    steps:\n      - run: php -l\n",
        })
        try:
            nodes = [c["node"] for c in next_candidates(root)]
            self.assertNotIn("composer-audit", nodes)
            self.assertNotIn("phpstan-level-0", nodes)
        finally:
            tmp.cleanup()

    def test_detect_and_roadmap_reports_php_floor_blocked(self):
        tmp, root = make_repo({
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
    """ordered_backlog() returns the complete ordered list of the nodes
    neither fulfilled nor rejected, in tree order, blocked nodes included —
    the nodes a scan offers tickets for."""

    def setUp(self):
        tmp, self.root = make_repo()
        self.addCleanup(tmp.cleanup)

    def test_backlog_of_a_target_not_onboarded_holds_no_node_of_the_parsers_own(self):
        tmp, root = make_repo(onboarded=False)
        self.addCleanup(tmp.cleanup)
        backlog = ordered_backlog(root)
        self.assertEqual(backlog[:2], ["ci-runner", "editorconfig"])
        self.assertNotIn("onboarding-setup", backlog)
        self.assertNotIn("git", backlog)

    def test_backlog_excludes_fulfilled_nodes(self):
        backlog = ordered_backlog(self.root, fulfilled={"onboarding-setup": True, "is-php-project": True, "composer": True})
        self.assertNotIn("onboarding-setup", backlog)
        self.assertNotIn("composer", backlog)

    def test_backlog_excludes_rejected_nodes(self):
        self.assertIn("phpunit", ordered_backlog(self.root))
        self.assertNotIn("phpunit", ordered_backlog(self.root, rejected={"phpunit"}))

    def test_backlog_includes_blocked_nodes(self):
        self.assertIn("composer", ordered_backlog(self.root))


class TicketableNodesTests(unittest.TestCase):
    """Backlog, node lists and `next` hold only nodes a ticket can be filed
    for. The nodes the parser settles itself, the recognition-only nodes
    and the aggregation nodes are in none of them."""

    NEVER_LISTED = {
        "git", "onboarding-setup", "is-php-project", "structural-scan",
        "php-safety-net", "static-code-analyzer", "psalm",
        "has-real-dependency", "phpstan-baseline-empty", "phpstan-not-psalm",
    }

    def _listed(self, data):
        listed = set(data["backlog"]) | {c["node"] for c in data["next"]}
        for track in data["tracks"].values():
            listed |= set(track["backlog"]) | {n["node"] for n in track["nodes"]}
        return listed

    def test_nothing_unticketable_is_listed_whatever_the_state(self):
        leaves = {leaf: True for leaf in AggregationStateTests.PHP_LEAVES}
        for onboarded, fulfilled in (
            (False, None),
            (True, None),
            (True, {"is-php-project": True, "composer": True, "static-code-analyzer": True}),
            # both gates fulfilled: structural-scan is still no candidate
            (True, {"is-php-project": True, "composer": True, "editorconfig": True, "ci-runner": True, **leaves}),
        ):
            tmp, root = make_repo(onboarded=onboarded)
            self.addCleanup(tmp.cleanup)
            data = tooling_tree.detect_and_roadmap(root, fulfilled=fulfilled)
            self.assertEqual(self._listed(data) & self.NEVER_LISTED, set(), fulfilled)

    def test_every_other_node_is_listed_in_exactly_one_track_in_tree_order(self):
        tree = load_tree()
        tracks = tooling_tree.track_nodes(tree)
        listed = [n["node"] for nodes in tracks.values() for n in nodes]
        self.assertEqual(sorted(listed), sorted(set(tree["nodes"]) - self.NEVER_LISTED))
        for nodes in tracks.values():
            slugs = [n["node"] for n in nodes]
            self.assertEqual(slugs, [n for n in tree["order"] if n in slugs])


class TrackFulfilledTests(unittest.TestCase):
    """The output says per Track whether it is fulfilled: every node of it
    a ticket can be filed for is fulfilled or rejected."""

    def setUp(self):
        tmp, self.root = make_repo()
        self.addCleanup(tmp.cleanup)
        self.tracks = tooling_tree.track_nodes(load_tree())

    def _fulfilled(self, **state):
        data = tooling_tree.detect_and_roadmap(self.root, **state)
        return {track: entry["fulfilled"] for track, entry in data["tracks"].items()}

    def _all(self, track, but=()):
        return {n["node"]: True for n in self.tracks[track] if n["node"] not in but}

    def test_nothing_decided_means_no_track_fulfilled(self):
        self.assertEqual(self._fulfilled(), {"Safety Net": False, "Guardrails": False})

    def test_safety_net_fulfilled_once_each_of_its_nodes_is_fulfilled_or_rejected(self):
        # nothing handed in for the gates or the recognition-only nodes
        self.assertEqual(
            self._fulfilled(fulfilled=self._all("Safety Net")),
            {"Safety Net": True, "Guardrails": False},
        )
        one_open = self._all("Safety Net", but={"php-cs-fixer"})
        self.assertFalse(self._fulfilled(fulfilled=one_open)["Safety Net"])
        self.assertTrue(self._fulfilled(fulfilled=one_open, rejected={"php-cs-fixer"})["Safety Net"])

    def test_a_node_closed_by_a_rejected_required_parent_counts_as_rejected(self):
        # phpstan-level-0 rejected closes the level chain behind it
        levels = {f"phpstan-level-{n}" for n in range(6)}
        state = self._all("Safety Net", but=levels)
        self.assertFalse(self._fulfilled(fulfilled=state)["Safety Net"])
        self.assertTrue(self._fulfilled(fulfilled=state, rejected={"phpstan-level-0"})["Safety Net"])

    def test_guardrails_fulfilled_independently(self):
        state = {**self._all("Safety Net"), **self._all("Guardrails")}
        self.assertEqual(self._fulfilled(fulfilled=state), {"Safety Net": True, "Guardrails": True})

    def test_the_flag_is_in_the_command_line_output(self):
        import subprocess
        import sys
        proc = subprocess.run([sys.executable, tooling_tree.__file__, str(self.root)], capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIs(json.loads(proc.stdout)["tracks"]["Safety Net"]["fulfilled"], False)


class WithheldWithReasonsTests(unittest.TestCase):
    """withheld_with_reasons() names every node held back and why."""

    FULFILLED = {
        "git": True, "onboarding-setup": True, "is-php-project": True,
        "composer": True, "static-code-analyzer": True,
        "phpstan-level-0": True, "rector-php-set": True,
        "phpstan-not-psalm": True, "phpstan-baseline-empty": True,
    }

    def setUp(self):
        tmp, self.root = make_repo()
        self.addCleanup(tmp.cleanup)

    def test_withheld_with_undecided_recommended_parent(self):
        reasons = {w["node"]: w["reason"] for w in withheld_with_reasons(self.root, fulfilled=self.FULFILLED)}
        self.assertEqual(reasons["rector-dead-code"], "waiting on: php-cs-fixer")
        self.assertEqual(reasons["php-cs-fixer"], "waiting on: editorconfig")

    def test_blocked_node_names_its_required_parent(self):
        reasons = {w["node"]: w["reason"] for w in withheld_with_reasons(self.root, fulfilled=self.FULFILLED)}
        self.assertEqual(reasons["phpstan-level-2"], "blocked by required parent phpstan-level-1")

    def test_node_below_its_php_floor_names_the_floor(self):
        tmp, root = make_repo({"composer.json": json.dumps({"require": {"php": ">=5.6"}})})
        self.addCleanup(tmp.cleanup)
        data = tooling_tree.detect_and_roadmap(root, fulfilled=self.FULFILLED | {"phpstan-level-0": False})
        self.assertIn("phpstan-level-0", data["backlog"])
        self.assertIn(
            {"node": "phpstan-level-0", "reason": "PHP floor 5.6 below phpstan-level-0's minimum PHP >= 7.0"},
            data["tracks"]["Safety Net"]["withheld"],
        )
        # still not a candidate, and not "waiting on" a recommended parent
        self.assertNotIn("phpstan-level-0", [c["node"] for c in data["next"]])
        self.assertNotIn("phpstan-level-0", [w["node"] for w in data["withheld"]])

    def test_rejected_recommended_parent_no_longer_withholds(self):
        withheld = withheld_with_reasons(self.root, fulfilled=self.FULFILLED, rejected={"php-cs-fixer"})
        self.assertNotIn("rector-dead-code", {w["node"] for w in withheld})


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


class SeedFileTests(unittest.TestCase):
    """On the command line the node state arrives as a seed file:
    ``{"fulfilled": [slug, ...], "rejected": {slug: null | {"php": "X.Y"}}}``."""

    def _run(self, root, *args):
        import subprocess
        import sys
        return subprocess.run(
            [sys.executable, tooling_tree.__file__, *args, str(root)],
            capture_output=True, text=True,
        )

    def test_seed_file_drives_the_output(self):
        tmp, root = make_repo({
            "composer.json": json.dumps({"require": {"php": ">=7.4"}}),
            "state.json": json.dumps({
                "fulfilled": ["onboarding-setup", "is-php-project", "composer", "static-code-analyzer", "editorconfig"],
                "rejected": {"phpunit": {"php": "7.2"}, "psr-4": None},
            }),
        })
        self.addCleanup(tmp.cleanup)
        proc = self._run(root, "--seed", str(root / "state.json"))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        data = json.loads(proc.stdout)
        nodes = [c["node"] for c in data["next"]]
        self.assertIn("php-cs-fixer", nodes)
        self.assertNotIn("phpunit", nodes)
        self.assertNotIn("psr-4", nodes)
        for gone in ("composer", "editorconfig", "phpunit", "psr-4", "coverage-floor"):
            self.assertNotIn(gone, data["backlog"])
        self.assertIn("coverage-floor", data["closed_by_rejection"])  # requires the rejected phpunit
        self.assertEqual([f["node"] for f in data["reversals"]], ["phpunit"])
        self.assertIn(
            {"node": "php-cs-fixer", "name": "PHP CS Fixer", "tool": "php-cs-fixer", "search": ["PHP CS Fixer", "php-cs-fixer"]},
            data["tracks"]["Safety Net"]["nodes"],
        )

    def test_rejected_may_be_a_plain_list(self):
        tmp, root = make_repo({"state.json": json.dumps({"rejected": ["composer"]})})
        self.addCleanup(tmp.cleanup)
        data = tooling_tree.detect_and_roadmap(root, seed_path=root / "state.json")
        self.assertIn("phpunit", data["closed_by_rejection"])
        self.assertNotIn("composer", data["backlog"])

    def test_without_a_seed_every_node_is_undecided(self):
        tmp, root = make_repo({".scratch/refactor/fulfilled-set.json": json.dumps({"onboarding-setup": True})}, onboarded=False)
        self.addCleanup(tmp.cleanup)
        proc = self._run(root)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        data = json.loads(proc.stdout)
        self.assertEqual(data["next"], [])
        self.assertFalse(data["detected"]["onboarding-setup"]["fulfilled"])
        self.assertIn({"node": "ci-runner", "reason": "blocked by required parent onboarding-setup"}, data["withheld_with_reasons"])

    def test_a_seed_may_say_anything_about_the_nodes_the_parser_settles_itself(self):
        tmp, root = make_repo({"state.json": json.dumps({
            "fulfilled": ["structural-scan", "php-safety-net", "git"],
            "rejected": {"structural-scan": None, "php-safety-net": {"php": "8.1"}, "onboarding-setup": None},
        })})
        self.addCleanup(tmp.cleanup)
        data = tooling_tree.detect_and_roadmap(root, seed_path=root / "state.json")
        self.assertFalse(data["detected"]["structural-scan"]["fulfilled"])
        self.assertFalse(data["detected"]["php-safety-net"]["fulfilled"])
        self.assertTrue(data["detected"]["onboarding-setup"]["fulfilled"])
        self.assertEqual(data["closed_by_rejection"], [])

    def test_unblocked_by_reads_the_seed(self):
        tmp, root = make_repo({"state.json": json.dumps({
            "fulfilled": ["onboarding-setup", "is-php-project", "composer", "static-code-analyzer"],
            "rejected": ["psr-4"],
        })})
        self.addCleanup(tmp.cleanup)
        proc = self._run(root, "--seed", str(root / "state.json"), "--unblocked-by", "composer")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(
            {c["node"] for c in json.loads(proc.stdout)["unblocked_by"]},
            {"phpunit", "test-runner-if-missing", "phpstan-level-0"},
        )

    def test_seed_that_cannot_be_used_raises(self):
        # A seed is the caller's judgement: when it can't be used as given,
        # fail loudly instead of answering from a different state.
        unusable = {
            "broken.json": "{not json",
            "list.json": "[]",
            "old-shape.json": '{"composer": true}',
            "fulfilled-not-a-list.json": '{"fulfilled": {"composer": true}}',
            "blocker-not-an-object.json": '{"rejected": {"phpmd": "PHP 8.1"}}',
            "blocker-without-version.json": '{"rejected": {"phpmd": {"php": "newer"}}}',
            "blocker-a-number.json": '{"rejected": {"phpmd": {"php": 8.10}}}',
            "both.json": '{"fulfilled": ["phpmd"], "rejected": ["phpmd"]}',
            "unknown-node.json": '{"fulfilled": ["phpunti"]}',
        }
        tmp, root = make_repo(unusable)
        self.addCleanup(tmp.cleanup)
        for name in ("missing.json", *unusable):
            with self.assertRaises(tooling_tree.SeedError, msg=name):
                tooling_tree.detect_and_roadmap(root, seed_path=root / name)

    def test_cli_exits_nonzero_on_unusable_seed(self):
        tmp, root = make_repo({"typo.json": '{"fulfilled": ["phpunti"]}'})
        self.addCleanup(tmp.cleanup)
        for name, needle in (("missing.json", "missing.json"), ("typo.json", "phpunti")):
            proc = self._run(root, "--seed", str(root / name))
            self.assertEqual(proc.returncode, 2, name)
            self.assertEqual(proc.stdout, "")
            self.assertIn(needle, proc.stderr)


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

    def test_multi_child_fan_out_from_composer(self):
        # composer alone (no phpunit/cs-fixer/CI configured yet) unblocks
        # four siblings at once: phpunit, test-runner-if-missing, and psr-4
        # directly, phpstan-level-0 through the static-code-analyzer
        # walk-through (a pure organizational node, never itself reported).
        # ticket 63: phpmd no longer shows up here -- it additionally
        # requires php-safety-net now (unfulfilled in this bare fixture), so
        # composer alone is no longer sufficient to unblock it.
        tmp, root = make_repo({
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
        tmp, root = make_repo({
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

    def test_walks_through_the_aggregation_nodes_to_what_they_open(self):
        # phpunit is the last undecided leaf: landing it fulfils
        # php-safety-net and, behind it, structural-scan. Neither is
        # reported; the nodes waiting on them are.
        others = [leaf for leaf in AggregationStateTests.PHP_LEAVES if leaf != "phpunit"]
        fulfilled = {
            "is-php-project": True, "composer": True, "phpunit": True,
            "editorconfig": True, "ci-runner": True,
        }
        tmp, root = make_repo()
        try:
            got = {c["node"] for c in directly_unblocked_children(root, "phpunit", fulfilled=fulfilled, rejected=set(others))}
            self.assertEqual(got, {"phpmd", "coverage-floor", "semgrep", "secret-detection"})
        finally:
            tmp.cleanup()

    def test_unknown_landed_node_returns_empty(self):
        tmp, root = make_repo({})
        try:
            self.assertEqual(directly_unblocked_children(root, "not-a-real-node"), [])
        finally:
            tmp.cleanup()

    def test_no_children_when_nothing_new(self):
        # Empty repo: onboarding-setup isn't fulfilled, so forcing it "unfulfilled"
        # in the counterfactual changes nothing real -- no children to report.
        tmp, root = make_repo(onboarded=False)
        try:
            self.assertEqual(directly_unblocked_children(root, "onboarding-setup"), [])
        finally:
            tmp.cleanup()
class BacklogOrderTests(unittest.TestCase):
    """The backlog is complete and ordered: blocked nodes included, in
    tree order."""

    def setUp(self):
        tmp, self.root = make_repo()
        self.addCleanup(tmp.cleanup)

    def test_backlog_includes_blocked_nodes_in_order(self):
        backlog = ordered_backlog(self.root, fulfilled={
            "git": True, "onboarding-setup": True, "is-php-project": True,
            "composer": True, "static-code-analyzer": True,
        })
        self.assertNotIn("onboarding-setup", backlog)
        self.assertNotIn("composer", backlog)
        self.assertIn("phpunit", backlog)
        self.assertIn("psr-4", backlog)
        # rector-dead-code is blocked (rector-php-set unfulfilled) and still
        # listed, after phpunit as in the tree's edge order.
        self.assertLess(backlog.index("phpunit"), backlog.index("rector-dead-code"))

    def test_handed_in_fulfilment_drives_the_backlog(self):
        seed = {
            "git": True, "onboarding-setup": True, "is-php-project": True,
            "composer": True, "editorconfig": True,
            "phpunit": True, "psr-4": True, "phpstan-level-0": True,
            "phpstan-level-1": True, "phpstan-level-2": True,
            "phpstan-level-3": True, "phpstan-level-4": True,
            "phpstan-level-5": True,
        }
        backlog = ordered_backlog(self.root, fulfilled=seed)
        self.assertNotIn("phpunit", backlog)
        self.assertNotIn("phpstan-level-0", backlog)
        self.assertNotIn("phpstan-level-5", backlog)
        self.assertIn("rector-dead-code", backlog)

    def test_empty_backlog_when_everything_resolved(self):
        tree = load_tree()
        seed = {n: True for n in tree["nodes"] if n not in tooling_tree._NEVER_PROPOSED}
        self.assertEqual(ordered_backlog(self.root, fulfilled=seed), [])


class RejectionCascadeTests(unittest.TestCase):
    """Every node closed by a rejected required ancestor leaves the
    backlog; handing the ancestor in as no longer rejected brings them
    back."""

    def setUp(self):
        tmp, self.root = make_repo()
        self.addCleanup(tmp.cleanup)

    def test_rejected_composer_removes_descendants_from_backlog(self):
        closed = closed_by_rejection(load_tree(), {"composer"})
        for node in ("php-cs-fixer", "phpunit", "rector-dead-code", "phpstan-level-0"):
            self.assertIn(node, closed)
        backlog = ordered_backlog(self.root, rejected={"composer"})
        for node in ("composer", "php-cs-fixer", "phpunit", "rector-dead-code"):
            self.assertNotIn(node, backlog)

    def test_reversal_brings_nodes_back(self):
        self.assertNotIn("phpunit", ordered_backlog(self.root, rejected={"composer"}))
        self.assertIn("phpunit", ordered_backlog(self.root, rejected=set()))

    def test_partial_rejection_only_closes_required_descendants(self):
        backlog = ordered_backlog(self.root, rejected={"phpstan-level-2"})
        # levels 3, 4, 5 are closed with it (required chain through level 2)
        for level in (2, 3, 4, 5):
            self.assertNotIn(f"phpstan-level-{level}", backlog)
        # siblings that don't depend on phpstan-level-2 remain
        self.assertIn("phpunit", backlog)
        self.assertIn("psr-4", backlog)
        self.assertIn("phpstan-level-1", backlog)


class StrandedRequiredAnyTests(unittest.TestCase):
    """A node whose whole `required-any` group is out of reach — each
    member rejected, closed by a rejection, or a recognition-only node that
    is not fulfilled — is closed by the rejection, like the child of a
    rejected required parent. `rector-php-set` hangs on `phpstan-level-0`
    or the recognition-only `psalm`, `psalm-taint-analysis` on
    `phpstan-level-4` or `psalm`."""

    BASE = {"is-php-project": True, "composer": True, "static-code-analyzer": True}
    STRANDED = ("rector-php-set", "psalm-taint-analysis")

    def _data(self, php=None, **state):
        files = {"composer.json": json.dumps({"require": {"php": php}})} if php else None
        tmp, root = make_repo(files)
        self.addCleanup(tmp.cleanup)
        return tooling_tree.detect_and_roadmap(root, **state)

    def test_group_out_of_reach_closes_the_node(self):
        data = self._data(fulfilled=self.BASE, rejected={"phpstan-level-0"})
        for node in self.STRANDED:
            self.assertIn(node, data["closed_by_rejection"])
            self.assertNotIn(node, data["backlog"])
            self.assertNotIn(node, data["tracks"]["Safety Net"]["backlog"])
        # and what requires a node closed this way is closed with it
        self.assertIn("rector-dead-code", data["closed_by_rejection"])
        self.assertNotIn("rector-dead-code", data["backlog"])

    def test_closed_node_counts_as_decided_for_its_aggregation_node(self):
        others = {"psr-4": True, "phpunit": True, "rector-type-coverage": True, "rector-phpunit-set": True}
        data = self._data(fulfilled={**self.BASE, **others}, rejected={"phpstan-level-0"})
        self.assertTrue(data["detected"]["php-safety-net"]["fulfilled"])

    def test_recognition_only_member_handed_in_as_fulfilled_closes_nothing(self):
        data = self._data(fulfilled={**self.BASE, "psalm": True}, rejected={"phpstan-level-0"})
        for node in self.STRANDED:
            self.assertNotIn(node, data["closed_by_rejection"])
            self.assertIn(node, data["backlog"])

    def test_member_still_open_closes_nothing(self):
        # psalm declined, phpstan-level-0 still to be set up
        data = self._data(fulfilled=self.BASE, rejected={"psalm"})
        self.assertEqual(data["closed_by_rejection"], [])
        for node in self.STRANDED:
            self.assertIn(node, data["backlog"])

    def test_unfulfilled_recognition_only_member_alone_closes_nothing(self):
        data = self._data(fulfilled=self.BASE)
        self.assertEqual(data["closed_by_rejection"], [])
        for node in self.STRANDED:
            self.assertIn(node, data["backlog"])

    def test_group_without_any_rejection_closes_nothing(self):
        # a group of recognition-only nodes alone: nothing was rejected, so
        # nothing is closed by a rejection
        tree = {
            "required_parents": {},
            "required_any_parents": {"child": ["psalm", "static-code-analyzer"], "other": ["psalm", "declined"]},
        }
        self.assertFalse(tooling_tree._is_effectively_rejected("child", tree, set()))
        self.assertFalse(tooling_tree._is_effectively_rejected("other", tree, set()))
        self.assertTrue(tooling_tree._is_effectively_rejected("other", tree, {"declined"}))

    def test_closure_follows_the_rejection(self):
        rejected = {"phpstan-level-0": {"php": "7.0"}}
        data = self._data(php=">=7.4", fulfilled=self.BASE, rejected=rejected)
        self.assertEqual([f["node"] for f in data["reversals"]], ["phpstan-level-0"])
        # still closed until the caller reverses the rejection
        for node in self.STRANDED:
            self.assertNotIn(node, data["backlog"])
        data = self._data(php=">=7.4", fulfilled=self.BASE, rejected={})
        self.assertEqual(data["closed_by_rejection"], [])
        for node in ("phpstan-level-0", *self.STRANDED):
            self.assertIn(node, data["backlog"])

    def test_php_floor_rejection_alone_opens_the_gate(self):
        """A PHP 5.6 target: `phpstan-level-0` is below its floor and
        rejected with that blocker, `psalm` is not fulfilled."""
        done = {
            "psr-4": True, "phpunit": True, "rector-type-coverage": True, "rector-phpunit-set": True,
            "editorconfig": True, "ci-runner": True,
        }
        data = self._data(php=">=5.6", fulfilled={**self.BASE, **done}, rejected={"phpstan-level-0": {"php": "7.0"}})
        self.assertTrue(data["detected"]["structural-scan"]["fulfilled"])
        self.assertEqual(data["reversals"], [])
        data = self._data(php=">=5.6", fulfilled={**self.BASE, **done})
        self.assertFalse(data["detected"]["structural-scan"]["fulfilled"])

    def test_functions_agree_with_the_output(self):
        tmp, root = make_repo()
        self.addCleanup(tmp.cleanup)
        tree = load_tree()
        closed = closed_by_rejection(tree, {"phpstan-level-0"}, fulfilled=self.BASE)
        backlog = ordered_backlog(root, fulfilled=self.BASE, rejected={"phpstan-level-0"})
        for node in self.STRANDED:
            self.assertIn(node, closed)
            self.assertNotIn(node, backlog)
        closed = closed_by_rejection(tree, {"phpstan-level-0"}, fulfilled={**self.BASE, "psalm": True})
        self.assertNotIn("rector-php-set", closed)


class HandedInStateTests(unittest.TestCase):
    """The caller hands in which nodes are fulfilled and which are rejected;
    the parser keeps no record of either and looks for none."""

    COMPOSER_DONE = {"onboarding-setup": True, "is-php-project": True, "composer": True, "static-code-analyzer": True}

    def test_handed_in_rejection_keeps_the_node_out(self):
        tmp, root = make_repo()
        try:
            nodes = [c["node"] for c in next_candidates(root, fulfilled=self.COMPOSER_DONE, rejected={"phpunit"})]
            self.assertNotIn("phpunit", nodes)
            self.assertIn("psr-4", nodes)
            self.assertNotIn("phpunit", ordered_backlog(root, fulfilled=self.COMPOSER_DONE, rejected={"phpunit"}))
        finally:
            tmp.cleanup()

    def test_without_state_every_node_is_undecided_whatever_the_old_files_say(self):
        # Everything the suite used to keep in a target: none of it is read.
        tmp, root = make_repo({
            ".scratch/refactor/fulfilled-set.json": json.dumps(self.COMPOSER_DONE),
            ".scratch/refactor/config.md": "**Bookkeeping:** notes/bookkeeping.md\n",
            ".scratch/refactor/bookkeeping.md": "## Safety Net\n\n**Open:**\n- none\n\n**Out-of-scope:**\n- none\n",
            ".scratch/refactor/out-of-scope/ci-runner.md": "rejected\n",
            "notes/bookkeeping.md": "## Safety Net\n\n**Open:**\n- none\n\n**Out-of-scope:**\n- none\n",
            "notes/out-of-scope/ci-runner.md": "rejected\n",
            "AGENTS.md": "Bookkeeping: `notes/bookkeeping.md`\n",
        }, onboarded=False)
        try:
            data = tooling_tree.detect_and_roadmap(root)
            self.assertEqual(data["next"], [])
            self.assertIn("ci-runner", data["backlog"])
            self.assertIn("composer", data["backlog"])
            self.assertEqual(data["closed_by_rejection"], [])
        finally:
            tmp.cleanup()


class OnboardingSetupTests(unittest.TestCase):
    """`onboarding-setup` is the one node the parser judges itself: it is
    fulfilled when the target's tracker file carries a
    `## Refactoring operations` section."""

    def _data(self, files, **state):
        tmp, root = make_repo(files, onboarded=False)
        self.addCleanup(tmp.cleanup)
        return tooling_tree.detect_and_roadmap(root, **state)

    def test_fulfilled_when_the_tracker_file_has_the_operations_section(self):
        data = self._data({TRACKER_FILE: "# Issue tracker\n\nGitHub.\n\n## Refactoring operations\n\n- **Search:** `gh issue list`\n"})
        self.assertNotIn("onboarding-setup", data["backlog"])
        self.assertTrue(data["detected"]["onboarding-setup"]["fulfilled"])
        self.assertEqual(
            [c["node"] for c in data["next"]],
            ["ci-runner", "editorconfig"],  # is-php-project, a gate, is never proposed
        )

    def test_not_fulfilled_without_a_tracker_file(self):
        data = self._data({})
        self.assertFalse(data["detected"]["onboarding-setup"]["fulfilled"])
        self.assertEqual(data["next"], [])  # everything waits behind it

    def test_the_caller_cannot_decide_it(self):
        data = self._data({}, fulfilled={"onboarding-setup": True})
        self.assertEqual(data["next"], [])
        self.assertFalse(data["detected"]["onboarding-setup"]["fulfilled"])
        section = {TRACKER_FILE: "## Refactoring operations\n"}
        data = self._data(section, fulfilled={"onboarding-setup": False}, rejected={"onboarding-setup", "git"})
        self.assertEqual([c["node"] for c in data["next"]], ["ci-runner", "editorconfig"])
        self.assertEqual(data["closed_by_rejection"], [])

    def test_not_fulfilled_when_the_tracker_file_lacks_the_section(self):
        data = self._data({TRACKER_FILE: "# Issue tracker\n\nGitHub. See Refactoring operations elsewhere.\n\n### Refactoring operations draft\n"})
        self.assertFalse(data["detected"]["onboarding-setup"]["fulfilled"])
        self.assertEqual(data["next"], [])


class TrackNodesTests(unittest.TestCase):
    """Per Track, the nodes with the name and tool their sections give.
    Which Track a node belongs to follows from the edges: everything
    behind a resolved-gated node is Guardrails, the rest Safety Net."""

    def test_nodes_carry_name_and_tool_from_their_sections(self):
        tracks = tooling_tree.track_nodes(load_tree())
        self.assertEqual(list(tracks), ["Safety Net", "Guardrails"])
        safety_net = {n["node"]: n for n in tracks["Safety Net"]}
        guardrails = {n["node"]: n for n in tracks["Guardrails"]}
        self.assertEqual(safety_net["phpunit"]["name"], "PHPUnit")
        self.assertEqual(safety_net["phpunit"]["tool"], "PHPUnit")
        self.assertEqual(safety_net["php-cs-fixer"]["tool"], "php-cs-fixer")
        self.assertEqual(guardrails["composer-audit"]["name"], "Composer Audit")
        # a section shared by a run of nodes names each of them
        self.assertEqual(safety_net["phpstan-level-4"]["name"], "PHPStan Level 4")
        self.assertEqual(guardrails["phpstan-level-10"]["name"], "PHPStan Level 10")
        self.assertEqual(guardrails["phpstan-level-10"]["tool"], "PHPStan")

    def test_nodes_carry_search_words(self):
        # name and tool, each once, as a tracker search would take them
        tracks = tooling_tree.track_nodes(load_tree())
        search = {n["node"]: n["search"] for nodes in tracks.values() for n in nodes}
        self.assertEqual(search["php-cs-fixer"], ["PHP CS Fixer", "php-cs-fixer"])
        self.assertEqual(search["phpunit"], ["PHPUnit"])
        self.assertEqual(search["composer-audit"], ["Composer Audit"])
        self.assertEqual(search["phpstan-level-0"], ["PHPStan Level 0", "PHPStan"])
        self.assertEqual(search["rector-dead-code"], ["Rector: Dead Code Set", "Rector"])
        self.assertEqual(search["editorconfig"], [".editorconfig", "EditorConfig"])
        self.assertEqual(search["semgrep"], ["Semgrep (OWASP Top 10)", "Semgrep"])
        # a node without a tool is searched by its name alone
        self.assertEqual(search["psr-4"], ["PSR-4 Autoloading"])

    def test_search_words_of_every_listed_node_are_short_and_plain(self):
        tracks = tooling_tree.track_nodes(load_tree())
        for node in (n for nodes in tracks.values() for n in nodes):
            self.assertTrue(node["name"], node)
            self.assertEqual(node["search"][0], node["name"], node)
            for word in node["search"]:
                self.assertNotRegex(word, r"[`—]|\.$", node)
                self.assertLessEqual(len(word), 30, node)
            if node["tool"] is not None:
                self.assertNotRegex(node["tool"], r"[()]", node)

    def test_fields_are_read_as_plain_text(self):
        tmp, root = make_repo({"tree.md": (
            "| from (parent) | to (child) | type |\n|---|---|---|\n"
            "| `git` | `dotfile` | required |\n"
            "| `git` | `convention` | required |\n"
            "| `git` | `wrapped` | required |\n"
            "| `git` | `bare` | required |\n"
            "\n### `dotfile`\n\n- **Name:** `.dotfile`\n- **Tool:** `dot` `--check`\n- **Purpose:** x\n"
            "\n### `convention`\n\n- **Name:** Convention\n- **Tool:** none\n"
            "\n### `wrapped`\n\n- **Name:** A Name Wrapped\n  Onto Two Lines\n- **Tool:** tool\n\nProse.\n"
        )})
        self.addCleanup(tmp.cleanup)
        nodes = {n["node"]: n for n in tooling_tree.track_nodes(load_tree(root / "tree.md"))["Safety Net"]}
        self.assertEqual(nodes["dotfile"], {"node": "dotfile", "name": ".dotfile", "tool": "dot --check", "search": [".dotfile", "dot --check"]})
        self.assertEqual(nodes["convention"], {"node": "convention", "name": "Convention", "tool": None, "search": ["Convention"]})
        self.assertEqual(nodes["wrapped"]["name"], "A Name Wrapped Onto Two Lines")
        # no node section in the tree doc
        self.assertEqual(nodes["bare"], {"node": "bare", "name": None, "tool": None, "search": []})

    def test_membership_follows_the_edges(self):
        tmp, root = make_repo({"tree.md": (
            "| from (parent) | to (child) | type |\n|---|---|---|\n"
            "| `git` | `linter` | required |\n"
            "| `linter` | `net` | resolved |\n"
            "| `net` | `auditor` | required |\n"
            "| `auditor` | `reporter` | recommended |\n"
            "| `auditor` | `strict-auditor` | required |\n"
            "\n### `linter`\n\n- **Name:** Linter\n- **Tool:** lint\n"
        )})
        self.addCleanup(tmp.cleanup)
        tracks = tooling_tree.track_nodes(load_tree(root / "tree.md"))
        # `git` is the parser's own and `net` an aggregation node: not listed
        self.assertEqual([n["node"] for n in tracks["Safety Net"]], ["linter", "reporter"])
        self.assertEqual([n["node"] for n in tracks["Guardrails"]], ["auditor", "strict-auditor"])

    def test_output_lists_nodes_backlog_and_withheld_reasons_per_track(self):
        tmp, root = make_repo()
        self.addCleanup(tmp.cleanup)
        data = tooling_tree.detect_and_roadmap(
            root,
            fulfilled={"onboarding-setup": True, "is-php-project": True, "composer": True, "static-code-analyzer": True},
            rejected={"phpmd"},
        )
        tracks = data["tracks"]
        self.assertEqual(list(tracks), ["Safety Net", "Guardrails"])
        self.assertIn({"node": "composer", "name": "Composer", "tool": "Composer", "search": ["Composer"]}, tracks["Safety Net"]["nodes"])
        self.assertIn({"node": "phpmd", "name": "PHPMD", "tool": "PHPMD", "search": ["PHPMD"]}, tracks["Guardrails"]["nodes"])
        # the two backlogs partition the overall one, order kept
        self.assertEqual(
            sorted(tracks["Safety Net"]["backlog"] + tracks["Guardrails"]["backlog"]),
            sorted(data["backlog"]),
        )
        self.assertEqual(tracks["Safety Net"]["backlog"][:4], ["ci-runner", "editorconfig", "psr-4", "php-cs-fixer"])
        self.assertIn("composer-audit", tracks["Guardrails"]["backlog"])
        self.assertNotIn("phpmd", tracks["Guardrails"]["backlog"])
        self.assertNotIn("composer", tracks["Safety Net"]["backlog"])
        self.assertIn(
            {"node": "php-cs-fixer", "reason": "waiting on: editorconfig"},
            tracks["Safety Net"]["withheld"],
        )
        self.assertIn(
            {"node": "composer-audit", "reason": "blocked by required parent php-safety-net"},
            tracks["Guardrails"]["withheld"],
        )


if __name__ == "__main__":
    unittest.main()
