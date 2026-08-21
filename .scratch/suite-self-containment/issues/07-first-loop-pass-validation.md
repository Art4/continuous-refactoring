# 07 — Validate: first loop pass in a PHP target repo

**What to build:** The suite is symlinked into a real PHP target repo and a first loop pass runs end-to-end: `/refactor-baseline` establishes the tooling floor, then `/continuous-refactoring` runs scan → prioritise → design → implement → review against it — using the suite's own skills only, without global skill references.

**Blocked by:** 05 ✓ done — Make the orchestrator degrade gracefully, 06 — Decide the baseline tooling details (grilling), 12 — Deliver each refactor as a merge request

**Status:** ready-for-agent

- [ ] Suite symlinked into a PHP target repo
- [ ] `refactor-baseline` completes (tooling floor + CI, baseline marked done)
- [ ] At least one full loop pass completes with findings recorded (backlog issues, learnings)
