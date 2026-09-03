# `loop-config`

Node on the generic **tooling tree** (`skills/refactor-scan/references/tooling-tree.md`); parents, edges, and the diagram live there. Vocabulary: `CONTEXT.md` (**node**, **required edge**, **recommended edge**).

- **Name:** Refactoring Config
- **Tool:** none — this is the suite's own state, not a third-party tool.
- **Purpose:** the continuous-refactoring loop's own configuration exists in the target repo, so a pass has somewhere to read/write focus areas and merge-request create-mode.
- **Fulfilment check:** the Refactoring Notes' `bookkeeping.md` exists in the target repo (see `skills/continuous-refactoring/references/refactoring-bookkeeping.md` for how the Refactoring Notes' own path is resolved — `docs/refactoring/` by default).
- **MR scope:** one MR — before writing anything, run the interview in `skills/continuous-refactoring/references/loop-config-interview.md`: explore the target repo for tracker/create-mode/Refactoring-Notes-location signals, ask the human to decide (with a recommended answer for each), then record the decisions. The MR itself creates `bookkeeping.md` in the Refactoring Notes with `Create-mode` already set from that interview (see `skills/continuous-refactoring/references/refactoring-bookkeeping.md` for the file's shape — there is deliberately no stored cadence, the loop never triggers itself) and, when the interview chose a local tracker, `docs/agents/issue-tracker.md` alongside it. `refactor-design` runs the interview and files this node as a single `refactor:candidate` issue carrying its recorded decisions, same as any other tooling-tree node's plan — `refactor-design`'s own step 1 exception spells out why this node alone doesn't skip straight to filing the tree doc's generic spec.
