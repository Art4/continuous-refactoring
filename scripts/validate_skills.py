#!/usr/bin/env python3
"""Tier 1 static suite validation for the continuous-refactoring skill suite.

Checks every ``skills/*/SKILL.md`` deterministically and without an LLM:

- frontmatter: valid YAML, ``name`` matches the directory (kebab-case, <= 64
  chars), ``description`` present and <= 1024 chars, only known fields
- required sections: ``## Completion criterion`` everywhere, ``## Process`` on
  the lifecycle skills (the orchestrator uses ``## The pass``), and
  ``## Fallback`` on every skill whose reference-ledger row is shipped
  (ADR-0003)
- global ``/X`` references: the set found in each skill body must equal the set
  recorded for that skill in ``docs/agents/skill-references.md``
- local file references (``docs/...``, ``CONTEXT.md``, ``*.md``) resolve to real
  files; target-repo artifacts (``docs/agents/refactoring.md``,
  ``CODING_STANDARDS.md``, ``CONTRIBUTING.md``) are exempt
- ADR references (``ADR-NNNN``) resolve to ``docs/adr/NNNN-*.md``
- glossary vocabulary: every ``CONTEXT.md`` term is in use; avoid-synonyms are
  flagged unless explicitly allowlisted (the allowlist documents legitimate
  prose uses, e.g. defining the seam)

Usage:
    pip install pyyaml          # only non-stdlib dependency
    python3 scripts/validate_skills.py [--strict] [REPO_ROOT]

Exit codes: 0 clean, 1 errors (or warnings with --strict), 2 warnings only.

Run the tests with: python3 -m unittest discover -s scripts -p 'test_*.py'
"""

import argparse
import pathlib
import re
import sys
from dataclasses import dataclass

import yaml

ORCHESTRATOR = "continuous-refactoring"

ALLOWED_FRONTMATTER = {"name", "description", "disable-model-invocation", "allowed-tools"}
MAX_NAME = 64
MAX_DESC = 1024
NAME_RE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")

LEDGER_PATH = "docs/agents/skill-references.md"
CONTEXT_PATH = "CONTEXT.md"

EXEMPT_LOCAL_REFS = {
    "docs/agents/refactoring.md": "scaffolded into the target repo by the orchestrator",
    "CODING_STANDARDS.md": "target-repo artifact (optional)",
    "CONTRIBUTING.md": "target-repo artifact (optional)",
}

# Glossary avoid-terms whose use in prose is legitimate. Keyed by (skill, term)
# so a new occurrence anywhere else is still flagged.
VOCAB_ALLOW = {
    ("refactor-design", "boundary"): "defines the 'seam' term — 'public boundary' is the definition, not a synonym replacement",
}


@dataclass(frozen=True)
class Issue:
    level: str  # "error" | "warning"
    skill: str
    message: str

    def __str__(self):
        return f"{self.level}: {self.skill}: {self.message}"


# --------------------------------------------------------------------------
# Frontmatter
# --------------------------------------------------------------------------

def parse_frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---(?:\n|$)", text, re.S)
    if not m:
        return None
    try:
        return yaml.safe_load(m.group(1))
    except yaml.YAMLError:
        return None


