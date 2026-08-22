# 18 — Specify the PHPStan adoption chain

**Type:** task

**What to build:** The child sequence for the PHPStan node on the PHP **tooling tree** (ADR-0005). Only PHPStan gets the level-sequence pattern; the Rector suite nodes adopt in levels too but share only the shrink-baseline duty (ADR-0007); audit does not inherit either. The shape is recorded on `docs/php-tooling-tree.md`; this ticket fills in the implementable details (exact config, baseline mechanics, stop conditions).

**Blocked by:** 06 ✓ done — Tooling tree (ADR-0005)

**Status:** ready-for-agent

Decided shape (2026-08-22 grilling, ADR-0007 — nodes on `docs/php-tooling-tree.md`):

1. **Introduce** = `phpstan-level-0-baseline` — `phpstan/phpstan` as a dev dependency; locally runnable; level 0; a committed baseline so the local run is green.
2. **CI job** — *deferred to a later wave*: two-parent nodes (tool + ci-runner) are postponed wholesale (ADR-0007).
3. **Level nodes** = `phpstan-level-1` → `phpstan-level-2` → `phpstan-level-3`, each with hard edge to its predecessor — raise exactly one level, only from an **empty baseline**; shrinking findings into the regenerated baseline is part of every level node's MR scope. The chain stays open above level 3: further levels are appended nodes.

Remaining to specify:

- [x] Each child named: parents, fulfilment check, MR scope — done on `docs/php-tooling-tree.md`
- [ ] Level-0 + baseline on introduce made exact (what `phpstan.neon` contains, how the baseline is generated, paths)
- [x] ~~CI-job child~~ — deferred to a later wave (ADR-0007); revisit when two-parent nodes arrive
- [ ] Shrink vs raise-level details still open: stop conditions, what "empty baseline" means operationally (file absent vs empty ignore)
- [ ] Equivalents: Psalm already present fulfils `phpstan-level-0-baseline` (ADR-0005); whether the level nodes still apply then
- [x] Outcome recorded where the PHP tooling tree lives: `docs/php-tooling-tree.md`

## Comments

> **2026-08-21:** Split from the 06 grilling. ADR-0005 records the sketch and explicitly defers this specification here.

> **2026-08-22:** Moved from `suite-self-containment/issues/` to `php-tooling-tree/issues/` — regrouped around the PHP tooling tree.

> **2026-08-22:** Grilled the tree shape end-to-end. Edges are now **required**/**recommended** (ADR-0007); Rector split into `rector-dead-code` / `rector-type-coverage`; CI-job children deferred. Shape lives on `docs/php-tooling-tree.md` — this ticket now only fills in operational details.
