# 30 — Extract tooling-tree node prose into per-node reference files, starting with `composer`

**Type:** task

**What to build:** A convention for extracting a tooling-tree node's Fulfilment check and MR scope out of `php-tooling-tree.md` into its own reference file, once that node's entry has grown enough to warrant it. `php-tooling-tree.md` keeps Tool and Purpose inline plus a pointer to the file — so a merge request can be described by the tool's human-readable name (e.g. `phpstan-level-0-baseline` → "PHPStan Level 0") rather than the node's slug. The diagram and edges table stay where they are (they never held node prose). First extraction: `composer`.

**Blocked by:** 06 ✓ done — Tooling tree (ADR-0005); 29 ✓ done — composer's `Learnings` entry (the trigger: composer's entry became the longest in the file once Learnings was added)

**Status:** done

Decided shape (2026-08-29):

1. **Location:** `skills/refactor-scan/references/php-tooling-tree/<node>.md` — a subdirectory sibling to `php-tooling-tree.md`, named after it, so it scales cleanly as more nodes are extracted one at a time.
2. **Stub in `php-tooling-tree.md`:** the node's `###` heading, Tool, and Purpose stay inline (so MRs can reference the node by its tool's human-readable name); Fulfilment check and MR scope move to the extracted file, with a pointer line replacing them.
3. **Not extracted yet:** every other PHP-tree node stays inline until it gets its own extraction ticket. This is a new precedent — no other skill's `references/` directory splits a topic into per-item files yet.
4. **No code impact:** confirmed by inspection that `skills/refactor-scan/references/tooling_tree.py` only parses the `## Edges` table and derives node names from it; node prose (including composer's) is never read programmatically. `scripts/test_tooling_tree.py`'s `test_tree_docs_are_siblings_of_the_module` only asserts `php-tooling-tree.md`'s existence, not its content — unaffected by the split.

Remaining to specify:

- [x] New file created — `skills/refactor-scan/references/php-tooling-tree/composer.md`
- [x] `php-tooling-tree.md`'s `composer` entry replaced with a stub pointing to it
- [x] `## Nodes` intro note added documenting the per-node-file pattern for future extractions
- [x] ~~Extract the remaining PHP-tree nodes (`ci-runner`, `php-cs-fixer`, `phpunit`, `test-runner-if-missing`, `composer-audit`, `phpstan-level-0-baseline`..`phpstan-level-3`, `rector-dead-code`, `rector-type-coverage`)~~ — deferred to future tickets, one node at a time

## Comments

> **2026-08-29:** Created at the user's request, directly following ticket 29 — composer's entry (Tool/Purpose/Fulfilment check/MR scope/Learnings) had become the tree doc's longest, and the user wanted to start pulling individual tool nodes out into their own reference files, with `composer` as the first.

> **2026-08-29 (later):** Refined the stub shape — Tool and Purpose stay inline in `php-tooling-tree.md` (not just a bare pointer), specifically so a merge request can be titled/described by the tool's human-readable name instead of the node's slug. Also: composer's `Learnings` list was folded into its Fulfilment check/MR scope prose in the extracted file, per ticket 29's follow-up comment — the extracted file no longer has a standalone Learnings section.
