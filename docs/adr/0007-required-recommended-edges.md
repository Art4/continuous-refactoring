# Required and recommended edges; Rector behind PHPStan levels

The tooling tree needs two kinds of edges, not one. A **required edge** gates: the child is proposed only once the parent is fulfilled, and rejecting a required parent closes every node beneath it. A **recommended edge** advises: the child stays proposable even when its recommended parent was rejected, the rejected parent is never re-proposed, and the merge request outlook states where it would have helped. Fulfilling a parent later unlocks its dependents; reopening a rejected node is a recorded reversal of its out-of-scope entry. A node is one adoption step of a tool — a tool may own several nodes, and a node may span several merge requests.

This revises ADR-0005's single-edge model and its first-wave list: Rector leaves the parallel Composer children and becomes suite nodes adopted in levels — `rector-dead-code` (required: `phpstan-level-0-baseline`) and `rector-type-coverage` (required: `phpstan-level-0-baseline`; recommended: `phpstan-level-3`, `php-cs-fixer`). Rector's rewrites are only reviewable under strict static analysis, and its output must remain styleable; adopting it blind in the first wave invited unreviewable MRs. The canonical shape now lives in `docs/php-tooling-tree.md`; target repos keep recording state under `docs/refactoring/`. CI-job children with two parents (tool + ci-runner) are deferred to a later wave.

## Considered Options

- **Keep Rector as a first-wave child of Composer** (ADR-0005). Rejected: Rector changes code at scale before any analysis or style gate exists to review that change.
- **Gate both Rector suites fully behind `phpstan-level-3`.** Partially rejected: dead-code rules are safe from level 0 on; only typing suites profit from level 3, so type coverage takes it as a recommended edge.

## Consequences

The PHPStan chain and the Rector suites share the shrink-baseline duty: every `phpstan-level-*` and `rector-*` merge request keeps analysis green by shrinking the baseline within the same MR. The chain above `phpstan-level-3` stays open — further levels are appended as new nodes.
