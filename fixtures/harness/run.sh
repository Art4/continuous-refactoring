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
    agent-loop  Prepare an isolated sandbox + prompt for a full-pass, Agent-tool-subagent-observed run (local-only, see fixtures/README.md)
    judge       LLM-judge rubric grading against fixtures/harness/rubric.md (local-only, advisory — ticket 27)
    lift        With-skill vs without-skill lift measurement (local-only, advisory — ticket 27)
    decision-gate-bypass   Decision-gate ready-for-agent bypass regression (fixture: php-decision-gate-bypass; local-only, advisory — ADR-0053)
    safety-net-track       Safety Net Track behavior regressions (fixtures: php-safety-net-*; local-only, advisory)
    guardrails-track       Guardrails Track behavior regressions (fixtures: php-guardrails-*, php-track-open-priority-guardrails; local-only, advisory)
    housekeeping-track     Housekeeping Track behavior regressions (fixtures: php-housekeeping-*; local-only, advisory)
    scheduler              Orchestrator Track-selection regressions (fixtures: php-scheduler-*; local-only, advisory — ADR-0055, ticket 04)

Options:
    --php-version VERSION   PHP version for Docker (default: 8.3)
    --verbose               Enable verbose output
    --opencode              Also run opencode isolated as subprocess (advisory, needs opencode binary)
                            Model is pinned via \$OPENCODE_MODEL (default: opencode/muse-spark-1.2-contributor-free)
                            Per-call timeout via \$OPENCODE_TIMEOUT (default: 60s — raise for a slower model)

Examples:
    $(basename "$0") tier2 php-project-with-candidates
    $(basename "$0") tier3 php-project-with-candidates --php-version 8.2
    $(basename "$0") tier4 php-clean --opencode --verbose
    $(basename "$0") agent-loop php-partial                   # prepare sandbox + prompt, then spawn a subagent yourself
    $(basename "$0") judge php-project-with-candidates --opencode
    $(basename "$0") lift php-partial --opencode
    $(basename "$0") decision-gate-bypass php-decision-gate-bypass --opencode
    $(basename "$0") safety-net-track php-safety-net-purpose-recognition --opencode
    $(basename "$0") guardrails-track php-guardrails-purpose-recognition --opencode
    $(basename "$0") housekeeping-track php-housekeeping-hand-adopted-guardrails --opencode
    $(basename "$0") housekeeping-track php-housekeeping-old-schema --opencode
    $(basename "$0") scheduler php-scheduler-staleness-selection --opencode
    $(basename "$0") scheduler php-scheduler-investigation-fallback --opencode
    $(basename "$0") scheduler php-scheduler-housekeeping-competes --opencode
    $(basename "$0") scheduler php-scheduler-bootstrap-investigation --opencode
    $(basename "$0") scheduler php-scheduler-bootstrap-guardrails --opencode
    $(basename "$0") scheduler php-scheduler-bootstrap-housekeeping --opencode
    $(basename "$0") scheduler php-scheduler-bootstrap-resumes --opencode
    $(basename "$0") scheduler php-scheduler-safety-net-blockade --opencode
    $(basename "$0") scheduler php-scheduler-guardrails-stalled --opencode
    $(basename "$0") scheduler php-scheduler-housekeeping-preempts-guardrails --opencode
    $(basename "$0") scheduler php-scheduler-bootstrap-guardrails-open --opencode
EOF
    exit 1
}

# Parse options
PHP_VERSION="${PHP_VERSION:-8.3}"
VERBOSE=false
WITH_OPENCODE=false
# Pinned explicitly — `opencode run` with no -m falls back to whatever
# local/ambient default model is configured (observed: a local ollama model
# that just hangs to timeout with zero output). fixtures/README.md's manual
# instructions already assume this exact model; override via env var if a
# different one is set up locally.
OPENCODE_MODEL="${OPENCODE_MODEL:-opencode/muse-spark-1.2-contributor-free}"
# Per-call default for run_opencode_advisory's internal `timeout` — callers
# can still pass their own timeout_s explicitly (e.g. tier4's shorter
# per-skill checks); this only changes the *default* a caller gets when it
# doesn't. 60s is tight for a model that actually reads several fixture
# files before answering (observed: some models need 2-4x that on a busier
# fixture) — override per run without editing the script.
OPENCODE_TIMEOUT="${OPENCODE_TIMEOUT:-60}"

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

# Parse trailing options (e.g., --opencode after fixture: tier4 php-clean --opencode)
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
# shared by every local-only advisory check (tier4, judge, lift). Echoes the
# command prefix on stdout; logs and returns
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
    local workdir="$1" prompt="$2" out_file="$3" timeout_s="${4:-$OPENCODE_TIMEOUT}" mount_skills="${5:-true}"
    local opencode_bin
    opencode_bin="$(resolve_opencode_bin)" || return 1
    if [[ "$mount_skills" == true ]]; then
        mkdir -p "$workdir/.agents"
        ln -sfn "$REPO_DIR/skills" "$workdir/.agents/skills"
    fi
    log_info "Running: $opencode_bin run -m $OPENCODE_MODEL (subprocess, timeout ${timeout_s}s) in $workdir$([[ "$mount_skills" == true ]] || echo ", no skills mounted")"
    # $prompt is passed as a positional parameter ($2 below), not
    # interpolated into the script text — a prompt containing shell
    # metacharacters (backticks, $, quotes — e.g. `judge`'s rubric text)
    # would otherwise be re-parsed as shell syntax by this inner bash -c.
    if timeout "$timeout_s" bash -c 'cd "$1" && '"$opencode_bin"' run -m '"$OPENCODE_MODEL"' "$2"' _ "$workdir" "$prompt" > "$out_file" 2>&1; then
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
    assert_file_exists "$FIXTURE_SRC/expected/docs/refactoring/bookkeeping.md"
    assert_config_format "$FIXTURE_SRC/expected/docs/refactoring/bookkeeping.md"
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

# Agent loop: prepare an isolated sandbox + prompt for a full-pass,
# subagent-observed run. Formalizes the manual dry-run methodology from
# ADR-0010's "## Validation" section against this repo's own fixtures.
#
# Unlike the `--opencode` advisory runs (subprocesses this script can launch
# itself), a Claude Code Agent-tool subagent cannot be started from Bash —
# this function only prepares the sandbox and a ready-to-use prompt; running
# the subagent against that prompt is a separate, manual step (see
# fixtures/README.md).
run_agent_loop() {
    log_info "=== Agent loop (full pass, subagent-observed) — fixture: $FIXTURE ==="

    # docs/agents/issue-tracker.md is deliberately NOT pre-seeded here — the
    # loop-config interview (skills/continuous-refactoring/references/
    # loop-config-interview.md) is what's supposed to create it, and this
    # sandbox has no `origin` remote, so Explore finds nothing and the
    # interview's own recommendation should converge on Local Markdown on
    # its own. Pre-seeding it would skip the one thing this dry-run mode
    # exists to actually exercise.
    mkdir -p "$FIXTURE_DST/docs/agents"
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
    git -C "$FIXTURE_DST" -c user.name="Test Runner" -c user.email="test@ci.local" commit -q -m "Seed triage-labels/CONTEXT.md for agent-loop sandbox"

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
not edit the skill files — note the ambiguity instead. If the loop-config
interview runs and there is nobody here to answer it, follow its own
"## If no human is present to ask" section (skills/continuous-refactoring/
references/loop-config-interview.md) rather than guessing past it. When the
pass ends (or stops itself per its own completion criterion), append your
findings to:
    $friction_file
covering: what you did each step, any ambiguity or guessed behavior, and
whether each step's completion criterion was actually met.
EOF

    log_info "Sandbox ready: $FIXTURE_DST (git initialized, no remote, triage-labels/CONTEXT.md/docs/adr seeded)"
    log_info "Prompt written: $prompt_file"
    log_info "Next step (manual — this script cannot spawn a Claude Code subagent itself):"
    log_info "  spawn an Agent-tool subagent with the contents of $prompt_file, let it run, then inspect"
    log_info "  $FIXTURE_DST (git log, docs/refactoring/, .scratch/refactor/issues/) and $friction_file"
    log_info "Optional post-run structural check once the pass has run:"
    log_info "  assert_config_format \"$FIXTURE_DST/docs/refactoring/bookkeeping.md\"  (source fixtures/harness/lib/assertions.sh first)"
}

# Tier 4: Trigger/discoverability tests (ticket 27) — explicit + implicit
# invocation per skill, and the two negative controls that are prose-level
# judgment calls a skill makes rather than something the deterministic
# script decides: "no git" (refactor-scan's own step-1 precondition —
# whether that precondition is actually *followed* is a model-behavior
# question, not a script one)
# and "not a PHP project" (ADR-0008 keeps language recognition an informal
# heuristic on purpose, "premature before a second language specialization
# exists"). The third negative control, "scan on clean repo reports clean",
# is fully deterministic and lives in `scripts/test_trigger_controls.py`
# (CI-gated) — the check here only confirms the skill's own wording matches
# that deterministic result.
#
# Local-only advisory, same posture as `agent-loop`: this repo's CI has no
# model credentials, so nothing here ever gates CI — see fixtures/README.md's
# "Tier 4" section. Run fixture
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
        if [[ -f "$no_git_dir/docs/refactoring/bookkeeping.md" ]]; then
            log_fail "No-git negative control: docs/refactoring/bookkeeping.md was written despite no git repository"
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
    # Embed the rubric's content directly rather than pointing the model at
    # `fixtures/harness/rubric.md` — that path only resolves from this
    # repo's root, not $FIXTURE_DST (the isolated /tmp copy the subprocess
    # actually runs in, which has no fixtures/ at all). Read on this
    # process's own host filesystem (no permission wall here) and pass the
    # content straight through — safe now that run_opencode_advisory passes
    # $prompt as a positional parameter instead of interpolating it.
    local rubric_text
    rubric_text="$(cat "$rubric")"
    local prompt="Grade this repo's refactoring-loop artifacts (docs/refactoring/, any filed issues, git log) against the rubric below. Give one score 1-5 per dimension plus a one-line justification each.

