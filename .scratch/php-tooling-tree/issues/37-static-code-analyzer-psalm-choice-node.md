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

**Status:** implemented (2026-08-30)

Already settled (confirmed during ticket 34's grilling — treat as decided, not open):

- [x] Mutual exclusion via auto-written `out-of-scope/` entries, no new rejection mechanism.
- [x] ~~`psalm` becomes an additional resolved-leaf (feeding `php-structural-scan`, per ticket 43's
  aggregation-node shape) alongside `phpstan-level-10` (was `phpstan-level-3`).~~ **Reversed (follow-up
  correction, before merge): built this way initially, then found redundant and dropped — see the dated
  comment below. `phpstan-level-10`'s own mutual-exclusion rejection was always the load-bearing part;
  `psalm` never needed a leaf of its own on top of it.**
- [x] A Psalm strictness ratchet (mirroring `phpstan-level-1..10`, via Psalm's `errorLevel`) is explicitly
  **out of scope** for this ticket — noted as a possible third follow-up ticket, not committed to.

Resolved during this session's dedicated grilling (2026-08-30):

- [x] `psalm`'s own node does **not** get ticket-34-style CI-gating self-wiring as part of this ticket —
  left as-is (deferred question, still open for a future ticket if ever needed).
- [x] Exact Fulfilment-check/MR-scope prose written for `static-code-analyzer`, `psalm`, and
  `phpstan-level-0-baseline`'s mutual-exclusion additions — see `php-tooling-tree.md`.
- [x] `tooling_tree.py`: **no new detection code was needed for the mutual exclusion itself** — the
  out-of-scope writes are documented MR-scope/housekeeping behavior (performed by whichever MR or scan
  pass makes the choice real), not new parser code; the parser only needed the new `psalm` resolved-edge
  row (parsed generically, `load_tree()`/`_parse_edges()`, no code change) and stayed a pure read-only
  detector.
- [x] **Important correction to this ticket's own "What to build" wording:** "phpstan-level-0-baseline's
  current Psalm-equivalence branch is removed/superseded" (above) is **not** implemented literally — doing
  so would reject `phpstan-level-0-baseline` itself on the Psalm path, and since `rector-php-set` (and
  transitively the rest of the Rector family) has it as a **required** parent, that would permanently close
  the entire Rector family for every Psalm-only target (a required-parent rejection closes everything
  beneath it) — a real regression, not just a wording issue. The equivalence behavior is kept exactly as
  ADR-0018 built it; mutual exclusion targets `psalm` and `phpstan-level-10` (the two `php-structural-scan`
  leaves) instead. See `php-tooling-tree.md`'s `phpstan` equivalents section for the corrected prose.
- [x] A related but distinct idea raised in the same session — Psalm's taint-analysis capability, unlocked
  regardless of which general analyzer was chosen — was filed and implemented separately as
  [ticket 44](../../tooling-tree/issues/44-psalm-taint-analysis-node.md), since it needed its own new tree
  primitive (`required-any` edges) and is a new capability, not part of this ticket's mutual-exclusion fix.

## Comments

> **2026-08-30:** Filed as a follow-up from ticket 34's `/grill-me` session (in German) — orthogonal to
> that ticket's CI-wiring concern (this changes *how* PHPStan/Psalm get introduced in the first place, not
> whether either is enforced in CI once adopted), so kept out of ticket 34's PR rather than folded in.
> See `.scratch/php-tooling-tree/issues/34-ci-quality-job-wiring.md`'s comments for the full grilling
> transcript context this ticket was extracted from.

> **2026-08-30 (later):** Dedicated grilling session held as this ticket itself required (see *Blocked by*
> above). User arrived with their own idea for "running PHPStan and Psalm in parallel" — turned out, after
> discussion, to mean two separable things: (1) this ticket's mutual exclusion should stay as originally
> scoped (general analyzer choice remains exclusive), and (2) a genuinely new, previously-undiscussed third
> capability — Psalm's taint analysis, adoptable regardless of the chosen general-analyzer path — which was
> filed as ticket 44 and implemented alongside this one. Also caught and fixed a real tension in this
> ticket's own "What to build" text (the equivalence-removal wording — see the resolved checklist above)
> before implementing, rather than after. Implemented via direct edits in the same session
> (`php-tooling-tree.md`, `tooling_tree.py`, fixtures, tests) — not via `/implement`.

> **2026-08-30 (follow-up correction, before merge):** Discussing PR #28's result surfaced a second
> refinement, this time to how the Rector family reads the mutual exclusion's static-analyzer gate.
> Previously `rector-dead-code`/`rector-type-coverage`/`rector-php-set` each carried a direct
> `required: phpstan-level-0-baseline` edge, relying on that node's own Psalm-equivalence fulfilment check
> to implicitly cover the Psalm path too. Reworked so `rector-php-set` reads
> `required-any(phpstan-level-0-baseline, psalm)` directly instead — the OR relationship explicit at the
> edge level, not hidden inside another node's fulfilment check — and `rector-dead-code`/
> `rector-type-coverage`'s own direct edges to `phpstan-level-0-baseline` were dropped outright (not
> replaced) as redundant, since both already require `rector-php-set`, which now carries the gate
> transitively. See [ticket 44](../../tooling-tree/issues/44-psalm-taint-analysis-node.md)'s own comment for
> the paired correction (`psalm-taint-analysis` becoming a `php-structural-scan` resolved-leaf) found in the
> same conversation. Both recorded together in ADR-0019's new Part C.

