"""Deterministic graph-logic parser for the tooling tree.

Provides load_tree, next_candidates, and graph-logic-only
outputs (ordered backlog, workable nodes, withheld with reasons, closed by
rejection, merge-request outlook) without invoking LLM or mutating repo.

Seam: skills/refactor-scan/references/tooling_tree.py — used by refactor-scan.

Docs: tooling-tree.md and php-tooling-tree.md (siblings to this file) are
machine-readable (edges table), CONTEXT.md vocabulary.
"""

from __future__ import annotations

import json
import pathlib
import re

_HERE = pathlib.Path(__file__).resolve().parent
TREE_MD = _HERE / "php-tooling-tree.md"
# Generic root: git -> onboarding-setup, and the structural-scan node that PHP's
# tree leaves point into via `resolved` edges.
GENERIC_TREE_MD = _HERE / "tooling-tree.md"

_VALID_EDGE_TYPES = ("required", "recommended", "resolved", "required-any")

# Ordinary required-gated nodes that must never be surfaced as a proposable
# candidate, regardless of their own fulfilled state: `git` (never an MR),
# `static-code-analyzer` (pure plumbing), `psalm` (recognition-only — same
# fait-accompli shape Pest already gets for `phpunit`), `is-php-project`
# (recognition-only gate for the whole PHP specialization — rejecting a
# required parent never unblocks its children, so a human filing an
# out-of-scope entry for it would never accomplish anything leaving it
# unfulfilled doesn't already). Resolved-gated aggregation nodes
# (`php-safety-net`) are excluded separately via
# `exposed_resolved_gate_nodes` in load_tree() — this set is for ordinary
# required-gated nodes instead.
_NEVER_PROPOSED = {"git", "static-code-analyzer", "psalm", "is-php-project", "has-real-dependency", "phpstan-baseline-empty", "phpstan-not-psalm"}

# ---------------------------------------------------------------------------
# Seed input: fulfilled-set file (agent-judged fulfilment)
# ---------------------------------------------------------------------------


