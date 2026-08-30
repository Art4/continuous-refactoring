# 01 — `.editorconfig` as its own node in the generic tooling tree, before `php-cs-fixer`

**What to build:** Add `.editorconfig` as its own node under `skills/refactor-scan/references/tooling-tree.md`'s `## Nodes` section (the generic root — `.editorconfig` is language-independent, even though today it only ever gates a PHP-tree child). Its edges are declared in `skills/refactor-scan/references/php-tooling-tree.md`'s edge table instead, mirroring the existing `loop-config → composer`/`loop-config → ci-runner` precedent (a generic-root node's outgoing/incoming edges into a PHP-tree node are owned by the PHP tree's own table, not the generic root's):

- `loop-config → editorconfig` — **required**. Without this, `editorconfig` would have no required parent at all and would be proposable from pass 1, before `git`/`loop-config` are even fulfilled — the parser derives nodes purely from edge rows (`tooling_tree.py`'s `load_tree()`), so an omitted incoming edge isn't a "no prerequisite" default, it's a bug.
- `editorconfig → php-cs-fixer` — **recommended**. Per ADR-0016, this withholds `php-cs-fixer` from `next_candidates()` until `.editorconfig` is *decided* (fulfilled or rejected) — the mechanism already does exactly what this ticket's motivation asked for ("settle `.editorconfig` before introducing `php-cs-fixer`"), no new gating logic needed.

**Node definition** (`tooling-tree.md`):
- **Name:** `.editorconfig`
- **Tool:** none — plain-text convention file, read by any EditorConfig-aware editor, not a runnable tool.
- **Purpose:** settle the most basic formatting conventions (indentation, charset, line endings) before `php-cs-fixer` introduces language-specific style rules, the same way `php-cs-fixer` itself exists so "later Rector output lands styled."
- **Fulfilment check:** `.editorconfig` exists at the repo root. Pure presence check, no tool run, no equivalent-detection nuance (unlike `phpstan-level-0-baseline`'s Psalm equivalent).
- **MR scope:** create a default `.editorconfig` when missing — single language-neutral `[*]` section, no per-language stanza:
  ```
  root = true

  [*]
  charset = utf-8
  end_of_line = lf
  insert_final_newline = true
  trim_trailing_whitespace = true
  indent_style = space
  indent_size = 4
  ```
  Ordinary node like any other — proposed as a `refactor:candidate`, rejectable as `wontfix` (recorded under `docs/refactoring/out-of-scope/editorconfig.md`) like any other node; no special carve-out.

**Scope:** PHP-tree-adjacent for now (YAGNI) — a concrete edge-table row, not a general "generic node reaches into any specialization" mechanism. Generalize once a second language specialization actually exists.

**Why:** Proposed by the user during the legacy-todo reviewer-loop findings review, in the context of the
Rector-before-`php-cs-fixer` ordering finding (see `.scratch/php-tooling-tree/issues/33-rector-before-recommended-cs-fixer.md`):
before introducing `php-cs-fixer` itself, a target benefits from `.editorconfig` settling the most basic
formatting conventions first, the same way `php-cs-fixer` exists so "later Rector output lands styled."

**Priority:** low — quality-of-life node, no urgency.

**Status:** ready-for-agent

- [ ] `skills/refactor-scan/references/tooling-tree.md`: add the `.editorconfig` node under `## Nodes` (Name, Tool, Purpose, Fulfilment check, MR scope — see above). Diagram stays untouched (illustrative-only, per its existing note; `composer`/`ci-runner` aren't drawn there either).
- [ ] `skills/refactor-scan/references/php-tooling-tree.md`: add `loop-config → editorconfig` (required) and `editorconfig → php-cs-fixer` (recommended) to the Edges table and the mermaid diagram; note in `php-cs-fixer`'s own node prose that it now has a recommended parent, mirroring `rector-dead-code`'s prose style.
- [ ] `skills/refactor-scan/references/tooling_tree.py`: add a `.editorconfig`-presence check and wire it into `detect_nodes()` (mirrors `_has_loop_config`). No other function needs changing — the required/recommended gating in `next_candidates()`/`withheld_candidates()`/`roadmap()` is already generic over the edge table.
- [ ] `scripts/test_tooling_tree.py`: `LoadTreeTests` assertion for the two new edges; a `detect_nodes()` present/absent case; a recommended-gate case that `php-cs-fixer` is withheld from `next_candidates()` until `editorconfig` is decided (mirrors `RecommendedGateTests`'s existing pattern).

## Comments

> **2026-08-29:** Filed from the legacy-todo reviewer-loop findings log
> (`.scratch/legacy-todo-loop-observation/findings.md`, "Idee für später — `.editorconfig` als eigener
> Knoten vor `php-cs-fixer` im allgemeinen Tool-Tree"). First ticket in this new feature directory — see
> `.scratch/tooling-tree/spec.md` for why it's separate from `.scratch/php-tooling-tree/`.

> **2026-08-30:** Design settled via a `/grill-me` session. All four of the ticket's original open
> questions resolved: (1) the edge into `php-cs-fixer` is declared in `php-tooling-tree.md`'s table, not
> `tooling-tree.md`'s — precedent already existed (`loop-config → composer`/`ci-runner`), contradicting
> the ticket's original premise that nothing does this today; (2) fulfilment check is a pure presence
> check, no equivalent-detection nuance, mirroring `loop-config`; (3) MR scope actively creates a default
> file when missing (mirroring `loop-config`'s own MR scope) and the node is ordinarily rejectable
> (`wontfix`) like any other; (4) built PHP-tree-adjacent for now, generalize once a second language
> specialization exists. One additional gap surfaced while checking the seam (`tooling_tree.py`) that the
> grill hadn't covered: without an incoming `required` edge, `.editorconfig` would have no prerequisite at
> all and be proposable from pass 1 — resolved by adding `loop-config → editorconfig` (required), same
> precedent as above. Captured to-spec in the same session — see the checklist above.
