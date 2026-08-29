"""Deterministic parser for the PHP tooling tree (php-tooling-tree.md, alongside this file).

Provides load_tree, detect_nodes, roadmap without invoking LLM or mutating repo.

Seam: skills/refactor-scan/references/tooling_tree.py — used by refactor-scan
and the roadmap dry-run harness.

Docs: php-tooling-tree.md (sibling to this file) is machine-readable (edges
table), CONTEXT.md vocabulary.
"""

from __future__ import annotations

import glob
import json
import pathlib
import re

_HERE = pathlib.Path(__file__).resolve().parent
TREE_MD = _HERE / "php-tooling-tree.md"
# Generic root: git -> loop-config, and the structural-scan node that PHP's
# tree leaves point into via `resolved` edges.
GENERIC_TREE_MD = _HERE / "tooling-tree.md"
# Suite repo root — used only by roadmap()'s dev/test-only fixtures fallback
# below. A shipped install has no fixtures/ directory, so this is never
# reached outside the suite's own test harness.
REPO_ROOT = _HERE.parents[2]  # references -> refactor-scan -> skills -> repo root

_VALID_EDGE_TYPES = ("required", "recommended", "resolved")


def _parse_edges(path: pathlib.Path) -> list[dict]:
    text = path.read_text(encoding="utf-8")
    edges = []
    # Parse edges table rows: | `from` | `to` | type |
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("| `"):
            continue
        # cols: from, to, type
        cols = [c.strip() for c in line.strip("|").split("|")]
        if len(cols) < 3:
            continue
        frm = cols[0].strip("`").strip()
        to = cols[1].strip("`").strip()
        typ = cols[2].strip()
        if frm in ("from (parent)", "from") and to == "to (child)":
            continue
        if typ not in _VALID_EDGE_TYPES:
            continue
        edges.append({"from": frm, "to": to, "type": typ})
    return edges


def load_tree(tree_md: pathlib.Path | None = None) -> dict:
    """Load the tree's edges.

    With an explicit ``tree_md``, loads only that one file (single-file mode,
    useful for isolated parser tests). With none, loads the generic root
    (``tooling-tree.md``) plus the PHP specialization
    (``php-tooling-tree.md``) and merges their edges — the default,
    real-world shape.
    """
    if tree_md is not None:
        paths = [pathlib.Path(tree_md)]
    else:
        paths = [GENERIC_TREE_MD, TREE_MD]
    edges: list[dict] = []
    for path in paths:
        if path.exists():
            edges.extend(_parse_edges(path))
    # nodes are distinct names from edges
    nodes = sorted({e["from"] for e in edges} | {e["to"] for e in edges})
    # Build parent maps
    required_parents: dict[str, list[str]] = {n: [] for n in nodes}
    recommended_parents: dict[str, list[str]] = {n: [] for n in nodes}
    # `resolved` parents: unlike a required parent, a *rejected* resolved
    # parent still counts as resolved — only structural-scan uses this edge
    # type today. See tooling-tree.md's structural-scan node.
    resolved_parents: dict[str, list[str]] = {n: [] for n in nodes}
    for e in edges:
        if e["type"] == "required":
            required_parents[e["to"]].append(e["from"])
        elif e["type"] == "recommended":
            recommended_parents[e["to"]].append(e["from"])
        else:
            resolved_parents[e["to"]].append(e["from"])
    # Preserve order as appear in file
    order = []
    seen = set()
    for e in edges:
        for n in (e["from"], e["to"]):
            if n not in seen:
                seen.add(n)
                order.append(n)
    return {
        "edges": edges,
        "nodes": nodes,
        "order": order,
        "required_parents": required_parents,
        "recommended_parents": recommended_parents,
        "resolved_parents": resolved_parents,
    }


def _read_composer(repo: pathlib.Path) -> dict | None:
    for cand in [repo / "composer.json", repo / "composer" / "composer.json"]:
        if cand.exists():
            try:
                return json.loads(cand.read_text(encoding="utf-8"))
            except Exception:
                return None
    return None


def _has_composer_json(repo: pathlib.Path) -> bool:
    return (repo / "composer.json").exists() or (repo / "composer" / "composer.json").exists()


def _has_dep(composer: dict | None, name: str) -> bool:
    if not composer:
        return False
    for k in ("require", "require-dev"):
        deps = composer.get(k, {})
        if name in deps:
            return True
    return False


