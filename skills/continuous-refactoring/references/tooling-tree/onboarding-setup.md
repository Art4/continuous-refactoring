# `onboarding-setup`

Node on the generic **tooling tree** (`../tooling-tree.md`); parents, edges, and the diagram live there. Vocabulary: `CONTEXT.md` (**node**, **required edge**, **recommended edge**).

- **Name:** Onboarding Setup
- **Tool:** none — the suite's own prerequisite, not a third-party tool.
- **Purpose:** the target says how the suite reaches its tickets and merge requests, so a run can search the tracker and the forge.
- **Fulfilment check:** the target's `docs/agents/issue-tracker.md` has a `## Refactoring operations` section. The parser settles this itself; whatever is handed in for this node is ignored.
- **MR scope:** none — never a ticket. A run's first step fulfils this node by running the interview in `../onboarding-setup-interview.md`, which writes that section. The node stays in the tree as the root prerequisite every other node hangs beneath.
