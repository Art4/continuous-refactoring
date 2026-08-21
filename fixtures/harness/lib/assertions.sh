#!/usr/bin/env bash
# fixtures/harness/lib/assertions.sh
# Shared assertion functions for the test harness

set -euo pipefail

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
    if grep -q "Cadence:" "$config_file" 2>/dev/null; then
        log_pass "Config has Cadence field"
        return 0
    else
        log_fail "Config missing Cadence field"
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
