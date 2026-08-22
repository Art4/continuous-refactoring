#!/usr/bin/env python3
"""Static suite validation for the continuous-refactoring skill suite.

Checks every ``skills/*/SKILL.md`` deterministically and without an LLM:

Tier 1 — structural:
- frontmatter: valid YAML, ``name`` matches the directory (kebab-case, <= 64
  chars), ``description`` present and <= 1024 chars, only known fields
- required sections: ``## Completion criterion`` everywhere, ``## Process`` on
  the lifecycle skills (the orchestrator uses ``## The pass``), and
  ``## Fallback`` on every skill whose reference-ledger row is shipped
  (ADR-0003)
- global ``/X`` references: the set found in each skill body must equal the set
  recorded for that skill in ``docs/agents/skill-references.md``
- local file references (``docs/...``, ``CONTEXT.md``, ``*.md``) resolve to real
  files; target-repo artifacts (``CODING_STANDARDS.md``, ``CONTRIBUTING.md``)
  and target-repo suite state (``docs/refactoring/**``, ADR-0005) are exempt
- ADR references (``ADR-NNNN``) resolve to ``docs/adr/NNNN-*.md``
- glossary vocabulary: every ``CONTEXT.md`` term is in use; avoid-synonyms are
  flagged unless explicitly allowlisted (the allowlist documents legitimate
  prose uses, e.g. defining the seam or quoting a user's words)

Tier 2 — semantic:
- ADR-0004 rule propagation: every rule keyword from ADR-0004 appears in at
  least one of ``refactor-design`` or ``refactor-implement``
- Cross-skill contract consistency: the orchestrator's description of each
  lifecycle step's output mentions that step's completion-criterion terms
- Glossary reverse check: domain vocabulary used in 2+ skills but absent from
  ``CONTEXT.md`` is flagged
- ADR staleness: ADRs containing ``retired``/``supersedes``/``amends`` are
  parsed into a dependency graph; skills referencing a superseded ADR without
  noting the successor are flagged

Usage:
    pip install pyyaml          # only non-stdlib dependency
    python3 scripts/validate_skills.py [REPO_ROOT]

Exit codes: 0 clean, 1 any issue found.

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
    "CODING_STANDARDS.md": "target-repo artifact (optional)",
    "CONTRIBUTING.md": "target-repo artifact (optional)",
}

# Target-repo suite state lives under docs/refactoring/ in the target repo
# (ADR-0005); the suite repo itself never contains these files.
EXEMPT_LOCAL_PREFIXES = {
    "docs/refactoring/": "target-repo suite state (ADR-0005)",
}

# Glossary avoid-terms whose use in prose is legitimate. Keyed by (skill, term)
# so a new occurrence anywhere else is still flagged.
VOCAB_ALLOW = {
    ("refactor-design", "boundary"): "defines the 'seam' term — 'public boundary' is the definition, not a synonym replacement",
    ("refactor-scan", "pain point"): "quotes a user-named direction; 'hot spot' is defined via change history, so it is not a synonym here",
}


@dataclass(frozen=True)
class Issue:
    skill: str
    message: str

    def __str__(self):
        return f"error: {self.skill}: {self.message}"


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
        return [Issue(dirname, "no valid YAML frontmatter block at the top of SKILL.md")]
    if not isinstance(fm, dict):
        return [Issue(dirname, "frontmatter is not a YAML mapping")]

    name = fm.get("name")
    if not name:
        issues.append(Issue(dirname, "frontmatter field 'name' is required"))
    elif not isinstance(name, str):
        issues.append(Issue(dirname, "frontmatter field 'name' must be a string"))
    else:
        if len(name) > MAX_NAME:
            issues.append(Issue(dirname, f"frontmatter 'name' is {len(name)} chars, max {MAX_NAME}"))
        if not NAME_RE.fullmatch(name):
            issues.append(Issue(dirname, f"frontmatter 'name' '{name}' is not kebab-case (lowercase letters, numbers, hyphens only)"))
        if name != dirname:
            issues.append(Issue(dirname, f"frontmatter 'name' '{name}' does not match the directory name '{dirname}'"))

    desc = fm.get("description")
    if not desc:
        issues.append(Issue(dirname, "frontmatter field 'description' is required and must be non-empty"))
    elif len(desc) > MAX_DESC:
        issues.append(Issue(dirname, f"frontmatter 'description' is {len(desc)} chars, max {MAX_DESC}"))

    unknown = sorted(set(fm) - ALLOWED_FRONTMATTER)
    for field in unknown:
        issues.append(Issue(dirname, f"frontmatter field '{field}' is not recognized (allowed: {', '.join(sorted(ALLOWED_FRONTMATTER))})"))
    return issues


# --------------------------------------------------------------------------
# Required sections
# --------------------------------------------------------------------------

def section_issues(text, skill, requires_fallback):
    issues = []
    headings = set(re.findall(r"^## (.+)$", text, re.M))

    if skill == ORCHESTRATOR:
        if "The pass" not in headings:
            issues.append(Issue(skill, "orchestrator skill must have a '## The pass' section"))
    elif "Process" not in headings:
        issues.append(Issue(skill, "missing required '## Process' section"))

    if "Completion criterion" not in headings:
        issues.append(Issue(skill, "missing required '## Completion criterion' section"))

    if requires_fallback and "Fallback" not in headings:
        issues.append(Issue(skill, "missing '## Fallback' section — required by ADR-0003 for a shipped global reference"))
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
    found = set(re.findall(r"(?<![a-zA-Z0-9])(?:`?)/([a-z][a-z0-9-]+)`?", text))
    external_refs = found - set(suite_names)
    ledger_refs = {ref for ref, _ in ledger.get(skill, [])}

    for ref in sorted(external_refs - ledger_refs):
        issues.append(Issue(skill, f"global '/{ref}' reference is not recorded in the reference ledger ({LEDGER_PATH})"))
    for ref in sorted(ledger_refs - external_refs):
        issues.append(Issue(skill, f"reference ledger records '/{ref}' but the skill no longer references it"))
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
        if not _PATH_LIKE.match(ref) or re.search(r"\s", ref):
            continue
        if ref in EXEMPT_LOCAL_REFS:
            continue
        if any(ref.startswith(p) for p in EXEMPT_LOCAL_PREFIXES):
            continue
        if not (repo_root / ref).exists():
            issues.append(Issue(skill or ref, f"local reference '{ref}' does not exist in the suite repo"))
    return issues


def adr_issues(text, repo_root, skill=""):
    issues = []
    repo_root = pathlib.Path(repo_root)
    for m in re.finditer(r"ADR-(\d{4})", text):
        num = m.group(1)
        if not list((repo_root / "docs/adr").glob(f"{num}-*.md")):
            issues.append(Issue(skill or f"ADR-{num}", f"ADR reference ADR-{num} has no matching docs/adr/{num}-*.md"))
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
        pattern = re.compile(r"\b" + re.escape(term) + r"s?\b", re.I)
        if not any(pattern.search(body) for body in skills.values()):
            issues.append(Issue("CONTEXT.md", f"glossary term '{term}' is defined but never used in the suite"))
    for skill, body in skills.items():
        for term in avoid:
            if (skill, term) in allow:
                continue
            if re.search(r"\b" + re.escape(term) + r"s?\b", body, re.I):
                issues.append(Issue(skill, f"glossary avoid-term '{term}' used — CONTEXT.md says to use the preferred term instead"))
    return issues


# --------------------------------------------------------------------------
# Tier 2 — ADR-0004 rule propagation
# --------------------------------------------------------------------------

ADR0004_KEYWORDS = [
    "behavior-preserving",
    "Strangler Fig",
    "Kent Beck",
    "deterministic tools",
    "own branch",
]


def adr0004_propagation_issues(skills_text):
    """Check that every ADR-0004 rule keyword appears in at least one of
    ``refactor-design`` or ``refactor-implement``."""
    issues = []
    targets = {"refactor-design", "refactor-implement"}
    combined = "\n".join(
        skills_text.get(s, "") for s in targets if s in skills_text
    )
    for kw in ADR0004_KEYWORDS:
        if not re.search(re.escape(kw), combined, re.I):
            issues.append(
                Issue(
                    "ADR-0004",
                    f"rule keyword '{kw}' from ADR-0004 not found in "
                    "refactor-design or refactor-implement",
                )
            )
    return issues


# --------------------------------------------------------------------------
# Tier 2 — Cross-skill contract consistency
# --------------------------------------------------------------------------

# Maps orchestrator step labels to the lifecycle skill that owns them.
# The orchestrator's text describes each step; the skill defines completion
# criteria.  A mismatch means the orchestrator promises something the skill
# doesn't deliver (or vice versa).
ORCH_STEP_SKILL_MAP = {
    "scan": "refactor-scan",
    "prioritise": "refactor-prioritize",
    "design": "refactor-design",
    "implement": "refactor-implement",
    "review": "refactor-review",
}

# Words too common to carry contract signal.
_ORCH_STOP = frozenset({
    "the", "a", "an", "of", "and", "or", "in", "on", "to", "for", "is",
    "that", "this", "it", "as", "by", "with", "from", "at", "if", "so",
    "its", "be", "do", "not", "but", "can", "will", "may", "shall",
    "must", "are", "was", "were", "been", "has", "have", "had", "each",
    "see", "run", "use", "via", "also", "into", "than", "then", "them",
    "they", "their", "there", "these", "those", "other", "more", "most",
    "some", "any", "all", "both", "very", "own", "same", "such",
    "just", "only", "even", "still", "already", "back", "here", "well",
    "now", "new", "old", "next", "first", "last", "long", "great",
    "little", "right", "high", "small", "large", "young", "few",
    "many", "much", "like", "about", "over", "after", "before",
    "between", "under", "until", "while", "where", "which", "whose",
    "don", "doesn", "didn", "won", "wouldn", "couldn", "shouldn",
    "block", "call", "flag", "come", "keep", "make", "take",
})


def _extract_keywords(text):
    """Extract significant lowercase words from text."""
    words = set(re.findall(r"[a-z]{4,}", text.lower()))
    return words - _ORCH_STOP


def _orchestrator_step_text(orch_text, step_label):
    """Return the text block for one numbered step in the orchestrator."""
    pattern = re.compile(
        r"\d+\.\s+\*\*" + re.escape(step_label) + r"\.\*\*\s*(.*?)(?=\n\s*\d+\.|\n## |\Z)",
        re.S | re.I,
    )
    m = pattern.search(orch_text)
    if not m:
        # Fallback: try without trailing period in bold
        pattern2 = re.compile(
            r"\d+\.\s+\*\*" + re.escape(step_label) + r"\*\*\.\s*(.*?)(?=\n\s*\d+\.|\n## |\Z)",
            re.S | re.I,
        )
        m = pattern2.search(orch_text)
    return m.group(1) if m else ""


def _completion_keywords(skill_text):
    """Extract keywords from a skill's ``## Completion criterion`` section."""
    m = re.search(r"## Completion criterion\n(.*?)(?=\n## |\Z)", skill_text, re.S)
    return _extract_keywords(m.group(1)) if m else set()