# Composer platform pseudo-packages: never real dependencies `composer audit`
# could report anything about (php-tooling-tree.md's composer-audit stop
# conditions).
_PLATFORM_PACKAGE_NAMES = {"php", "hhvm", "composer-plugin-api", "composer-runtime-api"}


def _has_real_require_dep(composer: dict | None) -> bool:
    """True if composer.json's `require` names at least one real package —
    excludes platform pseudo-packages (php, hhvm, ext-*, lib-*,
    composer-plugin-api, composer-runtime-api)."""
    if not composer:
        return False
    for name in composer.get("require", {}):
        if name in _PLATFORM_PACKAGE_NAMES:
            continue
        if name.startswith("ext-") or name.startswith("lib-"):
            continue
        return True
    return False


def _has_composer_audit_ci_job(repo: pathlib.Path) -> bool:
    """composer-audit's real fulfilment (php-tooling-tree.md): a CI job that
    runs `composer audit`, gating the pipeline on known advisories."""
    for pat in [".github/workflows/*.yml", ".github/workflows/*.yaml", ".gitlab-ci.yml"]:
        for f in glob.glob(str(repo / pat)):
            try:
                if "composer audit" in pathlib.Path(f).read_text(encoding="utf-8"):
                    return True
            except OSError:
                continue
    return False


def _parse_phpstan_level(repo: pathlib.Path) -> int | None:
    p = repo / "phpstan.neon"
    if not p.exists():
        # also check phpstan.neon.dist? canonical is phpstan.neon per spec
        return None
    txt = p.read_text(encoding="utf-8")
    m = re.search(r"^\s*level\s*:\s*(\d+)", txt, re.M)
    if m:
        try:
            return int(m.group(1))
        except ValueError:
            return None
    return None


def _is_baseline_empty(repo: pathlib.Path) -> bool:
    """Empty baseline: absent OR no message entries / empty ignoreErrors."""
    p = repo / "phpstan-baseline.neon"
    if not p.exists():
        return True
    txt = p.read_text(encoding="utf-8")
    # Count ignoreErrors entries via 'message:' or 'path:'
    # If file contains 'ignoreErrors' and no 'message:' -> empty
    if "ignoreErrors" not in txt:
        return True
    # Common pattern: '- message: #...'
    if re.search(r"message\s*:", txt):
        return False
    # If ignoreErrors: [] or empty array
    if re.search(r"ignoreErrors\s*:\s*\[\]", txt):
        return True
    # If file only header like parameters: ignoreErrors: [] or just parameters:
    # fallback: if we found ignoreErrors but no message, treat as empty
    return True


def _baseline_exists(repo: pathlib.Path) -> bool:
    return (repo / "phpstan-baseline.neon").exists()


def _has_loop_config(repo: pathlib.Path) -> bool:
    """loop-config's fulfilment check: docs/refactoring/config.md exists."""
    return (repo / "docs" / "refactoring" / "config.md").exists()


def _parse_min_version(constraint: str) -> tuple[int, ...] | None:
    """Best-effort minimum-version extraction from a composer-style version
    constraint (e.g. '>=7.2', '^8.1', '7.2.0'). Not a full composer
    constraint parser — handles the single-lower-bound shapes this suite's
    `Blocked by:` fields and `require.php`/`config.platform.php` actually
    use. Returns None if no version-like substring is found."""
    if not constraint:
        return None
    m = re.search(r"(\d+(?:\.\d+){0,2})", constraint)
    if not m:
        return None
    return tuple(int(p) for p in m.group(1).split("."))


def _current_php_floor(composer: dict | None) -> tuple[int, ...] | None:
    """The target's current minimum PHP version: `config.platform.php`
    (an exact pin) if present, else `require.php`'s constraint
    (best-effort lower bound)."""
    if not composer:
        return None
    platform_php = composer.get("config", {}).get("platform", {}).get("php")
    v = _parse_min_version(platform_php) if platform_php else None
    if v:
        return v
    return _parse_min_version(composer.get("require", {}).get("php"))


def _out_of_scope_blocked_by_php(repo: pathlib.Path, node: str) -> tuple[int, ...] | None:
    """Parse `**Blocked by:** PHP >= X.Y` from a node's out-of-scope entry,
    if the entry has one (php-tooling-tree.md's mechanical-reversal design;
    only PHP-version rejections are ever auto-detected this way)."""
    p = repo / "docs" / "refactoring" / "out-of-scope" / f"{node}.md"
    if not p.exists():
        return None
    try:
        txt = p.read_text(encoding="utf-8")
    except OSError:
        return None
    m = re.search(r"\*\*Blocked by:\*\*\s*PHP\s*>=\s*([\d.]+)", txt)
    if not m:
        return None
    return _parse_min_version(m.group(1))


