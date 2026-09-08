# 08 — Add a test-coverage floor to the baseline

**What to build:** The baseline measures test coverage in the target repo and CI enforces a floor, so a refactor that silently drops coverage fails the gate instead of drifting. Under-covered modules — untested seams — surface in `refactor-scan` as candidates (tooling pressure), making coverage a measurable loop dimension rather than an assumption. Baseline candidate: PHPUnit with a lightweight driver (PCOV or Xdebug); the concrete driver and floor are decided in ticket 06.

**Blocked by:** 06 ✓ done — later wave (ADR-0005): coverage is a PHPUnit child, not first wave

**Wave:** later — see `.scratch/php-tooling-tree/spec.md` (not pickable before first-wave tickets 10/18 land)

**Status:** ready-for-agent

- [ ] Coverage driver + floor configured in the baseline, enforced by CI
- [ ] Coverage drops and under-covered modules surface in `refactor-scan` as candidates
- [ ] Tool and floor choice match the defaults decided in ticket 06 (ADR)

## Comments

> **2026-08-21:** ADR-0005 — later specialization of the test-runner node, not first wave. No coverage floor decided in 06.
> **2026-08-22:** Moved from `suite-self-containment/issues/` to `php-tooling-tree/issues/` — regrouped around the PHP tooling tree.
> **2026-08-23:** Ticket hygiene — added an explicit `Wave:` field so `Status: ready-for-agent` isn't misread as pickable now; the prose in `Blocked by` said "later wave" but nothing machine-scannable enforced it. See `spec.md`'s wave table.
> **2026-09-07:** Signals ticket 2 (`.scratch/signals/issues/02-signal-tool-nodes-and-tree-edge-simplification.md`) settled the pattern this node should follow once picked up: a real, adoptable tooling-tree node with a **Signal** field, carrying **no** `resolved` edge into `php-structural-scan` — a Signal-producing node, not a Safety Net one (see `phpmd`'s and `secret-detection`'s node entries for the concrete shape). Applies here unchanged; nothing about coverage floors argued for gating structural work.
