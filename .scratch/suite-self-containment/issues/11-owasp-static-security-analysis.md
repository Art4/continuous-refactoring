# 11 — Add OWASP-aware static security analysis

**What to build:** The baseline carries a static security analysis pass against known attack patterns (OWASP Top 10) — the PHPStan security extension or equivalent, plus a security checklist the two-axis review's standards axis carries. Findings become candidates in `refactor-scan`; violations the tools miss are flagged in review.

**Blocked by:** 06 — Decide the baseline tooling details (grilling)

**Status:** ready-for-agent

- [ ] A static security pass exists in the baseline (tooling + review checklist)
- [ ] Findings are filed as candidates, not silently ignored
- [ ] Pass and checklist match ticket 06's defaults