---
$rubric_text
---"
    if run_opencode_advisory "$FIXTURE_DST" "$prompt" "$out" "$OPENCODE_TIMEOUT"; then
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

    if run_opencode_advisory "$FIXTURE_DST" "$prompt" "$with_out" "$OPENCODE_TIMEOUT"; then
        log_pass "With-skill run complete — $with_out"
    fi

    log_info "Running without-skill baseline (no .agents/skills symlink)..."
    if run_opencode_advisory "$FIXTURE_DST" "$prompt" "$without_out" "$OPENCODE_TIMEOUT" false; then
        log_pass "Without-skill run complete — $without_out"
    fi

    log_info "Compare $with_out vs $without_out by hand, or grade both against the rubric with:"
    log_info "  $(basename "$0") judge $FIXTURE --opencode"
}

# Tier 5 — decision-gate ready-for-agent bypass regression (ADR-0053).
# Local-only, advisory, non-CI. Reproduces the bug: an externally-labeled
# candidate issue pre-tagged ready-for-agent (fixture:
# php-decision-gate-bypass) should have that label actively corrected once
# refactor-design finds a decision meeting the ADR bar, and refactor-scan's
# resume check should then hold the candidate back instead of routing it to
# refactor-implement. The LLM run itself isn't deterministic, but the
# post-run label check is a real, non-advisory grep against the fixture's
# own committed expectation, not a judgment call.
#
# Uses opencode directly with --auto (unlike run_opencode_advisory, which
# doesn't pass it) — this scenario's own broader, unattended-mode prompt was
# observed to make the model explore outside its working directory, which
# --auto is what avoids the resulting permission wall (see
# fixtures/README.md's troubleshooting section).
run_decision_gate_bypass() {
    log_info "=== Decision-gate ready-for-agent bypass regression — fixture: $FIXTURE ==="
    local opencode_bin
    opencode_bin="$(resolve_opencode_bin)" || return 0

    local issue="$FIXTURE_DST/.scratch/refactor/issues/01-unify-retry-logic.md"
    if [[ ! -f "$issue" ]]; then
        log_fail "Missing seeded issue: $issue (fixture: $FIXTURE)"
        return 1
    fi

    log_info "Before: $(grep -m 1 '^\*\*Labels:\*\*' "$issue")"

    mkdir -p "$FIXTURE_DST/.agents"
    ln -sfn "$REPO_DIR/skills" "$FIXTURE_DST/.agents/skills"

    local design_out="/tmp/decision-gate-bypass-$FIXTURE-design.log"
    local design_prompt="Run /refactor-design against issue .scratch/refactor/issues/01-unify-retry-logic.md in this repo. Follow skills/refactor-design/SKILL.md literally, step by step, including its decision gate (skills/refactor-design/references/decision-gate.md). This is an unattended pass — no human is present to answer questions live, follow the skill's own unattended-mode instructions. Report what you wrote to the issue file and which labels you changed, if any."
    if ! timeout "$OPENCODE_TIMEOUT" bash -c 'cd "$1" && '"$opencode_bin"' run -m '"$OPENCODE_MODEL"' --auto "$2"' _ "$FIXTURE_DST" "$design_prompt" > "$design_out" 2>&1; then
        log_info "Opencode design run failed or timed out — see $design_out (advisory, not failing test)"
        rm -rf "$FIXTURE_DST/.agents"
        return 0
    fi

    local labels_line
    labels_line="$(grep -m 1 '^\*\*Labels:\*\*' "$issue" 2>/dev/null || echo '')"
    log_info "After:  $labels_line"
    if [[ "$labels_line" == *"needs-info"* && "$labels_line" != *"ready-for-agent"* ]]; then
        log_pass "refactor-design actively cleared the pre-existing ready-for-agent and added needs-info"
    else
        log_fail "refactor-design did not correct the label as expected (ADR-0053) — see $design_out"
    fi

    local scan_out="/tmp/decision-gate-bypass-$FIXTURE-scan.log"
    local scan_prompt="Run /refactor-scan against this repo. Follow skills/refactor-scan/SKILL.md literally, step by step, starting with its Pending candidates resume check. Report explicitly: did it route the pending candidate to refactor-implement, or hold it back? Why?"
    if timeout "$OPENCODE_TIMEOUT" bash -c 'cd "$1" && '"$opencode_bin"' run -m '"$OPENCODE_MODEL"' --auto "$2"' _ "$FIXTURE_DST" "$scan_prompt" > "$scan_out" 2>&1; then
        if grep -qiE "held back|not routed|does not route|not resumable" "$scan_out"; then
            log_pass "refactor-scan (advisory) reports holding the candidate back — see $scan_out"
        else
            log_info "refactor-scan output doesn't clearly confirm hold-back — check $scan_out by hand (advisory, non-blocking)"
        fi
    else
        log_info "Opencode scan run failed or timed out — see $scan_out (advisory, not failing test)"
    fi

    rm -rf "$FIXTURE_DST/.agents"
}

# Shared helper for the Track fixtures whose prompt asks the model to
# self-report the backlog it would record as one final line,
# `OPEN: slug, slug, ...`: pass when that line names every given slug in
# exactly the given order (a slug is matched as a whole token, so
# phpstan-level-1 never matches inside phpstan-level-10). Advisory
# otherwise — never fails on a missing/unclear line, only on a wrong order.
_check_open_order() {
    local out="$1"; shift
    local expected="$*"
    local pattern="^OPEN:" s
    for s in "$@"; do
        pattern+=".*[^a-z0-9-]${s}"'([^a-z0-9-]|$)'
    done
    if grep -qiE "$pattern" "$out" 2>/dev/null; then
        log_pass "Scan output reports OPEN in the script's order ($expected) — see $out"
    elif grep -qiE "^OPEN:" "$out" 2>/dev/null; then
        log_fail "Scan output's OPEN line doesn't list the backlog in the script's order ($expected) — see $out"
    else
        log_info "Scan output doesn't clearly self-report an OPEN line — check $out by hand (advisory, non-blocking)"
    fi
}

