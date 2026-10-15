# 01 — Pin behavior before structure moves

Type: task
Status: open

Refactor steps require a behavior pin (characterization test, snapshot or equivalence harness) before any structure moves; no coverage means the pin is written first; type check and lint do not count. For larger reshapes, an old-vs-new equivalence check on the real artifact. Wire into the implement step and the MR report.

First compare against the current skills: if already covered, close with a note instead of building.
See `../spec.md` for the source and the full list.

**Tooling-tree table (memory: tooling-tree-as-track-tagged-tables):** once Tracks no longer depend on each other, a Guardrails run can start without a finished Safety Net. The pin then moves from a Track precondition into each candidate: the implement step requires the candidate's own pin and writes it first when missing. Build this before or together with the table.

## Comments
