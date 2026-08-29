# Reference: manual tree-walk prompt (python3 unavailable)

When `python3` can't run — not installed, or executing it isn't permitted in the current harness — `refactor-scan` step 4 and `continuous-refactoring`'s outlook step dispatch a sub-agent with the prompt below instead of running `tooling_tree.py`. Fill in `{TARGET_REPO}` (the target repo's path) and `{N}` (`all` for the proposal step — the set is never capped — `1` for the outlook) before dispatching. With no sub-agent mechanism available, run the same steps yourself inline instead.

---

Read `skills/refactor-scan/references/tooling-tree.md` in full, plus the active language specialization's tree doc if one applies to `{TARGET_REPO}` (PHP: `skills/refactor-scan/references/php-tooling-tree.md`). Build the combined edge table from both, keeping the order rows appear in the docs (generic root first, then the specialization).

Before walking, read `{TARGET_REPO}/docs/refactoring/config.md`'s `Fulfilled nodes` field, if the file exists — a listed slug is already fulfilled; skip step 1 below for it entirely, don't re-derive it. Nodes not listed there still get evaluated fresh as usual.

For each node, in that order:

1. Already in `Fulfilled nodes`? Treat as fulfilled, skip to the next node — no file reads needed. Otherwise evaluate its Fulfilment check — written under the node's own heading — against `{TARGET_REPO}` directly. Read the files it names; don't guess.
2. A node is unblocked once every one of its **required** edges points to an already-fulfilled parent. `structural-scan`'s **resolved** edges are different: each one clears once its node is fulfilled *or* a file exists at `{TARGET_REPO}/docs/refactoring/out-of-scope/<node>.md` — once every resolved-edge parent clears one way or the other, `structural-scan` is proposable. Check this before the ordinary already-fulfilled skip below: `structural-scan` stays proposable every pass once open, it's not a one-time node.
3. Skip a node that's already fulfilled — except `structural-scan`, which the point above already covers.
4. Skip a node (other than `structural-scan`) that has a file at `{TARGET_REPO}/docs/refactoring/out-of-scope/<node>.md` — it was explicitly rejected and stays out until that entry is reversed (removed); don't re-propose it on the strength of newly-fulfilled required parents alone.
5. A node with one or more **recommended** edges is unblocked (by this point 5, on top of point 2) only once every one of those parents is *decided* — meaning fulfilled, or rejected. "Rejected" here includes a parent that's rejected outright (a file at `{TARGET_REPO}/docs/refactoring/out-of-scope/<parent>.md`) **and** a parent permanently closed because one of *its own* required parents is (recursively) decided-rejected the same way — walk that parent's required chain the same way you'd check point 2, just looking for a rejection instead of a fulfilment. A recommended parent that simply hasn't been reached yet (still blocked by its own required edges, neither fulfilled nor rejected) counts as undecided too — the same as one that's sitting unblocked-but-unactioned. Note any node you withhold this way, and which parent(s) it's still waiting on — the caller needs that to explain a gap in the results, not just a silently shorter list.

Collect nodes in table order until you have `{N}` that are unblocked (per points 2 and 5), not yet fulfilled, and not rejected, or the table runs out — `{N}` = `all` means don't stop early. `git` is never a candidate. This set is the fallback for `tooling_tree.py`'s `next` field; the withheld set from point 5 is the fallback for its `withheld` field.

Return only this: for each node in the set, its **Name** (the `**Name:**` field under its heading — never the node's slug) and one line — either why it's unblocked, or its Purpose, whichever the caller asked for; then, for the proposal step only, each withheld node's Name and which parent Name(s) it's waiting on. Nothing else: no restated edge table, no exploration narrative.
