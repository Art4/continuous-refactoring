# 11 — Add OWASP-aware static security analysis

**What to build:** The baseline carries a static security analysis pass against known attack patterns (OWASP Top 10) — the PHPStan security extension or equivalent, plus a security checklist the two-axis review's standards axis carries. Findings become candidates in `refactor-scan`; violations the tools miss are flagged in review. Candidate SAST stack (per ticket 06): Psalm Taint Analysis (strongest for A03 Injection, follows input → output data paths) · Semgrep with OWASP rulesets (broad Top 10 coverage) · PHPCS Security Audit · progpilot. The OWASP Top 10 mapping from the brainstorming (A01 → Arkitect/Deptrac, A03 → Psalm Taint, A08 → secret scanning, …) is reference input for the grilling.

**Blocked by:** 06 ✓ done — later wave (ADR-0005): all security deferred

**Wave:** later — see `.scratch/php-tooling-tree/spec.md` (not pickable before first-wave tickets 10/18 land)

**Status:** ready-for-agent

- [ ] A static security pass exists in the baseline (tooling + review checklist)
- [ ] Findings are filed as candidates, not silently ignored
- [ ] Pass and checklist match ticket 06's defaults

## Comments

> **2026-08-21:** ADR-0005 — later wave; all security deferred.
> **2026-08-22:** Moved from `suite-self-containment/issues/` to `php-tooling-tree/issues/` — regrouped around the PHP tooling tree.
> **2026-08-23:** Ticket hygiene — added an explicit `Wave:` field so `Status: ready-for-agent` isn't misread as pickable now; the prose in `Blocked by` said "later wave" but nothing machine-scannable enforced it. See `spec.md`'s wave table.
> **2026-09-07:** Signals ticket 2 (`.scratch/signals/issues/02-signal-tool-nodes-and-tree-edge-simplification.md`) settled the pattern this node should follow once picked up: a real, adoptable tooling-tree node with a **Signal** field, carrying **no** `resolved` edge into `php-structural-scan` — a Signal-producing node, not a Safety Net one (see `phpmd`'s and `secret-detection`'s node entries for the concrete shape). Applies here unchanged; `psalm-taint-analysis` already sets the precedent that a security-scan tool can be a deterministic `php-structural-scan` leaf when it's proposed as gating, but this ticket's own SAST stack was never scoped as a gate — it stays Signal-only.
