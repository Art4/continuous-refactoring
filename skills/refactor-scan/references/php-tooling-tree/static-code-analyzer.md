# `static-code-analyzer`

Node on the PHP **tooling tree** (`skills/refactor-scan/references/php-tooling-tree.md`); parents, edges, and the diagram live there. Vocabulary: `CONTEXT.md` (**node**, **required edge**, **recommended edge**).

- **Name:** Static Code Analyzer
- **Tool:** none — pure organizational node, no fulfilment check or MR scope of its own.
- **Purpose:** the shared required parent of the tree's two static-analysis paths, `phpstan-level-0`
  (`phpstan.md`) and `psalm` (`psalm.md`) — makes the branch explicit in the diagram/edge table instead of
  it living only inside `phpstan-level-0`'s own fulfilment check, the way it used to.
- **Fulfilment check:** always fulfilled once `composer` (its own required parent) is fulfilled — no
  independent state, no tool run. Adds no additional waiting beyond `composer`'s real fulfilment.
- **MR scope:** none — never proposed, never an MR. Same pattern as `php-structural-scan` (`php-structural-scan.md`): pure plumbing,
  the real work happens in its two children.