def _load_fulfilled_seed(seed_path: pathlib.Path) -> dict[str, bool]:
    """Load a fulfilled-set file: JSON ``{node_slug: true/false}``.

    Nodes missing from the file are treated as not fulfilled.
    Returns ``{node: bool}`` — simple, no reason/details metadata needed
    for graph-logic-only computation.
    """
    try:
        data = json.loads(seed_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return {k: bool(v) for k, v in data.items() if isinstance(v, bool)}


# The Track sections whose ``**Open:**``/``**Out-of-scope:**`` fields
# carry node state (skills/continuous-refactoring/references/
# refactoring-bookkeeping.md). `## Housekeeping`/`## Investigation` carry
# only Cadence/Last scan — no node state — so they are not section states
# here; any heading still ends the collecting state like every other one.
_TRACK_SECTION_HEADINGS = ("## Safety Net", "## Guardrails")


def _derive_fulfilled_from_bookkeeping(
    repo: pathlib.Path, tree: dict
) -> dict[str, bool] | None:
    """Derive node fulfilled state from bookkeeping.md's Track sections.

    Collects the bullets under the ``**Open:**``/``**Out-of-scope:**``
    field lines inside the ``## Safety Net``/``## Guardrails`` sections
    (the documented schema, written by
    skills/refactor-learn/references/safety-net-write.md and
    guardrails-write.md).  A scope node that is neither in ``Open`` nor
    in ``Out-of-scope`` is fulfilled.  Other fields (e.g. ``Last scan``,
    the retired ``Fulfilled nodes``) are ignored, not migrated.  Returns
    ``None`` when no bookkeeping file or no Track-section state exists
    (the caller returns ``{}`` — there is no detection fallback; scan
    passes require a seed).
    """
    bookkeeping = _resolve_refactoring_notes_dir(repo) / "bookkeeping.md"
    if not bookkeeping.exists():
        return None
    try:
        text = bookkeeping.read_text(encoding="utf-8")
    except OSError:
        return None

    open_nodes: set[str] = set()
    out_of_scope_nodes: set[str] = set()
    in_track_section = False
    collecting: str | None = None
    saw_track_state = False

    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            in_track_section = stripped.startswith(_TRACK_SECTION_HEADINGS)
            collecting = None
            continue
        if in_track_section and stripped.startswith("**Open:**"):
            collecting = "open"
            saw_track_state = True
            continue
        if in_track_section and stripped.startswith("**Out-of-scope:**"):
            collecting = "out-of-scope"
            saw_track_state = True
            continue
        if stripped.startswith("**"):
            collecting = None  # any other field (Last scan, retired Fulfilled nodes) ends the list
            continue
        if collecting == "open" and stripped.startswith("- "):
            slug = stripped[2:].split()[0].strip("`").strip()
            if slug and slug != "none":
                open_nodes.add(slug)
        elif collecting == "out-of-scope" and stripped.startswith("- "):
            slug = stripped[2:].split()[0].strip("`").strip()
            if slug and slug != "none":
                out_of_scope_nodes.add(slug)

    if not saw_track_state:
        return None

    result: dict[str, bool] = {}
    for node in tree["nodes"]:
        if node in open_nodes or node in out_of_scope_nodes:
            result[node] = False
        else:
            result[node] = True
    return result


def _resolve_fulfilled(
    repo: pathlib.Path,
    tree: dict,
    fulfilled: dict[str, bool] | None = None,
) -> dict[str, bool]:
    """Resolve the fulfilled set from the highest-priority source.

    Priority: explicit ``fulfilled`` parameter > seed file >
    bookkeeping derivation.  When none is available, returns ``{}``
    (no detection fallback — scan passes require the seed; other passes
    derive state from bookkeeping).
    """
    if fulfilled is not None:
        return fulfilled
    # Check for seed file in Refactoring Notes
    notes_dir = _resolve_refactoring_notes_dir(repo)
    seed_path = notes_dir / "fulfilled-set.json"
    if seed_path.exists():
        return _load_fulfilled_seed(seed_path)
    # Try bookkeeping derivation
    derived = _derive_fulfilled_from_bookkeeping(repo, tree)
    if derived is not None:
        return derived
    return {}


def closed_by_rejection(tree: dict, rejected: set[str]) -> list[str]:
    """Nodes whose required (or required-any) ancestor is rejected —
    permanently closed for good, unlike merely unfulfilled nodes."""
    result = []
    for node in tree["order"]:
        if node in rejected:
            continue
        if _is_effectively_rejected(node, tree, rejected):
            result.append(node)
    return result


def _withheld_guard_cascade(
    repo: pathlib.Path,
    tree: dict | None = None,
    fulfilled: dict[str, bool] | None = None,
):
    """The guard cascade withheld_with_reasons() and withheld_candidates()
    share: resolves fulfilled state, then yields ``(node, blocked_reason,
    undecided_parents)`` for every node that survives the common guards
    (not never-proposed, not resolved-gated, not fulfilled, not rejected,
    not PHP-floor-blocked, recommended gate not moot) and is either
    blocked on a required parent (``blocked_reason`` set,
    ``undecided_parents`` None — never computed, the node never gets that
    far) or waiting on undecided recommended parents (``blocked_reason``
    None)."""
    repo = pathlib.Path(repo)
    if tree is None:
        tree = load_tree()
    resolved = _resolve_fulfilled(repo, tree, fulfilled)
    resolved["git"] = True
    detected = {n: {"fulfilled": v} for n, v in resolved.items()}
    rejected = _rejected_nodes(repo)
    php_floor_blocked = {b["node"] for b in php_floor_precheck(repo)}
    for node in tree["order"]:
        if node in _NEVER_PROPOSED or tree["resolved_parents"].get(node):
            continue
        if detected.get(node, {}).get("fulfilled", False) or node in rejected:
            continue
        if node in php_floor_blocked:
            continue
        if _recommended_gate_moot(node, tree, detected):
            continue
        ok, why = _is_unblocked(node, tree, detected)
        if not ok:
            yield node, why, None
            continue
        undecided = _undecided_recommended_parents(node, tree, detected, rejected)
        if undecided:
            yield node, None, undecided


def withheld_with_reasons(
    repo: pathlib.Path,
    tree: dict | None = None,
    fulfilled: dict[str, bool] | None = None,
) -> list[dict]:
    """Withheld nodes with reasons: rejected required ancestors or
    undecided recommended parents."""
    result: list[dict] = []
    for node, why, undecided in _withheld_guard_cascade(repo, tree, fulfilled):
        if why is not None:
            result.append({"node": node, "reason": why})
        else:
            result.append({"node": node, "reason": f"waiting on: {', '.join(undecided)}"})
    return result


def ordered_backlog(
    repo: pathlib.Path,
    tree: dict | None = None,
    fulfilled: dict[str, bool] | None = None,
) -> list[str]:
    """Complete ordered list of unresolved scope nodes in tree order,
    blocked nodes included — the list a scan records into ``Open``."""
    repo = pathlib.Path(repo)
    if tree is None:
        tree = load_tree()
    resolved = _resolve_fulfilled(repo, tree, fulfilled)
    rejected = _rejected_nodes(repo)
    closed = set(closed_by_rejection(tree, rejected))
    backlog = []
    for node in tree["order"]:
        if node in _NEVER_PROPOSED:
            continue
        if resolved.get(node, False):
            continue
        if node in rejected:
            continue
        if node in closed:
            continue
        backlog.append(node)
    return backlog


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
    # parent still counts as resolved. Used by structural-scan and, one hop
    # down, by php-safety-net (the PHP tree's own aggregation node
    # feeding it) — see tooling-tree.md's structural-scan node.
    resolved_parents: dict[str, list[str]] = {n: [] for n in nodes}
    # `required-any` parents: unlike `required` (every parent
    # must be fulfilled), a node with required-any parents is unblocked once
    # *at least one* of them is fulfilled — e.g. psalm-taint-analysis is
    # proposed once either phpstan-level-4 or psalm is fulfilled, whichever
    # general-analysis path the target took. Ordinary required parents (if
    # any) on the same node must still all be fulfilled too — the two lists
    # combine with AND between them, OR within this one.
    required_any_parents: dict[str, list[str]] = {n: [] for n in nodes}
    for e in edges:
        if e["type"] == "required":
            required_parents[e["to"]].append(e["from"])
        elif e["type"] == "recommended":
            recommended_parents[e["to"]].append(e["from"])
        elif e["type"] == "required-any":
            required_any_parents[e["to"]].append(e["from"])
        else:
            resolved_parents[e["to"]].append(e["from"])
    # A resolved-gated node whose own resolved-ness only feeds *another*
    # resolved-gated node's resolved_parents (an aggregation node — today:
    # php-safety-net, feeding structural-scan) is never itself
    # proposed. Derived from the edge table rather than a hardcoded name, so
    # a future second aggregation node (e.g. js-structural-scan) needs no
    # code change here.
    _resolved_targets = {n for n, parents in resolved_parents.items() if parents}
    _aggregated_away = {
        p for n in _resolved_targets for p in resolved_parents[n] if p in _resolved_targets
    }
    exposed_resolved_gate_nodes = _resolved_targets - _aggregated_away
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
        "required_any_parents": required_any_parents,
        "recommended_parents": recommended_parents,
        "resolved_parents": resolved_parents,
        "exposed_resolved_gate_nodes": exposed_resolved_gate_nodes,
    }


