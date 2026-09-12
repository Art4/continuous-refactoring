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

_VALID_EDGE_TYPES = ("required", "recommended", "resolved", "required-any")

# Ordinary required-gated nodes that must never be surfaced as a proposable
# candidate, regardless of their own fulfilled state: `git` (never an MR),
# `static-code-analyzer` (pure plumbing), `psalm` (recognition-only — same
# fait-accompli shape Pest already gets for `phpunit`), `is-php-project`
# (recognition-only gate for the whole PHP specialization — rejecting a
# required parent never unblocks its children, so a human filing an
# out-of-scope entry for it would never accomplish anything leaving it
# unfulfilled doesn't already). Resolved-gated aggregation nodes
# (`php-structural-scan`) are excluded separately via
# `exposed_resolved_gate_nodes` in load_tree() — this set is for ordinary
# required-gated nodes instead.
_NEVER_PROPOSED = {"git", "static-code-analyzer", "psalm", "is-php-project"}

# The PHPStan level chain (1..10) — used by roadmap()'s per-level
# empty-baseline gate and its open-chain filler.
_PHPSTAN_LEVEL_NODES = [f"phpstan-level-{i}" for i in range(1, 11)]


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
    # down, by php-structural-scan (the PHP tree's own aggregation node
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
    # php-structural-scan, feeding structural-scan) is never itself
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


def _has_composer_json(repo: pathlib.Path) -> bool:
    return (repo / "composer.json").exists() or (repo / "composer" / "composer.json").exists()


def _has_php_files(repo: pathlib.Path) -> bool:
    """True if the target repo contains at least one *.php file anywhere in
    the tree, `vendor/` excluded (Composer's own dependency directory, never
    project code) — used alongside `_has_composer_json` by `is-php-project`'s
    fulfilment check (a PHP project without Composer yet should still open
    the tree)."""
    for f in repo.rglob("*.php"):
        if "vendor" not in f.relative_to(repo).parts:
            return True
    return False


def _psr4_root_namespace(composer: dict | None) -> str | None:
    """The declared PSR-4 root namespace for the app's own source, if any —
    the first entry in `autoload.psr-4` (composer.json), trailing backslash
    stripped. `None` when no `autoload.psr-4` section exists at all, or it's
    empty. `phpunit.md`'s `tests/Unit/` namespace derivation reads this once
    `psr-4` is fulfilled, instead of independently re-deriving from
    `composer.json`'s `name` field."""
    if not composer:
        return None
    psr4 = (composer.get("autoload") or {}).get("psr-4") or {}
    for prefix in psr4:
        return prefix.rstrip("\\")
    return None


def _has_verified_psr4_autoload(repo: pathlib.Path, composer: dict | None) -> bool:
    """True only once `autoload.psr-4` is both declared AND actually used —
    at least one real `.php` file under one of its mapped directories
    carries a `namespace` declaration matching the mapped prefix.
    Declaration alone (an autoload section nothing yet uses) is deliberately
    not enough — a claim, not evidence the mechanism works
    (`php-tooling-tree/psr-4.md`)."""
    if not composer:
        return False
    psr4 = (composer.get("autoload") or {}).get("psr-4") or {}
    for prefix, dirs in psr4.items():
        prefix_stripped = prefix.rstrip("\\")
        if not prefix_stripped:
            continue
        for d in ([dirs] if isinstance(dirs, str) else dirs):
            base = repo / d
            if not base.is_dir():
                continue
            for f in base.rglob("*.php"):
                try:
                    txt = f.read_text(encoding="utf-8")
                except OSError:
                    continue
                if re.search(rf"^\s*namespace\s+{re.escape(prefix_stripped)}\b", txt, re.MULTILINE):
                    return True
    return False


def _psr4_mapped_dirs(composer: dict | None) -> list[str]:
    """Every directory declared in autoload.psr-4 (composer.json) — excluded
    from entry-point detection below (php-tooling-tree/psr-4.md's own
    Composition root/Entry point wiring step): a file already reachable via
    the PSR-4 mapping is never itself an unwired entry-point candidate."""
    if not composer:
        return []
    psr4 = (composer.get("autoload") or {}).get("psr-4") or {}
    dirs: list[str] = []
    for _, d in psr4.items():
        dirs.extend([d] if isinstance(d, str) else d)
    return dirs


# require/include of a sibling file via the __DIR__-relative shape this
# suite's own fixtures and every real target observed so far actually use
# (`require_once __DIR__ . "/Foo.php"`, with or without `_once`, with or
# without `../` segments) — a conservative, single-shape approximation,
# not a full parser, matching every other filesystem-text check in this
# module.
_DIR_RELATIVE_REQUIRE_RE = re.compile(
    r"\b(?:require|include)(?:_once)?\s*\(?\s*__DIR__\s*\.\s*['\"]([^'\"]+\.php)['\"]"
)
_AUTOLOAD_REQUIRE_RE = re.compile(r"\b(?:require|include)(?:_once)?\b[^;]*vendor[/\\]autoload\.php")

# Known tooling-config scripts at the repo root that happen to carry a
# `.php` extension but are never a request-time entry point — each is only
# ever loaded by its own tool's CLI (Rector, php-cs-fixer), never by a
# webserver or the app's own runtime. Reuses the exact filenames this
# module's own rector-php-set/php-cs-fixer detection above already checks
# for, rather than a second, independent list.
_TOOLING_CONFIG_PHP_FILENAMES = {"rector.php", ".php-cs-fixer.php", ".php-cs-fixer.dist.php"}


def _require_targets(php_file: pathlib.Path) -> list[pathlib.Path]:
    """Every file `php_file` reaches via the __DIR__-relative require/include
    shape above, resolved to an absolute path. Best-effort: a target using a
    different loading style (autoloading already, `dirname(__FILE__)`, a
    plain relative path with no `__DIR__` prefix, …) simply isn't reflected
    here — the same conservative-approximation trade-off this tree's other
    filesystem-text checks already make."""
    try:
        text = php_file.read_text(encoding="utf-8")
    except OSError:
        return []
    targets = []
    for m in _DIR_RELATIVE_REQUIRE_RE.finditer(text):
        # The captured string conventionally starts with "/" (PHP's own
        # __DIR__ . "/Foo.php" concatenation) -- pathlib's own `/` operator
        # treats a leading-slash right-hand side as absolute and discards
        # the left side entirely, so it must be stripped before joining.
        candidate = (php_file.parent / m.group(1).lstrip("/")).resolve()
        targets.append(candidate)
    return targets


def _entry_point_candidates(repo: pathlib.Path, psr4_dirs: list[str]) -> list[pathlib.Path]:
    """Every `.php` file outside `vendor/`, any test directory, and the
    PSR-4-mapped namespace directory (already-autoloaded source is never an
    unwired entry-point candidate) — the search scope `_detect_entry_points`
    walks its require graph over."""
    excluded_roots = {(repo / d).resolve() for d in psr4_dirs}
    files = []
    for f in repo.rglob("*.php"):
        try:
            rel_parts = f.relative_to(repo).parts
        except ValueError:
            continue
        if any(part in ("vendor", ".git") or part.lower() == "tests" for part in rel_parts):
            continue
        if len(rel_parts) == 1 and rel_parts[0] in _TOOLING_CONFIG_PHP_FILENAMES:
            continue
        resolved = f.resolve()
        if any(root in resolved.parents or root == resolved for root in excluded_roots):
            continue
        files.append(f)
    return sorted(files)


