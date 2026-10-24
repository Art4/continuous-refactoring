"""Generator and checker for the ADR index, read from the ADRs' banners.

A development tool of this repository; it is not shipped with the skills. An ADR's **banner** is
the run of quoted lines (``> …``) right under its title. A banner states how the ADR relates to
others, each relation a clause that opens with one of these words and names the ADRs up to the next
``:`` or end of sentence:

* towards an older ADR: *Supersedes*, *Supersedes in part* / *Partly supersedes*, *Amends*,
  *Extends*, *Revises*;
* towards a newer one: *Superseded by*, *Superseded in part by*, *Amended by*, *Extended by*.

A clause counts where it opens a paragraph, a sentence or a list (after ``, `` ``; `` or ``and``);
"ADR-0015 was later superseded by …" describes another ADR and is not a clause of this one.

A decision reversed with no ADR to record it opens a banner paragraph with *Superseded without an
ADR*, *Superseded in part without an ADR* or *Amended without an ADR*, and says what changed.

* ``--check`` (and ``validate_skills.py``) holds that every relation is named in **both** ADRs'
  banners, and that ``docs/adr/README.md`` is current.
* Without ``--check`` it writes ``docs/adr/README.md``: every ADR with the status its banner gives
  (superseded, superseded in part, amended, in force) and the ADRs that changed it.

    python3 scripts/adr_index.py            # write the index
    python3 scripts/adr_index.py --check    # write nothing, report every problem
"""

from __future__ import annotations

import argparse
import pathlib
import re
import sys
from dataclasses import dataclass, field

REPO = pathlib.Path(__file__).resolve().parent.parent
ADR_DIR = pathlib.Path("docs/adr")
INDEX = ADR_DIR / "README.md"
COMMAND = "python3 scripts/adr_index.py"

# Relation word -> (direction, strength). "older": this ADR changes the one it names;
# "newer": the ADR it names changes this one.
RELATIONS = {
    "supersedes in part": ("older", "superseded in part"),
    "partly supersedes": ("older", "superseded in part"),
    "supersedes": ("older", "superseded"),
    "amends": ("older", "amended"),
    "extends": ("older", "amended"),
    "revises": ("older", "amended"),
    "superseded in part by": ("newer", "superseded in part"),
    "superseded by": ("newer", "superseded"),
    "amended by": ("newer", "amended"),
    "extended by": ("newer", "amended"),
}
_WORDS = "|".join(sorted(RELATIONS, key=len, reverse=True))
_CLAUSE = re.compile(rf"(?:^|(?<=\. )|(?<=, )|(?<=; )|(?<=\band ))(?:also )?({_WORDS})\b", re.I)
_LINK = re.compile(r"\[(ADR-\d{4})\]\([^)]*\)")
_REF = re.compile(r"ADR-(\d{4})")
_CLAUSE_END = re.compile(r":(?:\s|$)|\.(?:\s|$)")
_UNRECORDED = re.compile(r"^(superseded in part|superseded|amended) without an ADR\b", re.I)

# Status by strength of the strongest "newer" relation, strongest first.
STATUSES = ("superseded", "superseded in part", "amended", "in force")

Problem = tuple[str, str]  # (path relative to the repo root, what is wrong)


@dataclass
class Adr:
    number: str
    file: str
    title: str
    older: dict[str, str] = field(default_factory=dict)  # number -> strength, ADRs this one changes
    newer: dict[str, str] = field(default_factory=dict)  # number -> strength, ADRs that change this one
    unrecorded: set[str] = field(default_factory=set)  # strengths of changes no ADR records

    @property
    def status(self) -> str:
        strengths = set(self.newer.values()) | self.unrecorded
        return next((s for s in STATUSES[:-1] if s in strengths), "in force")


def banner(text: str) -> list[str]:
    """The banner's paragraphs, with links reduced to ``ADR-NNNN`` and emphasis removed."""
    paragraphs, current = [], []
    for line in text.split("\n")[1:]:
        if line.startswith(">"):
            content = line[1:].strip()
            if content:
                current.append(content)
            elif current:
                paragraphs.append(" ".join(current))
                current = []
        elif not line.strip():
            if current:
                paragraphs.append(" ".join(current))
                current = []
        else:
            break
    if current:
        paragraphs.append(" ".join(current))
    return [_LINK.sub(r"\1", p).replace("**", "") for p in paragraphs]


