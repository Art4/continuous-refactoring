#!/usr/bin/env bash
# fixtures/harness/lib/assertions.sh
# Shared assertion functions for the test harness

# NOTE: Do NOT use set -euo pipefail here.
# Assertions return 1 on failure but should not abort the script.
# The caller decides whether to use set -e.

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Counters
ASSERTIONS_PASSED=0
ASSERTIONS_FAILED=0

# Log functions
log_pass() {
    echo -e "${GREEN}✓ PASS${NC}: $*"
    ((ASSERTIONS_PASSED++))
}

log_fail() {
    echo -e "${RED}✗ FAIL${NC}: $*"
    ((ASSERTIONS_FAILED++))
}

log_info() {
    echo -e "${YELLOW}ℹ INFO${NC}: $*"
}

# Assertion: Check if file exists
assert_file_exists() {
    local file="$1"
    if [[ -f "$file" ]]; then
        log_pass "File exists: $file"
        return 0
    else
        log_fail "File not found: $file"
        return 1
    fi
}

# Assertion: Check if directory exists
assert_dir_exists() {
    local dir="$1"
    if [[ -d "$dir" ]]; then
        log_pass "Directory exists: $dir"
        return 0
    else
        log_fail "Directory not found: $dir"
        return 1
    fi
}

# Assertion: Check if file contains string
assert_file_contains() {
    local file="$1"
    local pattern="$2"
    if grep -q "$pattern" "$file" 2>/dev/null; then
        log_pass "File contains pattern: $pattern in $file"
        return 0
    else
        log_fail "File does not contain pattern: $pattern in $file"
        return 1
    fi
}

# Assertion: Check if issue file has required fields
assert_issue_has_fields() {
    local issue_file="$1"
    shift
    local fields=("$@")

    for field in "${fields[@]}"; do
        if ! grep -q "$field" "$issue_file" 2>/dev/null; then
            log_fail "Issue missing field: $field in $issue_file"
            return 1
        fi
    done

    log_pass "Issue has all required fields: ${fields[*]}"
    return 0
}

# Assertion: Check if issue has label
assert_issue_has_label() {
    local issue_file="$1"
    local label="$2"
    if grep -q "Labels:.*$label" "$issue_file" 2>/dev/null; then
        log_pass "Issue has label: $label"
        return 0
    else
        log_fail "Issue missing label: $label"
        return 1
    fi
}

# Assertion: Check config file format
assert_config_format() {
    local config_file="$1"
    # No Cadence field by design (ADR-0008): the loop never triggers itself,
    # so nothing stores a schedule. Last run is the orchestrator-written
    # anchor field instead.
    if grep -q "Last run:" "$config_file" 2>/dev/null; then
        log_pass "Config has Last run field"
        return 0
    else
        log_fail "Config missing Last run field"
        return 1
    fi
}

# Assertion: Check merge request chain length
assert_mr_chain_length() {
    local merge_requests_file="$1"
    local max_length="$2"

    local count
    count=$(grep -c "^### " "$merge_requests_file" 2>/dev/null || echo "0")

    if [[ "$count" -le "$max_length" ]]; then
        log_pass "MR chain length ($count) <= $max_length"
        return 0
    else
        log_fail "MR chain length ($count) > $max_length"
        return 1
    fi
}

# Assertion: No MR/branch was created (dry-run)
assert_no_mr_created() {
    local repo="$1"
    local before_branches after_branches before_commits after_commits
    # Count commits
    local commits
    commits=$(git -C "$repo" rev-list --count HEAD 2>/dev/null || echo "0")
    if [[ "$commits" -eq 1 ]]; then
        log_pass "No MR created — still 1 commit in $repo"
        return 0
    else
        log_fail "Expected 1 commit (initial), found $commits in $repo — MR was created"
        return 1
    fi
}

# Assertion: file should not exist (e.g., no merge-requests.md created)
assert_file_not_exists() {
    local file="$1"
    if [[ ! -e "$file" ]]; then
        log_pass "File correctly absent: $file"
        return 0
    else
        log_fail "File should not exist (dry-run): $file"
        return 1
    fi
}

