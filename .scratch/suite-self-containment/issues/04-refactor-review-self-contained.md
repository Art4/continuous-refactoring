# 04 — Make refactor-review self-contained

**What to build:** `refactor-review` works in a target repo that has no `/code-review` skill installed. The Fowler smell baseline (the fixed set of smells from `code-review`, each a labelled judgement call, documented repo standard overriding) and the standards-axis rules are inline in the skill's `## Fallback` section.

**Blocked by:** 01 ✓ done — Fallback convention and audit

**Status:** done

- [x] Runs without `/code-review` — the smell baseline and standards-axis rules are inline
- [x] Follows the convention (reference-first, inline fallback)
- [x] Tier 1 static validation passes (`python3 scripts/validate_skills.py .` exits 0)

## Comments

> **2026-08-20:** Implemented. `## Fallback` carries the self-sufficient contract — the full Fowler smell baseline (12 smells, each a labelled judgement call, repo-standard overrides, skip what tooling enforces) plus the standards-axis rules. Ledger row flipped to `04 ✓ shipped`, which now sets `requires_fallback` for `refactor-review`; Tier 1 validation passes. Unblocks 05.
