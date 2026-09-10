# 08 — Add a test-coverage floor to the baseline

**What to build:** The baseline measures test coverage in the target repo and CI enforces a floor, so a refactor that silently drops coverage fails the gate instead of drifting. Under-covered modules — untested seams — surface in `refactor-scan` as candidates (tooling pressure), making coverage a measurable loop dimension rather than an assumption. Baseline candidate: PHPUnit with a lightweight driver (PCOV or Xdebug); the concrete driver and floor are decided in ticket 06.

**Blocked by:** 06 ✓ done — later wave (ADR-0005): coverage is a PHPUnit child, not first wave

**Wave:** later — see `.scratch/php-tooling-tree/spec.md` (not pickable before first-wave tickets 10/18 land)

**Status:** done

- [x] Coverage driver + floor configured in the baseline, enforced by CI — new `coverage-floor` node
  (required parent `phpunit`), driver-agnostic Fulfilment check (PCOV is the MR-scope default, Xdebug
  acceptable on request), floor is a self-tightening ratchet (`.coverage-floor`, target-repo
  committed, never auto-bumped by CI) rather than a fixed percentage — ADR-0044
- [x] Coverage drops and under-covered modules surface in `refactor-scan` as candidates — feeds the
  existing generic **Untested / hard-to-test** Signal cue (`signals.md`) with real per-file Clover-XML
  numbers once adopted, no new mechanism or new Signal factor needed
- [x] Tool and floor choice match the defaults decided in ticket 06 (ADR) — PCOV matches ticket 06's
  own "PHPUnit + PCOV" brainstorming pairing

## Comments

> **2026-08-21:** ADR-0005 — later specialization of the test-runner node, not first wave. No coverage floor decided in 06.
> **2026-08-22:** Moved from `suite-self-containment/issues/` to `php-tooling-tree/issues/` — regrouped around the PHP tooling tree.
> **2026-08-23:** Ticket hygiene — added an explicit `Wave:` field so `Status: ready-for-agent` isn't misread as pickable now; the prose in `Blocked by` said "later wave" but nothing machine-scannable enforced it. See `spec.md`'s wave table.
> **2026-09-07:** Signals ticket 2 (`.scratch/signals/issues/02-signal-tool-nodes-and-tree-edge-simplification.md`) settled the pattern this node should follow once picked up: a real, adoptable tooling-tree node with a **Signal** field, carrying **no** `resolved` edge into `php-structural-scan` — a Signal-producing node, not a Safety Net one (see `phpmd`'s and `secret-detection`'s node entries for the concrete shape). Applies here unchanged; nothing about coverage floors argued for gating structural work.
> **2026-09-10:** Grilled jointly with tickets 11/13 (`/grill-with-docs`, three rounds) and implemented
> — ADR-0044. Settled: PCOV as the MR-scope default (Xdebug acceptable on request, Fulfilment check
> stays driver-agnostic either way); the floor is a ratchet (`.coverage-floor`, target-repo committed,
> starts at whatever the first real run measures, only ever rises via a normal reviewed commit — CI
> never auto-commits it, even upward); required parent `phpunit`; feeds the existing "Untested /
> hard-to-test" Signal cue, no new factor. Status: done.
