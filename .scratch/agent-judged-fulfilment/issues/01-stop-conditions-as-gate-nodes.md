# 01: Stop-conditions become recognition-only gate nodes

Spec: `agent-judged-fulfilment`.

**What to build:** The three propose-time stop conditions that today live as hidden flags inside the graph logic become ordinary tooling-tree structure. A project with no real (non-platform) dependency gets no audit node proposed, a non-empty PHPStan baseline stops the level chain, and Psalm as the project's analyzer keeps PHPStan level nodes out. Each becomes one recognition-only node, modeled on the existing `is-php-project` gate (never proposed, only a required parent), with a Purpose, a Fulfilment check in prose, and required edges to the nodes it gates. What gets proposed on any target stays exactly as it is today; only where the rule lives changes.

**Blocked by:** None (can start immediately).

**Status:** ready-for-agent

- [ ] Three gate nodes exist in the PHP tree: one meaning "the project has a real dependency" gating the audit node, one meaning "the current PHPStan baseline is empty" gating every PHPStan level node, one meaning "PHPStan, not Psalm, is the project's analyzer" gating the first level above zero.
- [ ] Each gate node has a Purpose and a Fulfilment check written as prose in the tree docs, is never proposed and never appears as a candidate.
- [ ] The deterministic parser derives each gate node's state from the same repo facts it uses today, and the graph logic (proposable, withheld, outlook views) has no special-case branch left for these three situations.
- [ ] Existing fixtures and tests covering "no real dependency", "non-empty baseline" and "Psalm project" produce the same proposals as before; a Psalm project still resolves the level chain through its recorded mutual-exclusion rejection.
- [ ] The baseline gate is a recurring state, not a one-way delivery. It is verified against permanent-gating and recommended-parent logic so that a temporarily closed gate never wrongly closes or withholds other nodes; any adjustment needed is covered by a test.
