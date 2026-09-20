# 07: Working an `Open` node — top to bottom, re-checked at pick-up, no pre-filing

Spec: `agent-judged-fulfilment`.

**What to build:** When a node-based Track has been selected, the pass works the topmost workable node of its `Open`: unblocked per the graph, not flagged `needs-info`, not held back by the PHP floor. Right before creating the node's issue, the agent re-runs that one node's Fulfilment check. A node that has become fulfilled since the scan (for example adopted by hand) leaves `Open` without a merge request, and the pass continues with the next workable node. Only now is the node's issue created; Track nodes are no longer pre-filed, and Rank mode no longer chooses among them. A priority-labeled issue keeps narrowing the Rank pool exactly as today whenever Rank mode runs, but it never preempts a Track's `Open` walk (Track nodes are not in the Rank pool) and takes no part in Track selection. Nodes skipped as not workable are collected with a reason for the pass report. The suite-wide cap on open suite merge requests is unchanged.

**Blocked by:** 06 (A Track scan fills `Open`; `refactor-learn` maintains it).

**Status:** ready-for-agent

- [ ] With a selected Track, exactly one node is worked per pass: the topmost workable `Open` node.
- [ ] Before creating its issue, the node's Fulfilment check is re-run; if now fulfilled, the node leaves `Open` with no merge request and the pass moves on to the next workable node.
- [ ] The node's issue is created only when the node is worked; no issues are created for the other `Open` nodes, and Rank mode is not used to choose among Track nodes.
- [ ] A `refactor:priority`-labeled issue narrows the Rank pool only; it never preempts a Track's `Open` walk, does not bypass the selected Track or the Safety Net blockade, and waits until `Open` is empty (Safety Net) or has no workable node left (Guardrails).
- [ ] Skipped non-workable nodes appear with a reason in the pass report.
- [ ] Advisory agent fixtures cover: pick-up re-check on a hand-adopted node, top-to-bottom order with a blocked node in between, and a priority-labeled issue versus the top of `Open` (Safety Net blockade and Guardrails variants).
- [ ] The pre-filing decision's documentation states that it no longer applies to Track nodes.
