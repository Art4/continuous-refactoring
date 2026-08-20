---
name: refactor-baseline
description: Establish the tooling floor before the loop starts — code style, Rector, PHPStan, CI enforcement. Run once before the first loop pass. PHP specialization.
---

# Refactor Baseline

Establish the **baseline** — the tooling floor a codebase needs before refactoring can be measured. The loop judges structural quality; tools judge mechanical quality. No loop pass runs until the baseline exists.

This skill is specialized for a **general PHP project** (ADR-0002). Other languages add their own variant.

## Process

### 1. Inventory

Explore the project's current tooling. Do not assume anything exists. Check:

- `composer.json` — installed dev dependencies, PHP version floor
- Existing config files: `.php-cs-fixer.php`, `.php-cs-fixer.dist.php`, `rector.php`, `phpstan.neon`, `phpstan.neon.dist`, `phpstan-baseline.neon`
- CI config (`.github/workflows/`, `.gitlab-ci.yml`, `build/`, etc.) — which quality jobs already run
- `Makefile` / `composer scripts` — convenience commands

Report what exists and what's missing.

### 2. Propose the trio

For each missing piece, propose the concrete introduction. Present as a plan, wait for confirmation before writing anything.

- **Code style** — PHP CS Fixer with a ruleset, wired into CI as a check.
- **Rector** — with a config (`rector.php`), first run in dry-run mode so it proposes a diff the team reviews rather than rewriting silently.
- **PHPStan** — at a chosen level (default `6`), with a baseline file so existing violations don't block adoption.

### 3. Confirm and write

Show the user the exact config contents and CI snippets you'll add. Get explicit confirmation per tool, then write.

### 4. Mark the baseline done

Write `docs/agents/refactoring.md` in the target repo with the baseline declared done. This is the marker the orchestrator reads to let the loop start.

The baseline's own first findings (PHPStan violations, Rector suggestions, style debt) become **candidates** in the backlog — see `refactor-scan` — not a separate fix-up path.

## Completion criterion

The three tools exist with configs, CI enforces them, and `docs/agents/refactoring.md` marks the baseline done.