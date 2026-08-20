# 01 — Define the fallback convention and audit all references

**What to build:** A binding convention that every skill in the suite carries a `## Fallback` section — the `/X` reference becomes "use X if installed, else the inline fallback in this section" — plus a complete inventory of every external skill reference across the suite. `refactor-scan` becomes self-contained in this ticket (its `/codebase-design` vocabulary is already inline, so it only needs the convention applied).

**Blocked by:** None — can start immediately.

**Status:** done

- [x] Convention documented (ADR-0003: `## Fallback` section, reference-first with inline fallback; two depths self-sufficient/crash-safe; applies to global refs only)
- [x] Full inventory of `/grilling`, `/tdd`, `/code-review`, `/codebase-design`, `/domain-modeling` references across `skills/`
- [x] `refactor-scan` updated to the convention and self-contained

## Comments

> **2026-08-20:** Grilled and implemented. Decisions: reference-first with inline fallback; two depths (self-sufficient for core procedures, crash-safe for enrichment); runtime check before invoking `/X`; fallbacks inline per-skill (no shared file); only global references, suite-internal exempt; only referencing skills carry fallbacks; skip-with-note for crash-safe. Delivered: ADR `docs/adr/0003-external-skill-references-carry-a-fallback.md`, inventory `docs/agents/skill-references.md`, `refactor-scan` `## Fallback` section. Unblocks 02, 03, 04.
