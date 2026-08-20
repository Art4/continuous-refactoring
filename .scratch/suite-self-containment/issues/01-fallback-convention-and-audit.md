# 01 — Define the fallback convention and audit all references

**What to build:** A binding convention that every skill in the suite carries a `## Fallback` section — the `/X` reference becomes "use X if installed, else the inline fallback in this section" — plus a complete inventory of every external skill reference across the suite. `refactor-scan` becomes self-contained in this ticket (its `/codebase-design` vocabulary is already inline, so it only needs the convention applied).

**Blocked by:** None — can start immediately.

**Status:** ready-for-agent

- [ ] Convention documented (each skill: `## Fallback` section, reference-first with inline fallback)
- [ ] Full inventory of `/grilling`, `/tdd`, `/code-review`, `/codebase-design`, `/domain-modeling` references across `skills/`
- [ ] `refactor-scan` updated to the convention and self-contained
