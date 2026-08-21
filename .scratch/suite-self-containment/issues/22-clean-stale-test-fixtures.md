# 22 — Clean stale test fixtures referencing retired refactor-baseline

**Type:** task

**What to build:** Replace all references to the retired `refactor-baseline` skill in `scripts/test_validate_skills.py` with a clearly-fictional test fixture name. ADR-0005 retired the baseline; no `skills/refactor-baseline/` directory exists; but the test file uses it in 3 places as a fixture — a ghost skill that obscures architecture for new contributors.

**Blocked by:** None — can start immediately.

**Status:** ready-for-agent

- [ ] `refactor-baseline` replaced with `test-skill-fixture` (or similar neutral name) in all test fixtures
- [ ] CI passes: `python3 -m unittest discover -s scripts -p 'test_*.py'`
- [ ] No behavioral change — only fixture names change

## Comments

> **2026-08-21:** Created from architecture review candidate 5 (Speculative). Minor hygiene — the validator dynamically discovers skills from `skills/*/`, so it never references `refactor-baseline` in production. Only the test fixtures are affected.
