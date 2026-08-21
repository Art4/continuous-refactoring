# 18 — Specify the PHPStan adoption chain

**Type:** task

**What to build:** The child sequence for the PHPStan node on the PHP **tooling tree** (ADR-0005). Only PHPStan gets this pattern; Rector / CS-Fixer / audit do not inherit it. The grilling sketched the shape; this ticket makes each step a named, implementable child node (what the MR contains, done-when, what the outlook names next).

**Blocked by:** 06 ✓ done — Tooling tree (ADR-0005)

**Status:** ready-for-agent

Sketch to specify (do not treat as the spec until this ticket fills it in):

1. **Introduce** — `phpstan/phpstan` as a dev dependency; locally runnable; level 0; a committed baseline so the local run is green.
2. **CI job** — next *if* the CI-runner node is fulfilled; if CI is missing, the CI-runner candidate comes first; if CI was rejected, this child is closed and the chain continues at (3).
3. **Shrink baseline** — fix findings that are in the baseline; shrink the baseline file in the same MR. Repeat across passes.
4. **Raise level** — only when the baseline is empty: bump one level, regenerate the baseline, no unrelated fixes. Then back to (3).

- [ ] Each child named: parents, fulfilment check, MR scope, outlook to the next child
- [ ] Level-0 + baseline on introduce is exact (what `phpstan.neon` contains, how the baseline is generated, paths)
- [ ] CI-job child: which job, how it stays green with the baseline, two parents (PHPStan introduce + CI-runner)
- [ ] Shrink vs raise-level: stop conditions, one-level-at-a-time, what “empty baseline” means (file absent vs empty ignore)
- [ ] Equivalents: Psalm already present fulfils PHPStan introduce (ADR-0005); whether any of (2)–(4) still apply
- [ ] Outcome recorded where the PHP tooling tree will live once skills implement ADR-0005 (do not invent a second source of truth)

## Comments

> **2026-08-21:** Split from the 06 grilling. ADR-0005 records the sketch and explicitly defers this specification here.
