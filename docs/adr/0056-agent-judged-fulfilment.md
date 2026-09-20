# Agent-judged fulfilment: `Open` as complete backlog, scheduler rules, `Fulfilled nodes` retired

> Amends [ADR-0055](0055-purpose-based-fulfilment-and-scheduled-tracks.md): `Open` in each Track's
> `bookkeeping.md` section is redefined as the complete, ordered backlog for that Track — every
> unresolved node of the Track's scope, blocked ones included, in script order, hand-reorderable,
> carrying an issue number only while the node is being worked. `Open` empty means the Track is done.
> `Fulfilled nodes` is retired from the schema and ignored where it still exists. The one-time
> bootstrap exception is corrected: it does not wait for Guardrails' `Open`, and the claim that
> ordinary eligibility keeps Guardrails selected after its first scan is removed.
>
> Amends [ADR-0047](0047-tooling-tree-proposals-are-pre-filed-before-ranking.md): pre-filing no
> longer applies to Track nodes (Safety Net, Guardrails) — an issue for a Track node is created only
> when the node is actually worked via the Track's `Open` walk, never pre-filed at proposal time.
> ADR-0047's pre-filing rule stands unchanged for every non-Track tooling-tree proposal.
>
> Replaces the earlier, unnumbered decision that shipped the parser with detection under
> `refactor-scan` — that parser's role as ground truth for fulfilment is superseded by agent judgement
> against each node's Purpose statement (ADR-0055), and its `Fulfilled nodes` cache is now ignored.

Raised against the observation that the old `Open` semantics (listing only nodes with filed issues)
created ambiguity about what "done" meant for a Track, and that `Fulfilled nodes` was a stale cache
no lifecycle skill needed once fulfilment checks moved to agent judgement. The scheduler rules also
needed formalizing: Safety Net's blockade behavior, Guardrails' yielding when nothing is workable,
Housekeeping's preemption when due, and Investigation's waiting behind a Guardrails backlog were all
implicit, not documented.

## Considered Options

- **Keep `Open` as "nodes with filed issues" and add a separate "all unresolved nodes" field.**
  Rejected — two overlapping lists for the same Track's nodes creates confusion about which is
  authoritative. The complete list is the only one the scheduler and lifecycle skills need.

- **Migrate existing `bookkeeping.md` files to the new schema.** Rejected — migration is error-prone
  and unnecessary. A section written under the old meaning is walked like any other `Open` (naming
  the Track manually forces no scan while `Open` has entries) and is corrected by the scan that runs
  once it is empty. A scan runs only when the selected Track has no `Open` entries; this narrows the spec's story 26
  and case 10 ("manual Track override to force an immediate rescan") accordingly. The old `Fulfilled nodes` field is simply ignored; old
  files retain it for historical record.

- **Keep `Fulfilled nodes` as a cache alongside the new `Open` model.** Rejected — the cache exists
  solely for the tree-walk-fallback prompt, which is itself superseded by agent judgement. Maintaining
  two sources of fulfilment state invites inconsistency with no operational benefit.

## Decision

### `Open` is the complete, ordered backlog

Every Track node's `Open` list contains every node of the Track's scope that is neither fulfilled nor
out-of-scope — blocked ones included, in the script's order, hand-reorderable. An issue number appears
only while the node is being worked. `Open` empty means the Track is done. Existing files under the old
meaning are not migrated; the next scan corrects them.

### Track nodes are not pre-filed

Issues for Track nodes (Safety Net, Guardrails) are created only when the node is actually worked via
the Track's `Open` walk — the walk's pick-up re-check runs first, and the issue is filed at the
moment the node is worked, at most one per pass. This amends ADR-0047's pre-filing decision: a
Track's backlog is its own `Open` list in `bookkeeping.md`, not a set of pre-filed issues, so Rank
mode's pre-filing no longer runs for Track nodes at all. ADR-0047's rule continues unchanged for
every non-Track tooling-tree proposal.

### Safety Net blockade

While Safety Net `Open` is non-empty, Safety Net is selected and nothing else runs, even if no node is
currently workable — the scheduler reports the wait. This is a system-wide blockade, not just a
self-exclusion via the ordinary eligibility rule.

### Guardrails yielding

With at least one workable `Open` node, Guardrails is selected ahead of Investigation. With nothing
workable, it yields — Investigation fills the pass instead.

### Housekeeping preemption

Housekeeping can preempt Guardrails for one pass when due (its `overdue_ratio >= 1`). After that one
pass, ordinary selection resumes.

### Investigation waiting

Investigation waits behind a Guardrails backlog with workable nodes. Guardrails' workable nodes
outrank Investigation's permanent fallback status.

### At most one Track per pass

Each pass runs exactly one Track's process (or no Track at all). This keeps each pass focused and
avoids interleaving different Tracks' work.

### Priority label: Rank-pool filter and tie-breaker, never a preemption

A `refactor:priority` label (ADR-0048) narrows the Rank-mode pool whenever Rank mode runs, and beyond
that acts only as a tie-breaker between otherwise equally ranked candidates. It never preempts a
Track's `Open` walk: Track nodes left the Rank pool (ADR-0047's Track-node amendment
above), so a labeled issue is never compared against the head of `Open`. While a Track with a
workable `Open` node is selected, the labeled issue waits until `Open` is empty (Safety Net: until
the blockade lifts; Guardrails: until no workable node is left, at which point Guardrails yields).
This narrows the spec's story 22 and case 9 ("priority outranks the top of `Open`") to a Rank-mode
pool filter plus a tie-breaker among otherwise equal candidates — never a preemption of the `Open`
walk. The label still takes no part in Track selection and still cannot bypass the Safety Net
blockade.

### Investigation gate: Safety Net section must exist with `Open` empty

`structural-scan` is proposable only when the Safety Net section exists in `bookkeeping.md` and its
`Open` is empty, plus the existing rule that a recorded rejection counts as resolved. This replaces
the old, implicit gate that assumed Safety Net's closure was always a precondition.

### `Fulfilled nodes` retired

`Fulfilled nodes` is retired from the bookkeeping schema. Old files keep the field; it is ignored by
all lifecycle skills. Every node's fulfilled state is now tracked in the Track's own `Open` list
(absence from `Open` means fulfilled or out-of-scope) and by the agent's judgement against the node's
Purpose during each Track's scan.

### One-time bootstrap exception corrected

The one-time bootstrap exception does not wait for Guardrails' `Open`. The earlier claim that
ordinary eligibility keeps Guardrails selected after its first scan is removed — Guardrails gets one
turn during the exception, and after that the ordinary eligibility rule governs it like any other Track.

## Consequences

`CONTEXT.md`'s **Track** entry is updated with blockade and yielding behavior. The **Proposals**
entry notes that pre-filing no longer applies to Track nodes, per the Track-node amendment of
ADR-0047 recorded above — ADR-0047's own header carries the reciprocal note. The **Fulfilment
check** entry notes it
is now agent-judged for every node. A new **recognition-only gate node** entry is added. The
bookkeeping schema documentation and scheduler documentation are updated to reflect all of the above.
