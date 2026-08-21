#!/usr/bin/env bash
# fixtures/harness/run.sh
# Main harness script: loads fixture, runs opencode, checks artifacts

set -euo pipefail

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
    tier2   Run artifact contract tests
    tier3   Run ground-truth precision/recall tests

Options:
    --php-version VERSION   PHP version for Docker (default: 8.3)
    --verbose               Enable verbose output

Examples:
    $(basename "$0") tier2 php-project-with-candidates
    $(basename "$0") tier3 php-project-with-candidates --php-version 8.2
EOF
    exit 1
}

# Parse options
PHP_VERSION="${PHP_VERSION:-8.3}"
VERBOSE=false

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

FIXTURE_SRC="$FIXTURES_DIR/php/$FIXTURE"
FIXTURE_DST="/tmp/continuous-refactoring-tests/$FIXTURE"

# Setup fixture
setup_fixture() {
    log_info "Setting up fixture: $FIXTURE"
    rm -rf "$FIXTURE_DST"
    mkdir -p "$(dirname "$FIXTURE_DST")"
    cp -r "$FIXTURE_SRC" "$FIXTURE_DST"
    cd "$FIXTURE_DST"
    git init -q
    git -c user.name="Test Runner" -c user.email="test@ci.local" add -A
    git -c user.name="Test Runner" -c user.email="test@ci.local" commit -q -m "Initial fixture state"
    log_info "Fixture ready at: $FIXTURE_DST"
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

    # Check issue structure
    assert_dir_exists "$FIXTURE_DST/.scratch" || true
    assert_dir_exists "$FIXTURE_DST/docs/refactoring" || true

    # Check config format
    if [[ -f "$FIXTURE_DST/docs/refactoring/config.md" ]]; then
        assert_config_format "$FIXTURE_DST/docs/refactoring/config.md"
    fi

    # Check MR chain
    if [[ -f "$FIXTURE_DST/docs/refactoring/merge-requests.md" ]]; then
        assert_mr_chain_length "$FIXTURE_DST/docs/refactoring/merge-requests.md" 2
    fi

    # Check for candidate issues
    local issue_count
    issue_count=$(find "$FIXTURE_DST" -name "*.md" -path "*issues*" | wc -l)
    if [[ "$issue_count" -gt 0 ]]; then
        log_pass "Found $issue_count issue(s)"
    else
        log_fail "No issues found"
    fi
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
        *)
            log_fail "Unknown tier: $TIER"
            usage
            ;;
    esac

    print_summary
}

main