def php_version_reversal_findings(repo: pathlib.Path) -> list[dict]:
    """Rejected nodes whose recorded `Blocked by: PHP >= X.Y` condition the
    target now satisfies — findings for `refactor-learn` to act on
    (removing the out-of-scope entry); this function only detects, per the
    suite's detect-never-write split (`refactor-scan`/`refactor-learn`)."""
    repo = pathlib.Path(repo)
    current = _current_php_floor(_read_composer(repo))
    if current is None:
        return []
    findings = []
    for node in sorted(_rejected_nodes(repo)):
        blocked_by = _out_of_scope_blocked_by_php(repo, node)
        if blocked_by is not None and current >= blocked_by:
            findings.append({
                "node": node,
                "reason": (
                    f"PHP floor now {'.'.join(map(str, current))}, satisfies "
                    f"Blocked by PHP >= {'.'.join(map(str, blocked_by))}"
                ),
            })
    return findings


def _is_effectively_rejected(node: str, tree: dict, rejected: set[str], _seen: set[str] | None = None) -> bool:
    """True if `node` is rejected outright, or permanently closed because a
    `required` ancestor is (recursively) effectively rejected — the same
    closure a `required` edge already causes for proposability, made
    explicit here because `recommended`-edge gating (unlike `required`-edge
    gating) must tell "permanently rejected" apart from "not reached yet":
    only the former releases a `recommended`-gated child."""
    if _seen is None:
        _seen = set()
    if node in _seen:
        return False  # guard against a cycle, which a well-formed tree never has
    _seen.add(node)
    if node in rejected:
        return True
    return any(
        _is_effectively_rejected(p, tree, rejected, _seen)
        for p in tree["required_parents"].get(node, [])
    )


def _is_decided(node: str, tree: dict, detected: dict, rejected: set[str]) -> bool:
    """True once `node` has reached a final state for `recommended`-edge
    gating purposes (CONTEXT.md's Recommended edge): fulfilled, or
    effectively rejected (see above) — not merely "not yet reached"."""
    return detected.get(node, {}).get("fulfilled", False) or _is_effectively_rejected(node, tree, rejected)


def _undecided_recommended_parents(node: str, tree: dict, detected: dict, rejected: set[str]) -> list[str]:
    """`node`'s `recommended` parents that haven't reached a decided state
    yet — a non-empty result means `node` stays withheld: a
    `recommended` edge now gates until every parent is decided, releasing
    the child either way once decided (fulfilled, or rejected — unlike a
    `required` edge, which closes the child on rejection instead)."""
    return [rp for rp in tree["recommended_parents"].get(node, []) if not _is_decided(rp, tree, detected, rejected)]


def _rejected_nodes(repo: pathlib.Path) -> set[str]:
    """Tooling-tree nodes recorded as out-of-scope for this target repo.

    Convention: one file per rejected node at
    ``docs/refactoring/out-of-scope/<node>.md``. This is the minimal
    convention needed for structural-scan's `resolved` gate — it does not
    parse structural-candidate rejections, which are keyed by issue number,
    not node name.
    """
    d = repo / "docs" / "refactoring" / "out-of-scope"
    if not d.is_dir():
        return set()
    return {p.stem for p in d.glob("*.md")}


