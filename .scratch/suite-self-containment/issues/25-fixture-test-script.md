# 25 — Shell Script for Fixture Tests

**What to build:** A shell script `scripts/run-test.sh` that automates fixture tests. The script supports multiple modes: setup, test, clean, and auto (all in one run).

**Blocked by:** None — can start immediately

**Status:** done

- [x] `scripts/run-test.sh` with modes: setup, test, clean, auto
- [x] `setup`: copy fixture from `fixtures/` to /tmp/, git init, git commit
- [x] `test`: start Docker container with variable PHP version
- [x] `clean`: remove temporary files
- [x] `auto`: setup → test → clean in one run
- [x] Exit-code + output for CI and manual use

## Comments

> **2026-08-21:** Split off from issue 23 (test fixture repo infrastructure).

> **2026-08-21:** Fixtures moved to main repo (no longer separate repo).

> **2026-08-21:** Script copied from `continuous-refactoring-tests/` and adapted.
