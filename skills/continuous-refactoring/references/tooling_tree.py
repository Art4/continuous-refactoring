"""Deterministic graph-logic parser for the tooling model: Roles, Tools and Stages in Packs.

Reads the Packs (``packs/*/pack.json``) and ``roles.json`` beside this file and
the tracker file of the target repository. What an agent can judge — which
Stages are fulfilled, which subjects are rejected, which Packs apply, the
target's runtime — is handed in as a seed; everything else is computed from it.
Emits, per Track, whether it is fulfilled, the Stages a ticket can be filed
for with name, tool and search words, the ordered backlog, and why a Stage is
withheld — without invoking an LLM, keeping a file of its own, or mutating
the repo. Standard library only.

Vocabulary and rules: tooling-model.md (beside this file).
"""

from __future__ import annotations

import json
import pathlib
import re

_HERE = pathlib.Path(__file__).resolve().parent
PACKS_DIR = _HERE / "packs"
ROLES_JSON = _HERE / "roles.json"

# The target's tracker file; its `## Refactoring operations` section is what
# onboarding leaves behind.
TRACKER_FILE = pathlib.PurePosixPath("docs/agents/issue-tracker.md")

# In the order a run works them; a Stage may require only Stages of the same
# or an earlier Track.
TRACKS = ("Safety Net", "Guardrails")

# The suite's own prerequisites: no Pack holds them, a seed may mention them
# and is ignored for them.
PREREQUISITES = ("git", "onboarding-setup")

_SLUG = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
_VERSION = re.compile(r"\d+(?:\.\d+)*")


class PackError(ValueError):
    """A Pack or the roles file could not be used as it is."""


class SeedError(ValueError):
    """A handed-over seed file could not be used as given."""


# ---------------------------------------------------------------------------
# Versions: best effort, numbers only
# ---------------------------------------------------------------------------


def _version(text) -> tuple[int, ...] | None:
    """The first run of dotted numbers in *text* (``'>=7.2'``, ``'8.1.3'``),
    or None where there is none. Best effort: a value it cannot read blocks
    nothing."""
    if not isinstance(text, str):
        return None
    match = _VERSION.search(text)
    return tuple(int(part) for part in match.group(0).split(".")) if match else None


def _below(current: tuple[int, ...], minimum: tuple[int, ...]) -> bool:
    width = max(len(current), len(minimum))
    pad = lambda v: v + (0,) * (width - len(v))  # noqa: E731
    return pad(current) < pad(minimum)


def _dotted(version: tuple[int, ...]) -> str:
    return ".".join(map(str, version))


# ---------------------------------------------------------------------------
# Loading and checking the model
# ---------------------------------------------------------------------------