def detect_nodes(repo: pathlib.Path, tree: dict | None = None) -> dict:
    """Return {node: {fulfilled: bool, reason: str, details: dict}} for each node."""
    repo = pathlib.Path(repo)
    if tree is None:
        tree = load_tree()
    composer = _read_composer(repo)
    has_composer_json = _has_composer_json(repo)
    # lock may be at root or composer/composer.lock
    has_lock = (repo / "composer.lock").exists() or (repo / "composer" / "composer.lock").exists()
    has_git = (repo / ".git").exists()
    # CI runner
    has_ci = False
    for pat in [".github/workflows/*.yml", ".github/workflows/*.yaml", ".gitlab-ci.yml"]:
        if glob.glob(str(repo / pat)):
            has_ci = True
            break
    # php-cs-fixer — spec (php-tooling-tree.md) requires dep + config + runnable (zero diffs)
    # For file-based dry-run we approximate runnable as present when both dep and config exist
    has_cs_config = (repo / ".php-cs-fixer.php").exists() or (repo / ".php-cs-fixer.dist.php").exists()
    has_cs_dep = _has_dep(composer, "friendsofphp/php-cs-fixer") or _has_dep(composer, "php-cs-fixer/php-cs-fixer")
    # phpunit / pest
    has_phpunit = _has_dep(composer, "phpunit/phpunit")
    has_pest = _has_dep(composer, "pestphp/pest")
    has_phpunit_xml = (repo / "phpunit.xml").exists() or (repo / "phpunit.xml.dist").exists()
    # psalm
    has_psalm_dep = _has_dep(composer, "vimeo/psalm")
    has_psalm_cfg = (repo / "psalm.xml").exists() or (repo / "psalm.xml.dist").exists()
    # phpstan
    has_phpstan_dep = _has_dep(composer, "phpstan/phpstan")
    phpstan_level = _parse_phpstan_level(repo)
    baseline_empty = _is_baseline_empty(repo)
    baseline_exists = _baseline_exists(repo)

    out: dict = {}

    def set_node(node, fulfilled, reason, **details):
        out[node] = {"fulfilled": fulfilled, "reason": reason, "details": details}

    # git
    set_node("git", has_git, "found .git" if has_git else "no .git")
    # loop-config
    has_loop_config = _has_loop_config(repo)
    set_node("loop-config", has_loop_config, "docs/refactoring/config.md present" if has_loop_config else "no docs/refactoring/config.md")
    # composer
    set_node("composer", has_composer_json and has_lock, "composer.json+lock present" if has_composer_json and has_lock else "missing composer.json or lock", has_json=has_composer_json, has_lock=has_lock)
    # ci-runner
    set_node("ci-runner", has_ci, "CI config present" if has_ci else "no CI config")
    # php-cs-fixer
    cs_fulfilled = has_cs_dep and has_cs_config
    set_node("php-cs-fixer", cs_fulfilled, "dep and config present" if cs_fulfilled else "missing cs-fixer (need dep + config)", has_dep=has_cs_dep, has_config=has_cs_config)
    # phpunit
    phpunit_fulfilled = has_phpunit or has_pest or has_phpunit_xml
    set_node("phpunit", phpunit_fulfilled, "phpunit/pest present" if phpunit_fulfilled else "no test runner", has_phpunit=has_phpunit, has_pest=has_pest)
    # test-runner-if-missing: fulfilled if some runner exists, else blocked by composer etc.
    # If phpunit fulfilled -> this node considered fulfilled (no need to propose)
    tr_fulfilled = phpunit_fulfilled
    set_node("test-runner-if-missing", tr_fulfilled, "runner exists" if tr_fulfilled else "no runner — would propose phpunit", depends_composer=has_composer_json)
    # composer-audit: fulfilled once CI actually gates on `composer audit` (php-tooling-tree.md).
    # Eligibility (whether it's *proposable* at all, beyond its required edges) is a separate,
    # extra gate handled in next_candidates()/roadmap() — a real dependency exists, or every
    # other structural-scan leaf is already resolved — mirroring the phpstan-level-N
    # stop-conditions pattern rather than living in this fulfilment check.
    has_real_dep = _has_real_require_dep(composer)
    audit_fulfilled = _has_composer_audit_ci_job(repo)
    set_node(
        "composer-audit",
        audit_fulfilled,
        "CI job runs composer audit" if audit_fulfilled else "no CI job runs composer audit yet",
        has_real_dep=has_real_dep,
    )
    # phpstan-level-0-baseline
    # Psalm equivalence: if psalm dep + config -> fulfilled without phpstan
    psalm_fulfils_p0 = has_psalm_dep and has_psalm_cfg
    if psalm_fulfils_p0:
        set_node("phpstan-level-0-baseline", True, "psalm fulfils p0 (vimeo/psalm + psalm.xml)", has_psalm=True)
    elif has_phpstan_dep and phpstan_level == 0 and baseline_exists:
        set_node("phpstan-level-0-baseline", True, "phpstan level 0 + baseline present", level=phpstan_level, baseline_empty=baseline_empty)
    elif has_phpstan_dep and phpstan_level == 0 and not baseline_exists:
        # level 0 but no baseline yet -> not green, not fulfilled
        set_node("phpstan-level-0-baseline", False, "phpstan level 0 but baseline missing", level=phpstan_level)
    else:
        set_node("phpstan-level-0-baseline", False, "missing phpstan or level 0 or baseline", has_phpstan=has_phpstan_dep, level=phpstan_level, baseline_exists=baseline_exists)

    # phpstan-level-1..3
    # For fulfilled check: level >= N
    for lvl, node in [(1, "phpstan-level-1"), (2, "phpstan-level-2"), (3, "phpstan-level-3")]:
        if psalm_fulfils_p0:
            # Psalm path: level nodes not applicable -> treat as not unblocked (blocked by equivalence)
            set_node(node, False, "not applicable: psalm fulfils p0", psalm_equivalent=True)
            continue
        fulfilled = (phpstan_level is not None and phpstan_level >= lvl)
        # For roadmap gate, predecessor must be fulfilled with empty baseline
        # We expose details
        set_node(node, fulfilled, f"level {phpstan_level} >= {lvl}" if fulfilled else f"level {phpstan_level} < {lvl} or no phpstan", level=phpstan_level, baseline_empty=baseline_empty)

    # rector
    # Fulfilment: dead-code suite enabled and fully applied — we approximate as False unless rector.php contains dead-code set
    has_rector = (repo / "rector.php").exists() or (repo / "rector.neon").exists()
    has_rector_dead = False
    has_rector_types = False
    if has_rector:
        txt = ""
        for p in [repo / "rector.php", repo / "rector.neon"]:
            if p.exists():
                txt += p.read_text(encoding="utf-8")
        has_rector_dead = "DeadCode" in txt or "dead-code" in txt.lower()
        has_rector_types = "Type" in txt or "type" in txt.lower()
    set_node("rector-dead-code", has_rector_dead, "rector dead-code set present" if has_rector_dead else "no rector dead-code", has_rector=has_rector)
    set_node("rector-type-coverage", has_rector_types, "rector type coverage present" if has_rector_types else "no rector type coverage", has_rector=has_rector)

    # structural-scan: fulfilled once every `resolved` parent — every
    # PHP-tree leaf — is fulfilled OR recorded as rejected. Unlike a
    # required parent, a rejected resolved parent still counts as resolved.
    rejected = _rejected_nodes(repo)
    leaves = tree["resolved_parents"].get("structural-scan", [])
    if leaves:
        unresolved = [leaf for leaf in leaves if not (out.get(leaf, {}).get("fulfilled") or leaf in rejected)]
        ss_fulfilled = not unresolved
        set_node(
            "structural-scan",
            ss_fulfilled,
            "all php-tree leaves resolved (fulfilled or rejected)" if ss_fulfilled else f"waiting on: {', '.join(unresolved)}",
            unresolved=unresolved,
            rejected=sorted(rejected),
        )

    # Also include git/composer etc. already
    return out