# Tier 5 — Safety Net Track behavior regressions (ticket 01,
# skills/refactor-scan/references/safety-net-track.md /
# skills/refactor-learn/references/safety-net-write.md). Local-only,
# advisory, non-CI — the deliberate replacement for `tooling_tree.py`
# ground-truth on a Safety Net Track node: the whole point under test is
# that the deterministic parser's own dependency-name match isn't
# authoritative here any more (fixtures/README.md's "safety-net-track"
# section). Each `php-safety-net-*` fixture exercises one distinct
# checklist item; dispatches by fixture name to the matching check below.
# Real, deterministic greps against the fixture's own post-run files where
# possible (same discipline `decision-gate-bypass` already uses) — LLM
# transcript wording only where no file-level signal exists.
run_safety_net_track() {
    log_info "=== Safety Net Track behavior — fixture: $FIXTURE ==="
    local opencode_bin
    opencode_bin="$(resolve_opencode_bin)" || return 0

    mkdir -p "$FIXTURE_DST/.agents"
    ln -sfn "$REPO_DIR/skills" "$FIXTURE_DST/.agents/skills"

    case "$FIXTURE" in
        php-safety-net-purpose-recognition)
            _safety_net_scan_prompt "Run /refactor-scan against this repo. Follow skills/refactor-scan/SKILL.md literally, including skills/refactor-scan/references/safety-net-track.md for step 4. Report, as your final line: FULFILLED (php-cs-fixer's Purpose is already served, not proposed) or PROPOSED (php-cs-fixer should be proposed as a fresh candidate)."
            local out="/tmp/safety-net-track-$FIXTURE-scan.log"
            if grep -qi "pint" "$out" 2>/dev/null; then
                log_pass "Scan output mentions Laravel Pint — advisory sign the Purpose judgement ran (see $out)"
            else
                log_info "Scan output doesn't mention Pint — check $out by hand (advisory, non-blocking)"
            fi
            if grep -qi "^PROPOSED" "$out" 2>/dev/null; then
                log_fail "Scan output self-reports PROPOSED — php-cs-fixer wrongly proposed despite Pint — see $out"
            elif grep -qi "^FULFILLED" "$out" 2>/dev/null; then
                log_pass "Scan output self-reports FULFILLED — see $out"
            else
                log_info "Scan output doesn't clearly self-report FULFILLED/PROPOSED — check $out by hand (advisory, non-blocking)"
            fi
            ;;
        php-safety-net-open-blocks-rescan)
            _safety_net_scan_prompt "Run /refactor-scan against this repo. Follow skills/refactor-scan/SKILL.md literally, including its step 2 resume check and skills/refactor-scan/references/safety-net-track.md. Report explicitly, as your final line: RESUMED (worked the existing php-cs-fixer #5 Open entry only) or RESCANNED (walked the tree fresh and proposed other nodes too)."
            local out="/tmp/safety-net-track-$FIXTURE-scan.log"
            if grep -qi "RESCANNED" "$out" 2>/dev/null; then
                log_fail "Scan output self-reports RESCANNED — Open may have been rescanned instead of resumed — see $out"
            elif grep -qi "RESUMED" "$out" 2>/dev/null; then
                log_pass "Scan output self-reports RESUMED — see $out"
            else
                log_info "Scan output doesn't clearly self-report RESUMED/RESCANNED — check $out by hand (advisory, non-blocking)"
            fi
            ;;
        php-safety-net-first-run)
            _safety_net_scan_prompt "Run one full pass: /refactor-scan, then /refactor-learn's closing call, against this repo. Follow skills/refactor-scan/SKILL.md and skills/refactor-learn/SKILL.md literally, including skills/refactor-scan/references/safety-net-track.md and skills/refactor-learn/references/safety-net-write.md. This target's Safety Net Track nodes are already fully resolved — report explicitly what (if anything) got written to docs/refactoring/bookkeeping.md."
            local bookkeeping="$FIXTURE_DST/docs/refactoring/bookkeeping.md"
            if grep -q "## Safety Net" "$bookkeeping" 2>/dev/null && grep -q "Last scan:" "$bookkeeping" 2>/dev/null; then
                log_pass "bookkeeping.md now carries a ## Safety Net section with Last scan written"
            else
                log_fail "bookkeeping.md missing ## Safety Net / Last scan after the pass — see $bookkeeping"
            fi
            ;;
        php-safety-net-rejection-symmetry)
            _safety_net_scan_prompt "Run /refactor-learn's early call against this repo, given this finding: the candidate MR for php-cs-fixer (issue .scratch/refactor/issues/05-php-cs-fixer.md) was closed without merge; the issue's own closing comment already gives a maintainer's structural reason. Follow skills/refactor-learn/SKILL.md literally, including skills/refactor-learn/references/safety-net-write.md. Report what you wrote."
            local bookkeeping="$FIXTURE_DST/docs/refactoring/bookkeeping.md"
            local oos="$FIXTURE_DST/docs/refactoring/out-of-scope/php-cs-fixer.md"
            if [[ -f "$oos" ]]; then
                log_pass "out-of-scope/php-cs-fixer.md written"
            else
                log_fail "out-of-scope/php-cs-fixer.md missing after the run — see $bookkeeping and $FIXTURE_DST/docs/refactoring/out-of-scope/"
            fi
            if grep -qE "Out-of-scope:" "$bookkeeping" 2>/dev/null && grep -qE "^- php-cs-fixer" <(sed -n '/Out-of-scope:/,/^$/p' "$bookkeeping" 2>/dev/null); then
                log_pass "## Safety Net's Out-of-scope list names php-cs-fixer"
            else
                log_info "## Safety Net's Out-of-scope list doesn't clearly name php-cs-fixer — check $bookkeeping by hand (advisory, non-blocking)"
            fi
            if grep -qE "^- php-cs-fixer" <(sed -n '/Open:/,/^$/p' "$bookkeeping" 2>/dev/null); then
                log_fail "## Safety Net's Open list still names php-cs-fixer — should have been removed"
            else
                log_pass "## Safety Net's Open list no longer names php-cs-fixer"
            fi
            ;;
        php-safety-net-old-schema)
            _safety_net_scan_prompt "Run /refactor-scan against this repo. Follow skills/refactor-scan/SKILL.md literally, including skills/refactor-scan/references/safety-net-track.md. This repo's docs/refactoring/bookkeeping.md is still in the pre-existing shape (Fulfilled nodes, global Pending candidates, no Safety Net section). Report explicitly: did the pass run normally, and did it error on or need to migrate the old fields?"
            local bookkeeping="$FIXTURE_DST/docs/refactoring/bookkeeping.md"
            if grep -q "loop-config" "$bookkeeping" 2>/dev/null; then
                log_pass "Pre-existing Fulfilled nodes content (loop-config) still present, untouched"
            else
                log_fail "Pre-existing Fulfilled nodes content is gone — see $bookkeeping"
            fi
            local out="/tmp/safety-net-track-$FIXTURE-scan.log"
            if grep -qiE "error|cannot proceed|unrecognized field" "$out" 2>/dev/null; then
                log_info "Scan output mentions an error/unrecognized-field phrase — check $out by hand (advisory, non-blocking)"
            else
                log_pass "Scan output doesn't report an error on the old-schema fields — see $out"
            fi
            ;;
        php-safety-net-rejection-cascade)
            _safety_net_scan_prompt "Run /refactor-learn's early call against this repo, given this finding: the candidate MR for phpstan-level-3 (issue .scratch/refactor/issues/12-phpstan-level-3.md) was closed without merge; the issue's own closing comment already gives a maintainer's structural reason. Follow skills/refactor-learn/SKILL.md literally, including skills/refactor-learn/references/safety-net-write.md. Report what you wrote."
            local bookkeeping="$FIXTURE_DST/docs/refactoring/bookkeeping.md"
            local oosdir="$FIXTURE_DST/docs/refactoring/out-of-scope"
            if [[ -f "$oosdir/phpstan-level-3.md" ]]; then
                log_pass "out-of-scope/phpstan-level-3.md written"
            else
                log_fail "out-of-scope/phpstan-level-3.md missing after the run — see $bookkeeping and $oosdir/"
            fi
            if [[ -f "$oosdir/phpstan-level-4.md" || -f "$oosdir/phpstan-level-5.md" ]]; then
                log_fail "An out-of-scope file was written for a downstream closure (phpstan-level-4/5) — closures are derived, never recorded — see $oosdir/"
            else
                log_pass "No out-of-scope file written for the closed descendants phpstan-level-4/5"
            fi
            if grep -qE "^- phpstan-level-(3|4|5)" <(sed -n '/Open:/,/^$/p' "$bookkeeping" 2>/dev/null); then
                log_fail "## Safety Net's Open list still names phpstan-level-3/4/5 — the rejected node and its closed descendants should all have left it"
            else
                log_pass "## Safety Net's Open list no longer names phpstan-level-3/4/5"
            fi
            if grep -qE "^- phpstan-level-[45]" <(sed -n '/Out-of-scope:/,/^$/p' "$bookkeeping" 2>/dev/null); then
                log_fail "## Safety Net's Out-of-scope list carries a pointer for phpstan-level-4/5 — only the rejected node gets one"
            else
                log_pass "## Safety Net's Out-of-scope list carries no pointer for the closed descendants"
            fi
            # Reversal half (scan-only, no writes): reverse the rejection by
            # hand, then ask what the next Safety Net scan would record.
            rm -f "$oosdir/phpstan-level-3.md"
            sed -i '/^- phpstan-level-3/d' "$bookkeeping" 2>/dev/null
            _safety_net_scan_prompt "The maintainer reversed the phpstan-level-3 rejection (its out-of-scope file and pointer are removed). Run /refactor-scan with the Safety Net Track named explicitly against this repo, following skills/refactor-scan/SKILL.md and skills/refactor-scan/references/safety-net-track.md. Do not write any file. Report, as your final line, the Open list the Track scan would record as: OPEN: <slugs, comma separated, in order>."
            _check_open_order "/tmp/safety-net-track-$FIXTURE-scan.log" phpstan-level-3 phpstan-level-4 phpstan-level-5
            ;;
        php-safety-net-old-meaning-open)
            _safety_net_scan_prompt "Run the Safety Net Track — it is named explicitly for this pass (manual Track override) — against this repo: /refactor-scan with that Track. Follow skills/refactor-scan/SKILL.md and skills/refactor-scan/references/safety-net-track.md literally. This repo's docs/refactoring/bookkeeping.md still has the old-meaning Open (only phpstan-level-1 (#7)) plus Fulfilled nodes/Focus areas residue. Report explicitly, as your final line: RESUMED (walked the existing Open entry phpstan-level-1 only) or RESCANNED (ran a fresh Track scan and recorded a new Open)."
            local bookkeeping="$FIXTURE_DST/docs/refactoring/bookkeeping.md"
            local out="/tmp/safety-net-track-$FIXTURE-scan.log"
            if grep -q "Fulfilled nodes" "$bookkeeping" 2>/dev/null && grep -q "loop-config" "$bookkeeping" 2>/dev/null; then
                log_pass "Pre-existing Fulfilled nodes residue still present, untouched"
            else
                log_fail "Pre-existing Fulfilled nodes residue is gone — see $bookkeeping"
            fi
            if grep -qE "^- phpstan-level-[2-5]" "$bookkeeping" 2>/dev/null; then
                log_fail "bookkeeping.md's Open now names phpstan-level-2..5 — the old-meaning Open was rewritten by a rescan instead of walked — see $bookkeeping"
            else
                log_pass "bookkeeping.md's Open was not rewritten to the complete backlog"
            fi
            if grep -qiE "^RESCANNED" "$out" 2>/dev/null; then
                log_fail "Scan output self-reports RESCANNED — naming the Track must not force a scan while Open has entries — see $out"
            elif grep -qiE "^RESUMED" "$out" 2>/dev/null; then
                log_pass "Scan output self-reports RESUMED — see $out"
            else
                log_info "Scan output doesn't clearly self-report RESUMED/RESCANNED — check $out by hand (advisory, non-blocking)"
            fi
            if grep -qiE "error|cannot proceed|unrecognized field" "$out" 2>/dev/null; then
                log_info "Scan output mentions an error/unrecognized-field phrase — check $out by hand (advisory, non-blocking)"
            else
                log_pass "Scan output doesn't report an error on the old-meaning Open — see $out"
            fi
            ;;
        *)
            log_fail "No safety-net-track check wired for fixture: $FIXTURE"
            ;;
    esac

    rm -rf "$FIXTURE_DST/.agents"
}