# Assertion: roadmap order matches expected
assert_roadmap_matches() {
    local generated="$1"
    local expected="$2"
    # Compare node lists via python
    if python3 -c "
import json, sys
g=json.load(open('$generated'))
e=json.load(open('$expected'))
gn=[r['node'] for r in g.get('roadmap', g if isinstance(g, list) else [])]
en=[r['node'] for r in e.get('roadmap', [])]
if gn==en:
    sys.exit(0)
else:
    print(f'generated: {gn}', file=sys.stderr)
    print(f'expected:  {en}', file=sys.stderr)
    sys.exit(1)
" 2>&1; then
        log_pass "Roadmap order matches $expected"
        return 0
    else
        log_fail "Roadmap order mismatch vs $expected"
        python3 -c "
import json
g=json.load(open('$generated'))
e=json.load(open('$expected'))
print('--- generated nodes ---')
for r in g.get('roadmap', []): print(r['n'], r['node'], '-', r.get('reason','')[:60])
print('--- expected nodes ---')
for r in e.get('roadmap', []): print(r['n'], r['node'])
" 2>&1 | while read -r line; do log_info \"$line\"; done
        return 1
    fi
}

# Assertion: detected nodes contain expected fulfilled set (subset)
assert_detected_contains() {
    local generated="$1"
    local expected="$2"
    if python3 -c "
import json, sys
g=json.load(open('$generated'))
e=json.load(open('$expected'))
# e detected is {node: {fulfilled: bool}}
for node, exp in e.get('detected', {}).items():
    g_val = g.get('detected', {}).get(node, {}).get('fulfilled')
    if g_val != exp.get('fulfilled'):
        print(f\"detect mismatch {node}: expected {exp.get('fulfilled')} got {g_val}\", file=sys.stderr)
        sys.exit(1)
sys.exit(0)
" 2>&1; then
        log_pass "Detected nodes match $expected"
        return 0
    else
        log_fail "Detected nodes mismatch vs $expected"
        return 1
    fi
}

# Assertion: repo has new commits past the initial fixture commit(s)
# (advisory sanity check after an agent-loop run — not a hard content match,
# since the subagent's output isn't deterministic)
assert_git_has_new_commits() {
    local repo="$1"
    local baseline="$2" # commit count right after setup_fixture
    local commits
    commits=$(git -C "$repo" rev-list --count HEAD 2>/dev/null || echo "0")
    if [[ "$commits" -gt "$baseline" ]]; then
        log_pass "New commits in $repo since baseline ($baseline -> $commits)"
        return 0
    else
        log_fail "No new commits in $repo since baseline ($baseline)"
        return 1
    fi
}

# Assertion: current tier-3 recall has not regressed against the committed
# baseline (ticket 27, Tier 5 — "wire harness into CI with regression
# baselines"). Compares found/planted ratios; a missing baseline file is not
# a regression (first run for this fixture) — it passes and lets the caller
# save the new baseline.
assert_baseline_not_regressed() {
    local baseline_file="$1"
    local current_found="$2"
    local current_planted="$3"

    if [[ ! -f "$baseline_file" ]]; then
        log_pass "No prior baseline at $baseline_file — nothing to regress against"
        return 0
    fi

    if python3 -c "
import json, sys
b = json.load(open('$baseline_file'))
b_found, b_planted = b.get('found', 0), b.get('planted', 0)
c_found, c_planted = $current_found, $current_planted
b_recall = (b_found / b_planted) if b_planted else 0
c_recall = (c_found / c_planted) if c_planted else 0
sys.exit(0 if c_recall >= b_recall else 1)
" 2>&1; then
        log_pass "Recall did not regress vs. baseline ($baseline_file)"
        return 0
    else
        log_fail "Recall regressed vs. baseline ($baseline_file): now $current_found/$current_planted, was better before"
        return 1
    fi
}

# Print summary
print_summary() {
    echo ""
    echo "========================================"
    echo "Assertion Summary"
    echo "========================================"
    echo -e "${GREEN}Passed: $ASSERTIONS_PASSED${NC}"
    echo -e "${RED}Failed: $ASSERTIONS_FAILED${NC}"
    echo "========================================"

    if [[ "$ASSERTIONS_FAILED" -gt 0 ]]; then
        return 1
    else
        return 0
    fi
}

# Reset counters
reset_counters() {
    ASSERTIONS_PASSED=0
    ASSERTIONS_FAILED=0
}