def contract_consistency_issues(orch_text, skills_text):
    """Flag mismatches between the orchestrator's step descriptions and each
    skill's completion criterion keywords.

    Checks that the orchestrator's step description uses at least some of the
    same domain terms as the skill's completion criterion.  Only flags when
    fewer than 20 % of the completion-criterion keywords appear in the
    orchestrator step — a significant conceptual gap.

    Note: the orchestrator step descriptions are intentionally brief; some
    false positives are expected.  These issues are advisory.
    """
    issues = []
    for step_label, skill_name in ORCH_STEP_SKILL_MAP.items():
        step_text = _orchestrator_step_text(orch_text, step_label)
        if not step_text:
            continue
        orch_kw = _extract_keywords(step_text)
        skill_kw = _completion_keywords(skills_text.get(skill_name, ""))
        if not skill_kw:
            continue
        overlap = orch_kw & skill_kw
        coverage = len(overlap) / len(skill_kw)
        if coverage < 0.2:
            missing_in_orch = skill_kw - orch_kw
            # Only flag when there are terms the orchestrator should mention
            # but doesn't — not when the orchestrator uses extra terms.
            significant = missing_in_orch - {
                "every", "candidate", "refactor", "skill", "issue",
            }
            if significant:
                issues.append(
                    Issue(
                        skill_name,
                        f"contract advisory: orchestrator '{step_label}' step "
                        f"does not mention completion-criterion terms "
                        f"({', '.join(sorted(significant)[:5])})",
                    )
                )
    return issues