# Shared helper for run_safety_net_track's cases above: run one opencode
# prompt with --auto (this scenario's broader, unattended-mode prompts were
# observed elsewhere in this file to need it — decision-gate-bypass's own
# troubleshooting note) against $FIXTURE_DST, logging to
# /tmp/safety-net-track-$FIXTURE-scan.log. Advisory only — never fails the
# caller.
_safety_net_scan_prompt() {
    local prompt="$1"
    local out="/tmp/safety-net-track-$FIXTURE-scan.log"
    if ! timeout "$OPENCODE_TIMEOUT" bash -c 'cd "$1" && '"$opencode_bin"' run -m '"$OPENCODE_MODEL"' --auto "$2"' _ "$FIXTURE_DST" "$prompt" > "$out" 2>&1; then
        log_info "Opencode run failed or timed out — see $out (advisory, not failing test)"
    fi
}

# Tier 5 — Guardrails Track behavior regressions (ticket 02,
# skills/refactor-scan/references/guardrails-track.md /
# skills/refactor-learn/references/guardrails-write.md). Local-only,
# advisory, non-CI — the Guardrails Track's own counterpart to
# run_safety_net_track above, reusing the exact same mechanism against a
# second node set (fixtures/README.md's "guardrails-track" section). Each
# `php-guardrails-*` fixture exercises one distinct checklist item;
# dispatches by fixture name to the matching check below. Real, deterministic
# greps against the fixture's own post-run files where possible, an advisory
# transcript grep otherwise — same discipline `run_safety_net_track` already
# uses.
run_guardrails_track() {
    log_info "=== Guardrails Track behavior — fixture: $FIXTURE ==="
    local opencode_bin
    opencode_bin="$(resolve_opencode_bin)" || return 0

    mkdir -p "$FIXTURE_DST/.agents"
    ln -sfn "$REPO_DIR/skills" "$FIXTURE_DST/.agents/skills"

    case "$FIXTURE" in
        php-guardrails-purpose-recognition)
            _guardrails_scan_prompt "Run /refactor-scan against this repo. Follow skills/refactor-scan/SKILL.md literally, including skills/refactor-scan/references/guardrails-track.md for step 4. Report, as your final line: FULFILLED (composer-audit's Purpose is already served, not proposed) or PROPOSED (composer-audit should be proposed as a fresh candidate)."
            local out="/tmp/guardrails-track-$FIXTURE-scan.log"
            if grep -qi "security-check" "$out" 2>/dev/null; then
                log_pass "Scan output mentions the security-check script — advisory sign the Purpose judgement ran (see $out)"
            else
                log_info "Scan output doesn't mention the security-check script — check $out by hand (advisory, non-blocking)"
            fi
            if grep -qiE "^PROPOSED" "$out" 2>/dev/null; then
                log_fail "Scan output self-reports PROPOSED — composer-audit wrongly proposed despite the indirect CI gate — see $out"
            elif grep -qiE "^FULFILLED" "$out" 2>/dev/null; then
                log_pass "Scan output self-reports FULFILLED — see $out"
            else
                log_info "Scan output doesn't clearly self-report FULFILLED/PROPOSED — check $out by hand (advisory, non-blocking)"
            fi
            ;;
        php-guardrails-open-blocks-rescan)
            _guardrails_scan_prompt "Run /refactor-scan against this repo. Follow skills/refactor-scan/SKILL.md literally, including its step 2 resume check and skills/refactor-scan/references/guardrails-track.md. Report explicitly, as your final line: RESUMED (worked the existing phpmd #5 Open entry only) or RESCANNED (walked the tree fresh and proposed other nodes too)."
            local out="/tmp/guardrails-track-$FIXTURE-scan.log"
            # Line-anchored, not a bare substring grep: the model's own
            # reasoning prose legitimately uses the word "rescanned" in a
            # negative sense elsewhere in the transcript (e.g. "nodes not
            # rescanned per guardrails-track.md") even on a correct RESUMED
            # run — only the actual final self-report line counts.
            if grep -qiE "^RESCANNED" "$out" 2>/dev/null; then
                log_fail "Scan output self-reports RESCANNED — Open may have been rescanned instead of resumed — see $out"
            elif grep -qiE "^RESUMED" "$out" 2>/dev/null; then
                log_pass "Scan output self-reports RESUMED — see $out"
            else
                log_info "Scan output doesn't clearly self-report RESUMED/RESCANNED — check $out by hand (advisory, non-blocking)"
            fi
            ;;
        php-guardrails-first-run)
            _guardrails_scan_prompt "Run one full pass: /refactor-scan, then /refactor-learn's closing call, against this repo. Follow skills/refactor-scan/SKILL.md and skills/refactor-learn/SKILL.md literally, including skills/refactor-scan/references/guardrails-track.md and skills/refactor-learn/references/guardrails-write.md. This target's Guardrails Track nodes are already fully resolved — report explicitly what (if anything) got written to docs/refactoring/bookkeeping.md."
            local bookkeeping="$FIXTURE_DST/docs/refactoring/bookkeeping.md"
            # refactor-learn/SKILL.md mandates a dedicated bookkeeping
            # branch, never a direct commit to the checked-out default
            # branch — this sandbox has no remote, so a correct run leaves
            # that branch unmerged (opening-a-merge-request.md's "no
            # forge/remote available" hand-off) rather than folding it back
            # into the working tree itself. Check the working tree first,
            # then every local branch, before concluding nothing was
            # written.
            local found=""
            if grep -q "## Guardrails" "$bookkeeping" 2>/dev/null && grep -q "Last scan:" "$bookkeeping" 2>/dev/null; then
                found="working tree"
            else
                local br
                for br in $(git -C "$FIXTURE_DST" branch --list --format='%(refname:short)' 2>/dev/null); do
                    if git -C "$FIXTURE_DST" show "$br:docs/refactoring/bookkeeping.md" 2>/dev/null | grep -q "## Guardrails" \
                        && git -C "$FIXTURE_DST" show "$br:docs/refactoring/bookkeeping.md" 2>/dev/null | grep -q "Last scan:"; then
                        found="branch $br"
                        break
                    fi
                done
            fi
            if [[ -n "$found" ]]; then
                log_pass "bookkeeping.md carries a ## Guardrails section with Last scan written ($found)"
            else
                log_fail "bookkeeping.md missing ## Guardrails / Last scan after the pass, on the working tree or any local branch — see $bookkeeping"
            fi
            ;;
        php-guardrails-rejection-symmetry)
            _guardrails_scan_prompt "Run /refactor-learn's early call against this repo, given this finding: the candidate MR for phpmd (issue .scratch/refactor/issues/05-phpmd.md) was closed without merge; the issue's own closing comment already gives a maintainer's structural reason. Follow skills/refactor-learn/SKILL.md literally, including skills/refactor-learn/references/guardrails-write.md. Report what you wrote."
            local bookkeeping="$FIXTURE_DST/docs/refactoring/bookkeeping.md"
            local oos="$FIXTURE_DST/docs/refactoring/out-of-scope/phpmd.md"
            if [[ -f "$oos" ]]; then
                log_pass "out-of-scope/phpmd.md written"
            else
                log_fail "out-of-scope/phpmd.md missing after the run — see $bookkeeping and $FIXTURE_DST/docs/refactoring/out-of-scope/"
            fi
            if grep -qE "Out-of-scope:" "$bookkeeping" 2>/dev/null && grep -qE "^- phpmd" <(sed -n '/## Guardrails/,$p' "$bookkeeping" 2>/dev/null | sed -n '/Out-of-scope:/,/^$/p'); then
                log_pass "## Guardrails's Out-of-scope list names phpmd"
            else
                log_info "## Guardrails's Out-of-scope list doesn't clearly name phpmd — check $bookkeeping by hand (advisory, non-blocking)"
            fi
            if grep -qE "^- phpmd" <(sed -n '/## Guardrails/,$p' "$bookkeeping" 2>/dev/null | sed -n '/Open:/,/^$/p'); then
                log_fail "## Guardrails's Open list still names phpmd — should have been removed"
            else
                log_pass "## Guardrails's Open list no longer names phpmd"
            fi
            ;;
        php-track-open-priority-guardrails)
            _guardrails_scan_prompt "Run one pass of the orchestrator against this repo: Track selection (skills/continuous-refactoring/SKILL.md step 0b, skills/continuous-refactoring/references/track-scheduler.md) and then /refactor-scan with the selected Track (skills/refactor-scan/SKILL.md, skills/refactor-scan/references/guardrails-track.md, skills/refactor-scan/references/track-open-processing.md). Stop after scan's output — do not implement. Report, as your final line: WORKED phpmd (the Guardrails Open walk worked phpmd) or WORKED priority (the refactor:priority issue was worked instead)."
            local out="/tmp/guardrails-track-$FIXTURE-scan.log"
            if grep -qiE "^WORKED priority" "$out" 2>/dev/null; then
                log_fail "Scan output self-reports WORKED priority — the priority label wrongly preempted the Guardrails Open walk — see $out"
            elif grep -qiE "^WORKED phpmd" "$out" 2>/dev/null; then
                log_pass "Scan output self-reports WORKED phpmd — the Open walk was not preempted — see $out"
            else
                log_info "Scan output doesn't clearly self-report WORKED phpmd/priority — check $out by hand (advisory, non-blocking)"
            fi
            ;;
        php-guardrails-old-schema)
            _guardrails_scan_prompt "Run /refactor-scan against this repo. Follow skills/refactor-scan/SKILL.md literally, including skills/refactor-scan/references/guardrails-track.md. This repo's docs/refactoring/bookkeeping.md already has a closed ## Safety Net section but still carries old-style Fulfilled nodes residue and no ## Guardrails section. Report explicitly: did the pass run normally, and did it error on or need to migrate the old fields?"
            local bookkeeping="$FIXTURE_DST/docs/refactoring/bookkeeping.md"
            if grep -q "## Safety Net" "$bookkeeping" 2>/dev/null; then
                log_pass "Pre-existing ## Safety Net section still present, untouched"
            else
                log_fail "Pre-existing ## Safety Net section is gone — see $bookkeeping"
            fi
            local out="/tmp/guardrails-track-$FIXTURE-scan.log"
            if grep -qiE "error|cannot proceed|unrecognized field" "$out" 2>/dev/null; then
                log_info "Scan output mentions an error/unrecognized-field phrase — check $out by hand (advisory, non-blocking)"
            else
                log_pass "Scan output doesn't report an error on the old-schema fields — see $out"
            fi
            ;;
        php-guardrails-scan-fills-open)
            _guardrails_scan_prompt "Run one full pass against this repo: the Guardrails Track is due with an empty Open, so run /refactor-scan for it and then /refactor-learn's closing call. Follow skills/refactor-scan/SKILL.md, skills/refactor-scan/references/guardrails-track.md and skills/refactor-learn/references/guardrails-write.md literally. Report, as your final line, the Open list you recorded into ## Guardrails as: OPEN: <slugs, comma separated, in order>."
            local out="/tmp/guardrails-track-$FIXTURE-scan.log"
            _check_open_order "$out" phpmd coverage-floor composer-audit phpstan-level-6 phpstan-level-7 phpstan-level-8 phpstan-level-9 phpstan-level-10 phpstan-deprecation-rules php-minimal-version semgrep
            if ls "$FIXTURE_DST/.scratch/refactor/issues/" 2>/dev/null | grep -q .; then
                log_fail "Issue file(s) exist under .scratch/refactor/issues/ — Track nodes must not be pre-filed by a scan — see $FIXTURE_DST/.scratch/refactor/issues/"
            else
                log_pass "No candidate issue was filed for the recorded Open nodes"
            fi
            ;;
        *)
            log_fail "No guardrails-track check wired for fixture: $FIXTURE"
            ;;
    esac

    rm -rf "$FIXTURE_DST/.agents"
}

