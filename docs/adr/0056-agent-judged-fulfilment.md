# Agent-judged fulfilment: `Open` as complete backlog, scheduler rules, `Fulfilled nodes` retired

> Amends [ADR-0055](0055-purpose-based-fulfilment-and-scheduled-tracks.md): `Open` in each Track's
> `bookkeeping.md` section is redefined as the complete, ordered backlog for that Track — every
> unresolved node of the Track's scope, blocked ones included, in script order, hand-reorderable,
> carrying an issue number only while the node is being worked. `Open` empty means the Track is done.
> `Fulfilled nodes` is retired from the schema and ignored where it still exists. The one-time
> bootstrap exception is corrected: it does not wait for Guardrails' `Open`, and the claim that
> ordinary eligibility keeps Guardrails selected after its first scan is removed.
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
  and unnecessary. A section written under the old meaning is corrected by the Track's next scan, or
  an immediate scan via the Track override. The old `Fulfilled nodes` field is simply ignored; old
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
entry notes that pre-filing no longer applies to Track nodes. The **Fulfilment check** entry notes it
is now agent-judged for every node. A new **recognition-only gate node** entry is added. The
bookkeeping schema documentation and scheduler documentation are updated to reflect all of the above.
