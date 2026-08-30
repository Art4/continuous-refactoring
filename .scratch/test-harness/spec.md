# test-harness

Spec extracted from `suite-self-containment` (2026-08-22): the suite's automated test harness — deterministic static validation (Tier 1), sandboxed runtime tiers, fixture repos, and the CI gate.

Harness decisions were grilled in ticket 17: custom harness (opencode + Docker + Bash), Tiers 2+3 first, 3–5 ground-truth fixtures, exit-code + stdout assertions, baselines in `fixtures/baselines/`. Infrastructure lives under `fixtures/harness/`, fixtures under `fixtures/`.

## Issues

| # | Ticket | Tier | Status |
|---|--------|------|--------|
| 16 | Static suite validation (`scripts/validate_skills.py`) | 1 | done |
| 23 | Test fixture repo infrastructure | fixtures | done |
| 24 | README for `fixtures/` | fixtures | done |
| 25 | Shell script for fixture tests (`scripts/run-test.sh`) | infra | done |
| 26 | Harness infrastructure (Docker image, assertion lib, CI workflow) | infra | done |
| 17 | Artifact contracts + ground truth (Tiers 2+3) | 2–3 | done |
| 27 | Trigger tests incl. negative controls; CI gate + rubric grading + lift measurement | 4–5 | done |

Numbering was kept from the original feature so cross-references in done tickets stay valid.
