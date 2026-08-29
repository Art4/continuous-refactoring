# 29 — Capture per-node learnings on the tooling tree, starting with `composer`

**Type:** task

**What to build:** A `Learnings` entry as an optional part of the tooling-tree node schema — alongside Tool/Purpose/Fulfilment check/MR scope — for recording operational lessons discovered while adopting or fulfilling a node, filled in as they're found rather than upfront. First (and so far only) populated instance: `composer`. Other nodes get a `Learnings` entry in later tickets, one at a time, as the individual tool nodes are improved.

**Blocked by:** 06 ✓ done — Tooling tree (ADR-0005)

**Status:** done

Decided shape (2026-08-29):

1. **Schema:** `Learnings` documented once on `CONTEXT.md`'s **Tooling tree** term, referenced by both tree documents like the rest of the node vocabulary.
2. **`composer`'s Learnings** (from real-world Composer practice):
   - `composer.json`'s `type` decides `composer.lock`'s git treatment: `library` → `composer.lock` goes in `.gitignore`, not committed; `project` (or any other non-library type) → `composer.lock` is committed.
   - A missing or generic `description` in `composer.json` is derived from the target repo's README or existing code where possible; if it can't be derived, it's left empty rather than filled with a placeholder.
   - `vendor/` always belongs in `.gitignore`, regardless of type.

Remaining to specify:

- [x] `Learnings` added to the node schema — `CONTEXT.md`'s **Tooling tree** term
- [x] `composer` node's Learnings filled in — `skills/refactor-scan/references/php-tooling-tree.md` (now `skills/refactor-scan/references/php-tooling-tree/composer.md`, see ticket 30)
- [x] This ticket recorded in the feature's issue table — `.scratch/php-tooling-tree/spec.md`
- [ ] Generalize `Learnings` to the remaining PHP-tree nodes (`ci-runner`, `php-cs-fixer`, `phpunit`, …) — deferred to future tickets, one node at a time

## Comments

> **2026-08-29:** Created at the user's request — they wanted the individual tool nodes improved, with a concrete first step of recording learnings on the `composer` node specifically (lockfile-vs-type handling, description derivation, vendor/ gitignore). Schema decision and composer content landed together in the same pass. If the pattern proves useful across more nodes, a dedicated ADR formalizing it is worth considering then — not done here.

> **2026-08-29:** Composer's entry (including this Learnings section) moved out of `php-tooling-tree.md` into its own reference file — see ticket 30.
