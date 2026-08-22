# 23 — Test Fixture Repo Infrastructure

**Type:** grilling + build

**What to build:** Fixtures for suite validation in the main repo. Each fixture is a directory representing a specific state on the tooling tree.

**Grilling focus:**
- How many fixtures do we really need?
- Which states are critical for issue 07 (first loop pass)?
- Reset strategy: git clean vs. snapshot vs. rebuild?
- Should fixtures have their own commits (history) or be flat?
- How do we test negative controls (non-PHP)?

**Planned fixtures:**
1. `php-minimal/` — No tooling, just PHP files (first wave: everything missing)
2. `php-partial/` — Composer + CS-Fixer, but no PHPStan/Rector
3. `php-full/` — CI + Composer + all tools (structural candidates only)
4. `non-php/` — Node/Python/Go for negative controls

**Blocked by:** —

**Status:** done

- [x] Grilling: number and scope of fixtures
- [x] Grilling: reset strategy
- [x] Grilling: structure (separate git repos or subdirectories?)
- [x] 24 — README for fixtures
- [x] 25 — Shell script for fixture tests
- [x] Build: create repo (done — already exists)
- [x] Build: create fixtures (done — php-project-with-candidates exists)
- [x] Build: reset scripts/docs

## Comments

> **2026-08-21:** Split off from issue 07 — test fixtures maintained separately. Issue 07 will reference this ticket.

> **2026-08-21:** Grilling session complete. Tickets 24 (README) and 25 (shell script) created.

> **2026-08-21:** Fixtures moved from `continuous-refactoring-tests/` to main repo under `fixtures/`.

> **2026-08-21:** Tickets 24 + 25 done. Issue 23 fully complete.

> **2026-08-22:** Moved from `suite-self-containment/issues/` to `test-harness/issues/` — regrouped around the automated test harness.
