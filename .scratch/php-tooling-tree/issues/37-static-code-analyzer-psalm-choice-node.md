# 37 — `static-code-analyzer` choice node: PHPStan vs. Psalm as mutually-exclusive required children

> **2026-08-30 update (ticket 43):** `static-code-analyzer` and `psalm` now exist in
> `php-tooling-tree.md` — but as a narrower, non-conflicting restructuring than this ticket proposes:
> `psalm` is recognition-only (never proposed, `MR scope: none`), *not* a `structural-scan` resolved-leaf,
> and there is no mutual-exclusion auto-rejection. `phpstan-level-0-baseline`'s equivalence branch still
> exists, just reads the `psalm` node's state instead of re-deriving it inline (see
> [ADR-0018](../../../docs/adr/0018-psalm-becomes-a-tree-node.md)). The latent bug in *Why* point 2 below
> is confirmed **still open** — unchanged, just relocated from `phpstan-level-3` to `phpstan-level-10`
> (ticket 43 extended the level chain). This ticket's remaining scope going forward is narrower than
> originally filed: making `psalm` an additional resolved-leaf plus the mutual-exclusion auto-rejection —
> the `static-code-analyzer`/`psalm` nodes themselves no longer need building, only this restructuring on
> top of them.

**What to build:** Replace today's Psalm-as-equivalence-inside-`phpstan-level-0-baseline` approach with an
explicit choice node:

- New node `static-code-analyzer` — required parent: `composer`; recommended parent: `ci-runner`.
  Purpose: introduce a static code analyser. Default proposal is PHPStan; a human can change the choice to
  Psalm instead.
- `phpstan-level-0-baseline` and a new node `psalm` both become required children of
  `static-code-analyzer`. They are mutually exclusive: choosing one tool automatically writes a
  `docs/refactoring/out-of-scope/<node>.md` entry for the other, reusing the existing rejection convention
  (`_rejected_nodes()`) rather than inventing new rejection machinery.
- `psalm` is added as an additional `structural-scan` resolved-leaf alongside `phpstan-level-10` (ticket
  43 renumbered this from `phpstan-level-3` once the level chain was extended) — see *Why* below for the
  bug this fixes.
- `phpstan-level-0-baseline`'s current Psalm-equivalence branch (`psalm_fulfils_p0` in `detect_nodes()`,
  and the *Equivalents* section in `php-tooling-tree.md`) is removed/superseded by this restructuring.

**Why:** Two independent reasons, both surfaced while grilling ticket 34:

1. **The choice mechanism itself.** The current design treats Psalm as an implicit equivalence inside
   `phpstan-level-0-baseline`'s own fulfilment check — there's no first-class node representing "a static
   analyser was introduced", and no explicit mutual-exclusion concept in the tree at all yet
   (`CONTEXT.md`'s vocabulary has no "choice"/XOR primitive). Modeling PHPStan and Psalm as siblings under
   a shared `static-code-analyzer` parent makes the choice a first-class, humanly-inspectable decision
   instead of an implicit branch inside another node's fulfilment logic.
2. **A latent bug this fixes.** `phpstan-level-1..10`'s own doc already says level nodes "do not apply
   when Psalm is the fulfiller" (`php-tooling-tree.md`'s *Equivalents* section) — a Psalm-choosing target
   never fulfils any `phpstan-level-N` and is never auto-rejected there either. But `php-structural-scan`'s
   resolved-leaf set only includes `phpstan-level-10` (renumbered by ticket 43; was `phpstan-level-3`),
   not any Psalm-path node (`detect_nodes()`, `php-tooling-tree.md`'s edges table). Reconfirmed directly
   against ticket 43's `php-psalm` fixture: for a Psalm-only target, `php-structural-scan` (and so
   `structural-scan`) stays permanently blocked unless a human manually writes an out-of-scope entry for
   `phpstan-level-10` — a leaf the target was never going to fulfil in the first place. Adding `psalm` as
   its own resolved-leaf, with the mutual-exclusion auto-rejection above making the *un*chosen sibling
   count as resolved automatically, closes this for free.

**Blocked by:** none technically, but this needs its own dedicated `/grill-me` session before
implementation — the points below are already settled from ticket 34's grilling (carried over, not
re-open), but the node's exact Fulfilment-check/MR-scope prose (mirroring the detail level of
`php-tooling-tree.md`'s other nodes) still needs to be worked out.

**Priority:** medium — fixes a real (if narrow) structural-scan gap, not just a design preference.

**Status:** ready-for-human

Already settled (confirmed during ticket 34's grilling — treat as decided, not open):

- [x] Mutual exclusion via auto-written `out-of-scope/` entries, no new rejection mechanism.
- [x] `psalm` becomes an additional resolved-leaf (feeding `php-structural-scan`, per ticket 43's
  aggregation-node shape) alongside `phpstan-level-10` (was `phpstan-level-3`).
- [x] A Psalm strictness ratchet (mirroring `phpstan-level-1..10`, via Psalm's `errorLevel`) is explicitly
  **out of scope** for this ticket — noted as a possible third follow-up ticket, not committed to.

Still open (needs the dedicated grilling session):

- [ ] Does `psalm`'s own node need the same CI-gating self-wiring `phpunit`/`phpstan-level-0-baseline` got
  in ticket 34 (a CI job invoking `vendor/bin/psalm`, once `ci-runner` is fulfilled)? Raised during ticket
  34's grilling and deliberately deferred rather than decided either way — `phpstan-level-0-baseline`'s
  Psalm-equivalence branch was left un-CI-gated specifically because this restructuring was coming.
- [ ] Exact Fulfilment-check/MR-scope prose for `static-code-analyzer` and `psalm`, matching the detail
  level of this tree's other nodes (see `phpstan-level-0-baseline`'s own entry in `php-tooling-tree.md`
  for the shape to match).
- [ ] `tooling_tree.py` implementation: new detection functions, edges-table rows, diagram update, and the
  `detect_nodes()`/`next_candidates()`/`roadmap()` changes the new mutual-exclusion behaviour needs.

## Comments

> **2026-08-30:** Filed as a follow-up from ticket 34's `/grill-me` session (in German) — orthogonal to
> that ticket's CI-wiring concern (this changes *how* PHPStan/Psalm get introduced in the first place, not
> whether either is enforced in CI once adopted), so kept out of ticket 34's PR rather than folded in.
> See `.scratch/php-tooling-tree/issues/34-ci-quality-job-wiring.md`'s comments for the full grilling
> transcript context this ticket was extracted from.
