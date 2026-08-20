# 03 — Make refactor-implement self-contained

**What to build:** `refactor-implement` works in a target repo that has no `/tdd` skill installed. The red → green loop rules (red before green, one slice at a time, no refactoring inside the loop) and what makes a test worth keeping (behaviour through public interfaces, no tautological or implementation-coupled tests) are inline in the skill's `## Fallback` section.

**Blocked by:** 01 ✓ done — Fallback convention and audit

**Status:** done

- [x] Runs without `/tdd` — red → green rules and test-quality guidance are inline
- [x] Follows the convention (reference-first, inline fallback)

## Comments

> **2026-08-20:** Implemented. `refactor-implement` now carries a `## Fallback` section per ADR-0003: `/tdd` is self-sufficient — red → green rules (red before green, one slice at a time, no refactoring inside the loop) and test-quality guidance (behaviour through public interfaces, no tautological or implementation-coupled tests) are inline. Body reference reworded reference-first. Ledger row updated to "03 ✓ shipped" in `docs/agents/skill-references.md`.