def _read_composer(repo: pathlib.Path) -> dict | None:
    for cand in [repo / "composer.json", repo / "composer" / "composer.json"]:
        if cand.exists():
            try:
                return json.loads(cand.read_text(encoding="utf-8"))
            except Exception:
                return None
    return None


def _resolve_refactoring_notes_dir(repo: pathlib.Path) -> pathlib.Path:
    """Where the suite keeps its own state in this target repo — the
    Refactoring Notes. Default docs/refactoring/; overridden by a
    `Refactoring Notes: `<path>`` line in the target's AGENTS.md or
    CLAUDE.md (onboarding-setup's own interview writes this once, into whichever
    of the two already existed — never both) — see
    skills/continuous-refactoring/references/refactoring-bookkeeping.md for the
    exact line format this parses."""
    default = repo / "docs" / "refactoring"
    for name in ("AGENTS.md", "CLAUDE.md"):
        p = repo / name
        if not p.exists():
            continue
        try:
            txt = p.read_text(encoding="utf-8")
        except OSError:
            continue
        m = re.search(r"^Refactoring Notes:\s*`([^`]+)`", txt, re.MULTILINE)
        if m:
            return repo / m.group(1).strip().strip("/")
    return default


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
    p = _resolve_refactoring_notes_dir(repo) / "out-of-scope" / f"{node}.md"
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


