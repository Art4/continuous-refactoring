#!/usr/bin/env bash
# fixtures/harness/test-tier2.sh
# Tier 2: Artifact Contract Tests

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"
FIXTURES_DIR="$REPO_DIR/fixtures"
LIB_DIR="$SCRIPT_DIR/lib"

source "$LIB_DIR/assertions.sh"

FIXTURE="php-project-with-candidates"
FIXTURE_SRC="$FIXTURES_DIR/php/$FIXTURE"
FIXTURE_DST="/tmp/continuous-refactoring-tests/$FIXTURE"

# Setup
setup_fixture() {
    log_info "Setting up fixture: $FIXTURE"
    rm -rf "$FIXTURE_DST"
    mkdir -p "$(dirname "$FIXTURE_DST")"
    cp -r "$FIXTURE_SRC" "$FIXTURE_DST"
    cd "$FIXTURE_DST"
    git init -q
    git -c user.name="Test Runner" -c user.email="test@ci.local" add -A
    git -c user.name="Test Runner" -c user.email="test@ci.local" commit -q -m "Initial fixture state"
}

# Run artifact contract tests
run_tier2_tests() {
    log_info "=== Tier 2: Artifact Contract Tests ==="
    log_info "Fixture: $FIXTURE"

    # Test 1: Check fixture structure
    log_info "Test 1: Fixture structure"
    assert_dir_exists "$FIXTURE_SRC/src"
    assert_dir_exists "$FIXTURE_SRC/composer"
    assert_dir_exists "$FIXTURE_SRC/expected"

    # Test 2: Check source files exist
    log_info "Test 2: Source files"
    assert_file_exists "$FIXTURE_SRC/src/UserService.php"
    assert_file_exists "$FIXTURE_SRC/src/UserRepository.php"
    assert_file_exists "$FIXTURE_SRC/src/UnusedReportingService.php"
    assert_file_exists "$FIXTURE_SRC/src/bootstrap.php"
    assert_file_exists "$FIXTURE_SRC/src/User.php"

    # Test 3: Check composer.json
    log_info "Test 3: Composer configuration"
    assert_file_exists "$FIXTURE_SRC/composer/composer.json"
    assert_file_contains "$FIXTURE_SRC/composer/composer.json" "php"

    # Test 4: Check expected candidate issues
    log_info "Test 4: Expected candidate issues"
    local expected_issues="$FIXTURE_SRC/expected/issues"
    assert_dir_exists "$expected_issues"
    assert_file_exists "$expected_issues/001-shallow-user-service.md"
    assert_file_exists "$expected_issues/002-sql-injection-user-repository.md"
    assert_file_exists "$expected_issues/003-hardcoded-secret-user-repository.md"
    assert_file_exists "$expected_issues/004-unused-unused-reporting-service.md"
    assert_file_exists "$expected_issues/005-style-violations-bootstrap.md"

    # Test 5: Check issue labels
    log_info "Test 5: Issue labels"
    for issue in "$expected_issues"/*.md; do
        assert_issue_has_label "$issue" "refactor:candidate"
    done

    # Test 6: Check issue required fields
    log_info "Test 6: Issue required fields"
    for issue in "$expected_issues"/*.md; do
        assert_issue_has_fields "$issue" "## Where" "## Problem" "## Signal"
    done

    # Test 7: Check expected docs structure
    log_info "Test 7: Expected docs structure"
    assert_dir_exists "$FIXTURE_SRC/expected/docs"
    assert_dir_exists "$FIXTURE_SRC/expected/docs/refactoring"

    # Test 8: Check expected config
    log_info "Test 8: Expected config"
    assert_file_exists "$FIXTURE_SRC/expected/docs/refactoring/config.md"
    assert_config_format "$FIXTURE_SRC/expected/docs/refactoring/config.md"

    # Test 9: Check expected MR file
    log_info "Test 9: Expected MR file"
    assert_file_exists "$FIXTURE_SRC/expected/docs/refactoring/merge-requests.md"
}

# Main
main() {
    reset_counters
    setup_fixture
    run_tier2_tests
    print_summary
}

main