def frontmatter_issues(text, dirname):
    issues = []
    fm = parse_frontmatter(text)
    if fm is None:
        return [Issue("error", dirname, "no valid YAML frontmatter block at the top of SKILL.md")]
    if not isinstance(fm, dict):
        return [Issue("error", dirname, "frontmatter is not a YAML mapping")]

    name = fm.get("name")
    if not name:
        issues.append(Issue("error", dirname, "frontmatter field 'name' is required"))
    elif not isinstance(name, str):
        issues.append(Issue("error", dirname, "frontmatter field 'name' must be a string"))
    else:
        if len(name) > MAX_NAME:
            issues.append(Issue("error", dirname, f"frontmatter 'name' is {len(name)} chars, max {MAX_NAME}"))
        if not NAME_RE.fullmatch(name):
            issues.append(Issue("error", dirname, f"frontmatter 'name' '{name}' is not kebab-case (lowercase letters, numbers, hyphens only)"))
        if name != dirname:
            issues.append(Issue("error", dirname, f"frontmatter 'name' '{name}' does not match the directory name '{dirname}'"))

    desc = fm.get("description")
    if not desc:
        issues.append(Issue("error", dirname, "frontmatter field 'description' is required and must be non-empty"))
    elif len(desc) > MAX_DESC:
        issues.append(Issue("error", dirname, f"frontmatter 'description' is {len(desc)} chars, max {MAX_DESC}"))

    unknown = sorted(set(fm) - ALLOWED_FRONTMATTER)
    for field in unknown:
        issues.append(Issue("error", dirname, f"frontmatter field '{field}' is not recognized (allowed: {', '.join(sorted(ALLOWED_FRONTMATTER))})"))
    return issues


# --------------------------------------------------------------------------
# Required sections
# --------------------------------------------------------------------------

def section_issues(text, skill, requires_fallback):
    issues = []
    headings = set(re.findall(r"^## (.+)$", text, re.M))

    if skill == ORCHESTRATOR:
        if "The pass" not in headings:
            issues.append(Issue("error", skill, "orchestrator skill must have a '## The pass' section"))
    elif "Process" not in headings:
        issues.append(Issue("error", skill, "missing required '## Process' section"))

    if "Completion criterion" not in headings:
        issues.append(Issue("error", skill, "missing required '## Completion criterion' section"))

    if requires_fallback and "Fallback" not in headings:
        issues.append(Issue("error", skill, "missing '## Fallback' section — required by ADR-0003 for a shipped global reference"))
    return issues


# --------------------------------------------------------------------------
# Global /X references vs the reference ledger
# --------------------------------------------------------------------------

def parse_ledger(text):
    """Return {skill_name: [(global_ref_without_slash, shipped: bool)]}."""
    rows = {}
    for line in text.splitlines():
        s = line.strip()
        if not (s.startswith("|") and s.endswith("|")):
            continue
        cols = [c.strip() for c in s.strip("|").split("|")]
        if len(cols) < 5:
            continue
        skill = cols[0].strip("`").strip()
        m = re.search(r"`([^`]+)`", cols[1])
        if not skill or not m:
            continue
        ref = m.group(1)
        if not ref.startswith("/"):
            continue
        status = cols[4].lower()
        shipped = "\u2713" in status or "shipped" in status
        rows.setdefault(skill, []).append((ref[1:], shipped))
    return rows


def global_ref_issues(text, skill, suite_names, ledger):
    issues = []
    found = set(re.findall(r"`/([a-z0-9-]+)`", text))
    global_found = found - set(suite_names)
    ledger_refs = {ref for ref, _ in ledger.get(skill, [])}

    for ref in sorted(global_found - ledger_refs):
        issues.append(Issue("error", skill, f"global '/{ref}' reference is not recorded in the reference ledger ({LEDGER_PATH})"))
    for ref in sorted(ledger_refs - global_found):
        issues.append(Issue("error", skill, f"reference ledger records '/{ref}' but the skill no longer references it"))
    return issues


# --------------------------------------------------------------------------
# Local file references and ADR references
# --------------------------------------------------------------------------

_PATH_LIKE = re.compile(r"(?:^docs/|^CONTEXT(?:-MAP)?\.md$|\.md$|^skills/)")


def local_ref_issues(text, repo_root, skill=""):
    issues = []
    repo_root = pathlib.Path(repo_root)
    for m in re.finditer(r"`([^`]+)`", text):
        ref = m.group(1)
        if not _PATH_LIKE.match(ref):
            continue
        if ref in EXEMPT_LOCAL_REFS:
            continue
        if not (repo_root / ref).exists():
            issues.append(Issue("error", skill or ref, f"local reference '{ref}' does not exist in the suite repo"))
    return issues


