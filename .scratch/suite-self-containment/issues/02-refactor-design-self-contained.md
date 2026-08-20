# 02 — Make refactor-design self-contained

**What to build:** `refactor-design` works in a target repo that has none of the global skills installed. The grilling loop (rounds, frontier, numbered questions with recommended answers) and the domain-modeling side effects (CONTEXT.md updates, ADR offers) are described inline in the skill's `## Fallback` section, per the convention from ticket 01.

**Blocked by:** 01 — Fallback convention and audit

**Status:** ready-for-agent

- [ ] Runs without `/grilling` — the design tree / round / frontier loop is inline
- [ ] Runs without `/domain-modeling` — CONTEXT.md / ADR side effects are inline
- [ ] Follows the convention (reference-first, inline fallback)
