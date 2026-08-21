# 14 — Add nightly DAST scans

**What to build:** A nightly pipeline runs DAST against a running instance (OWASP ZAP or Nuclei) — explicitly not part of per-MR gates, since DAST needs a live app. Findings feed the backlog as candidates for remediation (MR types), so dynamic security gaps are caught on a cadence instead of only at release time.

**Blocked by:** 06 ✓ done — later wave (ADR-0005): scheduled/DAST deferred; do not propose without a running instance

**Status:** ready-for-agent

- [ ] Nightly DAST pipeline runs against a running instance
- [ ] Findings are filed as candidates in the backlog
- [ ] Tool choice and scope match ticket 06's defaults

## Comments

> **2026-08-21:** ADR-0005 — later wave. Do not propose DAST without a configured running instance.