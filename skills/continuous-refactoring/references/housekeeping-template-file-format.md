# Reference: `housekeeping-template.md`, in the target repo's Refactoring Notes

The accumulated checklist the Housekeeping Track
(`skills/continuous-refactoring/references/housekeeping-track.md`) copies into each cycle's issue
(*Open this cycle's issue*). Doesn't exist until some tooling-tree node's own `Housekeeping` field first
contributes a line to it — either as part of that node's own delivering merge request, or via the
Housekeeping Track's own reconciliation step for a node already fulfilled before this file (or this
Track's own bookkeeping section) existed for this target — see `CONTEXT.md`'s **Tooling tree** entry, and
a node's own `Housekeeping` field where one names it (e.g.
`skills/refactor-scan/references/php-tooling-tree/composer.md`).

## Structure

```markdown
# Housekeeping checklist

- Run `composer update`; record the output.
- Review `composer audit`'s report; attempt a fix for anything with an available patched version.
- Check for new PHPStan deprecation-rule warnings after any dependency update; fix in scope.
- Check whether a newer PHP patch/minor release exists for the declared minimum version; update if so.
```

One bullet per contributing node, in whatever order they were added — no required ordering, no grouping.
Plain prose per line, not a second copy of the contributing node's own Fulfilment-check machinery; the
Housekeeping Track treats every line as an opaque instruction to carry out, not something it parses or
validates against the tree.

## Who writes it

- **Appending a line, ordinary path**: whichever tooling-tree node's own doc names a `Housekeeping` field,
  as part of that node's own delivering merge request (its `MR scope` says so) — creating the file fresh,
  with just that one line, if it doesn't exist yet. Never waits for the Housekeeping Track to have run
  first; the file exists independently of whether this Track has ever been scheduled for this target yet.
- **Appending a line, reconciliation path**: the Housekeeping Track itself, every cycle
  (`housekeeping-track.md`'s own *Reconcile* section) — for any fulfilled node whose own delivering MR
  predates this file, or whose adoption happened outside the suite entirely (a hand-adopted tool,
  Guardrails tools included), there's no future delivering MR left to carry the line. Reconciliation
  walks the tooling tree and judges each node's Fulfilment check itself (agent judgement), adding
  whatever's missing, so a node's line is never permanently lost just because no delivering MR exists.
- **Reading it**: only the Housekeeping Track (`housekeeping-track.md`'s own *Reconcile* section), once
  per cycle, copying its current contents into that cycle's issue.
- **Removing a line**: not a mechanism this document defines — a node rejected and later un-rejected, or
  a tool dropped entirely, leaves its housekeeping line in place; pruning is a hand edit, same as any
  other stale Refactoring Notes content nobody's built automatic removal for.

## Rules

- Never hand-authored from scratch — always the byproduct of some tooling-tree node's own `Housekeeping`
  field, reaching the file via whichever of the two paths above applies. A target with no tooling-tree
  nodes contributing anything yet (and none judged fulfilled that would) simply has no file, and the
  Housekeeping Track reports "nothing registered to check" rather than erroring.
- One line per concern, not one line per tool — a node with several housekeeping-relevant actions (e.g.
  "run X, then review Y") states them together in its own single contributed line, since the Housekeeping
  Track doesn't split or re-group entries.
