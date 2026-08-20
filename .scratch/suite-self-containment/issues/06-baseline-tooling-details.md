# 06 — Decide the baseline tooling details (grilling)

**Type:** grilling

**What to build:** A decision, reached by a `/grilling` session, on the open baseline-tooling questions deferred from the suite design session (Q13): dependency pinning, PHPStan / Rector levels, and which additional tools (if any) belong in the baseline basket beyond php-cs-fixer, Rector, and PHPStan. The grilling explicitly weighs the goal's missing dimensions as candidates: a test-coverage floor (08), mutation testing (09), a dependency vulnerability scan (10), and an OWASP-aware static security pass (11). The outcome lands as an ADR in `docs/adr/` so the `refactor-baseline` skill can reference concrete defaults.

**Blocked by:** None — can start immediately.

**Status:** ready-for-agent

- [ ] Grilling session held; each open tooling question decided
- [ ] Coverage floor, mutation testing, dependency scan, and OWASP static analysis each decided — in the basket or explicitly out, with concrete defaults
- [ ] Outcome recorded as an ADR in `docs/adr/`
- [ ] `refactor-baseline` updated to reference the concrete defaults where applicable