# The oldest PHP version each of the five deterministic PHP tooling leaves
# has ever run on, across every published major line of the
# tool — below this floor, no version of the tool (however old or
# unmaintained) can be installed at all, so a propose → design → implement
# → reject cycle can never land it. Checked once per pass instead of once
# per leaf (see `php_floor_precheck`). Source facts:
#   - php-cs-fixer: friendsofphp/php-cs-fixer 1.0 (2012) required PHP >=5.3.6.
#   - phpunit: phpunit/phpunit's earliest Composer-installable line (3.7)
#     required PHP >=5.3.3.
#   - test-runner-if-missing: defaults to adopting phpunit — same floor.
#   - composer-audit: the `composer audit` subcommand shipped in Composer
#     2.4.0 (2022); no earlier Composer release (1.x or 2.0-2.3) ever had it,
#     and Composer 2.4 itself requires PHP >=7.2.5.
#   - phpstan-level-0: phpstan/phpstan's first published release
#     (0.1) required PHP ~7.0 — it has never run on PHP 5.x; vimeo/psalm
#     (this node's equivalent fulfiller) has likewise required PHP 7+ since
#     its earliest releases.
_LEAF_MIN_PHP_VERSION = {
    "php-cs-fixer": "5.3",
    "phpunit": "5.3",
    "test-runner-if-missing": "5.3",
    "composer-audit": "7.2",
    "phpstan-level-0": "7.0",
}


