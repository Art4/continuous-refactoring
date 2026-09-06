# Reference: `housekeeping-template.md`, in the target repo's Refactoring Notes

The accumulated checklist `continuous-housekeeping` copies into each cycle's issue (`SKILL.md` step 4). Doesn't exist until some tooling-tree node's own `Housekeeping` field first contributes a line to it — either as part of that node's own delivering merge request, or via `continuous-housekeeping`'s own reconciliation pass for a node already fulfilled before this file (or the skill itself) existed for this target — see `CONTEXT.md`'s **Tooling tree** entry, and a node's own `Housekeeping` field where one names it (e.g. `skills/refactor-scan/references/php-tooling-tree/composer.md`).

## Structure

```markdown
# Housekeeping checklist

- Run `composer update`; record the output.
- Review `composer audit`'s report; attempt a fix for anything with an available patched version.
- Check for new PHPStan deprecation-rule warnings after any dependency update; fix in scope.
- Check whether a newer PHP patch/minor release exists for the declared minimum version; update if so.
```

One bullet per contributing node, in whatever order they were added — no required ordering, no grouping. Plain prose per line, not a second copy of the contributing node's own Fulfilment-check machinery; `continuous-housekeeping` treats every line as an opaque instruction to carry out, not something it parses or validates against the tree.

## Who writes it

- **Appending a line, ordinary path**: whichever tooling-tree node's own doc names a `Housekeeping` field, as part of that node's own delivering merge request (its `MR scope` says so) — creating the file fresh, with just that one line, if it doesn't exist yet. Never waits for `continuous-housekeeping` to be adopted first; the file exists independently of whether the target repo ever adopts the skill that reads it.
- **Appending a line, reconciliation path**: `continuous-housekeeping` itself, every cycle (`SKILL.md` step 3) — for any already-fulfilled node whose own delivering MR predates this file, or predates the target ever adopting `continuous-housekeeping` at all, there's no future delivering MR left to carry the line. Reconciliation reads `Fulfilled nodes` from `bookkeeping.md` and adds whatever's missing, so a node's line is never permanently lost just because its own adoption happened first.
- **Reading it**: only `continuous-housekeeping` (`SKILL.md` step 3), once per cycle, copying its current contents into that cycle's issue.
- **Removing a line**: not a mechanism this document defines — a node rejected and later un-rejected, or a tool dropped entirely, leaves its housekeeping line in place; pruning is a hand edit, same as any other stale Refactoring Notes content nobody's built automatic removal for.

## Rules

- Never hand-authored from scratch — always the byproduct of some tooling-tree node's own `Housekeeping` field, reaching the file via whichever of the two paths above applies. A target with no PHP-tree nodes contributing anything yet (and none listed in `Fulfilled nodes` that would) simply has no file, and `continuous-housekeeping` reports "nothing registered to check" rather than erroring.
- One line per concern, not one line per tool — a node with several housekeeping-relevant actions (e.g. "run X, then review Y") states them together in its own single contributed line, since `continuous-housekeeping` doesn't split or re-group entries.