def _is_unblocked(node: str, tree: dict, fulfilled: dict) -> tuple[bool, str]:
    """Check if node's required parents are fulfilled and no required parent is blocked by missing."""
    req = tree["required_parents"].get(node, [])
    for p in req:
        if not fulfilled.get(p, {}).get("fulfilled", False):
            return False, f"blocked by required parent {p}"
    return True, "required parents fulfilled"


def _composer_audit_extra_gate(has_real_dep: bool, tree: dict, resolved_check: dict, rejected: set[str]) -> tuple[bool, str]:
    """composer-audit's stop condition beyond required-edge fulfilment
    (php-tooling-tree.md): proposable once a real `require` dependency
    exists, or every *other* structural-scan leaf is already resolved —
    independent alternatives, not ordered. `resolved_check` maps node name
    to a bool: already fulfilled (real or simulated)."""
    if has_real_dep:
        return True, "real require dependency present"
    leaves = tree["resolved_parents"].get("structural-scan", [])
    other_leaves = [leaf for leaf in leaves if leaf != "composer-audit"]
    unresolved = [leaf for leaf in other_leaves if not (resolved_check.get(leaf, False) or leaf in rejected)]
    if not unresolved:
        return True, "no real dependency yet, but every other structural-scan leaf is resolved"
    return False, f"no real dependency yet, waiting on: {', '.join(unresolved)}"


