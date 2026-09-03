# 47 — MR outlook: fan-out diagram of newly-unblocked nodes

**Type:** grilling + task

**What to build:** Extend the merge-request outlook (`opening-a-merge-request.md`, ADR-0009) with a
Mermaid diagram alongside the existing plain sentence, showing every node the just-landed candidate
directly unblocks — not only the single top-priority pick the sentence names.

**Blocked by:** 19 ✓ done — Merge-request outlook and typed rationale (this ticket is its
diagram-shaped continuation, split out once the type-enum half closed with "none")

**Status:** done

Settled design (`/grill-me zu Ticket 19`, continued):

- [x] Content: fan-out — every node **directly** unblocked by the just-landed node, not a
      multi-step roadmap chain (a roadmap simulates picks `refactor-prioritize` hasn't made yet)
- [x] Relation to the sentence: supplements it, never replaces it — the sentence is the only part
      still legible in a terminal (`gh pr view`), a mailer, or anywhere else that doesn't render
      Mermaid
- [x] Computation: a direct tree-walk over the edge table, not a full before/after diff of
      `next_candidates()` — a pass delivers exactly one candidate per MR, so the walk answers the
      same question for a fraction of the cost
- [x] Threshold: diagram only when **2 or more** nodes are newly unblocked; 0 or 1 → sentence only
- [x] Node labels: the human-readable **Name**, not the slug (ADR-0009's plain-language principle)
- [x] Edge labels: `required`/`recommended`/`required-any`, same notation as the tree docs
- [x] Fallback: no diagram when `python3` isn't available — `tree-walk-prompt.md`'s manual path
      stays sentence-only, not extended

Implementation notes (correctness, not grilled — technical requirements of the design above):

- A direct child that's never itself a real candidate (`_NEVER_PROPOSED` for structural/plumbing
  reasons — `static-code-analyzer`; or a resolved-gated aggregation node that isn't itself exposed
  — `php-structural-scan`) is walked *through* to its own children instead of being reported, the
  same treatment `next_candidates()` already gives these nodes. The walk only continues past such a
  node while it's actually fulfilled/resolved right now.
- "Newly" unblocked excludes a `required-any` child already reachable via another already-fulfilled
  sibling parent (it was reachable before this candidate too) — a counterfactual check
  (`landed_node`'s own fulfilled flag forced back to `False`), not a hand-enumerated special case.
  `phpstan-level-0`'s Psalm-equivalence branch (`detect_nodes()`) needed one extra cascade: when
  `landed_node` is `psalm`, `phpstan-level-0`'s counterfactual flag is forced unfulfilled too, since
  `detect_nodes()`'s `if`/`elif` shortcut makes it impossible to tell whether the real, independent
  PHPStan check would also have passed. The safe direction to be wrong in is one extra diagram
  entry, never a silently missing one.

## Comments

> **2026-09-03:** Grilled as a continuation of ticket 19's `/grill-me` session, then implemented
> directly in the same change: `skills/refactor-scan/references/tooling_tree.py`
> (`directly_unblocked_children()`, `--unblocked-by` CLI flag),
> `scripts/test_tooling_tree.py` (new coverage: multi-child fan-out, both required-any directions,
> the resolved-gate walk-through to `structural-scan`), and
> `skills/continuous-refactoring/references/opening-a-merge-request.md` (the diagram step). Recorded
> as `docs/adr/0027-mr-outlook-diagram-of-unblocked-nodes.md`, amending ADR-0009.
