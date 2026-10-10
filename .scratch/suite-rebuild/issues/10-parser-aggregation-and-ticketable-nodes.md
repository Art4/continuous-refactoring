# 10: Parser computes the gates and lists only nodes that get a ticket

**What to build:** Whoever calls the tooling-tree parser hands in the state of the nodes an agent can
judge, and nothing about the aggregation nodes. The parser works out from their leaves whether
`structural-scan` and a language's safety-net node are fulfilled, says per Track whether the Track is
fulfilled, and returns backlog and node lists that hold only nodes a ticket can be filed for. The Track
choice of a run reads "is Safety Net fulfilled?" from this output instead of judging it.

Spec: `../spec.md` (sections *The parser*, *Track choice*, *Testing Decisions*). Follow-up to ticket 03,
whose comments name the two behaviours this ticket changes. Built test-first, like ticket 03.

**Blocked by:** 03

**Status:** ready-for-agent

- [ ] The state of an aggregation node (a node others reach through `resolved` edges) is computed from
      its leaves; whatever is handed in for such a node is ignored, as for `git` and `onboarding-setup`
- [ ] A rejected leaf counts as decided for its aggregation node, the way a rejected recommended parent
      already releases its child
- [ ] The output states, per Track, whether the Track is fulfilled: every node of it that can get a
      ticket is fulfilled or rejected
- [ ] Each Track's backlog and node list hold only nodes a ticket can be filed for; recognition-only and
      aggregation nodes (`git`, `onboarding-setup`, the recognition gate, `structural-scan`, the
      safety-net node) are left out of both, and out of the flat `backlog` and `next`
- [ ] Each listed node carries search words fit for a tracker search: the node's name and its tool as
      short plain strings, without Markdown backticks and without explanatory prose; where a node's tool
      field is a sentence, the node's tree-doc entry is given a short tool name and the sentence moves to
      its Purpose
- [ ] Parser tests cover the computed aggregation state, the per-Track fulfilled flag and the filtered
      lists at the parser's existing interface; the parser's own test file is green
- [ ] No skill text other than the tree-doc entries named above is touched; what goes red outside the
      parser's tests is listed in a comment on ticket 09
