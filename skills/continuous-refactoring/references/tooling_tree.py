"""Deterministic graph-logic parser for the tooling tree.

Reads the tree docs and the target repository; the state of the nodes an
agent can judge (which are fulfilled, which rejected) is handed in by the
caller, the state of the aggregation nodes is computed from it. Emits, per
Track, whether it is fulfilled, the nodes a ticket can be filed for with
name, tool and search words, the ordered backlog (blocked nodes included)
and why a node is withheld — without invoking an LLM, keeping a file of
its own, or mutating the repo.

Docs: tooling-tree.md and php-tooling-tree.md (siblings to this file) are
machine-readable (edges table, node sections), CONTEXT.md vocabulary.
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

# The target's tracker file; its `## Refactoring operations` section is what
# onboarding leaves behind.
TRACKER_FILE = pathlib.PurePosixPath("docs/agents/issue-tracker.md")

_VALID_EDGE_TYPES = ("required", "recommended", "resolved", "required-any")

# Recognition-only nodes: they say something about the target (or merely
# organise the tree) and are never work to do, so no ticket is ever filed
# for one — `git` (never an MR), `static-code-analyzer` (pure plumbing),
# `psalm` (recognised when present, never suggested), `is-php-project` (the
# gate of the whole PHP specialization), and the three gates in front of
# `composer-audit` and the PHPStan level chain. The other two kinds of node
# without a ticket are derived, see `_gets_ticket`.
_NEVER_PROPOSED = {"git", "static-code-analyzer", "psalm", "is-php-project", "has-real-dependency", "phpstan-baseline-empty", "phpstan-not-psalm"}

# The two nodes whose state the parser reads off the target itself.
_OWN_NODES = {"git", "onboarding-setup"}

# ---------------------------------------------------------------------------
# Node state: handed in by the caller, never looked up
# ---------------------------------------------------------------------------


class SeedError(ValueError):
    """A handed-over seed file could not be used as given."""


def load_seed(seed_path: pathlib.Path, tree: dict) -> tuple[dict[str, bool], dict[str, dict | None]]:
    """Load a seed file — the node state as a caller hands it in on the
    command line — and return ``(fulfilled, rejected)`` in the shape the
    functions here take::

        {"fulfilled": ["composer", "phpunit"],
         "rejected": {"phpmd": null, "phpstan-level-0": {"php": "7.1"}}}

    ``rejected`` maps each rejected node to its blocker: ``null``, or the
    minimum PHP version whose arrival lifts the rejection. A plain list of
    slugs works where no rejection carries a blocker. A node named in
    neither is undecided.

    Anything else raises ``SeedError`` — a caller who handed over a
    judgement must never get outputs computed from something else. That
    includes a slug the tree doesn't know: a typo would otherwise turn a
    decided node silently into an undecided one.
    """
    seed_path = pathlib.Path(seed_path)

    def fail(problem: str) -> SeedError:
        return SeedError(f"seed file {seed_path} {problem}")

    try:
        data = json.loads(seed_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise fail(f"could not be read as JSON: {exc}") from exc
    shape = 'must hold a JSON object {"fulfilled": [slug, ...], "rejected": {slug: null | {"php": "X.Y"}}}'
    if not isinstance(data, dict) or set(data) - {"fulfilled", "rejected"}:
        raise fail(shape)

    fulfilled = data.get("fulfilled", [])
    if not isinstance(fulfilled, list) or not all(isinstance(n, str) for n in fulfilled):
        raise fail(f'{shape} — "fulfilled" is not a list of slugs')

    rejected = data.get("rejected", {})
    if isinstance(rejected, list) and all(isinstance(n, str) for n in rejected):
        rejected = {n: None for n in rejected}
    if not isinstance(rejected, dict):
        raise fail(f'{shape} — "rejected" is neither an object nor a list of slugs')
    for node, blocker in rejected.items():
        if blocker is not None and _blocked_by_php(blocker) is None:
            raise fail(f'has no usable blocker for {node}: expected null or {{"php": "X.Y"}}')

    unknown = sorted((set(fulfilled) | set(rejected)) - set(tree["nodes"]))
    if unknown:
        raise fail(f"names nodes the tree doesn't have: {', '.join(unknown)}")
    # what is handed in for a node the parser settles itself is ignored anyway
    both = sorted((set(fulfilled) & set(rejected)) - _OWN_NODES - _aggregation_nodes(tree))
    if both:
        raise fail(f"names nodes as both fulfilled and rejected: {', '.join(both)}")
    return {n: True for n in fulfilled}, rejected


def _guardrails_scope(tree: dict) -> set[str]:
    """Nodes of the Guardrails Track: every node with a required (or
    required-any) ancestor that is itself resolved-gated (PHP:
    ``php-safety-net``) — proposable only once the Safety Net has closed.
    Every other node belongs to the Safety Net Track."""
    gates = _aggregation_nodes(tree)
    scope: set[str] = set()
    changed = True
    while changed:
        changed = False
        for node in tree["nodes"]:
            if node in scope:
                continue
            parents = tree["required_parents"].get(node, []) + tree["required_any_parents"].get(node, [])
            if any(parent in gates or parent in scope for parent in parents):
                scope.add(node)
                changed = True
    return scope


def _aggregation_nodes(tree: dict) -> set[str]:
    """The nodes others reach through ``resolved`` edges (PHP:
    ``php-safety-net``, and ``structural-scan`` behind it)."""
    return {n for n, parents in tree["resolved_parents"].items() if parents}


def _gets_ticket(node: str, tree: dict) -> bool:
    """Whether a ticket can be filed for *node*. Not for a recognition-only
    node, not for one the parser settles itself, and not for an aggregation
    node — its leaves are where the work is."""
    return node not in _NEVER_PROPOSED and node not in _OWN_NODES and node not in _aggregation_nodes(tree)


def _node_state(repo: pathlib.Path, tree: dict, fulfilled, rejected) -> tuple[dict[str, bool], set[str]]:
    """The node state every output is computed from: what the caller handed
    in. A node named in neither *fulfilled* nor *rejected* is undecided.
    Some nodes the parser settles itself, whatever was handed in for them:
    ``git`` is fulfilled, ``onboarding-setup`` is fulfilled exactly when
    the target's tracker file carries its ``## Refactoring operations``
    section, and an aggregation node is fulfilled once its leaves are
    decided (see ``_with_aggregation_state``)."""
    own = _OWN_NODES | _aggregation_nodes(tree)
    state = {n: v for n, v in (fulfilled or {}).items() if n not in own}
    state["git"] = True
    state["onboarding-setup"] = _has_refactoring_operations(repo)
    rejected = set(rejected or ()) - own
    return _with_aggregation_state(tree, state, rejected), rejected


def _with_aggregation_state(tree: dict, state: dict[str, bool], rejected: set[str]) -> dict[str, bool]:
    """*state* with every aggregation node's fulfilment computed from its
    leaves: fulfilled once each leaf is fulfilled or rejected."""
    gates = _resolved_gate_status(tree, lambda n: state.get(n, False), rejected)
    return {**state, **{node: resolved for node, (resolved, _) in gates.items()}}


def _has_refactoring_operations(repo: pathlib.Path) -> bool:
    try:
        text = (pathlib.Path(repo) / TRACKER_FILE).read_text(encoding="utf-8")
    except OSError:
        return False
    return re.search(r"^## Refactoring operations\s*$", text, re.MULTILINE) is not None


def track_nodes(tree: dict) -> dict[str, list[dict]]:
    """Per Track, the nodes a ticket can be filed for, in tree order, each
    with the ``name`` and ``tool`` its node section gives as plain text
    (None where the tree doc has no section for it, or names no tool) and
    with ``search``, the words to look the node's ticket up by: name and
    tool, each once. Membership is derived from the edges, see
    ``_guardrails_scope``."""
    guardrails = _guardrails_scope(tree)
    sections = tree.get("sections", {})
    tracks: dict[str, list[dict]] = {"Safety Net": [], "Guardrails": []}
    for node in tree["order"]:
        if not _gets_ticket(node, tree):
            continue
        section = sections.get(node, {})
        name, tool = _plain(section.get("name")), _plain(section.get("tool"))
        if tool == "none":
            tool = None
        search = [name] if name else []
        if tool and tool.casefold() != (name or "").casefold():
            search.append(tool)
        tracks["Guardrails" if node in guardrails else "Safety Net"].append(
            {"node": node, "name": name, "tool": tool, "search": search}
        )
    return tracks


def _plain(field: str | None) -> str | None:
    """A node section's field without its Markdown backticks."""
    if field is None:
        return None
    return field.replace("`", "").strip() or None