def relations(text: str) -> list[tuple[str, str]]:
    """(relation word, ADR number) for every ADR a banner clause names."""
    found = []
    for paragraph in banner(text):
        clauses = list(_CLAUSE.finditer(paragraph))
        for i, clause in enumerate(clauses):
            end = clauses[i + 1].start() if i + 1 < len(clauses) else len(paragraph)
            span = paragraph[clause.end():end]
            stop = _CLAUSE_END.search(span)
            if stop:
                span = span[:stop.start()]
            found += [(clause.group(1).lower(), number) for number in _REF.findall(span)]
    return found


def unrecorded(text: str) -> set[str]:
    """Strengths of the changes a banner states with no ADR to record them."""
    return {m.group(1).lower() for p in banner(text) if (m := _UNRECORDED.match(p))}


def load(repo: pathlib.Path) -> dict[str, Adr]:
    adrs = {}
    for path in sorted((repo / ADR_DIR).glob("[0-9][0-9][0-9][0-9]-*.md")):
        text = path.read_text()
        title = text.split("\n", 1)[0].lstrip("# ").strip()
        adr = Adr(path.name[:4], path.name, title, unrecorded=unrecorded(text))
        for word, number in relations(text):
            direction, strength = RELATIONS[word]
            getattr(adr, direction)[number] = strength
        adrs[adr.number] = adr
    return adrs


def _rel(path: pathlib.Path | str) -> str:
    return (ADR_DIR / path).as_posix()


def relation_problems(adrs: dict[str, Adr]) -> list[Problem]:
    """Every relation is named in both banners, and names an ADR that exists."""
    problems = []
    for adr in adrs.values():
        for direction, other_side, word in (("older", "newer", "names {} as changed by it"),
                                            ("newer", "older", "names {} as changing it")):
            for number in sorted(getattr(adr, direction)):
                other = adrs.get(number)
                if other is None:
                    problems.append((_rel(adr.file), f"banner names ADR-{number}, which does not exist"))
                elif adr.number not in getattr(other, other_side) and adr.number not in getattr(other, direction):
                    problems.append((_rel(adr.file), f"banner {word.format('ADR-' + number)}, "
                                                     f"but the banner of ADR-{number} does not name ADR-{adr.number}"))
    return problems


def _links(adrs: dict[str, Adr], numbers) -> str:
    return ", ".join(f"[{n}]({adrs[n].file})" for n in sorted(numbers) if n in adrs)


def render(adrs: dict[str, Adr]) -> str:
    counts = {s: sum(1 for a in adrs.values() if a.status == s) for s in STATUSES}
    lines = [
        f"<!-- Generated from the ADRs' banners by scripts/adr_index.py — do not edit. Regenerate with: {COMMAND} -->",
        "",
        "# Architecture decision records",
        "",
        "Every decision with the status its banner gives. *Superseded*: nothing of it holds; *superseded in part*: "
        "some of it holds, the banner says what; *amended*: it holds with the changes the later ADRs make; "
        "*in force*: unchanged.",
        "",
        " · ".join(f"{s.capitalize()}: {counts[s]}" for s in STATUSES),
        "",
        "| ADR | Decision | Status | Changed by | Changes |",
        "| --- | --- | --- | --- | --- |",
    ]
    for adr in adrs.values():
        title = adr.title.replace("|", "\\|")
        changed_by = ", ".join(filter(None, [_links(adrs, adr.newer), "without an ADR" if adr.unrecorded else ""]))
        lines.append(f"| [{adr.number}]({adr.file}) | {title} | {adr.status} | "
                     f"{changed_by} | {_links(adrs, adr.older)} |")
    return "\n".join(lines) + "\n"


def check(repo: pathlib.Path) -> list[Problem]:
    repo = pathlib.Path(repo)
    if not (repo / ADR_DIR).is_dir():
        return []
    adrs = load(repo)
    problems = relation_problems(adrs)
    index = repo / INDEX
    if not index.exists() or index.read_text() != render(adrs):
        problems.append((INDEX.as_posix(), f"is out of date — run `{COMMAND}`"))
    return problems


def write(repo: pathlib.Path) -> bool:
    """Write the index; True when it changed."""
    text = render(load(repo))
    index = repo / INDEX
    if index.exists() and index.read_text() == text:
        return False
    index.write_text(text)
    return True


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Write, or with --check verify, the ADR index and the banners' relations.")
    ap.add_argument("--check", action="store_true", help="write nothing; list every problem and exit 1 if any")
    ap.add_argument("--root", default=str(REPO), help="repository root (default: this repository)")
    args = ap.parse_args(argv)
    root = pathlib.Path(args.root)
    if args.check:
        problems = check(root)
        for where, problem in problems:
            print(f"{where}: {problem}")
        return 1 if problems else 0
    print(f"{INDEX.as_posix()} written." if write(root) else "Everything is current.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