# Shared helper for run_guardrails_track's cases above: run one opencode
# prompt with --auto against $FIXTURE_DST, logging to
# /tmp/guardrails-track-$FIXTURE-scan.log. Advisory only — never fails the
# caller. Mirrors _safety_net_scan_prompt exactly, own log prefix so the two
# Tracks' runs never clobber each other's transcript.
_guardrails_scan_prompt() {
    local prompt="$1"
    local out="/tmp/guardrails-track-$FIXTURE-scan.log"
    if ! timeout "$OPENCODE_TIMEOUT" bash -c 'cd "$1" && '"$opencode_bin"' run -m '"$OPENCODE_MODEL"' --auto "$2"' _ "$FIXTURE_DST" "$prompt" > "$out" 2>&1; then
        log_info "Opencode run failed or timed out — see $out (advisory, not failing test)"
    fi
}

# Ticket 09 — Housekeeping Track reconciliation regressions
# (skills/continuous-refactoring/references/housekeeping-track.md).
# Local-only, advisory, non-CI — same posture as
# `safety-net-track`/`guardrails-track`: the reconciliation is a behavioral
# property of the orchestrator's own prose, no deterministic ground truth to
# assert against. Each `php-housekeeping-*` fixture exercises one checklist
# item from ticket 09; dispatches by fixture name to the matching check
# below. Reuses `_guardrails_scan_prompt`'s and `_safety_net_scan_prompt`'s
# own shared-helper shape (own log prefix, so no transcript ever collides
# with either Track's own tier).
run_housekeeping_track() {
    log_info "=== Housekeeping Track behavior — fixture: $FIXTURE ==="
    local opencode_bin
    opencode_bin="$(resolve_opencode_bin)" || return 0

    mkdir -p "$FIXTURE_DST/.agents"
    ln -sfn "$REPO_DIR/skills" "$FIXTURE_DST/.agents/skills"

    case "$FIXTURE" in
        php-housekeeping-hand-adopted-guardrails)
            _housekeeping_scan_prompt "Run the Housekeeping Track process against this repo. Follow skills/continuous-refactoring/references/housekeeping-track.md literally — this target has a ## Housekeeping section (Cadence: 7, Last scan: 2026-09-01) and ## Guardrails already closed. The reconciliation step should walk the tooling tree and judge each node's Fulfilment check itself (agent judgement), NOT read Fulfilled nodes. Report explicitly: (1) which nodes were judged fulfilled and got their Housekeeping lines added, (2) whether Fulfilled nodes was read or not, and (3) whether housekeeping-template.md was created."
            local template="$FIXTURE_DST/docs/refactoring/housekeeping-template.md"
            if [[ -f "$template" ]]; then
                log_pass "housekeeping-template.md was created"
                if grep -qi "Fulfilled nodes" "$template" 2>/dev/null; then
                    log_fail "housekeeping-template.md mentions Fulfilled nodes — should not depend on it"
                else
                    log_pass "housekeeping-template.md doesn't reference Fulfilled nodes"
                fi
            else
                log_fail "housekeeping-template.md was not created — reconciliation may have failed"
            fi
            local out="/tmp/housekeeping-track-$FIXTURE-scan.log"
            if grep -qi "Fulfilled nodes" "$out" 2>/dev/null; then
                log_info "Scan output mentions Fulfilled nodes — check $out by hand (advisory, non-blocking)"
            else
                log_pass "Scan output doesn't reference Fulfilled nodes — agent judgement used instead"
            fi
            ;;
        php-housekeeping-old-schema)
            _housekeeping_scan_prompt "Run the Housekeeping Track process against this repo. Follow skills/continuous-refactoring/references/housekeeping-track.md literally. This target's bookkeeping.md is still in the old shape (Fulfilled nodes present, no ## Housekeeping section). The reconciliation should walk the tooling tree and judge fulfilment via agent judgement, NOT by reading Fulfilled nodes. Report explicitly: (1) did the pass run normally without erroring on the old Fulfilled nodes field, (2) which nodes got their Housekeeping lines, and (3) was ## Housekeeping created."
            local bookkeeping="$FIXTURE_DST/docs/refactoring/bookkeeping.md"
            if grep -q "loop-config" "$bookkeeping" 2>/dev/null && grep -q "Fulfilled nodes" "$bookkeeping" 2>/dev/null; then
                log_pass "Pre-existing Fulfilled nodes content still present, untouched"
            else
                log_fail "Pre-existing Fulfilled nodes content is gone — see $bookkeeping"
            fi
            local template="$FIXTURE_DST/docs/refactoring/housekeeping-template.md"
            if [[ -f "$template" ]]; then
                log_pass "housekeeping-template.md was created"
            else
                log_fail "housekeeping-template.md was not created — reconciliation may have failed"
            fi
            local out="/tmp/housekeeping-track-$FIXTURE-scan.log"
            if grep -qiE "error|cannot proceed|unrecognized field" "$out" 2>/dev/null; then
                log_info "Scan output mentions an error/unrecognized-field phrase — check $out by hand (advisory, non-blocking)"
            else
                log_pass "Scan output doesn't report an error on the old-schema fields — see $out"
            fi
            ;;
        *)
            log_fail "No housekeeping-track check wired for fixture: $FIXTURE"
            ;;
    esac

    rm -rf "$FIXTURE_DST/.agents"
}

# Shared helper for run_housekeeping_track's cases above: run one opencode
# prompt with --auto against $FIXTURE_DST, logging to
# /tmp/housekeeping-track-$FIXTURE-scan.log. Advisory only — never fails the
# caller. Mirrors _safety_net_scan_prompt / _guardrails_scan_prompt exactly,
# own log prefix so no tier's transcript ever clobbers another's.
_housekeeping_scan_prompt() {
    local prompt="$1"
    local out="/tmp/housekeeping-track-$FIXTURE-scan.log"
    if ! timeout "$OPENCODE_TIMEOUT" bash -c 'cd "$1" && '"$opencode_bin"' run -m '"$OPENCODE_MODEL"' --auto "$2"' _ "$FIXTURE_DST" "$prompt" > "$out" 2>&1; then
        log_info "Opencode run failed or timed out — see $out (advisory, not failing test)"
    fi
}