# --------------------------------------------------------------------------
# Tier 2 — Glossary reverse check
# --------------------------------------------------------------------------


def glossary_reverse_issues(skills_text, context_text):
    """Flag domain vocabulary used in 2+ skills but absent from CONTEXT.md.

    Checks bold/emphasised terms (``**term**``) in skill files — these are
    the terms authors explicitly mark as domain jargon.  The check catches
    drift like ``slice``, ``design tree``, ``frontier``, ``smell`` that
    enters multiple skills without a glossary entry.
    """
    issues = []
    skill_bold = {}
    for name, body in skills_text.items():
        terms = set()
        for m in re.finditer(r"\*\*([A-Za-z][A-Za-z -]{2,})\*\*", body):
            terms.add(m.group(1).lower().strip())
        skill_bold[name] = terms

    term_usage = {}
    for name, terms in skill_bold.items():
        for t in terms:
            term_usage.setdefault(t, set()).add(name)

    glossary_terms = set()
    if context_text:
        for m in re.finditer(r"\*\*([A-Za-z][A-Za-z -]+)\*\*", context_text):
            glossary_terms.add(m.group(1).lower().strip())

    for term, users in sorted(term_usage.items()):
        if len(users) >= 2 and term not in glossary_terms:
            user_list = ", ".join(sorted(users))
            issues.append(
                Issue(
                    "CONTEXT.md",
                    f"domain term '{term}' used in {len(users)} skills "
                    f"({user_list}) but missing from glossary",
                )
            )
    return issues


