# 41 — `editorconfig` becomes an 8th `resolved` leaf feeding `structural-scan`

**What to build:** Add `editorconfig -> structural-scan` as a `resolved` edge — an 8th leaf alongside the
seven existing PHP-tree leaves (`composer-audit`, `phpunit`, `test-runner-if-missing`, `php-cs-fixer`,
`phpstan-level-3`, `rector-dead-code`, `rector-type-coverage`) that already gate `structural-scan` this
way. Reuses the existing `resolved`-edge mechanism verbatim — no new edge type, no new code path. Since
both endpoints (`editorconfig`, `structural-scan`) are already generic-root nodes, the row belongs in
`skills/refactor-scan/references/tooling-tree.md`'s own edge table, per that document's established
edge-ownership rule (an edge belongs to the file where *both* endpoints already live), not
`php-tooling-tree.md`'s (where the other seven live, since each of *their* other endpoints is a PHP-tree
leaf).

**Why:** `structural-scan` exists to hold agent-driven structural refactoring back until deterministic
tooling has had its say. `.editorconfig` settling basic formatting conventions is exactly that kind of
deterministic groundwork, on the same footing as the seven PHP-tree leaves already gating this node — its
absence from the leaf set was a gap ticket 01 left open (it added `editorconfig` as a node and wired its
`php-cs-fixer` recommended edge, but never wired it into `structural-scan`'s own gate). The
resolved-vs-recommended edge-mechanics question was raised and settled with the user directly during a
`/plan` session (not a separate `/grill-me` round): a literal `recommended` edge into `structural-scan`
would currently have **no gating effect** at all (`next_candidates()`/`detect_nodes()`/`withheld_candidates()`
read only `resolved_parents` for this node — confirmed by reading the code), and `structural-scan`'s own
documentation explicitly says its edges are "never `required` or `recommended`", precisely so one declined
tooling branch never permanently blocks it (ADR-0008). Reusing the existing `resolved` mechanism instead
gets the actually-desired effect (structural-scan waits on `.editorconfig` too, a rejected `.editorconfig`
still unblocks it) with zero new code.

**Priority:** low — quality-of-life closure of a gap ticket 01 left open, no urgency, same footing as
ticket 01 itself.

**Status:** ready-for-agent

- [ ] `skills/refactor-scan/references/tooling-tree.md`: add `editorconfig -> structural-scan` (resolved)
      to the Edges table; add the real `edc -.->|resolved| ss` line to the diagram; reword the ownership
      paragraph below the table, `editorconfig`'s own node prose (two outgoing edges now, not one), and
      `structural-scan`'s Fulfilment-check/Edge-type bullets (leaf set is no longer purely "the active
      language specialization's tree").
- [ ] `skills/refactor-scan/references/php-tooling-tree.md`: clarify the "seven `resolved` rows above"
      sentence to name the 8th, elsewhere-declared leaf; update `composer-audit`'s Stop-conditions bullet
      to add `editorconfig` to its named "every other leaf" list (its fallback-eligibility gate already
      reads this generically from the resolved-parents table, so the prose was about to go stale). No
      diagram change — the new row doesn't live in this file's own table.
- [ ] `skills/refactor-scan/SKILL.md`: reword the `structural-scan` bullet's "every leaf of the active
      language tree" premise and the "no language tree recognized" bullet (`editorconfig`'s edge lives at
      the generic root regardless of language tree).
- [ ] `scripts/test_tooling_tree.py`: extend `LoadTreeTests` (new edge assertion, updated 8-name leaf
      set); add `.editorconfig` to `StructuralScanGateTests._fully_tooled_files()` and to
      `ComposerAuditGateTests.test_eligible_via_fallback_when_every_other_leaf_resolved`'s fixture (both
      currently build "every leaf resolved" scenarios that don't account for the new leaf); add two new
      `StructuralScanGateTests` cases proving the node genuinely waits on `editorconfig`
      (unresolved-when-missing, resolved-via-rejection).
- [ ] `fixtures/php/php-clean/project/`: verified no change needed — `.editorconfig` already present and
      unrejected there since ticket 01.
- [ ] Run `python3 -m unittest discover -s scripts -p 'test_*.py'` (must stay green) and
      `python3 scripts/validate_skills.py .` (must report clean) before opening the PR.

## Comments

> **2026-08-30:** Filed during a `/plan` session — the resolved-vs-recommended edge mechanics question was
> asked and settled with the user directly in that session (not a separate `/grill-me` round) before this
> ticket was written, so it ships already fully spec'd (`ready-for-agent`) rather than `needs-triage`.
> Branched off `tickets/01-editorconfig-node` (unmerged, PR #23) since this ticket depends on the
> `editorconfig` node it adds — stacked per ADR-0015.
