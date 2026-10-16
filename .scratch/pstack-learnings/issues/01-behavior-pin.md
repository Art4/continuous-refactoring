# 01 — Pin behavior before structure moves

Type: task
Status: open

Refactor steps require a behavior pin (characterization test, snapshot or equivalence harness) before any structure moves; no coverage means the pin is written first; type check and lint do not count. For larger reshapes, an old-vs-new equivalence check on the real artifact. Wire into the implement step and the MR report.

First compare against the current skills: if already covered, close with a note instead of building.
See `../spec.md` for the source and the full list.

**Tooling-tree table (memory: tooling-tree-as-track-tagged-tables):** once Tracks no longer depend on each other, a Guardrails run can start without a finished Safety Net. The pin then moves from a Track precondition into each candidate: the implement step requires the candidate's own pin and writes it first when missing. Build this before or together with the table.

## Comments

### 2026-10-16 — gap check against `skills/`: partial

`design-point.md` (*Planning any other ticket*) names "tests that survive" and `implement-point.md` step 3 writes a failing test at the seam first, but nothing pins the *current* behaviour before structure moves, and tooling/baseline tickets rely on "the existing suite notices" without checking it reaches the touched code. Step 4 runs the suite only after the last commit. `signals.md` has "Untested or hard to test" for selection only. Missing: a pin per candidate before the first structural commit, a coverage check of the touched area, an old-vs-new equivalence check for larger reshapes.

### 2026-10-16 — grilled; decisions

Term: **Pinning Test** (pin), after Feathers' characterization test. Scope: structural tickets only; tooling and baseline tickets keep relying on the existing suite. The plan gets a `Pin` item (kind and what it holds; existing tests count when named); a type check or linter is none. The rule sits in `foundational-refactoring-rules.md` so it binds a target's own skills too, and the review's Spec axis checks it. The pin is the first commit, run on the old code and passing before any structural commit; the merge request names it and says it passed before the change; review reads the order from `git log`. Missing coverage: the run writes the pin as the first slice, also when autonomous; where that costs too much the agent judges, records the reason under `Decisions`, and it is an open question (human asked / autonomous run ends). The pin stays as a test if it meets *Tests worth keeping*, else the last commit removes it. No ADR. Tree order untouched (the table covers that); the equivalence check for large reshapes is ticket 12. Built in the PR "Pinning Test before structure moves".