def php_floor_precheck(repo: pathlib.Path) -> list[dict]:
    """Check the target's current PHP floor once against each of
    `_LEAF_MIN_PHP_VERSION`'s five leaves, instead of proposing (and
    eventually rejecting) each one individually five separate times.
    Returns the leaves whose minimum isn't met yet, each with a
    human-readable reason — `next_candidates()` skips these,
    and `detect_and_roadmap()` surfaces the list so a caller can report the
    fact in one pass instead of it silently vanishing.

    Design decision: skip silently, no `docs/refactoring/out-of-scope/`
    entry written for a blocked leaf. The check is cheap and re-derived
    fully from `composer.json` every pass, so nothing is lost by not
    persisting it — and that directory otherwise records a genuine human/
    agent rejection decision (a mechanical-reversal design), not a
    mechanical fact already on disk. Once the target's PHP floor rises, a
    previously-blocked leaf is simply unblocked next pass; there is nothing
    to reverse. The one consequence worth naming: `phpunit` is the only one
    of these five nodes that's still a `php-safety-net` leaf (php-tooling-
    tree.md's `resolved` edges) — while blocked here, it counts as neither
    fulfilled nor rejected, so `structural-scan` stays genuinely closed
    until the floor rises (matching how a target that truly cannot run
    these tools yet shouldn't be treated as tooling-ready). `composer-audit`
    is no longer a `php-safety-net` leaf either (moved to the Signal wave
    instead) — like
    `php-cs-fixer`/`test-runner-if-missing`, a floor block on it now only
    delays its own adoption. A human who wants `structural-scan` to open
    anyway despite the floor can still file the out-of-scope entries by
    hand — this precheck doesn't do it for them.

    Returns `[]` when the target's PHP floor can't be determined (no
    `composer.json`, or neither `require.php` nor `config.platform.php`
    parses) — consistent with `php_version_reversal_findings()`, unknown
    floor never blocks anything here either."""
    repo = pathlib.Path(repo)
    current = _current_php_floor(_read_composer(repo))
    if current is None:
        return []
    blocked = []
    for node, min_constraint in _LEAF_MIN_PHP_VERSION.items():
        minimum = _parse_min_version(min_constraint)
        if minimum is not None and current < minimum:
            blocked.append({
                "node": node,
                "reason": (
                    f"PHP floor {'.'.join(map(str, current))} below {node}'s minimum "
                    f"PHP >= {'.'.join(map(str, minimum))}"
                ),
            })
    return blocked


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
    only the former releases a `recommended`-gated child. Also used by
    `_resolved_gate_status()` for the same "closed for good" question one
    level down: a `resolved`-gate leaf that isn't itself rejected but sits
    behind a rejected required parent (e.g. `phpstan-level-5` behind a
    rejected `phpstan-level-2`) must still count as resolved, the same as a
    directly-rejected leaf already does.

    A `required-any` parent only closes this way once *every* one of its
    options is effectively rejected — rejecting just one of several
    required-any options must not close the child, since any of the others
    fulfilling it still would (mirrors `_is_permanently_gated`'s identical
    required-any handling for its own, unrelated gate condition).

    Each sibling call below gets its own *copy* of `_seen`, not the same
    mutable set — two required(-any) siblings can legitimately re-converge
    on a shared ancestor further up (a diamond, not a cycle), and sharing
    one set across them would make the second sibling's honest re-visit
    look like a cycle and short-circuit to `False`, even when continuing
    would find the real rejection (e.g. `rector-php-set`'s `phpstan-level-0`
    and `psalm`, both requiring `static-code-analyzer`)."""
    if _seen is None:
        _seen = set()
    if node in _seen:
        return False  # guard against a cycle, which a well-formed tree never has
    _seen.add(node)
    if node in rejected:
        return True
    if any(
        _is_effectively_rejected(p, tree, rejected, set(_seen))
        for p in tree["required_parents"].get(node, [])
    ):
        return True
    req_any = tree["required_any_parents"].get(node, [])
    if req_any and all(_is_effectively_rejected(p, tree, rejected, set(_seen)) for p in req_any):
        return True
    return False


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


def _is_permanently_gated(node: str, tree: dict, detected: dict, _seen: set[str] | None = None) -> bool:
    """True once `node` sits behind an unfulfilled recognition/detection
    gate (`_NEVER_PROPOSED` — `is-php-project`, `static-code-analyzer`,
    `psalm`) somewhere in its required-parent closure: a real, currently-
    false signal about the target itself (wrong language, no static
    analyzer adopted) that no pass or human ever decides on — unlike
    `_is_effectively_rejected`, nobody rejected anything here.

    Each sibling call below gets its own *copy* of `_seen` — see
    `_is_effectively_rejected`'s identical note; the same diamond shape
    (two required(-any) siblings re-converging on a shared ancestor) would
    otherwise make the second sibling's honest re-visit look like a cycle."""
    if _seen is None:
        _seen = set()
    if node in _seen:
        return False
    _seen.add(node)
    if node in _NEVER_PROPOSED and not detected.get(node, {}).get("fulfilled", False):
        return True
    if any(_is_permanently_gated(p, tree, detected, set(_seen)) for p in tree["required_parents"].get(node, [])):
        return True
    req_any = tree["required_any_parents"].get(node, [])
    if req_any and all(_is_permanently_gated(p, tree, detected, set(_seen)) for p in req_any):
        return True
    return False


def _recommended_gate_moot(node: str, tree: dict, detected: dict) -> bool:
    """True when `node` has at least one `recommended` parent and *every*
    one of them is permanently gated (see `_is_permanently_gated`) — the
    recommended edge can never actually release on this target, so
    surfacing `node` as "withheld, waiting on X" is noise: X will never
    reach a decided state through ordinary loop action (e.g.
    `rector-type-coverage` on a non-PHP target, whose four recommended
    parents all bottom out at the unfulfilled `is-php-project` gate, despite
    `rector-type-coverage` itself carrying no required parent of its own to
    be blocked by directly)."""
    parents = tree["recommended_parents"].get(node, [])
    return bool(parents) and all(_is_permanently_gated(p, tree, detected) for p in parents)


def _rejected_nodes(repo: pathlib.Path) -> set[str]:
    """Tooling-tree nodes recorded as out-of-scope for this target repo.

    Convention: one file per rejected node at
    ``<Refactoring Notes>/out-of-scope/<node>.md`` (default
    ``docs/refactoring/out-of-scope/<node>.md`` — see
    _resolve_refactoring_notes_dir). This is the minimal convention needed
    for structural-scan's `resolved` gate — it does not parse
    structural-candidate rejections, which are keyed by issue number, not
    node name.
    """
    d = _resolve_refactoring_notes_dir(repo) / "out-of-scope"
    if not d.is_dir():
        return set()
    return {p.stem for p in d.glob("*.md")}


