# 17 — Automated test harness — Tiers 2–5: artifact contracts, ground truth, triggers, CI gate

**Type:** build

**What to build:** The runtime tiers of the suite harness, on top of the static validation tier (16).

## Grilling Decisions

| # | Decision | Choice |
|---|----------|--------|
| 1 | Infrastructure | Custom harness (opencode + Docker + Bash) |
| 2 | Scope | Tiers 2+3 first, 4+5 later |
| 3 | Ground-truth fixtures | 3-5 fixtures |
| 4 | Artifact contracts | Issue structure + config + MR chain |
| 5 | Script language | Bash |
| 6 | Sandbox mode | Docker container with opencode |
| 7 | Assertion format | Exit-code + stdout |
| 8 | Precision/recall | Simple (precision = found/expected, recall = found/planted) |
| 9 | Baseline storage | `fixtures/baselines/` |
| 10 | Commit structure | Feature branch, separate commits per tier |

## Plan

**Feature branch:** `feature/test-harness-tiers-2-3`

**Dependencies:**
- 07 ✓ done — First loop pass validated
- 16 ✓ done — Tier 1 static validation
- 26 ✓ done — Harness infrastructure (Docker, Bash functions)

**Commits:**
1. Ticket 26: Harness infrastructure
2. Tier 2: Artifact contracts
3. Tier 3: Ground truth + fixtures

**Later (separate ticket):**
- Tiers 4+5 (trigger tests + CI gate)

**Status:** done

## Checklist

- [x] Harness decision made (grilling) and recorded
- [x] Ticket 26: Harness infrastructure
- [x] Tier 2: artifact contract assertions over a sandboxed loop run
- [x] Tier 3: ground-truth repos + precision/recall score + saved baseline
- [ ] Tier 4: trigger tests incl. negative controls *(see ticket 27)*
- [ ] Tier 5: CI gate + rubric grading + lift measurement *(see ticket 27)*

## Comments

> **2026-08-20:** Split off from ticket 16 — the runtime tiers moved here; Tier 1 (static suite validation) stays in 16.

> **2026-08-21:** ADR-0005 retires the baseline marker. Tier 4 negative control "orchestrator without a baseline marker must not refactor" is obsolete — replace with: without git, the suite must not run; missing tools are candidates, not a start-gate. `.out-of-scope/` assertions move to `docs/refactoring/`.

> **2026-08-21:** Grilling session complete. Decisions: custom harness (Docker + Bash), Tiers 2+3 first, 3-5 fixtures, exit-code + stdout, baseline in `fixtures/baselines/`.

> **2026-08-21:** Tiers 2+3 implemented and merged in PR #1. CI pipeline green. Tiers 4+5 planned as separate ticket.