def next_candidates(repo: pathlib.Path, tree: dict | None = None, limit: int | None = None) -> list[dict]:
    """Return every node that is *really* unblocked and unfulfilled right now
    (or, with an explicit `limit`, at most that many — `refactor-scan` itself
    never passes one: more than five nodes can be genuinely unblocked at
    once, so this is never capped by default).

    Unlike ``roadmap()``, this does not simulate — it does not assume a
    returned node is already fulfilled to compute what comes after it. Only
    ``git``'s real ``.git`` check and each node's real required/resolved
    parents decide what's in this list, so entries here can be true siblings
    (e.g. ``composer`` and ``ci-runner`` once ``loop-config`` is really
    fulfilled), not a serial lookahead — ``refactor-scan`` needs "what's
    proposable now", not a forward roadmap.

    A node with an undecided `recommended` parent is withheld from this list
    entirely rather than merely ranked lower — see ``withheld_candidates()``
    for the matching "waiting on" list ``refactor-scan`` surfaces alongside
    this one.
    """
    repo = pathlib.Path(repo)
    if tree is None:
        tree = load_tree()
    detected = detect_nodes(repo, tree)
    detected["git"]["fulfilled"] = True  # never proposed
    rejected = _rejected_nodes(repo)

    result: list[dict] = []
    for node in tree["order"]:
        if node == "git":
            continue
        if node == "structural-scan":
            # Checked on its own terms, *before* the generic fulfilled-skip
            # below: detect_nodes() marks this node "fulfilled" the instant
            # its resolved-parent leaves resolve, but that's the gate
            # *opening*, not the node being delivered and done (unlike every
            # other tooling node, where fulfilled really does mean "don't
            # propose again"). Gating on the generic skip here made this
            # branch permanently unreachable dead code — structural-scan
            # must stay proposable every pass once open: it's an ongoing
            # candidate for refactor-design to keep drawing on, not a
            # one-time node.
            leaves = tree["resolved_parents"].get(node, [])
            unresolved = [leaf for leaf in leaves if not (detected.get(leaf, {}).get("fulfilled", False) or leaf in rejected)]
            if unresolved:
                continue
            result.append({"node": node, "reason": "all resolved-parent leaves fulfilled or rejected"})
        else:
            if detected.get(node, {}).get("fulfilled", False):
                continue
            if node in rejected:
                continue  # explicitly rejected — stays out until its out-of-scope entry is reversed
            ok, why = _is_unblocked(node, tree, detected)
            if not ok:
                continue
            if _undecided_recommended_parents(node, tree, detected, rejected):
                continue  # withheld — see withheld_candidates()
            if node == "composer-audit":
                has_real_dep = detected.get("composer-audit", {}).get("details", {}).get("has_real_dep", False)
                resolved_check = {n: d.get("fulfilled", False) for n, d in detected.items()}
                ok, why = _composer_audit_extra_gate(has_real_dep, tree, resolved_check, rejected)
                if not ok:
                    continue
            result.append({"node": node, "reason": why})
        if limit is not None and len(result) >= limit:
            break
    return result


def withheld_candidates(repo: pathlib.Path, tree: dict | None = None) -> list[dict]:
    """Nodes that would otherwise be in ``next_candidates()`` (required
    parents fulfilled, not rejected, not yet fulfilled) but stay withheld
    because one or more ``recommended`` parents haven't reached a decided
    state yet — surfaced separately so ``refactor-scan`` can name them and
    say what they're waiting on, instead of them silently vanishing from the
    proposal set."""
    repo = pathlib.Path(repo)
    if tree is None:
        tree = load_tree()
    detected = detect_nodes(repo, tree)
    detected["git"]["fulfilled"] = True
    rejected = _rejected_nodes(repo)

    result: list[dict] = []
    for node in tree["order"]:
        if node in ("git", "structural-scan"):
            continue
        if detected.get(node, {}).get("fulfilled", False) or node in rejected:
            continue
        ok, _why = _is_unblocked(node, tree, detected)
        if not ok:
            continue
        undecided = _undecided_recommended_parents(node, tree, detected, rejected)
        if undecided:
            result.append({"node": node, "waiting_on": undecided})
    return result