def _detect_entry_points(repo: pathlib.Path, psr4_dirs: list[str]):
    """php-tooling-tree/psr-4.md's own detection: **Entry point** (a file
    nothing in the target's own source tree requires) and **Composition
    root** (the file more than half of the entry points directly require,
    if any — recognized even when some entry points don't converge on it;
    see CONTEXT.md for both terms). Returns
    `(entry_points, composition_root, individually_wired_targets)` — the
    last is the composition root (as a one-element list) plus every entry
    point that doesn't require it, i.e. everything the autoloader-wiring
    check below must find `vendor/autoload.php` in, one way or another."""
    candidates = _entry_point_candidates(repo, psr4_dirs)
    required_by_something = set()
    direct_targets: dict[pathlib.Path, list[pathlib.Path]] = {}
    for f in candidates:
        targets = _require_targets(f)
        direct_targets[f] = targets
        required_by_something.update(targets)
    entry_points = [f for f in candidates if f.resolve() not in required_by_something]

    target_counts: dict[pathlib.Path, int] = {}
    for ep in entry_points:
        for t in direct_targets[ep]:
            # A require resolving into vendor/ (most notably
            # vendor/autoload.php itself) is direct wiring evidence, never a
            # composition-root candidate -- it isn't part of the target's
            # own source tree.
            if "vendor" in t.parts:
                continue
            target_counts[t] = target_counts.get(t, 0) + 1
    composition_root = None
    if entry_points and target_counts:
        best_target, best_count = max(target_counts.items(), key=lambda kv: (kv[1], str(kv[0])))
        if best_count * 2 > len(entry_points):
            composition_root = best_target

    if composition_root is not None:
        stragglers = [ep for ep in entry_points if composition_root not in direct_targets[ep]]
        wiring_targets = [composition_root] + stragglers
    else:
        wiring_targets = list(entry_points)
    return entry_points, composition_root, wiring_targets


def _autoloader_wired(repo: pathlib.Path, composer: dict | None) -> tuple[bool, list[str]]:
    """php-tooling-tree/psr-4.md's autoloader-wiring criterion: the
    Composition root (or every Entry point that doesn't converge on one, or
    every entry point at all when there's no composition root) contains a
    require/include resolving to `vendor/autoload.php`. No entry points at
    all (e.g. a pure library) is vacuously satisfied — nothing to wire, the
    same "nothing to recommend" convention this tree already uses elsewhere
    (php-minimal-version's own undeterminable-floor case, php_floor_precheck's
    unknown-floor case).

    Returns `(wired, unwired)` — `unwired` names every candidate (repo-
    relative path strings) that still needs its own `vendor/autoload.php`
    require, deliberately exposed rather than collapsed into the boolean:
    this check is a blunt, tool-agnostic "does the text contain the
    require" match — it has no way to tell a genuine, still-unwired
    application entry point apart from, say, a generated CI/tooling helper
    script that structurally never needs the app's own classes at all
    (a real false positive, caught live on Art4/legacy-todo). Sorting that
    out is a judgement call for whoever is actually interpreting this
    result — see php-tooling-tree/psr-4.md's own Fulfilment check for how
    to read a non-empty `unwired` list rather than trusting `wired` at face
    value."""
    psr4_dirs = _psr4_mapped_dirs(composer)
    _, _, wiring_targets = _detect_entry_points(repo, psr4_dirs)
    repo_resolved = repo.resolve()
    unwired: list[str] = []
    for target in wiring_targets:
        # wiring_targets mixes absolute paths (the composition root, itself
        # resolved elsewhere) and repo-relative ones (individually-wired
        # entry points) -- normalize both the same way before reporting.
        resolved = (target if target.is_absolute() else (repo / target)).resolve()
        try:
            rel = str(resolved.relative_to(repo_resolved))
        except ValueError:
            rel = str(resolved)
        try:
            text = resolved.read_text(encoding="utf-8")
        except OSError:
            unwired.append(rel)
            continue
        if not _AUTOLOAD_REQUIRE_RE.search(text):
            unwired.append(rel)
    return (not unwired, unwired)
    return False


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


def _has_ci_job_invoking(repo: pathlib.Path, needle: str) -> bool:
    """True if any CI workflow file (GitHub Actions or GitLab CI) contains
    `needle` as a literal substring. The conservative approximation shared by
    every self-wired CI-gate check in this module (`composer-audit`,
    `phpunit`/`phpstan-level-0`): presence of the
    invocation, not proof the job actually fails the pipeline on a red
    result."""
    for pat in [".github/workflows/*.yml", ".github/workflows/*.yaml", ".gitlab-ci.yml"]:
        for f in glob.glob(str(repo / pat)):
            try:
                if needle in pathlib.Path(f).read_text(encoding="utf-8"):
                    return True
            except OSError:
                continue
    return False


def _has_ephemeral_ci_dep(repo: pathlib.Path, package_name: str, invocation_needle: str) -> bool:
    """True if a CI workflow file both installs `package_name` at runtime
    (a `composer require[--dev] <package_name>` invocation, tolerant of
    flag order/spacing) and invokes it (`invocation_needle`) in the same
    job body — an ephemeral, not-committed-to-composer.json dependency
    that's still a real, wired CI gate (a target may deliberately keep
    its own dependency manifest free of pure-analysis tooling). Requires
    both signals in the *same file*, the same approximation every other
    self-wired CI-gate check in this module already makes (see
    `_has_ci_job_invoking`)."""
    require_pattern = re.compile(
        r"composer\s+require(?:\s+--dev|\s+-{1,2}dev)?\s+" + re.escape(package_name) + r"\b"
    )
    for pat in [".github/workflows/*.yml", ".github/workflows/*.yaml", ".gitlab-ci.yml"]:
        for f in glob.glob(str(repo / pat)):
            try:
                text = pathlib.Path(f).read_text(encoding="utf-8")
            except OSError:
                continue
            if require_pattern.search(text) and invocation_needle in text:
                return True
    return False


def _has_composer_audit_ci_job(repo: pathlib.Path) -> bool:
    """composer-audit's real fulfilment (php-tooling-tree.md): a CI job that
    runs `composer audit`, gating the pipeline on known advisories."""
    return _has_ci_job_invoking(repo, "composer audit")


# secret-detection's own `Tool: any secret scanner` (tooling-tree.md) — same
# generic-tool shape as test-runner-if-missing's `any test runner`. Checked
# by common invocation needle rather than one fixed tool name.
_SECRET_SCAN_NEEDLES = ("gitleaks", "detect-secrets", "trufflehog")


def _has_secret_scan_ci_job(repo: pathlib.Path) -> bool:
    """secret-detection's real fulfilment (tooling-tree.md): a CI job that
    runs any recognized secret scanner, gating the pipeline against
    committing credentials/tokens. Tool-agnostic by design — checks a small
    set of common invocation needles rather than one fixed tool."""
    return any(_has_ci_job_invoking(repo, needle) for needle in _SECRET_SCAN_NEEDLES)


