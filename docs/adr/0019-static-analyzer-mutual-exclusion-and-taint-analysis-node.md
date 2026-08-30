# PHPStan/Psalm mutual exclusion, and a new `required-any` edge for `psalm-taint-analysis`/`rector-php-set`

> Closes the gap ADR-0018 and ticket 43 left open: `psalm` existed as a recognition-only node but wasn't a
> `php-structural-scan` resolved-leaf, so a Psalm-only target's `structural-scan` gate stayed permanently
> blocked. Also introduces a new node, `psalm-taint-analysis` (itself a `php-structural-scan` resolved-leaf
> too — see Part C), and the tree's first `required-any` edges.

Ticket 37 was filed during ticket 34's grilling, `ready-for-human`, flagging that its own
`tooling_tree.py` mechanics needed a dedicated design pass before implementation. This ADR is the record of
that pass (held 2026-08-30), together with a second, related idea raised in the same session (ticket 44),
and a same-day follow-up correction round (Part C) found while reviewing the result before merge.

## Decision — Part A: mutual exclusion (ticket 37)

*(Superseded in one respect by Part D below, found the same day before merge: `psalm` does **not** become
a resolved-leaf after all — a dedicated leaf for it turned out to be redundant. The rest of this section —
the PHPStan-path/Psalm-path asymmetry, the correction on `phpstan-level-0-baseline`'s equivalence — still
stands; only the "PHPStan path... commits `out-of-scope/psalm.md`" bullet below is dropped. See Part D.)*

Originally: `psalm` becomes a thirteenth `php-structural-scan` resolved-leaf, alongside `phpstan-level-10`.
Whichever static-analysis path a target commits to, the introducing action also records the other side's
leaf as out-of-scope — reusing the existing `docs/refactoring/out-of-scope/<node>.md` rejection convention,
no new rejection machinery:

- ~~**PHPStan path:** `phpstan-level-0-baseline`'s introduce MR also commits `out-of-scope/psalm.md`.~~
  Dropped in Part D — no longer needed once `psalm` isn't a leaf.
- **Psalm path:** since `psalm` has `MR scope: none` (recognition-only, no tree-proposed MR to attach a
  write to), the first scan pass that recognizes it fulfilled writes `out-of-scope/phpstan-level-10.md` if
  not already present — housekeeping performed by the scanning agent, not a code-level write inside
  `tooling_tree.py` (which stays a pure read-only detector). **Still current** — this is the part that
  actually fixes the bug (see Part D).

**Correction to the ticket's original wording, made during this session's grilling:** the ticket's "What to
build" text said `phpstan-level-0-baseline`'s Psalm-equivalence branch would be "removed/superseded."
Implemented literally, that means rejecting `phpstan-level-0-baseline` itself on the Psalm path — but
`rector-php-set` has it as a **required** parent, and a required-parent rejection permanently closes
everything beneath it. That would silently make the entire Rector family unreachable for every Psalm-only
target, a real regression with no prior demand for it. **Decision: keep the equivalence intact.**
`phpstan-level-0-baseline`'s fulfilment check keeps reading "PHPStan path OR `psalm` fulfilled" exactly as
ADR-0018 built it. Mutual exclusion targets `phpstan-level-10` (originally: `phpstan-level-10` and `psalm`
together — see Part D) — never `phpstan-level-0-baseline` itself.

No `tooling_tree.py` code changes were needed for this part beyond the (later dropped, Part D) `psalm` →
`php-structural-scan` resolved edge row in `php-tooling-tree.md`'s edge table — `load_tree()`/`_parse_edges()` already parse
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
+ (once `ci-runner` is fulfilled) a CI job invoking `vendor/bin/psalm --taint-analysis`. It **is** a
`php-structural-scan` resolved-leaf — see Part C below (corrected from this ADR's original "not a
resolved-leaf" claim, found wrong the same session it was written).

**Known cosmetic wrinkle, accepted rather than engineered around:** adopting `psalm-taint-analysis` on the
PHPStan path installs `vimeo/psalm` + `psalm.xml`, which makes the `psalm` node's own live-detected
`fulfilled` flag incidentally read `true` too. Not fixed by disambiguating the `psalm` node's detection
further — the CI invocation string is already what actually distinguishes `psalm-taint-analysis`'s own
fulfilment from `psalm`'s, and adding detection complexity to `psalm` itself for a purely cosmetic readout
wasn't judged worth it. *(This paragraph originally explained why an `out-of-scope/psalm.md`
mutual-exclusion rejection stays authoritative regardless — moot after Part D, which established that no
such file is ever written in the first place.)*