# --------------------------------------------------------------------------
# Tier 2 — ADR staleness detection
# --------------------------------------------------------------------------


def parse_adr_graph(adr_dir):
    """Parse ADRs for ``retired``/``supersedes``/``amends`` metadata.

    Returns ``(graph, superseded_map)`` where:
    - *graph* is ``{adr_num: [referenced_adr_nums]}``
    - *superseded_map* is ``{superseded_num: successor_num}``
    """
    adr_dir = pathlib.Path(adr_dir)
    graph = {}
    superseded_map = {}
    for p in sorted(adr_dir.glob("*.md")):
        text = p.read_text()
        num_m = re.match(r"(\d{4})", p.name)
        if not num_m:
            continue
        num = num_m.group(1)
        refs = [m.group(1) for m in re.finditer(r"ADR-(\d{4})", text)]
        graph[num] = refs
        # Detect "This supersedes ADR-NNNN" or "supersedes ADR-NNNN"
        for m in re.finditer(r"supersedes\s+ADR-(\d{4})", text, re.I):
            superseded_map[m.group(1)] = num
        # Detect "This amends ADR-NNNN" — amends creates a dependency edge
        # but does not retire the amended ADR.
    return graph, superseded_map


def adr_staleness_issues(skills_text, adr_dir):
    """Flag skills that reference a superseded ADR without noting the
    successor."""
    issues = []
    _, superseded_map = parse_adr_graph(adr_dir)
    if not superseded_map:
        return issues

    for skill_name, body in skills_text.items():
        for old_num, successor_num in sorted(superseded_map.items()):
            old_ref = f"ADR-{old_num}"
            succ_ref = f"ADR-{successor_num}"
            if re.search(r"ADR-" + old_num, body) and succ_ref not in body:
                issues.append(
                    Issue(
                        skill_name,
                        f"references {old_ref} which is superseded by "
                        f"{succ_ref} — skill should note the successor",
                    )
                )
    return issues


# --------------------------------------------------------------------------
# Whole-repo orchestration
# --------------------------------------------------------------------------

def validate_repo(repo_root):
    repo_root = pathlib.Path(repo_root)
    issues = []
    skills_dir = repo_root / "skills"
    suite_names = sorted(d.name for d in skills_dir.iterdir() if d.is_dir())

    ledger_text = (repo_root / LEDGER_PATH).read_text() if (repo_root / LEDGER_PATH).exists() else None
    if ledger_text is None:
        issues.append(Issue(LEDGER_PATH, f"missing reference ledger — required at {LEDGER_PATH}"))
        ledger = {}
    else:
        ledger = parse_ledger(ledger_text)

    context_text = (repo_root / CONTEXT_PATH).read_text() if (repo_root / CONTEXT_PATH).exists() else None
    if context_text is None:
        issues.append(Issue(CONTEXT_PATH, f"missing glossary — required at {CONTEXT_PATH}"))
        glossary = Glossary(terms=[], avoid=[])
    else:
        glossary = parse_glossary(context_text)

    skills_text = {}

    for d in sorted(skills_dir.iterdir()):
        if not d.is_dir():
            continue
        md = d / "SKILL.md"
        if not md.exists():
            issues.append(Issue(d.name, "missing SKILL.md"))
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

    # --- Tier 2: semantic checks ---
    adr_dir = repo_root / "docs" / "adr"
    issues += adr0004_propagation_issues(skills_text)

    orchestrator_text = skills_text.get(ORCHESTRATOR, "")
    if orchestrator_text:
        issues += contract_consistency_issues(orchestrator_text, skills_text)

    if context_text:
        issues += glossary_reverse_issues(skills_text, context_text)

    if adr_dir.is_dir():
        issues += adr_staleness_issues(skills_text, adr_dir)

    return sorted(issues, key=lambda i: (i.skill, i.message))


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Static validation of the skill suite (Tier 1 + Tier 2)",
        epilog=(
            "Tier 2 checks: ADR-0004 rule propagation, cross-skill contract "
            "consistency, glossary reverse check, ADR staleness detection"
        ),
    )
    ap.add_argument("root", nargs="?", default=".", help="suite repo root (default: current directory)")
    args = ap.parse_args(argv)

    issues = validate_repo(args.root)
    if issues:
        print("Suite skill validation report:")
        for i in issues:
            print(f"  {i}")
    else:
        print("All suite skills validated clean.")
    return 1 if issues else 0


if __name__ == "__main__":
    sys.exit(main())