def _detected_secret_scanner(repo: pathlib.Path) -> str | None:
    """Which of `_SECRET_SCAN_NEEDLES` the CI config actually invokes — first
    match wins, `None` if none do. Exposed in `secret-detection`'s own
    `details` so a later pass (`refactor-scan/SKILL.md` step 4c's own
    history scan) doesn't have to re-derive it by re-reading the CI config
    itself; more than one matching scanner is possible but not disambiguated
    further — the first needle found is what step 4c reuses."""
    for needle in _SECRET_SCAN_NEEDLES:
        if _has_ci_job_invoking(repo, needle):
            return needle
    return None


# coverage-floor's own fulfilment (php-tooling-tree/coverage-floor.md):
# driver-agnostic by design (PCOV vs. Xdebug is a review-time choice, never
# checked here) — only "is coverage actually configured, and (once CI
# exists) enforced" matters. Needle set mirrors _SECRET_SCAN_NEEDLES's own
# shape — a named constant rather than an inline literal, so a future
# invocation spelling (e.g. a bare --coverage-clover with no --coverage
# prefix) is one line to add here, not a buried string to hunt down.
_COVERAGE_CI_NEEDLES = ("--coverage",)


def _has_coverage_report_config(repo: pathlib.Path) -> bool:
    """True if phpunit.xml(.dist) declares a <coverage> report section —
    coverage-floor's own local-adoption half."""
    for name in ("phpunit.xml.dist", "phpunit.xml"):
        p = repo / name
        if p.exists():
            try:
                if re.search(r"<coverage\b", p.read_text(encoding="utf-8")):
                    return True
            except OSError:
                continue
    return False


def _coverage_floor_value(repo: pathlib.Path) -> float | None:
    """The committed `.coverage-floor` ratchet value, if the file exists and
    parses as a number. `None` for both "missing" and "unparseable" — the
    node treats them the same (unfulfilled), never guessing a value."""
    p = repo / ".coverage-floor"
    if not p.exists():
        return None
    try:
        return float(p.read_text(encoding="utf-8").strip())
    except (OSError, ValueError):
        return None


# semgrep's own fulfilment (php-tooling-tree/semgrep.md): a CI job invoking
# semgrep, with an OWASP-Top-10 ruleset reference either inline in the CI
# invocation (the common `--config=p/owasp-top-ten` registry shape) or
# inside a committed .semgrep.yml/.semgrep.yaml. Two needles checked
# independently (not required to co-occur in the same file) — the same
# conservative-approximation looseness this module's other self-wired
# CI-gate checks already accept.
def _has_semgrep_owasp_ci_job(repo: pathlib.Path) -> bool:
    if not _has_ci_job_invoking(repo, "semgrep"):
        return False
    if _has_ci_job_invoking(repo, "owasp"):
        return True
    for name in (".semgrep.yml", ".semgrep.yaml"):
        p = repo / name
        if p.exists():
            try:
                if "owasp" in p.read_text(encoding="utf-8").lower():
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


