#!/usr/bin/env bash
# fixtures/harness/run.sh
# Main harness script: loads fixture, runs opencode, checks artifacts

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"
FIXTURES_DIR="$REPO_DIR/fixtures"
LIB_DIR="$SCRIPT_DIR/lib"

# Load assertion library
source "$LIB_DIR/assertions.sh"

usage() {
    cat <<EOF
Usage: $(basename "$0") <tier> <fixture> [options]

Tiers:
    tier2       Run artifact contract tests
    tier3       Run ground-truth precision/recall tests (also checks recall against the committed baseline — ticket 27)
    tier4       Trigger/discoverability tests: explicit+implicit invocation per skill, negative controls (fixture: php-clean; local-only, see fixtures/README.md)
    roadmap     Dry-run: detect tools, show decision chain and next 10 MRs (no MR created)
    agent-loop  Prepare an isolated sandbox + prompt for a full-pass, Agent-tool-subagent-observed run (local-only, see fixtures/README.md)
    judge       LLM-judge rubric grading against fixtures/harness/rubric.md (local-only, advisory — ticket 27)
    lift        With-skill vs without-skill lift measurement (local-only, advisory — ticket 27)

Options:
    --php-version VERSION   PHP version for Docker (default: 8.3)
    --verbose               Enable verbose output
    --opencode              Also run opencode isolated as subprocess (advisory, needs opencode binary)

Examples:
    $(basename "$0") tier2 php-project-with-candidates
    $(basename "$0") tier3 php-project-with-candidates --php-version 8.2
    $(basename "$0") tier4 php-clean --opencode --verbose
    $(basename "$0") roadmap php-empty
    $(basename "$0") roadmap php-p0-empty --verbose
    $(basename "$0") roadmap php-empty --opencode --verbose   # deterministic + opencode comparison
    $(basename "$0") agent-loop php-partial                   # prepare sandbox + prompt, then spawn a subagent yourself
    $(basename "$0") judge php-project-with-candidates --opencode
    $(basename "$0") lift php-partial --opencode
EOF
    exit 1
}

# Parse options
PHP_VERSION="${PHP_VERSION:-8.3}"
VERBOSE=false
WITH_OPENCODE=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        --php-version)
            PHP_VERSION="$2"
            shift 2
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        --opencode)
            WITH_OPENCODE=true
            shift
            ;;
        *)
            break
            ;;
    esac
done