def adr_issues(text, repo_root, skill=""):
    issues = []
    repo_root = pathlib.Path(repo_root)
    for m in re.finditer(r"ADR-(\d{4})", text):
        num = m.group(1)
        if not list((repo_root / "docs/adr").glob(f"{num}-*.md")):
            issues.append(Issue("error", skill or f"ADR-{num}", f"ADR reference ADR-{num} has no matching docs/adr/{num}-*.md"))
    return issues


# --------------------------------------------------------------------------
# Glossary vocabulary
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class Glossary:
    terms: list
    avoid: list


def parse_glossary(text):
    terms = re.findall(r"\*\*([A-Za-z][A-Za-z ]+)\*\*:", text)
    avoid = []
    for m in re.finditer(r"_Avoid_:?\s*(.+)", text):
        for part in m.group(1).split(","):
            term = part.strip()
            if term and "use the term as-is" not in term:
                avoid.append(term)
    return Glossary(terms=terms, avoid=avoid)


def vocab_issues(terms, avoid, skills, allow):
    """skills: {skill_name: SKILL.md body}; allow: set of (skill, term) pairs."""
    issues = []
    for term in terms:
        pattern = re.compile(r"\b" + re.escape(term) + r"\w*\b", re.I)
        if not any(pattern.search(body) for body in skills.values()):
            issues.append(Issue("error", "CONTEXT.md", f"glossary term '{term}' is defined but never used in the suite"))
    for skill, body in skills.items():
        for term in avoid:
            if (skill, term) in allow:
                continue
            if re.search(r"\b" + re.escape(term) + r"\b", body, re.I):
                issues.append(Issue("error", skill, f"glossary avoid-term '{term}' used — CONTEXT.md says to use the preferred term instead"))
    return issues


# --------------------------------------------------------------------------
# Whole-repo orchestration
# --------------------------------------------------------------------------

def validate_repo(repo_root):
    repo_root = pathlib.Path(repo_root)
    issues = []
    skills_dir = repo_root / "skills"
    suite_names = sorted(d.name for d in skills_dir.iterdir() if d.is_dir())

    ledger = parse_ledger((repo_root / LEDGER_PATH).read_text())
    glossary = parse_glossary((repo_root / CONTEXT_PATH).read_text())
    skills_text = {}

    for d in sorted(skills_dir.iterdir()):
        if not d.is_dir():
            continue
        md = d / "SKILL.md"
        if not md.exists():
            issues.append(Issue("error", d.name, "missing SKILL.md"))
            continue
        text = md.read_text()
        skills_text[d.name] = text
        shipped = any(shipped for _, shipped in ledger.get(d.name, []))
        issues += frontmatter_issues(text, d.name)
        issues += section_issues(text, d.name, requires_fallback=shipped)
        issues += global_ref_issues(text, d.name, set(suite_names), ledger)
        issues += local_ref_issues(text, repo_root, skill=d.name)
        issues += adr_issues(text, repo_root, skill=d.name)

    issues += vocab_issues(glossary.terms, glossary.avoid, skills_text, set(VOCAB_ALLOW))
    return sorted(issues, key=lambda i: (i.skill, i.message))


def main(argv=None):
    ap = argparse.ArgumentParser(description="Tier 1 static validation of the skill suite")
    ap.add_argument("--strict", action="store_true", help="treat warnings as errors (exit 1)")
    ap.add_argument("root", nargs="?", default=".", help="suite repo root (default: current directory)")
    args = ap.parse_args(argv)

    issues = validate_repo(args.root)
    if issues:
        print("Suite skill validation report:")
        for i in issues:
            print(f"  {i}")
    else:
        print("All suite skills validated clean.")

    errors = [i for i in issues if i.level == "error"]
    warnings = [i for i in issues if i.level == "warning"]
    if errors or (args.strict and warnings):
        return 1
    if warnings:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())