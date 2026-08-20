# 08 — Add a test-coverage floor to the baseline

**What to build:** The baseline measures test coverage in the target repo and CI enforces a floor, so a refactor that silently drops coverage fails the gate instead of drifting. Under-covered modules — untested seams — surface in `refactor-scan` as candidates (tooling pressure), making coverage a measurable loop dimension rather than an assumption.

**Blocked by:** 06 — Decide the baseline tooling details (grilling)

**Status:** ready-for-agent

- [ ] Coverage driver + floor configured in the baseline, enforced by CI
- [ ] Coverage drops and under-covered modules surface in `refactor-scan` as candidates
- [ ] Tool and floor choice match the defaults decided in ticket 06 (ADR)