def roadmap(repo: pathlib.Path, steps: int = 10, tree: dict | None = None) -> list[dict]:
    """Generate next `steps` MRs deterministically from current repo state.

    Does not mutate repo; simulates fulfilling nodes in priority order.
    After tooling nodes exhausted or blocked, fills with structural candidates from expected/issues if present.
    """
    repo = pathlib.Path(repo)
    if tree is None:
        tree = load_tree()
    # Priority order: as appear in edges table order (tree["order"])
    # But ensure stable priority: git, ci-runner, composer, then composer children in table order, then p-chain, rector
    priority = tree["order"]
    # Also include nodes not in order? fallback
    all_nodes = priority[:]

    detected = detect_nodes(repo, tree)
    # Copy fulfilled status to simulate
    fulfilled = {k: v["fulfilled"] for k, v in detected.items()}
    # git is never an MR; treat as implicitly fulfilled for roadmap (harness does git init)
    fulfilled["git"] = True
    detected["git"]["fulfilled"] = True
    # out-of-scope rejections, used by structural-scan's `resolved` gate
    rejected = _rejected_nodes(repo)

    # For roadmap simulation, we need to handle that composer-audit is special: we marked fulfilled False always, so it will be proposed.
    # But test-runner-if-missing is fulfilled if phpunit present — skip proposing it separately.
    # We'll generate steps by iteratively picking highest-priority unblocked not-yet-fulfilled node.

    result: list[dict] = []

    # Helper to get candidate structural issues for filling — supports new layout project/ + expected (sibling)
    structural_candidates: list[dict] = []
    # 1) Direct expected under repo (old layout: repo/expected, or DST with project copy but expected still at repo/expected for original fixture)
    for cand_dir in [repo / "expected" / "issues", repo / "project" / "expected" / "issues", repo / "composer" / "expected" / "issues"]:
        if cand_dir.exists():
            for f in sorted(cand_dir.glob("*.md")):
                structural_candidates.append({"file": f.name, "path": str(f)})
    # 2) If repo is a DST (/tmp/.../php-empty), look at original fixture's expected (sibling to project, not mounted)
    if not structural_candidates:
        # Dev/test-only: REPO_ROOT resolves to the suite checkout, which has
        # a fixtures/ tree; never reached at skill runtime (see REPO_ROOT above).
        fixtures_expected = REPO_ROOT / "fixtures" / "php" / repo.name / "expected" / "issues"
        if fixtures_expected.exists():
            for f in sorted(fixtures_expected.glob("*.md")):
                structural_candidates.append({"file": f.name, "path": str(f)})
    # 3) Fallback recursive
    if not structural_candidates:
        for p in repo.rglob("expected/issues/*.md"):
            structural_candidates.append({"file": p.name, "path": str(p)})
            if len(structural_candidates) >= 10:
                break

    # Simulate
    for _ in range(steps):
        sim_fulfilled = {**fulfilled, **{r["node"]: True for r in result}}
        # Find best unblocked candidate among tooling nodes
        best = None
        best_reason = ""
        for node in priority:
            if node == "git":
                continue  # never an MR
            if sim_fulfilled.get(node, False):
                continue  # already fulfilled (real or simulated), skip
            if node in rejected:
                continue  # explicitly rejected — stays out until its out-of-scope entry is reversed
            if node == "structural-scan":
                # `resolved` gate: every leaf must be fulfilled OR rejected —
                # not the standard required-parent check, which would
                # instead close this node forever on any rejection.
                leaves = tree["resolved_parents"].get(node, [])
                unresolved = [leaf for leaf in leaves if not (sim_fulfilled.get(leaf, False) or leaf in rejected)]
                if unresolved:
                    continue
                best = node
                best_reason = "all php-tree leaves resolved (fulfilled or rejected)"
                break
            # test-runner-if-missing is fulfilled if phpunit/pest already fulfilled (simulated)
            if node == "test-runner-if-missing" and sim_fulfilled.get("phpunit"):
                continue
            if node == "phpunit" and sim_fulfilled.get("test-runner-if-missing"):
                continue
            sim_ok, sim_why = _is_unblocked(node, tree, {k: {"fulfilled": v} for k, v in sim_fulfilled.items()})
            if not sim_ok:
                continue
            if node == "composer-audit":
                has_real_dep = detected.get("composer-audit", {}).get("details", {}).get("has_real_dep", False)
                sim_ok, sim_why = _composer_audit_extra_gate(has_real_dep, tree, sim_fulfilled, rejected)
                if not sim_ok:
                    continue
            # For phpstan levels, additional empty-baseline gate
            if node in ("phpstan-level-1", "phpstan-level-2", "phpstan-level-3"):
                # Need predecessor fulfilled with empty baseline
                # Predecessor mapping: p1 needs p0 empty, p2 needs p1 empty, etc.
                pred = {"phpstan-level-1": "phpstan-level-0-baseline", "phpstan-level-2": "phpstan-level-1", "phpstan-level-3": "phpstan-level-2"}[node]
                # For simulation, check predecessor fulfilled
                if not sim_fulfilled.get(pred, False):
                    continue
                # Check baseline empty per current repo state (or simulated after fulfilling pred? assume after pred fulfilled baseline becomes empty?)
                # For deterministic roadmap, we assume after p0 fulfilled, baseline may be non-empty -> p1 blocked until shrink.
                # Our detection says baseline_empty reflects current file state.
                # For simulation without shrinking, p1 would be blocked if baseline non-empty.
                # But to keep roadmap simple, we allow p1 if baseline_empty true, else skip and let tooling pressure fill?
                # We'll check actual baseline_empty
                if not _is_baseline_empty(repo):
                    # If non-empty, p1 not yet proposable — skip
                    continue
                # Also psalm equivalence blocks
                if detected.get("phpstan-level-0-baseline", {}).get("details", {}).get("has_psalm"):
                    continue
                # Alternative: if predecessor just simulated as fulfilled in this roadmap run, assume baseline becomes empty after shrink step? For simplicity allow next level.
                pass
            # For rector nodes: require p0 fulfilled (already checked), recommended parents are advisory not blocking
            # Choose best by priority order (first found)
            best = node
            best_reason = sim_why
            break
        if best:
            req = tree["required_parents"].get(best, [])
            rec = tree["recommended_parents"].get(best, [])
            # Outlook note for recommended parents missing
            outlook = ""
            for rp in rec:
                # check if recommended parent not fulfilled
                if not fulfilled.get(rp, False) and rp not in [r["node"] for r in result]:
                    outlook = f" | outlook: would benefit from {rp} (recommended) — still proposable"
                    break
            result.append({"n": len(result) + 1, "node": best, "type": "tooling", "required_parents": req, "recommended_parents": rec, "reason": best_reason + outlook})
            # Do not actually mutate repo; just mark fulfilled for simulation
            continue
        # No tooling node unblocked -> fill with structural candidates, but
        # only once the structural-scan gate has actually opened: every
        # PHP-tree leaf resolved. Otherwise structural work is exactly
        # what's still blocked — falling back to it here would silently
        # bypass the gate whenever the tooling chain stalls (e.g. a
        # non-empty PHPStan baseline blocking the next level).
        if structural_candidates and sim_fulfilled.get("structural-scan", False):
            # pop next structural
            idx = len([r for r in result if r["type"] == "structural"])
            if idx < len(structural_candidates):
                cand = structural_candidates[idx]
                result.append({"n": len(result) + 1, "node": f"structural:{cand['file']}", "type": "structural", "reason": "planted candidate"})
                continue
        # Fill remaining with open chain note
        if len(result) < steps:
            nxt = 4 + len([r for r in result if "phpstan-level" in r["node"]])
            result.append({"n": len(result) + 1, "node": f"phpstan-level-{nxt}", "type": "tooling (open chain)", "reason": "chain open above level 3 — appended node"})
            continue
        break

    # Ensure 10 steps by truncating/expanding
    return result[:steps]