if [[ $# -lt 2 ]]; then
    usage
fi

TIER="$1"
FIXTURE="$2"
shift 2

# Parse trailing options (e.g., --opencode after fixture: roadmap php-empty --opencode)
while [[ $# -gt 0 ]]; do
    case "$1" in
        --opencode)
            WITH_OPENCODE=true
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        --php-version)
            PHP_VERSION="$2"
            shift 2
            ;;
        *)
            break
            ;;
    esac
done

FIXTURE_SRC="$FIXTURES_DIR/php/$FIXTURE"
FIXTURE_DST="/tmp/continuous-refactoring-tests/$FIXTURE"

# Setup fixture — copies only project/ (expected stays outside container)
setup_fixture() {
    log_info "Setting up fixture: $FIXTURE"
    rm -rf "$FIXTURE_DST"
    mkdir -p "$(dirname "$FIXTURE_DST")"
    if [[ -d "$FIXTURE_SRC/project" ]]; then
        cp -r "$FIXTURE_SRC/project/." "$FIXTURE_DST/"
        # Ensure .github and dotfiles are copied (cp -r project/. may miss hidden on some shells, so explicit)
        if [[ -d "$FIXTURE_SRC/project/.github" ]]; then
            mkdir -p "$FIXTURE_DST/.github"
            cp -r "$FIXTURE_SRC/project/.github/." "$FIXTURE_DST/.github/" 2>/dev/null || true
        fi
        for dot in "$FIXTURE_SRC/project"/.php-cs-fixer.php "$FIXTURE_SRC/project"/.php-cs-fixer.dist.php; do
            [[ -f "$dot" ]] && cp "$dot" "$FIXTURE_DST/" 2>/dev/null || true
        done
    else
        cp -r "$FIXTURE_SRC" "$FIXTURE_DST"
    fi
    cd "$FIXTURE_DST"
    git init -q
    git -c user.name="Test Runner" -c user.email="test@ci.local" add -A
    git -c user.name="Test Runner" -c user.email="test@ci.local" commit -q -m "Initial fixture state"
    log_info "Fixture ready at: $FIXTURE_DST (project only, expected not mounted)"
}

# Resolve the opencode binary invocation (empty string if unavailable) —
# shared by every local-only advisory check (roadmap --opencode, tier4,
# judge, lift). Echoes the command prefix on stdout; logs and returns
# nonzero if no binary is found so callers can skip cleanly.
resolve_opencode_bin() {
    if command -v opencode >/dev/null 2>&1; then
        echo "opencode"
        return 0
    elif command -v npx >/dev/null 2>&1 && npx --yes opencode --help >/dev/null 2>&1; then
        echo "npx --yes opencode"
        return 0
    fi
    log_info "opencode binary not found (install via npm i -g opencode) — skipping advisory opencode run"
    return 1
}

# Run one opencode prompt, isolated (only skills/ from this repo, via a
# .agents/skills symlink — no global ~/.config/opencode/skills), as a
# subprocess against $1's working directory. $2 is the prompt, $3 the log
# file to write, $4 an optional timeout (default 60s), $5 an optional
# "false" to skip the skills symlink entirely (used by `lift`'s
# without-skill baseline — everything else about the invocation stays
# identical, so that run is a fair comparison against the with-skill one).
# Never fails the caller — advisory only; check the log file / grep it
# yourself.
run_opencode_advisory() {
    local workdir="$1" prompt="$2" out_file="$3" timeout_s="${4:-60}" mount_skills="${5:-true}"
    local opencode_bin
    opencode_bin="$(resolve_opencode_bin)" || return 1
    if [[ "$mount_skills" == true ]]; then
        mkdir -p "$workdir/.agents"
        ln -sfn "$REPO_DIR/skills" "$workdir/.agents/skills"
    fi
    log_info "Running: $opencode_bin run (subprocess, timeout ${timeout_s}s) in $workdir$([[ "$mount_skills" == true ]] || echo ", no skills mounted")"
    if timeout "$timeout_s" bash -c "cd \"$workdir\" && $opencode_bin run \"$prompt\" 2>&1" > "$out_file" 2>&1; then
        [[ "$mount_skills" == true ]] && rm -rf "$workdir/.agents"
        return 0
    else
        log_info "Opencode run failed or timed out — see $out_file (advisory, not failing test)"
        [[ "$mount_skills" == true ]] && rm -rf "$workdir/.agents"
        return 1
    fi
}

# Run opencode in Docker
run_opencode() {
    local command="$1"
    log_info "Running opencode: $command"

    docker run --rm \
        -v "$FIXTURE_DST:/workspace" \
        -w /workspace \
        -v "$REPO_DIR/skills:/workspace/.agents/skills:ro" \
        "php:$PHP_VERSION-cli" \
        bash -c "cd /workspace && opencode run $command"
}

# Tier 2: Artifact Contract Tests
run_tier2() {
    log_info "=== Tier 2: Artifact Contract Tests ==="

    # Check fixture structure (what exists in the source fixture) — supports both old (src at root) and new (project/src)
    local project_src="$FIXTURE_SRC/project"
    if [[ -d "$project_src" ]]; then
        assert_dir_exists "$project_src/src"
        # composer may be at project/composer.json (new) or legacy composer/composer.json
        if [[ -f "$project_src/composer.json" ]]; then
            assert_file_exists "$project_src/composer.json"
        elif [[ -d "$FIXTURE_SRC/composer" ]]; then
            assert_dir_exists "$FIXTURE_SRC/composer"
        fi
    else
        assert_dir_exists "$FIXTURE_SRC/src"
        assert_dir_exists "$FIXTURE_SRC/composer"
    fi
    assert_dir_exists "$FIXTURE_SRC/expected"

    # Check expected issues exist
    local expected_issues="$FIXTURE_SRC/expected/issues"
    assert_file_exists "$expected_issues/001-shallow-user-service.md"
    assert_file_exists "$expected_issues/002-sql-injection-user-repository.md"
    assert_file_exists "$expected_issues/003-hardcoded-secret-user-repository.md"
    assert_file_exists "$expected_issues/004-unused-unused-reporting-service.md"
    assert_file_exists "$expected_issues/005-style-violations-bootstrap.md"

    # Check issue labels and fields
    for issue in "$expected_issues"/*.md; do
        assert_issue_has_label "$issue" "refactor:candidate"
        assert_issue_has_fields "$issue" "## Where" "## Problem" "## Signal"
    done

    # Check expected docs
    assert_file_exists "$FIXTURE_SRC/expected/docs/refactoring/config.md"
    assert_config_format "$FIXTURE_SRC/expected/docs/refactoring/config.md"
}

# Tier 3: Ground Truth Tests
run_tier3() {
    log_info "=== Tier 3: Ground Truth Tests ==="

    local expected_dir="$FIXTURE_SRC/expected"
    local planted_count
    planted_count=$(find "$expected_dir/issues" -name "*.md" 2>/dev/null | wc -l)

    log_info "Planted candidates: $planted_count"

    # Count found candidates (issues filed by scan)
    local found_count
    found_count=$(find "$FIXTURE_DST/.scratch" -name "*.md" -path "*issues*" 2>/dev/null | wc -l)

    # Calculate precision/recall
    if [[ "$planted_count" -gt 0 ]]; then
        local recall
        recall=$(echo "scale=2; $found_count / $planted_count" | bc)
        log_info "Recall: $recall ($found_count/$planted_count)"
    fi

    # Regression gate (ticket 27, Tier 5): compare against the committed
    # baseline *before* overwriting it. In CI this stays a same-number
    # comparison (found is always 0 — no LLM runs in CI, see
    # fixtures/README.md), but the mechanism is real: it fails the moment a
    # baseline committed from a local `--opencode`/`agent-loop` run regresses.
    local baseline_dir="$FIXTURES_DIR/baselines"
    assert_baseline_not_regressed "$baseline_dir/$FIXTURE.json" "$found_count" "$planted_count"

    # Save baseline
    mkdir -p "$baseline_dir"
    cat > "$baseline_dir/$FIXTURE.json" <<EOF
{
    "tier": 3,
    "fixture": "$FIXTURE",
    "planted": $planted_count,
    "found": $found_count,
    "date": "$(date -I)"
}
EOF
    log_info "Baseline saved to $baseline_dir/$FIXTURE.json"
}

# Roadmap: Dry-run — detect tools, decision chain, next 10 MRs (no mutation)
run_roadmap() {
    log_info "=== Roadmap (dry-run, no MR) — fixture: $FIXTURE ==="

    local expected_roadmap="$FIXTURE_SRC/expected/roadmap.json"
    if [[ ! -f "$expected_roadmap" ]]; then
        log_fail "Missing expected roadmap: $expected_roadmap"
        return 1
    fi

    # Generate roadmap via deterministic parser (no opencode, no mutation) — source of truth is skills/refactor-scan/references/php-tooling-tree.md
    # Deterministic parser is intentionally used for reproducibility (no LLM flakiness); an opencode run
    # `opencode run /refactor-scan` + `/refactor-prioritize` would yield the same required/recommended chain
    # (see skills/continuous-refactoring: required edge gates, recommended only outlook). Optional: run_opencode "roadmap" can be added.
    local generated="/tmp/roadmap-$FIXTURE.json"
    if ! python3 "$REPO_DIR/skills/refactor-scan/references/tooling_tree.py" "$FIXTURE_DST" --steps 10 > "$generated" 2>/dev/null; then
        log_fail "Failed to generate roadmap for $FIXTURE_DST"
        return 1
    fi

    # Pretty print for human observation
    log_info "Detected tools (fulfilled):"
    python3 -c "
import json
d=json.load(open('$generated'))
for n,v in d['detected'].items():
    if v['fulfilled']:
        print(f\"  - {n}: {v['reason']}\")
" 2>&1 | while IFS= read -r line; do log_info \"$line\"; done

    log_info "Next 10 MRs (decision chain):"
    python3 -c "
import json
d=json.load(open('$generated'))
for r in d['roadmap']:
    print(f\"  {r['n']:2}. {r['node']:30} [{r['type']}] — {r.get('reason','')}\")
" 2>&1 | while IFS= read -r line; do log_info \"$line\"; done

    # Ensure no MR/branch was created (dry-run)
    assert_no_mr_created "$FIXTURE_DST"
    assert_file_not_exists "$FIXTURE_DST/docs/refactoring/merge-requests.md"
    assert_file_not_exists "$FIXTURE_DST/.scratch"

    # Compare detected & roadmap against expected
    assert_detected_contains "$generated" "$expected_roadmap"
    assert_roadmap_matches "$generated" "$expected_roadmap"

    # Also verify expected file itself is well-formed
    assert_file_exists "$expected_roadmap"

    # Optional: run opencode isolated as subprocess (advisory, no hard fail)
    if [[ "$WITH_OPENCODE" == true ]]; then
        log_info "=== Opencode isolated (advisory, no other skills) ==="
        local opencode_out="/tmp/opencode-$FIXTURE.log"
        if run_opencode_advisory "$FIXTURE_DST" "List the next 10 MRs for this repo without creating branches/MRs. Use skills/refactor-scan/references/php-tooling-tree.md." "$opencode_out"; then
            log_info "Opencode output (first 80 lines):"
            head -n 80 "$opencode_out" 2>&1 | while IFS= read -r line; do log_info "  $line"; done
            # Advisory comparison: check if opencode mentions expected first node
            local first_expected
            first_expected=$(python3 -c "import json; print(json.load(open('$expected_roadmap'))['roadmap'][0]['node'])" 2>/dev/null || echo "")
            if [[ -n "$first_expected" ]] && grep -qi "$first_expected" "$opencode_out" 2>/dev/null; then
                log_pass "Opencode (advisory) mentions expected first node: $first_expected"
            else
                log_info "Opencode (advisory) does not mention expected first node $first_expected — check $opencode_out for details (non-blocking)"
            fi
        else
            [[ -f "$opencode_out" ]] && head -n 40 "$opencode_out" 2>&1 | while IFS= read -r line; do log_info "  $line"; done
        fi
    fi
}

# Agent loop: prepare an isolated sandbox + prompt for a full-pass,
# subagent-observed run. Formalizes the manual dry-run methodology from
# ADR-0010's "## Validation" section against this repo's own fixtures.
#
# Unlike roadmap's --opencode (a Docker subprocess this script can launch
# itself), a Claude Code Agent-tool subagent cannot be started from Bash —
# this function only prepares the sandbox and a ready-to-use prompt; running
# the subagent against that prompt is a separate, manual step (see
# fixtures/README.md).
run_agent_loop() {
    log_info "=== Agent loop (full pass, subagent-observed) — fixture: $FIXTURE ==="

    # Local issue-tracker override so the skills never touch a real forge —
    # same convention this repo uses for itself (docs/agents/issue-tracker.md).
    mkdir -p "$FIXTURE_DST/docs/agents" "$FIXTURE_DST/.scratch/refactor/issues"
    cat > "$FIXTURE_DST/docs/agents/issue-tracker.md" <<'EOF'
# Issue tracker: Local Markdown

Issues live as markdown files in `.scratch/refactor/issues/`, one file per
issue, numbered from `01`. A `Status:` / `Labels:` line near the top records
triage state (see `docs/agents/triage-labels.md`). Comments append under a
`## Comments` heading at the bottom of the file.

## When a skill says "file an issue"

Create a new file at `.scratch/refactor/issues/<NN>-<slug>.md`.

## When a skill says "check the external tracker"

Read the files under `.scratch/refactor/issues/` directly — there is no
external forge in this sandbox.
EOF
    cat > "$FIXTURE_DST/docs/agents/triage-labels.md" <<'EOF'
# Triage Labels

| Label in mattpocock/skills | Label in our tracker | Meaning                                  |
| --------------------------- | --------------------- | ----------------------------------------- |
| `needs-triage`               | `needs-triage`          | Maintainer needs to evaluate this issue   |
| `needs-info`                 | `needs-info`            | Waiting on reporter for more information  |
| `ready-for-agent`            | `ready-for-agent`       | Fully specified, ready for an AFK agent   |
| `ready-for-human`            | `ready-for-human`       | Requires human implementation             |
| `wontfix`                    | `wontfix`               | Will not be actioned                      |
| —                            | `done`                  | Work complete, delivered, no longer open  |
EOF
    if [[ ! -f "$FIXTURE_DST/CONTEXT.md" ]]; then
        printf '# %s\n\n_Domain vocabulary for this sandbox project — the loop appends terms here as they crystallise._\n' "$FIXTURE" > "$FIXTURE_DST/CONTEXT.md"
    fi
    mkdir -p "$FIXTURE_DST/docs/adr"
    git -C "$FIXTURE_DST" add -A
    git -C "$FIXTURE_DST" -c user.name="Test Runner" -c user.email="test@ci.local" commit -q -m "Seed local issue-tracker override for agent-loop sandbox"

    local prompt_file="/tmp/continuous-refactoring-tests/agent-loop-prompt-$FIXTURE.md"
    local friction_file="$FIXTURE_DST/../agent-loop-friction-$FIXTURE.md"
    cat > "$prompt_file" <<EOF
You are dry-run testing the continuous-refactoring skill suite against an
isolated sandbox — a copy of the fixture "$FIXTURE", not a real project.

Sandbox (your working directory for everything below): $FIXTURE_DST
It is a real, freshly-initialized git repo with no remote — commit, branch,
and open merge requests (as local branches; there is no forge to push to)
freely inside it. Never read or write anything outside this path.

Read this file and follow it literally, as if you were the suite consuming
its own instructions for the first time:
    $REPO_DIR/skills/continuous-refactoring/SKILL.md
It will point you to the lifecycle skills it orchestrates (refactor-scan,
refactor-prioritize, refactor-design, refactor-implement, refactor-learn)
under $REPO_DIR/skills/ — read each one when the orchestrator step tells you
to run it.

Run exactly one pass. Where the skill text is ambiguous or you have to guess
at a behavior it doesn't spell out, do not silently improvise past it and do
not edit the skill files — note the ambiguity instead. When the pass ends
(or stops itself per its own completion criterion), append your findings to:
    $friction_file
covering: what you did each step, any ambiguity or guessed behavior, and
whether each step's completion criterion was actually met.
EOF

    log_info "Sandbox ready: $FIXTURE_DST (git initialized, no remote, tracker/CONTEXT.md/docs/adr seeded)"
    log_info "Prompt written: $prompt_file"
    log_info "Next step (manual — this script cannot spawn a Claude Code subagent itself):"
    log_info "  spawn an Agent-tool subagent with the contents of $prompt_file, let it run, then inspect"
    log_info "  $FIXTURE_DST (git log, docs/refactoring/, .scratch/refactor/issues/) and $friction_file"
    log_info "Optional post-run structural check once the pass has run:"
    log_info "  assert_config_format \"$FIXTURE_DST/docs/refactoring/config.md\"  (source fixtures/harness/lib/assertions.sh first)"
}

# Tier 4: Trigger/discoverability tests (ticket 27) — explicit + implicit
# invocation per skill, and the two negative controls that are prose-level
# judgment calls a skill makes rather than something the deterministic
# parser decides: "no git" (refactor-scan's own step-1 precondition —
# whether the check the parser's detect_nodes() already reports accurately
# is actually *followed* is a model-behavior question, not a parser one)
# and "not a PHP project" (ADR-0008 keeps language recognition an informal
# heuristic on purpose, "premature before a second language specialization
# exists"). The third negative control, "scan on clean repo reports clean",
# is fully deterministic and lives in `scripts/test_trigger_controls.py`
# (CI-gated) — the check here only confirms the skill's own wording matches
# that deterministic result.
#
# Local-only advisory, same posture as `roadmap --opencode` and
# `agent-loop`: this repo's CI has no model credentials, so nothing here
# ever gates CI — see fixtures/README.md's "Tier 4" section. Run fixture
# php-clean (its already-fully-resolved tree doubles as the clean-repo
# scenario); the no-git and non-PHP scenarios are synthesized fresh here,
# independent of $FIXTURE.
run_tier4() {
    log_info "=== Tier 4: Trigger & Discoverability (advisory) — fixture: $FIXTURE ==="

    if [[ "$WITH_OPENCODE" != true ]]; then
        log_info "Deterministic negative control (clean repo) already covered by: python3 -m unittest scripts.test_trigger_controls"
        log_info "The behavioral checks below need --opencode (local-only, non-CI, needs the opencode binary):"
        log_info "  $(basename "$0") tier4 $FIXTURE --opencode --verbose"
        return 0
    fi
    if ! resolve_opencode_bin >/dev/null; then
        return 0
    fi

    # --- Negative control 1: no git ---
    local no_git_dir="/tmp/continuous-refactoring-tests/tier4-no-git"
    rm -rf "$no_git_dir" && mkdir -p "$no_git_dir"
    cp -r "$FIXTURE_DST/." "$no_git_dir/" 2>/dev/null || true
    rm -rf "$no_git_dir/.git"
    local out="/tmp/tier4-no-git.log"
    if run_opencode_advisory "$no_git_dir" "Run one pass of the continuous refactoring loop (skills/continuous-refactoring/SKILL.md)." "$out" 60; then
        if grep -qi "no git\|not a git\|git repository" "$out"; then
            log_pass "No-git negative control: output names the missing git repository"
        else
            log_info "No-git negative control: expected wording not found in $out (advisory, non-blocking)"
        fi
        if [[ -f "$no_git_dir/docs/refactoring/config.md" ]]; then
            log_fail "No-git negative control: docs/refactoring/config.md was written despite no git repository"
        else
            log_pass "No-git negative control: no loop state written"
        fi
    fi

    # --- Negative control 2: non-PHP project ---
    local non_php_dir="/tmp/continuous-refactoring-tests/tier4-non-php"
    rm -rf "$non_php_dir" && mkdir -p "$non_php_dir/src"
    printf '{"name": "not-a-php-project", "version": "1.0.0"}\n' > "$non_php_dir/package.json"
    printf "console.log('hi');\n" > "$non_php_dir/src/index.js"
    (cd "$non_php_dir" && git init -q && git -c user.name="Test Runner" -c user.email="test@ci.local" add -A && git -c user.name="Test Runner" -c user.email="test@ci.local" commit -q -m "Initial fixture state")
    out="/tmp/tier4-non-php.log"
    if run_opencode_advisory "$non_php_dir" "Run /refactor-scan against this repo." "$out" 60; then
        if grep -qi "composer\|php-cs-fixer\|phpstan" "$out"; then
            log_info "Non-PHP negative control: output mentions PHP tooling — check $out (advisory, non-blocking)"
        else
            log_pass "Non-PHP negative control: no PHP-specific tooling proposed"
        fi
    fi

    # --- Negative control 3: clean repo (deterministic half already green
    # via scripts/test_trigger_controls.py against this same fixture) ---
    out="/tmp/tier4-clean.log"
    if run_opencode_advisory "$FIXTURE_DST" "Run /refactor-scan against this repo." "$out" 60; then
        if grep -qi "structural-scan\|nothing to propose\|nothing new" "$out"; then
            log_pass "Clean-repo negative control: report matches the deterministic result (only structural-scan open)"
        else
            log_info "Clean-repo negative control: expected wording not found in $out (advisory, non-blocking)"
        fi
    fi

    # --- Discoverability: explicit + implicit invocation per skill ---
    log_info "--- Discoverability: explicit + implicit invocation per skill ---"
    _tier4_discoverability "refactor-scan" "propose the next tooling-tree candidate for this repo" "tooling-tree"
    _tier4_discoverability "refactor-prioritize" "rank the current refactoring proposals and recommend the next one" "recommend"
    _tier4_discoverability "refactor-design" "turn the chosen refactor candidate into a concrete plan and file it as an issue" "issue"
    _tier4_discoverability "refactor-implement" "implement the designed refactor plan test-first and open the merge request" "merge request"
    _tier4_discoverability "refactor-learn" "record what this refactoring pass learned in the ledger" "ledger"
    _tier4_orchestrator_explicit_only
}

# One skill, both invocation modes — advisory grep against a marker word the
# skill's own SKILL.md process section uses. Not run for continuous-refactoring
# (see _tier4_orchestrator_explicit_only): it ships disable-model-invocation:
# true, so its implicit case has the opposite expected outcome.
_tier4_discoverability() {
    local skill="$1" implicit_prompt="$2" marker="$3"
    local explicit_out="/tmp/tier4-$skill-explicit.log"
    local implicit_out="/tmp/tier4-$skill-implicit.log"
    if run_opencode_advisory "$FIXTURE_DST" "/$skill" "$explicit_out" 45; then
        if grep -qi "$marker" "$explicit_out"; then
            log_pass "$skill: explicit invocation (/$skill) triggers — mentions '$marker'"
        else
            log_info "$skill: explicit invocation ran but didn't mention '$marker' — check $explicit_out (non-blocking)"
        fi
    fi
    if run_opencode_advisory "$FIXTURE_DST" "$implicit_prompt" "$implicit_out" 45; then
        if grep -qi "$marker" "$implicit_out"; then
            log_pass "$skill: implicit invocation (natural language) triggers — mentions '$marker'"
        else
            log_info "$skill: implicit invocation ran but didn't mention '$marker' — check $implicit_out (non-blocking)"
        fi
    fi
}

# continuous-refactoring ships disable-model-invocation: true in its own
# SKILL.md frontmatter — natural language alone must NOT trigger the full
# 6-step pass; only the explicit /continuous-refactoring form should.
_tier4_orchestrator_explicit_only() {
    local implicit_out="/tmp/tier4-continuous-refactoring-implicit.log"
    if run_opencode_advisory "$FIXTURE_DST" "Keep this codebase under continuous refactoring." "$implicit_out" 45; then
        if grep -qi "refactor-scan\|refactor-implement\|merge request" "$implicit_out"; then
            log_info "continuous-refactoring: implicit prompt appears to have run the full pass — check $implicit_out (disable-model-invocation should block this; advisory, non-blocking)"
        else
            log_pass "continuous-refactoring: implicit natural-language prompt did not trigger the full pass (disable-model-invocation: true honored)"
        fi
    fi
    local explicit_out="/tmp/tier4-continuous-refactoring-explicit.log"
    if run_opencode_advisory "$FIXTURE_DST" "/continuous-refactoring" "$explicit_out" 90; then
        log_pass "continuous-refactoring: explicit invocation ran — see $explicit_out"
    fi
}

# Tier 5 — LLM-judge rubric grading (ticket 27). Local-only, advisory,
# non-CI (needs model credentials this repo's CI does not have). Grades one
# fixture's loop-state artifacts against fixtures/harness/rubric.md.
run_judge() {
    log_info "=== LLM-judge rubric grading — fixture: $FIXTURE ==="
    if ! resolve_opencode_bin >/dev/null; then
        return 0
    fi
    local rubric="$FIXTURES_DIR/harness/rubric.md"
    if [[ ! -f "$rubric" ]]; then
        log_fail "Missing rubric: $rubric"
        return 1
    fi
    local out="/tmp/judge-$FIXTURE.log"
    local prompt="Grade this repo's refactoring-loop artifacts (docs/refactoring/, any filed issues, git log) against the rubric at fixtures/harness/rubric.md. Give one score 1-5 per rubric dimension plus a one-line justification each."
    if run_opencode_advisory "$FIXTURE_DST" "$prompt" "$out" 90; then
        log_info "Judge output:"
        while IFS= read -r line; do log_info "  $line"; done < "$out"
        log_pass "Judge run complete — read $out for the per-dimension scores (advisory, not a hard gate)"
    fi
}

# Tier 5 — with-skill vs. without-skill lift measurement (ticket 27).
# Local-only, advisory, non-CI. Runs the same prompt twice against the same
# fixture state: once with skills/ mounted (run_opencode_advisory's isolated
# .agents/skills symlink), once with no skill guidance at all — prints both
# transcript paths so a human (or `judge`'s rubric) can compare them.
run_lift() {
    log_info "=== Lift measurement (with-skill vs. without-skill) — fixture: $FIXTURE ==="
    if ! resolve_opencode_bin >/dev/null; then
        return 0
    fi

    local prompt="Improve this codebase's refactoring hygiene: find the single most valuable next step and take it."
    local with_out="/tmp/lift-$FIXTURE-with-skill.log"
    local without_out="/tmp/lift-$FIXTURE-without-skill.log"

    if run_opencode_advisory "$FIXTURE_DST" "$prompt" "$with_out" 90; then
        log_pass "With-skill run complete — $with_out"
    fi

    log_info "Running without-skill baseline (no .agents/skills symlink)..."
    if run_opencode_advisory "$FIXTURE_DST" "$prompt" "$without_out" 90 false; then
        log_pass "Without-skill run complete — $without_out"
    fi

    log_info "Compare $with_out vs $without_out by hand, or grade both against the rubric with:"
    log_info "  $(basename "$0") judge $FIXTURE --opencode"
}

# Main
main() {
    reset_counters
    setup_fixture

    case "$TIER" in
        tier2)
            run_tier2
            ;;
        tier3)
            run_tier3
            ;;
        tier4)
            run_tier4
            ;;
        roadmap)
            run_roadmap
            ;;
        agent-loop)
            run_agent_loop
            ;;
        judge)
            run_judge
            ;;
        lift)
            run_lift
            ;;
        *)
            log_fail "Unknown tier: $TIER"
            usage
            ;;
    esac

    print_summary
}

main