def _read_json(path: pathlib.Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PackError(f"{path} could not be read as JSON: {exc}") from exc


def _need(condition: bool, where: str, problem: str) -> None:
    if not condition:
        raise PackError(f"{where}: {problem}")


def _is_slug(value) -> bool:
    return isinstance(value, str) and _SLUG.match(value) is not None


def _is_text(value) -> bool:
    return isinstance(value, str) and bool(value.strip())


def load_roles(roles_json: pathlib.Path | None = None) -> dict[str, dict]:
    path = pathlib.Path(roles_json or ROLES_JSON)
    data = _read_json(path)
    _need(isinstance(data, dict) and isinstance(data.get("roles"), list), str(path), 'must hold {"roles": [...]}')
    roles: dict[str, dict] = {}
    for item in data["roles"]:
        _need(isinstance(item, dict), str(path), "a role is not an object")
        slug = item.get("slug")
        _need(_is_slug(slug), str(path), f"role slug {slug!r} is not a slug")
        _need(slug not in roles, str(path), f"role {slug} is listed twice")
        _need(_is_text(item.get("name")) and _is_text(item.get("purpose")), str(path), f"role {slug} needs a name and a purpose")
        _need(item.get("signal") is None or _is_text(item.get("signal")), str(path), f"role {slug}: signal must be text or null")
        roles[slug] = item
    return roles


def _pack_paths(packs_dir: pathlib.Path) -> list[pathlib.Path]:
    """``generic`` first, the other Packs in name order."""
    paths = sorted(packs_dir.glob("*/pack.json"), key=lambda p: (p.parent.name != "generic", p.parent.name))
    return paths


def load_model(packs_dir: pathlib.Path | None = None, roles_json: pathlib.Path | None = None) -> dict:
    """Load Roles and Packs and check what the parser computes with. Raises
    ``PackError`` for a model it cannot compute from.

    Returns ``roles`` (slug -> role), ``packs`` (name -> pack), ``tools``
    (slug -> tool, with ``pack`` and the slugs of its ``stage_slugs``),
    ``stages`` (slug -> stage, with ``tool``, ``pack``, ``first`` and
    ``index``) and ``stage_order`` (the Stages in the order of the Packs).
    """
    packs_dir = pathlib.Path(packs_dir or PACKS_DIR)
    roles = load_roles(roles_json)
    paths = _pack_paths(packs_dir)
    _need(bool(paths), str(packs_dir), "holds no pack.json")

    packs: dict[str, dict] = {}
    tools: dict[str, dict] = {}
    stages: dict[str, dict] = {}
    stage_order: list[str] = []
    for path in paths:
        data = _read_json(path)
        where = str(path)
        _need(isinstance(data, dict), where, "must be an object")
        name = data.get("pack")
        _need(_is_slug(name), where, f"pack name {name!r} is not a slug")
        _need(name not in packs, where, f"pack {name} is listed twice")
        scope = data.get("scope")
        _need(scope is None or _is_slug(scope), where, f"scope {scope!r} is not a slug")
        _need(_is_text(data.get("applies_when")), where, "needs an applies_when sentence")
        _need(isinstance(data.get("tools"), list) and data["tools"], where, "needs a list of tools")
        packs[name] = {"pack": name, "dir": path.parent, "scope": scope, "applies_when": data["applies_when"], "tools": []}
        for tool in data["tools"]:
            _need(isinstance(tool, dict), where, "a tool is not an object")
            slug = tool.get("tool")
            _need(_is_slug(slug), where, f"tool slug {slug!r} is not a slug")
            _need(slug not in tools, where, f"tool {slug} is listed twice")
            _need(slug not in roles, where, f"tool {slug} has the slug of a role")
            _need(_is_text(tool.get("name")), where, f"tool {slug} needs a name")
            _need(tool.get("uses") is None or _is_text(tool.get("uses")), where, f"tool {slug}: uses must be text or null")
            _need(tool.get("status") in ("recommended", "recognized"), where, f"tool {slug}: status must be recommended or recognized")
            _need(_is_text(tool.get("details")), where, f"tool {slug} needs a details file")
            tool_roles = tool.get("roles")
            _need(isinstance(tool_roles, list) and tool_roles, where, f"tool {slug} must play at least one role")
            for role in tool_roles:
                _need(role in roles, where, f"tool {slug} plays the unknown role {role!r}")
            min_runtime = tool.get("min_runtime", {})
            _need(
                isinstance(min_runtime, dict) and all(isinstance(k, str) and isinstance(v, str) for k, v in min_runtime.items()),
                where,
                f"tool {slug}: min_runtime must map runtime names to version strings",
            )
            _need(isinstance(tool.get("stages"), list) and tool["stages"], where, f"tool {slug} needs at least one stage")
            entry = {**tool, "pack": name, "dir": path.parent, "scope": scope, "stage_slugs": []}
            tools[slug] = entry
            packs[name]["tools"].append(slug)
            for index, stage in enumerate(tool["stages"]):
                _need(isinstance(stage, dict), where, f"a stage of {slug} is not an object")
                sslug = stage.get("slug")
                _need(_is_slug(sslug), where, f"stage slug {sslug!r} is not a slug")
                _need(sslug not in stages, where, f"stage {sslug} is listed twice")
                _need(sslug not in roles, where, f"stage {sslug} has the slug of a role")
                _need(_is_text(stage.get("name")), where, f"stage {sslug} needs a name")
                _need(stage.get("track") in TRACKS, where, f"stage {sslug}: track must be one of {', '.join(TRACKS)}")
                _need(isinstance(stage.get("requires"), list), where, f"stage {sslug}: requires must be a list")
                _need(isinstance(stage.get("after"), list), where, f"stage {sslug}: after must be a list")
                _need(
                    stage.get("applies_when") is None or _is_text(stage.get("applies_when")),
                    where,
                    f"stage {sslug}: applies_when must be text",
                )
                stages[sslug] = {**stage, "tool": slug, "pack": name, "scope": scope, "index": index, "first": index == 0}
                entry["stage_slugs"].append(sslug)
                stage_order.append(sslug)

    # a Tool and a Stage may share a slug only when the Stage is the Tool's only one
    for slug, tool in tools.items():
        if slug in stages:
            _need(
                tool["stage_slugs"] == [slug],
                slug,
                "a tool may share its slug with a stage only when that stage is its only one",
            )

    model = {"roles": roles, "packs": packs, "tools": tools, "stages": stages, "stage_order": stage_order}
    _check_references(model)
    return model


def _track_rank(track: str) -> int:
    return TRACKS.index(track)


def _role_tools(model: dict, role: str, scope: str | None) -> list[str]:
    """The Tools that can fill *role* for a Stage of *scope*: those of the same
    scope, or every Tool of the Role for a Stage that has none."""
    return [
        t for t, tool in model["tools"].items()
        if role in tool["roles"] and (scope is None or tool["scope"] == scope)
    ]


def _check_references(model: dict) -> None:
    roles, tools, stages = model["roles"], model["tools"], model["stages"]
    for slug, stage in stages.items():
        rank = _track_rank(stage["track"])
        for item in stage["requires"]:
            members = item if isinstance(item, list) else [item]
            _need(not isinstance(item, list) or len(item) >= 2, slug, "an any-of group needs at least two members")
            for member in members:
                _need(_is_slug(member), slug, f"requires {member!r} is not a slug")
                if isinstance(item, list):
                    _need(member in stages, slug, f"any-of group names {member}, which is not a stage")
                _need(member in stages or member in roles, slug, f"requires {member}, which is neither a stage nor a role")
                _need(member != slug, slug, "requires itself")
                if member in stages:
                    firsts = [stages[member]]
                else:
                    firsts = [stages[tools[t]["stage_slugs"][0]] for t in _role_tools(model, member, stage["scope"])]
                    _need(
                        bool(firsts),
                        slug,
                        f"requires the role {member}, which no tool of the scope {stage['scope']} plays",
                    )
                for parent in firsts:
                    _need(
                        _track_rank(parent["track"]) <= rank,
                        slug,
                        f"requires {parent['slug']}, which is in the later Track {parent['track']}",
                    )
        for after in stage["after"]:
            _need(after in stages, slug, f"after {after}, which is not a stage")
            _need(after != slug, slug, "is after itself")

    # no cycles over requires, role requirements and after
    def deps(slug: str) -> list[str]:
        stage = stages[slug]
        found: list[str] = []
        for item in stage["requires"]:
            for member in item if isinstance(item, list) else [item]:
                if member in stages:
                    found.append(member)
                else:
                    found.extend(tools[t]["stage_slugs"][0] for t in _role_tools(model, member, stage["scope"]))
        found.extend(stage["after"])
        return found

    state: dict[str, int] = {}

    def visit(slug: str, trail: list[str]) -> None:
        if state.get(slug) == 2:
            return
        _need(state.get(slug) != 1, slug, "is part of a cycle: " + " -> ".join(trail + [slug]))
        state[slug] = 1
        for dep in deps(slug):
            visit(dep, trail + [slug])
        state[slug] = 2

    for slug in model["stage_order"]:
        visit(slug, [])


# ---------------------------------------------------------------------------
# The seed: what the caller judged
# ---------------------------------------------------------------------------


def _blocker(value) -> tuple[str, tuple[int, ...]] | None:
    """A rejection's blocker ``{"php": "8.1"}`` as (runtime, version), or None."""
    if not isinstance(value, dict) or len(value) != 1:
        return None
    (runtime, text), = value.items()
    version = _version(text)
    return (runtime, version) if version is not None else None


def load_seed(seed_path: pathlib.Path, model: dict) -> dict:
    """Load a seed file and return it checked and in one shape::

        {"fulfilled": ["composer"],
         "rejected": {"phpmd": null, "static-analysis": null, "phpstan-level-0": {"php": "7.1"}},
         "packs": ["generic", "php"],
         "not_applicable": ["composer-audit"],
         "runtime": {"php": "7.4"}}

    ``fulfilled`` names Stages. ``rejected`` names a Role, a Tool or a Stage
    and maps it to its blocker: ``null``, or the minimum runtime whose arrival
    lifts the rejection (a plain list of slugs works where no rejection
    carries one). ``packs`` lists the Packs that apply (all, when it is
    missing), ``not_applicable`` the Stages whose own condition does not hold,
    ``runtime`` the lowest runtime the target allows, as a string.

    Anything else raises ``SeedError``: a judgement handed over is never
    answered with outputs computed from something else. That includes a name
    the model doesn't know, since a typo would otherwise turn a decided
    subject silently into an undecided one.
    """
    seed_path = pathlib.Path(seed_path)

    def fail(problem: str) -> SeedError:
        return SeedError(f"seed file {seed_path} {problem}")

    try:
        data = json.loads(seed_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise fail(f"could not be read as JSON: {exc}") from exc
    shape = (
        'must hold a JSON object {"fulfilled": [stage, ...], "rejected": {role|tool|stage: null | {"php": "X.Y"}}, '
        '"packs": [pack, ...], "not_applicable": [stage, ...], "runtime": {"php": "X.Y"}}'
    )
    allowed = {"fulfilled", "rejected", "packs", "not_applicable", "runtime"}
    if not isinstance(data, dict) or set(data) - allowed:
        raise fail(shape)

    def names(key: str) -> list[str]:
        value = data.get(key, [])
        if not isinstance(value, list) or not all(isinstance(n, str) for n in value):
            raise fail(f'{shape} — "{key}" is not a list of names')
        return value

    fulfilled = [n for n in names("fulfilled") if n not in PREREQUISITES]
    unknown = sorted(set(fulfilled) - set(model["stages"]))
    if unknown:
        raise fail(f"names stages the model doesn't have in \"fulfilled\": {', '.join(unknown)}")

    rejected = data.get("rejected", {})
    if isinstance(rejected, list) and all(isinstance(n, str) for n in rejected):
        rejected = {n: None for n in rejected}
    if not isinstance(rejected, dict):
        raise fail(f'{shape} — "rejected" is neither an object nor a list of names')
    rejected = {n: b for n, b in rejected.items() if n not in PREREQUISITES}
    for subject, blocker in rejected.items():
        if blocker is not None and _blocker(blocker) is None:
            raise fail(f'has no usable blocker for {subject}: expected null or {{"php": "X.Y"}}')
    known = set(model["roles"]) | set(model["tools"]) | set(model["stages"])
    unknown = sorted(set(rejected) - known)
    if unknown:
        raise fail(f"names subjects the model doesn't have in \"rejected\": {', '.join(unknown)}")
    both = sorted(set(fulfilled) & set(rejected))
    if both:
        raise fail(f"names stages as both fulfilled and rejected: {', '.join(both)}")

    packs = data.get("packs")
    if packs is not None:
        packs = names("packs")
        unknown = sorted(set(packs) - set(model["packs"]))
        if unknown:
            raise fail(f"names packs the model doesn't have: {', '.join(unknown)}")
    not_applicable = names("not_applicable")
    unknown = sorted(set(not_applicable) - set(model["stages"]))
    if unknown:
        raise fail(f"names stages the model doesn't have in \"not_applicable\": {', '.join(unknown)}")

    runtime = data.get("runtime", {})
    if not isinstance(runtime, dict) or not all(isinstance(k, str) and isinstance(v, str) for k, v in runtime.items()):
        raise fail('"runtime" must map runtime names to version strings')
    return {"fulfilled": fulfilled, "rejected": rejected, "packs": packs, "not_applicable": not_applicable, "runtime": runtime}


# ---------------------------------------------------------------------------
# Computing
# ---------------------------------------------------------------------------


def _has_refactoring_operations(repo: pathlib.Path) -> bool:
    try:
        text = (pathlib.Path(repo) / TRACKER_FILE).read_text(encoding="utf-8")
    except OSError:
        return False
    return re.search(r"^## Refactoring operations\s*$", text, re.MULTILINE) is not None


class _State:
    """Everything computed from a model and a seed, once."""

    def __init__(self, model: dict, seed: dict, onboarded: bool):
        self.model = model
        self.seed = seed
        self.onboarded = onboarded
        stages, tools, roles = model["stages"], model["tools"], model["roles"]

        packs = seed["packs"] if seed["packs"] is not None else list(model["packs"])
        self.packs = [p for p in model["packs"] if p in packs]
        self.active = {
            s for s in model["stage_order"]
            if stages[s]["pack"] in self.packs and s not in seed["not_applicable"]
        }
        self.fulfilled = {s for s in seed["fulfilled"] if s in self.active}

        rejected = set(seed["rejected"])
        self.rejected_roles = rejected & set(roles)
        self.rejected_tools = rejected & set(tools)
        self.rejected_stages = rejected & set(stages)

        # A Role is filled per scope: Tools compete for it only with Tools of
        # their own scope (a Pack without one is its own, general scope).
        self.tools_of_role: dict[str, list[str]] = {r: [] for r in roles}
        self.tools_of_slot: dict[tuple[str, str | None], list[str]] = {}
        for slug, tool in tools.items():
            if tool["pack"] in self.packs:
                for role in tool["roles"]:
                    self.tools_of_role[role].append(slug)
                    self.tools_of_slot.setdefault((role, tool["scope"]), []).append(slug)

        self.filled_by = {slot: self._filled_by(slot) for slot in self.tools_of_slot}
        self.out = self._out_tools()
        self._closed: dict[str, bool] = {}

    # -- roles and tools ----------------------------------------------------

    def first(self, tool: str) -> str:
        return self.model["tools"][tool]["stage_slugs"][0]

    def filled(self, role: str, scope: str | None) -> bool:
        """Is *role* filled for a Stage of *scope*; a Stage without a scope is
        content with the Role filled in any."""
        if scope is None:
            return any(self.filled_by[slot] for slot in self.tools_of_slot if slot[0] == role)
        return self.filled_by.get((role, scope)) is not None

    def _filled_by(self, slot: tuple[str, str | None]) -> str | None:
        """The Tool that fills the Role in a scope: the first, recommended ones
        before recognized ones, whose first Stage is fulfilled."""
        candidates = sorted(
            self.tools_of_slot[slot],
            key=lambda t: self.model["tools"][t]["status"] != "recommended",
        )
        for tool in candidates:
            if self.first(tool) in self.fulfilled:
                return tool
        return None

    def _out_tools(self) -> set[str]:
        """Tools another Tool has taken the place of: a Role of theirs is
        filled by that other Tool and their own first Stage is not fulfilled."""
        out = set()
        for slug, tool in self.model["tools"].items():
            if tool["pack"] not in self.packs or self.first(slug) in self.fulfilled:
                continue
            for role in tool["roles"]:
                filler = self.filled_by[(role, tool["scope"])]
                if filler is not None and filler != slug:
                    out.add(slug)
        return out

    def stage_out(self, stage: str) -> bool:
        return self.model["stages"][stage]["tool"] in self.out

    def never_fulfilled(self, stage: str) -> bool:
        """Nothing a run does will fulfil it: a Stage of a recognized Tool
        that is not there, or of a Tool another Tool took the place of."""
        if stage in self.fulfilled:
            return False
        tool_slug = self.model["stages"][stage]["tool"]
        return self.model["tools"][tool_slug]["status"] == "recognized" or tool_slug in self.out

    # -- rejection ------------------------------------------------------------

    def directly_rejected(self, stage: str) -> bool:
        s = self.model["stages"][stage]
        tool = self.model["tools"][s["tool"]]
        return (
            stage in self.rejected_stages
            or s["tool"] in self.rejected_tools
            or any(r in self.rejected_roles for r in tool["roles"])
        )

    def closed(self, stage: str) -> bool:
        """Rejected, or closed for good because something it requires is:
        a required Stage is closed, or an any-of group has a closed member and
        no member left that could be fulfilled, or a required Role cannot be
        filled any more."""
        if stage in self._closed:
            return self._closed[stage]
        self._closed[stage] = False  # a well-formed model has no cycle
        result = False
        if stage in self.active:
            if self.directly_rejected(stage):
                result = True
            else:
                scope = self.model["stages"][stage]["scope"]
                result = any(self._item_closed(item, scope) for item in self.model["stages"][stage]["requires"])
        self._closed[stage] = result
        return result

    def _item_closed(self, item, scope: str | None) -> bool:
        if isinstance(item, list):
            closed = [m for m in item if self._stage_dead(m)]
            return bool(closed) and all(self._stage_dead(m) or self.never_fulfilled(m) for m in item)
        if item in self.model["stages"]:
            return self._stage_dead(item)
        return self._role_closed(item, scope)

    def _stage_dead(self, stage: str) -> bool:
        """Closed, or in a Pack that does not apply."""
        return stage not in self.active or self.closed(stage)

    def _role_closed(self, role: str, scope: str | None) -> bool:
        if role in self.rejected_roles:
            return True
        if self.filled(role, scope):
            return False
        tools = [t for t in self.tools_of_role[role] if scope is None or self.model["tools"][t]["scope"] == scope]
        closed = [t for t in tools if self.closed(self.first(t))]
        return bool(closed) and all(
            t in closed or self.never_fulfilled(self.first(t)) for t in tools
        )

    def closed_because(self, stage: str) -> str:
        """What a closed Stage hangs on, as a phrase: a declined subject, or
        a Role no Tool can fill any more."""
        stages = self.model["stages"]

        def subject(slug: str) -> str | None:
            s = stages[slug]
            if slug in self.rejected_stages:
                return f"{slug} was declined"
            if s["tool"] in self.rejected_tools:
                return f"{s['tool']} was declined"
            for role in self.model["tools"][s["tool"]]["roles"]:
                if role in self.rejected_roles:
                    return f"{role} was declined"
            for item in s["requires"]:
                for member in item if isinstance(item, list) else [item]:
                    if member in stages:
                        if member in self.active and self.closed(member):
                            return subject(member)
                    elif self._role_closed(member, s["scope"]):
                        if member in self.rejected_roles:
                            return f"{member} was declined"
                        return f"no Tool can fill the Role {member} any more"
            return None

        return subject(stage) or f"{stage} was declined"

    def decided(self, stage: str) -> bool:
        """For `after`: fulfilled, closed, or never going to be."""
        return (
            stage in self.fulfilled
            or stage not in self.active
            or self.closed(stage)
            or self.never_fulfilled(stage)
        )

    # -- tickets --------------------------------------------------------------

    def ticketable(self, stage: str) -> bool:
        s = self.model["stages"][stage]
        return (
            stage in self.active
            and self.model["tools"][s["tool"]]["status"] == "recommended"
            and s["tool"] not in self.out
        )

    def backlog(self, track: str) -> list[str]:
        return [
            s for s in self.model["stage_order"]
            if self.model["stages"][s]["track"] == track
            and self.ticketable(s)
            and s not in self.fulfilled
            and not self.closed(s)
        ]

    # -- runtime --------------------------------------------------------------

    def runtime_blocked(self) -> list[dict]:
        blocked = []
        for slug, tool in self.model["tools"].items():
            if tool["pack"] not in self.packs:
                continue
            for runtime, minimum_text in tool.get("min_runtime", {}).items():
                current, minimum = _version(self.seed["runtime"].get(runtime)), _version(minimum_text)
                if current is not None and minimum is not None and _below(current, minimum):
                    node = self.first(slug)
                    blocked.append({
                        "node": node,
                        "reason": (
                            f"{runtime} runtime {_dotted(current)} is below {node}'s minimum "
                            f"{runtime} >= {_dotted(minimum)}"
                        ),
                    })
        return blocked

    def _subject_applies(self, subject: str) -> bool:
        if subject in self.model["stages"]:
            return subject in self.active
        if subject in self.model["tools"]:
            return self.model["tools"][subject]["pack"] in self.packs
        return bool(self.tools_of_role.get(subject))

    def reversals(self) -> list[dict]:
        found = []
        for subject in sorted(self.seed["rejected"]):
            if not self._subject_applies(subject):
                continue
            blocker = _blocker(self.seed["rejected"][subject])
            if blocker is None:
                continue
            runtime, needed = blocker
            current = _version(self.seed["runtime"].get(runtime))
            if current is not None and not _below(current, needed):
                found.append({
                    "node": subject,
                    "reason": (
                        f"{runtime} runtime now {_dotted(current)}, satisfies "
                        f"Blocked by {runtime} >= {_dotted(needed)}"
                    ),
                })
        return found

    # -- why a Stage waits ----------------------------------------------------

    def withheld_reason(self, stage: str, runtime_blocked: dict[str, str], safety_net_fulfilled: bool) -> str | None:
        s = self.model["stages"][stage]
        if not self.onboarded:
            return "onboarding-setup is not fulfilled"
        if stage in runtime_blocked:
            return runtime_blocked[stage]
        for item in s["requires"]:
            if isinstance(item, list):
                if not any(m in self.fulfilled for m in item):
                    return f"blocked — none of the alternatives fulfilled: {', '.join(item)}"
            elif item in self.model["stages"]:
                if item not in self.fulfilled:
                    return f"blocked by required parent {item}"
            elif not self.filled(item, s["scope"]):
                return f"blocked — no Tool fills the Role {item}"
        if s["track"] == "Guardrails" and not safety_net_fulfilled:
            return "waiting on the Safety Net"
        undecided = [a for a in s["after"] if not self.decided(a)]
        if undecided:
            return f"waiting on: {', '.join(undecided)}"
        return None


def _plain_search(name: str, uses: str | None) -> list[str]:
    search = [name]
    if uses and uses.casefold() != name.casefold():
        search.append(uses)
    return search


def compute(repo: pathlib.Path, model: dict | None = None, seed: dict | None = None) -> dict:
    """The graph outputs for *repo* from the handed-in *seed* (see
    ``load_seed``; without one, every Stage of every Pack is undecided)."""
    repo = pathlib.Path(repo)
    model = model or load_model()
    seed = seed or {"fulfilled": [], "rejected": {}, "packs": None, "not_applicable": [], "runtime": {}}
    state = _State(model, seed, _has_refactoring_operations(repo))
    stages, tools = model["stages"], model["tools"]

    backlogs = {track: state.backlog(track) for track in TRACKS}
    safety_net_fulfilled = not backlogs["Safety Net"]
    blocked = state.runtime_blocked()
    blocked_reason = {b["node"]: b["reason"] for b in blocked}

    tracks = {}
    for track in TRACKS:
        nodes = []
        for slug in model["stage_order"]:
            if stages[slug]["track"] != track or not state.ticketable(slug):
                continue
            stage, tool = stages[slug], tools[stages[slug]["tool"]]
            nodes.append({
                "node": slug,
                "name": stage["name"],
                "tool": tool["uses"],
                "search": _plain_search(stage["name"], tool["uses"]),
            })
        withheld = []
        for slug in model["stage_order"]:
            if stages[slug]["track"] != track or not state.ticketable(slug) or slug in state.fulfilled:
                continue
            if state.directly_rejected(slug):
                continue
            if state.closed(slug):
                withheld.append({"node": slug, "reason": f"closed — {state.closed_because(slug)}"})
                continue
            reason = state.withheld_reason(slug, blocked_reason, safety_net_fulfilled)
            if reason is not None:
                withheld.append({"node": slug, "reason": reason})
        waiting = {w["node"] for w in withheld}
        tracks[track] = {
            "fulfilled": not backlogs[track],
            "nodes": nodes,
            "backlog": backlogs[track],
            "workable": [s for s in backlogs[track] if s not in waiting],
            "withheld": withheld,
        }

    closed = [
        s for s in model["stage_order"]
        if s in state.active and s not in state.rejected_stages and state.closed(s)
    ]
    return {
        "prerequisites": {"git": True, "onboarding-setup": state.onboarded},
        "packs": state.packs,
        "roles": [
            {"role": slug, "name": role["name"], "scope": scope, "filled_by": state.filled_by.get((slug, scope))}
            for slug, role in model["roles"].items()
            for scope in (sorted({s for r, s in state.tools_of_slot if r == slug}, key=lambda s: (s is not None, s or "")) or [None])
        ],
        "tools": [
            {"tool": slug, "name": tool["name"], "roles": tool["roles"], "status": tool["status"],
             "pack": tool["pack"], "out": slug in state.out}
            for slug, tool in tools.items()
        ],
        "safety_net_fulfilled": safety_net_fulfilled,
        "tracks": tracks,
        "runtime_blocked": blocked,
        "reversals": state.reversals(),
        "closed_by_rejection": closed,
        "tree": {
            "stages": [
                {
                    "stage": slug,
                    "name": stages[slug]["name"],
                    "tool": stages[slug]["tool"],
                    "roles": tools[stages[slug]["tool"]]["roles"],
                    "pack": stages[slug]["pack"],
                    "track": stages[slug]["track"],
                    "requires": stages[slug]["requires"],
                    "after": stages[slug]["after"],
                }
                for slug in model["stage_order"]
            ]
        },
    }


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser(description="Compute the tooling model's graph outputs from a handed-in seed (dry-run, no mutation)")
    ap.add_argument("repo", nargs="?", default=".", help="path to the target repository (default: .)")
    ap.add_argument("--packs", type=str, default=None, help="directory holding the Packs, one subdirectory each with a pack.json (default: the suite's own)")
    ap.add_argument(
        "--seed", type=str, default=None,
        help='path to a JSON file holding what the caller judged: {"fulfilled": [stage, ...], "rejected": {role|tool|stage: null | {"php": "X.Y"}}, '
             '"packs": [pack, ...], "not_applicable": [stage, ...], "runtime": {"php": "X.Y"}} — without it, every Stage is undecided',
    )
    args = ap.parse_args()
    try:
        model = load_model(pathlib.Path(args.packs) if args.packs else None)
        seed = load_seed(pathlib.Path(args.seed), model) if args.seed else None
    except (PackError, SeedError) as exc:
        ap.exit(2, f"error: {exc}\n")
    print(json.dumps(compute(pathlib.Path(args.repo), model, seed), indent=2))
