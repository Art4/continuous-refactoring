# 11 — Add OWASP-aware static security analysis

**What to build:** The baseline carries a static security analysis pass against known attack patterns (OWASP Top 10) — the PHPStan security extension or equivalent, plus a security checklist the two-axis review's standards axis carries. Findings become candidates in `refactor-scan`; violations the tools miss are flagged in review. Candidate SAST stack (per ticket 06): Psalm Taint Analysis (strongest for A03 Injection, follows input → output data paths) · Semgrep with OWASP rulesets (broad Top 10 coverage) · PHPCS Security Audit · progpilot. The OWASP Top 10 mapping from the brainstorming (A01 → Arkitect/Deptrac, A03 → Psalm Taint, A08 → secret scanning, …) is reference input for the grilling.

**Blocked by:** 06 ✓ done — later wave (ADR-0005): all security deferred

**Status:** ready-for-agent

- [ ] A static security pass exists in the baseline (tooling + review checklist)
- [ ] Findings are filed as candidates, not silently ignored
- [ ] Pass and checklist match ticket 06's defaults

## Comments

> **2026-08-21:** ADR-0005 — later wave; all security deferred.
> **2026-08-22:** Moved from `suite-self-containment/issues/` to `php-tooling-tree/issues/` — regrouped around the PHP tooling tree.
