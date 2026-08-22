# 27 — Test Harness Tiers 4+5: trigger tests, CI gate, lift measurement

**Type:** build

**What to build:** Remaining tiers of the test harness: trigger/discoverability tests (Tier 4) and CI gate with lift measurement (Tier 5).

**Blocked by:** 17 ✓ done — Tiers 2+3 implemented

**Status:** ready-for-agent

- [ ] Tier 4: trigger tests incl. negative controls
- [ ] Tier 5: CI gate + rubric grading + lift measurement

## Plan

**Tier 4 — Trigger/discoverability tests:**
- Explicit + implicit invocation per skill
- Negative controls: orchestrator without git must not run, scan on clean repo reports clean, non-PHP project gets no PHP baseline

**Tier 5 — CI gate + lift measurement:**
- Wire harness into CI with regression baselines
- LLM-judge rubric grading
- With-skill vs without-skill lift measurement

## Comments

> **2026-08-21:** Split off from ticket 17. Tiers 2+3 done, 4+5 remaining.

> **2026-08-22:** Moved from `suite-self-containment/issues/` to `test-harness/issues/` — regrouped around the automated test harness.
