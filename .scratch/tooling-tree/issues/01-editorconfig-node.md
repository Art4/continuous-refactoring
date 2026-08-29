# 01 — `.editorconfig` as its own node in the generic tooling tree, before `php-cs-fixer`

**What to build:** Not yet spec'd — an idea to design properly, not a ready ticket. Add `.editorconfig`
as its own node in the **generic** tooling tree (`skills/refactor-scan/references/tooling-tree.md`),
positioned so it's proposed before `php-cs-fixer` in the PHP tree's adoption order — since `.editorconfig`
is language-independent (basic indentation/charset/line-ending conventions any editor respects), it
belongs in the generic root, not the PHP specialization, even though today it would only ever gate a
PHP-tree child.

**Why:** Proposed by the user during the legacy-todo reviewer-loop findings review, in the context of the
Rector-before-`php-cs-fixer` ordering finding (see `.scratch/php-tooling-tree/issues/33-rector-before-recommended-cs-fixer.md`):
before introducing `php-cs-fixer` itself, a target benefits from `.editorconfig` settling the most basic
formatting conventions first, the same way `php-cs-fixer` exists so "later Rector output lands styled."

**Priority:** (none — filed as an idea, not a firm ask)

**Status:** needs-triage

Open questions to resolve before this is spec'd:

- [ ] `skills/refactor-scan/references/tooling-tree.md` states "a language tree's own edge table is the
  source for edges into its nodes" — a generic-tree `.editorconfig` node with a `recommended` edge into
  the PHP tree's `php-cs-fixer` crosses that boundary. Which tree's edge table declares that edge: the
  generic root's (reaching forward into a specialization, which nothing does today), or the PHP tree's
  (reaching backward into the generic root, which `structural-scan`'s `resolved` edges already do in the
  other direction)?
- [ ] Fulfilment check: presence of a `.editorconfig` file at the repo root is presumably sufficient (no
  tool to run) — confirm there's no equivalent-detection nuance the way `phpstan-level-0-baseline` has
  Psalm as an equivalent.
- [ ] MR scope: does adopting this node ever *write* content into the file (a default indent/charset
  ruleset), or does it only ever record recognition of an existing one — i.e. can a target ever be
  *rejected* on this node (`wontfix`), or is presence-or-create always trivially achievable?
- [ ] Should this generalize beyond PHP immediately (i.e. designed as truly language-neutral from the
  start), or is it fine to build it PHP-tree-adjacent for now and generalize later once a second language
  specialization actually exists?

## Comments

> **2026-08-29:** Filed from the legacy-todo reviewer-loop findings log
> (`.scratch/legacy-todo-loop-observation/findings.md`, "Idee für später — `.editorconfig` als eigener
> Knoten vor `php-cs-fixer` im allgemeinen Tool-Tree"). First ticket in this new feature directory — see
> `.scratch/tooling-tree/spec.md` for why it's separate from `.scratch/php-tooling-tree/`.
