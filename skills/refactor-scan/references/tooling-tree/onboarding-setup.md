# `onboarding-setup`

Node on the generic **tooling tree** (`skills/refactor-scan/references/tooling-tree.md`); parents, edges, and the diagram live there. Vocabulary: `CONTEXT.md` (**node**, **required edge**, **recommended edge**).

- **Name:** Onboarding Setup
- **Tool:** none — this is the suite's own state, not a third-party tool.
- **Purpose:** the continuous-refactoring loop's own configuration exists in the target repo, so a pass has somewhere to read/write focus areas and merge-request create-mode.
- **Fulfilment check:** the Refactoring Notes' `bookkeeping.md` exists in the target repo (see `skills/continuous-refactoring/references/refactoring-bookkeeping.md` for how the Refactoring Notes' own path is resolved — `docs/refactoring/` by default).
- **Scope:** never proposed, never a candidate, no merge request. `continuous-refactoring`'s own onboarding step (step 0 of the dispatcher) fulfils this node before any Track runs, by running the interview in `skills/continuous-refactoring/references/onboarding-setup-interview.md` and writing `bookkeeping.md` (with `Create-mode` set from that interview — see `skills/continuous-refactoring/references/refactoring-bookkeeping.md` for the file's shape; there is deliberately no stored cadence for this loop itself, it never triggers itself) plus, where missing, `docs/agents/issue-tracker.md` and `docs/agents/triage-labels.md`. The node stays in the tree as the root prerequisite every other node hangs beneath; a scan only ever sees it already fulfilled, because `refactor-loop` and `continuous-housekeeping` abort when `bookkeeping.md` is missing.
