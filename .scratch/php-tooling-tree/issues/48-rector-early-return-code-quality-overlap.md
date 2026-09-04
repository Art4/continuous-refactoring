# 48 — `rector-early-return` overlaps `rector-code-quality` under the pinned Rector version

**What to build:** Reconsider whether `rector-early-return` and `rector-code-quality` should stay
separate sibling nodes on the Rector family tree (`skills/refactor-scan/references/php-tooling-tree/rector.md`),
given that under the currently pinned Rector release (2.6.6) `SetList::EARLY_RETURN` ships **empty**
— its rules (`RemoveAlwaysElse`, `ReturnEarlyIfVariable`, etc.) already live inside
`SetList::CODE_QUALITY`. Three shapes to weigh, not yet decided:

- Keep both nodes as-is, treat the overlap as a Rector-version-specific artifact that un-overlaps in
  a future release — the split stays forward-looking and correct, adopting `rector-early-return` is
  still a legitimate (if currently no-op) config addition.
- Merge `rector-early-return`'s scope into `rector-code-quality`'s own MR/node, dropping
  `rector-early-return` as a separate node.
- Keep both nodes separate, but change `rector-early-return`'s Fulfilment check itself to detect and
  skip cleanly when it's a known no-op under the pinned version, rather than silently landing a
  config-only, no-behavior-change MR every time.

**Why:** Live reviewer-loop finding (`Art4/legacy-todo` PR #112, 2026-09-04, Round 3 —
`.scratch/legacy-todo-loop-observation/findings.md`): adopting the early-return node produced no
actual rewrite. The PR body honestly disclosed this, so nothing incorrect landed — but it's not the
distinct code-level change the tree's node split implies to whoever reads `Fulfilled nodes`/the MR
history later.

**Blocked by:** none.

**Priority:** low — cosmetic/no-op-adoption risk only, not a bug; the PR that surfaced it disclosed
the situation plainly.

**Status:** done

- [x] Researched upstream directly (`rectorphp/rector-src`) rather than guessing: confirmed the
  overlap is not version-specific — `config/set/early-return.php` is `$rectorConfig->rules([])`
  with the comment "all early return rules were moved to code quality set or deprecated," the end
  of a multi-year, deliberate depopulation (individual rules removed/deprecated since 2022, the
  last ones folded into `CODE_QUALITY` or deprecated outright as of early August 2026). Settled the
  three-way choice: **merge/drop** (not "keep as forward-compatible," not "smart-skip Fulfilment
  check" — the latter would have been the only version-aware Fulfilment check in the whole tree,
  for a permanently-empty set).
- [x] `rector-early-return` retired as a node: section removed from `rector.md`, diagram entry + 4
  edge-table rows + `Nodes`-section stub removed from `php-tooling-tree.md`, leaf dropped from
  `php-structural-scan.md`/`composer-audit.md` (thirteen → twelve), detection removed from
  `tooling_tree.py`.
- [x] `rector-code-quality`'s Purpose text extended to name the absorbed early-return behavior
  ("flattens nested conditionals into early returns") — settled via grilling rather than relying on
  the pre-existing generic wording alone.
- [x] `rector-type-coverage`'s recommended-parent gate: `rector-early-return` **swapped for**
  `rector-code-quality`, not dropped outright — preserves the gate's original "control flow
  flattened first" rationale, now carried by the node that actually performs the flattening.
- [x] `scripts/test_tooling_tree.py` updated to match (edge/leaf assertions, fixture `rector.php`
  strings no longer need an `EarlyReturn` marker); `fixtures/php/*/expected/roadmap.json` (all 8) and
  `fixtures/php/php-clean/project/rector.php` regenerated against the real parser.
  `python3 -m unittest discover -s scripts -p 'test_*.py'` (240/240) and
  `python3 scripts/validate_skills.py` (same 5 pre-existing advisory warnings) both green.
- [x] New ADR: `docs/adr/0030-drop-rector-early-return-node-merge-into-code-quality.md`, amending
  ADR-0019 and ADR-0021.
- [x] `legacy-todo`'s already-fulfilled `rector-early-return (#112)` bookkeeping entry: confirmed no
  migration needed — `Fulfilled nodes` self-heals via the parser's own re-derivation.

## Comments

> **2026-09-04:** Filed from the `Art4/legacy-todo` reviewer-loop findings log (PR #112 finding) and
> the `rector-early-return-node-redundant` memory, per the user's request to prepare "für später"
> ideas for fixing.

> **2026-09-04 (later):** Design settled via a `/grill-me` session (in German). Upstream research
> (see checklist) ruled out the "wait for it to un-overlap" option before the first question was
> even asked. Key decisions: clean node removal + ADR as the sole historical record (no skill-text
> stub), `rector-type-coverage`'s gate swaps in `rector-code-quality` rather than losing the
> "flattened first" prerequisite, `rector-code-quality`'s Purpose text explicitly absorbs the
> early-return description, `legacy-todo`'s existing fulfilled-node entry needs no migration.
> Implemented in the same session on branch `tickets/48-drop-rector-early-return-node` — see the
> checklist above for the full file list.
