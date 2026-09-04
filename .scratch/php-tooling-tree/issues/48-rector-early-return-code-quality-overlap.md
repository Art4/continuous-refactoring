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

**Status:** needs-triage

Open design questions:

- [ ] Is the current overlap a property of the pinned Rector version specifically (does upstream
  Rector ever ship real early-return-only rules distinct from code-quality, meaning the split is
  forward-looking and correct), or is early-return conceptually always a subset of code-quality's
  broader modernization goal, making the split permanently redundant?
- [ ] If merged: does `rector-code-quality`'s own MR scope prose need to explicitly absorb
  early-return's Purpose text, and does anything reference `rector-early-return`'s slug elsewhere
  that would need updating — `rector-type-coverage`'s recommended-parent chain (`rector.md` line 44)
  currently names it explicitly ("waits on `rector-dead-code` and `rector-early-return` both
  decided").
- [ ] If kept separate with a smarter Fulfilment check: what should "detect known no-op" look like
  mechanically — a version-pinned rule-set-emptiness check inside `tooling_tree.py`, or a documented
  manual judgment call left to the agent adopting it?
- [ ] Does this affect `rector-type-coverage`'s existing "waits on `rector-dead-code` and
  `rector-early-return` both decided" gate — if early-return disappears as a node, does
  type-coverage's gate simplify to just `rector-dead-code`, or does it need a different replacement
  signal?

## Comments

> **2026-09-04:** Filed from the `Art4/legacy-todo` reviewer-loop findings log (PR #112 finding) and
> the `rector-early-return-node-redundant` memory, per the user's request to prepare "für später"
> ideas for fixing. Not yet grilled.