> **2026-08-30 (second follow-up correction, before merge):** The user asked directly whether `psalm`'s
> `php-structural-scan` resolved edge could be dropped. On review: yes — the actual bug this ticket fixes
> (a Psalm-only target never resolving `phpstan-level-10`) is already fixed by the mutual-exclusion
> housekeeping on `psalm`'s own node entry (writes `out-of-scope/phpstan-level-10.md`); giving `psalm` its
> own leaf on top of that only ever bought an extra, purely ceremonial `out-of-scope/psalm.md` write on the
> PHPStan path. Removed the `psalm` → `php-structural-scan` resolved edge entirely — verified safe on both
> paths (see ADR-0019 Part D). Doesn't undermine this ticket's original "first-class, humanly-inspectable
> decision" motivation, which was already satisfied by the `static-code-analyzer` tree structure itself
> (ADR-0018/ticket 43), not by the resolved-edge mechanism. Same conversation also added, unrelated:
> `rector-phpunit-set` now requires `phpunit` directly (a real gap — it previously only required
> `rector-php-set`, so nothing stopped PHPUnit-specific Rector rewrites being proposed before PHPUnit
> itself was adopted). Recorded in ADR-0019 Parts D and E.

> **2026-08-30 (third follow-up correction, before merge):** Two more requests in the same review pass.
> (1) Drop `php-cs-fixer`/`phpunit`'s direct `php-structural-scan` resolved edges too — analyzed and
> reported back that, unlike the edges dropped above, this one is **not** a safe no-op (nothing else in the
> tree guarantees either gets *decided* before `structural-scan` opens); withdrawn by the user once this was
> surfaced, no change made. (2) Restructure the Rector family: `rector-type-coverage`/`rector-phpunit-set`
> lose their direct `required: rector-php-set` edge, gated instead via new `recommended` edges from sibling
> Rector nodes (`rector-dead-code`/`rector-early-return` → `rector-type-coverage`, `rector-code-quality` →
> `rector-phpunit-set`) — confirmed as a deliberate replacement (not additive) after the shorthand request
> turned out genuinely ambiguous between two readings. Real, named consequence: `rector-type-coverage` now
> has no required tie to the static-analyzer choice at all, only decided-not-fulfilled recommended parents
> — confirmed as intended. Required regenerating four `expected/roadmap.json` fixture snapshots (a genuine
> roadmap-order change, not drift) and extending two `RecommendedGateTests` cases. Recorded in ADR-0019's
> new Part F.
