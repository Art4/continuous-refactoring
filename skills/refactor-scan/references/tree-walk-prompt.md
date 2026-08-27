# Reference: manual tree-walk prompt (python3 unavailable)

When `python3` can't run — not installed, or executing it isn't permitted in the current harness — `refactor-scan` step 4 and `continuous-refactoring`'s outlook step dispatch a sub-agent with the prompt below instead of running `tooling_tree.py`. Fill in `{TARGET_REPO}` (the target repo's path) and `{N}` (5 for the proposal step, 1 for the outlook) before dispatching. With no sub-agent mechanism available, run the same steps yourself inline instead.

---

Read `skills/refactor-scan/references/tooling-tree.md` in full, plus the active language specialization's tree doc if one applies to `{TARGET_REPO}` (PHP: `skills/refactor-scan/references/php-tooling-tree.md`). Build the combined edge table from both, keeping the order rows appear in the docs (generic root first, then the specialization).

For each node, in that order:

1. Evaluate its Fulfilment check — written under the node's own heading — against `{TARGET_REPO}` directly. Read the files it names; don't guess.
2. A node is unblocked once every one of its **required** edges points to an already-fulfilled parent. **Recommended** edges never block. `structural-scan`'s **resolved** edges are different: each one clears once its node is fulfilled *or* a file exists at `{TARGET_REPO}/docs/refactoring/out-of-scope/<node>.md` — once every resolved-edge parent clears one way or the other, `structural-scan` is proposable. Check this before the ordinary already-fulfilled skip below: `structural-scan` stays proposable every pass once open, it's not a one-time node.
3. Skip a node that's already fulfilled — except `structural-scan`, which the point above already covers.

Collect nodes in table order until you have `{N}` that are unblocked and not yet fulfilled, or the table runs out. `git` is never a candidate. This set is the fallback for `tooling_tree.py`'s `next` field.

Return only this: for each node in the set, its name and one line — either why it's unblocked, or its Purpose, whichever the caller asked for. Nothing else: no restated edge table, no exploration narrative.
