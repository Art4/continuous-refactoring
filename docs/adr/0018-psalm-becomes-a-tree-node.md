# Psalm becomes its own tree node under a shared `static-code-analyzer` ancestor

> Amends [ADR-0008](0008-generic-tool-tree-and-structural-scan-gate.md)'s `phpstan-level-0-baseline` equivalents note: Psalm's inline "fulfils as an equivalent" branch is replaced by a sibling node, `psalm`, sharing a new required parent, `static-code-analyzer`, with `phpstan-level-0-baseline` — no change to what any project's tree state actually resolves to.

Before this ADR, `phpstan-level-0-baseline`'s own fulfilment check carried two branches: the canonical
PHPStan path, and a "Psalm path (equivalent)" that inlined Psalm's raw detection (`vimeo/psalm` dependency
plus a committed `psalm.xml`) directly inside that one node's `if`/`elif` chain. `php-tooling-tree.md`'s own
prose already flagged this as provisional — "a follow-up ticket giving Psalm its own node is the intended
place" to add anything further to that path (e.g. its own CI-gating check).

Ticket 43 extended the PHPStan level chain from `phpstan-level-1..3` to `phpstan-level-1..10`, moving the
chain's `resolved`-edge leaf from `phpstan-level-3` to `phpstan-level-10`. That made the buried equivalence
harder to read: `phpstan-level-0-baseline` now sits ten hops below the node that actually gates
`php-structural-scan`, and "Psalm fulfils this one intermediate node, which happens to also transitively
unlock the whole chain and the Rector family beneath it" is a lot to hold in one inline `if` branch. The
user asked directly, during the same round that supplied ticket 43's new node list, to promote Psalm to a
first-class node rather than defer that redesign to the follow-up ticket the prose had anticipated.

## Decision

Introduce two nodes, both owned by `php-tooling-tree.md`:

- **`static-code-analyzer`** — pure plumbing, required parent `composer`, no fulfilment check of its own
  beyond "`composer` is fulfilled." Same shape as `php-structural-scan`: no tool, no MR scope, never
  proposed. Exists purely so the tree's edge table shows the PHPStan/Psalm branch explicitly instead of it
  living only inside one node's fulfilment check.
- **`psalm`** — required parent `static-code-analyzer` (sibling of `phpstan-level-0-baseline`). Fulfilment
  check is the exact detection formerly inlined in `phpstan-level-0-baseline`'s own "Psalm path" branch,
  moved verbatim rather than duplicated. `MR scope: none` — recognition-only, never proposed as a new
  adoption by `next_candidates()`/`roadmap()`, the same fait-accompli shape Pest already gets for
  `phpunit`.

`phpstan-level-0-baseline`'s own fulfilment check keeps its two-branch shape — PHPStan path, or Psalm
path — but the Psalm branch now reads "the `psalm` node is fulfilled" instead of re-deriving the raw
detection. This is the one constraint that mattered throughout: **no behavior change**. A Psalm-only
project's `phpstan-level-0-baseline` still reads fulfilled, which still satisfies its two Rector-family
required parents (`rector-dead-code`/`rector-type-coverage`, and now `rector-php-set` — ticket 43) exactly
as before. The existing "level nodes don't apply when Psalm is the fulfiller" stop condition and the
"PHPStan is authoritative on co-presence" rule both carry over unchanged, just phrased against the `psalm`
node instead of an inline flag.

`static-code-analyzer` and `psalm` are both added to a new `_NEVER_PROPOSED` set in `tooling_tree.py`
(replacing three individual `node == "git"` checks in `next_candidates()`/`withheld_candidates()`/
`roadmap()`) — the ordinary-node counterpart to `exposed_resolved_gate_nodes`'s aggregation-node carve-out
from ADR-0017. Both nodes are required-gated, not resolved-gated, so they needed a different mechanism than
that one; `git` moved into the same set for a single shared exclusion list instead of three separate
special cases plus this new one.

## Considered Options

- **Status quo — Psalm stays an inline equivalents branch.** Rejected: readable enough when
  `phpstan-level-0-baseline` was three hops from the leaf; a ten-level chain makes "this one intermediate
  node's equivalence transitively unlocks everything below it" too much to track without its own node.
- **Defer to a later, separate ticket** (the shape `php-tooling-tree.md`'s own prose had anticipated).
  Rejected by the user directly: doing it in the same pass as the level-chain extension that motivated it
  avoids a window where the doc's "Equivalents" section and the new, much longer chain are visibly out of
  sync with each other.
- **Make `psalm` actively proposable** (the engine could suggest "adopt Psalm" as an alternative to
  introducing PHPStan on a bare project). Rejected: a genuine behavior change with no prior demand for it —
  today's tool has only ever proposed the PHPStan path and recognized Psalm when already present, the same
  shape Pest gets for `phpunit`; nothing asked for symmetric proposability, and it would need new
  either/or-candidate machinery the engine doesn't have.
- **Give `rector-dead-code`/`rector-type-coverage`/the new Rector family a required parent of
  `static-code-analyzer` instead of `phpstan-level-0-baseline`** (skip the intermediate node entirely once
  *some* analyzer is chosen). Rejected: would have required `static-code-analyzer` to compute "some
  analyzer adopted" as its own fulfilment — a parent whose fulfilment depends on its own children's state,
  which the required-edge model doesn't support without new machinery. Keeping `phpstan-level-0-baseline`'s
  existing equivalence-driven fulfilment as the thing the Rector family reads (unchanged) reuses what
  already works.
- **Accepted: `psalm` and `static-code-analyzer` as new sibling/ancestor nodes, equivalence logic
  refactored (not replaced) to read the new node's state.**

## Consequences

`php-tooling-tree.md` gains two new nodes with no MR scope of their own; the "Equivalents" section shrinks
to state the relationship rather than the raw detection, cross-referencing `psalm`'s own entry.
`tooling_tree.py` gains a `_NEVER_PROPOSED` module constant (four call sites now read it instead of three
ad hoc `git` checks) and moves Psalm's detection into its own `set_node()` call, read back by
`phpstan-level-0-baseline`'s check rather than re-derived. Every fixture's `detected` output is unaffected
by this specific change in isolation (confirmed against `php-psalm`'s regenerated roadmap alongside ticket
43's level-chain/Rector-family additions) — a Psalm-only project still resolves `phpstan-level-0-baseline`,
and through it the whole Rector family via `rector-php-set`, without ever adopting real PHPStan. If a
second language specialization later needs its own static-analyzer choice, it follows the same shape: one
`<language>-static-code-analyzer` plumbing node, its own equivalent-tool sibling nodes underneath.