def _resolved_gate_status(
    tree: dict, fulfilled_lookup, rejected: set[str]
) -> dict[str, tuple[bool, list[str]]]:
    """Compute ``{node: (resolved, unresolved_leaves)}`` for every node with
    one or more `resolved` parents — generic over any such node (today:
    ``structural-scan``, and PHP's own aggregation node ``php-structural-
    scan`` feeding it), not hardcoded to one node name. A node is resolved
    once every one of its resolved-parent leaves is itself fulfilled,
    recorded as rejected, or effectively rejected (``_is_effectively_rejected``
    — closed for good because a required ancestor of the leaf is rejected,
    even though the leaf itself was never explicitly rejected) — unlike a
    required parent, a rejected resolved parent still counts as resolved.

    Computed in dependency order so an aggregation node (whose own
    resolved-parents are ordinary leaves) is resolved *before* a node that
    reads its resolved-ness as one of its own resolved-parents (e.g.
    structural-scan reading php-safety-net) — independent of where
    either node happens to sit in ``tree["order"]``.

    ``fulfilled_lookup(name) -> bool`` supplies each ordinary leaf's
    fulfilled state — either the real fulfilled-set output, or
    a per-iteration simulated snapshot.
    """
    resolved_gated = [n for n in tree["resolved_parents"] if tree["resolved_parents"][n]]
    computed: dict[str, tuple[bool, list[str]]] = {}
    pending = set(resolved_gated)
    while pending:
        progressed = False
        for node in list(pending):
            leaves = tree["resolved_parents"][node]
            if any(leaf in pending for leaf in leaves):
                continue  # a resolved-gated leaf not yet computed this pass -- defer
            unresolved = [
                leaf for leaf in leaves
                if not (
                    (computed[leaf][0] if leaf in computed else fulfilled_lookup(leaf))
                    or _is_effectively_rejected(leaf, tree, rejected)
                )
            ]
            computed[node] = (not unresolved, unresolved)
            pending.discard(node)
            progressed = True
        if not progressed:
            break  # cycle among resolved-gated nodes -- a well-formed tree never has one
    return computed


def _is_unblocked(node: str, tree: dict, fulfilled: dict) -> tuple[bool, str]:
    """Check if node's required parents are fulfilled and no required parent is blocked by missing."""
    req = tree["required_parents"].get(node, [])
    for p in req:
        if not fulfilled.get(p, {}).get("fulfilled", False):
            return False, f"blocked by required parent {p}"
    # required-any: at least one, not all, must be fulfilled.
    # Combines with the ordinary required parents above via AND (both checks
    # must pass); within this group the parents combine via OR.
    req_any = tree["required_any_parents"].get(node, [])
    if req_any and not any(fulfilled.get(p, {}).get("fulfilled", False) for p in req_any):
        return False, f"blocked — none of required-any parents fulfilled: {', '.join(req_any)}"
    return True, "required parents fulfilled"


def next_candidates(
    repo: pathlib.Path,
    tree: dict | None = None,
    limit: int | None = None,
    fulfilled: dict[str, bool] | None = None,
) -> list[dict]:
    """Return every node that is *really* unblocked and unfulfilled right now
    (or, with an explicit `limit`, at most that many — `refactor-scan` itself
    never passes one: more than five nodes can be genuinely unblocked at
    once, so this is never capped by default).

    Does not simulate — does not assume a returned node is already fulfilled
    to compute what comes after it.  Only ``git``'s real ``.git`` check and
    each node's real required/resolved parents decide what's in this list,
    so entries here can be true siblings, not a serial lookahead.

    A node with an undecided `recommended` parent is withheld from this list
    entirely rather than merely ranked lower — see ``withheld_candidates()``
    for the matching "waiting on" list.

    When *fulfilled* is provided (a ``{node: bool}`` mapping), it is used
    instead of deriving from seed/bookkeeping — the seed-input contract that
    lets the script run graph-logic-only.
    """
    repo = pathlib.Path(repo)
    if tree is None:
        tree = load_tree()
    resolved = _resolve_fulfilled(repo, tree, fulfilled)
    resolved["git"] = True  # never proposed
    # Build the detected-like dict expected by graph helpers
    detected = {n: {"fulfilled": v} for n, v in resolved.items()}
    rejected = _rejected_nodes(repo)
    php_floor_blocked = {b["node"] for b in php_floor_precheck(repo)}

    result: list[dict] = []
    for node in tree["order"]:
        if node in _NEVER_PROPOSED:
            continue
        if tree["resolved_parents"].get(node):
            if node not in tree["exposed_resolved_gate_nodes"]:
                continue
            if not detected.get(node, {}).get("fulfilled", False):
                continue
            result.append({"node": node, "reason": f"resolved gate open for {node}"})
        else:
            if detected.get(node, {}).get("fulfilled", False):
                continue
            if node in rejected:
                continue
            if node in php_floor_blocked:
                continue
            if _recommended_gate_moot(node, tree, detected):
                continue
            ok, why = _is_unblocked(node, tree, detected)
            if not ok:
                continue
            if _undecided_recommended_parents(node, tree, detected, rejected):
                continue
            result.append({"node": node, "reason": why})
        if limit is not None and len(result) >= limit:
            break
    return result