def closed_by_rejection(tree: dict, rejected: set[str], fulfilled: dict[str, bool] | None = None) -> list[str]:
    """Nodes closed by a rejection — permanently closed for good, unlike
    merely unfulfilled nodes: a required ancestor is rejected, or a
    rejection leaves no member of a required-any group that could still be
    fulfilled (see ``_is_effectively_rejected``). *fulfilled* is the
    handed-in node state; it says which recognition-only nodes are
    fulfilled."""
    state = fulfilled or {}
    result = []
    for node in tree["order"]:
        if node in rejected:
            continue
        if _is_effectively_rejected(node, tree, rejected, fulfilled_lookup=lambda n: state.get(n, False)):
            result.append(node)
    return result


def _withheld_guard_cascade(
    repo: pathlib.Path,
    tree: dict | None = None,
    fulfilled: dict[str, bool] | None = None,
    rejected=None,
):
    """The guard cascade withheld_with_reasons() and withheld_candidates()
    share: takes the handed-in node state, then yields ``(node, blocked_reason,
    undecided_parents)`` for every node that survives the common guards
    (gets a ticket, not fulfilled, not rejected,
    recommended gate not moot) and is either blocked — below its PHP floor
    or on a required parent (``blocked_reason`` set, ``undecided_parents``
    None — never computed, the node never gets that far) — or waiting on
    undecided recommended parents (``blocked_reason`` None)."""
    repo = pathlib.Path(repo)
    if tree is None:
        tree = load_tree()
    state, rejected = _node_state(repo, tree, fulfilled, rejected)
    detected = {n: {"fulfilled": v} for n, v in state.items()}
    php_floor_blocked = {b["node"]: b["reason"] for b in php_floor_precheck(repo)}
    for node in tree["order"]:
        if not _gets_ticket(node, tree):
            continue
        if detected.get(node, {}).get("fulfilled", False) or node in rejected:
            continue
        if node in php_floor_blocked:
            yield node, php_floor_blocked[node], None
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
    rejected=None,
) -> list[dict]:
    """Withheld nodes with reasons: below the PHP floor, blocked by an
    unfulfilled required parent, or waiting on undecided recommended
    parents."""
    result: list[dict] = []
    for node, why, undecided in _withheld_guard_cascade(repo, tree, fulfilled, rejected):
        if why is not None:
            result.append({"node": node, "reason": why})
        else:
            result.append({"node": node, "reason": f"waiting on: {', '.join(undecided)}"})
    return result


