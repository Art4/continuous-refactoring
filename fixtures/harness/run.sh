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
    tier3       Run ground-truth precision/recall tests
    roadmap     Dry-run: detect tools, show decision chain and next 10 MRs (no MR created)
    agent-loop  Prepare an isolated sandbox + prompt for a full-pass, Agent-tool-subagent-observed run (local-only, see fixtures/README.md)

Options:
    --php-version VERSION   PHP version for Docker (default: 8.3)
    --verbose               Enable verbose output
    --opencode              Also run opencode isolated as subprocess (advisory, needs opencode binary)

Examples:
    $(basename "$0") tier2 php-project-with-candidates
    $(basename "$0") tier3 php-project-with-candidates --php-version 8.2
    $(basename "$0") roadmap php-empty
    $(basename "$0") roadmap php-p0-empty --verbose
    $(basename "$0") roadmap php-empty --opencode --verbose   # deterministic + opencode comparison
    $(basename "$0") agent-loop php-partial                   # prepare sandbox + prompt, then spawn a subagent yourself
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

    # Save baseline
    local baseline_dir="$FIXTURES_DIR/baselines"
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
        local opencode_bin=""
        if command -v opencode >/dev/null 2>&1; then
            opencode_bin="opencode"
        elif command -v npx >/dev/null 2>&1 && npx --yes opencode --help >/dev/null 2>&1; then
            opencode_bin="npx --yes opencode"
        else
            log_info "opencode binary not found (install via npm i -g opencode) — skipping advisory opencode run"
            return 0
        fi
        # Isolated: only skills from this repo, no global ~/.config/opencode/skills
        # Sub-process: working dir = fixture, skills mounted via --skills flag if supported, else via .agents/skills symlink
        local opencode_out="/tmp/opencode-$FIXTURE.log"
        log_info "Running: $opencode_bin run --skills $REPO_DIR/skills (subprocess, timeout 60s) in $FIXTURE_DST"
        # Ensure .agents/skills symlink for opencode discovery (isolated)
        mkdir -p "$FIXTURE_DST/.agents"
        ln -sfn "$REPO_DIR/skills" "$FIXTURE_DST/.agents/skills"
        if timeout 60 bash -c "cd \"$FIXTURE_DST\" && $opencode_bin run \"List the next 10 MRs for this repo without creating branches/MRs. Use skills/refactor-scan/references/php-tooling-tree.md.\" 2>&1" > "$opencode_out" 2>&1; then
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
            log_info "Opencode run failed or timed out — see $opencode_out (advisory, not failing test)"
            head -n 40 "$opencode_out" 2>&1 | while IFS= read -r line; do log_info "  $line"; done
        fi
        # Cleanup symlink (keep fixture clean)
        rm -rf "$FIXTURE_DST/.agents"
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
        roadmap)
            run_roadmap
            ;;
        agent-loop)
            run_agent_loop
            ;;
        *)
            log_fail "Unknown tier: $TIER"
            usage
            ;;
    esac

    print_summary
}

main
