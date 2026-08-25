# 09 — Add mutation testing to the loop

**What to build:** The loop judges tests by whether they would catch a mutant, not by line coverage alone. Mutation testing (Infection for PHP) is configured with a defined scope — touched files in a loop pass, or a CI gate where affordable — and surviving mutants become candidates: the places where tests don't yet protect the seam.

**Blocked by:** 06 ✓ done — later wave (ADR-0005): mutation is a PHPUnit child, not first wave

**Wave:** later — see `.scratch/php-tooling-tree/spec.md` (not pickable before first-wave tickets 10/18 land)

**Status:** ready-for-agent

- [ ] Mutation tool configured with a defined scope per ticket 06's defaults
- [ ] Surviving mutants on touched files block a refactor or are filed as candidates
- [ ] Mutation gaps appear in `refactor-scan` output

## Comments

> **2026-08-21:** ADR-0005 — later wave (PHPUnit child). Not specified in 06.
> **2026-08-22:** Moved from `suite-self-containment/issues/` to `php-tooling-tree/issues/` — regrouped around the PHP tooling tree.
> **2026-08-23:** Ticket hygiene — added an explicit `Wave:` field so `Status: ready-for-agent` isn't misread as pickable now; the prose in `Blocked by` said "later wave" but nothing machine-scannable enforced it. See `spec.md`'s wave table.