def ordered_backlog(
    repo: pathlib.Path,
    tree: dict | None = None,
    fulfilled: dict[str, bool] | None = None,
    rejected=None,
) -> list[str]:
    """Complete ordered list of the nodes a ticket can be filed for that
    are neither fulfilled nor rejected, in tree order, blocked nodes
    included — the nodes a scan offers tickets for."""
    repo = pathlib.Path(repo)
    if tree is None:
        tree = load_tree()
    resolved, rejected = _node_state(repo, tree, fulfilled, rejected)
    closed = set(closed_by_rejection(tree, rejected, resolved))
    backlog = []
    for node in tree["order"]:
        if not _gets_ticket(node, tree):
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


_SECTION_HEADING = re.compile(r"^### `([^`]+)`(?: through `([^`]+)`)?\s*$")
_SECTION_FIELD = re.compile(r"^- \*\*(Names?|Tool):\*\*\s*(.*)$")
_TRAILING_NUMBER = re.compile(r"^(.*?)(\d+)$")


def _section_slugs(heading: str) -> tuple[list[str], dict[str, str]]:
    """The slugs a heading line opens a node section for, plus — for a
    numbered run — each slug's number. No node section: ``([], {})``."""
    match = _SECTION_HEADING.match(heading)
    if not match:
        return [], {}
    first, last = match.group(1), match.group(2)
    lo, hi = _TRAILING_NUMBER.match(first), _TRAILING_NUMBER.match(last or "")
    if lo and hi and lo.group(1) == hi.group(1):
        numbers = {f"{lo.group(1)}{n}": str(n) for n in range(int(lo.group(2)), int(hi.group(2)) + 1)}
        return list(numbers), numbers
    return [first], {}


