# 10: Drift check and a detection-free test suite

Spec: `agent-judged-fulfilment`.

**What to build:** With every consumer switched over, make the tests independent of detection and guard the one remaining duplication. The manual tree-walk fallback keeps the graph rules in prose while the script keeps them in code; a local, advisory check runs the fallback on the shared seed fixtures and compares its workable and withheld results with the script's output on the same seed. The remaining fixtures and expected outputs that were derived from detection are re-based on seeds, and the ground-truth tier that depended on detection is adapted or retired with its documentation updated. CI gates the script contract tests and the static validation tiers; agent-judged behavior stays local and advisory.

**Blocked by:** 05 (Script reduced to graph logic), 07 (Working an `Open` node), 08 (Scheduler — blockade, yield, insertion), 09 (Housekeeping sweep; `Fulfilled nodes` removed).

**Status:** implemented — PR #112, open items listed in Comments

- [ ] An advisory check compares the fallback prose's workable and withheld results with the script's on every shared seed fixture and reports differences.
- [x] No fixture or expected output still depends on the parser's detection; each supplies a seed and a bookkeeping file instead.
- [x] The detection-dependent ground-truth tier is adapted to the agent-judged flow or retired, and the fixtures documentation states which checks run in CI and which are local and advisory.
- [x] CI runs the script contract tests and the static validation tiers and passes; nothing agent-judged is a CI gate.
- [ ] The eleven cases listed in the spec's testing decisions are each covered by a fixture or a contract test somewhere in the suite (tickets 05 to 09 carry most; gaps are closed here).

## Comments

**PR:** [#112](https://github.com/Art4/continuous-refactoring/pull/112)

- Item 1 not met. `scripts/drift_check.py` (moved out of CI discovery, run by hand) does not run the
  manual tree-walk fallback: its 31 tests hard-code expectations transcribed from `tree-walk-prompt.md`
  and assert them against the script's `next_candidates()` on inline temp-repo seeds. It reads no shared
  seed fixture, and its docstring's "runs both" is not true. `python3 scripts/drift_check.py` passes, but
  a drift between the prose and the script would only show up if the prose were re-transcribed by hand.
- Item 2: no fixture or `expected/` output is consumed by anything that detects. There is no
  `expected/roadmap.json`, `run.sh` no longer calls `tooling_tree.py`, and the only script-driven fixture,
  `php-clean`, carries a seed and a bookkeeping file. `php-empty`, `php-p0-empty`, `php-p0-nonempty`,
  `php-partial`, `php-psalm` and `non-php-project` carry neither; they feed only the agent-run tier 3
  ground truth.
- Item 3: tier 3 is documented as local-only/advisory (`fixtures/README.md` "Tier 3"); `fixtures/README.md`
  states per section which tiers gate CI and which are local and advisory.
- Item 4: on #113 all checks pass (Tier 1, Tier 2, Tier 4 deterministic, `validate`, `check`); the
  workflows run `unittest discover -s scripts -p 'test_*.py'`, `validate_skills.py` and tiers 1, 2, 4; no
  agent-judged tier is in CI. Earlier PRs of the stack show `check` (changelog-fragment) as fail on
  #103-#109 and #111, and pass on #110, #112, #113; their test and validation jobs pass.
- Item 5 not met as a whole; mapping of the spec's eleven cases (spec.md, Testing Decisions):
  1. Safety Net blockade, nothing workable: `php-scheduler-safety-net-blockade` (advisory, wired).
  2. Guardrails stalled: `php-scheduler-guardrails-stalled` (advisory, wired; the stalled report itself is
     not documented in skills, ticket 08 item 3).
  3. Guardrails workable + Housekeeping due: `php-scheduler-housekeeping-preempts-guardrails` (advisory,
     wired).
  4. Scan populates `Open` with blocked nodes: `php-guardrails-scan-fills-open` (advisory, wired) and
     `OrderedBacklogTests`/`TrackOpenFillingTests` (contract).
  5. Pick-up re-check: `php-track-open-hand-adopted` exists but is not wired into `run.sh` (ticket 07
     item 6).
  6. Rejected ancestor and reversal: `php-safety-net-rejection-cascade` (advisory, wired) and
     `ClosedByRejectionTests`/`RejectionCascadeTests` (contract).
  7. Gate nodes: `GateNodeContractTests` (no dependency, non-empty baseline, Psalm `phpstan-not-psalm`) and
     `php-psalm`.
  8. Housekeeping sweep of a hand-adopted Guardrails tool: `php-housekeeping-hand-adopted-guardrails`
     (advisory, wired).
  9. Priority label: `php-track-open-priority-guardrails` (wired); the Safety Net blockade variant
     `php-track-open-priority-vs-top` is not wired. Narrowed by ADR-0056 to pool filter plus tie-breaker.
  10. Old-schema / old-`Open`: `php-safety-net-old-schema`, `php-guardrails-old-schema`,
      `php-housekeeping-old-schema`, `php-safety-net-old-meaning-open` (wired) and
      `OldSchemaPassThroughTests`. No forced rescan, per the amended ADR-0056.
  11. Drift check: `scripts/drift_check.py`, which does not run the fallback (item 1).
  Open: cases 5 and 9 (Safety Net variant) are not runnable through the harness, case 11 is only nominally
  covered.
