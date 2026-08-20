# 14 — Add nightly DAST scans

**What to build:** A nightly pipeline runs DAST against a running instance (OWASP ZAP or Nuclei) — explicitly not part of per-MR gates, since DAST needs a live app. Findings feed the backlog as candidates for remediation (MR types), so dynamic security gaps are caught on a cadence instead of only at release time.

**Blocked by:** 06 — Decide the baseline tooling details (grilling)

**Status:** ready-for-agent

- [ ] Nightly DAST pipeline runs against a running instance
- [ ] Findings are filed as candidates in the backlog
- [ ] Tool choice and scope match ticket 06's defaults