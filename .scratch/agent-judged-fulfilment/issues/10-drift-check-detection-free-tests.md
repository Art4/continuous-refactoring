# 10: Drift check and a detection-free test suite

Spec: `agent-judged-fulfilment`.

**What to build:** With every consumer switched over, make the tests independent of detection and guard the one remaining duplication. The manual tree-walk fallback keeps the graph rules in prose while the script keeps them in code; a local, advisory check runs the fallback on the shared seed fixtures and compares its workable and withheld results with the script's output on the same seed. The remaining fixtures and expected outputs that were derived from detection are re-based on seeds, and the ground-truth tier that depended on detection is adapted or retired with its documentation updated. CI gates the script contract tests and the static validation tiers; agent-judged behavior stays local and advisory.

**Blocked by:** 05 (Script reduced to graph logic), 07 (Working an `Open` node), 08 (Scheduler — blockade, yield, insertion), 09 (Housekeeping sweep; `Fulfilled nodes` removed).

**Status:** ready-for-agent

- [ ] An advisory check compares the fallback prose's workable and withheld results with the script's on every shared seed fixture and reports differences.
- [ ] No fixture or expected output still depends on the parser's detection; each supplies a seed and a bookkeeping file instead.
- [ ] The detection-dependent ground-truth tier is adapted to the agent-judged flow or retired, and the fixtures documentation states which checks run in CI and which are local and advisory.
- [ ] CI runs the script contract tests and the static validation tiers and passes; nothing agent-judged is a CI gate.
- [ ] The eleven cases listed in the spec's testing decisions are each covered by a fixture or a contract test somewhere in the suite (tickets 05 to 09 carry most; gaps are closed here).