def _resolve_refactoring_notes_dir(repo: pathlib.Path) -> pathlib.Path:
    """Where the suite keeps its own state in this target repo — the
    Refactoring Notes. Default docs/refactoring/; overridden by a
    `Refactoring Notes: `<path>`` line in the target's AGENTS.md or
    CLAUDE.md (loop-config's own interview writes this once, into whichever
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


def _has_loop_config(repo: pathlib.Path) -> bool:
    """loop-config's fulfilment check: the Refactoring Notes' bookkeeping.md exists
    (default docs/refactoring/bookkeeping.md; see _resolve_refactoring_notes_dir)."""
    return (_resolve_refactoring_notes_dir(repo) / "bookkeeping.md").exists()


def _has_editorconfig(repo: pathlib.Path) -> bool:
    """editorconfig's fulfilment check: .editorconfig exists at
    the repo root. Pure presence check, no equivalent-detection nuance."""
    return (repo / ".editorconfig").exists()


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


def _rector_php_set_level(rector_config_text: str) -> tuple[int, ...] | None:
    """php-minimal-version's only signal (see php-minimal-version.md):
    the specific PHP version `rector-php-set`'s own rule set targets — Rector's
    `LevelSetList::UP_TO_PHP_XY` constant naming (`UP_TO_PHP_82` -> (8, 2),
    `UP_TO_PHP_74` -> (7, 4)), read directly out of `rector.php`/`rector.neon`'s
    text rather than a second, separate config-presence check — same shallow
    substring-approximation style `has_rector_php_set` above already uses; a
    genuine syntax-compatibility scan is out of scope, matching the tree's
    every other Rector-family fulfilment check. `None` when no such constant is
    present (caller only invokes this once `has_rector_php_set` is already
    true, but stays defensive here since a config could plausibly enable the
    rule set through some other syntax this substring match doesn't catch)."""
    m = re.search(r"UP_TO_PHP_(\d)(\d+)", rector_config_text)
    if not m:
        return None
    return (int(m.group(1)), int(m.group(2)))


def php_floor_precheck(repo: pathlib.Path) -> list[dict]:
    """Check the target's current PHP floor once against each of
    `_LEAF_MIN_PHP_VERSION`'s five leaves, instead of proposing (and
    eventually rejecting) each one individually five separate times.
    Returns the leaves whose minimum isn't met yet, each with a
    human-readable reason — `next_candidates()` and `roadmap()` skip these,
    and `detect_and_roadmap()` surfaces the list so a caller can report the
    fact in one pass instead of it silently vanishing.

    Design decision: skip silently, no `docs/refactoring/out-of-scope/`
    entry written for a blocked leaf. The check is cheap and re-derived
    fully from `composer.json` every pass, so nothing is lost by not
    persisting it — and that directory otherwise records a genuine human/
    agent rejection decision (a mechanical-reversal design), not a
    mechanical fact already on disk. Once the target's PHP floor rises, a
    previously-blocked leaf is simply unblocked next pass; there is nothing
    to reverse. The one consequence worth naming: four of these five leaves
    (`php-cs-fixer`, `phpunit`, `test-runner-if-missing`, `composer-audit`)
    are themselves `structural-scan` leaves (php-tooling-tree.md's `resolved`
    edges) — while blocked here, they count as neither fulfilled nor
    rejected, so `structural-scan` stays genuinely closed until the floor
    rises (matching how a target that truly cannot run these tools yet
    shouldn't be treated as tooling-ready). A human who wants
    `structural-scan` to open anyway despite the floor can still file the
    out-of-scope entries by hand — this precheck doesn't do it for them.

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
    structural-scan reading php-structural-scan) — independent of where
    either node happens to sit in ``tree["order"]``.

    ``fulfilled_lookup(name) -> bool`` supplies each ordinary leaf's
    fulfilled state — either the real ``detect_nodes()`` output, or
    ``roadmap()``'s per-iteration simulated snapshot.
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
    notes_rel = _resolve_refactoring_notes_dir(repo).relative_to(repo).as_posix()
    has_loop_config = _has_loop_config(repo)
    set_node("loop-config", has_loop_config, f"{notes_rel}/bookkeeping.md present" if has_loop_config else f"no {notes_rel}/bookkeeping.md")
    # is-php-project: composer.json (recognized location) or at least one
    # *.php file outside vendor/ — see tooling-tree.md's own node entry for
    # the "why not composer.json-only" rationale.
    has_php_files = _has_php_files(repo)
    is_php_project = has_composer_json or has_php_files
    set_node(
        "is-php-project", is_php_project,
        "composer.json or *.php files present" if is_php_project else "no composer.json and no *.php files found",
        has_composer_json=has_composer_json, has_php_files=has_php_files,
    )
    # composer
    set_node("composer", has_composer_json and has_lock, "composer.json+lock present" if has_composer_json and has_lock else "missing composer.json or lock", has_json=has_composer_json, has_lock=has_lock)
    # psr-4: declared AND verifiably in use (see _has_verified_psr4_autoload's
    # own docstring for why declaration alone isn't enough), AND the
    # autoloader wired into the target's own Composition root/Entry points
    # (see _autoloader_wired's own docstring) — a target can have proven the
    # mapping mechanism works yet still never actually load its own code
    # through it at request time.
    has_psr4_declared = _psr4_root_namespace(composer) is not None
    psr4_mechanism_verified = _has_verified_psr4_autoload(repo, composer)
    if psr4_mechanism_verified:
        autoloader_wired, unwired_entry_points = _autoloader_wired(repo, composer)
    else:
        autoloader_wired, unwired_entry_points = False, []
    psr4_verified = psr4_mechanism_verified and autoloader_wired
    if psr4_verified:
        psr4_reason = "autoload.psr-4 declared, in use, and the autoloader is wired in"
    elif psr4_mechanism_verified:
        psr4_reason = "autoload.psr-4 declared and in use, but the autoloader isn't wired into the entry points/composition root yet"
    elif has_psr4_declared:
        psr4_reason = "autoload.psr-4 declared but no file under it uses the namespace yet"
    else:
        psr4_reason = "no autoload.psr-4 declared"
    set_node(
        "psr-4", psr4_verified, psr4_reason,
        declared=has_psr4_declared, mechanism_verified=psr4_mechanism_verified,
        autoloader_wired=autoloader_wired, unwired_entry_points=unwired_entry_points,
    )
    # ci-runner
    set_node("ci-runner", has_ci, "CI config present" if has_ci else "no CI config")
    # secret-detection: generic root, no resolved edge into structural-scan
    # (tooling-tree.md's own node entry states why) — fulfilled once CI gates
    # on any recognized secret scanner.
    secret_scan_fulfilled = _has_secret_scan_ci_job(repo)
    set_node(
        "secret-detection",
        secret_scan_fulfilled,
        "CI job runs a secret scanner" if secret_scan_fulfilled else "no CI job runs a secret scanner yet",
        scanner=_detected_secret_scanner(repo),
    )
    # editorconfig
    has_editorconfig = _has_editorconfig(repo)
    set_node("editorconfig", has_editorconfig, ".editorconfig present" if has_editorconfig else "no .editorconfig")
    # php-cs-fixer
    cs_fulfilled = has_cs_dep and has_cs_config
    set_node("php-cs-fixer", cs_fulfilled, "dep and config present" if cs_fulfilled else "missing cs-fixer (need dep + config)", has_dep=has_cs_dep, has_config=has_cs_config)
    # phpmd — same dep+config approximation as php-cs-fixer above, no
    # resolved edge into php-structural-scan (php-tooling-tree.md's own node
    # entry states why): a Signal-producing node, not a Safety Net one.
    has_phpmd_dep = _has_dep(composer, "phpmd/phpmd")
    has_phpmd_config = (repo / "phpmd.xml").exists() or (repo / "phpmd.xml.dist").exists() or (repo / ".phpmd.xml").exists()
    phpmd_fulfilled = has_phpmd_dep and has_phpmd_config
    set_node("phpmd", phpmd_fulfilled, "dep and config present" if phpmd_fulfilled else "missing phpmd (need dep + config)", has_dep=has_phpmd_dep, has_config=has_phpmd_config)
    # phpunit — adopted AND, once ci-runner is fulfilled, actually gated in
    # CI (self-wiring: folded into this node's own fulfilment
    # check instead of a separate CI-job node). No CI yet still fulfils the
    # node on adoption alone — nothing to wire in until CI exists.
    phpunit_adopted = has_phpunit or has_pest or has_phpunit_xml
    phpunit_ci_needle = "vendor/bin/pest" if has_pest else "vendor/bin/phpunit"
    phpunit_ci_ok = (not has_ci) or _has_ci_job_invoking(repo, phpunit_ci_needle)
    phpunit_fulfilled = phpunit_adopted and phpunit_ci_ok
    if phpunit_fulfilled:
        phpunit_reason = "phpunit/pest present"
    elif phpunit_adopted:
        phpunit_reason = "adopted locally but not gated in CI"
    else:
        phpunit_reason = "no test runner"
    set_node("phpunit", phpunit_fulfilled, phpunit_reason, has_phpunit=has_phpunit, has_pest=has_pest)
    # coverage-floor: local adoption (a <coverage> report configured, a
    # committed .coverage-floor ratchet value) plus, once ci-runner is
    # fulfilled, the same self-wiring CI-gate pattern phpunit's own check
    # above already uses. Driver-agnostic (php-tooling-tree/coverage-floor.md
    # states why) — never checks for "pcov"/"xdebug" by name.
    has_coverage_config = _has_coverage_report_config(repo)
    coverage_floor_value = _coverage_floor_value(repo)
    has_coverage_floor = coverage_floor_value is not None
    coverage_ci_ok = (not has_ci) or any(_has_ci_job_invoking(repo, needle) for needle in _COVERAGE_CI_NEEDLES)
    coverage_fulfilled = has_coverage_config and has_coverage_floor and coverage_ci_ok
    if coverage_fulfilled:
        coverage_reason = "coverage configured, floor committed, CI-gated"
    elif has_coverage_config and has_coverage_floor:
        coverage_reason = "coverage and floor present but not gated in CI"
    elif has_coverage_config:
        coverage_reason = "coverage configured but no .coverage-floor committed"
    else:
        coverage_reason = "no coverage report configured"
    set_node(
        "coverage-floor",
        coverage_fulfilled,
        coverage_reason,
        has_coverage_config=has_coverage_config,
        floor=coverage_floor_value,
    )
    # test-runner-if-missing: fulfilled once *any* runner is adopted, full
    # stop — independent of phpunit's CI-gating above. This node only
    # answers "does a runner exist at all", not "is it enforced in CI"
    # (php-tooling-tree.md).
    tr_fulfilled = phpunit_adopted
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
    # static-code-analyzer: pure organizational/plumbing node,
    # always fulfilled once composer is — no independent state of its own.
    set_node(
        "static-code-analyzer",
        out["composer"]["fulfilled"],
        "composer fulfilled" if out["composer"]["fulfilled"] else "waiting on composer",
    )
    # psalm: recognition-only, never proposed (see _NEVER_PROPOSED below). No
    # CI-gating requirement.
    psalm_fulfilled = has_psalm_dep and has_psalm_cfg
    set_node(
        "psalm",
        psalm_fulfilled,
        "vimeo/psalm + psalm.xml present" if psalm_fulfilled else "no psalm dep/config",
        has_psalm_dep=has_psalm_dep,
        has_psalm_cfg=has_psalm_cfg,
    )

    # phpstan-level-0
    # Self-wiring: once ci-runner is fulfilled, this node also
    # requires a CI job that actually invokes phpstan. The invocation is
    # level-independent (`vendor/bin/phpstan analyse` regardless of the
    # configured level), so gating it once here covers the whole
    # phpstan-level-1..3 chain — those nodes stay CI-agnostic on purpose.
    phpstan_p0_ci_ok = (not has_ci) or _has_ci_job_invoking(repo, "vendor/bin/phpstan analyse")
    # A target may deliberately keep phpstan out of its own composer.json,
    # installing it at CI-runtime only instead — still a real, wired gate,
    # just not detectable via composer.json alone.
    ephemeral_ci_dep = has_ci and _has_ephemeral_ci_dep(repo, "phpstan/phpstan", "vendor/bin/phpstan analyse")
    has_phpstan_dep_or_ephemeral = has_phpstan_dep or ephemeral_ci_dep
    # Psalm equivalence: fulfilled without phpstan whenever the `psalm` node
    # (above) is fulfilled — reads that node's computed state instead of
    # re-deriving the raw detection here. Co-presence (phpstan.md, psalm.md):
    # if PHPStan is *also* genuinely adopted (a real dependency, actually
    # configured with a level), PHPStan is the authoritative check and this
    # equivalence must not apply — Psalm fulfilment is superseded, not
    # additive. Without this guard, a target that adopts both (the ordinary
    # case once `psalm-taint-analysis` is layered onto an existing PHPStan
    # setup) would wrongly read every phpstan-level-N as "not applicable",
    # corrupting `refactor-learn`'s `Fulfilled nodes` overwrite the moment a
    # pass with parser access ran (confirmed live on `Art4/legacy-todo`:
    # already-fulfilled phpstan-level-1..5 vanished from the cache).
    phpstan_genuinely_adopted = has_phpstan_dep_or_ephemeral and phpstan_level is not None
    psalm_fulfils_p0 = psalm_fulfilled and not phpstan_genuinely_adopted
    # `phpstan_level == 0` here would mean this node goes right back to
    # unfulfilled the moment a project advances to level 1 — breaking the
    # level-1..10 chain's own required-parent-stays-fulfilled assumption
    # (a level-N node requires its predecessor fulfilled, forever, not just
    # at the moment it was first reached). Level 0's own checks (dep +
    # baseline + CI gate) are satisfied by any parsed level, so this reads
    # "some level is configured", not "level is still exactly 0".
    if psalm_fulfils_p0:
        set_node("phpstan-level-0", True, "psalm fulfils p0 (vimeo/psalm + psalm.xml)", has_psalm=True)
    elif has_phpstan_dep_or_ephemeral and phpstan_level is not None and baseline_exists and phpstan_p0_ci_ok:
        set_node("phpstan-level-0", True, "phpstan level 0 + baseline present", level=phpstan_level, baseline_empty=baseline_empty, ephemeral_ci_dep=ephemeral_ci_dep)
    elif has_phpstan_dep_or_ephemeral and phpstan_level is not None and baseline_exists and not phpstan_p0_ci_ok:
        # locally green, but CI exists and doesn't gate on it yet — the
        # baseline this level sets is only durable once CI enforces it.
        set_node("phpstan-level-0", False, "level 0 baseline green locally but not gated in CI", level=phpstan_level, baseline_empty=baseline_empty, ephemeral_ci_dep=ephemeral_ci_dep)
    elif has_phpstan_dep_or_ephemeral and phpstan_level is not None and not baseline_exists:
        # some level configured but no baseline yet -> not green, not fulfilled
        set_node("phpstan-level-0", False, "phpstan level configured but baseline missing", level=phpstan_level, ephemeral_ci_dep=ephemeral_ci_dep)
    else:
        set_node("phpstan-level-0", False, "missing phpstan, no level configured, or no baseline", has_phpstan=has_phpstan_dep, level=phpstan_level, baseline_exists=baseline_exists, ephemeral_ci_dep=ephemeral_ci_dep)

    # phpstan-level-1..10 — phpstan-level-5 is the chain's resolved-leaf
    # into php-structural-scan (see that node); levels 6-10 stay ordinary,
    # non-gating, still-proposable chain nodes.
    # For fulfilled check: level >= N
    for lvl in range(1, 11):
        node = f"phpstan-level-{lvl}"
        if psalm_fulfils_p0:
            # Psalm path: level nodes not applicable -> treat as not unblocked (blocked by equivalence)
            set_node(node, False, "not applicable: psalm fulfils p0", psalm_equivalent=True)
            continue
        fulfilled = (phpstan_level is not None and phpstan_level >= lvl)
        # For roadmap gate, predecessor must be fulfilled with empty baseline
        # We expose details
        set_node(node, fulfilled, f"level {phpstan_level} >= {lvl}" if fulfilled else f"level {phpstan_level} < {lvl} or no phpstan", level=phpstan_level, baseline_empty=baseline_empty)

    # phpstan-deprecation-rules: dependency-presence approximation,
    # same simplification style as php-cs-fixer's dep+config check — no real
    # `vendor/bin/phpstan analyse` invocation in this dry-run parser.
    has_deprecation_rules_dep = _has_dep(composer, "phpstan/phpstan-deprecation-rules")
    set_node(
        "phpstan-deprecation-rules",
        has_deprecation_rules_dep,
        "phpstan-deprecation-rules present" if has_deprecation_rules_dep else "no phpstan-deprecation-rules dep",
    )

    # psalm-taint-analysis: security-focused taint analysis,
    # orthogonal to which general analyzer was chosen — required-any parent
    # (phpstan-level-4 OR psalm) is checked separately by _is_unblocked(),
    # this only computes the node's own fulfilment. Deliberately reuses
    # has_psalm_dep/has_psalm_cfg (already computed above for the `psalm`
    # node) rather than re-deriving them — same dep+config signal, disjoint
    # concern (taint mode is a CI-invocation flag, not a config difference),
    # so the CI check below is what actually disambiguates this node from a
    # target that merely adopted Psalm as its general analyzer.
    taint_ci_ok = (not has_ci) or _has_ci_job_invoking(repo, "vendor/bin/psalm --taint-analysis")
    taint_fulfilled = has_psalm_dep and has_psalm_cfg and taint_ci_ok
    if taint_fulfilled:
        taint_reason = "vimeo/psalm + psalm.xml present, --taint-analysis gated in CI"
    elif has_psalm_dep and has_psalm_cfg:
        taint_reason = "psalm present but --taint-analysis not gated in CI"
    else:
        taint_reason = "no psalm dep/config"
    set_node(
        "psalm-taint-analysis",
        taint_fulfilled,
        taint_reason,
        has_psalm_dep=has_psalm_dep,
        has_psalm_cfg=has_psalm_cfg,
    )

    # semgrep: OWASP Top 10 coverage, complementary to psalm-taint-analysis
    # above rather than gated by its own dep/config -- Semgrep is a
    # standalone tool, never a composer.json entry. Recommended-parent
    # eligibility (whether psalm-taint-analysis is *decided* yet) is
    # handled separately by _is_unblocked(); this only computes the node's
    # own fulfilment.
    semgrep_fulfilled = _has_semgrep_owasp_ci_job(repo)
    set_node(
        "semgrep",
        semgrep_fulfilled,
        "semgrep + OWASP ruleset gated in CI" if semgrep_fulfilled else "no semgrep/OWASP CI job yet",
    )

    # rector
    # Fulfilment: dead-code suite enabled and fully applied — we approximate as False unless rector.php contains dead-code set
    has_rector = (repo / "rector.php").exists() or (repo / "rector.neon").exists()
    has_rector_dead = False
    has_rector_types = False
    has_rector_php_set = False
    has_rector_code_quality = False
    has_rector_phpunit_set = False
    if has_rector:
        txt = ""
        for p in [repo / "rector.php", repo / "rector.neon"]:
            if p.exists():
                txt += p.read_text(encoding="utf-8")
        # Substring detection has to tolerate both Rector SetList naming
        # styles actually seen in the wild: older/prose-ish "DeadCode" and
        # the current SetList::DEAD_CODE-style ALL_CAPS-with-underscores
        # constants. Lowercasing alone doesn't bridge the two — "DEAD_CODE"
        # lowercases to "dead_code", not "dead-code" — so each check
        # normalizes underscores to hyphens before comparing.
        norm = txt.lower().replace("_", "-")
        has_rector_dead = "DeadCode" in txt or "dead-code" in norm
        has_rector_types = "Type" in txt or "type" in txt.lower()
        has_rector_php_set = "LevelSetList" in txt or "php-set" in norm
        has_rector_code_quality = "CodeQuality" in txt or "code-quality" in norm
        has_rector_phpunit_set = "PHPUnitSetList" in txt or "phpunit-set" in norm
        rector_php_set_level = _rector_php_set_level(txt) if has_rector_php_set else None
    else:
        rector_php_set_level = None
    set_node("rector-dead-code", has_rector_dead, "rector dead-code set present" if has_rector_dead else "no rector dead-code", has_rector=has_rector)
    set_node("rector-type-coverage", has_rector_types, "rector type coverage present" if has_rector_types else "no rector type coverage", has_rector=has_rector)
    # rector-php-set and its 2 children: same has_rector-gated
    # substring-detection style as dead-code/type-coverage above.
    set_node("rector-php-set", has_rector_php_set, "rector php-version set present" if has_rector_php_set else "no rector php-version set", has_rector=has_rector)
    set_node("rector-code-quality", has_rector_code_quality, "rector code-quality set present" if has_rector_code_quality else "no rector code-quality set", has_rector=has_rector)
    set_node("rector-phpunit-set", has_rector_phpunit_set, "rector phpunit set present" if has_rector_phpunit_set else "no rector phpunit set", has_rector=has_rector)

    # php-minimal-version: a Floor correction only, never a
    # Floor raise (CONTEXT.md) — composer.json's declared PHP floor vs. the
    # PHP-version level rector-php-set has actually applied. Required parent
    # of this node (php-tooling-tree.md's edge table), so this must run
    # after rector-php-set's own detection above, not before it.
    current_php_floor = _current_php_floor(composer)
    if current_php_floor is None:
        set_node(
            "php-minimal-version", True,
            "PHP floor undeterminable (no composer.json) — nothing to correct",
        )
    elif rector_php_set_level is None:
        set_node(
            "php-minimal-version", True,
            "no rector-php-set level applied yet — nothing to correct",
            floor=list(current_php_floor),
        )
    elif current_php_floor >= rector_php_set_level:
        set_node(
            "php-minimal-version", True,
            f"floor {'.'.join(map(str, current_php_floor))} already matches rector-php-set's applied "
            f"PHP {'.'.join(map(str, rector_php_set_level))}",
            floor=list(current_php_floor), rector_level=list(rector_php_set_level),
        )
    else:
        set_node(
            "php-minimal-version", False,
            f"floor {'.'.join(map(str, current_php_floor))} behind rector-php-set's applied "
            f"PHP {'.'.join(map(str, rector_php_set_level))}",
            floor=list(current_php_floor), rector_level=list(rector_php_set_level),
        )

    # Resolved-gated nodes: structural-scan, and PHP's own aggregation node
    # php-structural-scan feeding it — fulfilled once every one of a node's
    # `resolved` parents is fulfilled OR recorded as rejected. Unlike a
    # required parent, a rejected resolved parent still counts as resolved.
    # Generic over every such node (see _resolved_gate_status), computed in
    # dependency order so php-structural-scan's status is already known by
    # the time structural-scan's own check reads it.
    rejected = _rejected_nodes(repo)
    gate = _resolved_gate_status(tree, lambda n: out.get(n, {}).get("fulfilled", False), rejected)
    for node, (resolved, unresolved) in gate.items():
        set_node(
            node,
            resolved,
            "all resolved-parent leaves resolved (fulfilled or rejected)" if resolved else f"waiting on: {', '.join(unresolved)}",
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
    # required-any: at least one, not all, must be fulfilled.
    # Combines with the ordinary required parents above via AND (both checks
    # must pass); within this group the parents combine via OR.
    req_any = tree["required_any_parents"].get(node, [])
    if req_any and not any(fulfilled.get(p, {}).get("fulfilled", False) for p in req_any):
        return False, f"blocked — none of required-any parents fulfilled: {', '.join(req_any)}"
    return True, "required parents fulfilled"


def _composer_audit_extra_gate(has_real_dep: bool, tree: dict, resolved_check: dict, rejected: set[str]) -> tuple[bool, str]:
    """composer-audit's stop condition beyond required-edge fulfilment
    (php-tooling-tree.md): proposable once a real `require` dependency
    exists, or every *other* leaf feeding php-structural-scan (its true
    siblings under the aggregation node, not structural-scan's own
    resolved-parents, which is just {editorconfig, php-structural-scan}) is
    already resolved — independent alternatives, not ordered.
    `resolved_check` maps node name to a bool: already fulfilled (real or
    simulated). A leaf counts as resolved when fulfilled, directly rejected,
    or effectively rejected (`_is_effectively_rejected` — closed for good
    because a required ancestor of the leaf is rejected, e.g.
    `phpstan-level-5` behind a rejected `phpstan-level-2`) — the same
    `resolved`-gate semantics `_resolved_gate_status()` already applies to
    the same leaf set, one gate condition over."""
    if has_real_dep:
        return True, "real require dependency present"
    leaves = tree["resolved_parents"].get("php-structural-scan", [])
    other_leaves = [leaf for leaf in leaves if leaf != "composer-audit"]
    unresolved = [
        leaf for leaf in other_leaves
        if not (resolved_check.get(leaf, False) or _is_effectively_rejected(leaf, tree, rejected))
    ]
    if not unresolved:
        return True, "no real dependency yet, but every other leaf feeding php-structural-scan is resolved"
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
    php_floor_blocked = {b["node"] for b in php_floor_precheck(repo)}

    result: list[dict] = []
    for node in tree["order"]:
        if node in _NEVER_PROPOSED:
            continue
        if tree["resolved_parents"].get(node):
            # Resolved-gated node (structural-scan, and any aggregation node
            # feeding it, e.g. php-structural-scan). Checked on its own
            # terms, *before* the generic fulfilled-skip below: detect_nodes()
            # marks such a node "fulfilled" the instant its resolved-parent
            # leaves resolve, but for an *exposed* one that's the gate
            # *opening*, not the node being delivered and done (unlike every
            # other tooling node, where fulfilled really does mean "don't
            # propose again"). Gating on the generic skip here made this
            # branch permanently unreachable dead code — an exposed
            # resolved-gated node must stay proposable every pass once open:
            # it's an ongoing candidate for refactor-design to keep drawing
            # on, not a one-time node. An aggregation node that isn't itself
            # exposed (its resolved-ness only feeds another resolved-gated
            # node) is never proposed at all, whatever its resolved state.
            if node not in tree["exposed_resolved_gate_nodes"]:
                continue
            if not detected.get(node, {}).get("fulfilled", False):
                continue
            result.append({"node": node, "reason": detected[node]["reason"]})
        else:
            if detected.get(node, {}).get("fulfilled", False):
                continue
            if node in rejected:
                continue  # explicitly rejected — stays out until its out-of-scope entry is reversed
            if node in php_floor_blocked:
                continue  # target's PHP floor doesn't meet this leaf's known minimum yet
            if _recommended_gate_moot(node, tree, detected):
                continue  # every recommended parent permanently gated (e.g. whole PHP tree closed by is-php-project) — not actionable, not even withheld
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
            if node in _PHPSTAN_LEVEL_NODES:
                # Empty-baseline stop condition (php-tooling-tree/phpstan.md's
                # "Stop conditions": baseline non-empty -> do not propose the
                # next level). _is_unblocked() above only checks required-
                # parent fulfilment (predecessor level reached), which says
                # nothing about the *current* baseline's contents — a real
                # target sitting on a fulfilled level with real, unshrunk
                # baseline entries would otherwise get the next level
                # proposed regardless. roadmap() already applies this same
                # gate during its own simulation; next_candidates() needs it
                # too since it's the set refactor-scan actually proposes from.
                if not _is_baseline_empty(repo):
                    continue
                if detected.get("phpstan-level-0", {}).get("details", {}).get("has_psalm"):
                    continue
            result.append({"node": node, "reason": why})
        if limit is not None and len(result) >= limit:
            break
    return result


def directly_unblocked_children(repo: pathlib.Path, landed_node: str, tree: dict | None = None) -> list[dict]:
    """Every node this one candidate's fulfilment newly makes proposable —
    the fan-out an MR's outlook diagram draws
    (``opening-a-merge-request.md``), distinct from ``roadmap(steps=1)``'s
    single top-priority pick.

    Walks ``landed_node``'s direct children in the edge table. A child
    that's never itself a real candidate — ``_NEVER_PROPOSED`` for
    structural/plumbing reasons (``static-code-analyzer``), or a
    resolved-gated aggregation node that isn't itself exposed
    (``php-structural-scan``) — is walked *through* to its own children
    instead of being reported, the same "not proposed itself, but its
    resolved-ness matters" treatment ``next_candidates()`` gives these
    nodes. The walk only continues past such a node while it's actually
    fulfilled/resolved right now; otherwise that branch contributes
    nothing and stops there.

    "Newly" unblocked is decided by a counterfactual: would this same node
    already have been proposable with ``landed_node``'s own fulfilled flag
    forced back to `False`? A `required-any` child also reachable via
    another already-fulfilled sibling parent answers yes — excluded, it
    was reachable before this candidate too, not newly opened by it.
    Every other gate ``next_candidates()`` applies (rejected, PHP floor,
    undecided recommended parents, `composer-audit`'s extra condition, the
    PHPStan baseline stop-condition) is independent of ``landed_node``'s
    own flag, so a node's current membership in ``next_candidates()``
    already answers those for both the "now" and "before" snapshots alike
    — only the required/required-any check itself needs re-evaluating
    under the counterfactual, not a second full tree scan.
    """
    repo = pathlib.Path(repo)
    if tree is None:
        tree = load_tree()
    if landed_node not in tree["nodes"]:
        return []

    detected = detect_nodes(repo, tree)
    detected["git"]["fulfilled"] = True  # never proposed
    rejected = _rejected_nodes(repo)

    # Counterfactual snapshot: landed_node never happened.
    # static-code-analyzer's own fulfilled flag is hardcoded to mirror
    # composer's (detect_nodes, above) rather than being independently
    # detected — keep that same derivation consistent here, or the
    # counterfactual would misreport composer's own downstream plumbing.
    detected_without = {k: dict(v) for k, v in detected.items()}
    detected_without[landed_node]["fulfilled"] = False
    if "static-code-analyzer" in detected_without:
        detected_without["static-code-analyzer"]["fulfilled"] = detected_without.get("composer", {}).get("fulfilled", False)
    if landed_node == "psalm" and detected.get("phpstan-level-0", {}).get("details", {}).get("has_psalm"):
        # phpstan-level-0's own fulfilled flag came from the Psalm-equivalence
        # branch above (`psalm_fulfils_p0`) -- that branch's if/elif shortcut
        # means we can't tell whether the real, independent PHPStan check
        # would also have passed once psalm's flag is hidden. Counting it as
        # unfulfilled too is the safe direction to be wrong in: it risks one
        # extra diagram entry (rector-php-set attributed to psalm even if
        # phpstan-level-0 would have covered it too), never a silently
        # missing one for a genuinely psalm-only target.
        detected_without["phpstan-level-0"]["fulfilled"] = False

    gate_now = _resolved_gate_status(tree, lambda n: detected.get(n, {}).get("fulfilled", False), rejected)
    gate_without = _resolved_gate_status(tree, lambda n: detected_without.get(n, {}).get("fulfilled", False), rejected)
    next_now = {c["node"] for c in next_candidates(repo, tree=tree)}

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
                fulfilled_now = gate_now.get(child, (False, []))[0]
            else:
                fulfilled_now = detected.get(child, {}).get("fulfilled", False)
            if fulfilled_now:
                frontier.extend((e["to"], e["type"]) for e in children_of.get(child, []))
            continue

        if child not in next_now:
            continue  # not a real candidate right now — blocked by something else too

        if tree["resolved_parents"].get(child):
            already_before = gate_without.get(child, (False, []))[0]
        else:
            already_before, _why = _is_unblocked(child, tree, detected_without)
        if already_before:
            continue  # reachable via some other already-fulfilled parent too — not new

        result.append({"node": child, "type": edge_type})
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
    php_floor_blocked = {b["node"] for b in php_floor_precheck(repo)}

    result: list[dict] = []
    for node in tree["order"]:
        if node in _NEVER_PROPOSED or tree["resolved_parents"].get(node):
            # Resolved-gated nodes (structural-scan, and any aggregation
            # node feeding it, e.g. php-structural-scan) are never withheld
            # by recommended-edge gating — they're gated by `resolved`
            # edges entirely, handled in next_candidates() instead.
            continue
        if detected.get(node, {}).get("fulfilled", False) or node in rejected:
            continue
        if node in php_floor_blocked:
            continue  # no recommended edge targets these leaves today, but stays consistent if one ever does
        if _recommended_gate_moot(node, tree, detected):
            continue  # every recommended parent permanently gated — see next_candidates()
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
    php_floor_blocked = {b["node"] for b in php_floor_precheck(repo)}

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
        # Fresh per-iteration resolved-gate status for every resolved-gated
        # node (structural-scan, and PHP's own aggregation node
        # php-structural-scan feeding it), computed from this iteration's
        # sim_fulfilled snapshot — independent of tree["order"] position, so
        # structural-scan's own check below reads php-structural-scan's
        # already-resolved status correctly even though the generic root's
        # structural-scan node sorts earlier in tree["order"] than the PHP
        # tree's aggregation node.
        gate = _resolved_gate_status(tree, lambda n: sim_fulfilled.get(n, False), rejected)
        # Find best unblocked candidate among tooling nodes
        best = None
        best_reason = ""
        for node in priority:
            if node in _NEVER_PROPOSED:
                continue  # never an MR / never a candidate
            if tree["resolved_parents"].get(node):
                # `resolved` gate: checked on its own terms, *before* the
                # generic sim_fulfilled-skip below — mirrors
                # next_candidates()'s ordering. sim_fulfilled marks a
                # resolved-gated node "fulfilled" the instant its gate opens,
                # but for an *exposed* one that's the gate *opening*, not the
                # node being delivered and done: it must stay proposable
                # every iteration once open (e.g. structural-scan keeps
                # accepting planted structural candidates), not just the one
                # iteration it first resolves in. Gating this behind the
                # generic skip made it unreachable once already simulated
                # fulfilled: once every PHP-tree leaf is resolved, the loop
                # would skip structural-scan every iteration and fall
                # through to the phantom phpstan-level-N "open chain" filler
                # forever instead of ever proposing structural-scan again.
                #
                # Every resolved-parent leaf must be fulfilled OR rejected —
                # not the standard required-parent check, which would
                # instead close this node forever on any rejection. Applies
                # to any resolved-gated node (structural-scan, and any
                # aggregation node feeding it, e.g. php-structural-scan) —
                # `gate` (computed fresh this iteration, above) already
                # resolves an aggregation node's own status first, so
                # structural-scan's check reads it correctly regardless of
                # tree["order"] position. An aggregation node that isn't
                # itself exposed is never a candidate, whatever its resolved
                # state.
                if node not in tree["exposed_resolved_gate_nodes"]:
                    continue
                resolved, _unresolved = gate[node]
                if not resolved:
                    continue
                best = node
                best_reason = "all resolved-parent leaves resolved (fulfilled or rejected)"
                break
            if sim_fulfilled.get(node, False):
                continue  # already fulfilled (real or simulated), skip
            if node in rejected:
                continue  # explicitly rejected — stays out until its out-of-scope entry is reversed
            if node in php_floor_blocked:
                continue  # target's PHP floor doesn't meet this leaf's known minimum yet
            # test-runner-if-missing is fulfilled if phpunit/pest already fulfilled (simulated) —
            # phpunit fulfilled implies a runner is adopted, so proposing this one too is redundant.
            if node == "test-runner-if-missing" and sim_fulfilled.get("phpunit"):
                continue
            # No symmetric skip the other way: test-runner-if-missing fulfilled no
            # longer implies phpunit fulfilled — a runner can be adopted (satisfying
            # test-runner-if-missing) while phpunit's own CI-gating requirement is still open, and
            # that's a genuinely different, still-proposable candidate (wire it into CI).
            sim_ok, sim_why = _is_unblocked(node, tree, {k: {"fulfilled": v} for k, v in sim_fulfilled.items()})
            if not sim_ok:
                continue
            if node == "composer-audit":
                has_real_dep = detected.get("composer-audit", {}).get("details", {}).get("has_real_dep", False)
                sim_ok, sim_why = _composer_audit_extra_gate(has_real_dep, tree, sim_fulfilled, rejected)
                if not sim_ok:
                    continue
            # For phpstan levels, the level chain's own empty-baseline gate
            # (phpstan.md's Stop conditions): predecessor level fulfilled AND
            # its baseline currently empty. roadmap() is a deterministic
            # simulation over real repo state, not a second engine — it
            # doesn't simulate baseline-shrink candidates landing (that's
            # real, skill-prose-driven work: refactor-scan step 4b proposes
            # the gate, refactor-design's phpstan-baseline-shrink.md picks
            # the fix). A non-empty baseline just stops the chain here for
            # the rest of this simulation, same as it does for real in
            # next_candidates().
            if node in _PHPSTAN_LEVEL_NODES:
                lvl = int(node.rsplit("-", 1)[1])
                pred = "phpstan-level-0" if lvl == 1 else f"phpstan-level-{lvl - 1}"
                if not sim_fulfilled.get(pred, False):
                    continue
                if not _is_baseline_empty(repo):
                    continue
                if detected.get("phpstan-level-0", {}).get("details", {}).get("has_psalm"):
                    continue
            # For rector nodes: require p0 fulfilled (already checked), recommended parents are advisory not blocking
            # Choose best by priority order (first found)
            best = node
            best_reason = sim_why
            break
        if best:
            req = tree["required_parents"].get(best, [])
            req_any = tree["required_any_parents"].get(best, [])
            rec = tree["recommended_parents"].get(best, [])
            # Outlook note for recommended parents missing
            outlook = ""
            for rp in rec:
                # check if recommended parent not fulfilled
                if not fulfilled.get(rp, False) and rp not in [r["node"] for r in result]:
                    outlook = f" | outlook: would benefit from {rp} (recommended) — still proposable"
                    break
            result.append({"n": len(result) + 1, "node": best, "type": "tooling", "required_parents": req, "required_any_parents": req_any, "recommended_parents": rec, "reason": best_reason + outlook})
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
            nxt = 11 + len([r for r in result if "phpstan-level" in r["node"]])
            result.append({"n": len(result) + 1, "node": f"phpstan-level-{nxt}", "type": "tooling (open chain)", "reason": "chain open above level 10 — appended node"})
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
    php_floor_blocked = php_floor_precheck(repo)
    return {
        "detected": detected,
        "roadmap": road,
        "next": nxt,
        "withheld": withheld,
        "reversals": reversals,
        "php_floor_blocked": php_floor_blocked,
        "tree": {"edges": tree["edges"]},
    }


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser(description="Detect tooling tree and propose next MRs (dry-run, no mutation)")
    ap.add_argument("repo", nargs="?", default=".", help="path to fixture/repo (default: .)")
    ap.add_argument("--steps", type=int, default=10, help="depth of the simulated `roadmap` lookahead — does not bound `next`, which is always every currently-unblocked node")
    ap.add_argument("--tree", type=str, default=None, help="path to a single tree file to use instead of the suite's own generic root + PHP tree (single-file mode, e.g. for a synthetic test tree). Only scopes edges/gating (next, roadmap, tree.edges) -- detect_nodes' per-tool filesystem checks are hardcoded and always run regardless of --tree, so 'detected' in the JSON output may list nodes your override tree doesn't even define")
    ap.add_argument("--json", action="store_true", help="output JSON (default)")
    ap.add_argument("--unblocked-by", type=str, default=None, metavar="NODE", help="add an 'unblocked_by' key: every node NODE's fulfilment newly makes proposable (opening-a-merge-request.md's outlook diagram) -- additive, does not change next/roadmap/detected")
    args = ap.parse_args()
    repo = pathlib.Path(args.repo)
    tree_md = pathlib.Path(args.tree) if args.tree else None
    data = detect_and_roadmap(repo, steps=args.steps, tree_md=tree_md)
    if args.unblocked_by:
        tree = load_tree(tree_md=tree_md)
        data["unblocked_by"] = directly_unblocked_children(repo, args.unblocked_by, tree=tree)
    # also add branch check: ensure no extra branches created
    # include git status
    print(json.dumps(data, indent=2))
