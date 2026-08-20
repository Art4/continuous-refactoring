# 02 — Make refactor-design self-contained

**What to build:** `refactor-design` works in a target repo that has none of the global skills installed. The grilling loop (rounds, frontier, numbered questions with recommended answers) and the domain-modeling side effects (CONTEXT.md updates, ADR offers) are described inline in the skill's `## Fallback` section, per the convention from ticket 01.

**Blocked by:** 01 ✓ done — Fallback convention and audit

**Status:** done

- [x] Runs without `/grilling` — the design tree / round / frontier loop is inline
- [x] Runs without `/domain-modeling` — CONTEXT.md / ADR side effects are inline
- [x] Follows the convention (reference-first, inline fallback)

## Comments

> **2026-08-20:** Implemented. `refactor-design` now carries a `## Fallback` section per ADR-0003: `/grilling` is self-sufficient (design tree / rounds / frontier / numbered questions with recommended answers inline), `/domain-modeling` is crash-safe (side effects already inline in section 2 and run regardless; enrichment moves skipped). Reviewed by two-axis review (Standards + Spec); findings addressed: ADR trigger aligned with section 2, skip-with-a-note clarified, question format matches `/grilling`. Ledger rows updated to "02 ✓ shipped" in `docs/agents/skill-references.md`. Unblocks 05.
