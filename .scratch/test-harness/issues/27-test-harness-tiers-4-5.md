# 27 — Test Harness Tiers 4+5: trigger tests, CI gate, lift measurement

**Type:** build

**What to build:** Remaining tiers of the test harness: trigger/discoverability tests (Tier 4) and CI gate with lift measurement (Tier 5).

**Blocked by:** 17 ✓ done — Tiers 2+3 implemented

**Status:** done

- [x] Tier 4: trigger tests incl. negative controls
- [x] Tier 5: CI gate + rubric grading + lift measurement

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

> **2026-08-30:** Implemented on `feature/test-harness-tiers-4-5`. Of the plan's three negative controls, only "scan on clean repo reports clean" turned out to be genuinely deterministic — the other two ("no git", "not a PHP project") are prose-level judgment calls a skill makes (`refactor-scan`'s own step-1 precondition; ADR-0008 explicitly keeps language recognition "an informal heuristic, not part of this ADR" on purpose), so those stay in Tier 4's opencode-advisory layer alongside "explicit + implicit invocation per skill" — same local-only, non-CI posture this harness already uses for `roadmap --opencode` and `agent-loop` (no model credentials in this repo's CI). Split: `scripts/test_trigger_controls.py` (new `tier4` CI job) covers the deterministic clean-repo control plus the ground-truth *signal* the other two prose-level judgments read; `fixtures/harness/run.sh tier4 <fixture> --opencode` covers the full behavioral set. New fixture `fixtures/php/php-clean/` (every deterministic PHP-tree leaf resolved) backs the clean-repo control and is added to the roadmap CI matrix (now 7 fixtures). Tier 5: `assert_baseline_not_regressed` (`fixtures/harness/lib/assertions.sh`) wired into `run_tier3`, with `actions/cache` persisting the gitignored `fixtures/baselines/` across CI runs so the comparison means something across runs, not just within one — caveat recorded in `fixtures/README.md`: CI has no LLM, so `found` is always 0 there today, the gate is real but currently compares 0 against 0. `judge`/`lift` commands added for rubric grading (`fixtures/harness/rubric.md`, 5 dimensions) and with/without-skill lift measurement, both local-only advisory. Filed [ticket 39](../../tooling-tree/issues/39-roadmap-simulation-never-proposes-open-structural-scan.md) (needs-triage) for a real `roadmap()` simulation bug found while building `php-clean` (it never proposes `structural-scan` once the gate is already open — `next_candidates()` already has the fix this lacks) — not fixed here to keep this ticket's diff scoped to the harness. 148 tests green (141 existing + 7 new); roadmap matrix verified locally against all 7 fixtures; tier2/tier3 verified locally with Docker.
