# 07 — Validate: first loop pass in a PHP target repo

**What to build:** The suite is symlinked into a real PHP target repo and a first loop pass runs end-to-end: scan proposes missing first-wave **tooling tree** nodes as candidates (ADR-0005 — no `/refactor-baseline`), then `/continuous-refactoring` runs scan → prioritise → design → implement → review — using the suite's own skills only, without global skill references.

**Blocked by:** 05 ✓ done — Make the orchestrator degrade gracefully, 06 ✓ done — Tooling tree (ADR-0005), 12 ✓ done — Deliver each refactor as a merge request (skills updated to ADR-0005 as part of #12), 23 — Test-Fixture-Repo-Infrastruktur (Grilling erledigt, 25 ✓ done, 24 offen)

**Status:** blocked

- [ ] Suite symlinked into a PHP target repo
- [ ] Scan files at least one missing first-wave tooling-tree node as a `refactor:candidate` (or reports the tree already fulfilled)
- [ ] At least one full loop pass completes with findings recorded (backlog issues, learnings)

## Comments

> **2026-08-21:** Unblocked on 06 via ADR-0005. Still blocked on 12 and on skills actually implementing the tooling tree (no ticket yet).

> **2026-08-21:** Blockers resolved. #12 implemented with full ADR-0005/0006 skill migration (commit `f14a626`). Ready for end-to-end validation in a real PHP target repo.

> **2026-08-21:** Blocked on 23 — Test-Fixture-Repo-Infrastruktur (eigenständiges Repo für PHP-Test-Fixtures).

> **2026-08-21:** 23 grilling done. Tickets 24 (README) + 25 (Shell-Script) erstellt. 07 bleibt blocked, bis beide fertig sind.

> **2026-08-21:** 25 done – Script aus tests-repo kopiert. 07 bleibt blocked auf 24.
