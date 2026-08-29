# 30 — Extract tooling-tree node prose into per-node reference files, starting with `composer`

**Type:** task

**What to build:** A convention for extracting a tooling-tree node's full definition (Tool/Purpose/Fulfilment check/MR scope/Learnings) out of `php-tooling-tree.md` into its own reference file, once that node's entry has grown enough to warrant it. `php-tooling-tree.md` keeps a short stub pointing to the file; the diagram and edges table stay where they are (they never held node prose). First extraction: `composer`.

**Blocked by:** 06 ✓ done — Tooling tree (ADR-0005); 29 ✓ done — composer's `Learnings` entry (the trigger: composer's entry became the longest in the file once Learnings was added)

**Status:** done

Decided shape (2026-08-29):

1. **Location:** `skills/refactor-scan/references/php-tooling-tree/<node>.md` — a subdirectory sibling to `php-tooling-tree.md`, named after it, so it scales cleanly as more nodes are extracted one at a time.
2. **Stub in `php-tooling-tree.md`:** the node's `###` heading stays (for scanability of the node list) but its body becomes a single line pointing at the file — no duplication, one source of truth.
3. **Not extracted yet:** every other PHP-tree node stays inline until it gets its own extraction ticket. This is a new precedent — no other skill's `references/` directory splits a topic into per-item files yet.
4. **No code impact:** confirmed by inspection that `skills/refactor-scan/references/tooling_tree.py` only parses the `## Edges` table and derives node names from it; node prose (including composer's) is never read programmatically. `scripts/test_tooling_tree.py`'s `test_tree_docs_are_siblings_of_the_module` only asserts `php-tooling-tree.md`'s existence, not its content — unaffected by the split.

Remaining to specify:

- [x] New file created — `skills/refactor-scan/references/php-tooling-tree/composer.md`
- [x] `php-tooling-tree.md`'s `composer` entry replaced with a stub pointing to it
- [x] `## Nodes` intro note added documenting the per-node-file pattern for future extractions
- [ ] Extract the remaining PHP-tree nodes (`ci-runner`, `php-cs-fixer`, `phpunit`, `test-runner-if-missing`, `composer-audit`, `phpstan-level-0-baseline`..`phpstan-level-3`, `rector-dead-code`, `rector-type-coverage`) — deferred to future tickets, one node at a time

## Comments

> **2026-08-29:** Created at the user's request, directly following ticket 29 — composer's entry (Tool/Purpose/Fulfilment check/MR scope/Learnings) had become the tree doc's longest, and the user wanted to start pulling individual tool nodes out into their own reference files, with `composer` as the first.
