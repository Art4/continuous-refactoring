# A `resolved`-gate leaf counts as resolved when a required ancestor is rejected, not just when it's rejected itself

A real gap observed live while reviewer-loop-watching `Art4/legacy-todo` (ticket 53): the maintainer
rejected `phpstan-level-6` specifically to reach `structural-scan` sooner. `php-structural-scan`'s own
`resolved`-gate check (`_resolved_gate_status()`) correctly counted `phpstan-level-6` itself as
`rejected`, but its actual leaf — `phpstan-level-10` — still sat in `unresolved`, since nothing with
its own out-of-scope entry existed for it. Net effect: rejecting level 6 never moved
`structural-scan` any closer to unlocking, directly undercutting the reason for rejecting it at all.
Settled via a `/grill-me` session (ticket 53).

## Considered Options

- **Write an out-of-scope entry for every node down the chain** (`phpstan-level-7` through `-10`, not
  just `-6`). Rejected — explicitly ruled out by the maintainer: only the node actually rejected
  should ever carry that record; the chain above it closing is a consequence the tooling should
  derive, not something a human (or agent) should have to restate node by node.
- **New standalone helper duplicating the required-parent walk.** Started here, then dropped once a
  near-identical function turned up already in the file: `_is_effectively_rejected()` (used today for
  `recommended`-edge gating — "permanently rejected" vs. "not reached yet") already walks a node's
  `required_parents` chain recursively with a cycle guard, checking whether any ancestor is rejected.
  Reusing and extending it, rather than writing a second copy of the same walk, is the smaller, more
  consistent change.

## Decision

**Extend `_is_effectively_rejected()` with `required-any` handling** (it previously only walked plain
`required_parents`), mirroring the identical pattern already used by its sibling
`_is_permanently_gated()` for an unrelated gate condition: a `required-any` parent group only closes
this way once *every* option in it is (recursively) effectively rejected — rejecting a single option
must never close the child, since any of the others fulfilling it still would.

**Wire it into `_resolved_gate_status()`**: a leaf now counts as resolved when it's fulfilled,
directly rejected, or `_is_effectively_rejected()` (closed via a rejected required ancestor) —
replacing the previous bare `leaf in rejected` check. Generic over the whole function, so this applies
identically to `structural-scan` and `php-structural-scan` (or any future `resolved`-gated node) with
no per-node special-casing.

No distinction is surfaced anywhere between "rejected outright" and "closed via an ancestor's
rejection" — both simply count as resolved, the same way a direct rejection already did before this
change; the maintainer's own answer during grilling was that this nuance isn't worth tracking
separately.

## Consequences

Rejecting a single required-parent node now correctly cascades through `resolved`-gate checks the
same way it already did for ordinary `next_candidates()` proposability — closing the actual real gap
the maintainer's rejection was meant to produce. No new file/convention: `_rejected_nodes()` and the
one-file-per-rejected-node convention are unchanged; only the *reading* side (`_resolved_gate_status()`,
via the extended `_is_effectively_rejected()`) got smarter. `_is_effectively_rejected()`'s two other
existing call sites (`_is_decided()`, `_undecided_recommended_parents()`, both for `recommended`-edge
gating) pick up the `required-any` fix too as a side effect — a strict improvement there as well,
not a behavior change anyone asked to avoid.
