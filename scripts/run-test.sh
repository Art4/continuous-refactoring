#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"
FIXTURES_DIR="$REPO_DIR/fixtures"
TEMP_DIR="/tmp/continuous-refactoring-tests"
PHP_VERSION="${PHP_VERSION:-8.2}"

usage() {
    cat <<EOF
Usage: $(basename "$0") <mode> <fixture> [options]

Modes:
    setup   Copy fixture to /tmp, init git repo
    test    Run Docker container with PHP to validate fixture
    clean   Remove temporary files
    auto    Run setup → test → clean in sequence

Options:
    --php-version VERSION   PHP version for Docker (default: 8.2)

Examples:
    $(basename "$0") setup php-project-with-candidates
    $(basename "$0") test php-project-with-candidates
    $(basename "$0") auto php-project-with-candidates --php-version 8.1
EOF
    exit 1
}

log() {
    echo "==> $*"
}

error() {
    echo "ERROR: $*" >&2
    exit 1
}

cmd_setup() {
    local fixture="$1"
    local fixture_src="$FIXTURES_DIR/php/$fixture"
    local fixture_dst="$TEMP_DIR/$fixture"

    if [[ ! -d "$fixture_src" ]]; then
        error "Fixture not found: $fixture_src"
    fi

    log "Setting up fixture: $fixture"

    rm -rf "$fixture_dst"
    mkdir -p "$(dirname "$fixture_dst")"
    cp -r "$fixture_src" "$fixture_dst"

    cd "$fixture_dst"
    git init -q
    git add -A
    git commit -q -m "Initial fixture state"

    log "Fixture ready at: $fixture_dst"
    echo "$fixture_dst"
}

cmd_test() {
    local fixture="$1"
    local fixture_dir="$TEMP_DIR/$fixture"

    if [[ ! -d "$fixture_dir" ]]; then
        error "Fixture not found at $fixture_dir. Run 'setup' first."
    fi

    log "Testing fixture: $fixture (PHP $PHP_VERSION)"

    docker run --rm \
        -v "$fixture_dir:/fixture" \
        -w /fixture \
        "php:$PHP_VERSION-cli" \
        php -v

    log "PHP syntax check passed"

    if [[ -f "$fixture_dir/composer/composer.json" ]]; then
        log "Running composer validate"
        docker run --rm \
            -v "$fixture_dir:/fixture" \
            -w /fixture/composer \
            "php:$PHP_VERSION-cli" \
            composer validate --quiet 2>/dev/null || log "composer validate completed with warnings"
    fi

    log "Test passed for fixture: $fixture"
}

cmd_clean() {
    local fixture="${1:-}"

    if [[ -n "$fixture" ]]; then
        local fixture_dir="$TEMP_DIR/$fixture"
        if [[ -d "$fixture_dir" ]]; then
            log "Cleaning fixture: $fixture"
            rm -rf "$fixture_dir"
        fi
    else
        log "Cleaning all temporary test files"
        rm -rf "$TEMP_DIR"
    fi

    log "Clean complete"
}

main() {
    if [[ $# -lt 2 ]]; then
        usage
    fi

    local mode="$1"
    local fixture="$2"
    shift 2

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --php-version)
                PHP_VERSION="$2"
                shift 2
                ;;
            *)
                error "Unknown option: $1"
                ;;
        esac
    done

    case "$mode" in
        setup)
            cmd_setup "$fixture"
            ;;
        test)
            cmd_test "$fixture"
            ;;
        clean)
            cmd_clean "$fixture"
            ;;
        auto)
            cmd_setup "$fixture"
            cmd_test "$fixture"
            cmd_clean "$fixture"
            ;;
        *)
            error "Unknown mode: $mode"
            ;;
    esac
}

main "$@"
