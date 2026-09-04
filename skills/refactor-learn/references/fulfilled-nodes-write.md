# Writing `Fulfilled nodes` and `Skip streak`

Part of `refactor-learn/SKILL.md`'s closing call, always last, regardless of which branch the pass's
other writes rode.

## `Fulfilled nodes`

Write the Refactoring Notes' `bookkeeping.md`'s `Fulfilled nodes` unconditionally
(`skills/continuous-refactoring/references/refactoring-bookkeeping.md`). Each entry carries the
delivering issue # (`- <slug> (#<issue>)`) — **read `bookkeeping.md` as currently committed before
writing**, so an overwrite doesn't lose annotations it didn't itself just produce:

- This pass ran `tooling_tree.py` (deterministic parser) → **overwrite the whole field** with its
  complete current fulfilled-set — keeps the cache correct across out-of-band changes (a revert, a
  manual edit) — but don't discard existing annotations: for every slug already listed as fulfilled
  before this write, carry its existing `(#N)` forward unchanged, keyed by slug, never by position;
  the slug this pass delivered gets its issue #; a parser-confirmed slug with no prior annotation and
  no delivery this pass (fulfilled before this convention existed) carries forward with no
  annotation — never invent one.
- This pass ran the manual/LLM tree-walk fallback instead → only *add* what that walk itself freshly
  confirmed fulfilled, each with this pass's delivering issue # if one exists — never remove/"clean
  up" entries, never guess at unchecked nodes; every other already-annotated entry stays untouched.
- Same `loop-config`-in-flight exception: before it merges, this write lands on its own branch, first
  entry `loop-config (#<its own issue>)`.
- **Worked example**: `bookkeeping.md` already lists `- composer (#77)` and `- ci-runner (#78)`. This
  pass delivers `php-cs-fixer` via issue `#82`; the parser's fulfilled-set is now `{loop-config,
  composer, ci-runner, php-cs-fixer}`. Correct overwrite: `- loop-config` (no annotation, predates
  the convention), `- composer (#77)`, `- ci-runner (#78)`, `- php-cs-fixer (#82)` — the two
  carried-forward annotations are never re-derived or dropped.

## `Skip streak`

Same write, alongside `Fulfilled nodes`: deterministic parser ran → re-run its unblocked-node check
and, for every `required` node it names that this pass did *not* choose, increment its entry by 1
(start at 1 if none); the node chosen or newly fulfilled → drop its entry entirely (omit zero, per
`refactoring-bookkeeping.md`). Manual/LLM fallback ran instead → only touch entries for nodes that
walk actually checked this round.
