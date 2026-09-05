# Writing `Fulfilled nodes` and `Skip streak`

Part of `refactor-learn/SKILL.md`'s closing call, always last, regardless of which branch the pass's
other writes rode.

## Read fresh, not stale

**Before computing either field**: `git fetch origin`, then sync the comparison inputs from
`origin/main` into the working tree — `git checkout origin/main -- docs/refactoring/out-of-scope/
docs/refactoring/bookkeeping.md` (skip a path that doesn't exist on `origin/main` yet, e.g. no
rejections recorded so far). This candidate branch's own already-landed changes (whatever this pass
delivered) stay exactly as they are — only these two comparison inputs get refreshed, and only in the
working tree; this branch's own commit history is never rewritten, merged, or rebased just for this.

This matters because a candidate branch can predate a sibling change landing on `main` — most
concretely, a maintainer rejecting a node (a new `out-of-scope/<node>.md` file) between when this
branch was created and when this write runs. Without the fresh sync: `Skip streak` can accumulate an
entry for a node that's actually already rejected (it still looks proposable-but-skipped from this
branch's stale point of view), and `Fulfilled nodes`' own "overwrite the whole field" rule below can
silently drop a different node's entry that only exists on `origin/main` because a separate sibling
PR landed it after this branch forked — both real, observed failures during a live run, not
hypothetical.

## `Fulfilled nodes`

Write the Refactoring Notes' `bookkeeping.md`'s `Fulfilled nodes` unconditionally
(`skills/continuous-refactoring/references/refactoring-bookkeeping.md`). Each entry carries the
delivering issue # (`- <slug> (#<issue>)`) — **read `bookkeeping.md` as freshly synced from
`origin/main` above before writing**, so an overwrite doesn't lose annotations it didn't itself just
produce, and doesn't lose a different sibling PR's already-landed entry either:

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

**A node with an `out-of-scope/<node>.md` entry (freshly synced from `origin/main` above) never gets
a skip-streak entry** — drop it if present, never add one — regardless of what the parser's raw
unblocked-check would otherwise say. It isn't a proposable candidate being passed over; it's
permanently closed. Belt-and-suspenders on top of the fresh-sync fix above, not a substitute for it —
the fresh sync is what keeps the parser from naming a rejected node as "unblocked" in the first place;
this rule guards the rare case something else still surfaces it.
