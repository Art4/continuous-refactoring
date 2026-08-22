# 26 — Test Harness Infrastructure

**Type:** build

**What to build:** Shared infrastructure for the test harness: Docker setup, Bash functions, and assertion helpers. This is the foundation for Tiers 2+3.

**Blocked by:** 07 ✓ done — First loop pass validated, 16 ✓ done — Tier 1 static validation

**Status:** done

- [x] Docker image for opencode + PHP
- [x] Bash library with assertion functions (`assert_file_exists`, `assert_field_value`, etc.)
- [x] Fixture setup script (copy fixture to Docker, run opencode)
- [x] CI script for GitHub Actions

## Plan

**Feature branch:** `feature/test-harness-tiers-2-3`

**Files:**
- `fixtures/harness/Dockerfile` — opencode + PHP 8.3 + Composer
- `fixtures/harness/lib/assertions.sh` — shared Bash functions
- `fixtures/harness/run.sh` — main script (load fixture, run opencode, assertions)
- `.github/workflows/test-harness.yml` — CI pipeline

## Comments

> **2026-08-21:** Split off from issue 17. Builds infrastructure for Tiers 2+3.

> **2026-08-21:** Implemented and merged in PR #1. CI pipeline green.

> **2026-08-22:** Moved from `suite-self-containment/issues/` to `test-harness/issues/` — regrouped around the automated test harness.