def _parse_node_sections(path: pathlib.Path) -> dict[str, dict]:
    """Each node section's ``**Name:**`` and ``**Tool:**`` fields, keyed by
    slug: ``{slug: {"name": ..., "tool": ...}}``, the field text as written
    (None for a field the section lacks).

    A section heading is ``### `slug```. One heading may cover a numbered
    run of nodes (``### `x-1` through `x-10```); its ``**Names:**`` field
    then holds a quoted template with ``N`` standing for the number."""
    sections: dict[str, dict] = {}
    slugs: list[str] = []
    numbers: dict[str, str] = {}
    fields: dict[str, str] = {}
    field: str | None = None

    def close_section() -> None:
        for slug in slugs:
            name = fields.get("name")
            template = re.search(r'"([^"]*\bN\b[^"]*)"', name or "") if slug in numbers else None
            if template:
                name = re.sub(r"\bN\b", numbers[slug], template.group(1))
            sections[slug] = {"name": name, "tool": fields.get("tool")}

    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("#"):
            close_section()
            (slugs, numbers), fields, field = _section_slugs(line), {}, None
            continue
        match = _SECTION_FIELD.match(line)
        if match:
            field = "tool" if match.group(1) == "Tool" else "name"
            fields[field] = match.group(2).strip()
        elif field and line[:1].isspace() and line.strip():
            fields[field] += " " + line.strip()  # a field wrapped onto the next line
        else:
            field = None
    close_section()
    return sections


