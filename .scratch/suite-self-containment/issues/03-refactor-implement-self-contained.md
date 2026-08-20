# 03 — Make refactor-implement self-contained

**What to build:** `refactor-implement` works in a target repo that has no `/tdd` skill installed. The red → green loop rules (red before green, one slice at a time, no refactoring inside the loop) and what makes a test worth keeping (behaviour through public interfaces, no tautological or implementation-coupled tests) are inline in the skill's `## Fallback` section.

**Blocked by:** 01 — Fallback convention and audit

**Status:** ready-for-agent

- [ ] Runs without `/tdd` — red → green rules and test-quality guidance are inline
- [ ] Follows the convention (reference-first, inline fallback)