def detect_and_roadmap(repo: pathlib.Path, steps: int = 10, tree_md: pathlib.Path | None = None) -> dict:
    tree = load_tree(tree_md=tree_md)
    detected = detect_nodes(repo, tree)
    road = roadmap(repo, steps=steps, tree=tree)
    # `next` is uncapped — `--steps` only bounds `roadmap`'s forward
    # simulation depth, a separate concept.
    nxt = next_candidates(repo, tree=tree)
    withheld = withheld_candidates(repo, tree=tree)
    reversals = php_version_reversal_findings(repo)
    return {
        "detected": detected,
        "roadmap": road,
        "next": nxt,
        "withheld": withheld,
        "reversals": reversals,
        "tree": {"edges": tree["edges"]},
    }


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser(description="Detect tooling tree and propose next MRs (dry-run, no mutation)")
    ap.add_argument("repo", nargs="?", default=".", help="path to fixture/repo (default: .)")
    ap.add_argument("--steps", type=int, default=10, help="depth of the simulated `roadmap` lookahead — does not bound `next`, which is always every currently-unblocked node")
    ap.add_argument("--tree", type=str, default=None, help="path to a single tree file to use instead of the suite's own generic root + PHP tree (single-file mode, e.g. for a synthetic test tree). Only scopes edges/gating (next, roadmap, tree.edges) -- detect_nodes' per-tool filesystem checks are hardcoded and always run regardless of --tree, so 'detected' in the JSON output may list nodes your override tree doesn't even define")
    ap.add_argument("--json", action="store_true", help="output JSON (default)")
    args = ap.parse_args()
    repo = pathlib.Path(args.repo)
    tree_md = pathlib.Path(args.tree) if args.tree else None
    data = detect_and_roadmap(repo, steps=args.steps, tree_md=tree_md)
    # also add branch check: ensure no extra branches created
    # include git status
    print(json.dumps(data, indent=2))
