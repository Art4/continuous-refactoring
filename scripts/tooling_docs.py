"""Generator and checker for the tooling model's data and its human-facing docs.

A development tool of this repository; it is not shipped with the skills. It reads the
Packs (``packs/*/pack.json``) and ``roles.json`` beside the parser and

* writes them back in one fixed form (two-space indent, objects one key per line, lists of
  plain values on one line, keys in the order of the schema), and
* writes the Markdown tables and Mermaid diagrams for humans under ``docs/tooling/``.

    python3 scripts/tooling_docs.py            # write both
    python3 scripts/tooling_docs.py --check    # write nothing, report every difference

``--check`` also holds what the standard-library parser leaves alone: the JSON Schemas
(``pip install jsonschema``), one recommended Tool per Role and Pack, and the existence of every
Tool's ``details`` file. ``validate_skills.py`` runs the same check.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
REFERENCES = pathlib.Path("skills/continuous-refactoring/references")
DOCS = pathlib.Path("docs/tooling")
COMMAND = "python3 scripts/tooling_docs.py"

sys.path.insert(0, str(REPO / REFERENCES))
import tooling_tree  # noqa: E402

# Keys in the order of the schemas; a key the schema does not know keeps its place after these.
ORDER = {
    "pack": ["$schema", "pack", "scope", "applies_when", "tools"],
    "tool": ["tool", "name", "uses", "roles", "status", "details", "min_runtime", "stages"],
    "stage": ["slug", "name", "track", "requires", "after", "applies_when"],
    "roles": ["$schema", "roles"],
    "role": ["slug", "name", "purpose", "signal"],
}
# The kind of object a key holds, so the right order applies one level down.
CHILD_KIND = {"tools": "tool", "stages": "stage", "roles": "role"}

Problem = tuple[str, str]  # (path relative to the repo root, what is wrong)


# ---------------------------------------------------------------------------
# The fixed JSON form
# ---------------------------------------------------------------------------


def _inline(value) -> bool:
    """A list of plain values (or of such lists) goes on one line."""
    if isinstance(value, list):
        return all(not isinstance(v, dict) and (not isinstance(v, list) or _inline(v)) for v in value)
    return not isinstance(value, dict)


def _dump(value, kind: str | None, depth: int) -> str:
    pad = "  " * (depth + 1)
    if isinstance(value, dict):
        keys = sorted(value, key=lambda k: (ORDER[kind].index(k) if kind in ORDER and k in ORDER[kind] else len(ORDER.get(kind, [])), 0))
        if not keys:
            return "{}"
        lines = [f"{pad}{json.dumps(k, ensure_ascii=False)}: {_dump(value[k], CHILD_KIND.get(k), depth + 1)}" for k in keys]
        return "{\n" + ",\n".join(lines) + "\n" + "  " * depth + "}"
    if isinstance(value, list) and not _inline(value):
        lines = [f"{pad}{_dump(v, kind, depth + 1)}" for v in value]
        return "[\n" + ",\n".join(lines) + "\n" + "  " * depth + "]"
    return json.dumps(value, ensure_ascii=False)


def canonical_json(data: dict, kind: str) -> str:
    """``data`` in the fixed form; ``kind`` is ``pack`` or ``roles``."""
    return _dump(data, kind, 0) + "\n"


# ---------------------------------------------------------------------------
# The docs
# ---------------------------------------------------------------------------

_HEADER = (
    "<!-- Generated from the Packs by scripts/tooling_docs.py — do not edit. "
    f"Regenerate with: {COMMAND} -->\n"
)


def _cell(text) -> str:
    return str(text).replace("|", "\\|").replace("\n", " ")


def _requirement(item, stages: dict, roles: dict) -> str:
    if isinstance(item, list):
        return "one of " + ", ".join(f"`{m}`" for m in item)
    return f"`{item}`" + (" (Role)" if item in roles and item not in stages else "")


def _node(prefix: str, slug: str) -> str:
    return prefix + "_" + slug.replace("-", "_")


def _label(text: str) -> str:
    return '"' + text.replace('"', "#quot;") + '"'


def _roles_page(model: dict) -> str:
    roles, tools, packs = model["roles"], model["tools"], model["packs"]
    out = [_HEADER, "# Tooling: Roles, Tools and Packs\n"]
    out.append(
        "What a tool is for (Roles), which tools can play them, and the Packs the tools come in. "
        "The words are defined in the suite's glossary; the rules are in "
        "[tooling-model.md](../../skills/continuous-refactoring/references/tooling-model.md).\n"
    )
    out.append("## Packs\n")
    out.append("| Pack | Applies when |\n| --- | --- |")
    for name, pack in packs.items():
        out.append(f"| [{name}](packs/{name}.md) | {_cell(pack['applies_when'])} |")
    out.append("\n## Roles\n")
    out.append("| Role | Purpose | Signal | Tools |\n| --- | --- | --- | --- |")
    for slug, role in roles.items():
        players = [f"{t['name']} ({t['status']}, {t['pack']})" for t in tools.values() if slug in t["roles"]]
        out.append(
            f"| {_cell(role['name'])} (`{slug}`) | {_cell(role['purpose'])} | {_cell(role['signal'] or '–')} | "
            f"{_cell('; '.join(players) or '–')} |"
        )
    return "\n".join(out) + "\n"


def _pack_page(model: dict, name: str) -> str:
    roles, tools, stages = model["roles"], model["tools"], model["stages"]
    pack = model["packs"][name]
    own = [stages[s] for s in model["stage_order"] if stages[s]["pack"] == name]
    out = [_HEADER, f"# Pack `{name}`\n", f"Applies when: {pack['applies_when']}\n"]

    out.append("## Diagram\n")
    out.append(_diagram(model, name, own))

    out.append("\n## Tools\n")
    out.append("| Tool | Status | Roles | Uses | Minimum runtime | Details |\n| --- | --- | --- | --- | --- | --- |")
    for slug in pack["tools"]:
        tool = tools[slug]
        role_names = ", ".join(roles[r]["name"] for r in tool["roles"])
        minimum = ", ".join(f"{k} {v}" for k, v in tool.get("min_runtime", {}).items()) or "–"
        details = f"packs/{tool['dir'].name}/{tool['details']}"
        link = f"[{details}](../../../{REFERENCES.as_posix()}/{details})"
        out.append(
            f"| {_cell(tool['name'])} (`{slug}`) | {tool['status']} | {_cell(role_names)} | "
            f"{_cell(tool['uses'] or '–')} | {_cell(minimum)} | {link} |"
        )

    out.append("\n## Stages\n")
    out.append("| Stage | Tool | Track | Requires | After | Applies when |\n| --- | --- | --- | --- | --- | --- |")
    for stage in own:
        requires = "; ".join(_requirement(i, stages, roles) for i in stage["requires"]) or "–"
        after = ", ".join(f"`{a}`" for a in stage["after"]) or "–"
        out.append(
            f"| {_cell(stage['name'])} (`{stage['slug']}`) | `{stage['tool']}` | {stage['track']} | "
            f"{_cell(requires)} | {after} | {_cell(stage.get('applies_when') or '–')} |"
        )

    return "\n".join(out) + "\n"


def _diagram(model: dict, name: str, own: list[dict]) -> str:
    roles, tools, stages, packs = model["roles"], model["tools"], model["stages"], model["packs"]
    lines = ["```mermaid", "flowchart TD"]
    declared: set[str] = set()
    edges: list[str] = []

    def stage_node(slug: str) -> str:
        stage = stages[slug]
        if stage["pack"] == name:
            return _node("s", slug)
        node = _node("x", slug)
        if node not in declared:
            declared.add(node)
            lines.append(f"  {node}[{_label(stage['name'] + ' (' + stage['pack'] + ')')}]")
        return node

    def players(slug: str) -> list[str]:
        return [t["stage_slugs"][0] for t in tools.values() if slug in t["roles"] and t["scope"] == packs[name]["scope"]]

    def role_node(slug: str) -> str:
        node = _node("r", slug)
        if node not in declared:
            declared.add(node)
            lines.append(f"  {node}([{_label(roles[slug]['name'])}])")
        if slug not in linked:
            linked.add(slug)
            edges.extend(f"  {stage_node(first)} --> {node}" for first in players(slug))
        return node

    own_slugs = {s["slug"]: s for s in own}
    wanted_roles = [i for s in own for i in s["requires"] if isinstance(i, str) and i not in stages]
    home: dict[str, str] = {}  # a Role sits in the Track of its first player in this Pack
    for slug in wanted_roles:
        first = next((p for p in players(slug) if p in own_slugs), None)
        if first:
            home.setdefault(slug, own_slugs[first]["track"])
    linked: set[str] = set()

    for track in tooling_tree.TRACKS:
        members = [s for s in own if s["track"] == track]
        if not members:
            continue
        lines.append(f"  subgraph {_node('t', track.lower().replace(' ', '_'))}[{_label(track)}]")
        for stage in members:
            lines.append(f"    {_node('s', stage['slug'])}[{_label(stage['name'])}]")
        for slug, home_track in home.items():
            if home_track == track:
                declared.add(_node("r", slug))
                lines.append(f"    {_node('r', slug)}([{_label(roles[slug]['name'])}])")
        lines.append("  end")

    for stage in own:
        target = _node("s", stage["slug"])
        for item in stage["requires"]:
            if isinstance(item, list):
                edges.extend(f"  {stage_node(m)} -->|one of| {target}" for m in item)
            elif item in stages:
                edges.append(f"  {stage_node(item)} --> {target}")
            else:
                edges.append(f"  {role_node(item)} --> {target}")
        for after in stage["after"]:
            edges.append(f"  {stage_node(after)} -.-> {target}")

    lines += edges
    lines.append("```")
    return "\n".join(lines)


def render_docs(model: dict) -> dict[str, str]:
    """Path (relative to the repo root) -> text of every generated doc."""
    docs = {(DOCS / "README.md").as_posix(): _roles_page(model)}
    for name in model["packs"]:
        docs[(DOCS / "packs" / f"{name}.md").as_posix()] = _pack_page(model, name)
    return docs


# ---------------------------------------------------------------------------
# Check and write
# ---------------------------------------------------------------------------


def _data_files(repo: pathlib.Path) -> list[tuple[pathlib.Path, str, str]]:
    """(path, kind, schema file name) of every JSON file the model is read from."""
    refs = repo / REFERENCES
    files = [(refs / "roles.json", "roles", "roles.schema.json")]
    files += [(p, "pack", "pack.schema.json") for p in tooling_tree._pack_paths(refs / "packs")] if (refs / "packs").is_dir() else []
    return files


def _rel(repo: pathlib.Path, path: pathlib.Path) -> str:
    return path.relative_to(repo).as_posix()


def schema_problems(repo: pathlib.Path) -> list[Problem]:
    try:
        import jsonschema
    except ImportError:
        return [("jsonschema", "is not installed — the schemas cannot be checked (pip install jsonschema)")]
    problems: list[Problem] = []
    for path, _kind, schema_name in _data_files(repo):
        try:
            data = json.loads(path.read_text())
            schema = json.loads((repo / REFERENCES / schema_name).read_text())
        except (OSError, ValueError) as error:
            problems.append((_rel(repo, path), f"cannot be read as JSON: {error}"))
            continue
        validator = jsonschema.Draft202012Validator(schema)
        for error in sorted(validator.iter_errors(data), key=lambda e: list(e.absolute_path)):
            where = "/".join(str(p) for p in error.absolute_path) or "(top)"
            problems.append((_rel(repo, path), f"breaks the schema at {where}: {error.message}"))
    return problems


def form_problems(repo: pathlib.Path) -> list[Problem]:
    problems: list[Problem] = []
    for path, kind, _schema in _data_files(repo):
        try:
            text = path.read_text()
            wanted = canonical_json(json.loads(text), kind)
        except (OSError, ValueError):
            continue  # schema_problems reports it
        if text != wanted:
            problems.append((_rel(repo, path), f"is not in the fixed form — run `{COMMAND}`"))
    return problems


def model_problems(repo: pathlib.Path, model: dict) -> list[Problem]:
    problems: list[Problem] = []
    for name, pack in model["packs"].items():
        seen: dict[str, str] = {}
        for slug in pack["tools"]:
            tool = model["tools"][slug]
            if tool["status"] != "recommended":
                continue
            for role in tool["roles"]:
                if role in seen:
                    problems.append((
                        f"pack {name}",
                        f"has two recommended tools for the role {role}: {seen[role]} and {slug}",
                    ))
                seen[role] = slug
    for slug, tool in model["tools"].items():
        if not (tool["dir"] / tool["details"]).is_file():
            problems.append((f"tool {slug}", f"names the details file {tool['details']}, which does not exist"))
    named = {(tool["dir"] / tool["details"]).resolve() for tool in model["tools"].values()}
    for path in sorted((repo / REFERENCES / "packs").glob("*/*.md")):
        if path.name != "README.md" and path.resolve() not in named:
            problems.append((path.relative_to(repo / REFERENCES).as_posix(), "is the details file of no Tool in its Pack"))
    return problems


def docs_problems(repo: pathlib.Path, model: dict) -> list[Problem]:
    problems: list[Problem] = []
    wanted = render_docs(model)
    for rel, text in wanted.items():
        path = repo / rel
        if not path.is_file():
            problems.append((rel, f"is missing — run `{COMMAND}`"))
        elif path.read_text() != text:
            problems.append((rel, f"is out of date — run `{COMMAND}`"))
    docs_dir = repo / DOCS
    if docs_dir.is_dir():
        for path in sorted(docs_dir.rglob("*.md")):
            if _rel(repo, path) not in wanted:
                problems.append((_rel(repo, path), f"belongs to no Pack — run `{COMMAND}`"))
    return problems


def check(repo: pathlib.Path) -> list[Problem]:
    """Every difference between the repository and what the Packs say it should be."""
    repo = pathlib.Path(repo)
    if not (repo / REFERENCES / "roles.json").is_file():
        return []
    problems = schema_problems(repo) + form_problems(repo)
    try:
        model = tooling_tree.load_model(repo / REFERENCES / "packs", repo / REFERENCES / "roles.json")
    except tooling_tree.PackError as error:
        return problems + [("tooling model", str(error))]
    return problems + model_problems(repo, model) + docs_problems(repo, model)


def write(repo: pathlib.Path) -> list[str]:
    """Write the fixed form and the docs; return the files that changed."""
    repo = pathlib.Path(repo)
    changed: list[str] = []

    def put(path: pathlib.Path, text: str) -> None:
        if not path.is_file() or path.read_text() != text:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)
            changed.append(_rel(repo, path))

    for path, kind, _schema in _data_files(repo):
        put(path, canonical_json(json.loads(path.read_text()), kind))
    model = tooling_tree.load_model(repo / REFERENCES / "packs", repo / REFERENCES / "roles.json")
    wanted = render_docs(model)
    for rel, text in wanted.items():
        put(repo / rel, text)
    for path in sorted((repo / DOCS).rglob("*.md")):
        if _rel(repo, path) not in wanted:
            path.unlink()
            changed.append(_rel(repo, path) + " (removed)")
    return changed


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Write, or with --check verify, the fixed JSON form and the tooling docs.")
    ap.add_argument("--check", action="store_true", help="write nothing; list every difference and exit 1 if any")
    ap.add_argument("--root", default=str(REPO), help="repository root (default: this repository)")
    args = ap.parse_args(argv)
    if args.check:
        problems = check(pathlib.Path(args.root))
        for where, problem in problems:
            print(f"{where}: {problem}")
        return 1 if problems else 0
    try:
        changed = write(pathlib.Path(args.root))
    except tooling_tree.PackError as error:
        print(f"cannot generate: {error}", file=sys.stderr)
        return 2
    print("\n".join(changed) if changed else "Everything is current.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
