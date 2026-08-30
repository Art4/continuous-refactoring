# 44 — `psalm-taint-analysis` node: security taint scanning, unlocked from either analyzer path

**What to build:** A new PHP-tooling-tree node, `psalm-taint-analysis`, plus a new tree primitive it needs:

- **New edge type `required-any`** (`tooling_tree.py`): unlike a `required` edge (every parent must be
  fulfilled), a node with `required-any` parents is proposed once *at least one* of them is fulfilled.
  `_VALID_EDGE_TYPES` gains the value; `load_tree()` builds a new `required_any_parents` map from edges of
  that type, parsed straight from `php-tooling-tree.md`'s edge table like every other edge; `_is_unblocked()`
  checks it — ordinary required parents (if any) must still all be fulfilled (AND between the two edge
  types), but only one of the required-any group needs to be (OR within it). `CONTEXT.md` gains a
  **Required-any edge** vocabulary entry alongside required/recommended.
- **`psalm-taint-analysis`** node: required-any parents `phpstan-level-4`, `psalm` — proposed once either
  the PHPStan level chain reaches 4, or the target chose Psalm as its general analyzer, regardless of which.
  Fulfilment check: `vimeo/psalm` present + committed `psalm.xml`/`psalm.xml.dist` + (once `ci-runner` is
  fulfilled) a CI job invoking `vendor/bin/psalm --taint-analysis` (same ticket-34 CI-self-wiring shape as
  `phpstan-level-0-baseline`). Not a `php-structural-scan` resolved-leaf — a security-scan addition,
  orthogonal to that aggregation's structural-quality scope.

**Why:** Psalm ships two distinct capabilities under one binary — general static analysis (what the
`psalm` node, ticket 43, already recognizes) and taint analysis for security bugs (SQL injection, XSS,
similar tainted-data-flow issues). These are orthogonal: a target that chose PHPStan as its general
analyzer should still be able to adopt Psalm's taint scanning specifically, without that reopening the
PHPStan/Psalm mutual exclusion (ticket 37) — installing `vimeo/psalm` purely for taint checking is not the
same decision as adopting it as a competing general analyzer. The tree had no way to express "unlocked by
either of two alternative paths" before this ticket; `required-any` is scoped narrowly to this one node,
not a general-purpose primitive speculatively added elsewhere.

**Blocked by:** none technically. Filed and designed alongside ticket 37 (same grilling session, user's own
idea) — implemented in the same pass, but kept as its own ticket per this repo's one-ticket-per-decision
convention (see ticket 37 out of ticket 34 for the precedent).

**Priority:** medium — a genuinely new capability, not a bug fix (contrast ticket 37).

**Status:** implemented (2026-08-30, same session as ticket 37).

Already settled (this session's grilling, user-confirmed):

- [x] `required-any` (OR), not a general "choice"/XOR primitive — that's a different concept, already
  covered by ticket 37's mutual-exclusion mechanism (rejection-based, no new edge type).
- [x] Threshold is `phpstan-level-4` specifically (not level 0, not level 10).
- [x] Taint-analysis is its own node, independent of the `psalm` node's mutual-exclusion rejection status —
  adopting it on the PHPStan path does not reopen that rejection (see `psalm`'s own *Co-presence* bullet in
  `php-tooling-tree.md`).
- [x] Not a `php-structural-scan` resolved-leaf.

## Comments

> **2026-08-30:** Filed alongside ticket 37 — the user's own idea, raised while grilling that ticket
> ("wie ich PHPStan und Psalm parallel betreiben kann"). Clarified during grilling that this is not "run
> both as competing general analyzers" (which ticket 37's mutual exclusion still forbids) but "run Psalm's
> taint analysis alongside whichever general analyzer was chosen" — a third, previously undiscussed
> capability, not a relaxation of the mutual exclusion. Implemented together with ticket 37 in the same
> session/PR.