def directly_unblocked_children(
    repo: pathlib.Path,
    landed_node: str,
    tree: dict | None = None,
    fulfilled: dict[str, bool] | None = None,
) -> list[dict]:
    """Every node this one candidate's fulfilment newly makes proposable —
    the fan-out an MR's outlook diagram draws
    (``opening-a-merge-request.md``).

    When *fulfilled* is provided, it is used instead of deriving from
    seed/bookkeeping — the seed-input contract.
    """
    repo = pathlib.Path(repo)
    if tree is None:
        tree = load_tree()
    if landed_node not in tree["nodes"]:
        return []

    resolved = _resolve_fulfilled(repo, tree, fulfilled)
    resolved["git"] = True
    detected = {n: {"fulfilled": v} for n, v in resolved.items()}
    rejected = _rejected_nodes(repo)

    # Counterfactual snapshot: landed_node never happened.
    # static-code-analyzer's own fulfilled flag is hardcoded to mirror
    # composer's (fulfilled state, above) rather than being independently
    # derived — keep that same derivation consistent here, or the
    # counterfactual would misreport composer's own downstream plumbing.
    if landed_node not in detected:
        return []
    detected_without = {k: dict(v) for k, v in detected.items()}
    detected_without[landed_node]["fulfilled"] = False
    if "static-code-analyzer" in detected_without:
        detected_without["static-code-analyzer"]["fulfilled"] = detected_without.get("composer", {}).get("fulfilled", False)

    gate_now = _resolved_gate_status(tree, lambda n: detected.get(n, {}).get("fulfilled", False), rejected)
    gate_without = _resolved_gate_status(tree, lambda n: detected_without.get(n, {}).get("fulfilled", False), rejected)
    # Build fulfilled dicts for next_candidates calls
    fulfilled_now = {n: v.get("fulfilled", False) for n, v in detected.items()}
    fulfilled_without = {n: v.get("fulfilled", False) for n, v in detected_without.items()}
    next_now = {c["node"] for c in next_candidates(repo, tree=tree, fulfilled=fulfilled_now)}
    next_without = {c["node"] for c in next_candidates(repo, tree=tree, fulfilled=fulfilled_without)}

    children_of: dict[str, list[dict]] = {}
    for e in tree["edges"]:
        children_of.setdefault(e["from"], []).append(e)

    result: list[dict] = []
    seen: set[str] = set()
    frontier: list[tuple[str, str]] = [(e["to"], e["type"]) for e in children_of.get(landed_node, [])]
    while frontier:
        child, edge_type = frontier.pop(0)
        if child in seen:
            continue
        seen.add(child)

        pass_through = child in _NEVER_PROPOSED or (
            tree["resolved_parents"].get(child) and child not in tree["exposed_resolved_gate_nodes"]
        )
        if pass_through:
            if tree["resolved_parents"].get(child):
                fulfilled_now_gate = gate_now.get(child, (False, []))[0]
            else:
                fulfilled_now_gate = detected.get(child, {}).get("fulfilled", False)
            if fulfilled_now_gate:
                frontier.extend((e["to"], e["type"]) for e in children_of.get(child, []))
            continue

        if child not in next_now:
            continue  # not a real candidate right now — blocked by something else too

        # Was this node already reachable before the landed node?
        if tree["resolved_parents"].get(child):
            already_before = gate_without.get(child, (False, []))[0]
        else:
            already_before = child in next_without
        if already_before:
            continue  # reachable via some other already-fulfilled parent too — not new

        result.append({"node": child, "type": edge_type})
    return result


