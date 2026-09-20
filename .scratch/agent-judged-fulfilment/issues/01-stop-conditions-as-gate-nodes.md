# 01: Stop-conditions become recognition-only gate nodes

Spec: `agent-judged-fulfilment`.

**What to build:** The three propose-time stop conditions that today live as hidden flags inside the graph logic become ordinary tooling-tree structure. A project with no real (non-platform) dependency gets no audit node proposed, a non-empty PHPStan baseline stops the level chain, and Psalm as the project's analyzer keeps PHPStan level nodes out. Each becomes one recognition-only node, modeled on the existing `is-php-project` gate (never proposed, only a required parent), with a Purpose, a Fulfilment check in prose, and required edges to the nodes it gates. What gets proposed on any target stays exactly as it is today; only where the rule lives changes.

**Blocked by:** None (can start immediately).

**Status:** done — PR #103

- [x] Three gate nodes exist in the PHP tree: one meaning "the project has a real dependency" gating the audit node, one meaning "the current PHPStan baseline is empty" gating every PHPStan level node, one meaning "PHPStan, not Psalm, is the project's analyzer" gating the first level above zero.
- [x] Each gate node has a Purpose and a Fulfilment check written as prose in the tree docs, is never proposed and never appears as a candidate.
- [x] The deterministic parser derives each gate node's state from the same repo facts it uses today, and the graph logic (proposable, withheld, outlook views) has no special-case branch left for these three situations.
- [x] Existing fixtures and tests covering "no real dependency", "non-empty baseline" and "Psalm project" produce the same proposals as before; a Psalm project still resolves the level chain through its recorded mutual-exclusion rejection.
- [x] The baseline gate is a recurring state, not a one-way delivery. It is verified against permanent-gating and recommended-parent logic so that a temporarily closed gate never wrongly closes or withholds other nodes; any adjustment needed is covered by a test.

## Comments

**PR:** [#103](https://github.com/Art4/continuous-refactoring/pull/103)

- **Level-0 is intentionally not gated by the baseline gate.** `phpstan-baseline-empty` is a required
  parent of `phpstan-level-1` through `phpstan-level-10`, not of `phpstan-level-0`: level 0's own delivering
  MR is what creates the baseline, so gating it on an empty baseline would deadlock the chain. Item 1's
  "every PHPStan level node" is read as "every level node above 0". `phpstan-not-psalm` gates
  `phpstan-level-1` only (the rest inherit through the chain).
- **Item 3 is met as of `75931b6` and has since been superseded by ticket 11.** The gate states were derived
  from the same repo facts as before and the special-case branches left `next_candidates()`; ticket 11 then
  deleted the parser's detection, so gate state now comes from the agent-judged fulfilled set (the
  gate nodes' prose Fulfilment checks in `php-tooling-tree.md`).
- **Item 5 (recurring gate) was verified by inspection and one scripted run, no code adjustment needed.**
  The baseline gate is only ever a `required` parent, and `_is_permanently_gated` is read solely by the
  recommended-gate-moot check, which needs *all* recommended parents permanently gated
  (`rector-type-coverage` also has `php-cs-fixer`, `rector-dead-code`, `rector-code-quality`). Running
  `next_candidates`/`withheld_with_reasons`/`ordered_backlog` with `phpstan-baseline-empty` seeded false
  and `phpstan-level-3` true only withheld the level chain (`blocked by required parent
  phpstan-baseline-empty`), nothing was closed or wrongly moot. No dedicated regression test for that
  scenario exists; `GateNodeContractTests` covers each gate seeded false/true for the node it gates.
- Tests: `python3 -m unittest discover -s scripts -p 'test_*.py'` (220 tests) and
  `python3 scripts/validate_skills.py .` pass on the branch head; the `php-psalm` fixture still carries
  the recorded `out-of-scope/phpstan-level-10.md` mutual-exclusion rejection.
