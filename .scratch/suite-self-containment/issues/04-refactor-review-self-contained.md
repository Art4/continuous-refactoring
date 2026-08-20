# 04 — Make refactor-review self-contained

**What to build:** `refactor-review` works in a target repo that has no `/code-review` skill installed. The Fowler smell baseline (the fixed set of smells from `code-review`, each a labelled judgement call, documented repo standard overriding) and the standards-axis rules are inline in the skill's `## Fallback` section.

**Blocked by:** 01 — Fallback convention and audit

**Status:** ready-for-agent

- [ ] Runs without `/code-review` — the smell baseline and standards-axis rules are inline
- [ ] Follows the convention (reference-first, inline fallback)