## Decision — Part C: follow-up correction (same session)

Discussing the result surfaced two further corrections before this ADR's underlying PR was merged — both
edge-table/prose-only, no `tooling_tree.py` code change needed beyond what Part B already built:

- **`psalm-taint-analysis` is a `php-structural-scan` resolved-leaf after all** (the fourteenth at the time
  this was written — back to thirteen after Part D drops `psalm`'s own leaf). Part B's original "not a
  resolved-leaf — security-scan addition, orthogonal to
  structural-quality scope" reasoning didn't survive comparison to `composer-audit`, already one of these
  leaves and itself a pure security tool (dependency-vulnerability scanning). The actual criterion
  (`tooling-tree.md`'s `structural-scan` node: "hold structural refactoring back until deterministic
  tooling has had its say") is about producing deterministic findings that could collide with agent-driven
  structural work, not "structural vs. security" — taint analysis qualifies exactly like PHPStan levels or
  Rector sets do.
- **`rector-php-set` reads its analyzer-chosen gate directly via `required-any(phpstan-level-0-baseline,
  psalm)`**, replacing its previous single `required: phpstan-level-0-baseline` parent — making the OR
  relationship explicit at the tree-edge level rather than relying on it being implicit inside
  `phpstan-level-0-baseline`'s own Psalm-equivalence fulfilment check (Part A). `rector-dead-code`'s and
  `rector-type-coverage`'s own **direct** `required: phpstan-level-0-baseline` edges are removed outright
  (not replaced) — both already have `rector-php-set` as a required parent, which now carries the same
  gate transitively. This consolidates the "static analyzer chosen" check into one place instead of it
  being duplicated across three nodes, and makes the Rector family's Psalm-path reachability independent
  of `phpstan-level-0-baseline`'s own fulfilled state entirely (previously the equivalence was the *only*
  path; now `psalm` unblocks `rector-php-set` directly too).

## Decision — Part D: drop `psalm`'s resolved-leaf (same day, before merge)

Reviewing Part A/C's result together surfaced that `psalm`'s own `php-structural-scan` resolved-leaf is
redundant. The actual bug (`phpstan-level-10` never resolving on the Psalm path) is already fixed by the
mutual-exclusion housekeeping on `psalm`'s own node entry, which writes `out-of-scope/phpstan-level-10.md`
— that alone is sufficient on both paths:

- **PHPStan path:** `phpstan-level-10` resolves normally (fulfilled via the level chain, or rejected if
  capped, e.g. `php-clean`) — never depended on `psalm` at all.
- **Psalm path:** `phpstan-level-10` resolves via the existing rejection housekeeping — never depended on
  `psalm` being its own leaf either.

The only thing `psalm`'s leaf membership ever caused was extra ceremony: on the PHPStan path, `psalm`
itself is never naturally fulfilled, so making it a leaf meant something had to write
`out-of-scope/psalm.md` just to resolve *that* leaf — a rejection whose only purpose was to satisfy a leaf
that didn't need to exist. **Decision: remove the `psalm` → `php-structural-scan` resolved edge**, and with
it the PHPStan-path `out-of-scope/psalm.md` write (Part A's now-struck bullet above). The Psalm-path write
to `out-of-scope/phpstan-level-10.md` stays — that one is load-bearing.

This doesn't undermine ticket 37's original "first-class, humanly-inspectable decision" motivation (Part
A's *Why* #1) — that's already satisfied by the tree structure itself (`static-code-analyzer` with
`phpstan-level-0-baseline`/`psalm` as explicit siblings, built in ADR-0018/ticket 43), not by the
resolved-edge/rejection mechanism, which was only ever motivated by the `phpstan-level-10` gating bug
(*Why* #2).

**`psalm-taint-analysis`'s "Co-presence" bullet needed a rewrite, not just a deletion:** it previously
explained why its incidental flip of `psalm`'s live-detected `fulfilled` flag (installing
`vimeo/psalm`+`psalm.xml` on the PHPStan path) was harmless *because* a prior `out-of-scope/psalm.md`
rejection stayed authoritative. With that file never written, the bullet now explains instead that nothing
depends on `psalm.fulfilled` being `false` on the PHPStan path any more — not `rector-php-set`'s
`required-any` gate (already satisfied via `phpstan-level-0-baseline` there regardless), not any
resolved-leaf (`psalm` isn't one).

## Decision — Part E: `rector-phpunit-set` requires `phpunit` (same review pass)

Unrelated to Parts A–D, raised in the same review: `rector-phpunit-set` (Rector's PHPUnit-modernization
rule set) had only `rector-php-set` as a required parent — no edge to `phpunit` at all, unlike every other
tool-specific Rector node's pattern of requiring the tool it rewrites. Added `phpunit` as a second required
parent (plain `required`, not `required-any` — no OR semantics needed here). No `tooling_tree.py` changes
needed; a plain `required` edge is parsed generically like every other one.

## Decision — Part F: Rector family restructured into two entry points + sibling ordering (next review pass)

Requested directly: `rector-type-coverage` and `rector-phpunit-set` lose their direct `required:
rector-php-set` edge; `rector-dead-code`, `rector-early-return`, `rector-code-quality` keep it, remaining
the family's three entry points. Three new `recommended` edges take over instead: `rector-dead-code` →
`rector-type-coverage`, `rector-early-return` → `rector-type-coverage` (two recommended parents — same
"gate waits on every recommended parent, not just one" shape `rector-type-coverage` already had for
`php-cs-fixer`/`phpstan-level-3`), and `rector-code-quality` → `rector-phpunit-set`.

**Real consequence, not glossed over:** `rector-type-coverage` now has **no required parent at all** tying
it to "a static analyzer was chosen" — only recommended parents, which need only be *decided*, and a
rejected recommended parent still releases its child (standing behavior throughout this tree). In
principle a human could pre-reject `rector-dead-code`/`rector-early-return` on a bare project and have
`rector-type-coverage` become proposable with `rector-php-set` never fulfilled at all. This isn't a new
category of gap — nothing in this tree validates that a rejected node was ever reachable first — but it is
a real, deliberate loosening for these two specific nodes, confirmed with the user before implementing
(unlike the parallel "drop `php-cs-fixer`/`phpunit`'s `php-structural-scan` leaves" request raised in the
same conversation, which was withdrawn once the equivalent analysis showed it wasn't a safe no-op).

Also required correcting two paragraphs elsewhere in `php-tooling-tree.md` that had (accurately, at the
time) described `rector-type-coverage` as reading `rector-php-set`'s `required-any` gate transitively — no
longer true after this restructuring; both were reworded to name the three remaining transitive readers
(`rector-dead-code`/`rector-code-quality`/`rector-early-return`) and state plainly that
`rector-type-coverage`/`rector-phpunit-set` are not among them.

No `tooling_tree.py` changes needed — plain `recommended` edges, parsed generically; `_undecided_recommended_parents()`
already handled multiple recommended parents on one node before this change (`rector-type-coverage`'s
existing `php-cs-fixer`/`phpstan-level-3` pair). Fixture fallout was real, not cosmetic: four
`expected/roadmap.json` snapshots (`php-empty`, `php-p0-nonempty`, `php-psalm`,
`php-project-with-candidates`) needed regenerating — `rector-phpunit-set` (now gated by `phpunit` alone)
and `rector-type-coverage` reach the 10-step roadmap simulation earlier/differently than before, a genuine
ordering change, not drift. `scripts/test_tooling_tree.py`'s `RecommendedGateTests` fixture
(`_p0_fulfilled_files()`) needed two of its dependent tests extended (decide `rector-dead-code`/
`rector-early-return` where a test needs `rector-type-coverage` reachable) rather than loosened.

## Considered Options

- **Also drop `php-cs-fixer`/`phpunit`'s direct `php-structural-scan` resolved edges** (Part F, requested
  alongside the Rector restructuring). Rejected once analyzed and reported back: unlike the redundant edges
  dropped in Part D, nothing else in the tree guarantees these two get *decided* before `structural-scan`
  opens if their direct leaf status is removed — a real gate relaxation, not a no-op. Withdrawn once this
  was surfaced.
- **Keep the three new Rector edges (`rector-dead-code`/`rector-early-return` → `rector-type-coverage`,
  `rector-code-quality` → `rector-phpunit-set`) additive, alongside the existing `required: rector-php-set`
  edges** (Reading A, considered before Part F). Rejected in favor of Reading B (replacement) — confirmed
  directly: the intent was to change what unblocks `rector-type-coverage`/`rector-phpunit-set`, not just add
  an ordering hint on top of unchanged gating.
- **Make the three new Rector edges `required-any` instead of `recommended`** (`rector-type-coverage` has
  two sources, a natural `required-any` fit). Considered, but `recommended` was chosen to match this
  family's existing ordering-edge precedent (`php-cs-fixer`'s recommended edges into the same five nodes)
  rather than introduce a second distinct gating shape for what reads as the same kind of "settle this
  first" relationship.
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
  `required-any` is the smaller, more honest addition. The same reasoning applies to `rector-php-set`
  (Part C) — it reads `required-any(phpstan-level-0-baseline, psalm)` directly rather than routing through
  `static-code-analyzer`, for the identical reason.
- **Leave `psalm-taint-analysis` off the `php-structural-scan` leaf set**, on a "security scan is
  orthogonal to structural quality" distinction (this ADR's original Part B decision). Rejected on review
  (Part C) — `composer-audit` already breaks that exact distinction, so it wasn't a real boundary.
- **Add `psalm-taint-analysis` and `rector-php-set`'s `required-any` group alongside their existing
  `required`/direct edges, instead of replacing them.** Rejected: functionally a no-op — a `required-any`
  group containing a node that's already a plain `required` parent is always trivially satisfied whenever
  the `required` check already passes, so it would add prose complexity for zero behavior change.
- **Keep `psalm` as its own `php-structural-scan` resolved-leaf** (this ADR's original Part A decision).
  Rejected on same-day review (Part D) — the only thing it ever bought was an extra, purely ceremonial
  `out-of-scope/psalm.md` write on the PHPStan path; `phpstan-level-10`'s own resolution (already required
  to fix the underlying bug) was sufficient on its own.

## Consequences (final state, after Parts A–F)

Part F's own consequences (Rector-family restructuring, fixture/test fallout) are detailed in that section
above rather than repeated here.

`php-tooling-tree.md`'s `php-structural-scan` gains one new resolved-leaf, net: `psalm-taint-analysis`
(thirteen leaves total, up from the original twelve — `psalm` was added in Part A and removed again in
Part D, a net wash on leaf count but not on the surrounding prose, which records both). `rector-php-set`
gains a `required-any(phpstan-level-0-baseline, psalm)` gate, replacing its old single `required:
phpstan-level-0-baseline` parent; `rector-dead-code`/`rector-type-coverage` lose their own now-redundant
direct `required: phpstan-level-0-baseline` edges (they read the gate transitively via `rector-php-set`
instead); `psalm-taint-analysis` gains `required-any(phpstan-level-4, psalm)`; `rector-phpunit-set` gains a
plain `required: phpunit` parent (Part E). `psalm`'s own node entry keeps
its mutual-exclusion housekeeping bullet (writes `out-of-scope/phpstan-level-10.md` on the Psalm path —
still the actual bug fix); `phpstan-level-0-baseline` loses the PHPStan-path write it briefly had.

`tooling_tree.py` gains the `required-any` edge type end to end (`_VALID_EDGE_TYPES`, `load_tree()`,
`_is_unblocked()`) and a `psalm-taint-analysis` detection block in `detect_nodes()` — no other function
needed special-casing, since both `next_candidates()` and `roadmap()` already route every ordinary node
through the shared `_is_unblocked()` helper, and `resolved_parents`/`required_parents`/
`required_any_parents` are all parsed generically from the edge table (no node name hardcoded in the
gating logic itself — every edge-table-only change across Parts C–E needed zero further Python changes).

`CONTEXT.md` gains **Required-any edge** and **Choice** vocabulary entries. Fixtures: `php-clean` (PHPStan
path) needs only `out-of-scope/psalm-taint-analysis.md` (its earlier `out-of-scope/psalm.md`, added for
Part A, was deleted again in Part D); `php-psalm` (Psalm path) needs `out-of-scope/phpstan-level-10.md`,
demonstrating the actual fix, and no change for `psalm-taint-analysis` (reads fulfilled there naturally —
same `vimeo/psalm`/`psalm.xml` signal as the `psalm` node, no CI to gate the taint-specific check on).
`scripts/test_tooling_tree.py` gained `PsalmMutualExclusionTests` (phpstan-level-10 resolution, not
psalm's — Part D removed the psalm-leaf-specific test), `PsalmTaintAnalysisTests`, `rector-php-set`
`required-any` coverage, and regression guards for the Rector-family reachability tension Part A's
correction addresses; several existing "fully tooled" synthetic fixtures need
`out-of-scope/psalm-taint-analysis.md` but not `out-of-scope/psalm.md`.