# Ticket 04 — Orchestrator Track-selection regressions
# (skills/continuous-refactoring/references/track-scheduler.md,
# skills/continuous-refactoring/SKILL.md step 0b). Local-only, advisory,
# non-CI — same posture as `safety-net-track`/`guardrails-track`: the
# scheduler is a behavioral property of the orchestrator's own prose, no
# deterministic ground truth to assert against. Each `php-scheduler-*`
# fixture exercises one distinct checklist item from ticket 04; dispatches by
# fixture name to the matching check below. Reuses `_guardrails_scan_prompt`'s
# and `_safety_net_scan_prompt`'s own shared-helper shape (own log prefix, so
# no transcript ever collides with either Track's own tier).
run_scheduler() {
    log_info "=== Track scheduler behavior — fixture: $FIXTURE ==="
    local opencode_bin
    opencode_bin="$(resolve_opencode_bin)" || return 0

    mkdir -p "$FIXTURE_DST/.agents"
    ln -sfn "$REPO_DIR/skills" "$FIXTURE_DST/.agents/skills"

    case "$FIXTURE" in
        php-scheduler-staleness-selection)
            _scheduler_scan_prompt "Run the orchestrator's own Track-selection step against this repo — follow skills/continuous-refactoring/SKILL.md step 0b literally, including skills/continuous-refactoring/references/track-scheduler.md for the full algorithm, reading docs/refactoring/bookkeeping.md's ## Safety Net and ## Guardrails sections. Compute each Track's overdue_ratio, then hand the winner to refactor-scan (skills/refactor-scan/SKILL.md step 4, including guardrails-track.md or safety-net-track.md as appropriate) for one scan only — stop there, do not continue past refactor-scan's own proposals (no design, no implement). Report, as your final line: SELECTED: Safety Net or SELECTED: Guardrails, naming whichever Track the scheduler actually selected."
            local out="/tmp/scheduler-$FIXTURE-scan.log"
            if grep -qiE "^SELECTED: *Safety Net" "$out" 2>/dev/null; then
                log_fail "Scheduler self-reports SELECTED: Safety Net — Guardrails (ratio 2.5) should have outranked Safety Net (ratio ~1.056) despite the fixed tie-break order — see $out"
            elif grep -qiE "^SELECTED: *Guardrails" "$out" 2>/dev/null; then
                log_pass "Scheduler self-reports SELECTED: Guardrails — see $out"
            else
                log_info "Scheduler output doesn't clearly self-report SELECTED: Safety Net/Guardrails — check $out by hand (advisory, non-blocking)"
            fi
            if grep -qiE "2\.5|150 */ *60|far more overdue|more overdue than Safety Net" "$out" 2>/dev/null; then
                log_pass "Scan output shows the ratio reasoning (Guardrails' higher overdue_ratio) — advisory sign the staleness comparison actually ran (see $out)"
            else
                log_info "Scan output doesn't clearly show the ratio comparison — check $out by hand (advisory, non-blocking)"
            fi
            ;;
        php-scheduler-investigation-fallback)
            _scheduler_scan_prompt "Run the orchestrator's own Track-selection step against this repo — follow skills/continuous-refactoring/SKILL.md step 0b literally, including skills/continuous-refactoring/references/track-scheduler.md for the full algorithm, reading docs/refactoring/bookkeeping.md's ## Safety Net, ## Guardrails, and ## Investigation sections. Compute (or, for Investigation, note the absence of) each Track's overdue_ratio, then hand the winner to refactor-scan (skills/refactor-scan/SKILL.md step 4, including skills/refactor-scan/references/investigation-track.md if Investigation wins) for one scan only — stop there, do not continue past refactor-scan's own proposals (no design, no implement). Report, as your final line: SELECTED: Safety Net or SELECTED: Guardrails or SELECTED: Investigation, naming whichever Track the scheduler actually selected."
            local out="/tmp/scheduler-$FIXTURE-scan.log"
            if grep -qiE "^SELECTED: *Investigation" "$out" 2>/dev/null; then
                log_pass "Scheduler self-reports SELECTED: Investigation — see $out"
            elif grep -qiE "^SELECTED: *Safety Net|^SELECTED: *Guardrails" "$out" 2>/dev/null; then
                log_fail "Scheduler self-reports a Safety Net/Guardrails selection — neither is due this pass (overdue_ratio ~0.2/~0.15), Investigation (always due, no fixed Cadence) should have been the only due-and-eligible Track — see $out"
            else
                log_info "Scheduler output doesn't clearly self-report SELECTED: Safety Net/Guardrails/Investigation — check $out by hand (advisory, non-blocking)"
            fi
            if grep -qiE "structural-scan" "$out" 2>/dev/null; then
                log_pass "Scan output mentions structural-scan — advisory sign refactor-scan actually reached investigation-track.md's own proposal step (see $out)"
            else
                log_info "Scan output doesn't clearly mention structural-scan — check $out by hand (advisory, non-blocking)"
            fi
            ;;
        php-scheduler-housekeeping-competes)
            _scheduler_scan_prompt "Run the orchestrator's own Track-selection step against this repo — follow skills/continuous-refactoring/SKILL.md step 0b literally, including skills/continuous-refactoring/references/track-scheduler.md for the full algorithm, reading docs/refactoring/bookkeeping.md's ## Safety Net, ## Guardrails, ## Housekeeping, and ## Investigation sections. Compute (or, for Investigation, note the absence of) each Track's overdue_ratio. Report, as your final line before continuing: SELECTED: Safety Net or SELECTED: Guardrails or SELECTED: Housekeeping or SELECTED: Investigation, naming whichever Track the scheduler actually selected. Then, only if Housekeeping was selected, run skills/continuous-refactoring/SKILL.md step 0c: follow skills/continuous-refactoring/references/housekeeping-track.md's own process (it is not handed to refactor-scan) — reconcile, open this cycle's issue per docs/agents/issue-tracker.md, work the checklist from docs/refactoring/housekeeping-template.md plus the standing AGENTS.md/skills check, run the quality gate, then reach the Deliver step. This sandbox has no git remote, so stop once you reach opening-a-merge-request.md's own 'no forge/remote available' branch — do not attempt to push or open a real merge request."
            local out="/tmp/scheduler-$FIXTURE-scan.log"
            if grep -qiE "^SELECTED: *Housekeeping" "$out" 2>/dev/null; then
                log_pass "Scheduler self-reports SELECTED: Housekeeping — see $out"
            elif grep -qiE "^SELECTED: *Safety Net|^SELECTED: *Guardrails|^SELECTED: *Investigation" "$out" 2>/dev/null; then
                log_fail "Scheduler self-reports a Track other than Housekeeping — Housekeeping's ratio (~4.29) is the highest due Track this pass, above Guardrails (~1.33) despite the fixed tie-break order ranking Guardrails higher — see $out"
            else
                log_info "Scheduler output doesn't clearly self-report SELECTED: Safety Net/Guardrails/Housekeeping/Investigation — check $out by hand (advisory, non-blocking)"
            fi
            if grep -qiE "4\.29|30 */ *7|higher (ratio|than Guardrails)|Guardrails.*outrank|ratio.*higher than Guardrails" "$out" 2>/dev/null; then
                log_pass "Scan output shows the ratio reasoning (Housekeeping's higher overdue_ratio over Guardrails) — advisory sign the staleness comparison actually ran (see $out)"
            else
                log_info "Scan output doesn't clearly show the ratio comparison — check $out by hand (advisory, non-blocking)"
            fi
            if grep -qiE "Housekeeping — 20|housekeeping-template|chore/housekeeping" "$out" 2>/dev/null; then
                log_pass "Scan output mentions the Housekeeping cycle's own issue/branch — advisory sign housekeeping-track.md's own process actually ran (see $out)"
            else
                log_info "Scan output doesn't clearly mention a Housekeeping cycle issue/branch — check $out by hand (advisory, non-blocking; only expected when Housekeeping was selected)"
            fi
            ;;
        php-scheduler-bootstrap-investigation)
            _scheduler_scan_prompt "Run the orchestrator's own Track-selection step against this repo — follow skills/continuous-refactoring/SKILL.md step 0b literally, including skills/continuous-refactoring/references/track-scheduler.md for the full algorithm. Check the one-time exception FIRST (track-scheduler.md's own 'One-time exception' section), before any overdue_ratio/tie-break computation: read docs/refactoring/bookkeeping.md's ## Safety Net section and note whether Investigation/Guardrails/Housekeeping have each already had their own turn. Then hand the winner to refactor-scan (skills/refactor-scan/SKILL.md step 4, including the matching Track's own reference file) for one scan only — stop there, do not continue past refactor-scan's own proposals (no design, no implement). Report, as your final line: SELECTED: Safety Net or SELECTED: Guardrails or SELECTED: Housekeeping or SELECTED: Investigation, naming whichever Track the scheduler actually selected."
            local out="/tmp/scheduler-$FIXTURE-scan.log"
            if grep -qiE "^SELECTED: *Investigation" "$out" 2>/dev/null; then
                log_pass "Scheduler self-reports SELECTED: Investigation — see $out"
            elif grep -qiE "^SELECTED: *Guardrails|^SELECTED: *Housekeeping|^SELECTED: *Safety Net" "$out" 2>/dev/null; then
                log_fail "Scheduler self-reports a Track other than Investigation — this is the pass right after Safety Net's Open first emptied, with Investigation/Guardrails/Housekeeping all never run; the one-time exception should select Investigation first, ahead of Guardrails even though ordinary never-run tie-break would rank Guardrails higher — see $out"
            else
                log_info "Scheduler output doesn't clearly self-report SELECTED — check $out by hand (advisory, non-blocking)"
            fi
            if grep -qiE "one-time exception|bootstrap|Investigation.*(first|before).*Guardrails|exception.*(fire|appl)" "$out" 2>/dev/null; then
                log_pass "Scan output shows the one-time exception reasoning — advisory sign the check actually ran ahead of ratio/tie-break (see $out)"
            else
                log_info "Scan output doesn't clearly show the one-time exception reasoning — check $out by hand (advisory, non-blocking)"
            fi
            if grep -qiE "structural-scan" "$out" 2>/dev/null; then
                log_pass "Scan output mentions structural-scan — advisory sign refactor-scan actually reached investigation-track.md's own proposal step (see $out)"
            else
                log_info "Scan output doesn't clearly mention structural-scan — check $out by hand (advisory, non-blocking)"
            fi
            ;;
        php-scheduler-bootstrap-guardrails)
            _scheduler_scan_prompt "Run the orchestrator's own Track-selection step against this repo — follow skills/continuous-refactoring/SKILL.md step 0b literally, including skills/continuous-refactoring/references/track-scheduler.md for the full algorithm. Check the one-time exception FIRST (track-scheduler.md's own 'One-time exception' section): read docs/refactoring/bookkeeping.md's ## Safety Net and ## Investigation sections — Investigation already ran its own turn (section present, Pending candidates: none) — so its own condition should NOT match; check whether Guardrails still owes its turn instead. Then hand the winner to refactor-scan (skills/refactor-scan/SKILL.md step 4, including guardrails-track.md) for one scan only — stop there, do not continue past refactor-scan's own proposals (no design, no implement). Report, as your final line: SELECTED: Safety Net or SELECTED: Guardrails or SELECTED: Housekeeping or SELECTED: Investigation, naming whichever Track the scheduler actually selected."
            local out="/tmp/scheduler-$FIXTURE-scan.log"
            if grep -qiE "^SELECTED: *Guardrails" "$out" 2>/dev/null; then
                log_pass "Scheduler self-reports SELECTED: Guardrails — see $out"
            elif grep -qiE "^SELECTED: *Investigation" "$out" 2>/dev/null; then
                log_fail "Scheduler self-reports SELECTED: Investigation again — Investigation's own turn already completed (Pending candidates: none), the one-time exception should have advanced to Guardrails instead — see $out"
            elif grep -qiE "^SELECTED: *Housekeeping|^SELECTED: *Safety Net" "$out" 2>/dev/null; then
                log_fail "Scheduler self-reports a Track other than Guardrails — Guardrails still owes its own one-time-exception turn (never run yet) and should have been selected next, ahead of Housekeeping — see $out"
            else
                log_info "Scheduler output doesn't clearly self-report SELECTED — check $out by hand (advisory, non-blocking)"
            fi
            if grep -qiE "one-time exception|Investigation.*(done|complete|already)|Guardrails.*(never run|absent|first)" "$out" 2>/dev/null; then
                log_pass "Scan output shows the one-time exception reasoning (Investigation's turn already done, Guardrails' still owed) — advisory sign (see $out)"
            else
                log_info "Scan output doesn't clearly show the one-time exception reasoning — check $out by hand (advisory, non-blocking)"
            fi
            ;;
        php-scheduler-bootstrap-housekeeping)
            _scheduler_scan_prompt "Run the orchestrator's own Track-selection step against this repo — follow skills/continuous-refactoring/SKILL.md step 0b literally, including skills/continuous-refactoring/references/track-scheduler.md for the full algorithm. Check the one-time exception FIRST (track-scheduler.md's own 'One-time exception' section): read docs/refactoring/bookkeeping.md's ## Safety Net, ## Guardrails, and ## Investigation sections — both Investigation and Guardrails already ran their own turns (present, Investigation's Pending candidates: none) — so neither of their conditions should match; check whether Housekeeping still owes its turn instead. Then, only if Housekeeping was selected, run skills/continuous-refactoring/SKILL.md step 0c: follow skills/continuous-refactoring/references/housekeeping-track.md's own process (it is not handed to refactor-scan) — reconcile, open this cycle's issue per docs/agents/issue-tracker.md, work the checklist from docs/refactoring/housekeeping-template.md plus the standing AGENTS.md/skills check, run the quality gate, then reach the Deliver step. This sandbox has no git remote, so stop once you reach opening-a-merge-request.md's own 'no forge/remote available' branch — do not attempt to push or open a real merge request. Report, as your final line before continuing: SELECTED: Safety Net or SELECTED: Guardrails or SELECTED: Housekeeping or SELECTED: Investigation, naming whichever Track the scheduler actually selected."
            local out="/tmp/scheduler-$FIXTURE-scan.log"
            if grep -qiE "^SELECTED: *Housekeeping" "$out" 2>/dev/null; then
                log_pass "Scheduler self-reports SELECTED: Housekeeping — see $out"
            elif grep -qiE "^SELECTED: *Investigation|^SELECTED: *Guardrails" "$out" 2>/dev/null; then
                log_fail "Scheduler self-reports Investigation/Guardrails again — both already had their own one-time-exception turn (sections present, Investigation's Pending candidates: none), the sequence should have advanced to Housekeeping instead — see $out"
            elif grep -qiE "^SELECTED: *Safety Net" "$out" 2>/dev/null; then
                log_fail "Scheduler self-reports SELECTED: Safety Net — Housekeeping still owes its own one-time-exception turn (never run yet) and should have been selected — see $out"
            else
                log_info "Scheduler output doesn't clearly self-report SELECTED — check $out by hand (advisory, non-blocking)"
            fi
            if grep -qiE "one-time exception|Housekeeping.*(never run|absent|first|owed)|Investigation.*(done|complete)|Guardrails.*(done|complete|present)" "$out" 2>/dev/null; then
                log_pass "Scan output shows the one-time exception reasoning (Investigation/Guardrails' turns already done, Housekeeping's still owed) — advisory sign (see $out)"
            else
                log_info "Scan output doesn't clearly show the one-time exception reasoning — check $out by hand (advisory, non-blocking)"
            fi
            if grep -qiE "Housekeeping — 20|housekeeping-template|chore/housekeeping" "$out" 2>/dev/null; then
                log_pass "Scan output mentions the Housekeeping cycle's own issue/branch — advisory sign housekeeping-track.md's own process actually ran (see $out)"
            else
                log_info "Scan output doesn't clearly mention a Housekeeping cycle issue/branch — check $out by hand (advisory, non-blocking; only expected when Housekeeping was selected)"
            fi
            ;;
        php-scheduler-bootstrap-resumes)
            _scheduler_scan_prompt "Run the orchestrator's own Track-selection step against this repo — follow skills/continuous-refactoring/SKILL.md step 0b literally, including skills/continuous-refactoring/references/track-scheduler.md for the full algorithm. Check the one-time exception FIRST (track-scheduler.md's own 'One-time exception' section): read docs/refactoring/bookkeeping.md's ## Safety Net, ## Guardrails, ## Housekeeping, and ## Investigation sections — every one of Investigation/Guardrails/Housekeeping has already run at least once, and Investigation carries no in-flight Pending candidates, so the exception should NOT apply this pass. Then run ordinary overdue_ratio/tie-break selection instead. Report, as your final line: SELECTED: Safety Net or SELECTED: Guardrails or SELECTED: Housekeeping or SELECTED: Investigation, naming whichever Track the scheduler actually selected."
            local out="/tmp/scheduler-$FIXTURE-scan.log"
            if grep -qiE "^SELECTED: *Guardrails" "$out" 2>/dev/null; then
                log_pass "Scheduler self-reports SELECTED: Guardrails — see $out"
            elif grep -qiE "^SELECTED: *Investigation" "$out" 2>/dev/null; then
                log_fail "Scheduler self-reports SELECTED: Investigation — the one-time exception is permanently done here (all three Tracks already had their turn), and ordinary ratio scheduling should have picked Guardrails (overdue_ratio ~1.33), not Investigation 'by elimination' — see $out"
            elif grep -qiE "^SELECTED: *Safety Net|^SELECTED: *Housekeeping" "$out" 2>/dev/null; then
                log_fail "Scheduler self-reports a Track other than Guardrails — Guardrails (overdue_ratio ~1.33) is the only genuinely due Track this pass; Safety Net (~0.2) and Housekeeping (~0.57) are both not due — see $out"
            else
                log_info "Scheduler output doesn't clearly self-report SELECTED — check $out by hand (advisory, non-blocking)"
            fi
            if grep -qiE "1\.33|80 */ *60|exception.*(done|retired|no longer|doesn.t apply)|ordinary.*(ratio|selection)" "$out" 2>/dev/null; then
                log_pass "Scan output shows the ratio reasoning and/or confirms the one-time exception no longer applies — advisory sign (see $out)"
            else
                log_info "Scan output doesn't clearly show the ratio/exception-retired reasoning — check $out by hand (advisory, non-blocking)"
            fi
            ;;
        php-scheduler-safety-net-blockade)
            _scheduler_scan_prompt "Run the orchestrator's own Track-selection step against this repo — follow skills/continuous-refactoring/SKILL.md step 0b literally, including skills/continuous-refactoring/references/track-scheduler.md for the full algorithm. Read docs/refactoring/bookkeeping.md's ## Safety Net section — its Open is non-empty (phpstan-level-6, coverage-floor). The Safety Net blockade rule applies: while Safety Net Open is non-empty, it is selected and nothing else runs, even if no node is currently workable. Then hand Safety Net to refactor-scan (skills/refactor-scan/SKILL.md step 4, including safety-net-track.md) for one Open walk — stop there, do not continue past the walk (no design, no implement). Report, as your final line: SELECTED: Safety Net, and list any skipped non-workable nodes with their reasons."
            local out="/tmp/scheduler-$FIXTURE-scan.log"
            if grep -qiE "^SELECTED: *Safety Net" "$out" 2>/dev/null; then
                log_pass "Scheduler self-reports SELECTED: Safety Net — see $out"
            elif grep -qiE "^SELECTED: *Guardrails|^SELECTED: *Housekeeping|^SELECTED: *Investigation" "$out" 2>/dev/null; then
                log_fail "Scheduler self-reports a Track other than Safety Net — Safety Net Open is non-empty (blockade active), nothing else should run — see $out"
            else
                log_info "Scheduler output doesn't clearly self-report SELECTED — check $out by hand (advisory, non-blocking)"
            fi
            if grep -qiE "blockade|non-empty.*Open|nothing.*(else|workable)|skipped|phpstan-level-6|coverage-floor" "$out" 2>/dev/null; then
                log_pass "Scan output mentions the blockade/non-workable nodes — advisory sign the blockade reasoning ran (see $out)"
            else
                log_info "Scan output doesn't clearly show the blockade reasoning — check $out by hand (advisory, non-blocking)"
            fi
            ;;
        php-scheduler-guardrails-stalled)
            _scheduler_scan_prompt "Run the orchestrator's own Track-selection step against this repo — follow skills/continuous-refactoring/SKILL.md step 0b literally, including skills/continuous-refactoring/references/track-scheduler.md for the full algorithm. Read docs/refactoring/bookkeeping.md's ## Safety Net, ## Guardrails, ## Housekeeping, and ## Investigation sections. Safety Net Open is empty (no blockade). Guardrails Open is non-empty (phpstan-level-6, coverage-floor) but both entries are non-workable (blocked or needs-info). Per the Eligibility rule, Guardrails with Open non-empty but nothing workable yields — it drops out of ratio comparison. Then pick the highest overdue_ratio among the remaining due-and-eligible Tracks. Report, as your final line: SELECTED: Safety Net or SELECTED: Guardrails or SELECTED: Housekeeping or SELECTED: Investigation, naming whichever Track the scheduler actually selected."
            local out="/tmp/scheduler-$FIXTURE-scan.log"
            if grep -qiE "^SELECTED: *Housekeeping" "$out" 2>/dev/null; then
                log_pass "Scheduler self-reports SELECTED: Housekeeping — see $out (Guardrails yielded, Housekeeping's ratio ~4.29 wins)"
            elif grep -qiE "^SELECTED: *Guardrails" "$out" 2>/dev/null; then
                log_fail "Scheduler self-reports SELECTED: Guardrails — Guardrails has non-empty Open with nothing workable, it should have yielded — see $out"
            elif grep -qiE "^SELECTED: *Safety Net|^SELECTED: *Investigation" "$out" 2>/dev/null; then
                log_fail "Scheduler self-reports a Track other than Housekeeping — Guardrails yielded, Housekeeping (ratio ~4.29) should be the highest due Track — see $out"
            else
                log_info "Scheduler output doesn't clearly self-report SELECTED — check $out by hand (advisory, non-blocking)"
            fi
            if grep -qiE "yield|non-workable|nothing.*(workable|blocked)|needs-info|stalled|phpstan-level-6|coverage-floor" "$out" 2>/dev/null; then
                log_pass "Scan output mentions Guardrails yielding/non-workable nodes — advisory sign the yield reasoning ran (see $out)"
            else
                log_info "Scan output doesn't clearly show the yield reasoning — check $out by hand (advisory, non-blocking)"
            fi
            ;;
        php-scheduler-housekeeping-preempts-guardrails)
            _scheduler_scan_prompt "Run the orchestrator's own Track-selection step against this repo — follow skills/continuous-refactoring/SKILL.md step 0b literally, including skills/continuous-refactoring/references/track-scheduler.md for the full algorithm. Read docs/refactoring/bookkeeping.md's ## Safety Net, ## Guardrails, ## Housekeeping, and ## Investigation sections. Safety Net Open is empty (no blockade). Guardrails Open is non-empty with workable entries (composer-audit, phpmd). Housekeeping is due at overdue_ratio ~4.29, Guardrails at ~1.33. Per the preemption rule, Housekeeping preempts Guardrails for one pass when due (overdue_ratio >= 1). Then, only if Housekeeping was selected, run skills/continuous-refactoring/SKILL.md step 0c: follow skills/continuous-refactoring/references/housekeeping-track.md's own process. This sandbox has no git remote, so stop once you reach opening-a-merge-request.md's own 'no forge/remote available' branch. Report, as your final line: SELECTED: Safety Net or SELECTED: Guardrails or SELECTED: Housekeeping or SELECTED: Investigation."
            local out="/tmp/scheduler-$FIXTURE-scan.log"
            if grep -qiE "^SELECTED: *Housekeeping" "$out" 2>/dev/null; then
                log_pass "Scheduler self-reports SELECTED: Housekeeping — see $out"
            elif grep -qiE "^SELECTED: *Guardrails" "$out" 2>/dev/null; then
                log_fail "Scheduler self-reports SELECTED: Guardrails — Housekeeping's ratio (~4.29) preempts Guardrails (~1.33) via the preemption rule — see $out"
            elif grep -qiE "^SELECTED: *Safety Net|^SELECTED: *Investigation" "$out" 2>/dev/null; then
                log_fail "Scheduler self-reports a Track other than Housekeeping — Housekeeping (ratio ~4.29) should preempt Guardrails — see $out"
            else
                log_info "Scheduler output doesn't clearly self-report SELECTED — check $out by hand (advisory, non-blocking)"
            fi
            if grep -qiE "preempt|4\.29|30 */ *7|higher.*(ratio|than Guardrails)|Guardrails.*outrank|ratio.*higher than Guardrails" "$out" 2>/dev/null; then
                log_pass "Scan output shows the preemption reasoning — advisory sign the preemption rule actually ran (see $out)"
            else
                log_info "Scan output doesn't clearly show the preemption reasoning — check $out by hand (advisory, non-blocking)"
            fi
            if grep -qiE "Housekeeping — 20|housekeeping-template|chore/housekeeping" "$out" 2>/dev/null; then
                log_pass "Scan output mentions the Housekeeping cycle's own issue/branch — advisory sign housekeeping-track.md's own process actually ran (see $out)"
            else
                log_info "Scan output doesn't clearly mention a Housekeeping cycle issue/branch — check $out by hand (advisory, non-blocking; only expected when Housekeeping was selected)"
            fi
            ;;
        php-scheduler-bootstrap-guardrails-open)
            _scheduler_scan_prompt "Run the orchestrator's own Track-selection step against this repo — follow skills/continuous-refactoring/SKILL.md step 0b literally, including skills/continuous-refactoring/references/track-scheduler.md for the full algorithm. Check the one-time exception FIRST (track-scheduler.md's own 'One-time exception' section): read docs/refactoring/bookkeeping.md's ## Safety Net, ## Investigation, ## Guardrails, and ## Housekeeping sections. Safety Net Open is empty (precondition met). Investigation is present (done, Pending candidates: none). Guardrails is present with a non-empty Open (phpstan-level-6, coverage-floor). Housekeeping is absent (never run). The one-time exception should advance to Housekeeping — it only checks whether each section exists, not Guardrails' Open state. Then, only if Housekeeping was selected, run skills/continuous-refactoring/SKILL.md step 0c: follow skills/continuous-refactoring/references/housekeeping-track.md's own process. This sandbox has no git remote, so stop once you reach opening-a-merge-request.md's own 'no forge/remote available' branch. Report, as your final line: SELECTED: Safety Net or SELECTED: Guardrails or SELECTED: Housekeeping or SELECTED: Investigation."
            local out="/tmp/scheduler-$FIXTURE-scan.log"
            if grep -qiE "^SELECTED: *Housekeeping" "$out" 2>/dev/null; then
                log_pass "Scheduler self-reports SELECTED: Housekeeping — see $out"
            elif grep -qiE "^SELECTED: *Guardrails" "$out" 2>/dev/null; then
                log_fail "Scheduler self-reports SELECTED: Guardrails — Guardrails is already present (section exists), condition 2 requires it to be absent; the exception should have advanced to Housekeeping instead — see $out"
            elif grep -qiE "^SELECTED: *Investigation" "$out" 2>/dev/null; then
                log_fail "Scheduler self-reports SELECTED: Investigation — Investigation is already present (done), condition 1 should not match — see $out"
            elif grep -qiE "^SELECTED: *Safety Net" "$out" 2>/dev/null; then
                log_fail "Scheduler self-reports SELECTED: Safety Net — the one-time exception should fire (Housekeeping absent) — see $out"
            else
                log_info "Scheduler output doesn't clearly self-report SELECTED — check $out by hand (advisory, non-blocking)"
            fi
            if grep -qiE "one-time exception|bootstrap|exception.*(fire|appl)|Housekeeping.*(never run|absent|first|owed)|Guardrails.*(present|Open)" "$out" 2>/dev/null; then
                log_pass "Scan output shows the one-time exception reasoning (advancing past Guardrails' non-empty Open) — advisory sign (see $out)"
            else
                log_info "Scan output doesn't clearly show the one-time exception reasoning — check $out by hand (advisory, non-blocking)"
            fi
            if grep -qiE "Housekeeping — 20|housekeeping-template|chore/housekeeping" "$out" 2>/dev/null; then
                log_pass "Scan output mentions the Housekeeping cycle's own issue/branch — advisory sign housekeeping-track.md's own process actually ran (see $out)"
            else
                log_info "Scan output doesn't clearly mention a Housekeeping cycle issue/branch — check $out by hand (advisory, non-blocking; only expected when Housekeeping was selected)"
            fi
            ;;
        *)
            log_fail "No scheduler check wired for fixture: $FIXTURE"
            ;;
    esac

    rm -rf "$FIXTURE_DST/.agents"
}

