# 03: Parser without bookkeeping

**What to build:** Whoever calls the tooling-tree parser hands in which nodes are fulfilled and which are
rejected, and gets back, per Track, the nodes with their name and tool, the ordered backlog with blocked
nodes included, and the reason a node is withheld. The parser reads the tree and the target repository,
and no file the suite used to keep.

Spec: `../spec.md` (sections *The parser*, *Testing Decisions*). This is the one ticket built test-first.

**Blocked by:** None (can start immediately)

**Status:** ready-for-agent

- [ ] The parser takes the node state (fulfilled, rejected) as input; called without it, it treats every
      node as undecided rather than looking for a file
- [ ] The parser emits, per Track, each node's slug, name and tool; Track membership is derived from the
      edges as before
- [ ] No code path reads a bookkeeping document, a config file, a bookkeeping pointer or the old
      out-of-scope folder; the code deriving state from them is deleted
- [ ] A rejection's machine-readable blocker (minimum PHP version) is handed in with the rejected state,
      and the reversal finding is still reported when the target meets it
- [ ] The `onboarding-setup` node counts as fulfilled when the target's tracker file has a
      `## Refactoring operations` section
- [ ] Parser tests cover the handed-in state and the per-Track list at the parser's existing interface;
      tests of the removed derivation are deleted; the parser's own test file is green