def withheld_candidates(
    repo: pathlib.Path,
    tree: dict | None = None,
    fulfilled: dict[str, bool] | None = None,
) -> list[dict]:
    """Nodes that would otherwise be in ``next_candidates()`` (required
    parents fulfilled, not rejected, not yet fulfilled) but stay withheld
    because one or more ``recommended`` parents haven't reached a decided
    state yet.

    When *fulfilled* is provided, it is used instead of deriving from
    seed/bookkeeping — the seed-input contract.
    """
    result: list[dict] = []
    for node, why, undecided in _withheld_guard_cascade(repo, tree, fulfilled):
        if why is not None:
            continue  # blocked on a required parent — not the recommended-gate withholding this list reports
        result.append({"node": node, "waiting_on": undecided})
    return result


def detect_and_roadmap(
    repo: pathlib.Path,
    steps: int = 10,
    tree_md: pathlib.Path | None = None,
    fulfilled: dict[str, bool] | None = None,
    seed_path: pathlib.Path | None = None,
) -> dict:
    """Main entry point: compute graph outputs from fulfilled state.

    When *seed_path* is provided, it takes priority over *fulfilled*.
    When neither is given, the script derives state from bookkeeping.
    """
    tree = load_tree(tree_md=tree_md)
    repo = pathlib.Path(repo)
    # Resolve fulfilled state: seed_path > fulfilled param > bookkeeping
    if seed_path is not None and seed_path.exists():
        resolved_fulfilled = _load_fulfilled_seed(seed_path)
    else:
        resolved_fulfilled = fulfilled
    resolved = _resolve_fulfilled(repo, tree, resolved_fulfilled)
    detected = {n: {"fulfilled": v, "reason": "", "details": {}} for n, v in resolved.items()}
    nxt = next_candidates(repo, tree=tree, fulfilled=resolved_fulfilled)
    withheld = withheld_candidates(repo, tree=tree, fulfilled=resolved_fulfilled)
    reversals = php_version_reversal_findings(repo)
    php_floor_blocked = php_floor_precheck(repo)
    rejected = _rejected_nodes(repo)
    backlog = ordered_backlog(repo, tree=tree, fulfilled=resolved_fulfilled)
    closed = closed_by_rejection(tree, rejected)
    withheld_reasons = withheld_with_reasons(repo, tree=tree, fulfilled=resolved_fulfilled)
    return {
        "detected": detected,
        "next": nxt,
        "withheld": withheld,
        "withheld_with_reasons": withheld_reasons,
        "reversals": reversals,
        "php_floor_blocked": php_floor_blocked,
        "backlog": backlog,
        "closed_by_rejection": closed,
        "tree": {"edges": tree["edges"]},
    }


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser(description="Detect tooling tree and propose next MRs (dry-run, no mutation)")
    ap.add_argument("repo", nargs="?", default=".", help="path to fixture/repo (default: .)")
    ap.add_argument("--tree", type=str, default=None, help="path to a single tree file to use instead of the suite's own generic root + PHP tree (single-file mode, e.g. for a synthetic test tree)")
    ap.add_argument("--seed", type=str, default=None, help="path to a fulfilled-set JSON file (node_slug: true/false) — when provided, graph outputs are computed from it instead of detection")
    ap.add_argument("--json", action="store_true", help="output JSON (default)")
    ap.add_argument("--unblocked-by", type=str, default=None, metavar="NODE", help="add an 'unblocked_by' key: every node NODE's fulfilment newly makes proposable (outlook diagram)")
    args = ap.parse_args()
    repo = pathlib.Path(args.repo)
    tree_md = pathlib.Path(args.tree) if args.tree else None
    seed_path = pathlib.Path(args.seed) if args.seed else None
    data = detect_and_roadmap(repo, tree_md=tree_md, seed_path=seed_path)
    if args.unblocked_by:
        tree = load_tree(tree_md=tree_md)
        data["unblocked_by"] = directly_unblocked_children(repo, args.unblocked_by, tree=tree)
    print(json.dumps(data, indent=2))