# Shared helper for run_scheduler's cases above: run one opencode prompt with
# --auto against $FIXTURE_DST, logging to /tmp/scheduler-$FIXTURE-scan.log.
# Advisory only — never fails the caller. Mirrors _safety_net_scan_prompt /
# _guardrails_scan_prompt exactly, own log prefix so no tier's transcript
# ever clobbers another's.
_scheduler_scan_prompt() {
    local prompt="$1"
    local out="/tmp/scheduler-$FIXTURE-scan.log"
    if ! timeout "$OPENCODE_TIMEOUT" bash -c 'cd "$1" && '"$opencode_bin"' run -m '"$OPENCODE_MODEL"' --auto "$2"' _ "$FIXTURE_DST" "$prompt" > "$out" 2>&1; then
        log_info "Opencode run failed or timed out — see $out (advisory, not failing test)"
    fi
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
        agent-loop)
            run_agent_loop
            ;;
        judge)
            run_judge
            ;;
        lift)
            run_lift
            ;;
        decision-gate-bypass)
            run_decision_gate_bypass
            ;;
        safety-net-track)
            run_safety_net_track
            ;;
        guardrails-track)
            run_guardrails_track
            ;;
        housekeeping-track)
            run_housekeeping_track
            ;;
        scheduler)
            run_scheduler
            ;;
        *)
            log_fail "Unknown tier: $TIER"
            usage
            ;;
    esac

    print_summary
}

main
