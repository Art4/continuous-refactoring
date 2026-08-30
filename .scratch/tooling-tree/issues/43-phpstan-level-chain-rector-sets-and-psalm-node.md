# 43 — PHPStan level chain 4–10, deprecation rules, Rector set family, Psalm becomes its own node

**What to build:** Extend the PHP tooling tree (`skills/refactor-scan/references/php-tooling-tree.md`)
with 13 new nodes the user named directly, structured together with a required restructuring of the
existing PHPStan/Psalm equivalence:

- **PHPStan level chain 4–10** (7 nodes): a straight continuation of the existing `phpstan-level-1..3`
  chain, same rules throughout (predecessor fulfilled + empty baseline). `phpstan-level-10` replaces
  `phpstan-level-3` as the chain's `resolved`-edge leaf into `php-structural-scan`; levels 3–9 become
  ordinary required intermediate nodes (same shape levels 1–2 already had).
- **`phpstan-deprecation-rules`**: a new `resolved`-edge leaf, orthogonal to the level chain — required
  parent `phpstan-level-5` (decided directly with the user, not tied to the chain's top).
- **Rector set family**: `rector-php-set` (required parent `phpstan-level-0-baseline`, same as
  `rector-dead-code`/`rector-type-coverage`) becomes the shared required parent for three new sibling
  nodes — `rector-code-quality`, `rector-phpunit-set`, `rector-early-return` — each also getting
  `php-cs-fixer` as a recommended parent (same styling-order rationale as `rector-dead-code`'s own). All
  five (the two existing plus these three new ones) are new `resolved`-edge leaves. `rector-php-set` also
  becomes an additional required parent of the two *existing* leaves, `rector-dead-code` and
  `rector-type-coverage` — decided directly with the user, so all five Rector nodes share one adoption
  gate. `rector-php-set` itself gets no `php-cs-fixer` recommended parent (the one exception in the family
  — also decided directly with the user).
- **Psalm becomes a first-class node.** Today, `phpstan-level-0-baseline`'s own fulfilment check embeds a
  "Psalm path (equivalent)" branch — raw Psalm detection folded into one node's `if`/`elif` chain. This
  ticket promotes it to its own `psalm` node, sharing a new required parent, `static-code-analyzer`, with
  `phpstan-level-0-baseline` (`composer -> static-code-analyzer -> {phpstan-level-0-baseline, psalm}`).
  `static-code-analyzer` is pure plumbing (fulfilled automatically once `composer` is), same pattern as
  `php-structural-scan`. **No behavior change**: `phpstan-level-0-baseline`'s fulfilment check still reads
  as "PHPStan path OR psalm fulfilled" — same equivalence, now referencing the sibling node's computed
  state instead of duplicating the raw detection. `psalm` is recognition-only (never proposed as new
  adoption, `MR scope: none`) — same fait-accompli shape Pest already gets for `phpunit`. Both
  `static-code-analyzer` and `psalm` are added to a new `_NEVER_PROPOSED` set in `tooling_tree.py`
  (`next_candidates()`/`roadmap()`/`withheld_candidates()`), the ordinary-node counterpart to
  `exposed_resolved_gate_nodes`'s aggregation-node carve-out.

**Why:** the user asked to extend the PHP tree with a specific, self-chosen node list (levels 4–10,
deprecation rules, four Rector sets). Structuring it surfaced that a longer PHPStan chain makes the
existing Psalm equivalence — buried inside one node's fulfilment check — harder to reason about once
`phpstan-level-0-baseline` sits three hops below the actual resolved-leaf instead of being the leaf itself;
promoting Psalm to its own node under a shared `static-code-analyzer` ancestor was raised directly by the
user (not deferred to the "follow-up ticket" ticket 42's own notes had anticipated) specifically to keep
that relationship legible without changing what the tree actually decides for any project — verified via
the `php-psalm` fixture, which must keep unlocking `rector-dead-code`/`rector-type-coverage` without real
PHPStan, exactly as before this ticket.

**Priority:** medium — user-directed scope expansion, not a bug fix; no regression tolerance on the
Psalm-equivalence behavior (see Verification).

**Status:** done

- [x] `skills/refactor-scan/references/php-tooling-tree.md`: diagram + edges table + node prose for all 13
      new nodes; `phpstan-level-3 -> php-structural-scan` (resolved) removed, `phpstan-level-10 ->
      php-structural-scan` added; `phpstan-level-0-baseline`'s Psalm-path bullet now references the `psalm`
      node instead of embedding the raw check; `phpstan-level-1..3` node section renamed/extended to
      `phpstan-level-1` through `phpstan-level-10`; `php-structural-scan`'s own Fulfilment-check/Purpose
      prose updated from seven to twelve leaves; `composer-audit`'s Stop-conditions leaf list updated to
      match.
- [x] `skills/refactor-scan/references/tooling_tree.py`: `static-code-analyzer` (trivial pass-through) and
      `psalm` (moved Psalm detection) added to `detect_nodes()`; `phpstan-level-0-baseline`'s equivalence
      now reads the `psalm` node's computed state; `phpstan-level-1..3` loop generalized to `1..10`
      (`_PHPSTAN_LEVEL_NODES` module constant); `phpstan-deprecation-rules` detection added
      (`phpstan/phpstan-deprecation-rules` dep presence); `rector-php-set`/`rector-code-quality`/
      `rector-phpunit-set`/`rector-early-return` detection added (substring-matched, same style as
      `rector-dead-code`/`rector-type-coverage`); new module-level `_NEVER_PROPOSED = {"git",
      "static-code-analyzer", "psalm"}` set, replacing the three individual `node == "git"` skip checks in
      `next_candidates()`/`withheld_candidates()`/`roadmap()`; `roadmap()`'s per-level empty-baseline gate
      and open-chain filler generalized from the `phpstan-level-1..3` hardcoded tuple/dict to
      `_PHPSTAN_LEVEL_NODES`/level-number arithmetic, filler now starts at `phpstan-level-11` (was `-4`).
      `_composer_audit_extra_gate()` needed no change — it already reads `php-structural-scan`'s
      resolved-parents from the edge table, so the new leaf set applies automatically.
- [x] `skills/refactor-scan/references/tree-walk-prompt.md`: "seven resolved-parents" → "twelve"; the
      aggregation-node carve-out's self-reference by line number replaced with a stable cross-reference;
      new paragraph added for the `static-code-analyzer`/`psalm` never-proposed carve-out (distinct from
      the aggregation-node one — these are ordinary required-gated nodes, not resolved-gated aggregation).
- [x] New ADR: `docs/adr/0018-psalm-becomes-a-tree-node.md`, amending ADR-0008's Equivalents note.
- [x] `scripts/test_tooling_tree.py`: `LoadTreeTests.test_resolved_parents_of_php_structural_scan` updated
      to the new twelve-leaf set; `StructuralScanGateTests`'/`PhpStructuralScanAggregationTests`'
      `_fully_tooled_files()`/`_fully_tooled_php_leaves()` helpers updated to reach `phpstan-level-10` and
      fulfil all five new Rector nodes (plus their two rejection-variant tests, which now drop only the
      `Type`/`type` marker instead of the whole Rector config); `RecommendedGateTests`'
      `_p0_fulfilled_files()` gained a `rector.php` fulfilling `rector-php-set` only, so its
      recommended-edge assertions about `rector-dead-code`/`rector-type-coverage` aren't incidentally
      blocked by the new required parent instead; `ComposerAuditGateTests
      .test_eligible_via_fallback_when_every_other_leaf_resolved`'s fixture reaches level 10 and fulfils
      all Rector nodes for the same reason; `RoadmapTests.test_recommended_outlook`'s lookahead widened
      from 10 to 25 steps (the level chain alone now spans 10 nodes).
- [x] `fixtures/php/php-clean/project/`: `rector.php` extended with all four new Rector set markers;
      `docs/refactoring/out-of-scope/` gained `phpstan-level-4.md` through `phpstan-level-10.md` and
      `phpstan-deprecation-rules.md` (this fixture's "declared ceiling is level 0" story now extends over
      the longer chain, same convention as the existing `phpstan-level-1..3.md` files).
- [x] `scripts/test_trigger_controls.py`: `CleanRepoReportsCleanTests
      .test_structural_scan_gate_open_for_the_resolved_reason`'s expected `rejected` list updated to the
      new 11-entry set (was 3).
- [x] `fixtures/php/*/expected/roadmap.json` (all 7): regenerated via
      `python3 skills/refactor-scan/references/tooling_tree.py fixtures/php/<name>/project --steps 10`;
      verified each with `fixtures/harness/run.sh roadmap <name>` — 7/7 green. `php-psalm` in particular
      confirmed the non-regression goal: its generated roadmap proposes `rector-php-set` and then the four
      other Rector nodes, unlocked purely by the Psalm equivalence, without ever proposing a PHPStan level
      node (the pre-existing "Psalm supersedes the level chain" stop condition, unchanged).
- [x] `python3 -m unittest discover -s scripts -p 'test_*.py'` — 167/167 pass. `python3
      scripts/validate_skills.py .` — clean.

## Comments

> **2026-08-30:** User supplied the node list directly (PHPStan levels 4–10, deprecation rules, four
> Rector sets — one duplicate entry, "Rector Code Quality Set", confirmed as a typo and dropped). Structure
> and edge types were worked out interactively before this ticket was filed: PHPStan-level-10 as the new
> resolved-leaf (levels 3–9 become plain intermediate nodes, same as 1–2 today); `rector-php-set` as a
> shared required parent for the whole Rector family, including the two pre-existing nodes; the
> Psalm-becomes-a-node redesign — originally flagged in `php-tooling-tree.md`'s own equivalents prose as
> "a follow-up ticket['s]" job — folded into this same ticket at the user's explicit request rather than
> deferred, once it became clear the longer chain made the old buried-equivalence shape harder to reason
> about. Non-regression on Psalm's existing unlock of `rector-dead-code`/`rector-type-coverage` (and now
> the whole Rector family via `rector-php-set`) was the one hard constraint throughout — verified via the
> `php-psalm` fixture's regenerated roadmap.
>
> **Cross-check against `.scratch/php-tooling-tree/issues/37-static-code-analyzer-psalm-choice-node.md`:**
> that pre-existing, `ready-for-human` ticket already proposed a `static-code-analyzer`/`psalm`
> restructuring — but a fuller one (`psalm` as an additional resolved-leaf, with automatic mutual-exclusion
> out-of-scope writes), which also fixes a latent gap: a Psalm-only project never auto-resolves the
> PHPStan level chain's leaf, so `structural-scan` stays permanently blocked without a human manually
> writing an out-of-scope entry for it. Confirmed this gap is unchanged by this ticket (only relocated from
> `phpstan-level-3` to `phpstan-level-10`) — deliberately left alone rather than folded in here; ticket 37
> (updated in place to reference the new node names/numbering) remains the tracked backlog item for
> closing it.