def load_tree(tree_md: pathlib.Path | None = None) -> dict:
    """Load the tree's edges and node sections.

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
    sections: dict[str, dict] = {}
    for path in paths:
        if path.exists():
            edges.extend(_parse_edges(path))
            sections.update(_parse_node_sections(path))
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
        "sections": {n: sections[n] for n in nodes if n in sections},
    }


def _read_composer(repo: pathlib.Path) -> dict | None:
    for cand in [repo / "composer.json", repo / "composer" / "composer.json"]:
        if cand.exists():
            try:
                return json.loads(cand.read_text(encoding="utf-8"))
            except Exception:
                return None
    return None


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


# The oldest PHP version each of the five deterministic PHP tooling leaves
# has ever run on, across every published major line of the
# tool — below this floor, no version of the tool (however old or
# unmaintained) can be installed at all, so no
# ticket could ever land it. Checked once per call instead of once
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
    fact at once instead of it silently vanishing.

    Design decision: skip silently, a blocked leaf is not a rejection.
    The check is cheap and re-derived fully from `composer.json` every
    call — a rejection records a genuine human/agent decision, not a
    mechanical fact already on disk. Once the target's PHP floor rises, a
    previously-blocked leaf is simply unblocked; there is nothing to
    reverse. The one consequence worth naming: `phpunit` is the only one
    of these five nodes that's still a `php-safety-net` leaf (php-tooling-
    tree.md's `resolved` edges) — while blocked here, it counts as neither
    fulfilled nor rejected, so `structural-scan` stays genuinely closed
    until the floor rises (matching how a target that truly cannot run
    these tools yet shouldn't be treated as tooling-ready). `composer-audit`
    is no longer a `php-safety-net` leaf either (moved to the Guardrails
    instead) — like
    `php-cs-fixer`/`test-runner-if-missing`, a floor block on it now only
    delays its own adoption. A human who wants `structural-scan` to open
    anyway despite the floor can still reject those leaves by
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


def _blocked_by_php(blocker) -> tuple[int, ...] | None:
    """The minimum PHP version a rejection's blocker names
    (``{"php": "8.1"}``), or None when the rejection carries none."""
    if not isinstance(blocker, dict) or set(blocker) != {"php"} or not isinstance(blocker["php"], str):
        return None
    return _parse_min_version(blocker["php"])


def php_version_reversal_findings(repo: pathlib.Path, rejected=None) -> list[dict]:
    """Rejected nodes whose handed-in blocker (``{node: {"php": "X.Y"}}``)
    the target's PHP floor now satisfies — findings the caller offers for
    reversal; the node stays rejected until the caller reverses it."""
    repo = pathlib.Path(repo)
    current = _current_php_floor(_read_composer(repo))
    if current is None or not isinstance(rejected, dict):
        return []
    findings = []
    for node in sorted(rejected):
        blocked_by = _blocked_by_php(rejected[node])
        if blocked_by is not None and current >= blocked_by:
            findings.append({
                "node": node,
                "reason": (
                    f"PHP floor now {'.'.join(map(str, current))}, satisfies "
                    f"Blocked by PHP >= {'.'.join(map(str, blocked_by))}"
                ),
            })
    return findings


def _is_effectively_rejected(
    node: str, tree: dict, rejected: set[str], _seen: set[str] | None = None, fulfilled_lookup=None
) -> bool:
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

    A `required-any` group only closes this way once *no* option is left
    that could be fulfilled: each one effectively rejected, or a
    recognition-only node (`_NEVER_PROPOSED`) that is not fulfilled — no
    ticket is ever filed for such a node, so nothing a run does fulfils it
    (e.g. `rector-php-set` behind a rejected `phpstan-level-0` on a target
    without `psalm`). Rejecting just one of several options must not close
    the child while another could still fulfil it, and without any
    rejection in the group nothing is closed: the closure follows the
    rejection and is gone with it. ``fulfilled_lookup(name) -> bool``
    supplies the handed-in state; without it no node is fulfilled.

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
        _is_effectively_rejected(p, tree, rejected, set(_seen), fulfilled_lookup)
        for p in tree["required_parents"].get(node, [])
    ):
        return True
    req_any = tree["required_any_parents"].get(node, [])
    rejected_options = {
        p for p in req_any if _is_effectively_rejected(p, tree, rejected, set(_seen), fulfilled_lookup)
    }
    never_fulfilled = {
        p for p in req_any
        if p in _NEVER_PROPOSED and not (fulfilled_lookup is not None and fulfilled_lookup(p))
    }
    return bool(rejected_options) and rejected_options | never_fulfilled == set(req_any)


def _is_decided(node: str, tree: dict, detected: dict, rejected: set[str]) -> bool:
    """True once `node` has reached a final state for `recommended`-edge
    gating purposes (CONTEXT.md's Recommended edge): fulfilled, or
    effectively rejected (see above) — not merely "not yet reached"."""
    def is_fulfilled(name: str) -> bool:
        return detected.get(name, {}).get("fulfilled", False)

    return is_fulfilled(node) or _is_effectively_rejected(node, tree, rejected, fulfilled_lookup=is_fulfilled)


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
    analyzer adopted) that no run or human ever decides on — unlike
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
    reach a decided state through a run's ordinary work (e.g.
    `rector-type-coverage` on a non-PHP target, whose four recommended
    parents all bottom out at the unfulfilled `is-php-project` gate, despite
    `rector-type-coverage` itself carrying no required parent of its own to
    be blocked by directly)."""
    parents = tree["recommended_parents"].get(node, [])
    return bool(parents) and all(_is_permanently_gated(p, tree, detected) for p in parents)


def _resolved_gate_status(
    tree: dict, fulfilled_lookup, rejected: set[str]
) -> dict[str, tuple[bool, list[str]]]:
    """Compute ``{node: (resolved, unresolved_leaves)}`` for every node with
    one or more `resolved` parents — generic over any such node (today:
    ``structural-scan``, and PHP's own aggregation node ``php-safety-net``
    feeding it), not hardcoded to one node name. A node is resolved
    once every one of its resolved-parent leaves is itself fulfilled,
    recorded as rejected, or effectively rejected (``_is_effectively_rejected``
    — closed for good because a required ancestor of the leaf is rejected or
    its whole required-any group is out of reach, even though the leaf
    itself was never explicitly rejected) — unlike a
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
    computed: dict[str, tuple[bool, list[str]]] = {}
    pending = _aggregation_nodes(tree)
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
                    or _is_effectively_rejected(leaf, tree, rejected, fulfilled_lookup=fulfilled_lookup)
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
    rejected=None,
) -> list[dict]:
    """Return every node a ticket can be filed for that is *really*
    unblocked and unfulfilled right now (or, with an explicit `limit`, at most that many — a scan itself
    never passes one: more than five nodes can be genuinely unblocked at
    once, so this is never capped by default).

    Does not simulate — does not assume a returned node is already fulfilled
    to compute what comes after it.  Only each node's real required
    parents decide what's in this list, so entries here can be true
    siblings, not a serial lookahead.

    A node with an undecided `recommended` parent is withheld from this list
    entirely rather than merely ranked lower — see ``withheld_candidates()``
    for the matching "waiting on" list.

    *fulfilled* (a ``{node: bool}`` mapping) and *rejected* (the rejected
    nodes' slugs) are the node state the caller hands in; a node named in
    neither is undecided.
    """
    repo = pathlib.Path(repo)
    if tree is None:
        tree = load_tree()
    state, rejected = _node_state(repo, tree, fulfilled, rejected)
    detected = {n: {"fulfilled": v} for n, v in state.items()}
    return _next_candidates(repo, tree, detected, rejected, limit)


def _next_candidates(
    repo: pathlib.Path, tree: dict, detected: dict, rejected: set[str], limit: int | None = None
) -> list[dict]:
    """next_candidates() over an already-resolved node state."""
    php_floor_blocked = {b["node"] for b in php_floor_precheck(repo)}

    result: list[dict] = []
    for node in tree["order"]:
        if not _gets_ticket(node, tree):
            continue
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
    rejected=None,
) -> list[dict]:
    """Every node this one candidate's fulfilment newly makes proposable.
    A node no ticket is filed for is walked through to what it opens in
    turn.

    *fulfilled* and *rejected* are the handed-in node state, as for
    ``next_candidates()``.
    """
    repo = pathlib.Path(repo)
    if tree is None:
        tree = load_tree()
    if landed_node not in tree["nodes"]:
        return []

    state, rejected = _node_state(repo, tree, fulfilled, rejected)
    detected = {n: {"fulfilled": v} for n, v in state.items()}

    # Counterfactual snapshot: landed_node never happened.
    # static-code-analyzer's own fulfilled flag is hardcoded to mirror
    # composer's (fulfilled state, above) rather than being independently
    # derived — keep that same derivation consistent here, or the
    # counterfactual would misreport composer's own downstream plumbing.
    if landed_node not in detected:
        return []
    without = {**state, landed_node: False}
    if "static-code-analyzer" in without:
        without["static-code-analyzer"] = without.get("composer", False)
    without = _with_aggregation_state(tree, without, rejected)
    detected_without = {n: {"fulfilled": v} for n, v in without.items()}

    next_now = {c["node"] for c in _next_candidates(repo, tree, detected, rejected)}
    next_without = {c["node"] for c in _next_candidates(repo, tree, detected_without, rejected)}

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

        if not _gets_ticket(child, tree):
            if detected.get(child, {}).get("fulfilled", False):
                frontier.extend((e["to"], e["type"]) for e in children_of.get(child, []))
            continue

        if child not in next_now:
            continue  # not a real candidate right now — blocked by something else too
        if child in next_without:
            continue  # reachable via some other already-fulfilled parent too — not new

        result.append({"node": child, "type": edge_type})
    return result


def withheld_candidates(
    repo: pathlib.Path,
    tree: dict | None = None,
    fulfilled: dict[str, bool] | None = None,
    rejected=None,
) -> list[dict]:
    """Nodes that would otherwise be in ``next_candidates()`` (required
    parents fulfilled, not rejected, not yet fulfilled) but stay withheld
    because one or more ``recommended`` parents haven't reached a decided
    state yet.

    *fulfilled* and *rejected* are the handed-in node state, as for
    ``next_candidates()``.
    """
    result: list[dict] = []
    for node, why, undecided in _withheld_guard_cascade(repo, tree, fulfilled, rejected):
        if why is not None:
            continue  # blocked outright — not the recommended-gate withholding this list reports
        result.append({"node": node, "waiting_on": undecided})
    return result


def detect_and_roadmap(
    repo: pathlib.Path,
    steps: int = 10,
    tree_md: pathlib.Path | None = None,
    fulfilled: dict[str, bool] | None = None,
    seed_path: pathlib.Path | None = None,
    rejected=None,
) -> dict:
    """Main entry point: compute graph outputs from the handed-in node state.

    The state comes from *seed_path* (see ``load_seed``; it must be usable
    as given, otherwise ``SeedError`` is raised) or from
    *fulfilled*/*rejected*. With none of them, every node is undecided.
    """
    tree = load_tree(tree_md=tree_md)
    repo = pathlib.Path(repo)
    if seed_path is not None:
        fulfilled, rejected = load_seed(seed_path, tree)
    state, rejected_nodes = _node_state(repo, tree, fulfilled, rejected)
    backlog = ordered_backlog(repo, tree=tree, fulfilled=fulfilled, rejected=rejected)
    withheld_reasons = withheld_with_reasons(repo, tree=tree, fulfilled=fulfilled, rejected=rejected)
    tracks = {}
    for track, nodes in track_nodes(tree).items():
        members = {n["node"] for n in nodes}
        track_backlog = [n for n in backlog if n in members]
        tracks[track] = {
            # every node of the Track is fulfilled or rejected
            "fulfilled": not track_backlog,
            "nodes": nodes,
            "backlog": track_backlog,
            "withheld": [w for w in withheld_reasons if w["node"] in members],
        }
    return {
        "detected": {n: {"fulfilled": v, "reason": "", "details": {}} for n, v in state.items()},
        "tracks": tracks,
        "next": next_candidates(repo, tree=tree, fulfilled=fulfilled, rejected=rejected),
        "withheld": withheld_candidates(repo, tree=tree, fulfilled=fulfilled, rejected=rejected),
        "withheld_with_reasons": withheld_reasons,
        "reversals": php_version_reversal_findings(repo, rejected),
        "php_floor_blocked": php_floor_precheck(repo),
        "backlog": backlog,
        "closed_by_rejection": closed_by_rejection(tree, rejected_nodes, state),
        "tree": {"edges": tree["edges"]},
    }


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser(description="Compute the tooling tree's graph outputs from a handed-in node state (dry-run, no mutation)")
    ap.add_argument("repo", nargs="?", default=".", help="path to fixture/repo (default: .)")
    ap.add_argument("--tree", type=str, default=None, help="path to a single tree file to use instead of the suite's own generic root + PHP tree (single-file mode, e.g. for a synthetic test tree)")
    ap.add_argument("--seed", type=str, default=None, help='path to a JSON file holding the node state: {"fulfilled": [slug, ...], "rejected": {slug: null | {"php": "X.Y"}}} — without it, every node is undecided')
    ap.add_argument("--json", action="store_true", help="output JSON (default)")
    ap.add_argument("--unblocked-by", type=str, default=None, metavar="NODE", help="add an 'unblocked_by' key: every node NODE's fulfilment newly makes proposable")
    args = ap.parse_args()
    repo = pathlib.Path(args.repo)
    tree_md = pathlib.Path(args.tree) if args.tree else None
    tree = load_tree(tree_md=tree_md)
    fulfilled = rejected = None
    if args.seed:
        try:
            fulfilled, rejected = load_seed(pathlib.Path(args.seed), tree)
        except SeedError as exc:
            ap.exit(2, f"error: {exc}\n")
    data = detect_and_roadmap(repo, tree_md=tree_md, fulfilled=fulfilled, rejected=rejected)
    if args.unblocked_by:
        data["unblocked_by"] = directly_unblocked_children(repo, args.unblocked_by, tree=tree, fulfilled=fulfilled, rejected=rejected)
    print(json.dumps(data, indent=2))
