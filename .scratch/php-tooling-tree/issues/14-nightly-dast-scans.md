# 14 — Add nightly DAST scans

**What to build:** A nightly pipeline runs DAST against a running instance (OWASP ZAP or Nuclei) — explicitly not part of per-MR gates, since DAST needs a live app. Findings feed the backlog as candidates for remediation (MR types), so dynamic security gaps are caught on a cadence instead of only at release time.

**Blocked by:** 06 ✓ done — later wave (ADR-0005): scheduled/DAST deferred; do not propose without a running instance

**Wave:** later — see `.scratch/php-tooling-tree/spec.md` (not pickable before first-wave tickets 10/18 land)

**Status:** ready-for-agent

- [ ] Nightly DAST pipeline runs against a running instance
- [ ] Findings are filed as candidates in the backlog
- [ ] Tool choice and scope match ticket 06's defaults

## Comments

> **2026-08-21:** ADR-0005 — later wave. Do not propose DAST without a configured running instance.
> **2026-08-22:** Moved from `suite-self-containment/issues/` to `php-tooling-tree/issues/` — regrouped around the PHP tooling tree.
> **2026-08-23:** Ticket hygiene — added an explicit `Wave:` field so `Status: ready-for-agent` isn't misread as pickable now; the prose in `Blocked by` said "later wave" but nothing machine-scannable enforced it. See `spec.md`'s wave table.
> **2026-09-07:** Signals ticket 2 (`.scratch/signals/issues/02-signal-tool-nodes-and-tree-edge-simplification.md`) settled the pattern this node should follow once picked up: a real, adoptable tooling-tree node with a **Signal** field, carrying **no** `resolved` edge into `php-structural-scan` — a Signal-producing node, not a Safety Net one (see `phpmd`'s and `secret-detection`'s node entries for the concrete shape). Applies here unchanged; a nightly scan against a live instance is inherently unsuited to gating a per-MR structural pass.
