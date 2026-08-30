# PHPStan/Psalm mutual exclusion, and a new `required-any` edge for `psalm-taint-analysis`

> Closes the gap ADR-0018 and ticket 43 left open: `psalm` existed as a recognition-only node but wasn't a
> `php-structural-scan` resolved-leaf, so a Psalm-only target's `structural-scan` gate stayed permanently
> blocked. Also introduces a new node, `psalm-taint-analysis`, and the tree's first `required-any` edge.

Ticket 37 was filed during ticket 34's grilling, `ready-for-human`, flagging that its own
`tooling_tree.py` mechanics needed a dedicated design pass before implementation. This ADR is the record of
that pass (held 2026-08-30), together with a second, related idea raised in the same session (ticket 44).

## Decision — Part A: mutual exclusion (ticket 37)

`psalm` becomes a thirteenth `php-structural-scan` resolved-leaf, alongside `phpstan-level-10`. Whichever
static-analysis path a target commits to, the introducing action also records the other side's leaf as
out-of-scope — reusing the existing `docs/refactoring/out-of-scope/<node>.md` rejection convention, no new
rejection machinery:

- **PHPStan path:** `phpstan-level-0-baseline`'s introduce MR also commits `out-of-scope/psalm.md`.
- **Psalm path:** since `psalm` has `MR scope: none` (recognition-only, no tree-proposed MR to attach a
  write to), the first scan pass that recognizes it fulfilled writes `out-of-scope/phpstan-level-10.md` if
  not already present — housekeeping performed by the scanning agent, not a code-level write inside
  `tooling_tree.py` (which stays a pure read-only detector).

**Correction to the ticket's original wording, made during this session's grilling:** the ticket's "What to
build" text said `phpstan-level-0-baseline`'s Psalm-equivalence branch would be "removed/superseded."
Implemented literally, that means rejecting `phpstan-level-0-baseline` itself on the Psalm path — but
`rector-php-set` has it as a **required** parent, and a required-parent rejection permanently closes
everything beneath it. That would silently make the entire Rector family unreachable for every Psalm-only
target, a real regression with no prior demand for it. **Decision: keep the equivalence intact.**
`phpstan-level-0-baseline`'s fulfilment check keeps reading "PHPStan path OR `psalm` fulfilled" exactly as
ADR-0018 built it. Mutual exclusion targets only the two `php-structural-scan` leaves — `psalm` and
`phpstan-level-10` — never `phpstan-level-0-baseline` itself.

No `tooling_tree.py` code changes were needed for this part beyond the new `psalm` → `php-structural-scan`
resolved edge row in `php-tooling-tree.md`'s edge table — `load_tree()`/`_parse_edges()` already parse
`resolved` edges generically.

## Decision — Part B: `psalm-taint-analysis` (ticket 44)

A distinct idea raised in the same grilling session: Psalm's taint analysis (SQL-injection/XSS-class
detection) is a separate capability from its general static analysis, and should be adoptable regardless of
which general analyzer a target chose — without reopening the mutual exclusion above (installing
`vimeo/psalm` purely for taint scanning is not the same decision as adopting it as a competing general
analyzer).

This needed one new primitive: a **`required-any` edge** — unlike `required` (every parent must be
fulfilled), a node with `required-any` parents is proposed once *at least one* is fulfilled. Scoped
narrowly:

- `_VALID_EDGE_TYPES` gains `"required-any"`.
- `load_tree()` builds a new `required_any_parents` map, parsed from the edge table exactly like the other
  three edge types.
- `_is_unblocked()` additionally requires at least one `required_any_parents` entry fulfilled, when the
  node has any — combining with ordinary required parents via AND, and within the group via OR.

`psalm-taint-analysis`'s two `required-any` parents are `phpstan-level-4` and `psalm`. Its fulfilment check
mirrors `phpstan-level-0-baseline`'s ticket-34 CI-self-wiring shape: `vimeo/psalm` + committed `psalm.xml`
+ (once `ci-runner` is fulfilled) a CI job invoking `vendor/bin/psalm --taint-analysis`. It is **not** a
`php-structural-scan` resolved-leaf — a security-scan addition, orthogonal to that aggregation's
structural-quality scope.

**Known cosmetic wrinkle, accepted rather than engineered around:** adopting `psalm-taint-analysis` on the
PHPStan path installs `vimeo/psalm` + `psalm.xml`, which makes the `psalm` node's own live-detected
`fulfilled` flag incidentally read `true` too — even though a prior `out-of-scope/psalm.md`
mutual-exclusion rejection (Part A) is still in force. This is harmless: rejection checks
(`_rejected_nodes()`/`_is_effectively_rejected()`) read the out-of-scope file directly, independent of the
detected-fulfilled flag. Not fixed by disambiguating the `psalm` node's detection further — the CI
invocation string is already what actually distinguishes `psalm-taint-analysis`'s own fulfilment from
`psalm`'s, and adding detection complexity to `psalm` itself for a purely cosmetic readout wasn't judged
worth it.

## Considered Options

- **Implement the mutual exclusion by literally rejecting `phpstan-level-0-baseline` on the Psalm path**
  (the ticket's original wording). Rejected — see the Rector-family regression above.
- **A general "choice"/XOR edge type**, for mutual exclusion generally. Rejected: mutual exclusion is
  already fully expressible via the existing rejection convention (writing the sibling's out-of-scope
  file) — no new edge type needed for it. `CONTEXT.md`'s new **Choice** entry documents this as a
  convention, not a primitive.
- **A general "required-any"/OR primitive speculatively available tree-wide.** Rejected in favor of adding
  it only where a real need exists (`psalm-taint-analysis`) — same incremental-primitive discipline ADR-0016
  used for `recommended` edges.
- **Give `psalm-taint-analysis` a `required` (not `required-any`) parent of `static-code-analyzer`
  directly**, skipping the OR entirely (mirrors an option ADR-0018 rejected for a different node). Rejected
  for the same reason ADR-0018 rejected it: `static-code-analyzer` would need to compute "some analyzer
  adopted" as its own fulfilment, which the required-edge model doesn't support without new machinery —
  `required-any` is the smaller, more honest addition.

## Consequences

`php-tooling-tree.md` gains one new resolved edge (`psalm` → `php-structural-scan`), two new `required-any`
edges, mutual-exclusion MR-scope/housekeeping prose on `psalm`'s and `phpstan-level-0-baseline`'s entries,
a corrected *Equivalents* section, and a new `psalm-taint-analysis` node. `tooling_tree.py` gains the
`required-any` edge type end to end (`_VALID_EDGE_TYPES`, `load_tree()`, `_is_unblocked()`) and a
`psalm-taint-analysis` detection block in `detect_nodes()` — no other function needed special-casing, since
both `next_candidates()` and `roadmap()` already route every ordinary node through the shared
`_is_unblocked()` helper. `CONTEXT.md` gains **Required-any edge** and **Choice** vocabulary entries.
Fixtures needed one addition each: `php-clean` (PHPStan path) gained `out-of-scope/psalm.md`; `php-psalm`
(Psalm path) gained `out-of-scope/phpstan-level-10.md`, demonstrating the fix. `scripts/test_tooling_tree.py`
gained two new test classes (`PsalmMutualExclusionTests`, `PsalmTaintAnalysisTests`) plus a regression guard
(`test_p0_psalm_equivalence_still_unblocks_rector_family`) for the tension this ADR's Part A correction
addresses, and several existing "fully tooled" synthetic fixtures needed the same `out-of-scope/psalm.md`
addition as `php-clean`.
